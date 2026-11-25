# Security Architecture & Audit Checklist
- **Password Hashing:** `bcrypt` via `passlib` (zero plaintext storage).
- **Authentication:** Signed HS256 JWT tokens with configurable `ACCESS_TOKEN_EXPIRE_MINUTES`.
- **RBAC Enforcement:** FastAPI `require_roles([...])` dependencies validate every protected route server-side.
- **File Upload Validation:** Extension whitelist (`.pdf`, `.ppt`, `.pptx`, `.doc`, `.docx`, `.txt`, `.mp4`), UUID filename sanitization, and max size cap.
- **Secret Hygiene:** `.env` excluded via `.gitignore`; only `.env.example` committed.
