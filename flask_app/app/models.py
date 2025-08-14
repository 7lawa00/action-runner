from datetime import datetime
from typing import Optional
from . import db
from sqlalchemy.dialects.postgresql import JSONB
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Environment(db.Model, TimestampMixin):
    __tablename__ = 'environment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(255))
    variables = db.relationship('EnvironmentVariable', backref='environment', cascade='all, delete-orphan')

class EnvironmentVariable(db.Model, TimestampMixin):
    __tablename__ = 'environment_variable'
    id = db.Column(db.Integer, primary_key=True)
    environment_id = db.Column(db.Integer, db.ForeignKey('environment.id', ondelete='CASCADE'), nullable=False)
    key = db.Column(db.String(120), nullable=False)
    value = db.Column(db.Text, default='')
    is_secret = db.Column(db.Boolean, default=False)

class RequestModel(db.Model, TimestampMixin):
    __tablename__ = 'request'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=False, default='GET')
    url = db.Column(db.Text, nullable=False)
    headers = db.Column(JSONB, default=dict)
    body = db.Column(db.Text, default='')
    payload_type = db.Column(db.String(10), default='json')  # json|xml|form|text
    pre_script = db.Column(db.Text, default='')  # JavaScript
    post_script = db.Column(db.Text, default='')  # JavaScript
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class ActionModel(db.Model, TimestampMixin):
    __tablename__ = 'action'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(255))
    language = db.Column(db.String(20), default='python')  # python|java|javascript
    code = db.Column(db.Text, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Snippet(db.Model, TimestampMixin):
    __tablename__ = 'snippet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(255))
    category = db.Column(db.String(50), default='utility')  # utility|selenium|database|api
    language = db.Column(db.String(20), default='javascript')  # javascript|java|python|sql
    code = db.Column(db.Text, nullable=False)
    tags = db.Column(JSONB, default=list)
    is_public = db.Column(db.Boolean, default=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Scenario(db.Model, TimestampMixin):
    __tablename__ = 'scenario'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(255))
    is_public = db.Column(db.Boolean, default=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    steps = db.relationship('ScenarioStep', backref='scenario', cascade='all, delete-orphan', order_by='ScenarioStep.order')

class ScenarioStep(db.Model, TimestampMixin):
    __tablename__ = 'scenario_step'
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenario.id', ondelete='CASCADE'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    step_type = db.Column(db.String(20), nullable=False)  # request|action
    ref_id = db.Column(db.Integer, nullable=False)  # ID of RequestModel or ActionModel

# User Authentication and Roles
class User(UserMixin, db.Model, TimestampMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin|user|viewer
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    requests = db.relationship('RequestModel', backref='created_by', lazy=True)
    actions = db.relationship('ActionModel', backref='created_by', lazy=True)
    snippets = db.relationship('Snippet', backref='created_by', lazy=True)
    scenarios = db.relationship('Scenario', backref='created_by', lazy=True)
    test_cases = db.relationship('TestCase', backref='created_by', lazy=True)
    test_suites = db.relationship('TestSuite', backref='created_by', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Database Connections
class DatabaseConnection(db.Model, TimestampMixin):
    __tablename__ = 'database_connection'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    db_type = db.Column(db.String(50), nullable=False)  # oracle|mysql|postgresql|mssql
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, default=1521)
    database_name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.Text, nullable=False)  # Should be encrypted
    connection_string = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Test Cases and Suites
class TestCase(db.Model, TimestampMixin):
    __tablename__ = 'test_case'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    test_type = db.Column(db.String(50), default='api')  # api|selenium|database
    test_data = db.Column(JSONB, default=dict)  # Test configuration
    expected_result = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    suite_tests = db.relationship('TestSuiteCase', backref='test_case', cascade='all, delete-orphan')
    shared_with = db.relationship('TestCaseShare', backref='test_case', cascade='all, delete-orphan')

class TestSuite(db.Model, TimestampMixin):
    __tablename__ = 'test_suite'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    test_cases = db.relationship('TestSuiteCase', backref='test_suite', cascade='all, delete-orphan')
    shared_with = db.relationship('TestSuiteShare', backref='test_suite', cascade='all, delete-orphan')

class TestSuiteCase(db.Model, TimestampMixin):
    __tablename__ = 'test_suite_case'
    id = db.Column(db.Integer, primary_key=True)
    test_suite_id = db.Column(db.Integer, db.ForeignKey('test_suite.id', ondelete='CASCADE'), nullable=False)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id', ondelete='CASCADE'), nullable=False)
    order = db.Column(db.Integer, nullable=False)

# Sharing Models
class TestCaseShare(db.Model, TimestampMixin):
    __tablename__ = 'test_case_share'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id', ondelete='CASCADE'), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    permission = db.Column(db.String(20), default='read')  # read|write|execute

class TestSuiteShare(db.Model, TimestampMixin):
    __tablename__ = 'test_suite_share'
    id = db.Column(db.Integer, primary_key=True)
    test_suite_id = db.Column(db.Integer, db.ForeignKey('test_suite.id', ondelete='CASCADE'), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    permission = db.Column(db.String(20), default='read')  # read|write|execute

# Selenium Actions and Java Support
class SeleniumAction(db.Model, TimestampMixin):
    __tablename__ = 'selenium_action'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    browser = db.Column(db.String(50), default='chrome')  # chrome|firefox|edge
    language = db.Column(db.String(20), default='java')  # java|python|javascript
    code = db.Column(db.Text, nullable=False)
    dependencies = db.Column(JSONB, default=list)  # Required libraries/dependencies
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# SQL Query Templates
class SQLQuery(db.Model, TimestampMixin):
    __tablename__ = 'sql_query'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    query = db.Column(db.Text, nullable=False)
    query_type = db.Column(db.String(20), default='select')  # select|insert|update|delete
    database_connection_id = db.Column(db.Integer, db.ForeignKey('database_connection.id'), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Update existing models to include user relationships
# Add foreign keys to existing models
