from . import db
from .models import (
    Environment, EnvironmentVariable, RequestModel, ActionModel, Snippet, Scenario, ScenarioStep,
    User, DatabaseConnection, TestCase, TestSuite, SeleniumAction, SQLQuery
)
from .services.oracle_client import OracleClient

def seed_demo_data():
    # Create demo users
    admin_user = User(username='admin', email='admin@example.com', role='admin')
    admin_user.set_password('admin123')
    
    demo_user = User(username='demo', email='demo@example.com', role='user')
    demo_user.set_password('demo123')
    
    test_user = User(username='tester', email='tester@example.com', role='user')
    test_user.set_password('test123')
    
    db.session.add_all([admin_user, demo_user, test_user])
    db.session.flush()

    # Environments
    dev = Environment(name='Development', description='Local development env')
    db.session.add(dev)
    db.session.flush()
    vars = [
        EnvironmentVariable(environment_id=dev.id, key='base_url', value='https://jsonplaceholder.typicode.com'),
        EnvironmentVariable(environment_id=dev.id, key='user_name', value='John Doe'),
        EnvironmentVariable(environment_id=dev.id, key='user_email', value='john@example.com'),
    ]
    db.session.add_all(vars)

    # Requests
    r1 = RequestModel(
        name='Get Users', method='GET', url='{{base_url}}/users', headers={'Accept': 'application/json'}, 
        payload_type='json', created_by_id=demo_user.id
    )
    r2 = RequestModel(
        name='Create Post', method='POST', url='{{base_url}}/posts', headers={'Content-Type': 'application/json'},
        body='{"title":"foo","body":"bar","userId":1}', payload_type='json', created_by_id=demo_user.id
    )
    r3 = RequestModel(
        name='XML Request Example', method='POST', url='{{base_url}}/xml-test', 
        headers={'Content-Type': 'application/xml'},
        body='<?xml version="1.0"?><user><name>John</name><email>john@test.com</email></user>', 
        payload_type='xml', created_by_id=demo_user.id
    )
    db.session.add_all([r1, r2, r3])

    # Actions
    a1 = ActionModel(
        name='Activate Dial Through Siebel (Demo)',
        description='Opens browser and verifies title',
        language='python',
        code='from app.services.selenium_actions import run_selenium_action_demo\nrun_selenium_action_demo()',
        created_by_id=demo_user.id
    )
    a2 = ActionModel(
        name='Java Selenium Demo',
        description='Java Selenium automation example',
        language='java',
        code='driver.get("https://example.com");\nString title = driver.getTitle();\nresult.put("page_title", title);',
        created_by_id=demo_user.id
    )
    db.session.add_all([a1, a2])

    # Snippets
    s1 = Snippet(
        name='Set Env from Response', category='api', language='javascript',
        description='Extract id into environment',
        code='var data = pm.response.json; if (data && data.id) { pm.environment.set("last_id", data.id); }',
        tags=['env','extract'], is_public=True, created_by_id=demo_user.id
    )
    s2 = Snippet(
        name='Java Selenium Login', category='selenium', language='java',
        description='Login automation with Java Selenium',
        code='WebElement username = driver.findElement(By.id("username"));\nusername.sendKeys("testuser");\nWebElement password = driver.findElement(By.id("password"));\npassword.sendKeys("testpass");\ndriver.findElement(By.id("login-btn")).click();',
        tags=['selenium','login','automation'], is_public=True, created_by_id=demo_user.id
    )
    s3 = Snippet(
        name='Oracle User Query', category='database', language='sql',
        description='Get active users from Oracle database',
        code='SELECT user_id, username, email, created_date\nFROM users\nWHERE status = \'ACTIVE\'\nAND created_date >= SYSDATE - 30\nORDER BY created_date DESC',
        tags=['oracle','users','database'], is_public=True, created_by_id=demo_user.id
    )
    s4 = Snippet(
        name='API Response Validator', category='utility', language='javascript',
        description='Validate API response structure',
        code='function validateResponse(response, expectedSchema) {\n  for (let key in expectedSchema) {\n    if (!(key in response)) {\n      throw new Error(`Missing key: ${key}`);\n    }\n  }\n  return true;\n}',
        tags=['validation','api','testing'], is_public=False, created_by_id=demo_user.id
    )
    db.session.add_all([s1, s2, s3, s4])

    # Database Connections
    oracle_client = OracleClient()
    demo_password = oracle_client.encrypt_password('demo_password')
    
    db1 = DatabaseConnection(
        name='Demo Oracle DB',
        db_type='oracle',
        host='localhost',
        port=1521,
        database_name='XE',
        username='demo_user',
        password=demo_password,
        created_by_id=demo_user.id
    )
    db.session.add(db1)

    # Selenium Actions
    sel1 = SeleniumAction(
        name='Login Test',
        description='Automated login test with Java Selenium',
        browser='chrome',
        language='java',
        code='driver.get("https://example.com/login");\nWebElement user = driver.findElement(By.id("username"));\nuser.sendKeys("testuser");\nWebElement pass = driver.findElement(By.id("password"));\npass.sendKeys("testpass");\ndriver.findElement(By.xpath("//button[@type=\'submit\']")).click();',
        dependencies=[{"groupId": "org.seleniumhq.selenium", "artifactId": "selenium-java", "version": "4.15.0"}],
        created_by_id=demo_user.id
    )
    db.session.add(sel1)

    # SQL Queries
    sql1 = SQLQuery(
        name='Get Active Users',
        description='Retrieve all active users from the system',
        query='SELECT user_id, username, email, status, created_date FROM users WHERE status = \'ACTIVE\' ORDER BY created_date DESC',
        query_type='select',
        database_connection_id=1,
        created_by_id=demo_user.id
    )
    db.session.add(sql1)

    # Test Cases
    tc1 = TestCase(
        name='API User Creation Test',
        description='Test user creation via API endpoint',
        test_type='api',
        test_data={
            'endpoint': '/api/users',
            'method': 'POST',
            'payload': {'name': 'Test User', 'email': 'test@example.com'},
            'expected_status': 201
        },
        expected_result='User created successfully with valid ID',
        is_public=True,
        created_by_id=demo_user.id
    )
    
    tc2 = TestCase(
        name='Login Selenium Test',
        description='Automated login functionality test',
        test_type='selenium',
        test_data={
            'url': 'https://example.com/login',
            'username': 'testuser',
            'password': 'testpass',
            'success_indicator': '.dashboard'
        },
        expected_result='User successfully logs in and reaches dashboard',
        is_public=False,
        created_by_id=demo_user.id
    )
    
    tc3 = TestCase(
        name='Database Query Test',
        description='Test database connection and query execution',
        test_type='database',
        test_data={
            'connection_id': 1,
            'query': 'SELECT COUNT(*) as user_count FROM users WHERE status = \'ACTIVE\'',
            'expected_min_count': 1
        },
        expected_result='Query returns at least 1 active user',
        is_public=True,
        created_by_id=demo_user.id
    )
    
    db.session.add_all([tc1, tc2, tc3])
    db.session.flush()

    # Test Suite
    ts1 = TestSuite(
        name='User Management Test Suite',
        description='Complete test suite for user management functionality',
        is_public=True,
        created_by_id=demo_user.id
    )
    db.session.add(ts1)
    db.session.flush()

    # Add test cases to suite
    suite_cases = [
        TestSuiteCase(test_suite_id=ts1.id, test_case_id=tc1.id, order=1),
        TestSuiteCase(test_suite_id=ts1.id, test_case_id=tc2.id, order=2),
        TestSuiteCase(test_suite_id=ts1.id, test_case_id=tc3.id, order=3)
    ]
    db.session.add_all(suite_cases)

    # Scenarios
    sc = Scenario(
        name='JSONPlaceholder Flow', 
        description='Demo flow using JSONPlaceholder',
        is_public=True,
        created_by_id=demo_user.id
    )
    db.session.add(sc)
    db.session.flush()
    
    step1 = ScenarioStep(scenario_id=sc.id, order=1, step_type='request', ref_id=1)
    step2 = ScenarioStep(scenario_id=sc.id, order=2, step_type='action', ref_id=1)
    db.session.add_all([step1, step2])

    db.session.commit()
