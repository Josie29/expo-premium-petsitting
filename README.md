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
- Open `index.html` from the project root in your browser.

Option 2: Run a local server (recommended)
1. From the project root, in a terminal:
   `python3 -m http.server 8000`
2. Visit: `http://localhost:8000`

## Deploy with GitHub Pages

1. Create a GitHub repo (e.g., `expo-premium-petsitting`).
2. From the project root, initialize and push:
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
   `cd backend`
   `python3 -m venv .venv && source .venv/bin/activate`
   `pip install -r requirements.txt`
2. Configure environment variables (still in `backend/`):
   - Copy `env.example`, fill in your SMTP values (or edit `env.example` directly for local-only use).
   - For local use: `export $(cat env.example | xargs)`
3. From the project root, run the API (venv still active):
   `cd .. && uvicorn backend.main:app --host 0.0.0.0 --port 8001`
4. Update the form endpoint in `index.html`:
   - `data-endpoint="http://localhost:8001/contact"`

### Backend tests

Tests import the `backend` package, so run pytest from the **repository root** (parent of `backend/`) with the backend venv activated:

1. `cd backend && source .venv/bin/activate`
2. `cd ..` (back to the project root)
3. `python -m pytest backend/tests/`

Alternatively, from `backend/` with the venv active: `PYTHONPATH=.. python -m pytest tests/`

### CI (GitHub)

On GitHub, the workflow `.github/workflows/backend-tests.yml` runs `pytest` on every pull request (and push) targeting `main`. To block merges until tests pass:

1. Repo → **Settings** → **Branches** → **Add branch protection rule** (or edit the rule for `main`).
2. Enable **Require status checks to pass before merging**.
3. Search for and select the check named **pytest** (the job name from the workflow). GitHub only lists checks after at least one run has **finished** on the repo—open a PR to `main`, push to `main`, or use **Actions** → **Backend tests** → **Run workflow** (requires `workflow_dispatch` in the workflow), then try the settings again.

### Deployment notes
- Set the same SMTP environment variables on your host.
- Set `FRONTEND_ORIGIN` to your public site URL for CORS.
- Update `data-endpoint` in `index.html` to your deployed backend URL.
