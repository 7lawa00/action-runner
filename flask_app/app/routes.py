import json
import os
from flask import Blueprint, jsonify, render_template, request
from . import db
from .models import (
    RequestModel,
    ActionModel,
    Environment,
    EnvironmentVariable,
    Snippet,
    Scenario,
    ScenarioStep,
)
from .services.http_client import send_http_request
from .services.selenium_actions import run_selenium_action_demo
from .services.trello import TrelloClient

api_bp = Blueprint('api', __name__)

@api_bp.route('/')
def index():
    return render_template('index.html')

# Environments
@api_bp.get('/api/environments')
def list_environments():
    envs = Environment.query.all()
    return jsonify([
        {
            'id': e.id,
            'name': e.name,
            'description': e.description,
            'variables': [{'key': v.key, 'value': v.value, 'is_secret': v.is_secret} for v in e.variables]
        }
        for e in envs
    ])

@api_bp.post('/api/environments')
def create_environment():
    data = request.get_json() or {}
    env = Environment(name=data.get('name', 'New Environment'), description=data.get('description', ''))
    db.session.add(env)
    db.session.commit()
    return jsonify({'id': env.id}), 201

# Requests
@api_bp.get('/api/requests')
def list_requests():
    rows = RequestModel.query.order_by(RequestModel.created_at.desc()).all()
    return jsonify([
        {
            'id': r.id,
            'name': r.name,
            'method': r.method,
            'url': r.url,
            'headers': r.headers,
            'body': r.body,
            'payload_type': r.payload_type
        } for r in rows
    ])

@api_bp.post('/api/requests')
def create_request():
    data = request.get_json() or {}
    r = RequestModel(
        name=data.get('name', 'New Request'),
        method=data.get('method', 'GET'),
        url=data.get('url', ''),
        headers=data.get('headers', {}),
        body=data.get('body', ''),
        payload_type=data.get('payload_type', 'json'),
        pre_script=data.get('pre_script', ''),
        post_script=data.get('post_script', ''),
    )
    db.session.add(r)
    db.session.commit()
    return jsonify({'id': r.id}), 201

@api_bp.post('/api/requests/<int:req_id>/send')
def send_request(req_id: int):
    data = request.get_json() or {}
    env_id = data.get('environment_id')
    req = RequestModel.query.get_or_404(req_id)
    env = Environment.query.get(env_id) if env_id else None
    result = send_http_request(req, env)
    return jsonify(result)

# Actions
@api_bp.get('/api/actions')
def list_actions():
    rows = ActionModel.query.all()
    return jsonify([
        {'id': a.id, 'name': a.name, 'description': a.description, 'language': a.language}
        for a in rows
    ])

@api_bp.post('/api/actions')
def create_action():
    data = request.get_json() or {}
    a = ActionModel(
        name=data.get('name', 'New Action'),
        description=data.get('description', ''),
        language=data.get('language', 'python'),
        code=data.get('code', 'print("Hello from action")')
    )
    db.session.add(a)
    db.session.commit()
    return jsonify({'id': a.id}), 201

@api_bp.post('/api/actions/<int:action_id>/run')
def run_action(action_id: int):
    # For demo, run a Selenium login demo regardless of action code
    result = run_selenium_action_demo()
    return jsonify(result)

# Scenarios
@api_bp.get('/api/scenarios')
def list_scenarios():
    rows = Scenario.query.all()
    return jsonify([
        {
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'steps': [
                {
                    'id': st.id,
                    'order': st.order,
                    'step_type': st.step_type,
                    'ref_id': st.ref_id
                } for st in s.steps
            ]
        } for s in rows
    ])

@api_bp.post('/api/scenarios/<int:scenario_id>/run')
def run_scenario(scenario_id: int):
    s = Scenario.query.get_or_404(scenario_id)
    results = []
    env = Environment.query.first()
    for step in s.steps:
        if step.step_type == 'request':
            req = RequestModel.query.get(step.ref_id)
            if req:
                results.append({'step': step.id, 'result': send_http_request(req, env)})
        elif step.step_type == 'action':
            results.append({'step': step.id, 'result': run_selenium_action_demo()})
    return jsonify({'scenario_id': s.id, 'results': results})

# Trello integration with fallback
@api_bp.get('/api/trello/boards')
def trello_boards():
    client = TrelloClient()
    return jsonify(client.get_boards())
