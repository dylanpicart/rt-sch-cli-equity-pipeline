from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import snowflake.connector
from snowflake.connector.errors import ProgrammingError
import openai

from .config import get_settings
from .langchain_chain import (
    get_relevant_docs,
    format_docs_for_prompt,
    run_rag,
)

settings = get_settings()
router = APIRouter()


# ---------- Pydantic models ----------


class RAGQuery(BaseModel):
    """
    Request body for the RAG endpoint.

    - question: natural language question from the user
    - district_id: primary district for context/metrics
    - other_district_id: optional second district for comparisons
    - year: optional filter for year (currently not used in snapshot)
    - mode:
        - "district_risk_overview"
        - "explain_metric"
        - "explain_question"
        - "compare_districts"
    """
    question: str
    district_id: Optional[int] = None
    other_district_id: Optional[int] = None
    year: Optional[int] = None
    mode: Optional[str] = "district_risk_overview"


class Citation(BaseModel):
    """
    A lightweight reference to a piece of retrieved context.
    """
    id: str
    source_type: str
    source_id: Optional[str] = None


class RAGResponse(BaseModel):
    """
    Response schema for the RAG API.
    """
    answer: str
    high_level_bullets: List[str]
    metrics: List[Dict[str, Any]]
    citations: List[Citation]


class StatusResponse(BaseModel):
    """
    Backend status for the RAG service so the UI can see how the server is configured.
    """
    use_fake_embeddings: bool
    use_fake_llm: bool
    embedding_model: str
    llm_model: str


# ---------- Status endpoint ----------


@router.get("/status", response_model=StatusResponse)
def get_status() -> StatusResponse:
    """
    Simple status endpoint so the UI can see how the backend is configured.
    """
    return StatusResponse(
        use_fake_embeddings=settings.USE_FAKE_EMBEDDINGS,
        use_fake_llm=settings.USE_FAKE_LLM,
        embedding_model=settings.EMBEDDING_MODEL,
        llm_model="gpt-4.1-mini",  # keep in sync with langchain_chain.py
    )


# ---------- Metrics fetch (SCHOOL_CLIMATE_SNAPSHOT) ----------


def fetch_metrics_from_snowflake(
    district_id: Optional[int],
    year: Optional[int],
) -> List[Dict[str, Any]]:
    """
    Fetch climate-related quantitative indicators for a district from
    GOLD.SCHOOL_CLIMATE_SNAPSHOT.

    Assumes SCHOOL_CLIMATE_SNAPSHOT has at least:
      - DISTRICT_NUMBER
      - DBN
      - PARENT_RESPONSE_RATE
      - TEACHER_RESPONSE_RATE
      - STUDENT_RESPONSE_RATE

    For now, we:
      - filter by DISTRICT_NUMBER
      - compute the average response rates across schools in that district
      - report how many schools were included

    If the table does not exist or the user is not authorized, we log and
    return an empty list instead of crashing the endpoint.
    """
    if district_id is None:
        return []

    conn = snowflake.connector.connect(
        account=settings.SNOWFLAKE_ACCOUNT,
        user=settings.SNOWFLAKE_USER,
        password=settings.SNOWFLAKE_PASSWORD,
        warehouse=settings.SNOWFLAKE_WAREHOUSE,
        database=settings.SNOWFLAKE_DATABASE,
        schema=settings.SNOWFLAKE_SCHEMA,
    )

    metrics: List[Dict[str, Any]] = []

    try:
        cur = conn.cursor()
        try:
            # Aggregate response rates and school count for the district
            cur.execute(
                """
                SELECT
                    AVG(PARENT_RESPONSE_RATE)   AS AVG_PARENT_RESPONSE_RATE,
                    AVG(TEACHER_RESPONSE_RATE)  AS AVG_TEACHER_RESPONSE_RATE,
                    AVG(STUDENT_RESPONSE_RATE)  AS AVG_STUDENT_RESPONSE_RATE,
                    COUNT(DISTINCT DBN)         AS SCHOOL_COUNT
                FROM SCHOOL_CLIMATE_SNAPSHOT
                WHERE DISTRICT_NUMBER = %s
                """,
                (district_id,),
            )
        except ProgrammingError as pe:
            # Table missing or not authorized: log and degrade gracefully
            print(
                f"[fetch_metrics_from_snowflake] Failed to query SCHOOL_CLIMATE_SNAPSHOT: {pe}"
            )
            return []

        row = cur.fetchone()
        if row is None:
            return []

        avg_parent, avg_teacher, avg_student, school_count = row

        table_fq = (
            f"{settings.SNOWFLAKE_DATABASE}."
            f"{settings.SNOWFLAKE_SCHEMA}."
            "SCHOOL_CLIMATE_SNAPSHOT"
        )

        if avg_parent is not None:
            metrics.append(
                {
                    "metric_name": "Average Parent Response Rate",
                    "value": float(avg_parent),
                    "district_rank": None,
                    "year": None,
                    "source": table_fq,
                }
            )

        if avg_teacher is not None:
            metrics.append(
                {
                    "metric_name": "Average Teacher Response Rate",
                    "value": float(avg_teacher),
                    "district_rank": None,
                    "year": None,
                    "source": table_fq,
                }
            )

        if avg_student is not None:
            metrics.append(
                {
                    "metric_name": "Average Student Response Rate",
                    "value": float(avg_student),
                    "district_rank": None,
                    "year": None,
                    "source": table_fq,
                }
            )

        metrics.append(
            {
                "metric_name": "Number of Schools in Snapshot",
                "value": int(school_count or 0),
                "district_rank": None,
                "year": None,
                "source": table_fq,
            }
        )

    finally:
        conn.close()

    return metrics


# ---------- RAG endpoint ----------


@router.post("/rag/query", response_model=RAGResponse)
def rag_query(payload: RAGQuery) -> RAGResponse:
    """
    Main RAG endpoint.

    Modes:

    - district_risk_overview (default):
        Uses LangChain retriever over the Chroma index to get semantic context
        and creates a district-level equity/risk overview combining SVI + climate.

    - explain_metric:
        Uses the same retriever + metrics, but the prompt is focused on explaining
        a single metric or concept in depth.

    - explain_question:
        Provides a deep dive on one or more climate survey questions, tying them to SVI themes.

    - compare_districts:
        Compares two districts using primary and comparison district metrics and context.
    """

    mode = (payload.mode or "district_risk_overview").lower()

    # 1) Retrieve semantic context (climate + SVI text)
    docs = get_relevant_docs(payload.question, k=8)

    # 2) Format context into a string for the prompt
    context_str = format_docs_for_prompt(docs)

    # 3) Fetch metrics depending on mode
    metrics: List[Dict[str, Any]] = []
    metrics_str = "[no numeric climate metrics found]"

    if mode == "compare_districts" and payload.district_id and payload.other_district_id:
        metrics_primary = fetch_metrics_from_snowflake(payload.district_id, payload.year)
        metrics_other = fetch_metrics_from_snowflake(payload.other_district_id, payload.year)

        part_a = "\n".join(
            f"- {m['metric_name']}: {m['value']} (source={m.get('source', 'unknown')})"
            for m in metrics_primary
        ) or "[no metrics for primary district]"
        part_b = "\n".join(
            f"- {m['metric_name']}: {m['value']} (source={m.get('source', 'unknown')})"
            for m in metrics_other
        ) or "[no metrics for comparison district]"

        metrics_str = (
            f"Primary district metrics (district_id={payload.district_id}):\n"
            f"{part_a}\n\n"
            f"Comparison district metrics (district_id={payload.other_district_id}):\n"
            f"{part_b}"
        )

        metrics = metrics_primary + metrics_other

    else:
        # Default: single-district metrics (or none if district_id is missing)
        metrics_single = fetch_metrics_from_snowflake(payload.district_id, payload.year)

        if metrics_single:
            metrics_str = "\n".join(
                f"- {m['metric_name']}: {m['value']} "
                f"(source={m.get('source', 'unknown')})"
                for m in metrics_single
            )
            metrics = metrics_single
        else:
            metrics_str = "[no numeric climate metrics found]"
            metrics = []

    # 4) Run the LangChain RAG chain (prompt + LLM) with mode
    try:
        llm_output = run_rag(
            question=payload.question,
            context_str=context_str,
            metrics_str=metrics_str,
            mode=mode,
        )
    except openai.RateLimitError:
        # LLM provider is rate-limiting or quota is exhausted
        raise HTTPException(
            status_code=503,
            detail=(
                "RAG service is currently rate-limited by the LLM provider or quota is exhausted. "
                "Please try again later or check API usage/billing."
            ),
        )
    except Exception as e:
        # Catch-all to avoid leaking stack traces to the client
        raise HTTPException(
            status_code=500,
            detail=f"RAG service failed: {type(e).__name__}: {str(e)}",
        )

    # 5) Post-process the LLM output into answer + bullets
    lines = [ln.strip() for ln in llm_output.split("\n") if ln.strip()]
    if not lines:
        answer = (
            "I wasn't able to generate an answer from the available "
            "school climate and SVI context."
        )
        bullets: List[str] = []
    else:
        answer = lines[0]
        bullets = [ln.lstrip("-• ") for ln in lines[1:6]]  # up to 5 bullets

    # 6) Build citations from the retrieved docs' metadata
    citations: List[Citation] = []
    for d in docs:
        meta = d.metadata or {}
        citations.append(
            Citation(
                id=str(
                    meta.get("id")
                    or meta.get("source_id")
                    or "unknown"
                ),
                source_type=meta.get("source_type", "unknown"),
                source_id=str(meta.get("source_id")) if meta.get("source_id") else None,
            )
        )

    return RAGResponse(
        answer=answer,
        high_level_bullets=bullets,
        metrics=metrics,
        citations=citations,
    )
