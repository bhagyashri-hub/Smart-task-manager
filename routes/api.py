"""
routes/api.py - REST API Blueprint
Provides JSON endpoints for users, projects, and tasks.
All endpoints require login (session-based auth).

Endpoints:
  GET    /api/users
  GET    /api/projects
  POST   /api/projects
  GET    /api/projects/<id>
  DELETE /api/projects/<id>
  GET    /api/tasks
  POST   /api/tasks
  GET    /api/tasks/<id>
  PUT    /api/tasks/<id>
  DELETE /api/tasks/<id>
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, User, Project, Task
from datetime import datetime

api_bp = Blueprint('api', __name__)


def admin_only():
    """Helper: return 403 JSON if current user is not admin."""
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    return None


# ── Users ──────────────────────────────────────────────────────────────────────

@api_bp.route('/users', methods=['GET'])
@login_required
def api_users():
    """GET /api/users - List all users (admin only)"""
    err = admin_only()
    if err:
        return err

    users = User.query.all()
    data = [{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'created_at': u.created_at.isoformat()
    } for u in users]
    return jsonify({'users': data, 'total': len(data)})


# ── Projects ───────────────────────────────────────────────────────────────────

@api_bp.route('/projects', methods=['GET'])
@login_required
def api_list_projects():
    """GET /api/projects - List projects"""
    if current_user.is_admin():
        projects = Project.query.all()
    else:
        ids = [t.project_id for t in Task.query.filter_by(assigned_to=current_user.id).all()]
        projects = Project.query.filter(Project.id.in_(ids)).all()

    data = [{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'created_by': p.creator.username if p.creator else None,
        'total_tasks': p.total_tasks,
        'completed_tasks': p.completed_tasks,
        'progress_percent': p.progress_percent,
        'created_at': p.created_at.isoformat()
    } for p in projects]
    return jsonify({'projects': data, 'total': len(data)})


@api_bp.route('/projects', methods=['POST'])
@login_required
def api_create_project():
    """POST /api/projects - Create a new project (admin only)"""
    err = admin_only()
    if err:
        return err

    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Project name is required'}), 400

    project = Project(
        name=data['name'].strip(),
        description=data.get('description', ''),
        created_by=current_user.id
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({'message': 'Project created', 'id': project.id}), 201


@api_bp.route('/projects/<int:project_id>', methods=['GET'])
@login_required
def api_get_project(project_id):
    """GET /api/projects/<id> - Get project detail"""
    project = Project.query.get_or_404(project_id)
    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'total_tasks': project.total_tasks,
        'completed_tasks': project.completed_tasks,
        'pending_tasks': project.pending_tasks,
        'progress_percent': project.progress_percent
    })


@api_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@login_required
def api_delete_project(project_id):
    """DELETE /api/projects/<id> - Delete project (admin only)"""
    err = admin_only()
    if err:
        return err

    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': f'Project "{project.name}" deleted'})


# ── Tasks ──────────────────────────────────────────────────────────────────────

@api_bp.route('/tasks', methods=['GET'])
@login_required
def api_list_tasks():
    """GET /api/tasks - List tasks (filtered by role)"""
    if current_user.is_admin():
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(assigned_to=current_user.id).all()

    return jsonify({'tasks': [t.to_dict() for t in tasks], 'total': len(tasks)})


@api_bp.route('/tasks', methods=['POST'])
@login_required
def api_create_task():
    """POST /api/tasks - Create a task (admin only)"""
    err = admin_only()
    if err:
        return err

    data = request.get_json()
    if not data or not data.get('title') or not data.get('project_id'):
        return jsonify({'error': 'title and project_id are required'}), 400

    deadline = None
    if data.get('deadline'):
        try:
            deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid deadline format. Use YYYY-MM-DD'}), 400

    task = Task(
        title=data['title'].strip(),
        description=data.get('description', ''),
        project_id=data['project_id'],
        assigned_to=data.get('assigned_to'),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        deadline=deadline
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Task created', 'task': task.to_dict()}), 201


@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def api_get_task(task_id):
    """GET /api/tasks/<id> - Get task details"""
    task = Task.query.get_or_404(task_id)
    if not current_user.is_admin() and task.assigned_to != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    return jsonify(task.to_dict())


@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def api_update_task(task_id):
    """PUT /api/tasks/<id> - Update task"""
    task = Task.query.get_or_404(task_id)
    if not current_user.is_admin() and task.assigned_to != current_user.id:
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if current_user.is_admin():
        if 'title' in data:
            task.title = data['title'].strip()
        if 'description' in data:
            task.description = data['description']
        if 'project_id' in data:
            task.project_id = data['project_id']
        if 'assigned_to' in data:
            task.assigned_to = data['assigned_to']
        if 'priority' in data and data['priority'] in ('low', 'medium', 'high'):
            task.priority = data['priority']
        if 'deadline' in data:
            try:
                task.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid deadline format'}), 400

    # Both roles can update status
    if 'status' in data and data['status'] in ('pending', 'completed'):
        task.status = data['status']

    db.session.commit()
    return jsonify({'message': 'Task updated', 'task': task.to_dict()})


@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def api_delete_task(task_id):
    """DELETE /api/tasks/<id> - Delete task (admin only)"""
    err = admin_only()
    if err:
        return err

    task = Task.query.get_or_404(task_id)
    title = task.title
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': f'Task "{title}" deleted'})


# ── Stats ──────────────────────────────────────────────────────────────────────

@api_bp.route('/stats', methods=['GET'])
@login_required
def api_stats():
    """GET /api/stats - Get dashboard stats"""
    if current_user.is_admin():
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(assigned_to=current_user.id).all()

    return jsonify({
        'total': len(tasks),
        'completed': sum(1 for t in tasks if t.status == 'completed'),
        'pending': sum(1 for t in tasks if t.status == 'pending'),
        'overdue': sum(1 for t in tasks if t.is_overdue),
        'total_projects': Project.query.count() if current_user.is_admin() else None,
        'total_users': User.query.count() if current_user.is_admin() else None
    })
