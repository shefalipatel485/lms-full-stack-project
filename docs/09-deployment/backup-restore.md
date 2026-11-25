# MySQL Backup & Restore Procedure
- **Backup:** `mysqldump -u root -p lms_db > lms_db_backup_$(date +%F).sql`
- **Restore:** `mysql -u root -p lms_db < lms_db_backup_YYYY-MM-DD.sql`
