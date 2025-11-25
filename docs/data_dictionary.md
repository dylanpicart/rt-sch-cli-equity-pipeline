# Data Dictionary – NYC School Climate ELT Pipeline

This document describes the core datasets produced by the hybrid Dataproc (batch) and Databricks (streaming) ELT pipeline.
It covers Bronze, Silver, and Gold tables powering the Power BI dashboard.

---

## **BRONZE Layer (Raw Data)**

### **Table: BRONZE.SCHOOL_CLIMATE_RAW**

**Grain:** 1 row per Kafka event (streamed record).

**Description:**
Raw JSON events from Confluent Kafka containing school climate survey metadata.

| Column        | Type      | Description                                     |
| ------------- | --------- | ----------------------------------------------- |
| key           | STRING    | Kafka message key (unused in downstream models) |
| value         | STRING    | Raw JSON payload                                |
| topic         | STRING    | Kafka topic name                                |
| partition     | INT       | Kafka partition                                 |
| offset        | BIGINT    | Kafka offset                                    |
| timestamp     | TIMESTAMP | Event time                                      |
| timestampType | INT       | Kafka timestamp type                            |
| ingest_ts     | TIMESTAMP | Bronze ingestion timestamp                      |

---

## **SILVER Layer (Cleansed Data)**

### **Table: SILVER.SCHOOL_CLIMATE_CLEAN**

**Grain:** 1 row per school per year.

**Purpose:**
Normalized, typed, cleaned climate survey response rates.

| Column                | Type      | Description                               |
| --------------------- | --------- | ----------------------------------------- |
| dbn                   | STRING    | DOE school ID (“District-Borough-Number”) |
| school_name           | STRING    | School name                               |
| borough               | STRING    | Derived from DBN (M/X/K/Q/R)              |
| district_number       | INT       | Derived from DBN prefix                   |
| student_response_rate | FLOAT     | % of students who responded (0–1)         |
| teacher_response_rate | FLOAT     | % of teachers who responded (0–1)         |
| parent_response_rate  | FLOAT     | % of parents who responded (0–1)          |
| event_ts              | TIMESTAMP | Kafka event timestamp                     |
| ingest_ts             | TIMESTAMP | Silver load timestamp                     |
| load_ts               | TIMESTAMP | Snowflake load timestamp                  |

---

## **GOLD Layer (Analytics Tables)**

### **Table: GOLD.SCHOOL_CLIMATE_SNAPSHOT**

**Grain:** 1 row per school.

| Column                | Type   | Description                  |
| --------------------- | ------ | ---------------------------- |
| dbn                   | STRING | School ID                    |
| school_name           | STRING | School name                  |
| borough               | STRING | Borough                      |
| district_number       | INT    | District                     |
| student_response_rate | FLOAT  | Student survey participation |
| teacher_response_rate | FLOAT  | Teacher participation        |
| parent_response_rate  | FLOAT  | Parent participation         |

---

### **Table: GOLD.SCHOOL_CLIMATE_DISTRICT_SUMMARY**

**Grain:** 1 row per district.

| Column                    | Type   | Description                   |
| ------------------------- | ------ | ----------------------------- |
| borough                   | STRING | Borough                       |
| district_number           | INT    | School district               |
| schools_count             | INT    | Schools in district           |
| avg_student_response_rate | FLOAT  | Average student response rate |
| avg_teacher_response_rate | FLOAT  | Average teacher response rate |
| avg_parent_response_rate  | FLOAT  | Average parent response rate  |

---

### **Table: GOLD.SCHOOL_CLIMATE_BOROUGH_SUMMARY**

**Grain:** 1 row per borough.

Same structure as District Summary, aggregated at borough level.

---

## **Batch (SVI) Data**

### **Table: GOLD.GOLD_CLIMATE_VULNERABILITY**

**Grain:** 1 row per census tract.

| Column             | Type   | Description                                             |
| ------------------ | ------ | ------------------------------------------------------- |
| TRACT_FIPS         | STRING | Census tract ID                                         |
| SVI_OVERALL_SCORE  | FLOAT  | Overall vulnerability score (0–1 or -999 if suppressed) |
| SVI_OVERALL_BUCKET | STRING | Vulnerability category (“Low”, “Moderate”, “High”)      |
| RPL_THEME1         | FLOAT  | Socioeconomic theme                                     |
| RPL_THEME2         | FLOAT  | Household composition & disability                      |
| RPL_THEME3         | FLOAT  | Minority status & language                              |
| RPL_THEME4         | FLOAT  | Housing & transportation                                |

**Note:**
`-999` values indicate suppressed CDC data and must be cleaned/filtered.
