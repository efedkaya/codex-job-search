"""Fictional tracker regressions; run with Python's standard-library unittest."""
import copy
from datetime import date, timedelta
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "skills/job-search/scripts"
sys.path.insert(0, str(SCRIPTS))
import track


def empty_tracker():
    return {"version": track.VERSION, **{key: [] for key in track.COLLECTIONS}}


def job_input(url="https://jobs.example/role", requisition=None, employer="Fictional Employer"):
    result = {"employer": employer, "title": "Research Coordinator", "posting_url": url,
              "checked_on": "2026-10-18"}
    if requisition is not None:
        result["requisition_id"] = requisition
    return result


def time_input(day, basis="reported"):
    return {"date": day, "human_minutes": 25, "agent_minutes": 5,
            "category": "search", "basis": basis}


class FixedDate(date):
    @classmethod
    def today(cls):
        return cls(2026, 10, 19)


class JobIdentityTests(unittest.TestCase):
    def setUp(self):
        self.data = empty_tracker()

    def test_conflicting_requisition_and_url_preserve_jobs_and_application(self):
        first = track.upsert_job(self.data, job_input("https://jobs.example/first"))
        track.record_application(self.data, {"job_id": first["job_id"], "created_on": "2026-10-18"})
        track.upsert_job(self.data, job_input("https://jobs.example/second", "REQ-42"))
        original = copy.deepcopy(self.data)

        with self.assertRaisesRegex(track.TrackerError, "Conflicting job identities"):
            track.upsert_job(self.data, job_input("https://jobs.example/first", "REQ-42"))

        self.assertEqual(self.data, original)

    def test_single_url_record_is_enriched_without_changing_application_identity(self):
        first = track.upsert_job(self.data, job_input())
        application = track.record_application(self.data, {"job_id": first["job_id"], "created_on": "2026-10-18"})
        enriched = track.upsert_job(self.data, job_input(requisition="REQ-42"))
        self.assertEqual(enriched["job_id"], application["job_id"])
        self.assertEqual(enriched["requisition_id"], "REQ-42")
        self.assertEqual(len(self.data["jobs"]), 1)

    def test_distinct_requisitions_can_share_a_url_and_update_independently(self):
        first = track.upsert_job(self.data, job_input(requisition="REQ-1"))
        second = track.upsert_job(self.data, job_input(requisition="REQ-2"))
        second_original = copy.deepcopy(second)
        update = job_input(requisition="REQ-1")
        update["notes"] = "Fictional update to the first requisition only."
        result = track.upsert_job(self.data, update)
        self.assertNotEqual(first["job_id"], second["job_id"])
        self.assertEqual(result["job_id"], first["job_id"])
        self.assertEqual(second, second_original)
        self.assertEqual(len(self.data["jobs"]), 2)

    def test_shared_url_without_requisition_is_ambiguous_and_unchanged(self):
        track.upsert_job(self.data, job_input(requisition="REQ-1"))
        track.upsert_job(self.data, job_input(requisition="REQ-2"))
        original = copy.deepcopy(self.data)
        with self.assertRaisesRegex(track.TrackerError, "Ambiguous posting URL"):
            track.upsert_job(self.data, job_input())
        self.assertEqual(self.data, original)

    def test_known_requisition_can_update_its_url(self):
        first = track.upsert_job(self.data, job_input(requisition="REQ-42"))
        result = track.upsert_job(self.data, job_input("https://jobs.example/new-url", "REQ-42"))
        self.assertEqual(result["job_id"], first["job_id"])
        self.assertEqual(result["canonical_url"], "https://jobs.example/new-url")
        self.assertEqual(len(self.data["jobs"]), 1)

    def test_normalized_employer_and_tracking_url_match_same_record(self):
        first = track.upsert_job(self.data, job_input("https://jobs.example/role?id=42&utm_source=fictional"))
        result = track.upsert_job(self.data, job_input("https://jobs.example/role?id=42", "REQ-42",
                                                        "  FICTIONAL   EMPLOYER  "))
        self.assertEqual(result["job_id"], first["job_id"])
        self.assertEqual(len(self.data["jobs"]), 1)

    def test_same_requisition_at_different_employers_stays_separate(self):
        track.upsert_job(self.data, job_input(requisition="REQ-42"))
        track.upsert_job(self.data, job_input(requisition="REQ-42", employer="Another Fictional Employer"))
        self.assertEqual(len(self.data["jobs"]), 2)


class TimeLogTests(unittest.TestCase):
    def test_future_dates_rejected_for_every_basis_without_mutation(self):
        for basis in ("reported", "measured", "estimated"):
            with self.subTest(basis=basis), patch.object(track, "date", FixedDate):
                data = empty_tracker()
                original = copy.deepcopy(data)
                with self.assertRaisesRegex(track.TrackerError, "completed work.*future-dated"):
                    track.log_time(data, time_input("2026-10-20", basis))
                self.assertEqual(data, original)

    def test_today_and_past_dates_preserve_each_duration_basis(self):
        for day in ("2026-10-19", "2026-10-18", "2024-02-29"):
            for basis in ("reported", "measured", "estimated"):
                with self.subTest(day=day, basis=basis), patch.object(track, "date", FixedDate):
                    data = empty_tracker()
                    row = track.log_time(data, time_input(day, basis))
                    self.assertEqual(row["date"], day)
                    self.assertEqual(row["basis"], basis)
                    self.assertEqual(row["human_minutes"], 25)
                    self.assertEqual(row["agent_minutes"], 5)
                    self.assertEqual(track.summary(data, None)["time_by_basis"][basis], 25)

    def test_omitted_basis_still_defaults_to_reported_and_zero_is_allowed(self):
        with patch.object(track, "date", FixedDate):
            row = track.log_time(empty_tracker(), {"date": "2026-10-19", "human_minutes": 0,
                                                   "category": "search"})
        self.assertEqual(row["basis"], "reported")
        self.assertEqual(row["human_minutes"], 0)
        self.assertEqual(row["agent_minutes"], 0)

    def test_invalid_dates_still_rejected_without_mutation(self):
        for invalid in ("2026-02-29", "2026-2-01", "not a date"):
            with self.subTest(date=invalid), patch.object(track, "date", FixedDate):
                data = empty_tracker()
                with self.assertRaisesRegex(track.TrackerError, "valid YYYY-MM-DD"):
                    track.log_time(data, time_input(invalid))
                self.assertEqual(data, empty_tracker())


class CommandLinePersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="fictional-job-search-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.workspace = self.root / "private"
        self.input_path = self.root / "input.json"
        self.invoke("init")

    def invoke(self, command, payload=None, expected_returncode=0):
        args = [sys.executable, "-B", str(SCRIPTS / "track.py"), "--workspace", str(self.workspace), command]
        if payload is not None:
            self.input_path.write_text(json.dumps(payload), encoding="utf-8")
            args.extend(["--input", str(self.input_path)])
        result = subprocess.run(args, capture_output=True, text=True, check=False,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, expected_returncode, result.stderr)
        return result

    def assert_only_tracker_remains(self):
        self.assertEqual({path.name for path in self.workspace.iterdir()}, {"tracker.json"})

    def test_identity_conflict_preserves_exact_file_and_existing_application(self):
        first = json.loads(self.invoke("upsert-job", job_input("https://jobs.example/first")).stdout)
        self.invoke("record-application", {"job_id": first["job_id"], "created_on": "2026-10-18"})
        self.invoke("upsert-job", job_input("https://jobs.example/second", "REQ-42"))
        tracker_path = self.workspace / "tracker.json"
        before = tracker_path.read_bytes()

        result = self.invoke("upsert-job", job_input("https://jobs.example/first", "REQ-42"), 2)

        self.assertIn("Conflicting job identities", result.stderr)
        self.assertEqual(tracker_path.read_bytes(), before)
        self.assert_only_tracker_remains()
        self.invoke("list")  # A rejected write must leave the workspace usable.

    def test_future_time_preserves_exact_file_for_every_basis(self):
        today = date.today()
        self.invoke("log-time", time_input(today.isoformat()))
        tracker_path = self.workspace / "tracker.json"
        before = tracker_path.read_bytes()
        tomorrow = (today + timedelta(days=1)).isoformat()
        for basis in ("reported", "measured", "estimated"):
            with self.subTest(basis=basis):
                result = self.invoke("log-time", time_input(tomorrow, basis), 2)
                self.assertIn("computer's local date", result.stderr)
                self.assertEqual(tracker_path.read_bytes(), before)
                self.assert_only_tracker_remains()
        self.invoke("summary")


if __name__ == "__main__":
    unittest.main()
