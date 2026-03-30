from fastapi import FastAPI, Request, Response, status
from sqlalchemy import create_engine, text
import os
import redis
import bcrypt
from datetime import datetime


app = FastAPI()

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@db:5432/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)

cache = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

# --- 1. AUTHENTICATION ENDPOINT ---
@app.post("/auth")
async def authenticate(request: Request, response: Response):
    data = await request.json()
    username = data.get("User-Name")
    sent_password = data.get("User-Password")

    with engine.connect() as conn:
        query = text("SELECT value FROM radcheck WHERE username = :u AND attribute = 'Crypt-Password'")
        result = conn.execute(query, {"u": username}).fetchone()

        if result:
            db_hash = result[0].strip()
            
            try:
                # Convert both the password and the hash to bytes for comparison
                password_bytes = sent_password.encode('utf-8')
                hash_bytes = db_hash.encode('utf-8')

                # Direct check using bcrypt
                if bcrypt.checkpw(password_bytes, hash_bytes):
                    return {"control": {"Auth-Type": "Accept"}}
                else:
                    print(f"Auth Failed for {username}: Password mismatch.")
            except Exception as e:
                print(f"Native Bcrypt Error: {e}")
        else:
            print(f"User {username} not found.")

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

# --- 3. ACCOUNTING ENDPOINT ---
@app.post("/accounting")
async def accounting(request: Request):
    data = await request.json()
    status_type = data.get("Acct-Status-Type")
    username = data.get("User-Name")
    session_id = data.get("Acct-Session-Id")
    nas_ip = data.get("NAS-IP-Address")
    input_octets = data.get("Acct-Input-Octets", 0)
    output_octets = data.get("Acct-Output-Octets", 0)
    session_time = data.get("Acct-Session-Time", 0)


    # Convert empty strings or None to 0
    def clean_int(val):
        if val is None or val == "":
            return 0
        try:
            return int(val)
        except ValueError:
            return 0

    # Handling empty Accounting info by defaukting to 0
    input_octets = clean_int(data.get("Acct-Input-Octets"))
    output_octets = clean_int(data.get("Acct-Output-Octets"))
    session_time = clean_int(data.get("Acct-Session-Time"))

    with engine.connect() as conn:
        if status_type == "Start":
            conn.execute(
                text("""
                    INSERT INTO radacct (acctsessionid, username, nasipaddress, acctstarttime, acctinputoctets, acctoutputoctets)
                    VALUES (:sid, :u, :nas, now(), 0, 0)
                """),
                {"sid": session_id, "u": username, "nas": nas_ip}
            )

            cache.set(f"session:{session_id}", username, ex=3600)

        elif status_type == "Interim-Update":
            conn.execute(
                text("""
                    UPDATE radacct SET acctinputoctets = :inp, acctoutputoctets = :out, acctsessiontime = :time
                    WHERE acctsessionid = :sid
                """),
                {"inp": input_octets, "out": output_octets, "time": session_time, "sid": session_id}
            )

        elif status_type == "Stop":
            conn.execute(
                text("""
                    UPDATE radacct SET acctstoptime = now(), acctinputoctets = :inp, 
                    acctoutputoctets = :out, acctsessiontime = :time
                    WHERE acctsessionid = :sid
                """),
                {"inp": input_octets, "out": output_octets, "time": session_time, "sid": session_id}
            )

            cache.delete(f"session:{session_id}")
            
        conn.commit()
    
    return {"status": "success"}


# --- 4. MONITORING ENDPOINTS ---

@app.get("/users")
async def get_users():
    """
    List all registered users and their basic group/status info from Postgres
    """
    with engine.connect() as conn:
        # Join radcheck with radusergroup to show who belongs to which VLAN/Group
        query = text("""
            SELECT rc.username, ug.groupname 
            FROM radcheck rc
            LEFT JOIN radusergroup ug ON rc.username = ug.username
            WHERE rc.attribute = 'User-Password'
        """)
        result = conn.execute(query).fetchall()
        
        # Convert SQLAlchemy rows to list of dictionaries
        users_list = [
            {"username": row[0], "group": row[1] if row[1] else "No Group"} 
            for row in result
        ]
        return {"total_users": len(users_list), "users": users_list}

@app.get("/sessions/active")
async def get_active_sessions():
    """
    Query Redis to find all currently 'Live' sessions
    """
    # Find all keys in Redis that start with our prefix
    keys = cache.keys("session:*")
    active_sessions = []
    
    for key in keys:
        username = cache.get(key)
        # Extract the Session ID from the key name (e.g., 'session:ABC' -> 'ABC')
        session_id = key.replace("session:", "")
        
        active_sessions.append({
            "username": username,
            "session_id": session_id
        })
        
    return {
        "active_count": len(active_sessions),
        "sessions": active_sessions
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
