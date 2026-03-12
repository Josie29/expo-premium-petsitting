# Expo Premium Petsitting Website

Simple static site for the dog sitting business.

## Project structure
- `index.html` - main page
- `css/` - stylesheets (colors and layout)
- `assets/` - images and media
- `js/` - frontend JavaScript
- `backend/` - FastAPI contact form backend

## Preview in a browser

Option 1: Open the file directly
- Open `/Users/c915852/Documents/cursor_practice/index.html` in your browser.

Option 2: Run a local server (recommended)
1. In a terminal:
   `cd /Users/c915852/Documents/cursor_practice && python3 -m http.server 8000`
2. Visit: `http://localhost:8000`

## Deploy with GitHub Pages

1. Create a GitHub repo (e.g., `expo-premium-petsitting`).
2. In your project folder, initialize and push:
   `cd /Users/c915852/Documents/cursor_practice`
   `git init`
   `git add .`
   `git commit -m "Initial site"`
   `git branch -M main`
   `git remote add origin https://github.com/<your-username>/<repo>.git`
   `git push -u origin main`
3. In GitHub:
   - Go to the repo → Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` / `/root`
4. Save, then wait 1-2 minutes. Your site URL will appear on that page.

## Contact form backend (FastAPI)

### Local setup
1. Create a virtual environment and install dependencies:
   `cd /Users/c915852/Documents/cursor_practice/backend`
   `python3 -m venv .venv && source .venv/bin/activate`
   `pip install -r requirements.txt`
2. Configure environment variables:
   - Copy `backend/env.example` and fill in your SMTP values.
   - For local use: `export $(cat backend/env.example | xargs)`
3. Run the API:
   `uvicorn backend.main:app --host 0.0.0.0 --port 8001`
4. Update the form endpoint in `index.html`:
   - `data-endpoint="http://localhost:8001/contact"`

### Deployment notes
- Set the same SMTP environment variables on your host.
- Set `FRONTEND_ORIGIN` to your public site URL for CORS.
- Update `data-endpoint` in `index.html` to your deployed backend URL.
