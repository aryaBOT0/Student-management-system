/* =====================================================================
   Student Management System - frontend logic
   It talks to the Flask backend using the Fetch API (no page reloads).
   ===================================================================== */

const API = "/api/students";
let studentToDelete = null;       // remembers which student the dialog is about

// ---------- Grab elements from the page ----------
const body = document.getElementById("student-body");
const emptyMsg = document.getElementById("empty-msg");
const form = document.getElementById("student-form");
const searchInput = document.getElementById("search-input");
const clearBtn = document.getElementById("clear-search");
const dialog = document.getElementById("confirm-dialog");
const fields = ["name", "roll_no", "class_name", "marks", "contact"];

// ---------- Small helper functions ----------

// Stops text typed by a user from being treated as HTML (prevents XSS)
function escapeHTML(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Show a temporary message (type = "success" or "error")
function showToast(message, type) {
  const toast = document.createElement("div");
  toast.className = "toast " + type;
  toast.textContent = message;
  document.getElementById("toast-area").appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// Switch between the "dashboard" view and the "form" view
function showView(name) {
  document.getElementById("view-dashboard").hidden = name !== "dashboard";
  document.getElementById("view-form").hidden = name !== "form";
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.view === name);
  });
}

// Send a request to the server and return {ok, data}.
// If the server cannot be reached at all, show an error message.
async function request(url, options) {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    return { ok: response.ok, data };
  } catch (err) {
    showToast("Cannot reach the server. Is app.py running?", "error");
    return { ok: false, data: null };
  }
}

// ---------- READ: load students and draw the table ----------

async function loadStudents() {
  const q = searchInput.value.trim();
  // If something is typed, use the search endpoint; otherwise get everyone
  const url = q ? API + "/search?q=" + encodeURIComponent(q) : API;
  const result = await request(url);
  if (!result.ok) {
    if (result.data) showToast(result.data.error, "error");
    return;
  }
  renderTable(result.data, q);

  // The summary cards always show the numbers for ALL students
  if (q) {
    const all = await request(API);
    if (all.ok) updateStats(all.data);
  } else {
    updateStats(result.data);
  }
}

function renderTable(students, query) {
  body.innerHTML = "";

  // Empty table / unsuccessful search messages
  if (students.length === 0) {
    emptyMsg.hidden = false;
    emptyMsg.textContent = query
      ? 'No students match "' + query + '". Try a different name or roll number.'
      : "No students yet. Use Add Student to create the first record.";
    return;
  }
  emptyMsg.hidden = true;

  students.forEach(s => {
    // Pick a colour for the marks badge
    let level = s.marks >= 75 ? "marks-high" : s.marks >= 50 ? "marks-mid" : "marks-low";
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHTML(s.roll_no)}</td>
      <td>${escapeHTML(s.name)}</td>
      <td>${escapeHTML(s.class_name)}</td>
      <td><span class="marks-badge ${level}">${s.marks}</span></td>
      <td>${escapeHTML(s.contact)}</td>
      <td class="actions">
        <button class="btn btn-ghost btn-sm edit-btn">Edit</button>
        <button class="btn btn-danger btn-sm delete-btn">Delete</button>
      </td>`;
    row.querySelector(".edit-btn").addEventListener("click", () => startEdit(s));
    row.querySelector(".delete-btn").addEventListener("click", () => askDelete(s));
    body.appendChild(row);
  });
}

function updateStats(students) {
  const total = students.length;
  const sum = students.reduce((acc, s) => acc + s.marks, 0);
  const top = students.reduce((max, s) => Math.max(max, s.marks), 0);
  document.getElementById("stat-total").textContent = total;
  document.getElementById("stat-avg").textContent = total ? (sum / total).toFixed(2) : "0";
  document.getElementById("stat-top").textContent = total ? top : "0";
}

// ---------- Form validation (runs in the browser before sending) ----------

function clearErrors() {
  fields.forEach(f => {
    document.getElementById("err-" + f).textContent = "";
    document.getElementById(f).classList.remove("invalid");
  });
}

function setError(field, message) {
  document.getElementById("err-" + field).textContent = message;
  document.getElementById(field).classList.add("invalid");
}

// Returns the student object if valid, otherwise null
function validateForm() {
  clearErrors();
  let valid = true;
  const v = {};
  fields.forEach(f => (v[f] = document.getElementById(f).value.trim()));

  if (!v.name) { setError("name", "Name is required."); valid = false; }
  else if (!/^[A-Za-z][A-Za-z .'-]*$/.test(v.name)) { setError("name", "Use letters and spaces only."); valid = false; }

  if (!v.roll_no) { setError("roll_no", "Roll number is required."); valid = false; }
  if (!v.class_name) { setError("class_name", "Class is required."); valid = false; }

  if (v.marks === "") { setError("marks", "Marks are required."); valid = false; }
  else if (isNaN(v.marks) || Number(v.marks) < 0 || Number(v.marks) > 100) {
    setError("marks", "Marks must be between 0 and 100."); valid = false;
  }

  const phone = v.contact.replace(/[\s-]/g, "");
  if (!v.contact) { setError("contact", "Contact number is required."); valid = false; }
  else if (!/^\+?\d{10,13}$/.test(phone)) { setError("contact", "Enter 10 to 13 digits."); valid = false; }

  return valid ? { ...v, marks: Number(v.marks), contact: phone } : null;
}

// ---------- CREATE and UPDATE (same form) ----------

form.addEventListener("submit", async (event) => {
  event.preventDefault();                    // stop the browser reloading the page
  const student = validateForm();
  if (!student) return;

  const id = document.getElementById("student-id").value;
  const editing = id !== "";
  const result = await request(editing ? API + "/" + id : API, {
    method: editing ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(student),
  });

  if (result.ok) {
    showToast(result.data.message, "success");
    resetForm();
    showView("dashboard");
    loadStudents();
  } else if (result.data) {
    // Server-side errors (e.g. duplicate roll number) are shown on the form too
    showToast(result.data.error, "error");
    if (/roll number/i.test(result.data.error)) setError("roll_no", result.data.error);
  }
});

function resetForm() {
  form.reset();
  document.getElementById("student-id").value = "";
  document.getElementById("form-title").textContent = "Add Student";
  document.getElementById("submit-btn").textContent = "Save student";
  document.getElementById("nav-form").textContent = "Add Student";
  clearErrors();
}

// Fill the form with an existing student so it can be edited
function startEdit(s) {
  resetForm();
  document.getElementById("student-id").value = s.id;
  fields.forEach(f => (document.getElementById(f).value = s[f]));
  document.getElementById("form-title").textContent = "Edit Student";
  document.getElementById("submit-btn").textContent = "Update student";
  document.getElementById("nav-form").textContent = "Edit Student";
  showView("form");
}

// ---------- DELETE (with confirmation dialog) ----------

function askDelete(s) {
  studentToDelete = s;
  document.getElementById("confirm-text").textContent =
    s.name + " (" + s.roll_no + ") will be removed permanently.";
  dialog.showModal();
}

document.getElementById("confirm-no").addEventListener("click", () => dialog.close());

document.getElementById("confirm-yes").addEventListener("click", async () => {
  dialog.close();
  const result = await request(API + "/" + studentToDelete.id, { method: "DELETE" });
  if (result.ok) showToast(result.data.message, "success");
  else if (result.data) showToast(result.data.error, "error");
  loadStudents();
});

// ---------- Search (waits 250 ms after typing stops) ----------

let searchTimer;
searchInput.addEventListener("input", () => {
  clearBtn.hidden = searchInput.value === "";
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadStudents, 250);
});
clearBtn.addEventListener("click", () => {
  searchInput.value = "";
  clearBtn.hidden = true;
  loadStudents();
});

// ---------- Navigation ----------

document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    // Clicking "Add Student" always gives a fresh, empty form
    if (btn.dataset.view === "form") resetForm();
    showView(btn.dataset.view);
  });
});
document.getElementById("cancel-btn").addEventListener("click", () => {
  resetForm();
  showView("dashboard");
});

// ---------- Start: load data when the page opens ----------
loadStudents();
