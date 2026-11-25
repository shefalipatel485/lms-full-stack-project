# Module Development Notes
1. **Authentication (`auth_router.py`):** JWT HS256 login, bcrypt hashing, inactive user blocking, password change/reset.
2. **Courses & Batches (`courses_router.py`, `batches_router.py`):** Full CRUD, module hierarchy, capacity enforcement, soft archiving.
3. **Lectures (`lectures_router.py`):** Video links, validated file uploads, student completion progress recalculation.
4. **Assessments (`assessments_router.py`):** Assignment submission versioning, late flags, instructor grading, MCQ quizzes with hidden answer keys until submission.
5. **Operations (`operations_router.py`):** Bulk attendance, fee installments, ReportLab PDF certificate generator, public verification, role dashboards.
