# 🧍‍💼 JobMatch

**JobMatch** is a modular, full-stack web application built with **Flask**, designed to connect **Job Seekers** and **Employers** on a unified platform.  
It provides end-to-end functionality — authentication, job management, application tracking, offer letters, chatbot, and learning resources — in one elegant interface.

---

## ⚙️ Installation

### 🧩 Prerequisites
- Python **3.9+**
- pip (Python package manager)

---

## 🧩 Environment Setup

###  Clone the repository

```bash
git clone https://github.com/gopikrishna1999/JobMatch.git
cd JobMatch
```

###  Install dependencies

```bash
pip install -r requirements.txt
```

###  Create `.env` file

```
SECRET_KEY=change_me
SQLALCHEMY_DATABASE_URI=sqlite:///../database/users.db
GEMINI_API_KEY=your_gemini_key_here
MAX_CONTENT_LENGTH=10485760
HOST=127.0.0.1
PORT=5000
FLASK_DEBUG=1
```

> You can skip `GEMINI_API_KEY` if you don’t want chatbot functionality.

---

## 🗄️ Initialize the Database

Open a Python shell and run:

```python
from application import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
```

---

## ▶️ Run the Application

```bash
python run.py
```

Now visit:  
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## ✨ Features

### 👥 Authentication & Role Management
- Secure login and registration using **Flask-Login**
- Role separation: **Seeker** and **Employer**
- Encrypted passwords via **Flask-Bcrypt**

### 💼 Employer Dashboard
- Post, edit, or close job listings
- Review applicants (with “Accept / Reject” confirmation modals)
- Auto-generate and download **Offer Letters**
- Manage educational resources for seekers

### 👨‍💻 Seeker Dashboard
- Apply for open jobs
- View job status (**Under Review / Accepted / Rejected**)
- Prevent duplicate or repeat applications (new Apply button lock system ✅)
- View and download generated **Offer Letters**
- Access resources and chatbot support

### 📬 Offer Letter System
- Auto-filled from template `offer_letter.html`
- Dynamic fields: seeker name, email, company, job title, dates
- Printable and downloadable formats

### 🤖 Chatbot (Gemini AI)
- Integrated with Google **Gemini API**
- Responds to job queries and user help
- Graceful fallback if API key is missing

### 📚 Resources
- Employers add/edit/delete resources
- Seekers browse categorized learning materials (books, links, videos)

---

## 🔒 Security Highlights
- CSRF protection
- Bcrypt password hashing
- Strict role access (employers ↔ seekers)
- Safe file uploads (with allowed file type checks)
- Max upload: 10 MB

---

## 🚀 Production Deployment

Run with Gunicorn:

```bash
gunicorn run:app
```

Or set up via any PaaS (Render, Railway, Azure, etc.), pointing the entry to `run:app`.

---

## 🧰 Troubleshooting

| Issue | Solution |
|-------|-----------|
| `sqlite3.OperationalError: no such table` | Run `db.create_all()` inside Flask shell |
| `GEMINI_API_KEY` error | Add valid API key in `.env` |
| Flash message color mismatch | Clear browser cache or restart Flask |
| Apply button not working | Ensure you applied DB migrations (new columns added) |

---

## 👨‍💻 Developer Notes

- The codebase follows **modular architecture**: routes, services, and utils are separated.
- Routes are registered dynamically inside the Flask **app factory** (`__init__.py`).
- Database models are centralized under `models.py`.
- The `OfferLetter` model and relationships must exist before job or application tables are created.

---

## ✅ Quick Commands

| Action | Command |
|--------|----------|
| Install dependencies | `pip install -r requirements.txt` |
| Initialize DB | `python -m flask shell` → `db.create_all()` |
| Run app | `python run.py` |
| View site | [http://127.0.0.1:5000](http://127.0.0.1:5000) |

---

## 📜 License

**MIT License** © 2025  
Developed by **Gopi Krishna**
