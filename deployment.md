# Deployment Guide 🚀

This guide provides instructions on how to deploy the CDM Reservation App to a production environment.

## 1. Environment Configuration

You should move sensitive information to environment variables. Update `backend/database.py` and `backend/main.py` to use `os.getenv`.

### Required Environment Variables:
- `SECRET_KEY`: A long, random string for JWT signing.
- `DATABASE_URL`: (Optional) If you switch to PostgreSQL. Default is `sqlite:///./test.db`.
- `CORS_ORIGINS`: The URL of your deployed frontend.

---

## 2. Frontend Deployment (Vercel / Netlify)

The easiest way to deploy the frontend is using **Vercel** or **Netlify**.

1.  Connect your GitHub repository.
2.  Set the **Build Command**: `npm run build`
3.  Set the **Output Directory**: `dist`
4.  Add an Environment Variable:
    - `VITE_API_URL`: The URL of your deployed backend (e.g., `https://api.your-cdm-app.com`).

> [!NOTE]
> Ensure `frontend/src/api.ts` uses `import.meta.env.VITE_API_URL` as the base URL.

---

## 3. Backend Deployment (Render / Railway / Fly.io)

### Option A: Render (Easiest)
1.  Create a new **Web Service**.
2.  Connect your repository.
3.  Select **Python** environment.
4.  **Build Command**: `pip install -r requirements.txt`
5.  **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
6.  Add Environment Variables:
    - `SECRET_KEY`: (Your secret)
    - `PYTHON_VERSION`: `3.10` or higher.

### Option B: Docker
If you prefer Docker, create a `Dockerfile` in the root (see below).

---

## 4. Simple "Single-Server" Deployment

You can serve the frontend static files directly from FastAPI.

1.  Build the frontend: `cd frontend && npm run build`.
2.  Move the `dist` folder content to `backend/static`.
3.  In `backend/main.py`, mount the static directory:
    ```python
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        return FileResponse("static/index.html")
    ```

---

## 5. Production Considerations

- **Database**: For production, use **PostgreSQL** instead of SQLite.
- **Security**: Always use **HTTPS**.
- **Process Manager**: Use **Gunicorn** with Uvicorn workers for better stability:
  ```bash
  gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
  ```
- **Reverse Proxy**: Use **Nginx** as a reverse proxy to handle SSL and serve static files efficiently.
