"""Search checkpoint invariants using fictional sources and an injected UTC clock."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "skills/job-search/scripts/search_state.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("search_state", SCRIPT)
search = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(search)


class SearchStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root / "private"
        self.data = {"version": 1, "scopes": {}}
        self.scope = {"source": "example-board", "query": "research coordinator",
                      "timezone": "America/Toronto", "filters": {"location": "Example City"}}

    def cli(self, command, obj=None, succeeds=True, full=False):
        args = [sys.executable, str(SCRIPT), "--workspace", str(self.workspace), command]
        if obj is not None:
            source = self.root / "input.json"
            source.write_text(json.dumps(obj), encoding="utf-8")
            args += ["--input", str(source)]
        if full:
            args.append("--full")
        result = subprocess.run(args, capture_output=True, text=True)
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stderr)
        return result

    def start(self, time="2026-10-13T01:00:00+00:00", scope=None):
        with mock.patch.object(search, "now", return_value=time):
            return search.start(self.data, scope or self.scope)

    def finish(self, run, outcome="complete", time="2026-10-13T03:00:00+00:00"):
        with mock.patch.object(search, "now", return_value=time):
            return search.finish(self.data, {"run_id": run["run_id"], "outcome": outcome,
                                            "stop_reason": "Observed end of reachable matching results.",
                                            "coverage_evidence": "Checked pages 1 through 4; no next page."})

    def test_first_plan_read_only_baseline_then_incremental_uses_local_start_day(self):
        plan = self.cli("plan", self.scope)
        self.assertEqual(plan["mode"], "baseline")
        self.assertIsNone(plan["requested_since"])
        self.assertFalse(self.workspace.exists())
        run = self.start()
        self.finish(run, time="2026-10-15T14:00:00+00:00")
        plan = search.plan(self.data, self.scope)
        self.assertEqual(plan["mode"], "incremental")
        self.assertEqual(plan["requested_since"], "2026-10-12")  # UTC Oct 13 is local Oct 12.
        self.assertEqual(plan["fetch_since"], "2026-10-11")
        self.assertTrue(plan["inclusive"])

    def test_filtered_queries_companies_profiles_and_sources_have_separate_baselines(self):
        run = self.start()
        self.finish(run)
        for change in ({"source": "another-board"}, {"query": "sales coordinator"},
                       {"filters": {"employer": "Fictional Bank"}},
                       {"filters": {"location": "Elsewhere"}}, {"profile_revision": "2"}):
            self.assertEqual(search.plan(self.data, {**self.scope, **change})["mode"], "baseline")
        changed_lookback = search.plan(self.data, {**self.scope, "lookback_days": 0})
        self.assertEqual(changed_lookback["mode"], "incremental")
        self.assertEqual(changed_lookback["fetch_since"], "2026-10-12")
        a = {**self.scope, "filters": {"location": "X", "employer": "Y"}}
        b = {**self.scope, "filters": {"employer": "Y", "location": "X"}}
        self.assertEqual(search.plan(self.data, a)["scope_id"], search.plan(self.data, b)["scope_id"])

    def test_partial_blocked_failed_never_advance_and_resume_keeps_coverage_anchor(self):
        for outcome in ("partial", "blocked", "failed"):
            run = self.start()
            search.checkpoint(self.data, {"run_id": run["run_id"], "seen_ids": ["req:1"],
                                         "pages_seen": 2, "resume_locator": {"page": 3}})
            result = self.finish(run, outcome)
            self.assertFalse(result["watermark_advanced"])
            self.assertEqual(search.plan(self.data, self.scope)["mode"], "baseline")
        resumed = self.start("2026-10-16T12:00:00+00:00")
        self.assertEqual(resumed["coverage_started_at"], "2026-10-13T01:00:00+00:00")
        self.assertEqual(len(resumed["pending_runs"]), 3)
        self.assertEqual(resumed["pending_runs"][0]["resume_locator"], {"page": 3})
        self.finish(resumed, time="2026-10-16T14:00:00+00:00")
        plan = search.plan(self.data, self.scope)
        self.assertEqual(plan["requested_since"], "2026-10-12")
        self.assertEqual(plan["pending_runs"], [])
        next_run = self.start("2026-10-18T12:00:00+00:00")
        self.finish(next_run, time="2026-10-18T14:00:00+00:00")
        self.assertEqual(search.plan(self.data, self.scope)["requested_since"], "2026-10-18")

    def test_gap_after_prior_success_stays_at_prior_watermark(self):
        first = self.start()
        self.finish(first)
        before = search.plan(self.data, self.scope)
        failed = self.start("2026-10-20T12:00:00+00:00")
        self.finish(failed, "blocked", "2026-10-20T13:00:00+00:00")
        after = search.plan(self.data, self.scope)
        self.assertEqual(before["requested_since"], after["requested_since"])
        self.assertEqual(before["last_completed_started_at"], after["last_completed_started_at"])
        self.assertEqual(len(after["pending_runs"]), 1)

    def test_repeated_ids_and_cumulative_pages_are_idempotent_not_new_published_proof(self):
        run = self.start()
        payload = {"run_id": run["run_id"], "seen_ids": ["req:1", "req:1", "unknown-date:2"], "pages_seen": 3}
        first = search.checkpoint(self.data, payload)
        again = search.checkpoint(self.data, payload)
        self.assertEqual(first["new_count"], 2)
        self.assertEqual(again["new_ids"], [])
        self.assertEqual(again["pages_seen"], 3)
        self.assertIn("not proof", first["meaning"])
        self.finish(run)
        second = self.start("2026-10-20T12:00:00+00:00")
        self.assertEqual(second["known_ids"], ["req:1", "unknown-date:2"])
        update = search.checkpoint(self.data, {"run_id": second["run_id"], "seen_ids": ["req:1", "req:3"]})
        self.assertEqual(update["new_ids"], ["req:3"])

    def test_old_attempt_finishing_later_cannot_regress_watermark(self):
        first = self.start()
        self.finish(first)
        old = self.start("2026-10-15T12:00:00+00:00", {**self.scope, "lookback_days": 0})
        self.finish(old, "partial", "2026-10-15T13:00:00+00:00")
        resumed = self.start("2026-10-16T12:00:00+00:00")
        parallel = self.start("2026-10-17T12:00:00+00:00")
        self.finish(parallel, time="2026-10-17T13:00:00+00:00")
        later = self.start("2026-10-18T12:00:00+00:00")
        self.finish(later, time="2026-10-18T13:00:00+00:00")
        watermark = search.plan(self.data, self.scope)["last_completed_started_at"]
        self.finish(resumed, time="2026-10-19T12:00:00+00:00")
        self.assertEqual(search.plan(self.data, self.scope)["last_completed_started_at"], watermark)

    def test_finished_runs_immutable_and_malformed_inputs_preserve_file(self):
        run = self.cli("start", self.scope)
        path = self.workspace / "search_state.json"
        for command, payload in (
            ("checkpoint", {"run_id": run["run_id"], "seen_ids": [""]}),
            ("checkpoint", {"run_id": run["run_id"], "seen_ids": [], "pages_seen": True}),
            ("checkpoint", {"run_id": run["run_id"], "seen_ids": [], "resume_locator": []}),
            ("finish", {"run_id": run["run_id"], "outcome": "complete", "stop_reason": "Done"}),
            ("finish", {"run_id": run["run_id"], "outcome": "bad", "stop_reason": "Done"}),
            ("start", {**self.scope, "last_completed_started_at": "2099-01-01"}),
            ("start", {**self.scope, "lookback_days": -1}),
            ("start", {**self.scope, "query": ""}),
            ("start", {**self.scope, "filters": []}),
        ):
            before = path.read_bytes()
            self.cli(command, payload, succeeds=False)
            self.assertEqual(before, path.read_bytes())
        finish = {"run_id": run["run_id"], "outcome": "partial", "stop_reason": "Time budget reached"}
        self.cli("finish", finish)
        before = path.read_bytes()
        self.cli("finish", {**finish, "outcome": "complete", "coverage_evidence": "Late claim"}, succeeds=False)
        self.assertEqual(before, path.read_bytes())
        self.assertFalse((self.workspace / "tracker.json").exists())

    def test_invalid_stored_watermark_fails_closed(self):
        self.cli("start", self.scope)
        path = self.workspace / "search_state.json"
        stored = json.loads(path.read_text())
        item = next(iter(stored["scopes"].values()))
        item["last_completed_started_at"] = "2099-01-01T00:00:00+00:00"
        path.write_text(json.dumps(stored))
        before = path.read_bytes()
        self.cli("start", self.scope, succeeds=False)
        self.assertEqual(before, path.read_bytes())

    def test_completed_cli_roundtrip_reloads_and_tracks_sources_independently(self):
        run = self.cli("start", self.scope)
        self.cli("checkpoint", {"run_id": run["run_id"], "seen_ids": ["example:1"], "pages_seen": 2})
        path = self.workspace / "search_state.json"
        before = path.read_bytes()
        self.cli("checkpoint", {"run_id": run["run_id"], "seen_ids": ["not-saved:2"],
                                "pages_seen": 1}, succeeds=False)
        self.assertEqual(before, path.read_bytes())
        self.cli("finish", {"run_id": run["run_id"], "outcome": "complete",
                            "stop_reason": "Results exhausted", "coverage_evidence": "Pages 1 and 2; no next page"})
        self.assertEqual(self.cli("plan", self.scope)["mode"], "incremental")
        other = {**self.scope, "source": "employer-careers", "filters": {"employer": "Fictional Company"}}
        self.assertEqual(self.cli("plan", other)["mode"], "baseline")
        self.cli("start", other)
        self.assertEqual(len(self.cli("status")["scopes"]), 2)

    def test_oversized_checkpoint_cannot_make_saved_state_unreadable(self):
        run = self.cli("start", self.scope)
        path = self.workspace / "search_state.json"
        before = path.read_bytes()
        # Input fits the 10 MB reader limit; duplicated run/scope IDs do not.
        large_ids = [f"{i}:" + "x" * 1800 for i in range(3000)]
        result = self.cli("checkpoint", {"run_id": run["run_id"], "seen_ids": large_ids}, succeeds=False)
        self.assertIn("10 MB readable limit", result.stderr)
        self.assertIn("archive", result.stderr)
        self.assertEqual(before, path.read_bytes())
        self.assertEqual(self.cli("status")["scopes"][0]["seen_count"], 0)
        self.assertFalse(list(self.workspace.glob(".tracker-*.tmp")))
        # Count serialized UTF-8 bytes, not Python string characters.
        with search.SearchStore(str(self.workspace)) as store:
            data = store.load()
            search.checkpoint(data, {"run_id": run["run_id"],
                                     "seen_ids": [f"{i}:" + "😀" * 1800 for i in range(1000)]})
            with self.assertRaisesRegex(search.TrackerError, "10 MB readable limit"):
                store.save(data)
        self.assertEqual(before, path.read_bytes())
        self.assertEqual(self.cli("plan", self.scope)["mode"], "baseline")

    def test_cumulative_id_limit_preserves_memory_and_disk_across_runs(self):
        first = self.cli("start", self.scope)
        self.cli("checkpoint", {"run_id": first["run_id"],
                                "seen_ids": [f"first:{index}" for index in range(60_000)]})
        self.cli("finish", {"run_id": first["run_id"], "outcome": "partial",
                            "stop_reason": "Fictional scan paused"})
        second = self.cli("start", self.scope)
        path = self.workspace / "search_state.json"
        before = path.read_bytes()
        incoming = [f"second:{index}" for index in range(40_001)]
        payload = {"run_id": second["run_id"], "seen_ids": incoming, "pages_seen": 2}
        # Each batch fits the input count/byte limits, but their scope union does not.
        self.assertLess(len(incoming), search.MAX_SEEN_IDS)
        self.assertLess(len(json.dumps(payload).encode("utf-8")), search.MAX_STATE_BYTES)
        data = search.SearchStore(str(self.workspace)).load()
        original_data = json.dumps(data, sort_keys=True)
        with self.assertRaisesRegex(search.TrackerError, "100,000 posting-ID readable limit"):
            search.checkpoint(data, payload)
        self.assertEqual(json.dumps(data, sort_keys=True), original_data)
        result = self.cli("checkpoint", payload, succeeds=False)
        self.assertIn("100,000 posting-ID readable limit", result.stderr)
        self.assertIn("Archive", result.stderr)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.cli("status")["scopes"][0]["seen_count"], 60_000)
        self.assertFalse((self.workspace / ".search_state.lock").exists())
        # The exact limit remains readable, and reobserving known IDs is allowed.
        self.cli("checkpoint", {**payload, "seen_ids": incoming[:-1]})
        self.assertEqual(self.cli("status")["scopes"][0]["seen_count"], 100_000)
        duplicate = self.cli("checkpoint", {"run_id": second["run_id"],
                                            "seen_ids": ["first:0", "second:0"]})
        self.assertEqual(duplicate["new_count"], 0)

    def test_private_root_guard_lock_symlink_and_atomic_failure(self):
        with self.assertRaises(search.TrackerError):
            search.SearchStore(str(SCRIPT.parents[3]))
        self.cli("start", self.scope)
        path = self.workspace / "search_state.json"
        before = path.read_bytes()
        with search.SearchStore(str(self.workspace)) as store:
            self.cli("start", self.scope, succeeds=False)
            data = store.load()
            with mock.patch.object(search.os, "replace", side_effect=OSError("simulated disk failure")):
                with self.assertRaises(OSError):
                    store.save(data)
        self.assertEqual(before, path.read_bytes())
        self.assertFalse(list(self.workspace.glob(".tracker-*.tmp")))
        real = self.root / "real.json"
        real.write_bytes(before)
        path.unlink()
        try:
            path.symlink_to(real)
        except OSError:
            self.skipTest("Symlinks unavailable")
        self.cli("status", succeeds=False)

    def test_timezone_and_date_boundaries_and_missing_timezone_data_fail_explicitly(self):
        for zone, expected in (("Pacific/Kiritimati", "2026-10-13"), ("America/Los_Angeles", "2026-10-12")):
            scope = {**self.scope, "timezone": zone}
            run = self.start(scope=scope)
            self.finish(run)
            self.assertEqual(search.plan(self.data, scope)["requested_since"], expected)
        with mock.patch.object(search, "ZoneInfo", side_effect=search.ZoneInfoNotFoundError("missing")):
            with self.assertRaisesRegex(search.TrackerError, "tzdata"):
                search.plan(self.data, self.scope)

    def test_compact_cli_keeps_resume_hints_without_dumping_history(self):
        first = self.cli("start", self.scope)
        self.assertEqual(first["known_count"], 0)
        self.assertNotIn("known_ids", first)
        for index in range(5):
            run = first if index == 0 else self.cli("start", self.scope)
            self.cli("checkpoint", {"run_id": run["run_id"], "seen_ids": [f"job:{index}"],
                                    "pages_seen": index + 1, "resume_locator": {"page": index + 2}})
            finished = self.cli("finish", {"run_id": run["run_id"], "outcome": "partial",
                                          "stop_reason": "Budget reached"})
            self.assertEqual(finished["seen_count"], 1)
            self.assertNotIn("seen_ids", finished)
        compact = self.cli("plan", self.scope)
        self.assertEqual(compact["pending_run_count"], 5)
        self.assertEqual(compact["pending_runs_omitted"], 2)
        self.assertEqual(len(compact["pending_runs"]), 3)
        self.assertEqual(compact["pending_runs"][-1]["resume_locator"], {"page": 6})
        self.assertNotIn("seen_ids", compact["pending_runs"][-1])
        complete = self.cli("plan", self.scope, full=True)
        self.assertEqual(len(complete["pending_runs"]), 5)
        self.assertEqual(complete["pending_runs"][0]["seen_ids"], ["job:0"])
        state = self.cli("status")["scopes"][0]
        self.assertNotIn("runs", state)
        self.assertEqual(state["run_count"], 5)
        self.assertEqual(state["latest_run"]["resume_locator"], {"page": 6})
        self.assertEqual(len(self.cli("status", full=True)["scopes"][0]["runs"]), 5)

    def test_membership_queries_current_batch_only_and_never_write(self):
        run = self.cli("start", self.scope)
        self.cli("checkpoint", {"run_id": run["run_id"], "seen_ids": ["job:1", "job:2"]})
        path = self.workspace / "search_state.json"
        before = path.read_bytes()
        result = self.cli("known", {"scope_id": run["scope_id"],
                                    "posting_ids": ["job:1", "job:3", "job:1"]})
        self.assertEqual(result["known_ids"], ["job:1"])
        self.assertEqual(result["unknown_ids"], ["job:3"])
        self.assertEqual(result["known_count"], 1)
        self.assertIn("assessment", result["meaning"])
        for payload in ({"scope_id": "missing", "posting_ids": []},
                        {"scope_id": run["scope_id"], "posting_ids": ["x"] * 1001},
                        {"scope_id": run["scope_id"], "posting_ids": [""]}):
            self.cli("known", payload, succeeds=False)
        self.assertEqual(path.read_bytes(), before)

    def test_compact_output_scales_without_duplicating_seen_id_history(self):
        run = self.start()
        search.checkpoint(self.data, {"run_id": run["run_id"],
                                     "seen_ids": [f"posting:{index:06d}" for index in range(2000)]})
        with search.SearchStore(str(self.workspace)) as store:
            store.save(self.data)
        full = self.cli("status", full=True)
        small = self.cli("status")
        self.assertEqual(small["scopes"][0]["seen_count"], 2000)
        self.assertLess(len(json.dumps(small)), len(json.dumps(full)) / 10)


if __name__ == "__main__":
    unittest.main()
