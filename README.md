<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# ScholarHub — Global Graduate Scholarships

A client-facing website for discovering fully-funded graduate scholarships (Masters, PhD, PostDoc) from around the world, open for the 2026 academic year and beyond.

- **Browse for free** — search and filter a curated list of 24+ worldwide scholarships by country, degree, and funding type.
- **Register for a free access token** — clients sign up with name + email and instantly receive a personal token (e.g. `SH-XXXX-XXXX`).
- **Unlock full access** — entering the token (on any device, via "Activate Token") reveals full descriptions, deadlines, and direct apply links, plus a live AI web-search tool for fresh listings.

There is no backend: tokens are derived deterministically from the registered email so the same token can be re-activated from any device, and the active session is stored in the browser's `localStorage`.

## Run Locally

**Prerequisites:** Node.js

1. Install dependencies:
   `npm install`
2. (Optional) Set `GEMINI_API_KEY` in `.env.local` to enable the Live AI Search feature
3. Run the app:
   `npm run dev`
4. Build for production:
   `npm run build`

## Deploying

This is a static Vite/React app (no backend), so it deploys to any static host. Config files for the two most common ones are included:

### Vercel
1. Import the GitHub repo at https://vercel.com/new
2. Framework preset: **Vite** (auto-detected via `vercel.json`)
3. Add an environment variable `GEMINI_API_KEY` if you want Live AI Search enabled
4. Deploy — Vercel gives you a public `*.vercel.app` URL, and redeploys automatically on every push to this branch/PR

### Netlify
1. Import the GitHub repo at https://app.netlify.com/start
2. Build settings are auto-detected from `netlify.toml` (`npm run build` → `dist`)
3. Add `GEMINI_API_KEY` under Site settings → Environment variables if desired
4. Deploy — Netlify gives you a public `*.netlify.app` URL

Either platform will auto-build a preview URL for this pull request once connected, and a production URL once merged to the default branch.
