# Requirements Management

## Last Updated
$(date)

## Source of Truth
This requirements.txt was frozen from the working Docker container on $(date).

## How to Update

### For Docker Deployment
1. Edit requirements.txt
2. Rebuild: `docker-compose down && docker-compose up -d --build`
3. Test thoroughly
4. If working, commit changes

### For Local Development
1. Create virtual environment: `python3 -m venv venv`
2. Activate: `source venv/bin/activate`
3. Install: `pip install -r requirements.txt`
4. This ensures local matches Docker

### Adding New Packages
1. Add to requirements.txt with version: `packagename==1.2.3`
2. Rebuild Docker AND reinstall locally
3. Test both environments
4. Document why package was added

## Emergency Rollback
Backup files are stored as `requirements.txt.backup_TIMESTAMP`
To rollback: `cp requirements.txt.backup_XXXXX requirements.txt`
