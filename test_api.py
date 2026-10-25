"""
Optional automated test. Start the app (python app.py) in one terminal,
then run in another terminal:  python test_api.py
Uses only Python's standard library. It creates and removes its own test records.
"""
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:5000/api/students"

def call(method, url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

passed = failed = 0
def check(label, actual, expected):
    global passed, failed
    ok = actual == expected
    passed += ok; failed += (not ok)
    print(("PASS" if ok else "FAIL"), "-", label, "" if ok else f"(got {actual}, expected {expected})")

good = {"name": "Test Student", "roll_no": "T900", "class_name": "TY BSc CS", "marks": 80, "contact": "9999999999"}

s, d = call("POST", BASE, good);                       check("Add student", s, 201)
sid = d["student"]["id"]
s, d = call("POST", BASE, good);                       check("Duplicate roll number rejected", s, 409)
s, d = call("POST", BASE, {**good, "roll_no": "T901", "marks": 150}); check("Marks 150 rejected", s, 400)
s, d = call("POST", BASE, {**good, "roll_no": "T901", "marks": -5});  check("Marks -5 rejected", s, 400)
s, d = call("POST", BASE, {**good, "roll_no": "T901", "contact": "123"}); check("Short contact rejected", s, 400)
s, d = call("POST", BASE, {**good, "roll_no": "T901", "name": ""});   check("Empty name rejected", s, 400)
s, d = call("GET", BASE + "/search?q=T900");           check("Search by roll number", (s, len(d)), (200, 1))
s, d = call("GET", BASE + "/search?q=test%20stu");       check("Search by name", (s, len(d)), (200, 1))
s, d = call("GET", BASE + "/search?q=zzzzzz");         check("Unsuccessful search returns empty list", (s, d), (200, []))
s, d = call("PUT", f"{BASE}/{sid}", {**good, "marks": 91}); check("Update student", (s, d["student"]["marks"]), (200, 91.0))
s, d = call("PUT", f"{BASE}/99999", good);             check("Update missing student -> 404", s, 404)
s, d = call("DELETE", f"{BASE}/{sid}");                check("Delete student", s, 200)
s, d = call("DELETE", f"{BASE}/{sid}");                check("Delete again -> 404", s, 404)
print(f"\n{passed} passed, {failed} failed")
