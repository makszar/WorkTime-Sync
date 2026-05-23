from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_login_returns_machine_role_and_scope():
    r=client.post('/auth/login',json={'login':'zarix','password':'i9VUibm6'})
    assert r.status_code==200
    u=r.json()['user']
    assert u['role']=='department_manager'
    assert u['scope']=='department'
    assert u['department']=='Core Platform'
    assert 'password' not in u

def test_executive_scope_sees_all_employees():
    r=client.get('/api/worktime/overview?user_id=u0')
    assert r.status_code==200
    assert r.json()['meta']['employees_count']==25

def test_department_manager_scope_sees_only_department():
    r=client.get('/api/worktime/overview?user_id=u1')
    assert r.status_code==200
    data=r.json()
    assert data['meta']['employees_count']==5
    assert all(e['team']=='Core Platform' for e in data['employees'])

def test_employee_scope_sees_only_self():
    r=client.get('/api/worktime/overview?user_id=emp5')
    assert r.status_code==200
    data=r.json()
    assert data['meta']['employees_count']==1
    assert data['employees'][0]['id']==5

def test_tasks_are_scoped_for_manager():
    r=client.get('/tasks?user_id=u1')
    assert r.status_code==200
    assert all(t['department']=='Core Platform' for t in r.json())

def test_employee_my_tasks():
    r=client.get('/tasks/my?user_id=emp5')
    assert r.status_code==200
    assert all(t['employee_id']==5 for t in r.json())

def test_employee_cannot_get_other_employee_card():
    assert client.get('/employees/12?user_id=emp5').status_code==403

def test_risk_explanation_contains_department_weights():
    r=client.get('/employees/5/risk-explanation?user_id=u1')
    assert r.status_code==200
    data=r.json()
    assert data['department']=='Core Platform'
    assert 'weights' in data
    assert 'formulaWithWeights' in data
    assert 'scheduleConfirmationStatus' in data

def test_company_analytics_executive_only():
    assert client.get('/analytics/company?user_id=u0').status_code==200
    assert client.get('/analytics/company?user_id=u1').status_code==403

def test_hr_dashboard_hr_only():
    assert client.get('/analytics/hr-dashboard?user_id=u_hr').status_code==200
    assert client.get('/analytics/hr-dashboard?user_id=u1').status_code==403
