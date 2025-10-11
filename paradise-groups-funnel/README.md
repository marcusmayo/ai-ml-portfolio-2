# Paradise Groups Funnel

Facebook Groups-first marketing funnel for Your Paradise boutique hotel in Costambar, DR.

## Quick Start (Cloud Shell)
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# (Edit .env with your values)

# Run locally
cd src
uvicorn app.api:app --reload --port 8080
