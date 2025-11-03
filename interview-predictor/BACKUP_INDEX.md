# Backup Directory Index

## Current Backups

Generated: $(date)

### Backup Directories


#### backup_20251027_044518/
- **Size**: 124K
- **Date**: 2025-10-27
- **Files**: 20
- **Contents**:
  - ✓ app.py
  - ✓ requirements-local.txt
  - ✓ Dockerfile
  - ✓ docker-compose.yml

#### backup_FINAL_20251027_045148/
- **Size**: 680K
- **Date**: 2025-10-27
- **Files**: 44
- **Contents**:
  - ✓ app.py
  - ✓ requirements-local.txt
  - ✓ Dockerfile
  - ✓ docker-compose.yml

## Recovery Instructions

To restore from a backup:
```bash
# Navigate to backup directory
cd backup_YYYYMMDD_HHMMSS/

# Copy files back to project root
cp app.py ../
cp requirements-local.txt ../
cp Dockerfile ../
cp docker-compose.yml ../
cp -r utils ../

# Restart application
cd ..
./start_local.sh
```

## Backup Policy

- Keep last 3 backups only
- Create new backup before major changes
- Always test restored backup before deployment
