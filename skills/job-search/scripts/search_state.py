#!/usr/bin/env python3
"""Offline search coverage checkpoints; Python 3.10+, no browser/network access."""
import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from track import Store, TrackerError, fields, identifier, read_json, text_field

VERSION = 1
MAX_STATE_BYTES = 10_000_000  # Match track.read_json's input-file limit.
MAX_SEEN_IDS = 100_000
OUTCOMES = {"running", "complete", "partial", "blocked", "failed"}
SCOPE_FIELDS = {"source", "query", "timezone", "filters", "profile_revision", "lookback_days"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            raise ValueError()
        return parsed.astimezone(timezone.utc)
    except (ValueError, TypeError) as exc:
        raise TrackerError("Invalid stored timestamp; original file was not changed") from exc


def zone(name):
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, TypeError) as exc:
        raise TrackerError("timezone must be an installed IANA zone, e.g. America/Toronto. "
                           "If valid zones are unavailable (often on Windows), install Python's "
                           "tzdata package, then retry; UTC is not silently substituted.") from exc


def safe_json(value):
    """Validate passive JSON data, never evaluated or interpreted as commands."""
    try:
        encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)
        if len(encoded) > 100_000:
            raise ValueError("JSON value exceeds 100 KB")
        return json.loads(encoded)
    except (ValueError, TypeError, RecursionError) as exc:
        raise TrackerError(f"Expected finite, serializable JSON data: {exc}") from exc


def normalize_scope(obj):
    fields(obj, SCOPE_FIELDS, ("source", "query", "timezone"))
    clean = {key: text_field(obj, key, True) for key in ("source", "query", "timezone")}
    clean["source"] = " ".join(clean["source"].casefold().split())
    zone(clean["timezone"])
    if not isinstance(obj.get("filters", {}), dict):
        raise TrackerError("filters must be a JSON object")
    clean["filters"] = safe_json(obj.get("filters", {}))
    if "profile_revision" in obj:
        clean["profile_revision"] = text_field(obj, "profile_revision", True)
    lookback = obj.get("lookback_days", 1)
    if type(lookback) is not int or not 0 <= lookback <= 365:
        raise TrackerError("lookback_days must be an integer from 0 to 365")
    digest = hashlib.sha256(json.dumps(clean, sort_keys=True, ensure_ascii=False,
                                      separators=(",", ":")).encode()).hexdigest()[:24]
    return "scope_" + digest, clean, lookback


def ids(value):
    if (not isinstance(value, list) or len(value) > MAX_SEEN_IDS or
            any(not isinstance(x, str) or not x.strip() or len(x) > 2048 for x in value)):
        raise TrackerError("seen_ids must be a list of nonempty posting IDs or canonical URLs")
    return list(dict.fromkeys(value))


class SearchStore(Store):
    def __init__(self, workspace):
        super().__init__(workspace)  # Reuse private-root and distribution safeguards.
        self.path = self.root / "search_state.json"
        self.lock = self.root / ".search_state.lock"

    def __enter__(self):
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.path.is_symlink():
            raise TrackerError("search_state.json may not be a symlink")
        try:
            self.fd = os.open(self.lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise TrackerError("Search state is locked. Retry when the other command finishes. "
                               "Remove a stale .search_state.lock only after verifying no command is running.") from exc
        os.write(self.fd, f"pid={os.getpid()}\nstarted={now()}\n".encode())
        return self

    def save(self, data):
        # A checkpoint repeats IDs in the scope and run. A valid input file can
        # therefore produce a state file too large for read_json to reopen.
        payload = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if len(payload.encode("utf-8")) > MAX_STATE_BYTES:
            raise TrackerError("Search state would exceed the 10 MB readable limit; the previous "
                               "file was not changed. Use shorter stable posting IDs, or archive "
                               "this private search workspace and start a separate one. No records "
                               "were deleted automatically.")
        super().save(data)

    def load(self, initialize=True):
        if not self.path.exists():
            if self.path.is_symlink():
                raise TrackerError("search_state.json may not be a symlink")
            return {"version": VERSION, "scopes": {}}
        data = read_json(self.path)
        fields(data, {"version", "scopes"}, ("version", "scopes"))
        if type(data["version"]) is not int or data["version"] != VERSION or not isinstance(data["scopes"], dict):
            raise TrackerError("Unsupported search-state schema")
        all_runs = set()
        for scope_id, item in data["scopes"].items():
            fields(item, {"scope", "seen_ids", "runs", "last_completed_started_at"},
                   ("scope", "seen_ids", "runs", "last_completed_started_at"))
            expected_id, clean_scope, _ = normalize_scope(item["scope"])
            if (expected_id != scope_id or clean_scope != item["scope"] or
                    ids(item["seen_ids"]) != item["seen_ids"]):
                raise TrackerError("Invalid stored scope or duplicate posting IDs")
            if not isinstance(item["runs"], list):
                raise TrackerError("Invalid stored runs")
            complete_anchors = []
            for run in item["runs"]:
                validate_run(run)
                if run["run_id"] in all_runs:
                    raise TrackerError("Duplicate stored run ID")
                all_runs.add(run["run_id"])
                if run["outcome"] == "complete":
                    complete_anchors.append(timestamp(run["coverage_started_at"]))
                if not set(run["seen_ids"]).issubset(item["seen_ids"]):
                    raise TrackerError("Run posting IDs are missing from its scope")
            expected = max(complete_anchors) if complete_anchors else None
            recorded = item["last_completed_started_at"]
            if (timestamp(recorded) if recorded else None) != expected:
                raise TrackerError("Invalid coverage watermark; original file was not changed")
        return data


def validate_run(run):
    required = {"run_id", "started_at", "coverage_started_at", "mode", "requested_since",
                "fetch_since", "lookback_days", "outcome", "seen_ids", "pages_seen",
                "resume_locator", "notes", "resume_from"}
    fields(run, required | {"finished_at", "stop_reason", "coverage_evidence"}, required)
    for key in ("run_id", "started_at", "coverage_started_at"):
        text_field(run, key, True)
    if timestamp(run["coverage_started_at"]) > timestamp(run["started_at"]):
        raise TrackerError("Coverage start cannot follow attempt start")
    if (not isinstance(run["outcome"], str) or run["outcome"] not in OUTCOMES or
            not isinstance(run["mode"], str) or run["mode"] not in {"baseline", "incremental"}):
        raise TrackerError("Invalid run outcome or mode")
    if type(run["pages_seen"]) is not int or run["pages_seen"] < 0:
        raise TrackerError("Invalid pages_seen")
    if ids(run["seen_ids"]) != run["seen_ids"] or ids(run["resume_from"]) != run["resume_from"]:
        raise TrackerError("Duplicate stored posting IDs or resume references")
    text_field(run, "notes")
    if type(run["lookback_days"]) is not int or not 0 <= run["lookback_days"] <= 365:
        raise TrackerError("Invalid stored lookback_days")
    try:
        if run["mode"] == "baseline":
            if run["requested_since"] is not None or run["fetch_since"] is not None:
                raise ValueError()
        else:
            requested = date.fromisoformat(run["requested_since"])
            fetched = date.fromisoformat(run["fetch_since"])
            if (requested.isoformat() != run["requested_since"] or fetched.isoformat() != run["fetch_since"]
                    or requested - timedelta(days=run["lookback_days"]) != fetched):
                raise ValueError()
    except (ValueError, TypeError) as exc:
        raise TrackerError("Invalid stored inclusive date window") from exc
    if not isinstance(run["resume_locator"], dict):
        raise TrackerError("resume_locator must be a passive JSON object")
    safe_json(run["resume_locator"])
    if run["outcome"] != "running":
        if timestamp(run.get("finished_at")) < timestamp(run["started_at"]):
            raise TrackerError("Finish timestamp precedes attempt start")
        text_field(run, "stop_reason", True)
        text_field(run, "coverage_evidence", run["outcome"] == "complete")
    elif any(key in run for key in ("finished_at", "stop_reason", "coverage_evidence")):
        raise TrackerError("Running attempt has finished-run fields")


def pending(item):
    completed = [r["started_at"] for r in item["runs"] if r["outcome"] == "complete"]
    latest = max(completed, key=timestamp) if completed else None
    return [r for r in item["runs"] if r["outcome"] != "complete"
            and (latest is None or timestamp(r["started_at"]) > timestamp(latest))]


def plan(data, obj):
    scope_id, scope, lookback = normalize_scope(obj)
    item = data["scopes"].get(scope_id, {"scope": scope, "seen_ids": [], "runs": [],
                                       "last_completed_started_at": None})
    watermark = item["last_completed_started_at"]
    requested = timestamp(watermark).astimezone(zone(scope["timezone"])).date() if watermark else None
    unresolved = pending(item)
    return {"scope_id": scope_id, "scope": scope,
            "mode": "incremental" if watermark else "baseline",
            "last_completed_started_at": watermark,
            "requested_since": requested.isoformat() if requested else None,
            "fetch_since": (requested - timedelta(days=lookback)).isoformat() if requested else None,
            "lookback_days": lookback, "inclusive": True, "seen_count": len(item["seen_ids"]),
            "pending_coverage_started_at": min((r["coverage_started_at"] for r in unresolved),
                                               key=timestamp, default=None),
            "pending_runs": unresolved}


def start(data, obj):
    result = plan(data, obj)
    item = data["scopes"].setdefault(result["scope_id"], {"scope": result["scope"], "seen_ids": [],
                                  "runs": [], "last_completed_started_at": None})
    started = now()
    unfinished = result["pending_runs"]
    # Resuming old coverage must not skip jobs added while an attempt was interrupted.
    anchor = min([started] + [r["coverage_started_at"] for r in unfinished], key=timestamp)
    run = {"run_id": identifier("search"), "started_at": started, "coverage_started_at": anchor,
           "mode": result["mode"], "requested_since": result["requested_since"],
           "fetch_since": result["fetch_since"], "lookback_days": result["lookback_days"],
           "outcome": "running", "seen_ids": [], "pages_seen": 0, "resume_locator": {},
           "notes": "", "resume_from": [r["run_id"] for r in unfinished]}
    item["runs"].append(run)
    return {"scope_id": result["scope_id"], **run, "pending_runs": unfinished,
            "known_ids": item["seen_ids"].copy()}


def find_run(data, obj):
    run_id = text_field(obj, "run_id", True)
    for item in data["scopes"].values():
        for run in item["runs"]:
            if run["run_id"] == run_id:
                if run["outcome"] != "running":
                    raise TrackerError("Finished runs are immutable; start a new attempt to resume")
                return item, run
    raise TrackerError("Unknown run_id")


def checkpoint(data, obj):
    fields(obj, {"run_id", "seen_ids", "pages_seen", "resume_locator", "notes"}, ("run_id", "seen_ids"))
    incoming = ids(obj["seen_ids"])
    item, run = find_run(data, obj)
    pages = obj.get("pages_seen", run["pages_seen"])
    if type(pages) is not int or pages < run["pages_seen"]:
        raise TrackerError("pages_seen must be a nondecreasing cumulative integer for this attempt")
    locator = obj.get("resume_locator", run["resume_locator"])
    if not isinstance(locator, dict):
        raise TrackerError("resume_locator must be a passive JSON object")
    locator = safe_json(locator)
    notes = text_field(obj, "notes") if "notes" in obj else run["notes"]
    known = set(item["seen_ids"])
    new_ids = [value for value in incoming if value not in known]
    if len(known) + len(new_ids) > MAX_SEEN_IDS:
        raise TrackerError("Search scope would exceed the 100,000 posting-ID readable limit; "
                           "the previous state was not changed. Archive this private search "
                           "workspace and start a separate one. No records were deleted automatically.")
    item["seen_ids"].extend(new_ids)
    run["seen_ids"] = list(dict.fromkeys(run["seen_ids"] + incoming))
    run.update(pages_seen=pages, resume_locator=locator, notes=notes)
    return {"run_id": run["run_id"], "new_ids": new_ids, "new_count": len(new_ids),
            "seen_count": len(item["seen_ids"]), "pages_seen": pages,
            "meaning": "Newly observed IDs, not proof of newly published jobs"}


def finish(data, obj):
    fields(obj, {"run_id", "outcome", "stop_reason", "coverage_evidence"},
           ("run_id", "outcome", "stop_reason"))
    outcome = text_field(obj, "outcome", True)
    if outcome not in OUTCOMES - {"running"}:
        raise TrackerError("outcome must be complete, partial, blocked or failed")
    reason = text_field(obj, "stop_reason", True)
    evidence = text_field(obj, "coverage_evidence", outcome == "complete") or ""
    item, run = find_run(data, obj)
    run.update(outcome=outcome, stop_reason=reason, coverage_evidence=evidence, finished_at=now())
    previous = item["last_completed_started_at"]
    if outcome == "complete" and (not previous or timestamp(run["coverage_started_at"]) > timestamp(previous)):
        item["last_completed_started_at"] = run["coverage_started_at"]
    return {**run, "last_completed_started_at": item["last_completed_started_at"],
            "watermark_advanced": previous != item["last_completed_started_at"]}


def status(data):
    return {"version": VERSION, "scopes": [{"scope_id": key, "scope": value["scope"],
            "last_completed_started_at": value["last_completed_started_at"],
            "seen_count": len(value["seen_ids"]), "runs": value["runs"]}
            for key, value in data["scopes"].items()]}


def known(data, obj):
    """Query only the current card batch; never return an entire scope's ID history."""
    fields(obj, {"scope_id", "posting_ids"}, ("scope_id", "posting_ids"))
    scope_id = text_field(obj, "scope_id", True)
    if scope_id not in data["scopes"]:
        raise TrackerError("Unknown scope_id; start the intended scope first (plan is read-only)")
    requested = ids(obj["posting_ids"])
    if len(obj["posting_ids"]) > 1000:
        raise TrackerError("Query at most 1000 posting_ids in one batch")
    seen = set(data["scopes"][scope_id]["seen_ids"])
    matches = [item for item in requested if item in seen]
    missing = [item for item in requested if item not in seen]
    return {"scope_id": scope_id, "known_ids": matches, "unknown_ids": missing,
            "known_count": len(matches), "unknown_count": len(missing),
            "meaning": "Seen IDs may still need assessment or reporting; consult the vacancy ledger"}


def run_summary(run):
    return {key: value for key, value in run.items() if key not in {"seen_ids", "resume_from"}} | {
        "seen_count": len(run["seen_ids"]), "resume_from_count": len(run["resume_from"])}


def pending_summary(runs):
    # Only recent resume hints are normally needed. --full preserves all history.
    recent = sorted(runs, key=lambda run: timestamp(run["started_at"]))[-3:]
    return {"pending_runs": [run_summary(run) for run in recent],
            "pending_run_count": len(runs), "pending_runs_omitted": max(0, len(runs) - 3)}


def compact(command, result, data):
    """Presentation only: keep stored schema and imported helper API compatible."""
    if command == "status":
        scopes = []
        for item in result["scopes"]:
            runs = item["runs"]
            latest = max(runs, key=lambda run: timestamp(run["started_at"]), default=None)
            scopes.append({key: value for key, value in item.items() if key != "runs"} | {
                "run_count": len(runs), "latest_run": run_summary(latest) if latest else None,
                **pending_summary(pending(data["scopes"][item["scope_id"]]))})
        return {"version": result["version"], "scopes": scopes}
    output = dict(result)
    for key, count in (("seen_ids", "seen_count"), ("known_ids", "known_count"),
                       ("resume_from", "resume_from_count")):
        if key in output and command != "known":
            output[count] = len(output.pop(key))
    if "pending_runs" in output:
        output.update(pending_summary(output["pending_runs"]))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="Absolute private candidate directory")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "start", "checkpoint", "finish", "known", "status"):
        subparser = commands.add_parser(command)
        if command != "status":
            subparser.add_argument("--input", required=True, help="UTF-8 JSON file")
        subparser.add_argument("--full", action="store_true", help="Include complete stored IDs/history in output")
    args = parser.parse_args()
    try:
        store = SearchStore(args.workspace)
        obj = read_json(args.input) if hasattr(args, "input") else None
        if args.command in {"plan", "status", "known"}:
            data = store.load()  # Atomic snapshots; read-only calls create no files/directories.
            result = status(data) if args.command == "status" else {"plan": plan, "known": known}[args.command](data, obj)
        else:
            with store:
                data = store.load()
                result = {"start": start, "checkpoint": checkpoint, "finish": finish}[args.command](data, obj)
                store.save(data)
        if not args.full:
            result = compact(args.command, result, data)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    except (TrackerError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
