# Expo Premium Petsitting Website

Simple static site for the dog sitting business.

## Project structure
- `index.html` - main page
- `css/` - stylesheets (colors and layout)
- `assets/` - images and media
- `js/` - future JavaScript (empty for now)

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
