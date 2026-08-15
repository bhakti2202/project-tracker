# Project & Content Progress Tracker

A personal Flask web dashboard for tracking software projects and blog/content progress.

## Features

- **Projects**: Create, view, edit, delete projects with status, progress, GitHub/live URLs, tech stack
- **Blogs**: Track content from idea to published with tags and statuses
- **Dashboard**: Overview stats, recent activity, progress bars
- **Clean UI**: Responsive developer-dashboard style with sidebar navigation

## Tech Stack

- Python 3.10+
- Flask 3.x
- Flask-SQLAlchemy 3.x
- SQLite (database)
- Jinja2 (templates)
- HTML5 / CSS3 / Vanilla JS

## Project Structure

```
paras/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   ├── models.py            # SQLAlchemy models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── dashboard.py     # Dashboard routes
│   │   ├── projects.py      # Project CRUD
│   │   └── blogs.py         # Blog CRUD
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── projects/
│   │   └── blogs/
│   └── static/
│       ├── css/
│       └── js/
├── instance/                # SQLite DB (auto-created)
├── tests/
├── .gitignore
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
flask init-db
```

### 4. Run Development Server

```bash
flask run
# or
python run.py
```

Visit `http://localhost:5000`

### 5. Run Tests

```bash
pytest
# or with coverage
pytest --cov=app tests/
```

## Configuration

Environment variables (optional):
- `FLASK_ENV` - `development` (default), `production`, `testing`
- `SECRET_KEY` - Secret key for sessions (change in production!)
- `DATABASE_URL` - Database URI (default: SQLite in `instance/tracker.db`)

## Future Improvements

- [ ] Full CRUD for Projects and Blogs
- [ ] Form validation with WTForms
- [ ] Search and filtering
- [ ] Export data (CSV/JSON)
- [ ] Dark mode toggle
- [ ] Mobile sidebar hamburger menu
- [ ] Unit and integration tests
- [ ] GitHub integration (fetch repo stats)
- [ ] Markdown support for notes
- [ ] Tags management for blogs