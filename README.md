# 🗂️ TaskFlow – Smart Team Task Manager

A full-stack web application for managing projects, assigning tasks, and tracking team progress with role-based access control.

Built with **Python Flask**, **Bootstrap 5**, and **SQLite** — deployable on Railway in minutes.

---

## 🚀 Live Demo

> **[Live App →](https://your-app.railway.app)**  
> Default login: `admin` / `admin123`

---

## ✨ Features

### 🔐 Authentication
- Secure registration and login with hashed passwords (Werkzeug)
- Session-based auth via Flask-Login
- Role-based access: **Admin** and **Member**

### 📁 Project Management
- Admin: Create, view, and delete projects
- Progress bar showing completion percentage per project
- Cascade delete (deleting a project removes all its tasks)

### ✅ Task Management
- Fields: Title, Description, Assigned User, Status, Priority, Deadline
- Admin: Full CRUD — create, edit, delete, assign
- Member: View assigned tasks, update status (Pending ↔ Completed)
- One-click status toggle
- Priority levels: 🟢 Low · 🟡 Medium · 🔴 High

### 📊 Dashboard
- Stat cards: Total, Completed, Pending, Overdue tasks
- Project progress overview (admin)
- Recent tasks table with quick actions
- Overdue tasks highlighted in red

### 🔒 Role-Based Access Control
- Admin-only routes protected via decorator
- Members can only view/update their own tasks
- Proper 403 handling on all protected routes

### 🌐 REST API
Full JSON API for external integration:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List all users (admin) |
| GET | `/api/projects` | List projects |
| POST | `/api/projects` | Create project (admin) |
| GET | `/api/projects/<id>` | Project detail |
| DELETE | `/api/projects/<id>` | Delete project (admin) |
| GET | `/api/tasks` | List tasks |
| POST | `/api/tasks` | Create task (admin) |
| GET | `/api/tasks/<id>` | Task detail |
| PUT | `/api/tasks/<id>` | Update task |
| DELETE | `/api/tasks/<id>` | Delete task (admin) |
| GET | `/api/stats` | Dashboard stats |

---

## 🗂️ Project Structure

```
smart-task-manager/
├── app.py                  # App factory, extensions, seed
├── models.py               # SQLAlchemy models (User, Project, Task)
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Login, Register, Logout
│   ├── dashboard.py        # Dashboard stats view
│   ├── projects.py         # Project CRUD
│   ├── tasks.py            # Task CRUD + toggle
│   ├── users.py            # User management (admin)
│   └── api.py              # REST API endpoints
├── templates/
│   ├── base.html           # Master layout with sidebar
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── projects/
│   │   ├── list.html
│   │   ├── detail.html
│   │   └── create.html
│   ├── tasks/
│   │   ├── list.html
│   │   ├── create.html
│   │   └── edit.html
│   └── users/
│       └── list.html
├── static/
│   └── css/
│       └── style.css       # Custom styles on Bootstrap 5
├── requirements.txt
├── Procfile                # Gunicorn for Railway
├── railway.json            # Railway deploy config
└── runtime.txt             # Python version pin
```

---

## ⚙️ Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/smart-task-manager.git
cd smart-task-manager
```

### 2. Create virtual environment
```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
```
http://localhost:5000
```

> ✅ On first run, a default admin account is created automatically:  
> **Username:** `admin` | **Password:** `admin123`

---

## 🚂 Deploy on Railway

### Option A: GitHub Integration (Recommended)
1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select this repo
4. Railway auto-detects Python and uses the `Procfile`
5. Set environment variable (optional):
   ```
   SECRET_KEY=your-super-secret-key-here
   ```
6. Click Deploy — your app is live! 🎉

### Option B: Railway CLI
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

---

## 🔑 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `smart-task-manager-secret-2024` | Flask session secret (change in production!) |
| `PORT` | `5000` | Server port (set automatically by Railway) |
| `DATABASE_URL` | `sqlite:///taskmanager.db` | Database URL |

---

## 🧪 Testing the REST API

```bash
# Get stats (must be logged in via session)
curl http://localhost:5000/api/stats

# List all tasks
curl http://localhost:5000/api/tasks

# Create a project (POST)
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "New Project", "description": "Test"}'
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 3.0 |
| Database | SQLite via SQLAlchemy ORM |
| Auth | Flask-Login (session-based) |
| Frontend | HTML5, Bootstrap 5, Bootstrap Icons |
| Deployment | Railway (Gunicorn WSGI) |

---

## 📋 Default Accounts

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Admin |

> Create member accounts from the registration page or Users panel.

---

## 📄 License

MIT License – free to use, modify, and distribute.

---

*Built with ❤️ using Flask + Bootstrap 5*
