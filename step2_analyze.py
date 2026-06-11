"""
STEP 2 — Analyze Annotated Responses & Generate Report
=======================================================
Run this AFTER you have manually filled in the annotation columns in 'llm_responses.csv'.

What this script does:
  1. Validates your annotations
  2. Generates 4 charts (bar, pie, heatmap, scatter)
  3. Saves a full Excel report with stats + charts
  4. Prints a summary in the terminal
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
import sys
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


# ── Constants ────────────────────────────────────────────────────────────────
INPUT_FILE  = "llm_responses.csv"
OUTPUT_FILE = "llm_annotation_report.xlsx"
CHART_DIR   = "charts"
CATEGORIES  = ["Factual", "Creative", "Coding", "Ethical", "Summarization", "Instruction-Following"]
COLORS      = ["#4C9BE8", "#F4845F", "#6FCF97", "#BB6BD9", "#F2C94C", "#56CCF2"]


# ── Helpers ──────────────────────────────────────────────────────────────────
def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Check annotations are filled and valid; exit with clear error if not."""
    required = ["accuracy_1_to_5", "clarity_1_to_5", "hallucination_yes_no", "tone_appropriate"]
    missing_rows = df[df[required].isin(["", None, float("nan")]).any(axis=1)]

    if not missing_rows.empty:
        ids = missing_rows["prompt_id"].tolist()
        print(f"❌ Found {len(missing_rows)} unannotated row(s): Prompt IDs {ids}")
        print("   Please fill in ALL 4 annotation columns in 'llm_responses.csv' and re-run.")
        sys.exit(1)

    # Coerce types
    df["accuracy_1_to_5"]  = pd.to_numeric(df["accuracy_1_to_5"],  errors="coerce")
    df["clarity_1_to_5"]   = pd.to_numeric(df["clarity_1_to_5"],   errors="coerce")
    df["hallucination_yes_no"] = df["hallucination_yes_no"].str.strip().str.capitalize()
    df["tone_appropriate"]     = df["tone_appropriate"].str.strip().str.capitalize()

    invalid_acc = df[~df["accuracy_1_to_5"].between(1, 5)]
    invalid_cla = df[~df["clarity_1_to_5"].between(1, 5)]
    invalid_hal = df[~df["hallucination_yes_no"].isin(["Yes", "No"])]
    invalid_ton = df[~df["tone_appropriate"].isin(["Appropriate", "Not"])]

    errors = []
    if not invalid_acc.empty: errors.append(f"accuracy_1_to_5 must be 1–5 (rows: {invalid_acc['prompt_id'].tolist()})")
    if not invalid_cla.empty: errors.append(f"clarity_1_to_5 must be 1–5 (rows: {invalid_cla['prompt_id'].tolist()})")
    if not invalid_hal.empty: errors.append(f"hallucination_yes_no must be 'Yes' or 'No' (rows: {invalid_hal['prompt_id'].tolist()})")
    if not invalid_ton.empty: errors.append(f"tone_appropriate must be 'Appropriate' or 'Not' (rows: {invalid_ton['prompt_id'].tolist()})")

    if errors:
        print("❌ Annotation validation failed:")
        for e in errors: print(f"   • {e}")
        sys.exit(1)

    print("✅ All 30 annotations validated successfully.\n")
    return df


def ensure_chart_dir():
    os.makedirs(CHART_DIR, exist_ok=True)


# ── Chart 1: Average Accuracy & Clarity per Category ─────────────────────────
def chart_accuracy_clarity(df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(10, 5))
    category_stats = df.groupby("category")[["accuracy_1_to_5", "clarity_1_to_5"]].mean().reindex(CATEGORIES)

    x = np.arange(len(CATEGORIES))
    width = 0.35
    bars1 = ax.bar(x - width/2, category_stats["accuracy_1_to_5"], width, label="Accuracy", color="#4C9BE8", edgecolor="white")
    bars2 = ax.bar(x + width/2, category_stats["clarity_1_to_5"],  width, label="Clarity",  color="#6FCF97", edgecolor="white")

    ax.set_xlabel("Category", fontsize=11)
    ax.set_ylabel("Average Score (1–5)", fontsize=11)
    ax.set_title("Average Accuracy & Clarity Scores by Category", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(CATEGORIES, rotation=15, ha="right")
    ax.set_ylim(0, 5.5)
    ax.legend()
    ax.yaxis.grid(True, alpha=0.4)
    ax.set_axisbelow(True)

    for bar in bars1: ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=8)
    for bar in bars2: ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    path = os.path.join(CHART_DIR, "chart1_accuracy_clarity.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


# ── Chart 2: Hallucination Rate per Category (Pie) ───────────────────────────
def chart_hallucination_pie(df: pd.DataFrame) -> str:
    hallucination_counts = df["hallucination_yes_no"].value_counts()
    labels = hallucination_counts.index.tolist()
    sizes  = hallucination_counts.values.tolist()
    pie_colors = ["#F4845F" if l == "Yes" else "#6FCF97" for l in labels]

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=pie_colors, autopct="%1.1f%%",
        startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 2}
    )
    for t in autotexts: t.set_fontsize(12)
    ax.set_title("Hallucination Rate Across All Responses", fontsize=13, fontweight="bold")

    plt.tight_layout()
    path = os.path.join(CHART_DIR, "chart2_hallucination_pie.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


# ── Chart 3: Tone Appropriateness per Category (Stacked Bar) ─────────────────
def chart_tone_stacked(df: pd.DataFrame) -> str:
    tone_data = df.groupby(["category", "tone_appropriate"]).size().unstack(fill_value=0).reindex(CATEGORIES)
    for col in ["Appropriate", "Not"]:
        if col not in tone_data.columns:
            tone_data[col] = 0

    fig, ax = plt.subplots(figsize=(10, 5))
    tone_data.plot(kind="bar", stacked=True, ax=ax, color=["#6FCF97", "#F4845F"], edgecolor="white")
    ax.set_xlabel("Category", fontsize=11)
    ax.set_ylabel("Number of Responses", fontsize=11)
    ax.set_title("Tone Appropriateness by Category", fontsize=13, fontweight="bold")
    ax.set_xticklabels(CATEGORIES, rotation=15, ha="right")
    ax.legend(title="Tone", loc="upper right")
    ax.yaxis.grid(True, alpha=0.4)
    ax.set_axisbelow(True)

    plt.tight_layout()
    path = os.path.join(CHART_DIR, "chart3_tone_stacked.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


# ── Chart 4: Accuracy vs Clarity Scatter ─────────────────────────────────────
def chart_scatter(df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(7, 6))
    cat_to_color = {c: COLORS[i] for i, c in enumerate(CATEGORIES)}
    
    for cat in CATEGORIES:
        subset = df[df["category"] == cat]
        ax.scatter(subset["accuracy_1_to_5"], subset["clarity_1_to_5"],
                   label=cat, color=cat_to_color[cat], s=80, alpha=0.85, edgecolors="white")

    ax.set_xlabel("Accuracy Score (1–5)", fontsize=11)
    ax.set_ylabel("Clarity Score (1–5)", fontsize=11)
    ax.set_title("Accuracy vs Clarity — All Responses", fontsize=13, fontweight="bold")
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.legend(fontsize=8, loc="lower right")
    ax.xaxis.grid(True, alpha=0.3)
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    # Diagonal reference line
    ax.plot([1, 5], [1, 5], "--", color="gray", alpha=0.4, linewidth=1)

    plt.tight_layout()
    path = os.path.join(CHART_DIR, "chart4_scatter.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


# ── Excel Report ─────────────────────────────────────────────────────────────
def style_header_row(ws, row, n_cols, fill_hex="1F4E79"):
    fill = PatternFill("solid", fgColor=fill_hex)
    font = Font(bold=True, color="FFFFFF", size=11)
    align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for col in range(1, n_cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.fill, cell.font, cell.alignment, cell.border = fill, font, align, border


def style_data_row(ws, row, n_cols, even: bool):
    fill_hex = "EBF3FB" if even else "FFFFFF"
    fill = PatternFill("solid", fgColor=fill_hex)
    thin = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    align = Alignment(vertical="center", wrap_text=True)
    for col in range(1, n_cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.fill, cell.border, cell.alignment = fill, border, align


def build_excel(df: pd.DataFrame, chart_paths: list):
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        # ── Sheet 1: Raw Annotated Data ──────────────────────────────────────
        df.to_excel(writer, sheet_name="Annotated Data", index=False)
        ws1 = writer.sheets["Annotated Data"]
        style_header_row(ws1, 1, len(df.columns))
        for row_idx in range(2, len(df) + 2):
            style_data_row(ws1, row_idx, len(df.columns), even=(row_idx % 2 == 0))
        col_widths = [8, 20, 50, 60, 15, 15, 20, 18, 30]
        for i, w in enumerate(col_widths, 1):
            ws1.column_dimensions[get_column_letter(i)].width = w
        ws1.row_dimensions[1].height = 30

        # ── Sheet 2: Summary Statistics ───────────────────────────────────────
        summary_data = []
        for cat in CATEGORIES:
            subset = df[df["category"] == cat]
            summary_data.append({
                "Category":              cat,
                "Prompts":               len(subset),
                "Avg Accuracy":          round(subset["accuracy_1_to_5"].mean(), 2),
                "Avg Clarity":           round(subset["clarity_1_to_5"].mean(), 2),
                "Hallucination Rate (%)":round((subset["hallucination_yes_no"] == "Yes").mean() * 100, 1),
                "Tone Appropriate (%)":  round((subset["tone_appropriate"] == "Appropriate").mean() * 100, 1),
            })

        # Overall row
        summary_data.append({
            "Category":              "OVERALL",
            "Prompts":               len(df),
            "Avg Accuracy":          round(df["accuracy_1_to_5"].mean(), 2),
            "Avg Clarity":           round(df["clarity_1_to_5"].mean(), 2),
            "Hallucination Rate (%)":round((df["hallucination_yes_no"] == "Yes").mean() * 100, 1),
            "Tone Appropriate (%)":  round((df["tone_appropriate"] == "Appropriate").mean() * 100, 1),
        })

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name="Summary Stats", index=False)
        ws2 = writer.sheets["Summary Stats"]
        style_header_row(ws2, 1, len(summary_df.columns))
        for row_idx in range(2, len(summary_df) + 2):
            is_overall = row_idx == len(summary_df) + 1
            if is_overall:
                fill = PatternFill("solid", fgColor="FFF2CC")
                font = Font(bold=True, size=11)
                for col in range(1, len(summary_df.columns) + 1):
                    ws2.cell(row=row_idx, column=col).fill = fill
                    ws2.cell(row=row_idx, column=col).font = font
            else:
                style_data_row(ws2, row_idx, len(summary_df.columns), even=(row_idx % 2 == 0))
        for i, w in enumerate([22, 10, 15, 14, 22, 22], 1):
            ws2.column_dimensions[get_column_letter(i)].width = w

        # ── Sheet 3: Charts ───────────────────────────────────────────────────
        ws3 = writer.book.create_sheet("Charts")
        ws3.sheet_view.showGridLines = False
        ws3["A1"] = "LLM Annotation Quality Report — Charts"
        ws3["A1"].font = Font(bold=True, size=16, color="1F4E79")
        ws3["A1"].alignment = Alignment(horizontal="center")
        ws3.merge_cells("A1:R1")

        positions = ["A3", "J3", "A30", "J30"]
        for path, pos in zip(chart_paths, positions):
            if os.path.exists(path):
                img = XLImage(path)
                img.width, img.height = 480, 300
                ws3.add_image(img, pos)

    print(f"📊 Excel report saved: {os.path.abspath(OUTPUT_FILE)}")


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    # Load CSV
    if not os.path.exists(INPUT_FILE):
        print(f"❌ '{INPUT_FILE}' not found. Please run step1_fetch_responses.py first.")
        sys.exit(1)

    df = pd.read_csv(INPUT_FILE, dtype=str)
    df = df.fillna("")

    print("=" * 55)
    print("  LLM Annotation Analysis — Step 2")
    print("=" * 55)

    df = validate_dataframe(df)
    ensure_chart_dir()

    print("📈 Generating charts...")
    chart_paths = [
        chart_accuracy_clarity(df),
        chart_hallucination_pie(df),
        chart_tone_stacked(df),
        chart_scatter(df),
    ]
    print(f"   ✅ 4 charts saved to '{CHART_DIR}/' folder.\n")

    print("📝 Building Excel report...")
    build_excel(df, chart_paths)

    # Terminal summary
    print("\n" + "=" * 55)
    print("  SUMMARY")
    print("=" * 55)
    print(f"  Total Responses Analyzed : 30")
    print(f"  Avg Accuracy Score       : {df['accuracy_1_to_5'].mean():.2f} / 5.00")
    print(f"  Avg Clarity Score        : {df['clarity_1_to_5'].mean():.2f} / 5.00")
    print(f"  Hallucination Rate       : {(df['hallucination_yes_no']=='Yes').mean()*100:.1f}%")
    print(f"  Tone Appropriate         : {(df['tone_appropriate']=='Appropriate').mean()*100:.1f}%")
    print("=" * 55)
    print(f"\n✅ All done! Open '{OUTPUT_FILE}' to view your full report.")


if __name__ == "__main__":
    main()