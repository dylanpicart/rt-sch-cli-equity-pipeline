from typing import List, Dict, Any
import snowflake.connector

from .config import get_settings
from .embeddings import embed_texts
from .vector_store import upsert_documents

settings = get_settings()


def _snowflake_connection():
    """
    Create a Snowflake connection using config settings.
    Assumes DATABASE=SCHOOL_CLIMATE and SCHEMA=GOLD in .env.
    """
    return snowflake.connector.connect(
        account=settings.SNOWFLAKE_ACCOUNT,
        user=settings.SNOWFLAKE_USER,
        password=settings.SNOWFLAKE_PASSWORD,
        warehouse=settings.SNOWFLAKE_WAREHOUSE,
        database=settings.SNOWFLAKE_DATABASE,
        schema=settings.SNOWFLAKE_SCHEMA,
    )


def fetch_gold_text_rows() -> List[Dict[str, Any]]:
    """
    Pull text for RAG embeddings from:

      1. GOLD.DIM_CLIMATE_QUESTION
         - semantic info about climate survey questions

      2. GOLD.DIM_CLIMATE_METRIC_DEFINITION
         - semantic info about climate metrics (e.g. response rates)

      3. GOLD.DIM_SVI_DEFINITION
         - semantic info about SVI themes, metrics, and bucket logic

      4. BRONZE_GOLD.GOLD_CLIMATE_VULNERABILITY
         - numeric SVI/RPL scores per tract, turned into narrative text
    """

    query = """
      ---------------------------------------
      -- 1. Climate survey questions (GOLD)
      ---------------------------------------
      SELECT
          'climate_question' AS source_type,
          QUESTION_ID AS source_id,
          NULL AS district_id,
          NULL AS school_id,
          CONCAT(
              '[', SURVEY_GROUP, ' / ', DOMAIN, '] ',
              SHORT_QUESTION_TEXT,
              ' (scale: ', RESPONSE_SCALE, ')'
          ) AS text
      FROM DIM_CLIMATE_QUESTION
      WHERE IS_ACTIVE = TRUE

      UNION ALL

      ---------------------------------------
      -- 2. Climate metric definitions (GOLD)
      ---------------------------------------
      SELECT
          'climate_metric' AS source_type,
          METRIC_NAME AS source_id,
          NULL AS district_id,
          NULL AS school_id,
          CONCAT(
              METRIC_LABEL,
              ' – ',
              DEFINITION_TEXT,
              ' Formula: ',
              FORMULA_TEXT
          ) AS text
      FROM DIM_CLIMATE_METRIC_DEFINITION
      WHERE IS_ACTIVE = TRUE

      UNION ALL

      ---------------------------------------
      -- 3. SVI semantic definitions (GOLD)
      ---------------------------------------
      SELECT
          'svi_definition' AS source_type,
          THEME_ID AS source_id,
          NULL AS district_id,
          NULL AS school_id,
          CONCAT(
              '[SVI ', THEME_ID, '] ',
              THEME_NAME, ': ',
              THEME_DESCRIPTION,
              ' Metric: ', METRIC_NAME,
              ' – ', METRIC_DESCRIPTION,
              CASE
                  WHEN BUCKET_DEFINITION IS NOT NULL AND BUCKET_DEFINITION <> ''
                      THEN CONCAT(' Buckets: ', BUCKET_DEFINITION)
                  ELSE ''
              END
          ) AS text
      FROM DIM_SVI_DEFINITION
      WHERE IS_ACTIVE = TRUE

      UNION ALL

      ---------------------------------------
      -- 4. SVI / climate vulnerability by tract (BRONZE_GOLD)
      ---------------------------------------
      SELECT
          'svi_tract' AS source_type,
          TRACT_FIPS AS source_id,
          NULL AS district_id,
          NULL AS school_id,
          CONCAT(
              'Census tract ', TRACT_FIPS,
              ' has SVI overall score ', TO_CHAR(SVI_OVERALL_SCORE),
              ' (bucket: ', SVI_OVERALL_BUCKET, '), ',
              'themes: [',
                  'RPL_THEME1=', TO_CHAR(RPL_THEME1), ', ',
                  'RPL_THEME2=', TO_CHAR(RPL_THEME2), ', ',
                  'RPL_THEME3=', TO_CHAR(RPL_THEME3), ', ',
                  'RPL_THEME4=', TO_CHAR(RPL_THEME4),
              ']'
          ) AS text
      FROM BRONZE_GOLD.GOLD_CLIMATE_VULNERABILITY
    """

    conn = _snowflake_connection()
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cols = [c[0].lower() for c in cur.description]
        return [dict(zip(cols, row)) for row in rows]
    finally:
        conn.close()


def build_and_upsert_index():
    """
    Build the embedding index by:
      - fetching climate question text, climate metric definitions,
        SVI semantic definitions, and SVI tract summaries
      - embedding them
      - upserting into the Chroma vector store
    """
    rows = fetch_gold_text_rows()
    if not rows:
        print("No rows found for RAG index.")
        return

    ids: List[str] = []
    texts: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    for r in rows:
        doc_id = f"{r['source_type']}::{r['source_id']}"
        ids.append(doc_id)
        texts.append(r["text"])
        metadatas.append(
            {
                "source_type": r["source_type"],
                "source_id": r["source_id"],
                "district_id": r.get("district_id"),
                "school_id": r.get("school_id"),
            }
        )

    embeddings = embed_texts(texts)
    upsert_documents(
        ids=ids,
        texts=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    print(f"Upserted {len(ids)} documents into vector store.")


if __name__ == "__main__":
    build_and_upsert_index()
