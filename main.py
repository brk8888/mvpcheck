from fastapi import FastAPI, Body
import os
import psycopg2
import requests
import json

app = FastAPI()

# Load environment variables
DB = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
BUCKET = os.getenv("SUPABASE_BUCKET", "media")
IDEA_URL = os.getenv("IDEASOFT_BASE_URL")
IDEA_KEY = os.getenv("IDEASOFT_API_KEY")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"ok": True}


@app.post("/leads")
def create_lead(payload: dict = Body(...)):
    """Create a new lead in the database.

    Expects a JSON payload with keys: name, email, phone, note.
    If DATABASE_URL is not configured, returns an error message.
    """
    if not DB:
        return {"error": "DATABASE_URL is not configured"}
    # Ensure table exists and insert the lead
    with psycopg2.connect(DB) as con:
        cur = con.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS leads(\n"
            "  id serial PRIMARY KEY,\n"
            "  name text,\n"
            "  email text,\n"
            "  phone text,\n"
            "  note text,\n"
            "  created_at TIMESTAMP DEFAULT NOW()\n"
            ")"
        )
        cur.execute(
            "INSERT INTO leads(name, email, phone, note) VALUES (%s, %s, %s, %s)",
            (
                payload.get("name"),
                payload.get("email"),
                payload.get("phone"),
                payload.get("note"),
            ),
        )
    return {"ok": True}


@app.post("/publish/ideasoft")
def publish_ideasoft(p: dict = Body(...)):
    """Publish product data to IdeaSoft API.

    Expects a JSON payload with product fields, then sends it to the configured
    IdeaSoft endpoint. Returns the status code and response body.
    """
    if not IDEA_URL or not IDEA_KEY:
        return {"error": "IdeaSoft API not configured"}
    headers = {"X-API-KEY": IDEA_KEY, "Content-Type": "application/json"}
    resp = requests.post(f"{IDEA_URL}/products", headers=headers, data=json.dumps(p))
    return {"status": resp.status_code, "body": resp.text}