from datetime import datetime
from typing import Optional
from . import db
from sqlalchemy.dialects.postgresql import JSONB

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
    payload_type = db.Column(db.String(10), default='json')  # json|xml
    pre_script = db.Column(db.Text, default='')  # JavaScript
    post_script = db.Column(db.Text, default='')  # JavaScript

class ActionModel(db.Model, TimestampMixin):
    __tablename__ = 'action'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(255))
    language = db.Column(db.String(20), default='python')
    code = db.Column(db.Text, nullable=False)

class Snippet(db.Model, TimestampMixin):
    __tablename__ = 'snippet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(255))
    category = db.Column(db.String(50), default='utility')
    language = db.Column(db.String(20), default='javascript')
    code = db.Column(db.Text, nullable=False)
    tags = db.Column(JSONB, default=list)

class Scenario(db.Model, TimestampMixin):
    __tablename__ = 'scenario'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(255))
    steps = db.relationship('ScenarioStep', backref='scenario', cascade='all, delete-orphan', order_by='ScenarioStep.order')

class ScenarioStep(db.Model, TimestampMixin):
    __tablename__ = 'scenario_step'
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenario.id', ondelete='CASCADE'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    step_type = db.Column(db.String(20), nullable=False)  # request|action
    ref_id = db.Column(db.Integer, nullable=False)  # ID of RequestModel or ActionModel
