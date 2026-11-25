import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_token(email: str, password: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    return res.json()["access_token"]

def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_auth_login_valid_and_invalid():
    # Valid admin login
    res = client.post("/api/auth/login", json={"email": "admin@lms.edu", "password": "Admin@123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"

    # Invalid password
    bad = client.post("/api/auth/login", json={"email": "admin@lms.edu", "password": "WrongPassword"})
    assert bad.status_code == 401

def test_rbac_authorization_enforcement():
    student_token = get_token("student@lms.edu", "Student@123")
    headers = {"Authorization": f"Bearer {student_token}"}

    # Student must NOT be allowed to create a course (403 Forbidden)
    res = client.post(
        "/api/courses",
        json={
            "code": "HACK-999",
            "title": "Unauthorized Course",
            "description": "Should fail",
            "category": "Security",
            "duration_weeks": 4,
            "fee": 1000
        },
        headers=headers
    )
    assert res.status_code == 403

def test_dashboard_metrics_by_role():
    for email, pwd, expected_role in [
        ("admin@lms.edu", "Admin@123", "admin"),
        ("instructor@lms.edu", "Instructor@123", "instructor"),
        ("student@lms.edu", "Student@123", "student"),
    ]:
        token = get_token(email, pwd)
        res = client.get("/api/reports/dashboard", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["role"] == expected_role

def test_quiz_answers_hidden_before_submission_and_scored_on_backend():
    stu_token = get_token("student@lms.edu", "Student@123")
    headers = {"Authorization": f"Bearer {stu_token}"}

    quizzes_res = client.get("/api/quizzes", headers=headers)
    assert quizzes_res.status_code == 200
    quizzes = quizzes_res.json()
    assert len(quizzes) >= 1
    q = quizzes[0]

    # Verify is_correct is NOT exposed to student
    for ques in q["questions"]:
        for opt in ques["options"]:
            assert "is_correct" not in opt

    # Submit attempt
    answers = [{"question_id": ques["id"], "selected_option_id": ques["options"][0]["id"]} for ques in q["questions"]]
    attempt_res = client.post(f"/api/quizzes/{q['id']}/attempt", json={"answers": answers}, headers=headers)
    assert attempt_res.status_code == 201
    assert "score" in attempt_res.json()

def test_certificate_verification():
    res = client.get("/api/certificates/verify/CERT-LMS-2026-8841")
    assert res.status_code == 200
    assert res.json()["valid"] is True
