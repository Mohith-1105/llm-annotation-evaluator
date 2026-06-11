# LLM Response Annotation & Quality Evaluation Framework

A Python-based pipeline to evaluate and annotate Large Language Model (LLM) responses across multiple categories. Built as a hands-on AI data annotation project demonstrating skills relevant to LLM training and evaluation workflows.

---

## 📌 Project Overview

This project simulates the core workflow of a **Data Annotation AI Specialist**:
- Generating LLM responses across diverse prompt categories
- Manually annotating responses for quality dimensions
- Analyzing annotation data and producing structured reports

---

## 🗂️ Project Structure

```
llm_evaluator/
│
├── step1_fetch_responses.py   # Fetches 30 LLM responses via Gemini API → saves to CSV
├── step2_analyze.py           # Reads annotated CSV → generates charts + Excel report
├── llm_responses.csv          # Generated after Step 1 (fill in annotations manually)
├── llm_annotation_report.xlsx # Generated after Step 2 (full analysis report)
├── charts/                    # Auto-generated chart images
│   ├── chart1_accuracy_clarity.png
│   ├── chart2_hallucination_pie.png
│   ├── chart3_tone_stacked.png
│   └── chart4_scatter.png
└── README.md
```

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install pandas matplotlib openpyxl requests
```

### 2. Get a free Gemini API Key
- Visit https://aistudio.google.com
- Sign in → Click **"Get API Key"** → **"Create API Key"**
- Copy and paste it into `step1_fetch_responses.py`

---

## 🚀 How to Run

### Step 1 — Fetch LLM Responses
```bash
python step1_fetch_responses.py
```
This creates `llm_responses.csv` with 30 prompts and their LLM responses.

### Step 2 — Annotate (Manual)
Open `llm_responses.csv` and fill in these 4 columns for each row:

| Column | Valid Values | Description |
|--------|-------------|-------------|
| `accuracy_1_to_5` | 1, 2, 3, 4, 5 | How factually correct is the response? |
| `clarity_1_to_5` | 1, 2, 3, 4, 5 | How clear and readable is the response? |
| `hallucination_yes_no` | Yes / No | Did the model make up facts? |
| `tone_appropriate` | Appropriate / Not | Is the tone suitable for the prompt? |

You can also add free-text notes in the `your_notes` column.

### Step 3 — Analyze & Report
```bash
python step2_analyze.py
```
This generates:
- 4 analysis charts in the `charts/` folder
- A full Excel report: `llm_annotation_report.xlsx`

---

## 📊 Annotation Schema

### Accuracy (1–5)
| Score | Meaning |
|-------|---------|
| 5 | Completely accurate, no errors |
| 4 | Mostly accurate, minor issues |
| 3 | Partially accurate, some errors |
| 2 | Mostly inaccurate |
| 1 | Completely wrong |

### Clarity (1–5)
| Score | Meaning |
|-------|---------|
| 5 | Very clear and well-structured |
| 4 | Clear with minor confusion |
| 3 | Somewhat unclear |
| 2 | Hard to follow |
| 1 | Incomprehensible |

### Hallucination (Yes/No)
- **Yes** — Model stated false facts confidently
- **No** — No hallucinations detected

### Tone (Appropriate/Not)
- **Appropriate** — Tone matches the context and prompt
- **Not** — Tone is off (too casual, too harsh, too vague, etc.)

---

## 📁 Output

The Excel report contains 3 sheets:
1. **Annotated Data** — All 30 prompts with responses and your annotations
2. **Summary Stats** — Per-category averages and rates
3. **Charts** — All 4 visualizations embedded in the sheet

---

## 🧠 Skills Demonstrated

- LLM output evaluation and quality assessment
- Data annotation across multiple quality dimensions
- Hallucination detection methodology
- Structured data analysis with Pandas
- Data visualization with Matplotlib
- Report generation with OpenPyXL
- Working with REST APIs (Gemini)

---

## 👤 Author

**Mohith S** — B.E in Artificial Intelligence and Machine Learning  
Sri Sairam College of Engineering, Bangalore  
[LinkedIn](https://www.linkedin.com/in/mohith-s-207084322) | [GitHub](https://github.com/Mohith-1105)
