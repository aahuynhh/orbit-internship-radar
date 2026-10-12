# Orbit — UI/UX & Product Design Internship Radar

**Version 2:** saved applications + automatically refreshed internship discovery, with honest unknown fields.

## What it does

- Watches a customizable list of employer public job boards through **Greenhouse, Ashby, and Lever**.
- Filters listings for internship/co-op titles related to **product design, UX/UI, interaction design, visual design, design systems, UX research, experience design, service design**, etc.
- Produces `data/internships.json` through `refresh_jobs.py`; a scheduled GitHub Action runs **daily** after you deploy the repository to GitHub.
- Discover tab shows imported published roles. Save a role into the application tracker with **+ Track**, then manage its deadline, pay, relocation, housing, next action, notes, and status.
- Preserves your manually tracked applications and task list in local browser storage.
- Marks unverified compensation, deadlines, and relocation as **unknown**. Never assumes a posting has 2027 eligibility without verifying it.

## Enable automated updating (important)

1. Create a new public repository on GitHub and upload **all** files in this folder, including `.github/workflows/refresh.yml`, `sources.json`, `refresh_jobs.py`, and `data/internships.json`.
2. In **GitHub → Actions**, enable workflows if needed. Select **Refresh public internship feeds** → **Run workflow** once. Watch the logs for skipped invalid boards and successful feed updates.
3. In **Settings → Pages**, deploy from your main branch root (`/`). Open the resulting `https://USERNAME.github.io/REPO/` link to use Orbit.
4. After the first run, the workflow is scheduled **daily at 12:14 UTC** (GitHub's schedule may run late). The page reloads its current published feed whenever opened; click **Refresh listings** to re-fetch the latest file. Clicking refresh **does not trigger the backend collection**; the next GitHub Action does that.
5. Add more verified public ATS board slugs to `sources.json` for wider coverage. Invalid or private boards are skipped. Track listings missed by the feeds with the **+ Add internship** button.

## Important limits and safety

- **Not every internship on the internet.** Employers not on the configured feeds, roles at other ATS vendors, private postings and board failures will not appear. Search employer career sites too.
- Job listings are live *only after you run the workflow and host the app*. The downloadable HTML alone is offline with saved examples and won't auto-update; this is a static web app, not a server.
- The filter catches broad design internship titles regardless of graduating class and may include internships outside Summer 2027 or outside the US. Check role requirements yourself.
- Salary, deadline, housing, and relocation are not inferred from vague descriptions. Ashby compensation may appear as raw employer text where published; track a verified number manually.
- The current feed represents postings present at last successful fetch, not guaranteed available at the moment of application.
- Personal applications and tasks use browser `localStorage`, not cloud sync. Export backups; different browsers/devices do not automatically share state.
- GitHub Pages serves public job listing data only; **do not commit private personal notes, resumes, or backup files**.

## Run manually

```bash
python3 refresh_jobs.py
python3 -m http.server 8000
```

Open `http://localhost:8000/` to view the current collected feed. Requires outbound internet to employer job board APIs. No Python packages beyond the standard library.
