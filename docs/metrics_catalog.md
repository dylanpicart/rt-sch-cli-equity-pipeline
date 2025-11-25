# Metrics Catalog – NYC School Climate & Vulnerability

This catalog defines each analytic metric produced in the Gold layer and displayed in the Power BI dashboard.

---

## **Climate Engagement Metrics (School Level)**

### **Student Response Rate**

**Definition:** % of students responding to the climate survey.
**Formula:**

```
student_response_rate = responses_students / total_enrolled_students
```

**Grain:** school (`dbn`)
**Source:** SILVER.SCHOOL_CLIMATE_CLEAN
**Used in:** KPI cards, histogram, heatmap, bar chart

---

### **Teacher Response Rate**

Same format as above.

---

### **Parent Response Rate**

Same format.

---

## **District-Level Metrics**

### **Avg Student Response Rate (District)**

**Definition:** Mean of student response rates across all schools in the district.
**Formula:**

```
AVG(student_response_rate)
```

**Grain:** district
**Source:** GOLD.SCHOOL_CLIMATE_DISTRICT_SUMMARY
**Used in:** dashboard visuals (parent page)

---

## **Borough-Level Metrics**

### **Avg Student Response Rate (Borough)**

Analogous to district metric.

---

## **SVI Metrics (Future Work)**

### **SVI Overall Score**

**Definition:** CDC Social Vulnerability Index score (0–1).
**Status:** Contains `-999` suppressed placeholders requiring cleaning.
**Usage:** Future equity integrations.

---

### **SVI Bucket Distribution**

**Definition:** Count of tracts in Low/Moderate/High buckets.
**Usage:** SVI Context page (in progress).

---

### **District SVI Score (Future)**

**Definition:** Avg SVI score for tracts within a given district.
**Dependency:** Requires tract → district crosswalk.
**Status:** Planned.

---

### **Equity Gap Metrics (Future)**

Examples:

* District response rate minus district SVI score
* School response rate percentile within district
* SVI-adjusted engagement index

These will be added once SVI data is cleaned and aggregated.
