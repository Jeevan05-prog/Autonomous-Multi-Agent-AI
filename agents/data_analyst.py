import os
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


CHART_FOLDER = "outputs/charts"
ANALYSIS_FOLDER = "outputs/analysis"

os.makedirs(CHART_FOLDER, exist_ok=True)
os.makedirs(ANALYSIS_FOLDER, exist_ok=True)


def clear_charts():
    for name in os.listdir(CHART_FOLDER):
        if name.endswith(".png"):
            os.remove(os.path.join(CHART_FOLDER, name))


def save_analysis(text):
    with open(
        os.path.join(ANALYSIS_FOLDER, "data_analysis.txt"),
        "w",
        encoding="utf-8"
    ) as file:
        file.write(text)


def analyze_cybersecurity_topic():

    clear_charts()

    years = [2021, 2022, 2023, 2024, 2025]

    losses = [6.9, 10.3, 12.5, 16.6, 20.877]

    complaints = [
        847376,
        800944,
        880418,
        859532,
        1008597
    ]

    # GRAPH 1: Reported internet-crime losses

    plt.figure(figsize=(10, 5))

    plt.plot(
        years,
        losses,
        marker="o",
        linewidth=2
    )

    plt.title(
        "Reported Internet Crime Losses (FBI IC3, 2021–2025)"
    )

    plt.xlabel("Year")
    plt.ylabel("Reported losses (USD billions)")

    plt.xticks(years)
    plt.grid(alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        os.path.join(CHART_FOLDER, "total_trend.png"),
        dpi=160
    )

    plt.close()

    # GRAPH 2: Number of complaints

    plt.figure(figsize=(10, 5))

    plt.bar(
        [str(year) for year in years],
        complaints
    )

    plt.title(
        "Internet Crime Complaints Received by FBI IC3"
    )

    plt.xlabel("Year")
    plt.ylabel("Number of complaints")

    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        os.path.join(CHART_FOLDER, "category_trends.png"),
        dpi=160
    )

    plt.close()

    analysis = """
CYBERSECURITY CONTEXTUAL DATA ANALYSIS
======================================

Dataset:
FBI Internet Crime Complaint Center (IC3) annual reports.

1. REPORTED INTERNET-CRIME LOSSES

Year       Reported Losses
2021       $6.9 billion
2022       $10.3 billion
2023       $12.5 billion
2024       $16.6 billion
2025       $20.877 billion

2. INTERNET-CRIME COMPLAINTS

Year       Complaints
2021       847,376
2022       800,944
2023       880,418
2024       859,532
2025       1,008,597

3. OBSERVATIONS

- Reported financial losses increased across the period.
- The highest reported losses in this series occurred in 2025.
- Complaint numbers did not increase every year.
- Financial losses and complaint counts measure different things.

4. IMPORTANT LIMITATION

These figures describe broader internet crime reported to FBI IC3.
They do NOT measure only AI-powered cyberattacks.

They are included as contextual evidence for the cybersecurity
research topic, not as a direct measurement of AI attack frequency.

The 2026 full-year report is not yet available.

5. SOURCE REFERENCES

2021 FBI Internet Crime Report:
https://www.fbi.gov/news/press-releases/fbi-releases-the-internet-crime-complaint-center-2021-internet-crime-report

2024 FBI Internet Crime Report:
https://www.fbi.gov/news/press-releases/fbi-releases-annual-internet-crime-report

2025 FBI Internet Crime Report:
https://www.fbi.gov/news/press-releases/cryptocurrency-and-ai-scams-bilk-americans-of-billions
"""

    save_analysis(analysis)

    return analysis


def analyze_csv(file_path):

    if not file_path or not os.path.isfile(file_path):
        return "No valid CSV dataset was supplied."

    clear_charts()

    try:
        df = pd.read_csv(file_path)

        if df.empty:
            return "The uploaded CSV is empty."

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        result = [
            "UPLOADED DATASET ANALYSIS",
            "=========================",
            f"Rows: {len(df)}",
            f"Columns: {len(df.columns)}",
            f"Column names: {list(df.columns)}",
            "",
            "MISSING VALUES",
            str(df.isnull().sum()),
            "",
            "DUPLICATE ROWS",
            str(df.duplicated().sum()),
            "",
            "DESCRIPTIVE STATISTICS",
            str(df.describe().round(2))
        ]

        if numeric_columns:

            # Plot numeric columns from the actual CSV.

            plt.figure(figsize=(10, 5))

            for column in numeric_columns[:6]:

                plt.plot(
                    df.index,
                    df[column],
                    marker="o",
                    label=column
                )

            plt.title("Uploaded Dataset: Numeric Measures")
            plt.xlabel("Record")
            plt.ylabel("Recorded value")

            plt.legend()
            plt.grid(alpha=0.3)

            plt.tight_layout()

            plt.savefig(
                os.path.join(CHART_FOLDER, "category_trends.png"),
                dpi=160
            )

            plt.close()

            result.append(
                "\nNUMERIC COLUMN STATISTICS"
            )

            for column in numeric_columns:

                result.append(
                    f"{column}: "
                    f"Mean={df[column].mean():.2f}, "
                    f"Minimum={df[column].min():.2f}, "
                    f"Maximum={df[column].max():.2f}"
                )

        else:

            result.append(
                "\nNo numeric columns were available for chart generation."
            )

        analysis = "\n".join(result)

        save_analysis(analysis)

        return analysis

    except Exception as error:

        return (
            "Data analysis failed: "
            f"{type(error).__name__}: {error}"
        )


def data_analyst_agent(state):

    dataset_path = str(
        state.get("dataset_path", "") or ""
    ).strip()

    topic = state.get("user_request", "").lower()

    if dataset_path:

        state["analysis"] = analyze_csv(dataset_path)

    elif any(word in topic for word in [
        "cybersecurity",
        "cyber attack",
        "cyberattack",
        "cybercrime",
        "ransomware",
        "malware",
        "threat detection",
        "phishing"
    ]):

        state["analysis"] = analyze_cybersecurity_topic()

    else:

        clear_charts()

        state["analysis"] = (
            "WEB RESEARCH ONLY\n\n"
            "No CSV dataset was uploaded. "
            "No topic-specific numerical dataset was available "
            "for statistical chart generation. "
            "No numerical values have been invented."
        )

        save_analysis(state["analysis"])

    return state