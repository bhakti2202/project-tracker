from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models import Project
from app import db

bp = Blueprint('projects', __name__, url_prefix='/projects')


@bp.route('/')
def index():
    projects = Project.query.order_by(Project.updated_at.desc()).all()
    return render_template('projects/index.html', projects=projects)


def validate_project_form(form):
    """Validate project form data and return errors dict."""
    errors = {}
    
    name = form.get('name', '').strip()
    if not name:
        errors['name'] = 'Project name is required.'
    elif len(name) > 100:
        errors['name'] = 'Project name must be 100 characters or less.'
    
    status = form.get('status', '').strip()
    if status and status not in Project.VALID_STATUSES:
        errors['status'] = f'Invalid status. Must be one of: {", ".join(Project.VALID_STATUSES)}'
    
    progress_str = form.get('progress', '').strip()
    if progress_str:
        try:
            progress = int(progress_str)
            if progress < 0 or progress > 100:
                errors['progress'] = 'Progress must be between 0 and 100.'
        except ValueError:
            errors['progress'] = 'Progress must be a valid number.'
    
    github_url = form.get('github_url', '').strip()
    if github_url and len(github_url) > 255:
        errors['github_url'] = 'GitHub URL must be 255 characters or less.'
    
    live_url = form.get('live_url', '').strip()
    if live_url and len(live_url) > 255:
        errors['live_url'] = 'Live URL must be 255 characters or less.'
    
    tech_stack = form.get('tech_stack', '').strip()
    if tech_stack and len(tech_stack) > 255:
        errors['tech_stack'] = 'Tech stack must be 255 characters or less.'
    
    return errors


@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        errors = validate_project_form(request.form)
        
        if errors:
            for field, message in errors.items():
                flash(message, 'error')
            return render_template('projects/create.html', form=request.form, errors=errors), 400
        
        project = Project(
            name=request.form.get('name', '').strip(),
            description=request.form.get('description', '').strip() or None,
            status=request.form.get('status', 'Idea').strip() or 'Idea',
            progress=int(request.form.get('progress', 0) or 0),
            github_url=request.form.get('github_url', '').strip() or None,
            live_url=request.form.get('live_url', '').strip() or None,
            tech_stack=request.form.get('tech_stack', '').strip() or None,
            notes=request.form.get('notes', '').strip() or None,
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully!', 'success')
        return redirect(url_for('projects.detail', id=project.id))
    
    # GET request - show empty form with defaults
    default_form = {
        'name': '',
        'description': '',
        'status': 'Idea',
        'progress': '0',
        'github_url': '',
        'live_url': '',
        'tech_stack': '',
        'notes': '',
    }
    return render_template('projects/create.html', form=default_form, errors={}, valid_statuses=Project.VALID_STATUSES)


@bp.route('/<int:id>')
def detail(id):
    project = Project.query.get_or_404(id)
    return render_template('projects/detail.html', project=project)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    project = Project.query.get_or_404(id)
    
    if request.method == 'POST':
        errors = validate_project_form(request.form)
        
        if errors:
            for field, message in errors.items():
                flash(message, 'error')
            # Re-populate form with submitted values
            form_data = dict(request.form)
            return render_template('projects/edit.html', project=project, form=form_data, errors=errors), 400
        
        project.name = request.form.get('name', '').strip()
        project.description = request.form.get('description', '').strip() or None
        project.status = request.form.get('status', 'Idea').strip() or 'Idea'
        project.progress = int(request.form.get('progress', 0) or 0)
        project.github_url = request.form.get('github_url', '').strip() or None
        project.live_url = request.form.get('live_url', '').strip() or None
        project.tech_stack = request.form.get('tech_stack', '').strip() or None
        project.notes = request.form.get('notes', '').strip() or None
        
        db.session.commit()
        
        flash('Project updated successfully!', 'success')
        return redirect(url_for('projects.detail', id=project.id))
    
    # GET request - pre-populate form with current values
    form_data = {
        'name': project.name,
        'description': project.description or '',
        'status': project.status,
        'progress': str(project.progress),
        'github_url': project.github_url or '',
        'live_url': project.live_url or '',
        'tech_stack': project.tech_stack or '',
        'notes': project.notes or '',
    }
    return render_template('projects/edit.html', project=project, form=form_data, errors={}, valid_statuses=Project.VALID_STATUSES)


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    project = Project.query.get_or_404(id)
    
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('projects.index'))