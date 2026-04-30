"""
routes/users.py - User management blueprint (Admin only)
Lists all users and allows role/account management.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User
from functools import wraps

users_bp = Blueprint('users', __name__, url_prefix='/users')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


@users_bp.route('/')
@login_required
@admin_required
def list_users():
    """Admin: view all registered users."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users/list.html', users=users)


@users_bp.route('/<int:user_id>/toggle-role', methods=['POST'])
@login_required
@admin_required
def toggle_role(user_id):
    """Admin: switch a user between admin and member roles."""
    user = User.query.get_or_404(user_id)

    # Prevent admin from removing their own admin role
    if user.id == current_user.id:
        flash("You can't change your own role.", 'warning')
        return redirect(url_for('users.list_users'))

    user.role = 'member' if user.role == 'admin' else 'admin'
    db.session.commit()
    flash(f'{user.username} is now a {user.role}.', 'success')
    return redirect(url_for('users.list_users'))


@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Admin: delete a user account."""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You can't delete your own account.", 'warning')
        return redirect(url_for('users.list_users'))

    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{username}" deleted.', 'info')
    return redirect(url_for('users.list_users'))
