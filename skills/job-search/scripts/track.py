#!/usr/bin/env python3
"""Offline, private job-search records. Python 3.10+; standard library only."""
import argparse
import csv
from datetime import date, datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import uuid

VERSION = 1
MAX_JSON_BYTES = 10_000_000
COLLECTIONS = ("jobs", "applications", "events", "time_logs")
TERMINAL = {"accepted", "rejected", "withdrawn"}
STATES = {"submitted": "submitted", "interview_scheduled": "interviewing",
          "interview_completed": "interviewing", "offer_received": "offered",
          "accepted": "accepted", "rejected": "rejected", "withdrawn": "withdrawn"}
LEVEL = {"draft": 0, "submitted": 1, "interviewing": 2, "offered": 3,
         "accepted": 4, "rejected": 4, "withdrawn": 4}
EVENT_TYPES = set(STATES) | {"prepared", "followup_planned", "followup_sent", "note"}
TRACKING = {"fbclid", "gclid", "dclid", "msclkid", "mc_cid", "mc_eid"}


class TrackerError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def identifier(prefix):
    return prefix + "_" + uuid.uuid4().hex


def reject_constant(value):
    raise TrackerError("Non-finite JSON number is not allowed: " + value)


def read_json(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise TrackerError(f"Expected a regular, non-symlink JSON file: {path}")
    if path.stat().st_size > MAX_JSON_BYTES:
        raise TrackerError("JSON file exceeds the 10 MB limit")
    try:
        return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise TrackerError(f"Invalid UTF-8 JSON in {path}: {exc}") from exc


def fields(obj, allowed, required=()):
    if not isinstance(obj, dict):
        raise TrackerError("Input must be one JSON object")
    unknown = set(obj) - set(allowed)
    missing = set(required) - set(obj)
    if unknown or missing:
        raise TrackerError(f"Unexpected fields: {sorted(unknown)}; missing fields: {sorted(missing)}")


def text_field(obj, key, required=False):
    if key not in obj:
        if required:
            raise TrackerError(f"{key} is required")
        return None
    value = obj[key]
    if not isinstance(value, str) or (required and not value.strip()):
        raise TrackerError(f"{key} must be {'nonempty ' if required else ''}text")
    return value.strip()


def day(obj, key, required=False):
    value = text_field(obj, key, required)
    if value is not None:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError()
            date.fromisoformat(value)
        except ValueError as exc:
            raise TrackerError(f"{key} must be a valid YYYY-MM-DD date") from exc
    return value


def choice(obj, key, choices, default):
    value = obj.get(key, default)
    if not isinstance(value, str) or value not in choices:
        raise TrackerError(f"{key} must be one of: {', '.join(sorted(choices))}")
    return value


def confirmation(obj, flag="confirmed", evidence="evidence"):
    if obj.get(flag) is not True or not text_field(obj, evidence, True):
        raise TrackerError(f"This action requires {flag}: true and nonempty {evidence}")


def canonical_url(value):
    try:
        parts = urlsplit(value)
        if parts.scheme.lower() not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
            raise ValueError()
        _ = parts.port  # Validate malformed ports without discarding valid job identifiers.
        query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                 if not k.lower().startswith("utm_") and k.lower() not in TRACKING]
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path,
                           urlencode(query), parts.fragment))
    except ValueError as exc:
        raise TrackerError("posting_url must be an HTTP(S) URL without credentials") from exc


class Store:
    """One lock covers reading, validation and atomic replacement; stale locks fail closed."""
    def __init__(self, workspace):
        supplied = Path(workspace).expanduser()
        if not supplied.is_absolute():
            raise TrackerError("--workspace must be an absolute private directory path")
        self.root = supplied.resolve()
        if supplied != self.root:
            raise TrackerError("Workspace may not contain symlinks or '..' components")
        script = Path(__file__).resolve()
        skill = script.parents[1]
        if self.root == skill or skill in self.root.parents:
            raise TrackerError("Use a private workspace outside the installed skill folder")
        # A distribution checkout is public/shareable, including its root and siblings
        # of skills/. An installed standalone skill has no such distribution marker.
        for ancestor in script.parents:
            if ((ancestor / "distribution.json").is_file()
                    and script == ancestor / "skills" / "job-search" / "scripts" / "track.py"
                    and (self.root == ancestor or ancestor in self.root.parents)):
                raise TrackerError("Use a private workspace outside the public distribution folder")
        self.path = self.root / "tracker.json"
        self.lock = self.root / ".tracker.lock"
        self.temp = None
        self.fd = None

    def __enter__(self):
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.path.is_symlink():
            raise TrackerError("tracker.json may not be a symlink")
        try:
            self.fd = os.open(self.lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise TrackerError("Workspace is locked. Retry after the other command finishes. "
                               "Remove a stale .tracker.lock only after verifying no command is running.") from exc
        os.write(self.fd, f"pid={os.getpid()}\nstarted={now()}\n".encode())
        return self

    def __exit__(self, *_):
        if self.fd is not None:
            os.close(self.fd)
            self.lock.unlink()
        if self.temp and self.temp.exists():
            self.temp.unlink()

    def load(self, initialize=False):
        if not self.path.exists():
            if initialize:
                return {"version": VERSION, **{key: [] for key in COLLECTIONS}}
            raise TrackerError("Workspace is not initialized; run init first")
        data = read_json(self.path)
        if not isinstance(data, dict) or data.get("version") != VERSION:
            raise TrackerError("Unsupported or missing tracker schema version")
        for key in COLLECTIONS:
            if not isinstance(data.get(key), list) or not all(isinstance(x, dict) for x in data[key]):
                raise TrackerError(f"Invalid tracker collection: {key}; original file was not changed")
        for key, id_key in (("jobs", "job_id"), ("applications", "application_id"),
                            ("events", "event_id"), ("time_logs", "time_id")):
            ids = [x.get(id_key) for x in data[key]]
            if any(not isinstance(x, str) or not x for x in ids) or len(set(ids)) != len(ids):
                raise TrackerError(f"Invalid or duplicate IDs in {key}")
        return data

    def save(self, data):
        payload = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if len(payload.encode("utf-8")) > MAX_JSON_BYTES:
            raise TrackerError("Tracker would exceed the 10 MB readable limit; the previous file "
                               "was not changed. Use shorter notes, or archive this private "
                               "workspace and start a separate one. No records were deleted automatically.")
        fd, name = tempfile.mkstemp(prefix=".tracker-", suffix=".tmp", dir=self.root)
        self.temp = Path(name)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(self.temp, self.path)
        self.temp = None


def upsert_job(data, obj):
    allowed = {"employer", "title", "posting_url", "requisition_id", "status", "retrieval_status",
               "closure_confirmed", "closure_evidence", "reopen_confirmed", "reopen_evidence",
               "checked_on", "deadline", "location", "work_arrangement", "salary", "notes"}
    fields(obj, allowed, ("employer", "title", "posting_url", "checked_on"))
    clean = {key: text_field(obj, key, key in {"employer", "title", "posting_url", "requisition_id"})
             for key in obj if key not in {"closure_confirmed", "reopen_confirmed"}}
    for key in ("closure_confirmed", "reopen_confirmed"):
        if key in obj and not isinstance(obj[key], bool):
            raise TrackerError(f"{key} must be a boolean")
    clean["checked_on"] = day(obj, "checked_on", True)
    if "deadline" in obj:
        clean["deadline"] = day(obj, "deadline")
    clean["canonical_url"] = canonical_url(clean["posting_url"])
    clean["retrieval_status"] = choice(obj, "retrieval_status", {"verified", "blocked", "unavailable"}, "verified")
    status = choice(obj, "status", {"open", "closed", "unverified"}, "unverified")
    company = " ".join(clean["employer"].casefold().split())
    req = clean.get("requisition_id")
    same_company = [j for j in data["jobs"] if " ".join(j["employer"].casefold().split()) == company]
    matches = [j for j in same_company if j.get("requisition_id") == req] if req else []
    if not matches:
        matches = [j for j in same_company if j["canonical_url"] == clean["canonical_url"]
                   and (not req or not j.get("requisition_id"))]
    if len(matches) > 1:
        raise TrackerError("Ambiguous posting URL; provide its specific requisition_id")
    existing = matches[0] if matches else None
    if status == "closed":
        confirmation(obj, "closure_confirmed", "closure_evidence")
    if status == "open" and clean["retrieval_status"] != "verified":
        raise TrackerError("An open status requires a verified retrieval")
    if existing and existing["status"] == "closed" and status != "closed":
        if status == "open":
            confirmation(obj, "reopen_confirmed", "reopen_evidence")
        else:
            status = "closed"
    if existing and existing["status"] == "open" and status == "unverified":
        status = "open"  # Retrieval failure records uncertainty, not evidence of closure.
    clean["status"] = status
    if existing:
        entry = existing
    else:
        entry = {"job_id": identifier("job"), "history": []}
        data["jobs"].append(entry)
    changes = {k: {"before": entry.get(k), "after": v} for k, v in clean.items() if entry.get(k) != v}
    entry.update(clean)
    entry["history"].append({"recorded_at": now(), "changes": changes})
    return entry


def by_id(rows, key, value):
    for row in rows:
        if row.get(key) == value:
            return row
    raise TrackerError(f"Unknown {key}: {value}")


def record_application(data, obj):
    fields(obj, {"job_id", "created_on", "resume_version", "notes"}, ("job_id", "created_on"))
    job_id = text_field(obj, "job_id", True)
    by_id(data["jobs"], "job_id", job_id)
    row = {"application_id": identifier("app"), "job_id": job_id,
           "created_on": day(obj, "created_on", True), "status": "draft", "recorded_at": now()}
    for key in ("resume_version", "notes"):
        if key in obj:
            row[key] = text_field(obj, key)
    data["applications"].append(row)
    return row


def record_event(data, obj):
    fields(obj, {"application_id", "type", "occurred_on", "confirmed", "evidence", "notes"},
           ("application_id", "type", "occurred_on"))
    app = by_id(data["applications"], "application_id", text_field(obj, "application_id", True))
    kind = choice(obj, "type", EVENT_TYPES, None)
    occurred = day(obj, "occurred_on", True)
    confirmed = obj.get("confirmed", False)
    if not isinstance(confirmed, bool):
        raise TrackerError("confirmed must be a boolean")
    evidence = text_field(obj, "evidence")
    notes = text_field(obj, "notes")
    if kind in set(STATES) | {"followup_sent"}:
        confirmation(obj)
        if occurred > date.today().isoformat():
            raise TrackerError("A confirmed event cannot have a future occurred_on date")
    if kind == "followup_planned" and confirmed:
        raise TrackerError("Planned follow-ups cannot be marked confirmed; log followup_sent after sending")
    next_state = STATES.get(kind, app["status"])
    if next_state != app["status"] and (app["status"] in TERMINAL or LEVEL[next_state] < LEVEL[app["status"]]):
        raise TrackerError("Event would regress or replace a terminal application state; use a new application attempt")
    if kind == "accepted" and app["status"] != "offered":
        raise TrackerError("Record offer_received before accepting an offer")
    row = {"event_id": identifier("evt"), "application_id": app["application_id"], "type": kind,
           "occurred_on": occurred, "confirmed": confirmed, "evidence": evidence,
           "notes": notes, "recorded_at": now()}
    data["events"].append(row)
    app["status"] = next_state
    return row


def log_time(data, obj):
    fields(obj, {"date", "human_minutes", "agent_minutes", "category", "basis", "notes"},
           ("date", "human_minutes", "category"))
    row = {"time_id": identifier("time"), "date": day(obj, "date", True), "recorded_at": now()}
    for key in ("human_minutes", "agent_minutes"):
        value = obj.get(key, 0)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise TrackerError(f"{key} must be a nonnegative integer; zero is allowed")
        row[key] = value
    row["category"] = choice(obj, "category", {"setup", "search", "application", "networking", "interview", "other"}, None)
    row["basis"] = choice(obj, "basis", {"reported", "measured", "estimated"}, "reported")
    row["notes"] = text_field(obj, "notes")
    data["time_logs"].append(row)
    return row


def summary(data, budget):
    if budget is not None and (not math.isfinite(budget) or budget < 0):
        raise TrackerError("--budget-hours must be finite and nonnegative")
    human = sum(t["human_minutes"] for t in data["time_logs"])
    agent = sum(t["agent_minutes"] for t in data["time_logs"])
    result = {"jobs": len(data["jobs"]), "application_attempts": len(data["applications"]),
              "applications_by_status": {s: sum(a["status"] == s for a in data["applications"]) for s in LEVEL},
              "human_minutes": human, "agent_minutes": agent,
              "time_by_basis": {b: sum(t["human_minutes"] for t in data["time_logs"] if t["basis"] == b)
                                for b in ("reported", "measured", "estimated")}}
    if budget is not None:
        result.update(budget_minutes=budget * 60, remaining_human_minutes=budget * 60 - human,
                      over_budget_minutes=max(0, human - budget * 60))
    return result


def csv_safe(value):
    value = "" if value is None else str(value)
    probe = value
    while probe and (probe[0].isspace() or unicodedata.category(probe[0]) in {"Cc", "Cf"}):
        probe = probe[1:]
    return "'" + value if probe.startswith(("=", "+", "-", "@")) else value


def export_csv(data, destination, store):
    destination = Path(destination).expanduser().absolute()
    if destination.is_symlink() or destination.resolve() in {store.path, store.lock}:
        raise TrackerError("Export must be a separate, non-symlink file")
    if destination.exists():
        raise TrackerError("Export destination already exists; choose a new filename")
    headers = ("job_id", "employer", "title", "requisition_id", "posting_url", "status", "retrieval_status",
               "checked_on", "location", "work_arrangement", "salary", "notes")
    # Exclusive creation avoids overwriting another process's export or the tracker.
    with destination.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream, quoting=csv.QUOTE_ALL)
        writer.writerow(headers)
        for job in data["jobs"]:
            writer.writerow([csv_safe(job.get(key)) for key in headers])
    return {"output": str(destination), "rows": len(data["jobs"])}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="Absolute private directory outside the skill")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "list"):
        sub.add_parser(name)
    for name in ("upsert-job", "record-application", "record-event", "log-time"):
        sub.add_parser(name).add_argument("--input", required=True, help="One UTF-8 JSON object")
    sub.add_parser("export").add_argument("--output", required=True)
    sub.add_parser("summary").add_argument("--budget-hours", type=float)
    args = parser.parse_args(argv)
    try:
        obj = read_json(args.input) if hasattr(args, "input") else None
        with Store(args.workspace) as store:
            data = store.load(initialize=args.command == "init")
            handlers = {"upsert-job": upsert_job, "record-application": record_application,
                        "record-event": record_event, "log-time": log_time}
            if args.command in handlers:
                result = handlers[args.command](data, obj)
                store.save(data)
            elif args.command == "init":
                if not store.path.exists():
                    store.save(data)
                result = {"workspace": str(store.root), "schema_version": VERSION}
            elif args.command == "list":
                result = data["jobs"]
            elif args.command == "summary":
                result = summary(data, args.budget_hours)
            else:
                result = export_csv(data, args.output, store)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (TrackerError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
