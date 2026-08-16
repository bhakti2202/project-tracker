from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models import Blog
from app import db

bp = Blueprint('blogs', __name__, url_prefix='/blogs')


def validate_blog_form(form):
    """Validate blog form data and return errors dict."""
    errors = {}
    
    title = form.get('title', '').strip()
    if not title:
        errors['title'] = 'Blog title is required.'
    elif len(title) > 200:
        errors['title'] = 'Blog title must be 200 characters or less.'
    
    status = form.get('status', '').strip()
    if status and status not in Blog.VALID_STATUSES:
        errors['status'] = f'Invalid status. Must be one of: {", ".join(Blog.VALID_STATUSES)}'
    
    url = form.get('url', '').strip()
    if url and len(url) > 255:
        errors['url'] = 'URL must be 255 characters or less.'
    
    tags = form.get('tags', '').strip()
    if tags and len(tags) > 255:
        errors['tags'] = 'Tags must be 255 characters or less.'
    
    return errors


@bp.route('/')
def index():
    search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    query = Blog.query
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Blog.title.ilike(search_term),
                Blog.description.ilike(search_term),
                Blog.tags.ilike(search_term),
            )
        )
    
    if status_filter:
        query = query.filter(Blog.status == status_filter)
    
    blogs = query.order_by(Blog.updated_at.desc()).all()
    return render_template('blogs/index.html', blogs=blogs, search=search, status_filter=status_filter, valid_statuses=Blog.VALID_STATUSES)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        errors = validate_blog_form(request.form)
        
        if errors:
            for field, message in errors.items():
                flash(message, 'error')
            return render_template('blogs/create.html', form=request.form, errors=errors, valid_statuses=Blog.VALID_STATUSES), 400
        
        blog = Blog(
            title=request.form.get('title', '').strip(),
            description=request.form.get('description', '').strip() or None,
            status=request.form.get('status', 'Idea').strip() or 'Idea',
            url=request.form.get('url', '').strip() or None,
            tags=request.form.get('tags', '').strip() or None,
            notes=request.form.get('notes', '').strip() or None,
        )
        
        db.session.add(blog)
        db.session.commit()
        
        flash('Blog created successfully!', 'success')
        return redirect(url_for('blogs.detail', id=blog.id))
    
    # GET request - show empty form with defaults
    default_form = {
        'title': '',
        'description': '',
        'status': 'Idea',
        'url': '',
        'tags': '',
        'notes': '',
    }
    return render_template('blogs/create.html', form=default_form, errors={}, valid_statuses=Blog.VALID_STATUSES)


@bp.route('/<int:id>')
def detail(id):
    blog = Blog.query.get_or_404(id)
    return render_template('blogs/detail.html', blog=blog)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    blog = Blog.query.get_or_404(id)
    
    if request.method == 'POST':
        errors = validate_blog_form(request.form)
        
        if errors:
            for field, message in errors.items():
                flash(message, 'error')
            # Re-populate form with submitted values
            form_data = dict(request.form)
            return render_template('blogs/edit.html', blog=blog, form=form_data, errors=errors, valid_statuses=Blog.VALID_STATUSES), 400
        
        blog.title = request.form.get('title', '').strip()
        blog.description = request.form.get('description', '').strip() or None
        blog.status = request.form.get('status', 'Idea').strip() or 'Idea'
        blog.url = request.form.get('url', '').strip() or None
        blog.tags = request.form.get('tags', '').strip() or None
        blog.notes = request.form.get('notes', '').strip() or None
        
        db.session.commit()
        
        flash('Blog updated successfully!', 'success')
        return redirect(url_for('blogs.detail', id=blog.id))
    
    # GET request - pre-populate form with current values
    form_data = {
        'title': blog.title,
        'description': blog.description or '',
        'status': blog.status,
        'url': blog.url or '',
        'tags': blog.tags or '',
        'notes': blog.notes or '',
    }
    return render_template('blogs/edit.html', blog=blog, form=form_data, errors={}, valid_statuses=Blog.VALID_STATUSES)


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    blog = Blog.query.get_or_404(id)
    
    db.session.delete(blog)
    db.session.commit()
    
    flash('Blog deleted successfully!', 'success')
    return redirect(url_for('blogs.index'))