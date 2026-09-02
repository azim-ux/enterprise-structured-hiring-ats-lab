import copy
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from scripts import data_contracts as contracts


ROOT = Path(__file__).resolve().parents[1]


class DataContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid = contracts.load_repository(ROOT)

    def snapshot(self):
        return copy.deepcopy(self.valid)

    def assert_rejected(self, snapshot, category):
        findings = contracts.validate_snapshot(snapshot)
        self.assertIn(category, {finding.category for finding in findings})
        rendered = contracts.format_findings(findings)
        self.assertNotIn("Synthetic Candidate", rendered)
        self.assertNotIn(str(snapshot.tables["candidates"][0]), rendered)

    def test_current_repository_satisfies_every_data_contract(self):
        self.assertEqual([], contracts.validate_repository(ROOT))

    def test_current_exact_schemas_and_field_rules_pass(self):
        findings = contracts.validate_snapshot(self.valid)
        blocked = {"schema", "required field", "nullability", "type", "format"}
        self.assertTrue(blocked.isdisjoint(finding.category for finding in findings))

    def test_missing_unexpected_and_duplicate_columns_are_rejected(self):
        cases = []
        missing = self.snapshot()
        missing.headers["requisitions"].remove("Hired")
        cases.append(missing)
        unexpected = self.snapshot()
        unexpected.headers["candidates"].append("Unexpected_Field")
        cases.append(unexpected)
        duplicate = self.snapshot()
        duplicate.headers["interviews"][1] = "Interview_ID"
        cases.append(duplicate)
        for snapshot in cases:
            with self.subTest(headers=snapshot.headers):
                self.assert_rejected(snapshot, "schema")

    def test_malformed_csv_rows_are_rejected_without_dumping_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "malformed.csv"
            path.write_text("A,B\nrecord-key,one,extra\n", encoding="utf-8")
            findings = contracts.csv_structure_findings(path, ("A", "B"), "test")
        self.assertEqual("schema", findings[0].category)
        self.assertNotIn("one", contracts.format_findings(findings))

    def test_required_and_nullable_field_mutations_are_rejected(self):
        required = self.snapshot()
        required.tables["candidates"][0]["Candidate_ID"] = ""
        self.assert_rejected(required, "required field")
        downstream = self.snapshot()
        row = next(r for r in downstream.tables["candidates"] if r["Current_Stage"] == "Application Review")
        row["Composite_Score"] = "3.50"
        self.assert_rejected(downstream, "nullability")

    def test_type_format_range_and_precision_mutations_are_rejected(self):
        cases = []
        invalid_integer = self.snapshot()
        invalid_integer.tables["requisitions"][0]["Total_Applicants"] = "many"
        cases.append((invalid_integer, "type"))
        invalid_date = self.snapshot()
        invalid_date.tables["candidates"][0]["Applied_Date"] = "2026-99-40"
        cases.append((invalid_date, "format"))
        out_of_range = self.snapshot()
        out_of_range.tables["candidates"][0]["Resume_Screen_Score"] = "5.01"
        cases.append((out_of_range, "range"))
        excessive_precision = self.snapshot()
        excessive_precision.tables["interviews"][0]["Mean_BARS_Score"] = "4.650"
        cases.append((excessive_precision, "precision"))
        for snapshot, category in cases:
            with self.subTest(category=category):
                self.assert_rejected(snapshot, category)

    def test_unique_and_sequential_identifier_mutations_are_rejected(self):
        duplicate = self.snapshot()
        duplicate.tables["candidates"][1]["Candidate_ID"] = duplicate.tables["candidates"][0]["Candidate_ID"]
        self.assert_rejected(duplicate, "identifier")
        gap = self.snapshot()
        gap.tables["interviews"][10]["Interview_ID"] = "INT-2026-9999"
        self.assert_rejected(gap, "identifier")
        duplicate_req = self.snapshot()
        duplicate_req.tables["requisitions"][1]["Requisition_ID"] = duplicate_req.tables["requisitions"][0]["Requisition_ID"]
        self.assert_rejected(duplicate_req, "identifier")

    def test_foreign_key_and_candidate_requisition_pair_mutations_are_rejected(self):
        orphan_candidate = self.snapshot()
        orphan_candidate.tables["interviews"][0]["Candidate_ID"] = "CAND-2026-9999"
        self.assert_rejected(orphan_candidate, "foreign key")
        orphan_requisition = self.snapshot()
        orphan_requisition.tables["candidates"][0]["Requisition_ID"] = "REQ-2026-NOT-REAL"
        self.assert_rejected(orphan_requisition, "foreign key")
        pair_mismatch = self.snapshot()
        pair_mismatch.tables["interviews"][0]["Requisition_ID"] = "REQ-2026-ENG-G1"
        self.assert_rejected(pair_mismatch, "foreign key")

    def test_allowed_enumeration_mutation_is_rejected(self):
        snapshot = self.snapshot()
        snapshot.tables["candidates"][0]["Gender"] = "Undocumented value"
        self.assert_rejected(snapshot, "enumeration")

    def test_impossible_stage_and_offer_transitions_are_rejected(self):
        early_score = self.snapshot()
        row = next(r for r in early_score.tables["candidates"] if r["Current_Stage"] == "Application Review")
        row["Phone_Screen_Score"] = "4.00"
        self.assert_rejected(early_score, "stage progression")
        accepted_without_offer = self.snapshot()
        row = next(r for r in accepted_without_offer.tables["candidates"] if r["Offer_Extended"] == "No")
        row["Offer_Accepted"] = "Yes"
        self.assert_rejected(accepted_without_offer, "stage progression")
        hired_without_date = self.snapshot()
        row = next(r for r in hired_without_date.tables["candidates"] if r["Current_Stage"] == "Hired")
        row["Hired_Date"] = ""
        self.assert_rejected(hired_without_date, "stage progression")

    def test_current_per_requisition_stage_totals_pass(self):
        self.assertNotIn("requisition totals", {f.category for f in contracts.validate_snapshot(self.valid)})

    def test_each_per_requisition_total_mutation_is_rejected(self):
        for field in ("Total_Applicants", "Shortlisted", "Interviewed", "Offered", "Hired"):
            snapshot = self.snapshot()
            snapshot.tables["requisitions"][0][field] = str(int(snapshot.tables["requisitions"][0][field]) + 1)
            with self.subTest(field=field):
                self.assert_rejected(snapshot, "requisition totals")

    def test_current_all_500_composites_and_bias_gaps_pass(self):
        findings = contracts.validate_snapshot(self.valid)
        self.assertNotIn("composite", {f.category for f in findings})
        self.assertNotIn("bias gap", {f.category for f in findings})

    def test_each_composite_component_and_result_mutation_is_rejected(self):
        for field in (
            "Work_Sample_Score",
            "Structured_Interview_Score",
            "Job_Knowledge_Score",
            "Composite_Score",
        ):
            snapshot = self.snapshot()
            row = next(r for r in snapshot.tables["candidates"] if r["Composite_Score"] and r["Candidate_ID"] != "CAND-2026-0013")
            row[field] = str(Decimal(row[field]) + Decimal("0.01"))
            with self.subTest(field=field):
                self.assert_rejected(snapshot, "composite")

    def test_missing_partial_and_corrupt_composite_inputs_are_rejected(self):
        for field, value in (
            ("Work_Sample_Score", ""),
            ("Structured_Interview_Score", ""),
            ("Job_Knowledge_Score", ""),
            ("Composite_Score", "not-a-score"),
        ):
            snapshot = self.snapshot()
            row = next(r for r in snapshot.tables["candidates"] if r["Composite_Score"] and r["Candidate_ID"] != "CAND-2026-0013")
            row[field] = value
            with self.subTest(field=field):
                self.assert_rejected(snapshot, "composite")

    def test_decimal_half_up_rounding_and_tie_order_are_deterministic(self):
        self.assertEqual(Decimal("1.01"), contracts.weighted_composite("1.00", "1.00", "1.025"))
        rows = [
            {"Candidate_ID": "CAND-2026-0002", "Composite_Score": "4.50"},
            {"Candidate_ID": "CAND-2026-0001", "Composite_Score": "4.50"},
        ]
        self.assertEqual(
            ["CAND-2026-0001", "CAND-2026-0002"],
            [row["Candidate_ID"] for row in contracts.rank_scored_candidates(rows)],
        )

    def test_current_cohort_sla_and_governed_kpis_pass(self):
        categories = {f.category for f in contracts.validate_snapshot(self.valid)}
        self.assertTrue({"cohort progression", "sla", "governed kpi"}.isdisjoint(categories))

    def test_cohort_progression_and_governed_kpi_mutations_are_rejected(self):
        cohort = self.snapshot()
        cohort.tables["candidates"][0]["Demographic_Cohort"] = "Focal Group"
        self.assert_rejected(cohort, "cohort progression")
        hire = self.snapshot()
        row = next(r for r in hire.tables["candidates"] if r["Current_Stage"] == "Hired")
        row["Current_Stage"] = "Interview Complete"
        row["Offer_Extended"] = "No"
        row["Offer_Accepted"] = "No"
        row["Hired_Date"] = ""
        self.assert_rejected(hire, "governed kpi")

    def test_sla_boundary_and_mean_mutations_are_rejected(self):
        boundary = self.snapshot()
        row = next(r for r in boundary.tables["interviews"] if r["Turnaround_Hours"] == "48.0")
        row["SLA_Met"] = "No"
        self.assert_rejected(boundary, "sla")
        mean = self.snapshot()
        mean.tables["interviews"][0]["Mean_BARS_Score"] = "4.64"
        self.assert_rejected(mean, "sla")

    def test_current_embedded_json_matches_every_csv_value_in_both_routes(self):
        self.assertNotIn("embedded parity", {f.category for f in contracts.validate_snapshot(self.valid)})

    def test_embedded_json_missing_additional_modified_and_field_drift_are_rejected(self):
        mutations = []
        missing = self.snapshot()
        missing.embedded["index.html"]["candidates"].pop()
        mutations.append(missing)
        additional = self.snapshot()
        additional.embedded["dashboard.html"]["requisitions"].append(copy.deepcopy(additional.embedded["dashboard.html"]["requisitions"][0]))
        mutations.append(additional)
        modified = self.snapshot()
        modified.embedded["index.html"]["interviews"][0]["SLA_Met"] = "Yes"
        mutations.append(modified)
        field_drift = self.snapshot()
        field_drift.embedded["dashboard.html"]["candidates"][0]["Unexpected_Field"] = "synthetic"
        mutations.append(field_drift)
        for snapshot in mutations:
            with self.subTest():
                self.assert_rejected(snapshot, "embedded parity")

    def test_structured_embedded_json_extraction_rejects_missing_or_invalid_blocks(self):
        missing = '<script id="candidates-data" type="application/json">[]</script>'
        self.assertTrue(contracts.embedded_json_findings(missing, "route.html"))
        invalid = '<script id="requisitions-data" type="application/json">{invalid}</script>'
        self.assertTrue(contracts.embedded_json_findings(invalid, "route.html"))

    def test_current_halo_control_values_pass(self):
        self.assertNotIn("halo control", {f.category for f in contracts.validate_snapshot(self.valid)})

    def test_each_halo_control_value_mutation_is_rejected(self):
        protected = (
            "Work_Sample_Score",
            "Structured_Interview_Score",
            "Job_Knowledge_Score",
            "Composite_Score",
            "Subjective_Impression_Score",
            "Bias_Variance_Gap",
            "Current_Stage",
            "Disposition_Reason",
        )
        for field in protected:
            snapshot = self.snapshot()
            row = next(r for r in snapshot.tables["candidates"] if r["Candidate_ID"] == "CAND-2026-0013")
            row[field] = "changed"
            with self.subTest(field=field):
                self.assert_rejected(snapshot, "halo control")

    def test_current_five_slide_and_control_contract_passes(self):
        categories = {f.category for f in contracts.validate_snapshot(self.valid)}
        self.assertTrue({"slide contract", "pagination contract"}.isdisjoint(categories))

    def test_slide_id_order_and_control_relationship_mutations_are_rejected(self):
        wrong_id = self.snapshot()
        wrong_id.slides_html = wrong_id.slides_html.replace('id="slide-3"', 'id="slide-x"', 1)
        self.assert_rejected(wrong_id, "slide contract")
        missing_control = self.snapshot()
        missing_control.slides_html = missing_control.slides_html.replace('id="next-slide"', 'id="next-missing"', 1)
        self.assert_rejected(missing_control, "slide contract")

    def test_pagination_model_bounds_and_next_previous_are_deterministic(self):
        first = contracts.paginate(total_rows=51, page_size=25, current_page=0)
        self.assertEqual((1, 3, 0, 25, True, False), first.as_tuple())
        middle = contracts.paginate(total_rows=51, page_size=25, current_page=2)
        self.assertEqual((2, 3, 25, 50, False, False), middle.as_tuple())
        last = contracts.paginate(total_rows=51, page_size=25, current_page=99)
        self.assertEqual((3, 3, 50, 51, False, True), last.as_tuple())
        empty = contracts.paginate(total_rows=0, page_size=50, current_page=1)
        self.assertEqual((1, 1, 0, 0, True, True), empty.as_tuple())

    def test_dashboard_pagination_source_mutations_are_rejected(self):
        for route in ("index.html", "dashboard.html"):
            snapshot = self.snapshot()
            snapshot.dashboard_html[route] = snapshot.dashboard_html[route].replace(
                "Math.max(1,Math.ceil(filteredRows.length/pageSize))",
                "Math.ceil(filteredRows.length/pageSize)",
                1,
            )
            with self.subTest(route=route):
                self.assert_rejected(snapshot, "pagination contract")


if __name__ == "__main__":
    unittest.main(verbosity=2)
