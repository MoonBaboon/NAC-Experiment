from fastapi import FastAPI, Request, Response, status
from sqlalchemy import create_engine, text
import os

app = FastAPI()

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@db:5432/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)

# --- 1. AUTHENTICATION ENDPOINT ---
@app.post("/auth")
async def authenticate(request: Request, response: Response):
    data = await request.json()
    username = data.get("User-Name")
    password = data.get("User-Password")

    with engine.connect() as conn:
        query = text("SELECT value FROM radcheck WHERE username = :u AND attribute = 'User-Password'")
        user = conn.execute(query, {"u": username}).fetchone()

#        print(f"Auth Attempt: {username} | DB Pass: {user[0] if user else 'None'} | Sent Pass: {password}")

        if user and user[0] == password:
            return {"control": {"Auth-Type": "Accept"}}

        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"control": {"Auth-Type": "Reject"}}

# --- 2. AUTHORIZATION ENDPOINT ---
@app.post("/authorize")
async def authorize(request: Request):
    data = await request.json()
    username = data.get("User-Name")

    with engine.connect() as conn:
        # Fetch VLAN from radgroupreply by joining with radusergroup
        query = text("""
            SELECT rg.attribute, rg.value 
            FROM radusergroup ug
            JOIN radgroupreply rg ON ug.groupname = rg.groupname
            WHERE ug.username = :u
        """)
        results = conn.execute(query, {"u": username}).fetchall()

    # Build the reply attributes (VLAN, etc.)
    reply = {
        "Tunnel-Type": "VLAN",
        "Tunnel-Medium-Type": "IEEE-802"
    }
    
    for attr, val in results:
        reply[attr] = val

    return {"reply": reply}

@app.get("/health")
def health():
    return {"status": "healthy"}
