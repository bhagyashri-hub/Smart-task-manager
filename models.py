"""
models.py - Database models for Smart Team Task Manager
Defines User, Project, and Task tables using SQLAlchemy ORM
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

# Initialize SQLAlchemy (will be bound to app in app.py)
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User model - stores all registered users.
    Roles: 'admin' can manage everything, 'member' can view/update their tasks.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')  # 'admin' or 'member'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    tasks_assigned = db.relationship('Task', backref='assignee', lazy=True, foreign_keys='Task.assigned_to')
    projects_created = db.relationship('Project', backref='creator', lazy=True)

    def set_password(self, password):
        """Hash and store password securely"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Helper to check if user has admin role"""
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Project(db.Model):
    """
    Project model - a container for tasks.
    Only admins can create/delete projects.
    """
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: one project has many tasks
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')

    @property
    def total_tasks(self):
        return len(self.tasks)

    @property
    def completed_tasks(self):
        return sum(1 for t in self.tasks if t.status == 'completed')

    @property
    def pending_tasks(self):
        return sum(1 for t in self.tasks if t.status == 'pending')

    @property
    def progress_percent(self):
        if self.total_tasks == 0:
            return 0
        return int((self.completed_tasks / self.total_tasks) * 100)

    def __repr__(self):
        return f'<Project {self.name}>'


class Task(db.Model):
    """
    Task model - the core unit of work.
    Can be assigned to users, tracked by status and priority.
    """
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Status: pending or completed
    status = db.Column(db.String(20), nullable=False, default='pending')

    # Priority: low, medium, high
    priority = db.Column(db.String(20), nullable=False, default='medium')

    # Deadline date (optional but shown as overdue if past)
    deadline = db.Column(db.Date, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def is_overdue(self):
        """Returns True if deadline is in the past and task isn't completed"""
        if self.deadline and self.status == 'pending':
            return self.deadline < date.today()
        return False

    @property
    def priority_badge(self):
        """Returns Bootstrap badge color for priority"""
        colors = {'low': 'success', 'medium': 'warning', 'high': 'danger'}
        return colors.get(self.priority, 'secondary')

    @property
    def status_badge(self):
        """Returns Bootstrap badge color for status"""
        return 'success' if self.status == 'completed' else 'secondary'

    def to_dict(self):
        """Serialize task to dict for REST API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'assigned_to': self.assigned_to,
            'assigned_username': self.assignee.username if self.assignee else None,
            'status': self.status,
            'priority': self.priority,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'is_overdue': self.is_overdue,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Task {self.title} [{self.status}]>'
