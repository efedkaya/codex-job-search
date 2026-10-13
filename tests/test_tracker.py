"""Behavior tests for the offline tracker; every record below is fictional."""
import csv
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "skills/job-search/scripts/track.py"
SPEC = importlib.util.spec_from_file_location("track", SCRIPT)
track = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(track)


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root / "private"
        self.run_cli("init")

    def run_cli(self, command, obj=None, *extra, succeeds=True):
        args = [sys.executable, str(SCRIPT), "--workspace", str(self.workspace), command]
        if obj is not None:
            source = self.root / "input.json"
            source.write_text(json.dumps(obj), encoding="utf-8")
            args += ["--input", str(source)]
        result = subprocess.run(args + list(extra), capture_output=True, text=True)
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stderr)
        return result

    def payload(self, **changes):
        return {"employer": "Example Company", "title": "Research Coordinator",
                "posting_url": "https://careers.example/jobs?id=100", "checked_on": "2025-01-01",
                "status": "open", **changes}

    def job(self, **changes):
        return self.run_cli("upsert-job", self.payload(**changes))

    def application(self, job=None):
        job = job or self.job()
        return self.run_cli("record-application", {"job_id": job["job_id"], "created_on": "2025-01-01"})

    def event(self, app, kind, **changes):
        return self.run_cli("record-event", {"application_id": app["application_id"], "type": kind,
                                             "occurred_on": "2025-01-02", **changes})

    def bytes(self):
        return (self.workspace / "tracker.json").read_bytes()

    def test_tracking_parameters_deduplicate_but_job_identifiers_survive(self):
        first = self.job(posting_url="https://careers.example/jobs?id=100&utm_source=mail&gclid=abc")
        again = self.job(posting_url="https://careers.example/jobs?id=100&utm_campaign=weekly")
        distinct = self.job(posting_url="https://careers.example/jobs?id=101")
        self.assertEqual(first["job_id"], again["job_id"])
        self.assertNotEqual(first["job_id"], distinct["job_id"])
        self.assertEqual(again["canonical_url"], "https://careers.example/jobs?id=100")
        self.assertEqual(len(self.run_cli("list")), 2)
        self.assertEqual(len(again["history"]), 2)

    def test_same_employer_title_different_requisitions_survive(self):
        first = self.job(requisition_id="REQ-1")
        second = self.job(requisition_id="REQ-2")
        self.run_cli("upsert-job", self.payload(), succeeds=False)
        updated = self.job(requisition_id="REQ-1", posting_url="https://careers.example/new/REQ-1")
        self.assertNotEqual(first["job_id"], second["job_id"])
        self.assertEqual(first["job_id"], updated["job_id"])
        self.assertEqual(len(self.run_cli("list")), 2)

    def test_new_requisition_can_enrich_unidentified_existing_job(self):
        first = self.job()
        enriched = self.job(requisition_id="REQ-1")
        self.assertEqual(first["job_id"], enriched["job_id"])

    def test_bad_input_and_invalid_dates_do_not_change_valid_data(self):
        self.job()
        original = self.bytes()
        for changes in ({"checked_on": "2025-02-30"}, {"checked_on": "20250101"},
                        {"status": "applied"}, {"checked_on": 0}, {"title": ""},
                        {"posting_url": "javascript:alert(1)"}, {"unexpected": "ignored?"},
                        {"closure_confirmed": "true"}):
            with self.subTest(changes=changes):
                self.run_cli("upsert-job", self.payload(**changes), succeeds=False)
                self.assertEqual(self.bytes(), original)
        source = self.root / "broken.json"
        source.write_text("{broken", encoding="utf-8")
        self.run_cli("upsert-job", None, "--input", str(source), succeeds=False)
        self.assertEqual(self.bytes(), original)

    def test_unavailable_is_not_closed_and_closure_requires_confirmation(self):
        self.job()
        failed = self.job(status="unverified", retrieval_status="blocked")
        self.assertEqual(failed["status"], "open")
        self.assertEqual(failed["retrieval_status"], "blocked")
        before = self.bytes()
        self.run_cli("upsert-job", self.payload(status="closed", retrieval_status="unavailable"), succeeds=False)
        self.assertEqual(before, self.bytes())
        closed = self.job(status="closed", closure_confirmed=True, closure_evidence="Employer posting says closed.")
        self.assertEqual(closed["status"], "closed")
        self.run_cli("upsert-job", self.payload(), succeeds=False)
        reopened = self.job(reopen_confirmed=True, reopen_evidence="Employer reopened this same requisition.")
        self.assertEqual(reopened["status"], "open")

    def test_application_attempts_are_distinct_and_start_as_drafts(self):
        job = self.job()
        first, second = self.application(job), self.application(job)
        self.assertNotEqual(first["application_id"], second["application_id"])
        self.assertNotEqual(first["application_id"], job["job_id"])
        self.assertEqual(first["status"], "draft")
        self.assertEqual(second["status"], "draft")
        self.run_cli("record-application", {"job_id": job["job_id"], "created_on": "2025-01-01",
                                            "status": "submitted"}, succeeds=False)
        self.assertEqual(self.run_cli("list")[0]["status"], "open")

    def test_sends_require_confirmation_and_planned_stays_planned(self):
        app = self.application()
        for kind in ("submitted", "followup_sent"):
            before = self.bytes()
            self.run_cli("record-event", {"application_id": app["application_id"], "type": kind,
                                          "occurred_on": "2025-01-02", "evidence": "I will send it tomorrow."}, succeeds=False)
            self.assertEqual(before, self.bytes())
        self.event(app, "followup_planned", notes="Intend to send next week.")
        self.assertEqual(self.run_cli("summary")["applications_by_status"]["draft"], 1)
        self.event(app, "submitted", confirmed=True, evidence="User reports the form was submitted.")
        self.assertEqual(self.run_cli("summary")["applications_by_status"]["submitted"], 1)
        self.run_cli("record-event", {"application_id": app["application_id"], "type": "followup_sent",
                                      "occurred_on": "2999-01-01", "confirmed": True,
                                      "evidence": "A future action cannot be confirmed."}, succeeds=False)

    def test_terminal_state_and_progress_cannot_regress(self):
        app = self.application()
        self.event(app, "interview_scheduled", confirmed=True, evidence="User reports receiving an invitation.")
        before = self.bytes()
        self.run_cli("record-event", {"application_id": app["application_id"], "type": "submitted",
                                      "occurred_on": "2025-01-02", "confirmed": True,
                                      "evidence": "Attempting a status regression."}, succeeds=False)
        self.assertEqual(self.bytes(), before)
        self.event(app, "rejected", confirmed=True, evidence="User reports rejection email.")
        self.run_cli("record-event", {"application_id": app["application_id"], "type": "offer_received",
                                      "occurred_on": "2025-01-02", "confirmed": True,
                                      "evidence": "Cannot silently replace terminal state."}, succeeds=False)
        self.event(app, "note", notes="Reflect on interview questions.")
        self.assertEqual(self.run_cli("summary")["applications_by_status"]["rejected"], 1)

    def test_csv_quoting_utf8_and_formula_protection(self):
        self.job(employer='=HYPERLINK("https://malicious.example")', title='Résumé, "Research"', notes="@SUM(1,2)")
        destination = self.root / "jobs.csv"
        self.run_cli("export", None, "--output", str(destination))
        with destination.open(encoding="utf-8-sig", newline="") as source:
            exported = list(csv.DictReader(source))
        self.assertTrue(exported[0]["employer"].startswith("'="))
        self.assertTrue(exported[0]["notes"].startswith("'@"))
        self.assertEqual(exported[0]["title"], 'Résumé, "Research"')
        for value in ("=1+1", " \t+1", "\x00-1", "\ufeff@SUM(1)", "\u00a0=1"):
            self.assertTrue(track.csv_safe(value).startswith("'"))
        self.assertEqual(track.csv_safe("ordinary text"), "ordinary text")
        self.assertEqual(track.csv_safe(0), "0")
        self.run_cli("export", None, "--output", str(destination), succeeds=False)
        self.run_cli("export", None, "--output", str(self.workspace / "tracker.json"), succeeds=False)

    def test_lock_prevents_concurrent_writer_and_keeps_data(self):
        self.job()
        before = self.bytes()
        with track.Store(str(self.workspace)):
            result = self.run_cli("upsert-job", self.payload(title="Concurrent update"), succeeds=False)
            self.assertIn("locked", result.stderr)
            self.assertEqual(self.bytes(), before)
        self.job(title="Update after release")
        self.assertFalse((self.workspace / ".tracker.lock").exists())

    def test_atomic_replace_failure_preserves_previous_file(self):
        self.job()
        before = self.bytes()
        with track.Store(str(self.workspace)) as store:
            data = store.load()
            data["jobs"][0]["title"] = "Unsaved title"
            with mock.patch.object(track.os, "replace", side_effect=OSError("simulated disk failure")):
                with self.assertRaises(OSError):
                    store.save(data)
        self.assertEqual(self.bytes(), before)
        self.assertFalse(list(self.workspace.glob(".tracker-*.tmp")))

    def test_readable_input_cannot_grow_tracker_beyond_readable_byte_limit(self):
        self.job()
        before = self.bytes()
        for character, count in (("x", 5_000_000), ("é", 2_500_000)):
            with self.subTest(character=character):
                # History duplicates changed notes. Both inputs are below the
                # reader limit, but the persisted history would exceed it.
                notes = character * count
                source = self.root / "large-input.json"
                source.write_text(json.dumps(self.payload(notes=notes), ensure_ascii=False),
                                  encoding="utf-8")
                self.assertLess(source.stat().st_size, track.MAX_JSON_BYTES)
                self.assertEqual(track.read_json(source)["notes"], notes)
                result = self.run_cli("upsert-job", None, "--input", str(source), succeeds=False)
                self.assertIn("10 MB readable limit", result.stderr)
                self.assertEqual(self.bytes(), before)
                self.assertEqual(self.run_cli("summary")["jobs"], 1)
                self.assertFalse((self.workspace / ".tracker.lock").exists())
                self.assertFalse(list(self.workspace.glob(".tracker-*.tmp")))

    def test_symlink_data_and_skill_directory_workspace_rejected(self):
        source = self.root / "real-data.json"
        source.write_bytes(self.bytes())
        (self.workspace / "tracker.json").unlink()
        try:
            (self.workspace / "tracker.json").symlink_to(source)
        except OSError:
            self.skipTest("Symlinks unavailable on this platform")
        self.run_cli("list", succeeds=False)
        with self.assertRaises(track.TrackerError):
            track.Store(str(SCRIPT.parents[1] / "private-data"))

    def test_human_agent_time_and_zero_budget_are_separate(self):
        self.run_cli("log-time", {"date": "2025-01-01", "human_minutes": 0, "agent_minutes": 50,
                                  "category": "search", "basis": "measured"})
        self.run_cli("log-time", {"date": "2025-01-01", "human_minutes": 30, "agent_minutes": 2,
                                  "category": "application", "basis": "estimated"})
        result = self.run_cli("summary", None, "--budget-hours", "24")
        self.assertEqual(result["human_minutes"], 30)
        self.assertEqual(result["agent_minutes"], 52)
        self.assertEqual(result["remaining_human_minutes"], 1410)
        self.assertEqual(result["time_by_basis"]["estimated"], 30)
        zero = self.run_cli("summary", None, "--budget-hours", "0")
        self.assertEqual(zero["over_budget_minutes"], 30)
        before = self.bytes()
        self.run_cli("log-time", {"date": "2025-01-01", "human_minutes": True,
                                  "category": "search"}, succeeds=False)
        self.assertEqual(self.bytes(), before)
        self.run_cli("summary", None, "--budget-hours", "nan", succeeds=False)

    def test_public_distribution_cannot_hold_private_workspace(self):
        package = self.root / "public-package"
        package.mkdir()
        (package / "distribution.json").write_text('{"version":"0.1.0","files":[]}', encoding="utf-8")
        script = package / "skills/job-search/scripts/track.py"
        with mock.patch.object(track, "__file__", str(script)):
            for destination in (package, package / "private", package / "examples/candidate"):
                with self.subTest(destination=destination):
                    with self.assertRaisesRegex(track.TrackerError, "public distribution"):
                        track.Store(str(destination))
            store = track.Store(str(self.root / "separate-private"))
            self.assertEqual(store.root, self.root / "separate-private")
        # A standalone installation has no distribution marker and must still work.
        installed = self.root / "installed/skills/job-search/scripts/track.py"
        with mock.patch.object(track, "__file__", str(installed)):
            track.Store(str(self.root / "separate-private"))
            with self.assertRaisesRegex(track.TrackerError, "installed skill"):
                track.Store(str(installed.parents[1] / "private"))

    def test_corrupted_store_is_not_reset_by_init(self):
        path = self.workspace / "tracker.json"
        path.write_text("{broken", encoding="utf-8")
        before = path.read_bytes()
        self.run_cli("init", succeeds=False)
        self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
