# Known Issues & Limitations Log
1. **Local Development File Storage:** Uploaded files save to `backend/uploads/` locally; configure AWS S3 or Cloudinary for stateless cloud hosting.
2. **Email Delivery:** Password reset currently generates a demo reset token response; connect SMTP credentials in production `.env`.
