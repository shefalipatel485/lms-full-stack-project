# Database ER Diagram & Data Dictionary (24 Tables)

## Entity Relationship Overview
```
[roles] 1---* [users] 1---0..1 [instructors]
                 |
                 +---* [courses] 1---* [course_modules] 1---* [lectures] 1---* [study_materials]
                 |        |                                      |
                 |        +---* [batches] 1---* [batch_students] +---* [lecture_progress]
                 |        |        |
                 |        |        +---* [attendance]
                 |        +---* [enrollments]
                 |        +---* [assignments] 1---* [submissions] 1---0..1 [assignment_feedback]
                 |        +---* [quizzes] 1---* [questions] 1---* [quiz_options]
                 |        |        +---* [quiz_attempts] 1---* [quiz_answers]
                 |        +---* [certificates]
                 |        +---* [payments]
                 +---* [notifications]
                 +---* [announcements]
```

## Core Tables & Delete Behavior
| Table | Primary Key | Unique Constraints | Delete Behavior |
|---|---|---|---|
| `roles` | `id` | `name` | `RESTRICT` on users |
| `users` | `id` | `email` | Soft-deactivate (`is_active=False`) |
| `courses` | `id` | `code` | Archive if enrollments exist |
| `batches` | `id` | `name` | `RESTRICT` on course |
| `batch_students` | `id` | `(batch_id, student_id)` | `CASCADE` |
| `enrollments` | `id` | `(student_id, course_id)` | `CASCADE` |
| `lecture_progress` | `id` | `(student_id, lecture_id)` | `CASCADE` |
| `attendance` | `id` | `(batch_id, student_id, session_date)` | `CASCADE` |
| `certificates` | `id` | `certificate_number`, `(student_id, course_id)` | `CASCADE` |
| `payments` | `id` | `receipt_number` | `RESTRICT` on course |
