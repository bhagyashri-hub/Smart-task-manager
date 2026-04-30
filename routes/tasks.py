"""
routes/tasks.py - Task management blueprint
Admin: create, edit, delete, assign tasks
Member: view and update status of assigned tasks
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Task, Project, User
from datetime import datetime
from functools import wraps

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


def admin_required(f):
    """Decorator: restrict route to admin users only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


@tasks_bp.route('/')
@login_required
def list_tasks():
    """
    All tasks view.
    Admin: sees everything with filters.
    Member: sees only assigned tasks.
    """
    # Filter params
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    project_filter = request.args.get('project_id', '')

    query = Task.query

    # Members only see their tasks
    if not current_user.is_admin():
        query = query.filter_by(assigned_to=current_user.id)

    # Apply optional filters
    if status_filter:
        query = query.filter_by(status=status_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    if project_filter and project_filter.isdigit():
        query = query.filter_by(project_id=int(project_filter))

    tasks = query.order_by(Task.deadline.asc()).all()
    projects = Project.query.all()

    return render_template(
        'tasks/list.html',
        tasks=tasks,
        projects=projects,
        status_filter=status_filter,
        priority_filter=priority_filter,
        project_filter=project_filter
    )


@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_task():
    """Admin: create a new task and assign it to a member."""
    projects = Project.query.all()
    members = User.query.all()  # Admin can assign to any user

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        project_id = request.form.get('project_id', '')
        assigned_to = request.form.get('assigned_to', '')
        status = request.form.get('status', 'pending')
        priority = request.form.get('priority', 'medium')
        deadline_str = request.form.get('deadline', '')

        # ── Validations ──────────────────────────────────────────────────────
        errors = []
        if not title:
            errors.append('Task title is required.')
        if not project_id or not project_id.isdigit():
            errors.append('Please select a project.')
        if status not in ('pending', 'completed'):
            status = 'pending'
        if priority not in ('low', 'medium', 'high'):
            priority = 'medium'

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid deadline format.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('tasks/create.html', projects=projects, members=members)

        task = Task(
            title=title,
            description=description,
            project_id=int(project_id),
            assigned_to=int(assigned_to) if assigned_to and assigned_to.isdigit() else None,
            status=status,
            priority=priority,
            deadline=deadline
        )
        db.session.add(task)
        db.session.commit()

        flash(f'Task "{title}" created!', 'success')
        return redirect(url_for('tasks.list_tasks'))

    return render_template('tasks/create.html', projects=projects, members=members)


@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """
    Edit task.
    Admin: can edit all fields.
    Member: can only update status of their own task.
    """
    task = Task.query.get_or_404(task_id)

    # Members can only edit their own tasks
    if not current_user.is_admin() and task.assigned_to != current_user.id:
        flash('You can only edit your own tasks.', 'danger')
        return redirect(url_for('tasks.list_tasks'))

    projects = Project.query.all()
    members = User.query.all()

    if request.method == 'POST':
        if current_user.is_admin():
            # Admin can update all fields
            task.title = request.form.get('title', task.title).strip()
            task.description = request.form.get('description', '').strip()
            project_id = request.form.get('project_id', '')
            if project_id and project_id.isdigit():
                task.project_id = int(project_id)
            assigned_to = request.form.get('assigned_to', '')
            task.assigned_to = int(assigned_to) if assigned_to and assigned_to.isdigit() else None
            task.priority = request.form.get('priority', task.priority)
            deadline_str = request.form.get('deadline', '')
            if deadline_str:
                try:
                    task.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid date format.', 'warning')

        # Both admin and member can update status
        new_status = request.form.get('status', task.status)
        if new_status in ('pending', 'completed'):
            task.status = new_status

        if not task.title:
            flash('Task title cannot be empty.', 'danger')
            return render_template('tasks/edit.html', task=task, projects=projects, members=members)

        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks.list_tasks'))

    return render_template('tasks/edit.html', task=task, projects=projects, members=members)


@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_task(task_id):
    """Admin: delete a task."""
    task = Task.query.get_or_404(task_id)
    title = task.title
    db.session.delete(task)
    db.session.commit()
    flash(f'Task "{title}" deleted.', 'info')
    return redirect(url_for('tasks.list_tasks'))


@tasks_bp.route('/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_status(task_id):
    """Quick toggle: switch task status between pending/completed."""
    task = Task.query.get_or_404(task_id)

    # Members can only toggle their own tasks
    if not current_user.is_admin() and task.assigned_to != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('tasks.list_tasks'))

    task.status = 'completed' if task.status == 'pending' else 'pending'
    db.session.commit()
    flash(f'Task marked as {task.status}.', 'success')
    return redirect(request.referrer or url_for('tasks.list_tasks'))
