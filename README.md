# Student Management System

A beginner-friendly web app to add, view, search, update and delete student records.

**Stack:** HTML + CSS + JavaScript (frontend) · Python Flask (backend) · SQLite (database)

## Project structure

```
student-management-system/
├── app.py              Flask backend: database, validation, API routes
├── students.db         SQLite database (created automatically on first run)
├── seed.py             OPTIONAL: adds 6 demo students
├── test_api.py         OPTIONAL: automated API test (13 checks)
├── requirements.txt    Python dependencies (Flask)
├── templates/
│   └── index.html      The web page
└── static/
    ├── style.css       Styling (colours, layout, responsive rules)
    └── script.js       Frontend logic (Fetch API calls)
```

## How to run (Windows)

1. **Install Python** (skip if already installed). Download from https://www.python.org/downloads/ and
   run the installer. **Tick "Add python.exe to PATH"** on the first screen.
   Check it worked: open Command Prompt and type `python --version`.
2. **Open the project in VS Code:** File > Open Folder > select `student-management-system`.
   Then open the terminal with **Terminal > New Terminal**.
3. **Create a virtual environment:**
   ```
   python -m venv venv
   ```
4. **Activate it:**
   ```
   venv\Scripts\activate
   ```
   (Use this in Command Prompt. In PowerShell, if you see a "running scripts is disabled" error, run
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first, then activate again.)
   You should now see `(venv)` at the start of the prompt.
5. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
6. **(Optional) Add demo data:**
   ```
   python seed.py
   ```
7. **Start the app:**
   ```
   python app.py
   ```
8. **Open the browser** at http://127.0.0.1:5000

Press `Ctrl + C` in the terminal to stop the server. Your data stays in `students.db`.
To start with an empty database, stop the server and delete `students.db`.

## API endpoints

| Method | URL                     | Purpose                         | Success | Errors        |
|--------|-------------------------|---------------------------------|---------|---------------|
| GET    | `/api/students`         | List all students               | 200     | 500           |
| GET    | `/api/students/search?q=value` | Search by name or roll no | 200  | 500           |
| POST   | `/api/students`         | Add a student                   | 201     | 400, 409, 500 |
| PUT    | `/api/students/<id>`    | Update a student                | 200     | 400, 404, 409, 500 |
| DELETE | `/api/students/<id>`    | Delete a student                | 200     | 404, 500      |

Codes: 400 = invalid input, 404 = student not found, 409 = duplicate roll number, 500 = database error.

## Validation rules

- All fields are required.
- Name: letters and spaces only.
- Marks: a number from 0 to 100.
- Contact: 10 to 13 digits (an optional leading `+`; spaces and dashes are ignored).
- Roll number: must be unique (stored in capitals, so `cs101` and `CS101` are the same).

Validation runs twice: in the browser (instant feedback) and in Flask (the real safety check).

## Testing

Manual test cases:

| # | Test | Steps | Expected result |
|---|------|-------|-----------------|
| 1 | Add | Add Student > Aarav Sharma, CS101, TY BSc CS, 88.5, 9876543210 > Save | Green "added" message; row appears; total increases by 1 |
| 2 | Search by name | Type `aarav` in the search bar | Only matching rows are shown |
| 3 | Search by roll no | Type `CS10` | All roll numbers containing CS10 are shown |
| 4 | No match | Type `zzzz` | "No students match..." message |
| 5 | Update | Click Edit, change marks to 91, click Update student | Green "updated" message; table shows 91; average changes |
| 6 | Delete | Click Delete, then Delete in the dialog | Row disappears; green "deleted" message |
| 7 | Cancel delete | Click Delete, then Keep student | Nothing is deleted |
| 8 | Duplicate roll no | Add another student with roll number CS101 | Red error "Roll number CS101 already exists." |
| 9 | Invalid marks | Enter marks 150 (or -5) | Red message "Marks must be between 0 and 100." |
| 10 | Bad contact | Enter contact `12345` | Red message "Enter 10 to 13 digits." |
| 11 | Empty fields | Click Save with a blank form | Red "required" message under each field |
| 12 | Persistence | Stop the server (Ctrl+C), run `python app.py` again | All records are still there |

Automated API test: start the app in one terminal, then in a second terminal (with the venv active) run
`python test_api.py`. It should end with `13 passed, 0 failed`.

## How the parts work together

1. The **browser** requests `/`. **Flask** returns `index.html`, which links `style.css` and `script.js`.
2. **HTML** is the structure (form, table, buttons). **CSS** is the look (colours, cards, responsive layout).
3. **JavaScript** runs in the browser. When the page opens (or you click Save, Edit, Delete, or type in search),
   it uses `fetch()` to send a request to an `/api/...` URL and gets JSON back. It then redraws only the table,
   so the page never reloads.
4. **Flask** receives the request, validates the data, and runs a parameterized SQL query.
5. **SQLite** stores the data in the file `students.db`, so it survives restarts.
6. Flask sends JSON back (with a status code), and JavaScript shows a success or error notification.

```
Browser (HTML/CSS/JS)  --fetch JSON-->  Flask (app.py)  --SQL-->  SQLite (students.db)
Browser                <--JSON + code--  Flask           <--rows--  SQLite
```

## Troubleshooting

- **`python` is not recognized:** reinstall Python and tick "Add python.exe to PATH", or try `py` instead of `python`.
- **Port 5000 already in use:** close the other program, or change the last line of `app.py` to `app.run(debug=True, port=5001)`.
- **Cannot reach the server message in the browser:** `python app.py` is not running.
