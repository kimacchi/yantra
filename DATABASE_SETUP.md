# Database Setup Guide

## For Fresh Installations

If you're setting up Yantra for the first time, the database will be created automatically with all necessary columns when you run:

```bash
docker-compose up -d
```

The `init.sql` file will be executed automatically and includes:
- `compilers.build_logs` - For storing full Docker build output
- `submissions.uploaded_files` - For storing file metadata
- `submissions.files_directory` - For storing file directory paths

**No manual migration needed for fresh installations!**

---

## For Existing Databases

If you already have a running Yantra instance and are adding the new features, you need to run the migration scripts:

### 1. Add Build Logs Column

This adds the ability to store full Docker build output:

```bash
docker exec -i yantra-db-1 psql -U admin -d yantra_db < add_build_logs_column.sql
```

Or manually:
```bash
docker exec -it yantra-db-1 psql -U admin -d yantra_db
```
```sql
ALTER TABLE compilers ADD COLUMN IF NOT EXISTS build_logs TEXT;
```

### 2. Add File Upload Columns

This adds the ability to upload files with code submissions:

```bash
docker exec -i yantra-db-1 psql -U admin -d yantra_db < add_file_upload_columns.sql
```

Or manually:
```bash
docker exec -it yantra-db-1 psql -U admin -d yantra_db
```
```sql
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS uploaded_files TEXT;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS files_directory VARCHAR(500);
```

---

## Verify Schema

Check if your database has the latest schema:

```bash
docker exec -it yantra-db-1 psql -U admin -d yantra_db
```

```sql
-- Check compilers table
\d compilers

-- Check submissions table
\d submissions

-- Should see:
-- compilers.build_logs (text)
-- submissions.uploaded_files (text)
-- submissions.files_directory (character varying(500))
```

---

## Migration Scripts vs init.sql

### `init.sql`
- **Purpose**: Creates database schema from scratch
- **When used**: First time setup, fresh installations
- **Executed by**: PostgreSQL automatically via Docker entrypoint
- **Includes**: All current schema including new columns

### `add_build_logs_column.sql` & `add_file_upload_columns.sql`
- **Purpose**: Adds new columns to existing database
- **When used**: Upgrading existing installations
- **Executed by**: Manually by administrator
- **Includes**: Only the new columns (using `IF NOT EXISTS`)

---

## Complete Fresh Setup

For a completely fresh installation:

```bash
# 1. Clone the repository
git clone <repo-url>
cd yantra

# 2. Create required directories
mkdir -p tmp/executor_jobs

# 3. Start all services
docker-compose up -d

# 4. Wait for services to be healthy
docker-compose ps

# 5. Check database was initialized
docker exec -it yantra-db-1 psql -U admin -d yantra_db -c "\dt"

# 6. Verify all columns exist
docker exec -it yantra-db-1 psql -U admin -d yantra_db -c "\d compilers"
docker exec -it yantra-db-1 psql -U admin -d yantra_db -c "\d submissions"
```

---

## Upgrade from Previous Version

For upgrading an existing installation:

```bash
# 1. Pull latest code
git pull

# 2. Stop services
docker-compose down

# 3. Run migration scripts
docker-compose up -d db  # Start database only
docker exec -i yantra-db-1 psql -U admin -d yantra_db < add_build_logs_column.sql
docker exec -i yantra-db-1 psql -U admin -d yantra_db < add_file_upload_columns.sql

# 4. Rebuild and restart all services
docker-compose up -d --build

# 5. Verify
docker-compose logs api
docker-compose logs worker
```

---

## Troubleshooting

### "Column already exists" error

This is safe to ignore - it means the column was already added. The migration scripts use `IF NOT EXISTS` to prevent errors.

### Fresh database doesn't have new columns

Check if `init.sql` is being mounted correctly in `docker-compose.yml`:

```yaml
db:
  volumes:
    - ./init.sql:/docker-entrypoint-initdb.d/init.sql  # This line
```

Verify init.sql includes the new columns (should be on lines 15, 29, 30).

### Database won't start after migration

Check PostgreSQL logs:
```bash
docker-compose logs db
```

If corrupted, you can reset (WARNING: destroys all data):
```bash
docker-compose down -v  # Removes volumes
docker-compose up -d
```

---

## Schema Version History

### v1.0 (Initial)
- Basic compilers and submissions tables
- Build status tracking

### v1.1 (Build Logs Feature)
- Added `compilers.build_logs`
- Stores full Docker build output

### v1.2 (File Upload Feature)
- Added `submissions.uploaded_files`
- Added `submissions.files_directory`
- Supports per-submission file uploads

---

## Backup & Restore

### Backup current database

```bash
docker exec yantra-db-1 pg_dump -U admin yantra_db > backup.sql
```

### Restore from backup

```bash
docker exec -i yantra-db-1 psql -U admin -d yantra_db < backup.sql
```

### Backup with migrations

After running migrations, create a new backup:
```bash
docker exec yantra-db-1 pg_dump -U admin yantra_db > backup_v1.2.sql
```
