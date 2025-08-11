from . import db
from .models import Environment, EnvironmentVariable, RequestModel, ActionModel, Snippet, Scenario, ScenarioStep

def seed_demo_data():
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
        name='Get Users', method='GET', url='{{base_url}}/users', headers={'Accept': 'application/json'}, payload_type='json'
    )
    r2 = RequestModel(
        name='Create Post', method='POST', url='{{base_url}}/posts', headers={'Content-Type': 'application/json'},
        body='{"title":"foo","body":"bar","userId":1}', payload_type='json'
    )
    db.session.add_all([r1, r2])

    # Action (Selenium Demo)
    a1 = ActionModel(
        name='Activate Dial Through Siebel (Demo)',
        description='Opens browser and verifies title',
        code='from app.services.selenium_actions import run_selenium_action_demo\nrun_selenium_action_demo()'
    )
    db.session.add(a1)

    # Snippets
    s1 = Snippet(
        name='Set Env from Response', category='post-request', language='javascript',
        description='Extract id into environment',
        code='var data = pm.response.json; if (data && data.id) { pm.environment.set("last_id", data.id); }',
        tags=['env','extract']
    )
    db.session.add(s1)

    # Scenario
    sc = Scenario(name='JSONPlaceholder Flow', description='Demo flow using JSONPlaceholder')
    db.session.add(sc)
    db.session.flush()
    step1 = ScenarioStep(scenario_id=sc.id, order=1, step_type='request', ref_id=1)
    step2 = ScenarioStep(scenario_id=sc.id, order=2, step_type='action', ref_id=1)
    db.session.add_all([step1, step2])

    db.session.commit()
