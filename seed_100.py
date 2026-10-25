"""
Adds 100 random demo students to students.db.
Run once with:  python seed_100.py
Roll numbers are unique, and existing roll numbers are skipped,
so running it twice will not create duplicates.
"""
import random
import sqlite3
from app import init_db, DB_PATH

first_names = ["Aarav", "Priya", "Rohan", "Sneha", "Imran", "Neha", "Vikram", "Anjali", "Karan", "Pooja",
               "Rahul", "Divya", "Amit", "Sakshi", "Arjun", "Isha", "Nikhil", "Riya", "Siddharth", "Tanvi",
               "Yash", "Megha", "Harsh", "Kavya", "Manish", "Shruti", "Omkar", "Pallavi", "Tushar", "Ritika"]
last_names = ["Sharma", "Deshmukh", "Patil", "Kulkarni", "Sheikh", "Joshi", "Verma", "Gupta", "Mehta", "Reddy",
              "Nair", "Bhosale", "Jadhav", "Pawar", "Kale", "Thakur", "Khan", "Singh", "Iyer", "Chavan"]
classes = ["FY BSc CS", "SY BSc CS", "TY BSc CS", "FY BSc IT", "SY BSc IT", "TY BSc IT"]
prefixes = {"FY BSc CS": "FC", "SY BSc CS": "SC", "TY BSc CS": "TC",
            "FY BSc IT": "FI", "SY BSc IT": "SI", "TY BSc IT": "TI"}

random.seed(42)  # same data every time you run it
init_db()
conn = sqlite3.connect(DB_PATH)
added = 0

for i in range(1, 101):
    name = random.choice(first_names) + " " + random.choice(last_names)
    class_name = random.choice(classes)
    roll_no = f"{prefixes[class_name]}{1000 + i}"               # e.g. TC1007
    marks = round(random.uniform(35, 99), 1)                    # between 35 and 99
    contact = str(random.choice("6789")) + "".join(random.choice("0123456789") for _ in range(9))
    try:
        conn.execute(
            "INSERT INTO students (name, roll_no, class_name, marks, contact) VALUES (?, ?, ?, ?, ?)",
            (name, roll_no, class_name, marks, contact),
        )
        added += 1
    except sqlite3.IntegrityError:
        pass  # roll number already exists, skip

conn.commit()
conn.close()
print(f"Done: {added} student(s) added.")
