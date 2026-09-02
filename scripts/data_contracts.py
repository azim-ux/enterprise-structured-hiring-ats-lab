#!/usr/bin/env python3
"""Deterministic, privacy-safe contracts for the synthetic hiring datasets."""

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from html.parser import HTMLParser
from pathlib import Path


TABLE_FILES = {
    "requisitions": "synthetic_requisitions.csv",
    "candidates": "synthetic_candidates.csv",
    "interviews": "synthetic_interviews.csv",
}

SCHEMAS = {
    "requisitions": (
        "Requisition_ID", "Job_Title", "Department", "Grade",
        "Hiring_Manager_ID", "Target_Headcount", "Open_Date", "Close_Date",
        "Days_to_Fill", "Status", "Sourcing_Channel_Primary",
        "Total_Applicants", "Shortlisted", "Interviewed", "Offered", "Hired",
    ),
    "candidates": (
        "Candidate_ID", "Full_Name", "Gender", "Demographic_Cohort",
        "Requisition_ID", "Applied_Date", "Source_Channel", "Current_Stage",
        "Disposition_Reason", "Resume_Screen_Score", "Phone_Screen_Score",
        "Work_Sample_Score", "Structured_Interview_Score",
        "Job_Knowledge_Score", "Composite_Score",
        "Subjective_Impression_Score", "Bias_Variance_Gap",
        "Offer_Extended", "Offer_Accepted", "Hired_Date",
    ),
    "interviews": (
        "Interview_ID", "Candidate_ID", "Requisition_ID", "Stage_Name",
        "Interviewer_ID", "Interviewer_Role", "Scheduled_Date",
        "Feedback_Submitted_Date", "Turnaround_Hours", "SLA_Met",
        "BARS_Score_1", "BARS_Score_2", "BARS_Score_3", "BARS_Score_4",
        "Mean_BARS_Score", "Notes_Summary",
    ),
}

NULLABLE_CANDIDATE_FIELDS = {
    "Phone_Screen_Score", "Work_Sample_Score", "Structured_Interview_Score",
    "Job_Knowledge_Score", "Composite_Score", "Subjective_Impression_Score",
    "Bias_Variance_Gap", "Hired_Date",
}

SOURCE_CHANNELS = {
    "LinkedIn Recruiter", "Direct Career Portal", "Employee Referral",
    "Skills Academy", "Regional Hiring Drive",
}

ENUMS = {
    "requisitions": {
        "Department": {"Engineering", "People & Culture", "Quality", "Supply Chain"},
        "Grade": {"APD-G1", "APD-G2", "APD-G3", "APD-G4"},
        "Status": {"Filled"},
        "Sourcing_Channel_Primary": SOURCE_CHANNELS,
    },
    "candidates": {
        "Gender": {"Male", "Female"},
        "Demographic_Cohort": {"Reference Group", "Focal Group"},
        "Source_Channel": SOURCE_CHANNELS,
        "Current_Stage": {"Application Review", "Shortlisted", "Interview Complete", "Hired"},
        "Disposition_Reason": {
            "Selected - highest governed composite",
            "Composite below requisition threshold",
            "Halo Effect control - evidence did not support override",
            "Not advanced to standardized assessment",
            "Automated job-related knockout criteria not met",
        },
        "Offer_Extended": {"Yes", "No"},
        "Offer_Accepted": {"Yes", "No"},
    },
    "interviews": {
        "Stage_Name": {
            "Work Sample Review", "Structured Interview A",
            "Structured Interview B", "Calibration Review",
        },
        "Interviewer_Role": {
            "Technical Assessor", "Hiring Manager",
            "Cross-functional Panelist", "Talent Acquisition Partner",
        },
        "SLA_Met": {"Yes", "No"},
    },
}

EXPECTED_REQUISITIONS = {
    "REQ-2026-ENG-G4": (800, 197, 100, 10, 10),
    "REQ-2026-ENG-G1": (1600, 395, 200, 60, 60),
    "REQ-2026-QUA-G3": (600, 148, 75, 15, 15),
    "REQ-2026-PNC-G2": (400, 98, 50, 10, 10),
    "REQ-2026-SCM-G2": (600, 148, 75, 25, 25),
}

EXPECTED_COHORTS_BY_REQUISITION = {
    "REQ-2026-ENG-G4": ((480, 320), (125, 72), (60, 40), (6, 4)),
    "REQ-2026-ENG-G1": ((960, 640), (250, 145), (120, 80), (36, 24)),
    "REQ-2026-QUA-G3": ((360, 240), (94, 54), (45, 30), (9, 6)),
    "REQ-2026-PNC-G2": ((240, 160), (62, 36), (30, 20), (6, 4)),
    "REQ-2026-SCM-G2": ((360, 240), (93, 55), (45, 30), (15, 10)),
}

GOVERNED_DISPLAY_MARKERS = (
    '<div class="kpi-label">Applicants</div><div class="kpi-value">4,000</div>',
    '<div class="kpi-label">Conversion</div><div class="kpi-value">3.0%</div>',
    '<div class="kpi-label">Time to fill</div><div class="kpi-value">28.5d</div>',
    '<div class="kpi-label">Feedback SLA</div><div class="kpi-value">91.8%</div>',
    '<div class="kpi-label">Adverse impact ratio</div><div class="kpi-value">0.87</div>',
    "4,000 applied → 986 shortlisted → 500 assessed → 120 hired.",
    "1,836 / 2,000 at or below 48 hours",
)

HALO_CONTROL = {
    "Work_Sample_Score": "4.00",
    "Structured_Interview_Score": "3.80",
    "Job_Knowledge_Score": "4.00",
    "Composite_Score": "3.92",
    "Subjective_Impression_Score": "4.60",
    "Bias_Variance_Gap": "0.68",
    "Current_Stage": "Interview Complete",
    "Disposition_Reason": "Halo Effect control - evidence did not support override",
    "Offer_Extended": "No",
    "Offer_Accepted": "No",
    "Hired_Date": "",
}

ID_PATTERNS = {
    "Requisition_ID": re.compile(r"^REQ-2026-(?:ENG-G[14]|QUA-G3|PNC-G2|SCM-G2)$"),
    "Candidate_ID": re.compile(r"^CAND-2026-\d{4}$"),
    "Interview_ID": re.compile(r"^INT-2026-\d{4}$"),
    "Hiring_Manager_ID": re.compile(r"^APD-MGR-0[1-5]$"),
    "Interviewer_ID": re.compile(r"^APD-INT-(?:00[1-9]|0[1-5]\d|060)$"),
}


@dataclass(frozen=True)
class Finding:
    category: str
    record_key: str
    field: str


@dataclass
class Snapshot:
    headers: dict
    tables: dict
    embedded: dict
    dashboard_html: dict
    slides_html: str
    load_findings: list = field(default_factory=list)


@dataclass(frozen=True)
class PageState:
    current_page: int
    total_pages: int
    start: int
    stop: int
    previous_disabled: bool
    next_disabled: bool

    def as_tuple(self):
        return (
            self.current_page, self.total_pages, self.start, self.stop,
            self.previous_disabled, self.next_disabled,
        )


def _finding(category, key, field):
    return Finding(category, str(key or "dataset"), str(field or "record"))


def format_findings(findings):
    return "\n".join(
        f"- {item.category}: {item.record_key[:48]} [{item.field[:48]}]"
        for item in findings
    )


def csv_structure_findings(path, expected_header, table):
    findings = []
    try:
        with Path(path).open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            header = tuple(reader.fieldnames or ())
            if header != tuple(expected_header) or len(header) != len(set(header)):
                findings.append(_finding("schema", table, "header"))
            for number, row in enumerate(reader, 1):
                if None in row or any(value is None for value in row.values()):
                    findings.append(_finding("schema", f"{table}:{number}", "row shape"))
    except (OSError, csv.Error, UnicodeError):
        findings.append(_finding("schema", table, "read"))
    return findings


def _read_table(root, table):
    path = Path(root) / TABLE_FILES[table]
    findings = csv_structure_findings(path, SCHEMAS[table], table)
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or ()), list(reader), findings
    except (OSError, csv.Error, UnicodeError):
        return [], [], findings


class _EmbeddedParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.parts = []
        self.blocks = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        identifier = attributes.get("id", "")
        if tag.lower() == "script" and identifier.endswith("-data"):
            self.current = identifier
            self.parts = []

    def handle_data(self, data):
        if self.current:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self.current:
            self.blocks[self.current] = "".join(self.parts)
            self.current = None
            self.parts = []


def extract_embedded_json(html_text, route="dashboard"):
    parser = _EmbeddedParser()
    findings = []
    try:
        parser.feed(html_text)
    except Exception:
        return {}, [_finding("embedded parity", route, "html parse")]
    result = {}
    for table in TABLE_FILES:
        identifier = f"{table}-data"
        payload = parser.blocks.get(identifier)
        if payload is None:
            findings.append(_finding("embedded parity", route, identifier))
            continue
        try:
            value = json.loads(payload)
        except (TypeError, json.JSONDecodeError):
            findings.append(_finding("embedded parity", route, identifier))
            continue
        if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
            findings.append(_finding("embedded parity", route, identifier))
            continue
        result[table] = value
    return result, findings


def embedded_json_findings(html_text, route):
    return extract_embedded_json(html_text, route)[1]


def load_repository(root):
    root = Path(root)
    headers, tables, findings = {}, {}, []
    for table in TABLE_FILES:
        headers[table], tables[table], table_findings = _read_table(root, table)
        findings.extend(table_findings)
    embedded, dashboard_html = {}, {}
    for route in ("index.html", "dashboard.html"):
        try:
            text = (root / route).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            text = ""
            findings.append(_finding("embedded parity", route, "read"))
        dashboard_html[route] = text
        embedded[route], route_findings = extract_embedded_json(text, route)
        findings.extend(route_findings)
    try:
        slides_html = (root / "slides.html").read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        slides_html = ""
        findings.append(_finding("slide contract", "slides.html", "read"))
    return Snapshot(headers, tables, embedded, dashboard_html, slides_html, findings)


def _key(table, row, number):
    field_name = {
        "requisitions": "Requisition_ID",
        "candidates": "Candidate_ID",
        "interviews": "Interview_ID",
    }[table]
    return row.get(field_name) or f"{table}:{number}"


def _schema_findings(snapshot):
    findings = []
    for table, expected in SCHEMAS.items():
        header = snapshot.headers.get(table, [])
        if tuple(header) != expected or len(header) != len(set(header)):
            findings.append(_finding("schema", table, "header"))
        expected_set = set(expected)
        for number, row in enumerate(snapshot.tables.get(table, []), 1):
            if set(row) != expected_set or None in row or any(value is None for value in row.values()):
                findings.append(_finding("schema", _key(table, row, number), "row shape"))
    return findings


def _required_and_nullability_findings(snapshot):
    findings = []
    for table, rows in snapshot.tables.items():
        nullable = NULLABLE_CANDIDATE_FIELDS if table == "candidates" else set()
        for number, row in enumerate(rows, 1):
            key = _key(table, row, number)
            for column in SCHEMAS[table]:
                if column not in nullable and row.get(column, "") == "":
                    findings.append(_finding("required field", key, column))
    downstream = (
        "Work_Sample_Score", "Structured_Interview_Score", "Job_Knowledge_Score",
        "Composite_Score", "Subjective_Impression_Score", "Bias_Variance_Gap",
    )
    for number, row in enumerate(snapshot.tables.get("candidates", []), 1):
        key = _key("candidates", row, number)
        stage = row.get("Current_Stage")
        if stage == "Application Review":
            expected_empty = ("Phone_Screen_Score",) + downstream + ("Hired_Date",)
        elif stage == "Shortlisted":
            expected_empty = downstream + ("Hired_Date",)
        elif stage == "Interview Complete":
            expected_empty = ("Hired_Date",)
        else:
            expected_empty = ()
        for column in expected_empty:
            if row.get(column, "") != "":
                findings.append(_finding("nullability", key, column))
        required_progression = ()
        if stage == "Shortlisted":
            required_progression = ("Phone_Screen_Score",)
        elif stage in {"Interview Complete", "Hired"}:
            required_progression = ("Phone_Screen_Score",) + downstream
        for column in required_progression:
            if row.get(column, "") == "":
                findings.append(_finding("nullability", key, column))
    return findings


def _valid_date(value):
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return parsed.isoformat() == value


def _decimal(value):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return None


def _field_rule_findings(snapshot):
    findings = []
    integer_fields = {
        "requisitions": {"Target_Headcount", "Total_Applicants", "Shortlisted", "Interviewed", "Offered", "Hired"},
    }
    decimal_patterns = {
        "requisitions": {"Days_to_Fill": re.compile(r"^\d+\.\d$")},
        "candidates": {
            field_name: re.compile(r"^-?\d+\.\d{2}$")
            for field_name in (
                "Resume_Screen_Score", "Phone_Screen_Score", "Work_Sample_Score",
                "Structured_Interview_Score", "Job_Knowledge_Score",
                "Composite_Score", "Subjective_Impression_Score", "Bias_Variance_Gap",
            )
        },
        "interviews": {
            "Turnaround_Hours": re.compile(r"^\d+\.\d$"),
            "BARS_Score_1": re.compile(r"^\d+\.\d$"),
            "BARS_Score_2": re.compile(r"^\d+\.\d$"),
            "BARS_Score_3": re.compile(r"^\d+\.\d$"),
            "BARS_Score_4": re.compile(r"^\d+\.\d$"),
            "Mean_BARS_Score": re.compile(r"^\d+\.\d{2}$"),
        },
    }
    date_fields = {
        "requisitions": ("Open_Date", "Close_Date"),
        "candidates": ("Applied_Date", "Hired_Date"),
        "interviews": ("Scheduled_Date", "Feedback_Submitted_Date"),
    }
    for table, rows in snapshot.tables.items():
        for number, row in enumerate(rows, 1):
            key = _key(table, row, number)
            for column in integer_fields.get(table, set()):
                value = row.get(column, "")
                try:
                    valid = str(int(value)) == value and int(value) >= 0
                except (TypeError, ValueError):
                    valid = False
                if not valid:
                    findings.append(_finding("type", key, column))
            for column, pattern in decimal_patterns.get(table, {}).items():
                value = row.get(column, "")
                if value == "":
                    continue
                if _decimal(value) is None:
                    findings.append(_finding("type", key, column))
                elif not pattern.fullmatch(value):
                    findings.append(_finding("precision", key, column))
            for column in date_fields.get(table, ()):
                value = row.get(column, "")
                if value and not _valid_date(value):
                    findings.append(_finding("format", key, column))
            for column, pattern in ID_PATTERNS.items():
                if column in row and row.get(column) and not pattern.fullmatch(row[column]):
                    findings.append(_finding("format", key, column))
    for number, row in enumerate(snapshot.tables.get("candidates", []), 1):
        key = _key("candidates", row, number)
        for column in (
            "Resume_Screen_Score", "Phone_Screen_Score", "Work_Sample_Score",
            "Structured_Interview_Score", "Job_Knowledge_Score", "Composite_Score",
            "Subjective_Impression_Score",
        ):
            value = _decimal(row.get(column, ""))
            if value is not None and not Decimal("1.00") <= value <= Decimal("5.00"):
                findings.append(_finding("range", key, column))
        expected_name = f"Synthetic Candidate {number:04d}"
        if row.get("Full_Name") != expected_name:
            findings.append(_finding("format", key, "Full_Name"))
    for number, row in enumerate(snapshot.tables.get("interviews", []), 1):
        key = _key("interviews", row, number)
        for column in ("BARS_Score_1", "BARS_Score_2", "BARS_Score_3", "BARS_Score_4", "Mean_BARS_Score"):
            value = _decimal(row.get(column, ""))
            if value is not None and not Decimal("1.00") <= value <= Decimal("5.00"):
                findings.append(_finding("range", key, column))
        turnaround = _decimal(row.get("Turnaround_Hours", ""))
        if turnaround is not None and turnaround < 0:
            findings.append(_finding("range", key, "Turnaround_Hours"))
    return findings


def _enumeration_findings(snapshot):
    findings = []
    for table, field_values in ENUMS.items():
        for number, row in enumerate(snapshot.tables.get(table, []), 1):
            key = _key(table, row, number)
            for column, allowed in field_values.items():
                if row.get(column) not in allowed:
                    findings.append(_finding("enumeration", key, column))
    return findings


def _identifier_and_fk_findings(snapshot):
    findings = []
    for table, id_field in (("requisitions", "Requisition_ID"), ("candidates", "Candidate_ID"), ("interviews", "Interview_ID")):
        values = [row.get(id_field, "") for row in snapshot.tables.get(table, [])]
        if len(values) != len(set(values)):
            findings.append(_finding("identifier", table, id_field))
    candidate_ids = [row.get("Candidate_ID", "") for row in snapshot.tables.get("candidates", [])]
    interview_ids = [row.get("Interview_ID", "") for row in snapshot.tables.get("interviews", [])]
    if candidate_ids != [f"CAND-2026-{number:04d}" for number in range(1, len(candidate_ids) + 1)]:
        findings.append(_finding("identifier", "candidates", "Candidate_ID sequence"))
    if interview_ids != [f"INT-2026-{number:04d}" for number in range(1, len(interview_ids) + 1)]:
        findings.append(_finding("identifier", "interviews", "Interview_ID sequence"))
    requisition_ids = {row.get("Requisition_ID") for row in snapshot.tables.get("requisitions", [])}
    candidate_by_id = {row.get("Candidate_ID"): row for row in snapshot.tables.get("candidates", [])}
    for number, row in enumerate(snapshot.tables.get("candidates", []), 1):
        if row.get("Requisition_ID") not in requisition_ids:
            findings.append(_finding("foreign key", _key("candidates", row, number), "Requisition_ID"))
    for number, row in enumerate(snapshot.tables.get("interviews", []), 1):
        key = _key("interviews", row, number)
        candidate = candidate_by_id.get(row.get("Candidate_ID"))
        if candidate is None:
            findings.append(_finding("foreign key", key, "Candidate_ID"))
        if row.get("Requisition_ID") not in requisition_ids:
            findings.append(_finding("foreign key", key, "Requisition_ID"))
        elif candidate is not None and candidate.get("Requisition_ID") != row.get("Requisition_ID"):
            findings.append(_finding("foreign key", key, "Candidate_ID+Requisition_ID"))
    return findings


def weighted_composite(work_sample, structured_interview, job_knowledge):
    result = (
        Decimal(work_sample) * Decimal("0.40")
        + Decimal(structured_interview) * Decimal("0.40")
        + Decimal(job_knowledge) * Decimal("0.20")
    )
    return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def rank_scored_candidates(rows):
    return sorted(rows, key=lambda row: (-Decimal(row["Composite_Score"]), row["Candidate_ID"]))


def _stage_findings(snapshot):
    findings = []
    interviews_by_candidate = defaultdict(list)
    for row in snapshot.tables.get("interviews", []):
        interviews_by_candidate[row.get("Candidate_ID")].append(row)
    expected_stages = ENUMS["interviews"]["Stage_Name"]
    for number, row in enumerate(snapshot.tables.get("candidates", []), 1):
        key = _key("candidates", row, number)
        stage = row.get("Current_Stage")
        has_phone = bool(row.get("Phone_Screen_Score"))
        has_composite = bool(row.get("Composite_Score"))
        if (stage == "Application Review" and has_phone) or (stage == "Shortlisted" and (not has_phone or has_composite)):
            findings.append(_finding("stage progression", key, "Current_Stage"))
        if stage in {"Interview Complete", "Hired"} and not (has_phone and has_composite):
            findings.append(_finding("stage progression", key, "Current_Stage"))
        expected_offer = "Yes" if stage == "Hired" else "No"
        if row.get("Offer_Extended") != expected_offer or row.get("Offer_Accepted") != expected_offer:
            findings.append(_finding("stage progression", key, "offer state"))
        if (stage == "Hired") != bool(row.get("Hired_Date")):
            findings.append(_finding("stage progression", key, "Hired_Date"))
        expected_dispositions = {
            "Application Review": {"Automated job-related knockout criteria not met"},
            "Shortlisted": {"Not advanced to standardized assessment"},
            "Interview Complete": {
                "Composite below requisition threshold",
                "Halo Effect control - evidence did not support override",
            },
            "Hired": {"Selected - highest governed composite"},
        }
        if stage in expected_dispositions and row.get("Disposition_Reason") not in expected_dispositions[stage]:
            findings.append(_finding("stage progression", key, "Disposition_Reason"))
        events = interviews_by_candidate.get(row.get("Candidate_ID"), [])
        if has_composite:
            if len(events) != 4 or {event.get("Stage_Name") for event in events} != expected_stages:
                findings.append(_finding("stage progression", key, "interview events"))
        elif events:
            findings.append(_finding("stage progression", key, "interview events"))
    return findings


def _temporal_findings(snapshot):
    findings = []
    requisitions = {
        row.get("Requisition_ID"): row
        for row in snapshot.tables.get("requisitions", [])
    }
    for row in requisitions.values():
        opened, closed = row.get("Open_Date", ""), row.get("Close_Date", "")
        if _valid_date(opened) and _valid_date(closed) and opened > closed:
            findings.append(_finding("temporal consistency", row.get("Requisition_ID"), "Open_Date+Close_Date"))
    for number, row in enumerate(snapshot.tables.get("candidates", []), 1):
        requisition = requisitions.get(row.get("Requisition_ID"))
        applied = row.get("Applied_Date", "")
        if requisition and _valid_date(applied):
            if not requisition.get("Open_Date", "") <= applied <= requisition.get("Close_Date", ""):
                findings.append(_finding("temporal consistency", _key("candidates", row, number), "Applied_Date"))
        hired = row.get("Hired_Date", "")
        if requisition and hired and _valid_date(hired) and hired > requisition.get("Close_Date", ""):
            findings.append(_finding("temporal consistency", _key("candidates", row, number), "Hired_Date"))
    for number, row in enumerate(snapshot.tables.get("interviews", []), 1):
        scheduled = row.get("Scheduled_Date", "")
        submitted = row.get("Feedback_Submitted_Date", "")
        if _valid_date(scheduled) and _valid_date(submitted) and submitted < scheduled:
            findings.append(_finding("temporal consistency", _key("interviews", row, number), "Feedback_Submitted_Date"))
    return findings


def _requisition_findings(snapshot):
    findings = []
    candidates = snapshot.tables.get("candidates", [])
    for number, requisition in enumerate(snapshot.tables.get("requisitions", []), 1):
        key = _key("requisitions", requisition, number)
        rows = [row for row in candidates if row.get("Requisition_ID") == key]
        actual = (
            len(rows),
            sum(bool(row.get("Phone_Screen_Score")) for row in rows),
            sum(bool(row.get("Composite_Score")) for row in rows),
            sum(row.get("Offer_Extended") == "Yes" for row in rows),
            sum(row.get("Current_Stage") == "Hired" for row in rows),
        )
        declared = tuple(
            int(requisition.get(field_name, -1)) if str(requisition.get(field_name, "")).isdigit() else -1
            for field_name in ("Total_Applicants", "Shortlisted", "Interviewed", "Offered", "Hired")
        )
        if declared != actual or actual != EXPECTED_REQUISITIONS.get(key):
            findings.append(_finding("requisition totals", key, "pipeline totals"))
        if str(requisition.get("Target_Headcount")) != str(requisition.get("Hired")):
            findings.append(_finding("requisition totals", key, "Target_Headcount"))
    return findings


def _composite_findings(snapshot):
    findings = []
    interviews_by_candidate = defaultdict(list)
    for row in snapshot.tables.get("interviews", []):
        interviews_by_candidate[row.get("Candidate_ID")].append(row)
        key = row.get("Interview_ID") or "interview"
        values = [_decimal(row.get(f"BARS_Score_{index}", "")) for index in range(1, 5)]
        mean = _decimal(row.get("Mean_BARS_Score", ""))
        if any(value is None for value in values) or mean is None:
            findings.append(_finding("interview score", key, "Mean_BARS_Score"))
        else:
            expected_mean = (sum(values) / Decimal("4")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if mean != expected_mean:
                findings.append(_finding("interview score", key, "Mean_BARS_Score"))
    for number, row in enumerate(snapshot.tables.get("candidates", []), 1):
        key = _key("candidates", row, number)
        columns = ("Work_Sample_Score", "Structured_Interview_Score", "Job_Knowledge_Score", "Composite_Score", "Subjective_Impression_Score", "Bias_Variance_Gap")
        values = [row.get(column, "") for column in columns]
        if any(values) and not all(values):
            findings.append(_finding("composite", key, "assessment fields"))
            continue
        if not all(values):
            continue
        parsed = [_decimal(value) for value in values]
        if any(value is None for value in parsed):
            findings.append(_finding("composite", key, "assessment fields"))
            continue
        expected = weighted_composite(values[0], values[1], values[2])
        if parsed[3] != expected:
            findings.append(_finding("composite", key, "Composite_Score"))
        expected_gap = (parsed[4] - parsed[3]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if parsed[5] != expected_gap:
            findings.append(_finding("bias gap", key, "Bias_Variance_Gap"))
        event_means = {_decimal(event.get("Mean_BARS_Score", "")) for event in interviews_by_candidate.get(row.get("Candidate_ID"), [])}
        if event_means and event_means != {parsed[1]}:
            findings.append(_finding("composite", key, "Structured_Interview_Score"))
    for requisition_id, expected in EXPECTED_REQUISITIONS.items():
        rows = [row for row in snapshot.tables.get("candidates", []) if row.get("Requisition_ID") == requisition_id and row.get("Composite_Score")]
        if not rows:
            continue
        valid_rows = [row for row in rows if _decimal(row.get("Composite_Score")) is not None]
        if len(valid_rows) != len(rows):
            findings.append(_finding("composite", requisition_id, "ranked selection"))
            continue
        selected = {row.get("Candidate_ID") for row in rank_scored_candidates(valid_rows)[:expected[4]]}
        hired = {row.get("Candidate_ID") for row in rows if row.get("Current_Stage") == "Hired"}
        if selected != hired:
            findings.append(_finding("composite", requisition_id, "ranked selection"))
    return findings


def _kpi_findings(snapshot):
    findings = []
    requisitions = snapshot.tables.get("requisitions", [])
    candidates = snapshot.tables.get("candidates", [])
    interviews = snapshot.tables.get("interviews", [])
    cohort = Counter(row.get("Demographic_Cohort") for row in candidates)
    progressed = Counter(row.get("Demographic_Cohort") for row in candidates if row.get("Phone_Screen_Score"))
    assessed = Counter(row.get("Demographic_Cohort") for row in candidates if row.get("Composite_Score"))
    if cohort != Counter({"Reference Group": 2400, "Focal Group": 1600}) or progressed != Counter({"Reference Group": 624, "Focal Group": 362}) or assessed != Counter({"Reference Group": 300, "Focal Group": 200}):
        findings.append(_finding("cohort progression", "candidates", "cohort totals"))
    for requisition_id, expected_groups in EXPECTED_COHORTS_BY_REQUISITION.items():
        rows = [row for row in candidates if row.get("Requisition_ID") == requisition_id]
        actual_groups = []
        for predicate in (
            lambda row: True,
            lambda row: bool(row.get("Phone_Screen_Score")),
            lambda row: bool(row.get("Composite_Score")),
            lambda row: row.get("Current_Stage") == "Hired",
        ):
            selected = [row for row in rows if predicate(row)]
            counts = Counter(row.get("Demographic_Cohort") for row in selected)
            actual_groups.append((counts["Reference Group"], counts["Focal Group"]))
        if tuple(actual_groups) != expected_groups:
            findings.append(_finding("cohort progression", requisition_id, "stage cohorts"))
    for row in interviews:
        turnaround = _decimal(row.get("Turnaround_Hours", ""))
        if turnaround is not None:
            expected = "Yes" if turnaround <= Decimal("48.0") else "No"
            if row.get("SLA_Met") != expected:
                findings.append(_finding("sla", row.get("Interview_ID"), "SLA_Met"))
    if Counter(row.get("SLA_Met") for row in interviews) != Counter({"Yes": 1836, "No": 164}):
        findings.append(_finding("sla", "interviews", "SLA totals"))
    try:
        mean_days = sum(Decimal(row["Days_to_Fill"]) for row in requisitions) / len(requisitions)
        reference_rate = Decimal(progressed["Reference Group"]) / Decimal(cohort["Reference Group"])
        focal_rate = Decimal(progressed["Focal Group"]) / Decimal(cohort["Focal Group"])
        air = (focal_rate / reference_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (ArithmeticError, InvalidOperation, KeyError, ZeroDivisionError):
        mean_days, air = None, None
    actual = {
        "requisitions": len(requisitions),
        "candidates": len(candidates),
        "interviews": len(interviews),
        "shortlisted": sum(bool(row.get("Phone_Screen_Score")) for row in candidates),
        "assessed": sum(bool(row.get("Composite_Score")) for row in candidates),
        "hires": sum(row.get("Current_Stage") == "Hired" for row in candidates),
        "offered": sum(row.get("Offer_Extended") == "Yes" for row in candidates),
        "mean_days": mean_days,
        "air": air,
    }
    expected = {
        "requisitions": 5, "candidates": 4000, "interviews": 2000,
        "shortlisted": 986, "assessed": 500, "hires": 120, "offered": 120,
        "mean_days": Decimal("28.5"), "air": Decimal("0.87"),
    }
    if actual != expected:
        findings.append(_finding("governed kpi", "repository", "governed constants"))
    for route, html_text in snapshot.dashboard_html.items():
        if any(marker not in html_text for marker in GOVERNED_DISPLAY_MARKERS):
            findings.append(_finding("governed kpi", route, "displayed constants"))
    return findings


def _embedded_findings(snapshot):
    findings = []
    for route in ("index.html", "dashboard.html"):
        route_data = snapshot.embedded.get(route, {})
        for table, rows in snapshot.tables.items():
            embedded_rows = route_data.get(table)
            if embedded_rows is None or len(embedded_rows) != len(rows):
                findings.append(_finding("embedded parity", route, table))
                continue
            expected_fields = set(SCHEMAS[table])
            mismatch = False
            for csv_row, embedded_row in zip(rows, embedded_rows):
                normalized = {key: "" if value is None else str(value) for key, value in embedded_row.items()}
                if set(normalized) != expected_fields or normalized != csv_row:
                    mismatch = True
                    break
            if mismatch:
                findings.append(_finding("embedded parity", route, table))
    return findings


def _halo_findings(snapshot):
    rows = [row for row in snapshot.tables.get("candidates", []) if row.get("Candidate_ID") == "CAND-2026-0013"]
    if len(rows) != 1:
        return [_finding("halo control", "CAND-2026-0013", "record")]
    return [
        _finding("halo control", "CAND-2026-0013", field_name)
        for field_name, expected in HALO_CONTROL.items()
        if rows[0].get(field_name) != expected
    ]


class _StructureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slide_ids = []
        self.slide_labels = []
        self.ids = []
        self.current_select = None
        self.options = defaultdict(list)
        self.in_script = False
        self.script_parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        identifier = attributes.get("id")
        if identifier:
            self.ids.append(identifier)
        classes = set(attributes.get("class", "").split())
        if tag.lower() == "section" and "slide" in classes:
            self.slide_ids.append(identifier)
            self.slide_labels.append(attributes.get("aria-label"))
        if tag.lower() == "select":
            self.current_select = identifier
        if tag.lower() == "option" and self.current_select:
            self.options[self.current_select].append(attributes.get("value"))
        if tag.lower() == "script" and not attributes.get("src"):
            self.in_script = True

    def handle_data(self, data):
        if self.in_script:
            self.script_parts.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "select":
            self.current_select = None
        if tag.lower() == "script":
            self.in_script = False

    @property
    def script(self):
        return "\n".join(self.script_parts)


def slide_contract_findings(html_text):
    parser = _StructureParser()
    try:
        parser.feed(html_text)
    except Exception:
        return [_finding("slide contract", "slides.html", "html parse")]
    findings = []
    if parser.slide_ids != [f"slide-{number}" for number in range(1, 6)]:
        findings.append(_finding("slide contract", "slides.html", "slide IDs/order"))
    if parser.slide_labels != [f"Slide {number} of 5" for number in range(1, 6)]:
        findings.append(_finding("slide contract", "slides.html", "slide labels"))
    required_ids = {"previous-slide", "next-slide", "slide-counter", "progress-bar"}
    if not required_ids.issubset(parser.ids):
        findings.append(_finding("slide contract", "slides.html", "controls"))
    markers = (
        "Math.max(0, Math.min(slides.length - 1, index))",
        'previous.addEventListener("click", function () { show(current - 1); })',
        'next.addEventListener("click", function () { show(current + 1); })',
        "show(0)",
    )
    if any(marker not in parser.script for marker in markers):
        findings.append(_finding("slide contract", "slides.html", "navigation source"))
    return findings


def dashboard_pagination_findings(html_text, route):
    parser = _StructureParser()
    try:
        parser.feed(html_text)
    except Exception:
        return [_finding("pagination contract", route, "html parse")]
    findings = []
    if not {"previous-page", "next-page", "page-indicator", "page-size"}.issubset(parser.ids):
        findings.append(_finding("pagination contract", route, "controls"))
    if parser.options.get("page-size") != ["25", "50"]:
        findings.append(_finding("pagination contract", route, "page sizes"))
    markers = (
        "let currentPage=1",
        "Math.max(1,Math.ceil(filteredRows.length/pageSize))",
        "currentPage=Math.min(currentPage,totalPages)",
        "filteredRows.slice(start,start+pageSize)",
        "previousPage.disabled=currentPage===1",
        "nextPage.disabled=currentPage===totalPages",
        'previousPage.addEventListener("click"',
        'nextPage.addEventListener("click"',
    )
    if any(marker not in parser.script for marker in markers):
        findings.append(_finding("pagination contract", route, "navigation source"))
    return findings


def paginate(total_rows, page_size, current_page):
    if total_rows < 0 or page_size <= 0:
        raise ValueError("pagination inputs must be non-negative with a positive page size")
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    current = min(max(1, current_page), total_pages)
    start = (current - 1) * page_size if total_rows else 0
    stop = min(start + page_size, total_rows)
    return PageState(current, total_pages, start, stop, current == 1, current == total_pages)


def _deduplicate(findings):
    return list(dict.fromkeys(findings))


VALIDATORS_BY_CATEGORY = {
    "schema": (_schema_findings,),
    "required field": (_required_and_nullability_findings,),
    "nullability": (_required_and_nullability_findings,),
    "type": (_field_rule_findings,),
    "format": (_field_rule_findings,),
    "range": (_field_rule_findings,),
    "precision": (_field_rule_findings,),
    "enumeration": (_enumeration_findings,),
    "identifier": (_identifier_and_fk_findings,),
    "foreign key": (_identifier_and_fk_findings,),
    "stage progression": (_stage_findings,),
    "temporal consistency": (_temporal_findings,),
    "requisition totals": (_requisition_findings,),
    "composite": (_composite_findings,),
    "bias gap": (_composite_findings,),
    "interview score": (_composite_findings,),
    "cohort progression": (_kpi_findings,),
    "sla": (_kpi_findings,),
    "governed kpi": (_kpi_findings,),
    "embedded parity": (_embedded_findings,),
    "halo control": (_halo_findings,),
}


def validate_categories(snapshot, categories):
    findings = list(snapshot.load_findings)
    validators = []
    for category in categories:
        if category == "slide contract":
            findings.extend(slide_contract_findings(snapshot.slides_html))
            continue
        if category == "pagination contract":
            for route, html_text in snapshot.dashboard_html.items():
                findings.extend(dashboard_pagination_findings(html_text, route))
            continue
        validators.extend(VALIDATORS_BY_CATEGORY.get(category, ()))
    validators = list(dict.fromkeys(validators))
    for validator in validators:
        try:
            findings.extend(validator(snapshot))
        except (ArithmeticError, KeyError, TypeError, ValueError):
            findings.append(_finding("data contract", validator.__name__, "validation"))
    return _deduplicate(findings)


def validate_snapshot(snapshot):
    categories = tuple(VALIDATORS_BY_CATEGORY) + ("slide contract", "pagination contract")
    return validate_categories(snapshot, categories)


def validate_repository(root):
    return validate_snapshot(load_repository(root))
