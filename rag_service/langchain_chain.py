from typing import List, Any

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI

from .config import get_settings
from .embeddings import get_embedding_client
from .prompts import (
    overview_prompt,
    explain_metric_prompt,
    explain_question_prompt,
    compare_districts_prompt,
)

settings = get_settings()

# Embeddings (real or fake, depending on USE_FAKE_EMBEDDINGS in .env)
embeddings = get_embedding_client()

# Attach to existing Chroma index
vectordb = Chroma(
    collection_name="school_climate_semantic",
    persist_directory=settings.VECTOR_DIR,
    embedding_function=embeddings,
)

retriever = vectordb.as_retriever(search_kwargs={"k": 8})


class FakeChatLLM:
    """
    Simple fake LLM for dev/testing when USE_FAKE_LLM=true.

    - Does NOT call any external APIs.
    - Returns canned but structured responses that follow the
      expected formats for various modes:
        - district_risk_overview
        - explain_metric
        - explain_question
        - compare_districts (falls back to overview-style text)
    """

    def __init__(self, mode: str = "district_risk_overview"):
        self.mode = mode.lower()

    def invoke(self, input_data: Any) -> AIMessage:
        """
        For fake mode, we mostly ignore prompt messages and rely on
        a simple dict with keys: question, context, metrics.
        """
        if isinstance(input_data, dict):
            question = input_data.get("question", "")
            metrics = input_data.get("metrics", "")
        else:
            question = ""
            metrics = ""

        if self.mode == "explain_metric":
            content = self._explain_metric_response(question, metrics)
        elif self.mode == "explain_question":
            content = self._explain_question_response(question, metrics)
        elif self.mode == "compare_districts":
            content = self._compare_districts_response(question, metrics)
        else:
            content = self._overview_response(question, metrics)

        return AIMessage(content=content)

    def _overview_response(self, question: str, metrics_str: str) -> str:
        lines: List[str] = []

        # Paragraph
        lines.append(
            "This is a simulated district-level risk and equity overview generated in fake LLM mode. "
            "It illustrates how SVI themes and climate metrics might be combined for interpretation, "
            "but does not reflect real model reasoning."
        )

        # Theme 1
        lines.append(
            "- Theme: Socioeconomic Status (Theme 1) – Metric: Student Response Rate – "
            "Explanation: In high-socioeconomic-vulnerability areas, student response rates may be lower "
            "due to instability at home, making it important to interpret climate surveys alongside SVI."
        )
        # Theme 2
        lines.append(
            "- Theme: Household Composition & Disability (Theme 2) – Metric: Student Response Rate – "
            "Explanation: Communities with higher concentrations of caregiving responsibilities, "
            "disability, or single-parent households may face additional barriers to consistent attendance "
            "and survey participation, which can depress student response rates."
        )
        # Theme 3
        lines.append(
            "- Theme: Minority Status & Language (Theme 3) – Metric: Parent Response Rate – "
            "Explanation: Tracts with higher linguistic isolation can correspond to lower parent survey "
            "participation, suggesting a need for translated surveys, interpreters, and targeted outreach."
        )
        # Theme 4
        lines.append(
            "- Theme: Housing & Transportation (Theme 4) – Metric: Teacher Response Rate – "
            "Explanation: Teachers serving communities with housing and transit challenges may face higher "
            "stress and workload, which can influence how they respond to climate questions."
        )

        return "\n".join(lines)

    def _explain_metric_response(self, question: str, metrics_str: str) -> str:
        lines: List[str] = []

        # Definition paragraph
        lines.append(
            "This is a simulated explanation of a climate metric in fake LLM mode. "
            "It shows the shape and structure of the response you would get from the real model."
        )

        # Why this matters for equity
        lines.append("Why this matters for equity:")
        lines.append(
            "- **Represents whose voices are heard:** When response rates are low, certain groups "
            "may be systematically underrepresented in climate data."
        )
        lines.append(
            "- **Signals structural barriers:** Gaps in the metric across districts or schools can highlight "
            "transportation, language, or resource barriers that are harder to see in aggregate reports."
        )
        lines.append(
            "- **Links to SVI:** When high-SVI communities consistently show weaker results on this metric, "
            "it suggests that structural vulnerability and climate experiences are reinforcing each other."
        )

        # Interaction with SVI themes
        lines.append(
            "In high-SVI tracts, this metric may consistently look worse, indicating that families and educators "
            "in those communities face compounded barriers that should be accounted for when using climate data "
            "for decision-making."
        )

        return "\n".join(lines)

    def _explain_question_response(self, question: str, metrics_str: str) -> str:
        lines: List[str] = []

        # Question overview
        lines.append(
            "This is a simulated deep-dive explanation of a climate survey question in fake LLM mode. "
            "It illustrates how you might interpret a question about safety, relationships, or engagement "
            "through an equity and SVI lens."
        )

        # Interpretation bullets
        lines.append("Interpretation for equity:")
        lines.append(
            "- In high-SVI tracts with housing instability or caregiving burdens, lower agreement with this "
            "question may signal that students or families are carrying stressors outside of school that "
            "shape how they experience the school environment."
        )
        lines.append(
            "- In communities with high linguistic diversity, responses to this question may depend on whether "
            "surveys and follow-up conversations are available in home languages."
        )
        lines.append(
            "- For staff-facing questions, responses may reflect working conditions that are unevenly distributed "
            "across schools and neighborhoods."
        )

        # Caveats
        lines.append(
            "If response rates are low for the group answering this question, interpretation should be cautious, "
            "because the loudest voices may not represent the full community."
        )

        return "\n".join(lines)

    def _compare_districts_response(self, question: str, metrics_str: str) -> str:
        lines: List[str] = []

        lines.append(
            "This is a simulated comparison of two districts in fake LLM mode. "
            "It shows the type of narrative you might generate when contrasting SVI and climate metrics, "
            "but does not reflect real model reasoning."
        )
        lines.append(
            "In a real comparison, you would highlight which district appears to have higher structural "
            "vulnerability (based on SVI themes) and how that aligns with climate metrics such as response "
            "rates, safety perceptions, or engagement indicators."
        )
        lines.append(
            "You would also call out any caveats, such as differences in survey participation or missing data, "
            "to avoid over-interpreting small numeric differences."
        )

        return "\n".join(lines)


def _get_llm(mode: str) -> Any:
    """
    Return the LLM client according to configuration:

    - If USE_FAKE_LLM=true, returns FakeChatLLM with the given mode.
    - Otherwise, returns ChatOpenAI with the configured model and key.
    """
    if settings.USE_FAKE_LLM:
        return FakeChatLLM(mode=mode)
    else:
        return ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.2,
            openai_api_key=settings.OPENAI_API_KEY,
        )


# ---------- RETRIEVAL & RUNNERS ----------


def get_relevant_docs(question: str, k: int = 8) -> List[Document]:
    """
    Use LangChain retriever (Runnable-style) to get semantically relevant chunks.

    In LangChain v0.2+, retrievers implement `.invoke()` instead of `.get_relevant_documents()`.
    """
    docs = retriever.invoke(question)
    return docs


def format_docs_for_prompt(docs: List[Document]) -> str:
    """
    Format retrieved documents so the LLM can see what type of context each line is.

    We expect source_type values like:
      - "climate_question"
      - "climate_metric"
      - "svi_definition"
      - "svi_tract"
    """
    if not docs:
        return "[no semantic context found]"

    lines: List[str] = []
    for d in docs:
        meta = d.metadata or {}
        source_type = (meta.get("source_type") or "unknown").lower()
        source_id = meta.get("source_id") or ""

        if source_type == "climate_question":
            prefix = "[CLIMATE_QUESTION"
        elif source_type == "climate_metric":
            prefix = "[CLIMATE_METRIC"
        elif source_type == "svi_definition":
            prefix = "[SVI_DEFINITION"
        elif source_type == "svi_tract":
            prefix = "[SVI_TRACT"
        else:
            prefix = "[CONTEXT"

        if source_id:
            prefix = f"{prefix} {source_id}]"
        else:
            prefix = f"{prefix}]"

        lines.append(f"- {prefix} {d.page_content}")

    return "\n".join(lines)


def run_rag(
    question: str,
    context_str: str,
    metrics_str: str,
    mode: str = "district_risk_overview",
) -> str:
    """
    Call LLM (real or fake) with assembled context + metrics and a specific "mode":

    - "district_risk_overview": explain district-level risk patterns tying SVI + climate.
    - "explain_metric": explain a single metric or concept in depth.
    - "explain_question": deep-dive explanation of a survey question.
    - "compare_districts": compare two districts using metric summaries.
    """
    mode = (mode or "district_risk_overview").lower()

    if mode == "explain_metric":
        prompt_template = explain_metric_prompt
    elif mode == "explain_question":
        prompt_template = explain_question_prompt
    elif mode == "compare_districts":
        prompt_template = compare_districts_prompt
    else:
        prompt_template = overview_prompt

    llm_client = _get_llm(mode=mode)

    # Build messages from the prompt template
    messages: List[BaseMessage] = prompt_template.format_messages(
        question=question,
        context=context_str,
        metrics=metrics_str or "[no metrics available]",
    )

    # For real LLM, pass the messages; for fake LLM, pass a simple dict
    if isinstance(llm_client, ChatOpenAI):
        result = llm_client.invoke(messages)
    else:
        # FakeChatLLM ignores the LCEL messages and expects a dict
        result = llm_client.invoke(
            {
                "question": question,
                "context": context_str,
                "metrics": metrics_str or "[no metrics available]",
            }
        )

    return result.content or ""
