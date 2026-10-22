# TruthLens Django Prototype (Image + Video)

TruthLens is a Django analysis API and a static browser dashboard. Deploy the dashboard to Vercel and keep the Django/OpenCV backend on Render.

## Features
- Professional browser dashboard.
- Image/video upload and basic OpenCV analysis.
- Explainable findings and transparent limitations.
- SHA-256 fingerprinting.
- Local SQLite database for trusted reference hashes.
- Django admin to inspect trusted reference records.

## Important limitation
This first version is **not a trained deepfake detector**. It uses basic image/video technical heuristics and the displayed score is a review-priority indicator, not the probability that a file is fake. The local database is not a blockchain. Hash matching indicates byte-identical content to a registered reference, not factual truth.

## Windows setup
1. Extract the ZIP.
2. Open the extracted `TruthLens_Django` folder.
3. Click File Explorer's address bar, type `cmd`, press Enter.
4. Run each command:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

5. Open http://127.0.0.1:8000
6. Keep the terminal open while the server runs. Press Ctrl+C to stop.

## Optional Django admin
Create an admin user:

```bat
python manage.py createsuperuser
```

Then visit http://127.0.0.1:8000/admin

## Deploy to Render

1. Create a Blueprint on Render using this GitHub repository. Render reads `render.yaml` to create the Django web service and PostgreSQL database.
2. The web service installs dependencies, collects static files, applies database migrations, and starts Gunicorn. Save the backend URL shown in the Render dashboard.

The Blueprint uses Render's free plans where available; free PostgreSQL databases are temporary and have limited storage. Choose a paid database plan for persistent production data. The site is public and currently has no user authentication or rate limiting; do not use it for sensitive uploads or treat it as a production forensic service.

For local deployments, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, and `DATABASE_URL` are optional. Set a unique secret key and turn debug off for any public deployment.

## Deploy the dashboard to Vercel

The Django/OpenCV backend stays on Render; Vercel serves only the static dashboard. Do not deploy the Django project root as a Vercel application.

1. Deploy the Render Blueprint first and copy its HTTPS service URL.
2. Import this repository in Vercel and set the **Root Directory** to `frontend`. Use the **Other** framework preset and leave the build command blank.
3. In `frontend/config.js`, set `TRUTHLENS_API_BASE_URL` to the Render service URL (for example, `https://your-service.onrender.com`), without a trailing slash, and push the change.
4. Copy the final Vercel origin (for example, `https://your-project.vercel.app`) into both Render environment variables `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`. Include the `https://` scheme and no path, then redeploy the backend.

The frontend and backend use credentialed cross-origin requests and Django CSRF protection. Keep the CORS origin restricted to your actual Vercel site; do not use `*`. Vercel hosts only the static UI: uploads and analysis still run on Render and are subject to that service's request and runtime limits.

## Demo
Register a trusted original image/video, then analyze the exact same file. Its hash should match. Edit or re-encode a copy and analyze it; its hash should normally differ. A mismatch means the bytes differ from the registered file, not that the content is fake.

## Next steps
Integrate a properly evaluated manipulation-detection model, add model-compatible explainability, evaluate on held-out data, then consider blockchain only for a defined trusted provenance workflow. Before public deployment, add authentication, rate limits, secure file handling, and production settings.


## Empathy mapping and user-centred design

The dashboard includes an empathy map for a person who encounters potentially misleading digital media. It groups initial user hypotheses into four areas:

- **Says:** asks whether content is genuine, wants an explanation, and asks about its source.
- **Thinks:** considers AI generation or editing, the reliability of results, and whether a file matches a trusted original.
- **Does:** uploads media, searches for source context, and compares evidence before sharing.
- **Feels:** may feel confused, worried about being misled, or frustrated by technical results.

### Design implications

1. Keep the upload-and-review workflow simple.
2. Explain what each technical signal measures and what it cannot establish.
3. Present the review-priority score as a triage aid, not a probability that content is fake.
4. Explain SHA-256 reference matching accurately: a match means identical file bytes to a registered reference, not factual truth.
5. Offer clear next steps without pressuring the user to share, accuse, or trust content automatically.

**Research integrity:** The displayed statements are design hypotheses, not real participant quotes or validated findings. Conduct short user interviews or surveys, obtain consent, record anonymized observations, group recurring themes, and revise the map. Do not label invented examples as research data.

See `EMPATHY_MAP.md` for the research brief, interview prompts, and validation plan.
