"""
Student Management System - Flask backend
-----------------------------------------
This file has three clearly separated parts:
  1. DATABASE  - connecting to SQLite and creating the table
  2. VALIDATION - checking the data sent by the browser
  3. ROUTES    - the web page and the REST API endpoints
"""

import os
import re
import sqlite3

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# The database file is stored next to app.py, so it is always found
# no matter which folder you start the program from.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.db")


# ======================================================================
# 1. DATABASE LAYER
# ======================================================================

def get_db():
    """Open a connection to students.db.
    row_factory lets us read columns by name (row["name"])."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the students table if it does not exist yet.
    Runs every time the app starts; existing data is NOT deleted."""
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            roll_no    TEXT UNIQUE NOT NULL,
            class_name TEXT NOT NULL,
            marks      REAL NOT NULL,
            contact    TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def row_to_dict(row):
    """Convert a database row into a normal dictionary (so jsonify works)."""
    return dict(row)


# ======================================================================
# 2. VALIDATION LAYER
# ======================================================================

def validate_student(data):
    """Check the JSON data from the browser.
    Returns (clean_data, error_message). If error_message is not None,
    the data is invalid."""
    if not isinstance(data, dict):
        return None, "Invalid request: JSON data expected."

    # --- Required text fields must be present and not blank ---
    name = str(data.get("name", "")).strip()
    roll_no = str(data.get("roll_no", "")).strip().upper()  # ABC1 and abc1 are the same
    class_name = str(data.get("class_name", "")).strip()
    contact = re.sub(r"[\s-]", "", str(data.get("contact", "")))  # remove spaces and dashes
    marks_raw = data.get("marks", "")

    if not name or not roll_no or not class_name or not contact or str(marks_raw).strip() == "":
        return None, "All fields are required."

    # --- Name: letters, spaces, dots and apostrophes only ---
    if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", name):
        return None, "Name may contain only letters and spaces."

    # --- Marks: must be a number between 0 and 100 ---
    try:
        marks = float(marks_raw)
    except (TypeError, ValueError):
        return None, "Marks must be a number."
    if marks != marks or marks < 0 or marks > 100:  # marks != marks catches NaN
        return None, "Marks must be between 0 and 100."

    # --- Contact: 10 to 13 digits, optional leading + ---
    if not re.fullmatch(r"\+?\d{10,13}", contact):
        return None, "Contact number must have 10 to 13 digits."

    clean = {
        "name": name,
        "roll_no": roll_no,
        "class_name": class_name,
        "marks": marks,
        "contact": contact,
    }
    return clean, None


# ======================================================================
# 3. ROUTES
# ======================================================================

@app.route("/")
def index():
    """Serve the main web page."""
    return render_template("index.html")


# Every route below follows the same safe pattern:
#     conn = None
#     try:    ... do the database work ...
#     except: ... return a proper error ...
#     finally: conn.close()      <- ALWAYS runs, even after an error
# Closing the connection in "finally" is important: if an error happened
# and the connection stayed open, SQLite would stay locked.

# ---------- READ: all students ----------
@app.route("/api/students", methods=["GET"])
def get_students():
    conn = None
    try:
        conn = get_db()
        rows = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
        return jsonify([row_to_dict(r) for r in rows]), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if conn:
            conn.close()


# ---------- READ: search by name or roll number ----------
# This fixed path (/search) does not clash with /api/students/<id>
# because <id> only accepts whole numbers (<int:student_id>).
@app.route("/api/students/search", methods=["GET"])
def search_students():
    q = request.args.get("q", "").strip()
    conn = None
    try:
        conn = get_db()
        # The ? placeholders make this a parameterized query (safe from SQL injection)
        rows = conn.execute(
            "SELECT * FROM students WHERE name LIKE ? OR roll_no LIKE ? ORDER BY id DESC",
            (f"%{q}%", f"%{q}%"),
        ).fetchall()
        return jsonify([row_to_dict(r) for r in rows]), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if conn:
            conn.close()


# ---------- CREATE ----------
@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)  # silent=True: returns None instead of crashing on bad JSON
    clean, error = validate_student(data)
    if error:
        return jsonify({"error": error}), 400

    conn = None
    try:
        conn = get_db()
        cur = conn.execute(
            "INSERT INTO students (name, roll_no, class_name, marks, contact) VALUES (?, ?, ?, ?, ?)",
            (clean["name"], clean["roll_no"], clean["class_name"], clean["marks"], clean["contact"]),
        )
        conn.commit()  # commit = permanently save to students.db
        row = conn.execute("SELECT * FROM students WHERE id = ?", (cur.lastrowid,)).fetchone()
        return jsonify({"message": "Student added successfully.", "student": row_to_dict(row)}), 201
    except sqlite3.IntegrityError:
        # Raised because roll_no is UNIQUE and this one already exists
        return jsonify({"error": f"Roll number {clean['roll_no']} already exists."}), 409
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if conn:
            conn.close()


# ---------- UPDATE ----------
@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json(silent=True)
    clean, error = validate_student(data)
    if error:
        return jsonify({"error": error}), 400

    conn = None
    try:
        conn = get_db()
        cur = conn.execute(
            "UPDATE students SET name = ?, roll_no = ?, class_name = ?, marks = ?, contact = ? WHERE id = ?",
            (clean["name"], clean["roll_no"], clean["class_name"], clean["marks"], clean["contact"], student_id),
        )
        conn.commit()
        if cur.rowcount == 0:  # no row was changed -> this id does not exist
            return jsonify({"error": "Student not found."}), 404
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        return jsonify({"message": "Student updated successfully.", "student": row_to_dict(row)}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": f"Roll number {clean['roll_no']} already belongs to another student."}), 409
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if conn:
            conn.close()


# ---------- DELETE ----------
@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    conn = None
    try:
        conn = get_db()
        cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Student not found."}), 404
        return jsonify({"message": "Student deleted successfully."}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if conn:
            conn.close()


# Return JSON (not an HTML page) for unknown API URLs
@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Resource not found."}), 404


@app.errorhandler(405)
def method_not_allowed(_):
    return jsonify({"error": "Method not allowed."}), 405


# ======================================================================
# START THE SERVER
# ======================================================================
if __name__ == "__main__":
    init_db()                 # create students.db and the table if needed
    app.run(debug=True)       # Flask's built-in development server
