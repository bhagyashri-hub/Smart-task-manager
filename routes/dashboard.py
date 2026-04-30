"""
routes/dashboard.py - Dashboard blueprint
Shows task summary cards and task table for current user.
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Task, Project, User
from datetime import date

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    Main dashboard:
    - Admin: sees ALL tasks and projects overview
    - Member: sees only their assigned tasks
    """
    today = date.today()

    if current_user.is_admin():
        # Admin sees all tasks
        all_tasks = Task.query.all()
        projects = Project.query.all()
        total_users = User.query.count()
    else:
        # Member sees only their assigned tasks
        all_tasks = Task.query.filter_by(assigned_to=current_user.id).all()
        projects = []
        total_users = 0

    # Compute stats
    total = len(all_tasks)
    completed = sum(1 for t in all_tasks if t.status == 'completed')
    pending = sum(1 for t in all_tasks if t.status == 'pending')
    overdue = sum(1 for t in all_tasks if t.is_overdue)

    # Recent 10 tasks for the table
    if current_user.is_admin():
        recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(10).all()
    else:
        recent_tasks = Task.query.filter_by(
            assigned_to=current_user.id
        ).order_by(Task.created_at.desc()).limit(10).all()

    return render_template(
        'dashboard.html',
        total=total,
        completed=completed,
        pending=pending,
        overdue=overdue,
        recent_tasks=recent_tasks,
        projects=projects,
        total_users=total_users,
        today=today
    )
