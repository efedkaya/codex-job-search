"""Vacancy ledger invariants, with entirely fictional source data."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "skills/job-search/scripts/vacancies.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("vacancies", SCRIPT)
vacancies = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vacancies)


class VacancyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root / "private"
        self.path = self.workspace / "vacancies.json"
        self.data = {"version": 1, "vacancies": {}}
        self.discovery = {"employer": "Fictional Company", "title": "Research Coordinator",
                          "summary": "Coordinates fictional market research projects.",
                          "discovered_at": "2026-10-13T12:00:00-04:00",
                          "provenance": "Fictional result; posting ID explicitly shown.",
                          "aliases": [{"source": "example-board", "posting_id": "EX-42"}]}

    def cli(self, command, obj=None, succeeds=True, extra=()):
        args = [sys.executable, str(SCRIPT), "--workspace", str(self.workspace), command, *extra]
        if obj is not None:
            source = self.root / "input.json"
            source.write_text(json.dumps(obj), encoding="utf-8")
            args += ["--input", str(source)]
        result = subprocess.run(args, capture_output=True, text=True)
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stderr)
        return result

    def assess(self, row, **changes):
        return {"vacancy_id": row["vacancy_id"], "expected_revision": row["revision"],
                "status": "possible", "reason": "Relevant research skills; availability still unknown.",
                "skills_fit": "strong", "eligibility": "unknown", "readiness": "needs_work",
                "profile_revision": "profile-1", "assessed_at": "2026-10-13T17:00:00+00:00",
                "provenance": "Fictional candidate evidence compared with observed requirements.", **changes}

    def verify(self, row, **changes):
        return {"vacancy_id": row["vacancy_id"], "expected_revision": row["revision"],
                "status": "verified_open", "checked_at": "2026-10-13T16:30:00+00:00",
                "source_url": "https://careers.example.invalid/jobs/42",
                "provenance": "Official fictional requisition explicitly open at check time.", **changes}

    def report(self, row, **changes):
        return {"vacancy_id": row["vacancy_id"], "expected_revision": row["revision"],
                "profile_revision": "profile-1", "reported_at": "2026-10-13T18:00:00+00:00",
                "report_ref": "Fictional private shortlist note 1", **changes}

    def test_exact_aliases_canonical_ids_and_no_title_matching(self):
        first = vacancies.upsert(self.data, self.discovery)
        again = vacancies.upsert(self.data, {**self.discovery, "aliases": [
            {"source": " Example-Board ", "posting_id": "EX-42"}]})
        self.assertEqual(first["vacancy_id"], again["vacancy_id"])
        different = vacancies.upsert(self.data, {**self.discovery, "aliases": [
            {"source": "example-board", "posting_id": "EX-43"}]})
        self.assertNotEqual(first["vacancy_id"], different["vacancy_id"])
        self.assertEqual(len(self.data["vacancies"]), 2)
        connected = {**self.discovery, "requisition_id": "R-42",
                     "official_url": "https://careers.example.invalid/jobs/42?jobId=42&utm_source=board"}
        upgraded = vacancies.upsert(self.data, connected)
        another_source = vacancies.upsert(self.data, {**connected, "aliases": [
            {"source": "other-board", "posting_id": "ABC"}],
            "official_url": "https://careers.example.invalid/jobs/42?jobId=42"})
        self.assertEqual(upgraded["vacancy_id"], another_source["vacancy_id"])
        self.assertEqual(another_source["revision"], upgraded["revision"])
        self.assertEqual(len(self.data["vacancies"][first["vacancy_id"]]["aliases"]), 2)
        vacancies.validate(self.data)

    def test_conflicting_bridges_employers_and_requisitions_fail_without_mutation(self):
        first = vacancies.upsert(self.data, {**self.discovery, "requisition_id": "R-1"})
        vacancies.upsert(self.data, {**self.discovery, "aliases": [{"source": "second", "posting_id": "B"}],
                                     "requisition_id": "R-2"})
        for obj in ({**self.discovery, "requisition_id": "R-2"},
                    {**self.discovery, "employer": "Other Fictional Company"},
                    {**self.discovery, "requisition_id": "NOT-R-1"}):
            before = copy.deepcopy(self.data)
            with self.assertRaises(vacancies.TrackerError):
                vacancies.upsert(self.data, obj)
            self.assertEqual(before, self.data)
        self.assertEqual(self.data["vacancies"][first["vacancy_id"]]["requisition_id"], "R-1")

    def test_same_req_different_employers_and_same_ids_different_sources_stay_distinct(self):
        one = vacancies.upsert(self.data, {**self.discovery, "aliases": [], "requisition_id": "42"})
        two = vacancies.upsert(self.data, {**self.discovery, "aliases": [], "requisition_id": "42",
                                         "employer": "Another Fictional Company"})
        self.assertNotEqual(one["vacancy_id"], two["vacancy_id"])
        for source in ("one", "two"):
            vacancies.upsert(self.data, {**self.discovery, "aliases": [{"source": source, "posting_id": "42"}]})
        self.assertEqual(len(self.data["vacancies"]), 4)

    def test_pending_assessment_reporting_and_profile_revision_are_independent(self):
        row = vacancies.upsert(self.data, self.discovery)
        self.assertEqual(vacancies.listing(self.data, pending=True)["total"], 1)
        with self.assertRaises(vacancies.TrackerError):
            vacancies.update(self.data, self.report(row), "reporting")
        assessed = vacancies.update(self.data, self.assess(row), "assessment")
        self.assertEqual(assessed["skills_fit"], "strong")
        self.assertEqual(assessed["eligibility"], "unknown")
        self.assertEqual(assessed["readiness"], "needs_work")
        self.assertEqual(assessed["reporting_status"], "unreported")
        self.assertEqual(vacancies.listing(self.data, pending=True, profile_revision="profile-1")["total"], 0)
        self.assertEqual(vacancies.listing(self.data, pending=True, profile_revision="profile-2")["total"], 1)
        with self.assertRaises(vacancies.TrackerError):
            vacancies.update(self.data, self.report(row, profile_revision="profile-2"), "reporting")
        reported = vacancies.update(self.data, self.report(row), "reporting")
        self.assertEqual(reported["reporting_status"], "reported")
        vacancies.upsert(self.data, {**self.discovery, "discovered_at": "2026-10-14T16:00:00+00:00"})
        self.assertEqual(vacancies.listing(self.data, unreported=True)["total"], 0)
        vacancies.update(self.data, self.assess(row, status="rejected", eligibility="ineligible",
                                              assessed_at="2026-10-14T17:00:00+00:00"), "assessment")
        self.assertEqual(vacancies.listing(self.data, unreported=True)["total"], 1)
        vacancies.validate(self.data)

    def test_material_changes_invalidate_all_reuse_and_reject_stale_writes(self):
        row = vacancies.upsert(self.data, self.discovery)
        vacancies.update(self.data, self.assess(row), "assessment")
        vacancies.update(self.data, self.verify(row), "verification")
        vacancies.update(self.data, self.report(row), "reporting")
        changed = vacancies.upsert(self.data, {**self.discovery, "details": {"salary": "Fictional range B"}})
        self.assertTrue(changed["material_changed"])
        self.assertEqual(changed["revision"], 2)
        self.assertEqual(changed["assessment_status"], "pending")
        self.assertEqual(changed["reporting_status"], "unreported")
        stored = self.data["vacancies"][row["vacancy_id"]]
        self.assertFalse(vacancies.verification(stored, 24, "2026-10-13T18:00:00+00:00")["reusable"])
        self.assertEqual(stored["assessment"]["reason"], self.assess(row)["reason"])
        for kind, obj in (("assessment", self.assess(row)), ("verification", self.verify(row)),
                          ("reporting", self.report(row))):
            before = copy.deepcopy(self.data)
            with self.assertRaisesRegex(vacancies.TrackerError, "stale"):
                vacancies.update(self.data, obj, kind)
            self.assertEqual(before, self.data)
        vacancies.validate(self.data)

    def test_cache_requires_recent_explicit_verification_and_provenance(self):
        row = vacancies.upsert(self.data, self.discovery)
        stored = self.data["vacancies"][row["vacancy_id"]]
        at = "2026-10-13T17:30:00+00:00"
        self.assertFalse(vacancies.verification(stored, 24, at)["reusable"])
        vacancies.update(self.data, self.verify(row), "verification")
        self.assertTrue(vacancies.verification(stored, 1, at)["reusable"])
        self.assertFalse(vacancies.verification(stored, .5, at)["reusable"])
        self.assertFalse(vacancies.verification(stored, 24, "2026-10-13T15:00:00+00:00")["reusable"])
        for status in ("blocked", "unavailable", "unverified"):
            vacancies.update(self.data, self.verify(row, status=status), "verification")
            self.assertFalse(vacancies.verification(stored, 24, at)["reusable"])
        for bad in (float("inf"), float("nan"), -1, True):
            with self.assertRaises(vacancies.TrackerError):
                vacancies.verification(stored, bad, at)

    def test_older_discovery_and_evidence_cannot_replace_newer_facts(self):
        row = vacancies.upsert(self.data, self.discovery)
        vacancies.update(self.data, self.verify(row), "verification")
        before = copy.deepcopy(self.data)
        with self.assertRaisesRegex(vacancies.TrackerError, "Older discovery"):
            vacancies.upsert(self.data, {**self.discovery, "title": "Changed fictional role",
                                        "discovered_at": "2026-10-12T12:00:00+00:00"})
        with self.assertRaisesRegex(vacancies.TrackerError, "Older verification"):
            vacancies.update(self.data, self.verify(row, checked_at="2026-10-12T12:00:00+00:00"), "verification")
        self.assertEqual(before, self.data)

    def test_read_only_compact_pagination_get_and_independence_from_search_state(self):
        self.assertEqual(self.cli("pending")["total"], 0)
        self.assertFalse(self.workspace.exists())
        for number in range(3):
            row = self.cli("upsert", {**self.discovery, "aliases": [{"source": "example", "posting_id": str(number)}]})
        result = self.cli("list", extra=("--limit", "2", "--offset", "1", "--source", "example"))
        self.assertEqual(result["total"], 3)
        self.assertEqual(len(result["vacancies"]), 2)
        self.assertNotIn("summary", result["vacancies"][0])
        full = self.cli("get", extra=("--id", row["vacancy_id"]))
        self.assertEqual(full["summary"], self.discovery["summary"])
        self.assertEqual(full["discovery_provenance"], self.discovery["provenance"])
        self.assertEqual(self.cli("summary")["assessment_counts"]["pending"], 3)
        self.assertFalse((self.workspace / "tracker.json").exists())
        self.assertFalse((self.workspace / "search_state.json").exists())

    def test_malformed_inputs_preserve_disk_state_and_leave_no_lock(self):
        row = self.cli("upsert", self.discovery)
        for command, obj in (("upsert", {**self.discovery, "aliases": []}),
                             ("upsert", {**self.discovery, "discovered_at": "2026-10-13"}),
                             ("upsert", {**self.discovery, "provenance": ""}),
                             ("upsert", {**self.discovery, "official_url": "https://user:secret@example.invalid/"}),
                             ("upsert", {**self.discovery, "aliases": [{"source": "x", "posting_id": 42}]}),
                             ("upsert", {**self.discovery, "details": {"unexpected": "x"}}),
                             ("assess", self.assess(row, expected_revision=True)),
                             ("assess", self.assess(row, skills_fit="excellent")),
                             ("verify", self.verify(row, checked_at="bad")),
                             ("report", self.report(row))):
            before = self.path.read_bytes()
            self.cli(command, obj, succeeds=False)
            self.assertEqual(before, self.path.read_bytes())
            self.assertFalse((self.workspace / ".vacancies.lock").exists())
        self.cli("list", succeeds=False, extra=("--limit", "0"))

    def test_batch_is_atomic_bounded_and_preserves_valid_earlier_records(self):
        first = self.cli("upsert", self.discovery)
        more = {**self.discovery, "aliases": [{"source": "another", "posting_id": "43"}]}
        result = self.cli("upsert-batch", {"vacancies": [self.discovery, more]})
        self.assertEqual((result["received"], result["created"], result["changed"]), (2, 1, 0))
        before = self.path.read_bytes()
        for items in ([], [self.discovery] * 101,
                      [{**self.discovery, "title": "Updated"}, {**more, "provenance": ""}]):
            self.cli("upsert-batch", {"vacancies": items}, succeeds=False)
            self.assertEqual(before, self.path.read_bytes())
        data = json.loads(before)
        prior = copy.deepcopy(data)
        with self.assertRaises(vacancies.TrackerError):
            vacancies.upsert_batch(data, {"vacancies": [{**self.discovery, "title": "Updated"}, {}]})
        self.assertEqual(prior, data)
        self.assertEqual(self.cli("get", extra=("--id", first["vacancy_id"]))["title"], self.discovery["title"])

    def test_cli_assessment_verification_and_reporting_roundtrip(self):
        row = self.cli("upsert", self.discovery)
        self.cli("assess", self.assess(row))
        self.cli("verify", self.verify(row))
        self.cli("report", self.report(row))
        self.cli("assess", self.assess(row))  # Exact repeat does not clear a report.
        full = self.cli("get", extra=("--id", row["vacancy_id"]))
        self.assertEqual(full["reporting_status"], "reported")
        cache = self.cli("verification", extra=("--id", row["vacancy_id"], "--max-age-hours", "1",
                                                "--at", "2026-10-13T17:30:00+00:00"))
        self.assertTrue(cache["reusable"])
        before = self.path.read_bytes()
        self.assertEqual(self.cli("pending", extra=("--profile-revision", "profile-2"))["total"], 1)
        self.assertEqual(before, self.path.read_bytes())
        self.cli("upsert", {**self.discovery, "summary": "Changed fictional requirements."})
        full = self.cli("get", extra=("--id", row["vacancy_id"]))
        self.assertEqual(full["assessment_status"], "pending")
        self.assertEqual(full["reporting_status"], "unreported")
        self.assertEqual(full["assessment"]["revision"], 1)
        self.assertEqual(full["revision"], 2)

    def test_lock_covers_load_and_update_atomic_failure_preserves_state(self):
        self.cli("upsert", self.discovery)
        before = self.path.read_bytes()
        with vacancies.VacancyStore(str(self.workspace)) as store:
            self.cli("upsert", {**self.discovery, "title": "Changed"}, succeeds=False)
            data = store.load()
            vacancies.upsert(data, {**self.discovery, "title": "Changed"})
            with mock.patch.object(vacancies.os, "replace", side_effect=OSError("simulated disk failure")):
                with self.assertRaises(OSError):
                    store.save(data)
        self.assertEqual(before, self.path.read_bytes())
        self.assertFalse(list(self.workspace.glob(".tracker-*.tmp")))
        self.cli("upsert", {**self.discovery, "aliases": [{"source": "another", "posting_id": "43"}]})
        self.assertEqual(self.cli("summary")["total"], 2)
        with self.assertRaisesRegex(vacancies.TrackerError, "lock"):
            vacancies.VacancyStore(str(self.workspace)).save(self.data)
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(self.workspace.stat().st_mode), 0o700)

    def test_private_guards_symlinks_invalid_stored_schema_and_size_limit(self):
        for path in (str(SCRIPT.parents[3]), str(SCRIPT.parent), "relative"):
            with self.assertRaises(vacancies.TrackerError):
                vacancies.VacancyStore(path)
        self.cli("upsert", self.discovery)
        before = self.path.read_bytes()
        with vacancies.VacancyStore(str(self.workspace)) as store:
            with mock.patch.object(vacancies, "MAX_STATE_BYTES", 10):
                with self.assertRaisesRegex(vacancies.TrackerError, "10 MB"):
                    store.save(store.load())
        self.assertEqual(before, self.path.read_bytes())
        malformed = json.loads(before)
        next(iter(malformed["vacancies"].values()))["revision"] = True
        self.path.write_text(json.dumps(malformed), encoding="utf-8")
        corrupt = self.path.read_bytes()
        self.cli("upsert", self.discovery, succeeds=False)
        self.assertEqual(corrupt, self.path.read_bytes())
        self.path.unlink()
        real = self.root / "real.json"
        real.write_bytes(before)
        try:
            self.path.symlink_to(real)
        except OSError:
            self.skipTest("Symlinks unavailable")
        self.cli("get", succeeds=False, extra=("--id", "unknown"))
        self.cli("upsert", self.discovery, succeeds=False)
        self.assertEqual(before, real.read_bytes())


if __name__ == "__main__":
    unittest.main()
