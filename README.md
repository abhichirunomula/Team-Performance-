# ⚡ PerfTrack — Team Performance Management System

A full-featured, dark-themed **Django web application** for managing employee performance reviews, goals, and review cycles — with a three-tier role hierarchy: **Admin → Manager → Employee**.

---

## ✨ Features

| Role | Capabilities |
|------|-------------|
| 🛡️ **Admin** | Create & delete managers, assign managers to employees, full user oversight |
| 👔 **Manager** | Add employees to team, assign tasks/goals, write & finalize performance reviews |
| 👤 **Employee** | Set personal goals, update task status, submit self-assessments, view feedback |

- **Review Cycles** — OPEN → UNDER\_REVIEW → CLOSED state machine
- **Goal Tracking** — with status updates (Not Started / In Progress / Completed)
- **Self-Assessments & Manager Reviews** — visibility gated until review is finalized
- **Filters, Sorting & Pagination** — on all list views
- **Dark glassmorphism UI** — Inter font, CSS variables, responsive sidebar

---

## 🛠️ Tech Stack

- **Backend:** Python 3.x, Django 6.0.5
- **Database:** SQLite (zero-config, included)
- **Frontend:** Vanilla HTML/CSS, Google Fonts (Inter)
- **Auth:** Django built-in authentication + custom `AbstractUser`

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10+** installed → [python.org](https://www.python.org/downloads/)
- Git installed → [git-scm.com](https://git-scm.com/)

---

### 1. Clone the Repository

```bash
git clone https://github.com/abhichirunomula/Team-Performance-.git
cd Team-Performance-
```

---

### 2. Create a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> You should see `(venv)` at the start of your terminal prompt.

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

This creates the SQLite database (`db.sqlite3`) with all required tables.

---

### 5. Create a Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Enter a **username**, **email**, and **password** when prompted.  
This account will have full Admin Panel access inside the app.

---

### 6. Run the Development Server

```bash
python manage.py runserver
```

Open your browser and go to:

```
http://127.0.0.1:8000/
```

Log in with the superuser credentials you created in Step 5.

---

## 🗺️ Application URLs

| URL | Description |
|-----|-------------|
| `/` | Dashboard (role-aware home) |
| `/login/` | Sign in |
| `/register/` | Self-registration |
| `/admin-panel/` | 🛡️ Admin Panel (superuser only) |
| `/team/` | 👔 My Team (managers only) |
| `/goals/` | Goal / Task list |
| `/goals/assign/` | Assign task to employee (manager) |
| `/cycles/` | Review cycles |
| `/reviews/` | Team review management (manager) |
| `/admin/` | Django built-in admin (superuser) |

---

## 👥 User Hierarchy & Setup Guide

```
🛡️  Admin  (superuser — created via createsuperuser)
      │
      ├── Creates Managers  (/admin-panel/managers/create/)
      │
      └── Assigns Managers to Employees  (/admin-panel/employees/<id>/assign-manager/)

👔  Manager  (role = MANAGER — created by Admin)
      │
      ├── Adds Employees to team  (/team/add-employee/)
      └── Assigns Tasks  (/goals/assign/)

👤  Employee  (role = EMPLOYEE — created by Manager or self-registered)
      ├── Updates task status  (/goals/<id>/status/)
      └── Submits self-assessment  (/self-assessment/<cycle>/)
```

**Recommended first-time setup:**
1. Log in as Admin → **Admin Panel** → Create a Manager
2. Log in as Manager → **My Team** → Add Employees
3. Manager → **Goals** → Assign Tasks to employees
4. Manager → **Review Cycles** → Create a cycle and transition to "Under Review"
5. Employees → Submit self-assessments
6. Manager → Write and finalize reviews

---

## 📁 Project Structure

```
Team-Performance-/
│
├── manage.py                     # Django management CLI
├── requirements.txt              # Python dependencies
├── db.sqlite3                    # SQLite database (auto-generated)
│
├── team_performance/             # Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── users/                        # User model, auth, admin panel, team mgmt
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── goals/                        # Goals / Task assignment
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── cycles/                       # Review cycle lifecycle
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── reviews/                      # Self-assessments & manager reviews
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── dashboard/                    # Home / dashboard view
│   └── views.py
│
└── templates/                    # All HTML templates
    ├── base.html                 # Shared layout (sidebar, CSS variables)
    ├── home.html                 # Dashboard
    ├── registration/             # Login, register
    ├── goals/                    # Goal list, create, edit, assign, status
    ├── cycles/                   # Cycle list, create, detail, transition
    ├── reviews/                  # Review forms and detail pages
    └── users/                    # Admin panel, team management pages
```

---

## ⚙️ Environment Notes

- The project uses **SQLite** by default — no external database setup required.
- `DEBUG = True` is set for development. **Never deploy with this setting.**
- The `SECRET_KEY` in `settings.py` must be changed before any production use.

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Django | 6.0.5 | Web framework |
| asgiref | 3.11.1 | ASGI support |
| sqlparse | 0.5.5 | SQL formatting |
| tzdata | 2026.2 | Timezone data |

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source. Feel free to use and modify it.
