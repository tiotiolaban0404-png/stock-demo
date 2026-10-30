import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from lead_processor import classify_timeline, process_leads, run_pipeline


class TimelineClassificationTests(unittest.TestCase):
    def test_classifies_clear_near_term_later_and_unknown_timelines(self):
        self.assertEqual(classify_timeline(3), "HOT")
        self.assertEqual(classify_timeline("within 3 months"), "HOT")
        self.assertEqual(classify_timeline("4-6 months"), "NURTURE")
        self.assertEqual(classify_timeline("not sure"), "REVIEW")
        self.assertEqual(classify_timeline(""), "REVIEW")

    def test_processes_and_routes_leads_with_consent_and_deduplication(self):
        import pandas as pd

        source = pd.DataFrame(
            [
                {"lead_id": "L1", "name": "Ari", "phone": "+62 812-3456-7890", "email": "ari@example.com", "preferred_contact": "phone", "purchase_timeline": "2 months", "contact_consent": "yes"},
                {"lead_id": "L2", "name": "Bela", "phone": "+62 813-5555-5555", "email": "bela@example.com", "preferred_contact": "email", "purchase_timeline": "5 months", "contact_consent": "yes"},
                {"lead_id": "L3", "name": "Candra", "phone": "", "email": "candra@example.com", "preferred_contact": "email", "purchase_timeline": "not sure", "contact_consent": "yes"},
                {"lead_id": "L4", "name": "Dina", "phone": "+62 811-1111-1111", "email": "dina@example.com", "preferred_contact": "phone", "purchase_timeline": "1 month", "contact_consent": "no"},
                {"lead_id": "L5", "name": "Eka", "phone": "+62 812-2222-2222", "email": "eka@example.com", "preferred_contact": "phone", "purchase_timeline": "3-6 months", "contact_consent": "yes"},
                {"lead_id": "L1", "name": "Ari duplicate", "phone": "+62 812-3456-7890", "email": "ari@example.com", "preferred_contact": "phone", "purchase_timeline": "2 months", "contact_consent": "yes"},
            ]
        )

        processed, summary = process_leads(source)

        self.assertEqual(processed["lead_id"].tolist(), ["L1", "L2", "L3", "L4", "L5"])
        self.assertEqual(
            processed["lead_status"].tolist(),
            ["HOT", "NURTURE", "REVIEW", "HOT", "REVIEW"],
        )
        self.assertEqual(
            processed["next_action"].tolist(),
            ["CALL_QUEUE", "NURTURE_QUEUE", "MANUAL_REVIEW", "CONSENT_REQUIRED", "MANUAL_REVIEW"],
        )
        self.assertEqual(summary["duplicates_removed"], 1)
        self.assertEqual(summary["hot"], 2)
        self.assertEqual(summary["nurture"], 1)
        self.assertEqual(summary["review"], 2)

    def test_pipeline_writes_queues_and_summary_without_modifying_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = root / "leads.csv"
            output_dir = root / "output"
            pd.DataFrame(
                [
                    {"lead_id": "L1", "name": "Ari", "phone": "+62 812-3456-7890", "email": "ari@example.com", "preferred_contact": "phone", "purchase_timeline": "2 months", "contact_consent": "yes"},
                    {"lead_id": "L2", "name": "Bela", "phone": "+62 813-5555-5555", "email": "bela@example.com", "preferred_contact": "email", "purchase_timeline": "5 months", "contact_consent": "yes"},
                    {"lead_id": "L3", "name": "Candra", "phone": "", "email": "candra@example.com", "preferred_contact": "email", "purchase_timeline": "not sure", "contact_consent": "yes"},
                    {"lead_id": "L4", "name": "Dina", "phone": "+62 811-1111-1111", "email": "dina@example.com", "preferred_contact": "phone", "purchase_timeline": "1 month", "contact_consent": "no"},
                    {"lead_id": "L1", "name": "Ari duplicate", "phone": "+62 812-3456-7890", "email": "ari@example.com", "preferred_contact": "phone", "purchase_timeline": "2 months", "contact_consent": "yes"},
                ]
            ).to_csv(input_path, index=False)
            original_bytes = input_path.read_bytes()

            result = run_pipeline(input_path, output_dir)

            self.assertEqual(result["summary"]["duplicates_removed"], 1)
            self.assertTrue((output_dir / "classified_leads.csv").is_file())
            self.assertEqual(len(pd.read_csv(output_dir / "hot_call_queue.csv")), 1)
            self.assertEqual(len(pd.read_csv(output_dir / "nurture_queue.csv")), 1)
            self.assertEqual(len(pd.read_csv(output_dir / "manual_review.csv")), 2)
            self.assertEqual(json.loads((output_dir / "summary.json").read_text()), result["summary"])
            self.assertEqual(input_path.read_bytes(), original_bytes)


if __name__ == "__main__":
    unittest.main()
