#!/usr/bin/env python3
"""Offline shared vacancy ledger; Python 3.10+, standard library only."""
import argparse
import copy
from datetime import datetime, timezone
import json
import math
import os
import re
import sys

from track import Store, TrackerError, canonical_url, choice, fields, identifier, read_json, text_field

VERSION = 1
MAX_STATE_BYTES = 10_000_000
DETAILS = {"location", "work_arrangement", "salary", "deadline", "requirements", "description"}
ASSESSMENT = {"recommended", "possible", "rejected", "deferred"}
VERIFICATION = {"verified_open", "verified_closed", "unavailable", "blocked", "unverified"}
ASSESS_FIELDS = {"status", "reason", "skills_fit", "eligibility", "readiness", "profile_revision",
                 "assessed_at", "provenance"}
VERIFY_FIELDS = {"status", "checked_at", "source_url", "provenance"}
REPORT_FIELDS = {"profile_revision", "reported_at", "report_ref"}
MATERIAL = ("employer", "title", "summary", "details", "requisition_id", "official_url")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def stamp(value):
    try:
        if not isinstance(value, str):
            raise ValueError()
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError()
        return parsed.astimezone(timezone.utc)
    except (ValueError, TypeError, OverflowError) as exc:
        raise TrackerError("Timestamps must be ISO 8601 text with an explicit timezone") from exc


def timestamp(value):
    return stamp(value).isoformat(timespec="microseconds")


def text(obj, key, required=True):
    value = text_field(obj, key, required)
    if value is not None and (len(value) > 50_000 or any(ord(c) < 32 and c not in "\n\t\r" for c in value)):
        raise TrackerError(f"{key} exceeds the text limit or contains control characters")
    return value


def normalized(value):
    return " ".join(value.casefold().split())


def url(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 4096 or any(c.isspace() for c in value):
        raise TrackerError("URLs must be nonempty HTTP(S) text without whitespace")
    return canonical_url(value)


def revision(value):
    if type(value) is not int or value < 1:
        raise TrackerError("revision must be a positive integer")
    return value


def aliases(value):
    if not isinstance(value, list) or len(value) > 1000:
        raise TrackerError("aliases must be a list of at most 1000 explicit source IDs")
    clean = []
    for item in value:
        fields(item, {"source", "posting_id"}, {"source", "posting_id"})
        alias = {"source": normalized(text(item, "source")), "posting_id": text(item, "posting_id")}
        if max(map(len, alias.values())) > 2048:
            raise TrackerError("source and posting_id must be at most 2048 characters")
        if alias not in clean:
            clean.append(alias)
    return clean


def details(value):
    fields(value, DETAILS)
    return {key: text(value, key, False) for key in value}


def clean_assessment(obj):
    fields(obj, ASSESS_FIELDS, ASSESS_FIELDS)
    result = {key: text(obj, key) for key in ASSESS_FIELDS}
    result["status"] = choice(obj, "status", ASSESSMENT, None)
    result["skills_fit"] = choice(obj, "skills_fit", {"strong", "partial", "weak", "unknown"}, None)
    result["eligibility"] = choice(obj, "eligibility", {"eligible", "ineligible", "unknown"}, None)
    result["readiness"] = choice(obj, "readiness", {"ready", "needs_work", "blocked", "unknown"}, None)
    result["assessed_at"] = timestamp(obj["assessed_at"])
    return result


def clean_verification(obj):
    fields(obj, VERIFY_FIELDS, VERIFY_FIELDS)
    return {"status": choice(obj, "status", VERIFICATION, None),
            "checked_at": timestamp(obj["checked_at"]), "source_url": url(obj["source_url"]),
            "provenance": text(obj, "provenance")}


def clean_report(obj):
    fields(obj, REPORT_FIELDS, REPORT_FIELDS)
    return {"profile_revision": text(obj, "profile_revision"), "reported_at": timestamp(obj["reported_at"]),
            "report_ref": text(obj, "report_ref")}


def identity_keys(row):
    keys = {("alias", a["source"], a["posting_id"]) for a in row["aliases"]}
    if row["requisition_id"]:
        keys.add(("requisition", normalized(row["employer"]), row["requisition_id"]))
    if row["official_url"]:
        keys.add(("url", row["official_url"]))
    return keys


def state(row, profile_revision=None):
    assessment = row["assessment"]
    current = bool(assessment and assessment["revision"] == row["revision"] and
                   (profile_revision is None or assessment["profile_revision"] == profile_revision))
    report = row["reporting"]
    reported = bool(current and report and report["revision"] == row["revision"] and
                    report["profile_revision"] == assessment["profile_revision"])
    return {"assessment_status": assessment["status"] if current else "pending",
            "assessment_current": current, "reporting_status": "reported" if reported else "unreported"}


def validate(data):
    fields(data, {"version", "vacancies"}, {"version", "vacancies"})
    if type(data["version"]) is not int or data["version"] != VERSION or not isinstance(data["vacancies"], dict):
        raise TrackerError("Unsupported vacancy-ledger schema")
    used = set()
    required = {"vacancy_id", "revision", *MATERIAL, "aliases", "first_seen_at", "last_seen_at",
                "discovery_provenance", "assessment", "verification", "reporting"}
    for vacancy_id, row in data["vacancies"].items():
        fields(row, required, required)
        if not re.fullmatch(r"vacancy_[0-9a-f]{32}", vacancy_id) or row["vacancy_id"] != vacancy_id:
            raise TrackerError("Invalid stored vacancy ID")
        revision(row["revision"])
        for key in ("employer", "title", "summary", "discovery_provenance"):
            if text(row, key) != row[key]:
                raise TrackerError("Invalid stored text")
        if details(row["details"]) != row["details"] or aliases(row["aliases"]) != row["aliases"]:
            raise TrackerError("Invalid stored details or aliases")
        if row["requisition_id"] is not None and text(row, "requisition_id") != row["requisition_id"]:
            raise TrackerError("Invalid stored requisition_id")
        if row["official_url"] is not None and url(row["official_url"]) != row["official_url"]:
            raise TrackerError("Invalid stored official_url")
        keys = identity_keys(row)
        if not keys or used.intersection(keys):
            raise TrackerError("Missing or duplicate vacancy identity")
        used.update(keys)
        for key in ("first_seen_at", "last_seen_at"):
            if timestamp(row[key]) != row[key]:
                raise TrackerError("Invalid stored discovery timestamp")
        if stamp(row["first_seen_at"]) > stamp(row["last_seen_at"]):
            raise TrackerError("first_seen_at follows last_seen_at")
        for key, cleaner in (("assessment", clean_assessment), ("verification", clean_verification),
                             ("reporting", clean_report)):
            item = row[key]
            if item is not None:
                if not isinstance(item, dict) or "revision" not in item:
                    raise TrackerError(f"Invalid stored {key}")
                if revision(item["revision"]) > row["revision"]:
                    raise TrackerError(f"Stored {key} refers to a future revision")
                clean = cleaner({k: v for k, v in item.items() if k != "revision"})
                if {**clean, "revision": item["revision"]} != item:
                    raise TrackerError(f"Invalid stored {key}")
        if row["reporting"]:
            report, assessment = row["reporting"], row["assessment"]
            if (not assessment or report["revision"] != assessment["revision"] or
                    report["profile_revision"] != assessment["profile_revision"] or
                    stamp(report["reported_at"]) < stamp(assessment["assessed_at"])):
                raise TrackerError("Stored report has no matching assessment")


class VacancyStore(Store):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.path = self.root / "vacancies.json"
        self.lock = self.root / ".vacancies.lock"

    def __enter__(self):
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.path.is_symlink():
            raise TrackerError("vacancies.json may not be a symlink")
        try:
            self.fd = os.open(self.lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise TrackerError("Vacancy ledger is locked. Retry after the other command finishes. "
                               "Remove a stale .vacancies.lock only after verifying no command is running.") from exc
        try:
            os.write(self.fd, f"pid={os.getpid()}\nstarted={now()}\n".encode())
        except OSError:
            self.__exit__()
            raise
        return self

    def __exit__(self, *args):
        try:
            super().__exit__(*args)
        finally:
            self.fd = None

    def load(self, initialize=True):
        if not self.path.exists() and not self.path.is_symlink():
            return {"version": VERSION, "vacancies": {}}
        data = read_json(self.path)
        validate(data)
        return data

    def save(self, data):
        if self.fd is None:
            raise TrackerError("Writes require the vacancy ledger lock")
        validate(data)
        payload = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if len(payload.encode("utf-8")) > MAX_STATE_BYTES:
            raise TrackerError("Vacancy ledger would exceed the 10 MB readable limit; original file unchanged. "
                               "Archive the private workspace and start a separate one; no records were removed.")
        super().save(data)


def upsert(data, obj):
    required = {"employer", "title", "summary", "discovered_at", "provenance"}
    fields(obj, required | {"aliases", "requisition_id", "official_url", "details"}, required)
    incoming = {key: text(obj, key) for key in ("employer", "title", "summary")}
    incoming.update(aliases=aliases(obj.get("aliases", [])),
                    requisition_id=text(obj, "requisition_id") if "requisition_id" in obj else None,
                    official_url=url(obj["official_url"]) if "official_url" in obj else None,
                    details=details(obj.get("details", {})))
    observed, provenance = timestamp(obj["discovered_at"]), text(obj, "provenance")
    keys = identity_keys(incoming)
    if not keys:
        raise TrackerError("Supply an explicit source alias, employer requisition, or official URL")
    matches = [r for r in data["vacancies"].values() if identity_keys(r).intersection(keys)]
    if len(matches) > 1:
        raise TrackerError("Identities match multiple vacancies; automatic merging is prohibited")
    existing = matches[0] if matches else None
    if existing:
        if normalized(existing["employer"]) != normalized(incoming["employer"]):
            raise TrackerError("Identity conflict: employer differs; verify identity before updating")
        for key in ("requisition_id", "official_url"):
            if existing[key] and incoming[key] and existing[key] != incoming[key]:
                raise TrackerError(f"Identity conflict: {key} differs; no guessed aliases are accepted")
        row = copy.deepcopy(existing)
        # Missing detail/identity fields mean no update, never deletion.
        incoming["details"] = {**row["details"], **incoming["details"]}
        for key in ("requisition_id", "official_url"):
            incoming[key] = incoming[key] or row[key]
        incoming["employer"] = row["employer"]
        incoming["aliases"] = aliases(row["aliases"] + incoming["aliases"])
        changed = any(row[key] != incoming[key] for key in MATERIAL)
        if changed and observed < row["last_seen_at"]:
            raise TrackerError("Older discovery cannot overwrite newer material details")
        row.update(incoming)
        row["revision"] += int(changed)
        row["first_seen_at"] = min(row["first_seen_at"], observed)
        if observed >= row["last_seen_at"]:
            row.update(last_seen_at=observed, discovery_provenance=provenance)
    else:
        changed = False
        row = {**incoming, "vacancy_id": identifier("vacancy"), "revision": 1,
               "first_seen_at": observed, "last_seen_at": observed, "discovery_provenance": provenance,
               "assessment": None, "verification": None, "reporting": None}
    data["vacancies"][row["vacancy_id"]] = row
    return {**compact(row), "created": existing is None, "material_changed": changed}


def find(data, vacancy_id):
    if not isinstance(vacancy_id, str) or vacancy_id not in data["vacancies"]:
        raise TrackerError("Unknown vacancy_id")
    return data["vacancies"][vacancy_id]


def upsert_batch(data, obj):
    fields(obj, {"vacancies"}, {"vacancies"})
    items = obj["vacancies"]
    if not isinstance(items, list) or not 1 <= len(items) <= 100:
        raise TrackerError("vacancies must contain 1..100 discovery objects")
    staged = copy.deepcopy(data)
    results = [upsert(staged, item) for item in items]
    validate(staged)
    data["vacancies"] = staged["vacancies"]
    return {"received": len(results), "created": sum(r["created"] for r in results),
            "changed": sum(r["material_changed"] for r in results), "vacancies": results}


def update(data, obj, kind):
    expected_fields, cleaner = {"assessment": (ASSESS_FIELDS, clean_assessment),
                                "verification": (VERIFY_FIELDS, clean_verification),
                                "reporting": (REPORT_FIELDS, clean_report)}[kind]
    fields(obj, expected_fields | {"vacancy_id", "expected_revision"},
           expected_fields | {"vacancy_id", "expected_revision"})
    clean = cleaner({k: v for k, v in obj.items() if k not in {"vacancy_id", "expected_revision"}})
    row = find(data, text(obj, "vacancy_id"))
    if revision(obj["expected_revision"]) != row["revision"]:
        raise TrackerError("Vacancy changed: expected_revision is stale; reread and reassess before writing")
    time_key = {"assessment": "assessed_at", "verification": "checked_at", "reporting": "reported_at"}[kind]
    if row[kind] and stamp(clean[time_key]) < stamp(row[kind][time_key]):
        raise TrackerError(f"Older {kind} cannot overwrite newer evidence")
    if kind == "reporting":
        if not state(row, clean["profile_revision"])["assessment_current"]:
            raise TrackerError("A current assessment for this profile is required before reporting")
        if stamp(clean["reported_at"]) < stamp(row["assessment"]["assessed_at"]):
            raise TrackerError("reported_at cannot precede assessed_at")
    clean["revision"] = row["revision"]
    if kind == "assessment" and row[kind] != clean:
        row["reporting"] = None
    row[kind] = clean
    return compact(row)


def compact(row, profile_revision=None):
    result = {key: row[key] for key in ("vacancy_id", "revision", "employer", "title", "last_seen_at")}
    result.update(state(row, profile_revision))
    if result["assessment_current"]:
        result.update({key: row["assessment"][key] for key in ("skills_fit", "eligibility", "readiness")})
    return result


def listing(data, *, pending=False, profile_revision=None, unreported=False, source=None,
            employer=None, query=None, limit=20, offset=0):
    if type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or offset < 0:
        raise TrackerError("limit must be 1..100 and offset must be nonnegative")
    rows = sorted(data["vacancies"].values(), key=lambda r: (r["last_seen_at"], r["vacancy_id"]), reverse=True)
    rows = [r for r in rows if (not source or any(a["source"] == normalized(source) for a in r["aliases"]))
            and (not employer or normalized(employer) == normalized(r["employer"]))
            and (not query or normalized(query) in normalized(" ".join(r[k] for k in ("employer", "title", "summary"))))
            and (not pending or not state(r, profile_revision)["assessment_current"])
            and (not unreported or state(r, profile_revision)["reporting_status"] == "unreported")]
    return {"total": len(rows), "offset": offset, "limit": limit,
            "vacancies": [compact(r, profile_revision) for r in rows[offset:offset + limit]]}


def verification(row, max_age_hours, at=None):
    if (isinstance(max_age_hours, bool) or not isinstance(max_age_hours, (float, int)) or
            not math.isfinite(max_age_hours) or max_age_hours < 0):
        raise TrackerError("max-age-hours must be finite and nonnegative")
    at = timestamp(at or now())
    cache = row["verification"]
    age = (stamp(at) - stamp(cache["checked_at"])).total_seconds() / 3600 if cache else None
    reusable = bool(cache and cache["revision"] == row["revision"] and 0 <= age <= max_age_hours
                    and cache["status"] in {"verified_open", "verified_closed"})
    return {"vacancy_id": row["vacancy_id"], "revision": row["revision"], "as_of": at,
            "max_age_hours": max_age_hours, "age_hours": age, "reusable": reusable, "verification": cache}


def summary(data, profile_revision=None):
    rows = list(data["vacancies"].values())
    return {"total": len(rows), "assessment_counts": {s: sum(state(r, profile_revision)["assessment_status"] == s
            for r in rows) for s in ("pending", *sorted(ASSESSMENT))},
            "unreported": sum(state(r, profile_revision)["reporting_status"] == "unreported" for r in rows)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="Absolute private directory outside the skill/distribution")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("upsert", "upsert-batch", "assess", "verify", "report"):
        commands.add_parser(command).add_argument("--input", required=True, help="One UTF-8 JSON object")
    for command in ("list", "pending"):
        sub = commands.add_parser(command)
        sub.add_argument("--limit", type=int, default=20)
        sub.add_argument("--offset", type=int, default=0)
        sub.add_argument("--profile-revision")
        sub.add_argument("--unreported", action="store_true")
        for key in ("source", "employer", "query"):
            sub.add_argument("--" + key)
    sub = commands.add_parser("get")
    sub.add_argument("--id", required=True)
    sub.add_argument("--profile-revision")
    commands.add_parser("summary").add_argument("--profile-revision")
    sub = commands.add_parser("verification")
    sub.add_argument("--id", required=True)
    sub.add_argument("--max-age-hours", type=float, required=True)
    sub.add_argument("--at")
    args = parser.parse_args(argv)
    try:
        store = VacancyStore(args.workspace)
        if args.command in {"upsert", "upsert-batch", "assess", "verify", "report"}:
            obj = read_json(args.input)
            with store:
                data = store.load()
                if args.command in {"upsert", "upsert-batch"}:
                    result = {"upsert": upsert, "upsert-batch": upsert_batch}[args.command](data, obj)
                else:
                    result = update(data, obj, {"assess": "assessment", "verify": "verification", "report": "reporting"}[args.command])
                store.save(data)
        else:
            data = store.load()  # Atomic snapshots; reads never create a workspace or lock.
            if args.command in {"list", "pending"}:
                result = listing(data, pending=args.command == "pending", **{k: getattr(args, k)
                    for k in ("limit", "offset", "profile_revision", "unreported", "source", "employer", "query")})
            elif args.command == "summary":
                result = summary(data, args.profile_revision)
            elif args.command == "get":
                row = find(data, args.id)
                result = {**row, **state(row, args.profile_revision)}
            else:
                result = verification(find(data, args.id), args.max_age_hours, args.at)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (TrackerError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
