# Test Execution Report

| Test ID | Module | Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-01 | Health | `GET /api/health` | HTTP 200 `healthy` | HTTP 200 `healthy` | PASS |
| TC-02 | Auth | Valid login (`admin@lms.edu`) | HTTP 200 + JWT token | HTTP 200 + JWT token | PASS |
| TC-03 | Auth | Wrong password login | HTTP 401 generic error | HTTP 401 generic error | PASS |
| TC-04 | RBAC | Student attempts `POST /api/courses` | HTTP 403 Forbidden | HTTP 403 Forbidden | PASS |
| TC-05 | Dashboard | Role KPIs (`admin`, `instructor`, `student`) | Role-specific DB metrics | Role-specific DB metrics | PASS |
| TC-06 | Quizzes | Student fetches quiz before attempt | `is_correct` omitted | `is_correct` omitted | PASS |
| TC-07 | Quizzes | Student submits quiz attempt | Server calculates score | Server calculates score | PASS |
| TC-08 | Certificates | `GET /api/certificates/verify/CERT-LMS-2026-8841` | HTTP 200 `valid: true` | HTTP 200 `valid: true` | PASS |
