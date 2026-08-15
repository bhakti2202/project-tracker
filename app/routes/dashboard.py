from flask import Blueprint, render_template
from app.models import Project, Blog
from app import db

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    total_projects = Project.query.count()
    active_projects = Project.query.filter(Project.status.in_(['Planning', 'In Progress', 'Paused'])).count()
    completed_projects = Project.query.filter_by(status='Completed').count()
    avg_progress = db.session.query(db.func.avg(Project.progress)).scalar() or 0

    total_blogs = Blog.query.count()
    draft_blogs = Blog.query.filter_by(status='Draft').count()
    published_blogs = Blog.query.filter_by(status='Published').count()

    recent_projects = Project.query.order_by(Project.updated_at.desc()).limit(5).all()
    recent_blogs = Blog.query.order_by(Blog.updated_at.desc()).limit(5).all()

    return render_template('dashboard.html',
        total_projects=total_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        avg_progress=round(avg_progress, 1),
        total_blogs=total_blogs,
        draft_blogs=draft_blogs,
        published_blogs=published_blogs,
        recent_projects=recent_projects,
        recent_blogs=recent_blogs
    )


@bp.route('/health')
def health():
    return {'status': 'ok'}, 200