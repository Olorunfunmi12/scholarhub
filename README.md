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
