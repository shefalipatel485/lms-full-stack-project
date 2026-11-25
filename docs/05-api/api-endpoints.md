# REST API Endpoint Inventory
Base URL: `http://localhost:8000` | Interactive Swagger UI: `http://localhost:8000/docs`

| Method | Endpoint | Roles | Description |
|---|---|---|---|
| POST | `/api/auth/login` | Public | Authenticate user & issue JWT |
| POST | `/api/auth/register` | Public | Register new student/instructor |
| GET | `/api/auth/me` | Authenticated | Current user profile |
| GET/POST | `/api/users` | Admin, Instructor | List/create users |
| GET/POST | `/api/courses` | All / Admin | List or create courses |
| GET/POST | `/api/batches` | All / Admin | List or create batches |
| GET/POST | `/api/lectures` | All / Admin, Inst | List or create lectures |
| POST | `/api/lectures/{id}/complete` | Student | Mark lecture completed & update progress |
| GET/POST | `/api/assignments` | All / Admin, Inst | List or create assignments |
| POST | `/api/submissions` | Student | Submit assignment answer |
| POST | `/api/submissions/{id}/evaluate` | Admin, Instructor | Grade submission & feedback |
| GET/POST | `/api/quizzes` | All / Admin, Inst | List or create MCQ quizzes |
| POST | `/api/quizzes/{id}/attempt` | Student | Submit quiz & compute score server-side |
| GET/POST | `/api/attendance` | All / Admin, Inst | View summary or mark bulk attendance |
| GET/POST | `/api/payments` | Admin, Student / Admin | View or record fee payments |
| GET | `/api/certificates/verify/{id}` | Public | Verify certificate authenticity |
| GET | `/api/reports/dashboard` | Authenticated | Role-specific KPIs & chart data |
