"""
routes/projects.py - Project management blueprint
Admin: create, view, delete projects
Member: view projects only
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, Project, Task, User
from functools import wraps

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')


def admin_required(f):
    """Decorator: only allow admin users. Returns 403 for others."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


@projects_bp.route('/')
@login_required
def list_projects():
    """Show all projects. Admins see all; members see projects with their tasks."""
    if current_user.is_admin():
        projects = Project.query.order_by(Project.created_at.desc()).all()
    else:
        # Members see projects that have tasks assigned to them
        task_project_ids = db.session.query(Task.project_id).filter_by(
            assigned_to=current_user.id
        ).distinct().all()
        ids = [r[0] for r in task_project_ids]
        projects = Project.query.filter(Project.id.in_(ids)).all()

    return render_template('projects/list.html', projects=projects)


@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_project():
    """Admin: create a new project."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Project name is required.', 'danger')
            return render_template('projects/create.html')

        if Project.query.filter_by(name=name).first():
            flash('A project with that name already exists.', 'warning')
            return render_template('projects/create.html')

        project = Project(name=name, description=description, created_by=current_user.id)
        db.session.add(project)
        db.session.commit()

        flash(f'Project "{name}" created successfully!', 'success')
        return redirect(url_for('projects.list_projects'))

    return render_template('projects/create.html')


@projects_bp.route('/<int:project_id>')
@login_required
def project_detail(project_id):
    """View a project and its tasks."""
    project = Project.query.get_or_404(project_id)

    if current_user.is_admin():
        tasks = Task.query.filter_by(project_id=project_id).all()
    else:
        tasks = Task.query.filter_by(
            project_id=project_id,
            assigned_to=current_user.id
        ).all()

    members = User.query.filter_by(role='member').all()
    return render_template('projects/detail.html', project=project, tasks=tasks, members=members)


@projects_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_project(project_id):
    """Admin: delete a project (cascades to tasks)."""
    project = Project.query.get_or_404(project_id)
    name = project.name
    db.session.delete(project)
    db.session.commit()
    flash(f'Project "{name}" deleted.', 'info')
    return redirect(url_for('projects.list_projects'))
