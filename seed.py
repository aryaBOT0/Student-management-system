"""
OPTIONAL: adds 6 demo students so the dashboard is not empty.
Run once with:  python seed.py
Students whose roll number already exists are skipped, so it is safe to run twice.
"""
import sqlite3
from app import init_db, DB_PATH

DEMO = [
    ("Aarav Sharma",  "CS101", "TY BSc CS", 88.5, "9876543210"),
    ("Priya Deshmukh", "CS102", "TY BSc CS", 92.0, "9823456781"),
    ("Rohan Patil",   "CS103", "SY BSc CS", 67.5, "9765432109"),
    ("Sneha Kulkarni", "IT201", "SY BSc IT", 74.0, "9890123456"),
    ("Imran Sheikh",  "IT202", "FY BSc IT", 55.0, "9922334455"),
    ("Neha Joshi",    "IT203", "FY BSc IT", 81.25, "9811223344"),
]

init_db()
conn = sqlite3.connect(DB_PATH)
added = 0
for row in DEMO:
    try:
        conn.execute(
            "INSERT INTO students (name, roll_no, class_name, marks, contact) VALUES (?, ?, ?, ?, ?)", row
        )
        added += 1
    except sqlite3.IntegrityError:
        pass  # already there
conn.commit()
conn.close()
print(f"Seed complete: {added} student(s) added.")
