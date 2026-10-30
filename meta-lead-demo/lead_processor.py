"""Lead intake, classification, and queue-export demo for Meta Lead Ads CSVs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd


def classify_timeline(value: object) -> str:
    """Classify purchase timing as HOT (0-3 months), NURTURE (>3), or REVIEW.

    Numeric values are interpreted as months. Text can use clear month labels
    such as ``within 3 months``, ``4-6 months``, or ``not sure``. A range that
    crosses the 3-month cutoff is ambiguous and goes to REVIEW.
    """
    if value is None or pd.isna(value):
        return "REVIEW"

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        months = float(value)
        if months < 0:
            return "REVIEW"
        return "HOT" if months <= 3 else "NURTURE"

    text = str(value).strip().lower()
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    if not text:
        return "REVIEW"

    if text in {"not sure", "not sure yet", "unknown", "undecided", "researching"}:
        return "REVIEW" if text in {"not sure", "not sure yet", "unknown", "undecided"} else "NURTURE"

    if text in {"asap", "immediately", "this month", "within 3 months", "within the next 3 months", "0-3 months", "1-3 months"}:
        return "HOT"
    if text in {"over 3 months", "more than 3 months", "4-6 months", "7+ months", "6+ months", "later", "not within 3 months"}:
        return "NURTURE"

    within_match = re.fullmatch(r"within\s+(\d+(?:\.\d+)?)\s+months?", text)
    if within_match:
        return "HOT" if float(within_match.group(1)) <= 3 else "NURTURE"

    single_match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(?:months?|mos?|m)", text)
    if single_match:
        months = float(single_match.group(1))
        return "HOT" if months <= 3 else "NURTURE"

    range_match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:months?|mos?|m)?", text)
    if range_match:
        lower, upper = map(float, range_match.groups())
        if lower < 0 or upper < lower:
            return "REVIEW"
        if upper <= 3:
            return "HOT"
        if lower > 3:
            return "NURTURE"
        return "REVIEW"

    number_match = re.fullmatch(r"\d+(?:\.\d+)?", text)
    if number_match:
        months = float(text)
        if months < 0:
            return "REVIEW"
        return "HOT" if months <= 3 else "NURTURE"

    return "REVIEW"


def _has_contact_consent(value: object) -> bool:
    if value is None or pd.isna(value):
        return False
    return str(value).strip().lower() in {"yes", "y", "true", "1", "granted", "opt-in", "opted in"}


def _valid_phone(value: object) -> bool:
    if value is None or pd.isna(value):
        return False
    digits = re.sub(r"\D", "", str(value))
    return 7 <= len(digits) <= 15


def _valid_email(value: object) -> bool:
    if value is None or pd.isna(value):
        return False
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", str(value).strip()))


def _contact_channel(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    channel = str(value).strip().lower()
    aliases = {"call": "phone", "telephone": "phone", "text": "sms", "e-mail": "email"}
    return aliases.get(channel, channel)


def process_leads(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Classify leads and create safe next-action labels without contacting anyone."""
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("dataframe must be a pandas DataFrame")

    required = {
        "lead_id",
        "name",
        "phone",
        "email",
        "preferred_contact",
        "purchase_timeline",
        "contact_consent",
    }
    missing = sorted(required - set(dataframe.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    processed = dataframe.copy(deep=True)
    input_rows = len(processed)
    processed["lead_id"] = processed["lead_id"].astype("string").str.strip()
    has_id = processed["lead_id"].notna() & processed["lead_id"].ne("")
    duplicates = has_id & processed["lead_id"].duplicated(keep="first")
    processed = processed.loc[~duplicates].copy()
    duplicates_removed = int(duplicates.sum())

    processed["lead_status"] = processed["purchase_timeline"].map(classify_timeline)

    def next_action(row: pd.Series) -> str:
        if pd.isna(row["lead_id"]) or not str(row["lead_id"]).strip():
            return "MANUAL_REVIEW"

        status = row["lead_status"]
        if status == "REVIEW":
            return "MANUAL_REVIEW"
        if not _has_contact_consent(row["contact_consent"]):
            return "CONSENT_REQUIRED"

        channel = _contact_channel(row["preferred_contact"])
        if status == "HOT":
            if channel == "phone" and _valid_phone(row["phone"]):
                return "CALL_QUEUE"
            return "MANUAL_REVIEW"

        if channel == "email" and _valid_email(row["email"]):
            return "NURTURE_QUEUE"
        if channel == "sms" and _valid_phone(row["phone"]):
            return "NURTURE_QUEUE"
        return "MANUAL_REVIEW"

    processed["next_action"] = processed.apply(next_action, axis=1)
    counts = processed["lead_status"].value_counts()
    actions = processed["next_action"].value_counts()
    summary = {
        "input_rows": input_rows,
        "duplicates_removed": duplicates_removed,
        "processed_rows": len(processed),
        "hot": int(counts.get("HOT", 0)),
        "nurture": int(counts.get("NURTURE", 0)),
        "review": int(counts.get("REVIEW", 0)),
        "call_queue": int(actions.get("CALL_QUEUE", 0)),
        "nurture_queue": int(actions.get("NURTURE_QUEUE", 0)),
        "consent_required": int(actions.get("CONSENT_REQUIRED", 0)),
        "manual_review": int(actions.get("MANUAL_REVIEW", 0)),
    }
    return processed.reset_index(drop=True), summary


def run_pipeline(input_csv: str | Path, output_dir: str | Path) -> dict[str, object]:
    """Read a CSV export and write classified leads plus action queues.

    This demo is local and read-only toward the source. It never calls Meta,
    CRM, email, SMS, or Google Sheets APIs.
    """
    source = Path(input_csv).expanduser()
    destination = Path(output_dir).expanduser()
    if not source.is_file():
        raise FileNotFoundError(f"Input CSV not found: {source}")
    if source.suffix.lower() != ".csv":
        raise ValueError("This demo accepts CSV input files only")
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {destination}")

    leads = pd.read_csv(source, encoding="utf-8-sig")
    processed, summary = process_leads(leads)
    destination.mkdir(parents=True, exist_ok=True)

    outputs = {
        "classified_leads.csv": processed,
        "hot_call_queue.csv": processed.loc[processed["next_action"] == "CALL_QUEUE"],
        "nurture_queue.csv": processed.loc[processed["next_action"] == "NURTURE_QUEUE"],
        "manual_review.csv": processed.loc[
            processed["next_action"].isin({"MANUAL_REVIEW", "CONSENT_REQUIRED"})
        ],
    }
    for filename, dataframe in outputs.items():
        dataframe.to_csv(destination / filename, index=False, encoding="utf-8-sig")

    summary_path = destination / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "input": str(source),
        "output_dir": str(destination),
        "summary": summary,
        "files": [str(destination / filename) for filename in outputs] + [str(summary_path)],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Classify a local Meta Lead Ads CSV as HOT, NURTURE, or REVIEW "
            "and write follow-up queues. No messages are sent."
        )
    )
    parser.add_argument("input_csv", help="CSV exported from Meta Lead Ads or a CRM")
    parser.add_argument(
        "--output-dir",
        default="lead_output",
        help="New or empty folder for result files (default: lead_output)",
    )
    args = parser.parse_args(argv)

    try:
        result = run_pipeline(args.input_csv, args.output_dir)
    except (OSError, ValueError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    summary = result["summary"]
    print(f"Processed: {summary['input_rows']} input rows")
    print(f"Duplicates removed: {summary['duplicates_removed']}")
    print(
        f"Status: HOT={summary['hot']}  NURTURE={summary['nurture']}  REVIEW={summary['review']}"
    )
    print(
        "Queues: "
        f"CALL={summary['call_queue']}  NURTURE={summary['nurture_queue']}  "
        f"CONSENT_REQUIRED={summary['consent_required']}  "
        f"MANUAL_REVIEW={summary['manual_review']}"
    )
    print(f"Output folder: {result['output_dir']}")
    print("Demo mode: no API calls, emails, SMS messages, or CRM updates were made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
