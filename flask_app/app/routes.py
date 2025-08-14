import json
import os
from flask import Blueprint, jsonify, render_template, request, session
from flask_login import login_required, current_user
from . import db
from .models import (
    RequestModel,
    ActionModel,
    Environment,
    EnvironmentVariable,
    Snippet,
    Scenario,
    ScenarioStep,
    User,
    DatabaseConnection,
    TestCase,
    TestSuite,
    TestSuiteCase,
    TestCaseShare,
    TestSuiteShare,
    SeleniumAction,
    SQLQuery,
)
from .services.http_client import send_http_request
from .services.selenium_actions import run_selenium_action_demo
from .services.java_selenium import JavaSeleniumRunner
from .services.oracle_client import OracleClient
from .services.trello import TrelloClient
from .services.auth import AuthService, require_auth, require_admin

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

@api_bp.put('/api/requests/<int:req_id>')
def update_request(req_id: int):
    data = request.get_json() or {}
    req = RequestModel.query.get_or_404(req_id)
    req.name = data.get('name', req.name)
    req.method = data.get('method', req.method)
    req.url = data.get('url', req.url)
    req.headers = data.get('headers', req.headers)
    req.body = data.get('body', req.body)
    req.payload_type = data.get('payload_type', req.payload_type)
    req.pre_script = data.get('pre_script', req.pre_script)
    req.post_script = data.get('post_script', req.post_script)
    db.session.commit()
    return jsonify({'id': req.id})

@api_bp.delete('/api/requests/<int:req_id>')
def delete_request(req_id: int):
    req = RequestModel.query.get_or_404(req_id)
    db.session.delete(req)
    db.session.commit()
    return jsonify({'success': True})

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

# Authentication Routes
@api_bp.post('/api/auth/register')
def register():
    data = request.get_json() or {}
    result = AuthService.register_user(
        data.get('username', ''),
        data.get('email', ''),
        data.get('password', ''),
        data.get('role', 'user')
    )
    return jsonify(result), 201 if result['success'] else 400

@api_bp.post('/api/auth/login')
def login():
    data = request.get_json() or {}
    result = AuthService.authenticate_user(
        data.get('username', ''),
        data.get('password', '')
    )
    return jsonify(result), 200 if result['success'] else 401

@api_bp.post('/api/auth/logout')
def logout():
    result = AuthService.logout_user_session()
    return jsonify(result)

@api_bp.get('/api/auth/me')
@require_auth
def get_current_user():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role
    })

# Snippets Management
@api_bp.get('/api/snippets')
def list_snippets():
    if current_user.is_authenticated:
        # Show user's snippets + public snippets
        snippets = Snippet.query.filter(
            (Snippet.created_by_id == current_user.id) | (Snippet.is_public == True)
        ).all()
    else:
        # Show only public snippets
        snippets = Snippet.query.filter_by(is_public=True).all()
    
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'category': s.category,
        'language': s.language,
        'code': s.code,
        'tags': s.tags,
        'is_public': s.is_public,
        'created_by': s.created_by.username if s.created_by else 'System'
    } for s in snippets])

@api_bp.post('/api/snippets')
@require_auth
def create_snippet():
    data = request.get_json() or {}
    snippet = Snippet(
        name=data.get('name', 'New Snippet'),
        description=data.get('description', ''),
        category=data.get('category', 'utility'),
        language=data.get('language', 'javascript'),
        code=data.get('code', ''),
        tags=data.get('tags', []),
        is_public=data.get('is_public', False),
        created_by_id=current_user.id
    )
    db.session.add(snippet)
    db.session.commit()
    return jsonify({'id': snippet.id}), 201

@api_bp.put('/api/snippets/<int:snippet_id>')
@require_auth
def update_snippet(snippet_id: int):
    snippet = Snippet.query.filter_by(id=snippet_id, created_by_id=current_user.id).first_or_404()
    data = request.get_json() or {}
    
    snippet.name = data.get('name', snippet.name)
    snippet.description = data.get('description', snippet.description)
    snippet.category = data.get('category', snippet.category)
    snippet.language = data.get('language', snippet.language)
    snippet.code = data.get('code', snippet.code)
    snippet.tags = data.get('tags', snippet.tags)
    snippet.is_public = data.get('is_public', snippet.is_public)
    
    db.session.commit()
    return jsonify({'id': snippet.id})

@api_bp.delete('/api/snippets/<int:snippet_id>')
@require_auth
def delete_snippet(snippet_id: int):
    snippet = Snippet.query.filter_by(id=snippet_id, created_by_id=current_user.id).first_or_404()
    db.session.delete(snippet)
    db.session.commit()
    return jsonify({'success': True})

# Database Connections
@api_bp.get('/api/database-connections')
@require_auth
def list_database_connections():
    connections = DatabaseConnection.query.filter_by(created_by_id=current_user.id).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'db_type': c.db_type,
        'host': c.host,
        'port': c.port,
        'database_name': c.database_name,
        'username': c.username,
        'is_active': c.is_active
    } for c in connections])

@api_bp.post('/api/database-connections')
@require_auth
def create_database_connection():
    data = request.get_json() or {}
    oracle_client = OracleClient()
    
    # Encrypt password
    encrypted_password = oracle_client.encrypt_password(data.get('password', ''))
    
    connection = DatabaseConnection(
        name=data.get('name', 'New Connection'),
        db_type=data.get('db_type', 'oracle'),
        host=data.get('host', ''),
        port=data.get('port', 1521),
        database_name=data.get('database_name', ''),
        username=data.get('username', ''),
        password=encrypted_password,
        created_by_id=current_user.id
    )
    
    db.session.add(connection)
    db.session.commit()
    return jsonify({'id': connection.id}), 201

@api_bp.post('/api/database-connections/<int:conn_id>/test')
@require_auth
def test_database_connection(conn_id: int):
    connection = DatabaseConnection.query.filter_by(id=conn_id, created_by_id=current_user.id).first_or_404()
    oracle_client = OracleClient()
    
    config = {
        'host': connection.host,
        'port': connection.port,
        'service_name': connection.database_name,
        'username': connection.username,
        'password': connection.password
    }
    
    result = oracle_client.test_connection(config)
    return jsonify(result)

@api_bp.post('/api/database-connections/<int:conn_id>/execute')
@require_auth
def execute_sql_query(conn_id: int):
    connection = DatabaseConnection.query.filter_by(id=conn_id, created_by_id=current_user.id).first_or_404()
    data = request.get_json() or {}
    query = data.get('query', '')
    
    if not query:
        return jsonify({'success': False, 'error': 'Query is required'}), 400
    
    oracle_client = OracleClient()
    config = {
        'host': connection.host,
        'port': connection.port,
        'service_name': connection.database_name,
        'username': connection.username,
        'password': connection.password
    }
    
    result = oracle_client.execute_query(config, query, data.get('parameters'))
    return jsonify(result)

# Java Selenium Actions
@api_bp.get('/api/selenium-actions')
@require_auth
def list_selenium_actions():
    actions = SeleniumAction.query.filter_by(created_by_id=current_user.id).all()
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'description': a.description,
        'browser': a.browser,
        'language': a.language,
        'dependencies': a.dependencies
    } for a in actions])

@api_bp.post('/api/selenium-actions')
@require_auth
def create_selenium_action():
    data = request.get_json() or {}
    action = SeleniumAction(
        name=data.get('name', 'New Selenium Action'),
        description=data.get('description', ''),
        browser=data.get('browser', 'chrome'),
        language=data.get('language', 'java'),
        code=data.get('code', ''),
        dependencies=data.get('dependencies', []),
        created_by_id=current_user.id
    )
    db.session.add(action)
    db.session.commit()
    return jsonify({'id': action.id}), 201

@api_bp.post('/api/selenium-actions/<int:action_id>/execute')
@require_auth
def execute_selenium_action(action_id: int):
    action = SeleniumAction.query.filter_by(id=action_id, created_by_id=current_user.id).first_or_404()
    
    if action.language == 'java':
        runner = JavaSeleniumRunner()
        result = runner.execute_java_selenium(action.code, action.dependencies)
    else:
        # Fall back to Python Selenium
        result = run_selenium_action_demo()
    
    return jsonify(result)

# Test Cases and Suites
@api_bp.get('/api/test-cases')
@require_auth
def list_test_cases():
    # User's test cases + public ones + shared with user
    user_cases = TestCase.query.filter_by(created_by_id=current_user.id).all()
    public_cases = TestCase.query.filter_by(is_public=True).all()
    shared_cases = db.session.query(TestCase).join(TestCaseShare).filter(
        TestCaseShare.shared_with_id == current_user.id
    ).all()
    
    all_cases = list(set(user_cases + public_cases + shared_cases))
    
    return jsonify([{
        'id': tc.id,
        'name': tc.name,
        'description': tc.description,
        'test_type': tc.test_type,
        'is_public': tc.is_public,
        'created_by': tc.created_by.username,
        'can_edit': tc.created_by_id == current_user.id
    } for tc in all_cases])

@api_bp.post('/api/test-cases')
@require_auth
def create_test_case():
    data = request.get_json() or {}
    test_case = TestCase(
        name=data.get('name', 'New Test Case'),
        description=data.get('description', ''),
        test_type=data.get('test_type', 'api'),
        test_data=data.get('test_data', {}),
        expected_result=data.get('expected_result', ''),
        is_public=data.get('is_public', False),
        created_by_id=current_user.id
    )
    db.session.add(test_case)
    db.session.commit()
    return jsonify({'id': test_case.id}), 201

@api_bp.post('/api/test-cases/<int:case_id>/share')
@require_auth
def share_test_case(case_id: int):
    test_case = TestCase.query.filter_by(id=case_id, created_by_id=current_user.id).first_or_404()
    data = request.get_json() or {}
    
    username = data.get('username', '')
    permission = data.get('permission', 'read')
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Check if already shared
    existing = TestCaseShare.query.filter_by(
        test_case_id=case_id,
        shared_with_id=user.id
    ).first()
    
    if existing:
        existing.permission = permission
    else:
        share = TestCaseShare(
            test_case_id=case_id,
            shared_with_id=user.id,
            permission=permission
        )
        db.session.add(share)
    
    db.session.commit()
    return jsonify({'success': True})

# Test Suites
@api_bp.get('/api/test-suites')
@require_auth
def list_test_suites():
    # User's test suites + public ones + shared with user
    user_suites = TestSuite.query.filter_by(created_by_id=current_user.id).all()
    public_suites = TestSuite.query.filter_by(is_public=True).all()
    shared_suites = db.session.query(TestSuite).join(TestSuiteShare).filter(
        TestSuiteShare.shared_with_id == current_user.id
    ).all()
    
    all_suites = list(set(user_suites + public_suites + shared_suites))
    
    return jsonify([{
        'id': ts.id,
        'name': ts.name,
        'description': ts.description,
        'is_public': ts.is_public,
        'created_by': ts.created_by.username,
        'test_count': len(ts.test_cases),
        'can_edit': ts.created_by_id == current_user.id
    } for ts in all_suites])

@api_bp.post('/api/test-suites')
@require_auth
def create_test_suite():
    data = request.get_json() or {}
    test_suite = TestSuite(
        name=data.get('name', 'New Test Suite'),
        description=data.get('description', ''),
        is_public=data.get('is_public', False),
        created_by_id=current_user.id
    )
    db.session.add(test_suite)
    db.session.commit()
    return jsonify({'id': test_suite.id}), 201

# Trello integration with fallback
@api_bp.get('/api/trello/boards')
def trello_boards():
    client = TrelloClient()
    return jsonify(client.get_boards())
