# TruthLens Django Prototype (Image + Video)

This is a Django version of the TruthLens browser prototype.

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

1. Push this project to GitHub and create a new Blueprint on Render using the repository.
2. Render reads `render.yaml` to create the web service and PostgreSQL database. The web service installs dependencies, collects static files, applies database migrations, and starts Gunicorn.
3. Wait for the first deploy to finish, then open the service URL shown in the Render dashboard.

The Blueprint uses Render's free plans where available; free PostgreSQL databases are temporary and have limited storage. Choose a paid database plan for persistent production data. The site is public and currently has no user authentication or rate limiting; do not use it for sensitive uploads or treat it as a production forensic service.

For local deployments, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, and `DATABASE_URL` are optional. Set a unique secret key and turn debug off for any public deployment.

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
