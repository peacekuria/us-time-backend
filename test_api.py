# test_api.py
"""End-to-end checks against a running US Time API.

Start the server first:

    .venv/bin/python -m uvicorn app:app --port 8000

Then run:

    .venv/bin/python test_api.py

Set API_BASE_URL to point somewhere else. The script exits non-zero if any
check fails.
"""

import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

_failures = []
_checks = 0


def check(label, condition, detail=""):
    """Record the outcome of one assertion and print it."""
    global _checks
    _checks += 1

    if condition:
        print(f"PASS  {label}")
        return True

    _failures.append(label)
    print(f"FAIL  {label}  {detail}")
    return False


def request(method, path, payload=None):
    """Perform a JSON request and return (status_code, parsed_body)."""
    url = f"{BASE_URL}{path}"
    data = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8")
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = raw
        return error.code, parsed


def test_health():
    status, body = request("GET", "/health")
    check("GET /health returns 200", status == 200, f"got {status}")
    check("GET /health reports healthy", body == {"status": "healthy"}, body)


def test_questions():
    status, body = request("GET", "/api/questions")
    check("GET /api/questions returns 200", status == 200, f"got {status}")
    check("questions is a non-empty list", isinstance(body, list) and body, body)

    if isinstance(body, list) and body:
        first = body[0]
        check("question has id and text", "id" in first and "text" in first, first)


def test_disorders_list():
    status, body = request("GET", "/api/disorders")
    check("GET /api/disorders returns 200", status == 200, f"got {status}")
    check("disorders seeded", isinstance(body, list) and len(body) > 0, body)

    if not isinstance(body, list) or not body:
        return []

    names = [item["name"] for item in body]
    check("known disorder present", "Depression" in names, names)

    with_remedies = [item for item in body if item.get("remedies")]
    check(
        "disorders carry remedies",
        len(with_remedies) == len(body),
        f"{len(with_remedies)}/{len(body)} have remedies",
    )
    check(
        "remedies are strings",
        all(isinstance(r, str) for item in body for r in item["remedies"]),
        body[0].get("remedies"),
    )

    return body


def test_disorder_crud():
    payload = {
        "name": "Test Disorder",
        "description": "Created by test_api.py",
        "symptoms": "None, this is a fixture",
    }

    status, created = request("POST", "/api/disorders", payload)
    check("POST /api/disorders returns 201", status == 201, f"got {status}")

    if status != 201:
        return

    disorder_id = created["id"]
    check("created disorder echoes name", created["name"] == payload["name"], created)
    check("created disorder has remedies key", "remedies" in created, created)

    status, _ = request("POST", "/api/disorders", payload)
    check("duplicate name rejected with 409", status == 409, f"got {status}")

    status, fetched = request("GET", f"/api/disorders/{disorder_id}")
    check("GET single disorder returns 200", status == 200, f"got {status}")
    check("fetched name matches", fetched.get("name") == payload["name"], fetched)

    status, _ = request("GET", "/api/disorders/999999")
    check("unknown disorder returns 404", status == 404, f"got {status}")

    updated = dict(payload, symptoms="Updated symptoms")
    status, body = request("PATCH", f"/api/disorders/{disorder_id}", updated)
    check("PATCH returns 200", status == 200, f"got {status}")
    check("PATCH applied", body.get("symptoms") == "Updated symptoms", body)

    status, _ = request("PATCH", "/api/disorders/999999", updated)
    check("PATCH unknown returns 404", status == 404, f"got {status}")

    status, _ = request("DELETE", f"/api/disorders/{disorder_id}")
    check("DELETE returns 200", status == 200, f"got {status}")

    status, _ = request("GET", f"/api/disorders/{disorder_id}")
    check("deleted disorder is gone", status == 404, f"got {status}")


def test_disorder_search():
    status, body = request("GET", "/api/disorders/search/depression")
    check("search returns 200", status == 200, f"got {status}")
    check("search finds Depression", any(d["name"] == "Depression" for d in body), body)

    status, body = request("GET", "/api/disorders/search/DEPRESSION")
    check(
        "search is case-insensitive",
        any(d["name"] == "Depression" for d in body),
        body,
    )

    status, body = request("GET", "/api/disorders/search/zzzznotathing")
    check("search miss returns empty list", body == [], body)


def test_assessment_scoring():
    """Each severity band should be reachable from a matching answer set."""
    cases = [
        (["yes"] * 5, "high", 5),
        (["no"] * 5, "low", 0),
        (["unsure"] * 5, "medium", 2),
        (["yes", "yes", "yes", "no", "no"], "medium", 3),
    ]

    for answers, expected_severity, expected_score in cases:
        status, body = request("POST", "/api/assessments", {"answers": answers})
        label = f"answers {answers} -> {expected_severity}"

        if status != 200:
            check(label, False, f"got status {status}")
            continue

        check(
            label,
            body["severity"] == expected_severity
            and body["severity_score"] == expected_score,
            f"got {body['severity']} / {body['severity_score']}",
        )
        check(
            f"remedies returned for {expected_severity}",
            isinstance(body.get("remedies"), list) and body["remedies"],
            body.get("remedies"),
        )
        check(
            f"result text returned for {expected_severity}",
            isinstance(body.get("result"), str) and body["result"],
            body.get("result"),
        )


def test_assessment_persistence():
    answers = ["yes", "yes", "no", "no", "unsure"]
    status, created = request("POST", "/api/assessments", {"answers": answers})
    check("assessment submission returns 200", status == 200, f"got {status}")

    if status != 200:
        return

    session_id = created["session_id"]
    check("session id issued", bool(session_id), created)

    status, fetched = request("GET", f"/api/assessments/{session_id}")
    check("GET assessment by session returns 200", status == 200, f"got {status}")
    check(
        "stored assessment round-trips its score",
        fetched.get("severity_score") == created["severity_score"],
        fetched,
    )

    status, _ = request("GET", "/api/assessments/no-such-session")
    check("unknown session returns 404", status == 404, f"got {status}")


def test_assessment_resubmission():
    """Reusing a session id updates the row instead of failing on the unique index."""
    answers = ["yes", "yes", "yes", "yes", "yes"]
    status, created = request("POST", "/api/assessments", {"answers": answers})

    if status != 200:
        check("resubmission setup", False, f"got status {status}")
        return

    session_id = created["session_id"]

    status, second = request(
        "POST",
        "/api/assessments",
        {"answers": ["no", "no", "no", "no", "no"], "session_id": session_id},
    )
    check("resubmission accepted", status == 200, f"got {status}")
    check("resubmission rescored", second.get("severity") == "low", second)
    check("resubmission keeps session", second.get("session_id") == session_id, second)


def test_assessment_validation():
    status, _ = request("POST", "/api/assessments", {"answers": []})
    check("empty answers rejected with 422", status == 422, f"got {status}")

    status, _ = request("POST", "/api/assessments", {})
    check("missing answers rejected with 422", status == 422, f"got {status}")


def test_raw_assessment_crud():
    payload = {
        "session_id": "raw-crud-fixture",
        "answers": "yes,no,yes",
        "result": "medium",
        "severity_score": 2,
        "disorder_id": 1,
    }

    status, _ = request("POST", "/assessment", payload)
    check("POST /assessment returns 200", status == 200, f"got {status}")

    status, listing = request("GET", "/assessment")
    check("GET /assessment returns 200", status == 200, f"got {status}")

    match = None
    if isinstance(listing, list):
        match = next(
            (row for row in listing if row["session_id"] == payload["session_id"]),
            None,
        )

    check("raw assessment stored", match is not None, listing)

    if match is None:
        return

    assessment_id = match["id"]

    status, _ = request("GET", f"/assessment/{assessment_id}")
    check("GET /assessment/{id} returns 200", status == 200, f"got {status}")

    status, _ = request(
        "PATCH", f"/assessment/{assessment_id}", dict(payload, result="low")
    )
    check("PATCH /assessment/{id} returns 200", status == 200, f"got {status}")

    status, _ = request("DELETE", f"/assessment/{assessment_id}")
    check("DELETE /assessment/{id} returns 200", status == 200, f"got {status}")

    status, _ = request("DELETE", f"/assessment/{assessment_id}")
    check("second DELETE returns 404", status == 404, f"got {status}")


def main():
    print(f"Testing API at {BASE_URL}\n")

    try:
        request("GET", "/health")
    except Exception as error:  # noqa: BLE001 - report any connection problem
        print(f"Cannot reach {BASE_URL}: {error}")
        return 1

    test_health()
    test_questions()
    test_disorders_list()
    test_disorder_crud()
    test_disorder_search()
    test_assessment_scoring()
    test_assessment_persistence()
    test_assessment_resubmission()
    test_assessment_validation()
    test_raw_assessment_crud()

    print(f"\n{_checks - len(_failures)}/{_checks} checks passed")

    if _failures:
        print("Failed checks:")
        for failure in _failures:
            print(f"  - {failure}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
