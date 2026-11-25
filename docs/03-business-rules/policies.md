# Business Rules & Academic Policies
1. **Attendance Formula:** `Attendance % = (Present Classes / Total Eligible Classes) * 100`. Holidays are excluded from the denominator. Duplicate records for `(batch_id, student_id, session_date)` are prevented via unique DB constraint.
2. **Course Progress Formula:** `Progress % = (Completed Lectures / Total Course Lectures) * 100`. Reaching 100% transitions enrollment status to `Completed`.
3. **Certificate Eligibility:** Certificates are generated strictly when `progress_percent >= 100.0` and carry a unique `CERT-LMS-YYYY-XXXXX` verification code.
4. **Quiz Security Rule:** Correct option flags (`is_correct`) are stripped from student GET responses; final marks are computed exclusively on the FastAPI backend.
5. **Late Assignment Rule:** Submissions past `due_date` are automatically tagged `Late Submission` when `allow_late=True` and rejected with HTTP 400 when `allow_late=False`.
