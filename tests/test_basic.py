import pytest
from app import create_app, db
from app.models import Project, Blog


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_app_startup(client):
    """Test that the application starts and responds."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_dashboard_route(client):
    """Test dashboard route returns 200."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Dashboard' in response.data


def test_create_project(app):
    """Test creating a project."""
    with app.app_context():
        project = Project(
            name='Test Project',
            description='A test project',
            status='In Progress',
            progress=50,
            github_url='https://github.com/test/repo',
            tech_stack='Python, Flask'
        )
        db.session.add(project)
        db.session.commit()

        assert project.id is not None
        assert project.name == 'Test Project'
        assert project.status == 'In Progress'
        assert project.progress == 50


def test_retrieve_projects(app):
    """Test retrieving projects."""
    with app.app_context():
        Project(name='Project 1', status='Idea').save()
        Project(name='Project 2', status='Completed').save()

        projects = Project.query.all()
        assert len(projects) == 2
        assert projects[0].name == 'Project 1'
        assert projects[1].name == 'Project 2'


def test_create_blog(app):
    """Test creating a blog."""
    with app.app_context():
        blog = Blog(
            title='Test Blog',
            description='A test blog post',
            status='Draft',
            tags='python, flask',
            url='https://example.com/blog'
        )
        db.session.add(blog)
        db.session.commit()

        assert blog.id is not None
        assert blog.title == 'Test Blog'
        assert blog.status == 'Draft'


def test_project_crud(app):
    """Test basic project CRUD operations."""
    with app.app_context():
        # Create
        project = Project(name='CRUD Test', status='Planning', progress=10)
        db.session.add(project)
        db.session.commit()
        pid = project.id

        # Read
        project = Project.query.get(pid)
        assert project.name == 'CRUD Test'

        # Update
        project.status = 'In Progress'
        project.progress = 50
        db.session.commit()

        project = Project.query.get(pid)
        assert project.status == 'In Progress'
        assert project.progress == 50

        # Delete
        db.session.delete(project)
        db.session.commit()

        assert Project.query.get(pid) is None


def test_blog_crud(app):
    """Test basic blog CRUD operations."""
    with app.app_context():
        # Create
        blog = Blog(title='CRUD Blog', status='Idea')
        db.session.add(blog)
        db.session.commit()
        bid = blog.id

        # Read
        blog = Blog.query.get(bid)
        assert blog.title == 'CRUD Blog'

        # Update
        blog.status = 'Published'
        db.session.commit()

        blog = Blog.query.get(bid)
        assert blog.status == 'Published'

        # Delete
        db.session.delete(blog)
        db.session.commit()

        assert Blog.query.get(bid) is None

# Add save method to models for test convenience
def _save(self):
    db.session.add(self)
    db.session.commit()


Project.save = _save
Blog.save = _save


# Web-level Project CRUD tests
def test_project_create_page(client):
    """Test GET /projects/create returns the create form."""
    response = client.get('/projects/create')
    assert response.status_code == 200
    assert b'New Project' in response.data
    assert b'Project Name' in response.data


def test_project_create_valid_post(client):
    """Test valid POST to /projects/create creates a Project."""
    response = client.post('/projects/create', data={
        'name': 'Web Test Project',
        'description': 'Created via web form',
        'status': 'In Progress',
        'progress': '75',
        'github_url': 'https://github.com/test/web',
        'live_url': 'https://example.com/web',
        'tech_stack': 'Python, Flask, HTMX',
        'notes': 'Web test notes'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Web Test Project' in response.data
    assert b'Project created successfully' in response.data
    
    # Verify in database
    with client.application.app_context():
        project = Project.query.filter_by(name='Web Test Project').first()
        assert project is not None
        assert project.description == 'Created via web form'
        assert project.status == 'In Progress'
        assert project.progress == 75
        assert project.github_url == 'https://github.com/test/web'
        assert project.live_url == 'https://example.com/web'
        assert project.tech_stack == 'Python, Flask, HTMX'
        assert project.notes == 'Web test notes'


def test_project_detail_page(client):
    """Test GET /projects/<id> returns 200 for existing project."""
    with client.application.app_context():
        project = Project(name='Detail Test', status='Planning', progress=25)
        db.session.add(project)
        db.session.commit()
        pid = project.id
    
    response = client.get(f'/projects/{pid}')
    assert response.status_code == 200
    assert b'Detail Test' in response.data
    assert b'Planning' in response.data
    assert b'25%' in response.data


def test_project_detail_404(client):
    """Test GET /projects/<id> returns 404 for non-existent project."""
    response = client.get('/projects/99999')
    assert response.status_code == 404


def test_project_edit_page(client):
    """Test GET /projects/<id>/edit returns form with existing data."""
    with client.application.app_context():
        project = Project(name='Edit Test', status='In Progress', progress=50, tech_stack='Go, React')
        db.session.add(project)
        db.session.commit()
        pid = project.id
    
    response = client.get(f'/projects/{pid}/edit')
    assert response.status_code == 200
    assert b'Edit Project' in response.data
    assert b'Edit Test' in response.data
    assert b'In Progress' in response.data
    assert b'Go, React' in response.data


def test_project_edit_valid_post(client):
    """Test valid POST to /projects/<id>/edit updates the Project."""
    with client.application.app_context():
        project = Project(name='Before Edit', status='Idea', progress=0)
        db.session.add(project)
        db.session.commit()
        pid = project.id
    
    response = client.post(f'/projects/{pid}/edit', data={
        'name': 'After Edit',
        'description': 'Updated description',
        'status': 'Completed',
        'progress': '100',
        'github_url': '',
        'live_url': '',
        'tech_stack': 'Updated Stack',
        'notes': 'Updated notes'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'After Edit' in response.data
    assert b'Project updated successfully' in response.data
    
    # Verify in database
    with client.application.app_context():
        project = Project.query.get(pid)
        assert project.name == 'After Edit'
        assert project.description == 'Updated description'
        assert project.status == 'Completed'
        assert project.progress == 100
        assert project.tech_stack == 'Updated Stack'
        assert project.notes == 'Updated notes'


def test_project_delete(client):
    """Test POST /projects/<id>/delete deletes the Project."""
    with client.application.app_context():
        project = Project(name='To Delete', status='Archived')
        db.session.add(project)
        db.session.commit()
        pid = project.id
    
    response = client.post(f'/projects/{pid}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Project deleted successfully' in response.data
    
    # Verify deleted from database
    with client.application.app_context():
        project = Project.query.get(pid)
        assert project is None


def test_project_edit_404(client):
    """Test GET /projects/<id>/edit returns 404 for non-existent project."""
    response = client.get('/projects/99999/edit')
    assert response.status_code == 404


def test_project_delete_404(client):
    """Test POST /projects/<id>/delete returns 404 for non-existent project."""
    response = client.post('/projects/99999/delete')
    assert response.status_code == 404


def test_project_create_invalid_progress(client):
    """Test invalid progress values are rejected."""
    response = client.post('/projects/create', data={
        'name': 'Invalid Progress',
        'status': 'Idea',
        'progress': '150'  # Invalid: > 100
    }, follow_redirects=True)
    
    assert response.status_code == 400
    assert b'Progress must be between 0 and 100' in response.data
    # Should re-render form with error
    assert b'New Project' in response.data


def test_project_create_invalid_status(client):
    """Test invalid status values are rejected."""
    response = client.post('/projects/create', data={
        'name': 'Invalid Status',
        'status': 'NotAValidStatus',
        'progress': '50'
    }, follow_redirects=True)
    
    assert response.status_code == 400
    assert b'Invalid status' in response.data


def test_project_create_missing_name(client):
    """Test missing required name is rejected."""
    response = client.post('/projects/create', data={
        'name': '',
        'status': 'Idea',
        'progress': '0'
    }, follow_redirects=True)
    
    assert response.status_code == 400
    assert b'Project name is required' in response.data


# Web-level Blog CRUD tests
def test_blog_index_page(client):
    """Test GET /blogs/ returns the blog list."""
    response = client.get('/blogs/')
    assert response.status_code == 200
    assert b'Blogs' in response.data
    assert b'New Blog' in response.data


def test_blog_create_page(client):
    """Test GET /blogs/create returns the create form."""
    response = client.get('/blogs/create')
    assert response.status_code == 200
    assert b'New Blog' in response.data
    assert b'Blog Title' in response.data


def test_blog_create_valid_post(client):
    """Test valid POST to /blogs/create creates a Blog."""
    response = client.post('/blogs/create', data={
        'title': 'Web Test Blog',
        'description': 'Created via web form',
        'status': 'Draft',
        'url': 'https://example.com/blog',
        'tags': 'python, flask',
        'notes': 'Web test notes'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Web Test Blog' in response.data
    assert b'Blog created successfully' in response.data
    
    # Verify in database
    with client.application.app_context():
        blog = Blog.query.filter_by(title='Web Test Blog').first()
        assert blog is not None
        assert blog.description == 'Created via web form'
        assert blog.status == 'Draft'
        assert blog.url == 'https://example.com/blog'
        assert blog.tags == 'python, flask'
        assert blog.notes == 'Web test notes'


def test_blog_detail_page(client):
    """Test GET /blogs/<id> returns 200 for existing blog."""
    with client.application.app_context():
        blog = Blog(title='Detail Blog', status='Published', description='Test description')
        db.session.add(blog)
        db.session.commit()
        bid = blog.id
    
    response = client.get(f'/blogs/{bid}')
    assert response.status_code == 200
    assert b'Detail Blog' in response.data
    assert b'Published' in response.data
    assert b'Test description' in response.data


def test_blog_detail_404(client):
    """Test GET /blogs/<id> returns 404 for non-existent blog."""
    response = client.get('/blogs/99999')
    assert response.status_code == 404


def test_blog_edit_page(client):
    """Test GET /blogs/<id>/edit returns form with existing data."""
    with client.application.app_context():
        blog = Blog(title='Edit Blog', status='Draft', description='To edit', tags='test', url='https://example.com')
        db.session.add(blog)
        db.session.commit()
        bid = blog.id
    
    response = client.get(f'/blogs/{bid}/edit')
    assert response.status_code == 200
    assert b'Edit Blog' in response.data
    assert b'Edit Blog' in response.data
    assert b'Draft' in response.data
    assert b'test' in response.data


def test_blog_edit_valid_post(client):
    """Test valid POST to /blogs/<id>/edit updates the Blog."""
    with client.application.app_context():
        blog = Blog(title='Before Edit', status='Idea', description='Old')
        db.session.add(blog)
        db.session.commit()
        bid = blog.id
    
    response = client.post(f'/blogs/{bid}/edit', data={
        'title': 'After Edit',
        'description': 'Updated description',
        'status': 'Published',
        'url': 'https://updated.com',
        'tags': 'updated, tags',
        'notes': 'Updated notes'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'After Edit' in response.data
    assert b'Blog updated successfully' in response.data
    
    # Verify in database
    with client.application.app_context():
        blog = Blog.query.get(bid)
        assert blog.title == 'After Edit'
        assert blog.description == 'Updated description'
        assert blog.status == 'Published'
        assert blog.url == 'https://updated.com'
        assert blog.tags == 'updated, tags'
        assert blog.notes == 'Updated notes'


def test_blog_delete(client):
    """Test POST /blogs/<id>/delete deletes the Blog."""
    with client.application.app_context():
        blog = Blog(title='To Delete', status='Archived')
        db.session.add(blog)
        db.session.commit()
        bid = blog.id
    
    response = client.post(f'/blogs/{bid}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Blog deleted successfully' in response.data
    
    # Verify deleted from database
    with client.application.app_context():
        blog = Blog.query.get(bid)
        assert blog is None


def test_blog_edit_404(client):
    """Test GET /blogs/<id>/edit returns 404 for non-existent blog."""
    response = client.get('/blogs/99999/edit')
    assert response.status_code == 404


def test_blog_delete_404(client):
    """Test POST /blogs/<id>/delete returns 404 for non-existent blog."""
    response = client.post('/blogs/99999/delete')
    assert response.status_code == 404


def test_blog_create_invalid_status(client):
    """Test invalid status values are rejected."""
    response = client.post('/blogs/create', data={
        'title': 'Invalid Status',
        'status': 'NotAValidStatus',
    }, follow_redirects=True)
    
    assert response.status_code == 400
    assert b'Invalid status' in response.data


def test_blog_create_missing_title(client):
    """Test missing required title is rejected."""
    response = client.post('/blogs/create', data={
        'title': '',
        'status': 'Idea',
    }, follow_redirects=True)
    
    assert response.status_code == 400
    assert b'Blog title is required' in response.data


# Web-level search/filter tests for Projects
def test_projects_index_search_by_name(client):
    """Test searching projects by name."""
    with client.application.app_context():
        Project(name='Alpha Project', status='Idea', description='First project').save()
        Project(name='Beta Project', status='Completed', description='Second project').save()
        Project(name='Gamma', status='Planning', description='Third').save()
    
    response = client.get('/projects/?q=Alpha')
    assert response.status_code == 200
    assert b'Alpha Project' in response.data
    assert b'Beta Project' not in response.data
    assert b'Gamma' not in response.data


def test_projects_index_search_by_description(client):
    """Test searching projects by description."""
    with client.application.app_context():
        Project(name='Project A', status='Idea', description='Uses React').save()
        Project(name='Project B', status='Completed', description='Uses Vue').save()
    
    response = client.get('/projects/?q=React')
    assert response.status_code == 200
    assert b'Project A' in response.data
    assert b'Project B' not in response.data


def test_projects_index_search_by_tech_stack(client):
    """Test searching projects by tech stack."""
    with client.application.app_context():
        Project(name='Project A', status='Idea', tech_stack='Python, Flask').save()
        Project(name='Project B', status='Completed', tech_stack='JavaScript, React').save()
    
    response = client.get('/projects/?q=Python')
    assert response.status_code == 200
    assert b'Project A' in response.data
    assert b'Project B' not in response.data


def test_projects_index_filter_by_status(client):
    """Test filtering projects by status."""
    with client.application.app_context():
        Project(name='Idea Project', status='Idea').save()
        Project(name='Completed Project', status='Completed').save()
        Project(name='In Progress Project', status='In Progress').save()
    
    response = client.get('/projects/?status=Completed')
    assert response.status_code == 200
    assert b'Completed Project' in response.data
    assert b'Idea Project' not in response.data
    assert b'In Progress Project' not in response.data


def test_projects_index_search_and_filter_combined(client):
    """Test combined search and status filter."""
    with client.application.app_context():
        Project(name='Search Project', status='Completed', description='Test').save()
        Project(name='Other Project', status='Idea', description='Test').save()
    
    response = client.get('/projects/?q=Search&status=Completed')
    assert response.status_code == 200
    assert b'Search Project' in response.data
    assert b'Other Project' not in response.data
    
    # Different status should not match
    response = client.get('/projects/?q=Search&status=Idea')
    assert response.status_code == 200
    assert b'Search Project' not in response.data


def test_projects_index_clear_filter(client):
    """Test that clear filter link works."""
    with client.application.app_context():
        Project(name='Test Project', status='Completed').save()
    
    # First with filter
    response = client.get('/projects/?status=Completed')
    assert response.status_code == 200
    assert b'Test Project' in response.data
    
    # Clear filter (no params) should show all
    response = client.get('/projects/')
    assert response.status_code == 200
    assert b'Test Project' in response.data


def test_projects_index_empty_search_shows_all(client):
    """Test empty search shows all projects."""
    with client.application.app_context():
        Project(name='Project 1', status='Idea').save()
        Project(name='Project 2', status='Completed').save()
    
    response = client.get('/projects/?q=')
    assert response.status_code == 200
    assert b'Project 1' in response.data
    assert b'Project 2' in response.data


# Web-level search/filter tests for Blogs
def test_blogs_index_search_by_title(client):
    """Test searching blogs by title."""
    with client.application.app_context():
        Blog(title='First Blog Post', status='Published').save()
        Blog(title='Second Blog Post', status='Draft').save()
        Blog(title='Another Article', status='Idea').save()
    
    response = client.get('/blogs/?q=First')
    assert response.status_code == 200
    assert b'First Blog Post' in response.data
    assert b'Second Blog Post' not in response.data
    assert b'Another Article' not in response.data


def test_blogs_index_search_by_description(client):
    """Test searching blogs by description."""
    with client.application.app_context():
        Blog(title='Blog A', status='Published', description='About Python').save()
        Blog(title='Blog B', status='Draft', description='About JavaScript').save()
    
    response = client.get('/blogs/?q=Python')
    assert response.status_code == 200
    assert b'Blog A' in response.data
    assert b'Blog B' not in response.data


def test_blogs_index_search_by_tags(client):
    """Test searching blogs by tags."""
    with client.application.app_context():
        Blog(title='Blog A', status='Published', tags='python, flask').save()
        Blog(title='Blog B', status='Draft', tags='javascript, react').save()
    
    response = client.get('/blogs/?q=flask')
    assert response.status_code == 200
    assert b'Blog A' in response.data
    assert b'Blog B' not in response.data


def test_blogs_index_filter_by_status(client):
    """Test filtering blogs by status."""
    with client.application.app_context():
        Blog(title='Idea Blog', status='Idea').save()
        Blog(title='Published Blog', status='Published').save()
        Blog(title='Draft Blog', status='Draft').save()
    
    response = client.get('/blogs/?status=Published')
    assert response.status_code == 200
    assert b'Published Blog' in response.data
    assert b'Idea Blog' not in response.data
    assert b'Draft Blog' not in response.data


def test_blogs_index_search_and_filter_combined(client):
    """Test combined search and status filter for blogs."""
    with client.application.app_context():
        Blog(title='Search Blog', status='Published', description='Test').save()
        Blog(title='Other Blog', status='Idea', description='Test').save()
    
    response = client.get('/blogs/?q=Search&status=Published')
    assert response.status_code == 200
    assert b'Search Blog' in response.data
    assert b'Other Blog' not in response.data
    
    # Different status should not match
    response = client.get('/blogs/?q=Search&status=Idea')
    assert response.status_code == 200
    assert b'Search Blog' not in response.data


def test_blogs_index_clear_filter(client):
    """Test that clear filter link works for blogs."""
    with client.application.app_context():
        Blog(title='Test Blog', status='Published').save()
    
    # First with filter
    response = client.get('/blogs/?status=Published')
    assert response.status_code == 200
    assert b'Test Blog' in response.data
    
    # Clear filter (no params) should show all
    response = client.get('/blogs/')
    assert response.status_code == 200
    assert b'Test Blog' in response.data


def test_blogs_index_empty_search_shows_all(client):
    """Test empty search shows all blogs."""
    with client.application.app_context():
        Blog(title='Blog 1', status='Idea').save()
        Blog(title='Blog 2', status='Published').save()
    
    response = client.get('/blogs/?q=')
    assert response.status_code == 200
    assert b'Blog 1' in response.data
    assert b'Blog 2' in response.data


def test_projects_index_search_case_insensitive(client):
    """Test search is case insensitive."""
    with client.application.app_context():
        Project(name='Test Project', status='Idea').save()
    
    response = client.get('/projects/?q=test')
    assert response.status_code == 200
    assert b'Test Project' in response.data
    
    response = client.get('/projects/?q=TEST')
    assert response.status_code == 200
    assert b'Test Project' in response.data


def test_blogs_index_search_case_insensitive(client):
    """Test blog search is case insensitive."""
    with client.application.app_context():
        Blog(title='Test Blog', status='Idea').save()
    
    response = client.get('/blogs/?q=test')
    assert response.status_code == 200
    assert b'Test Blog' in response.data
    
    response = client.get('/blogs/?q=TEST')
    assert response.status_code == 200
    assert b'Test Blog' in response.data