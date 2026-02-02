# 🧍‍💼 JobMatch

**JobMatch** is a modular, full-stack web application built with **Flask** that connects **Job Seekers** and **Employers** on a single platform.

It supports authentication, job postings, application tracking, offer letter generation, learning resources, and an AI chatbot — all structured using a clean **Flask app-factory architecture**.

🔗 **Live Demo**  
https://jobmatch-kpo1.onrender.com/

---

## ⚙️ Tech Stack

- **Backend:** Python, Flask  
- **Frontend:** HTML, Jinja2, CSS  
- **Database:** SQLite (SQLAlchemy ORM)  
- **Auth:** Flask-Login, Flask-Bcrypt  
- **AI:** Google Gemini (optional)  
- **Deployment:** Gunicorn + Render  

---

## 📁 Project Structure

```
JobMatch/
│
├── application/
│   ├── templates/        # Jinja HTML templates (case-sensitive)
│   ├── static/           # CSS, images
│   ├── routes/           # Modular route files
│   ├── models.py         # Database models
│   ├── database.py       # DB, bcrypt, login manager
│   ├── config.py         # Environment configs
│   └── __init__.py       # App factory
│
├── run.py                # Local development entry
├── wsgi.py               # Production entry (Gunicorn)
├── requirements.txt
├── .env                  # Not committed
└── README.md
```

## 🧩 Installation (Local)

### Prerequisites
- Python **3.9+**
- pip

### Clone the repository

```bash
git clone https://github.com/gopikrishna9133/JobMatch.git
cd JobMatch
```

### Create virtual environment

```bash
python -m venv venv
```

Activate:

**Windows**
```bash
venv\Scripts\activate
```

**macOS / Linux**
```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
SQLALCHEMY_DATABASE_URI=sqlite:///database.db
GEMINI_API_KEY=your_gemini_api_key
MAX_CONTENT_LENGTH=10485760
```

---

## 🗄️ Initialize the Database

```bash
python
```

```python
from application import create_app
from application.database import db

app = create_app()
with app.app_context():
    db.create_all()
```

---

## ▶️ Run the Application

```bash
python run.py
```

Visit: http://127.0.0.1:5000

---

## 🚀 Production

```bash
gunicorn wsgi:app
```

---

## 📜 License

MIT License © 2026  
Developed by **Gopi Krishna**
