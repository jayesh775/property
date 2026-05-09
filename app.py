"""
PropertyWeb - Flask Backend
============================
Main application file containing:
- Database initialization and seeding
- All API routes for properties, users, chat
- Page routes for all HTML templates
"""

import os
import csv
import random
import sqlite3
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, jsonify, g

# ─────────────────────────────────────────────
# App Configuration
# ─────────────────────────────────────────────
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "property.db")
CSV_PATH = os.path.join(BASE_DIR, "pro.csv")

# ── Load ML pipeline (RandomForestRegressor trained on Gurugram property data)
PIPELINE_PATH = os.path.join(BASE_DIR, "pipeline.pkl")
try:
    with open(PIPELINE_PATH, "rb") as f:
        price_pipeline = pickle.load(f)
    print("✓ ML pipeline loaded")
except Exception as e:
    price_pipeline = None
    print(f"⚠ Pipeline not loaded: {e}")

# ─────────────────────────────────────────────
# Database Helpers
# ─────────────────────────────────────────────
def get_db():
    """Return a thread-local DB connection with row_factory for dict-like access."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    """Auto-close DB connection after each request."""
    db = g.pop("db", None)
    if db:
        db.close()

def query(sql, args=(), one=False):
    """Run a SELECT and return one row or all rows."""
    cur = get_db().execute(sql, args)
    rows = cur.fetchall()
    return (rows[0] if rows else None) if one else rows

def execute(sql, args=()):
    """Run INSERT / UPDATE / DELETE and commit."""
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid

# ─────────────────────────────────────────────
# Database Initialisation
# ─────────────────────────────────────────────
def init_db():
    """Create all tables and seed data if the DB doesn't exist yet."""
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    # ── Users Table ──────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            UserId      INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            gender      TEXT,
            age         INTEGER,
            Password    TEXT NOT NULL,
            occupation  TEXT,
            organisation TEXT,
            orgAddress  TEXT,
            orgSector   TEXT,
            Status      TEXT DEFAULT 'yes'
        )
    """)

    # ── Property Table ───────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Property (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            property_type   TEXT,
            society         TEXT,
            sector          TEXT,
            priceCr         REAL,
            area            REAL,
            bedroom         INTEGER,
            bathroom        INTEGER,
            balcony         TEXT,
            StudyRoom       INTEGER,
            servantRoom     INTEGER,
            floorNum        INTEGER,
            agePossession   TEXT,
            Furnishing_type TEXT,
            Luxury_category TEXT,
            UserID          INTEGER,
            PricePerSquare  REAL,
            Rent            REAL,
            FOREIGN KEY (UserID) REFERENCES Users(UserId)
        )
    """)

    # ── Image Table ──────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Image (
            Furnishing_type TEXT PRIMARY KEY,
            i1 TEXT, i2 TEXT, i3 TEXT,
            i4 TEXT, i5 TEXT, i6 TEXT
        )
    """)

    # ── Chat Table ───────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Chat (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            senderId   INTEGER,
            recieverId INTEGER,
            message    TEXT,
            time       TEXT,
            FOREIGN KEY (senderId)   REFERENCES Users(UserId),
            FOREIGN KEY (recieverId) REFERENCES Users(UserId)
        )
    """)

    db.commit()

    # ── Seed Users (25 rows) ─────────────────
    count = db.execute("SELECT COUNT(*) FROM Users").fetchone()[0]
    if count == 0:
        users = [
            (1,  "Aarav Sharma",     "aarav@gmail.com",     "male",   24, "pass123", "job",      "Infosys Ltd",            "DLF Cyber City, Gurugram",   "sector 24",          "yes"),
            (2,  "Priya Verma",      "priya@gmail.com",     "female", 22, "pass123", "student",  "BITS Pilani",             "Vidya Vihar, Pilani",        "sector 46",          "yes"),
            (3,  "Rohan Mehta",      "rohan@gmail.com",     "male",   28, "pass123", "job",      "Wipro Technologies",      "Sector 45, Gurugram",        "sector 45",          "yes"),
            (4,  "Sneha Gupta",      "sneha@gmail.com",     "female", 26, "pass123", "job",      "HCL Technologies",        "Sector 60, Noida",           "sector 60",          "yes"),
            (5,  "Karan Singh",      "karan@gmail.com",     "male",   30, "pass123", "business", "Singh Realtors Pvt Ltd",  "MG Road, Gurugram",          "sector 28",          "yes"),
            (6,  "Ananya Joshi",     "ananya@gmail.com",    "female", 23, "pass123", "student",  "Delhi University",        "North Campus, Delhi",        "sector 14",          "yes"),
            (7,  "Vikram Rao",       "vikram@gmail.com",    "male",   32, "pass123", "job",      "Accenture India",         "Sector 57, Gurugram",        "sector 57",          "yes"),
            (8,  "Divya Nair",       "divya@gmail.com",     "female", 27, "pass123", "job",      "Deloitte India",          "DLF Cyber City, Gurugram",   "sector 24",          "yes"),
            (9,  "Amit Patel",       "amit@gmail.com",      "male",   35, "pass123", "business", "Patel Constructions",     "Sohna Road, Gurugram",       "sohna road",         "yes"),
            (10, "Pooja Mishra",     "pooja@gmail.com",     "female", 21, "pass123", "student",  "Amity University",        "Sector 125, Noida",          "sector 45",          "yes"),
            (11, "Rajesh Kumar",     "rajesh@gmail.com",    "male",   40, "pass123", "job",      "TCS Ltd",                 "Sector 126, Noida",          "sector 62",          "yes"),
            (12, "Meera Iyer",       "meera@gmail.com",     "female", 29, "pass123", "job",      "IBM India",               "Sector 67, Gurugram",        "sector 67",          "yes"),
            (13, "Siddharth Das",    "siddharth@gmail.com", "male",   25, "pass123", "student",  "IIT Delhi",               "Hauz Khas, Delhi",           "sector 54",          "yes"),
            (14, "Kavya Reddy",      "kavya@gmail.com",     "female", 31, "pass123", "job",      "Google India",            "Sector 44, Gurugram",        "sector 44",          "yes"),
            (15, "Nikhil Bhatia",    "nikhil@gmail.com",    "male",   27, "pass123", "job",      "Microsoft India",         "Signature Towers, Gurugram", "sector 30",          "yes"),
            (16, "Tanya Chopra",     "tanya@gmail.com",     "female", 24, "pass123", "student",  "Symbiosis International", "Pune",                       "sector 58",          "yes"),
            (17, "Arjun Malhotra",   "arjun@gmail.com",     "male",   33, "pass123", "business", "Malhotra Group",          "Golf Course Road, Gurugram", "sector 55",          "yes"),
            (18, "Swati Aggarwal",   "swati@gmail.com",     "female", 26, "pass123", "job",      "Amazon India",            "Sector 49, Gurugram",        "sector 49",          "yes"),
            (19, "Rahul Saxena",     "rahul@gmail.com",     "male",   22, "pass123", "student",  "MDU Rohtak",              "Rohtak",                     "sector 46",          "yes"),
            (20, "Ishita Kapoor",    "ishita@gmail.com",    "female", 28, "pass123", "job",      "Flipkart",                "Sector 72, Gurugram",        "sector 72",          "yes"),
            (21, "Manish Trivedi",   "manish@gmail.com",    "male",   36, "pass123", "business", "Trivedi Traders",         "Manesar, Gurugram",          "manesar",            "yes"),
            (22, "Priyanka Dubey",   "priyanka@gmail.com",  "female", 30, "pass123", "job",      "Capgemini India",         "Sector 74, Gurugram",        "sector 74",          "yes"),
            (23, "Suresh Pillai",    "suresh@gmail.com",    "male",   45, "pass123", "job",      "HDFC Bank",               "Sector 43, Gurugram",        "sector 43",          "yes"),
            (24, "Nisha Thakur",     "nisha@gmail.com",     "female", 23, "pass123", "student",  "Ashoka University",       "Sonipat",                    "sector 66",          "yes"),
            (25, "Deepak Choudhary", "deepak@gmail.com",    "male",   38, "pass123", "business", "Choudhary Infra",         "Dwarka Expressway, Gurugram","dwarka expressway",  "yes"),
        ]
        cur.executemany("INSERT INTO Users VALUES (?,?,?,?,?,?,?,?,?,?,?)", users)
        db.commit()
        print("Users seeded")

    # ── Seed Image Table ──────────────────────
    img_count = db.execute("SELECT COUNT(*) FROM Image").fetchone()[0]
    if img_count == 0:
        cur.executemany("INSERT INTO Image VALUES (?,?,?,?,?,?,?)", [
            ("furnished",    "fun1.jpg",  "fun2.jpg",  "fun3.jpg",  "fun4.jpg",  "fun5.jpg",  "fun6.jpg"),
            ("semifurnished", "semi1.jpg", "semi2.jpg", "semi3.jpg", "semi4.jpg", "semi5.jpg", "semi6.jpg"),
            ("unfurnished",  "un1.jpg",   "un2.jpg",   "un3.jpg",   "un4.jpg",   "un5.jpg",   "un6.jpg"),
        ])
        db.commit()
        print("Image table seeded")

    # ── Seed Property Table from CSV ──────────
    prop_count = db.execute("SELECT COUNT(*) FROM Property").fetchone()[0]
    if prop_count == 0:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                rows.append((
                    row["property_type"],
                    row["society"],
                    row["sector"],
                    float(row["priceCr"]        or 0),
                    float(row["area"]           or 0),
                    int(row["bedRoom"]          or 0),
                    int(row["bathroom"]         or 0),
                    row["balcony"],
                    int(row["study room"]       or 0),
                    int(row["servant room"]     or 0),
                    int(row["floorNum"]         or 0),
                    row["agePossession"],
                    row["furnishing_type"],
                    row["luxury_category"],
                    random.randint(1, 25),     # randomly assign UserID 1-25
                    float(row["PricePerSquare"] or 0),
                    float(row["Rent"]           or 0),
                ))
        cur.executemany("""
            INSERT INTO Property
            (property_type,society,sector,priceCr,area,bedroom,bathroom,
             balcony,StudyRoom,servantRoom,floorNum,agePossession,
             Furnishing_type,Luxury_category,UserID,PricePerSquare,Rent)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, rows)
        db.commit()
        print(f"Property table seeded with {len(rows)} rows")

    # ── Seed sample Chat messages ─────────────
    chat_count = db.execute("SELECT COUNT(*) FROM Chat").fetchone()[0]
    if chat_count == 0:
        chats = [
            (1, 2,  "Hi! Is the flat in Sector 24 still available?",   "2025-04-01 10:00"),
            (2, 1,  "Yes it is! Would you like to schedule a visit?",  "2025-04-01 10:05"),
            (1, 2,  "Sure, how about this Saturday?",                  "2025-04-01 10:10"),
            (3, 4,  "Hello, I saw your listing on Sohna Road.",        "2025-04-02 09:00"),
            (4, 3,  "Yes! It is a 3BHK, fully furnished.",             "2025-04-02 09:15"),
            (5, 6,  "Are you looking for a flatmate?",                 "2025-04-03 14:00"),
            (6, 5,  "Yes! I work in Sector 46. Where do you work?",    "2025-04-03 14:05"),
            (7, 8,  "Is the DLF apartment pet-friendly?",              "2025-04-04 11:00"),
            (8, 7,  "Yes, pets are allowed in the society.",           "2025-04-04 11:10"),
            (9, 10, "What is the monthly maintenance for Sector 89?",  "2025-04-05 16:00"),
            (10, 9, "Around 3500 per month including gym.",            "2025-04-05 16:20"),
        ]
        cur.executemany("INSERT INTO Chat (senderId,recieverId,message,time) VALUES (?,?,?,?)", chats)
        db.commit()
        print("Chat seeded")

    db.close()
    print("Database ready")

# ─────────────────────────────────────────────
# Page Routes
# ─────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/bproperty")
def bproperty():
    return render_template("bproperty.html")

@app.route("/rproperty")
def rproperty():
    return render_template("rproperty.html")

@app.route("/map")
def map_page():
    return render_template("map.html")

@app.route("/connect")
def connect():
    return render_template("connect.html")

@app.route("/sell")
def sell():
    return render_template("sell.html")

# ─────────────────────────────────────────────
# API – Price Prediction (ML pipeline)
# ─────────────────────────────────────────────
@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Predict property price using the trained RandomForest pipeline.
    Input features must match exactly what the pipeline was trained on:
      Numeric : bedRoom, bathroom, built_up_area, servant room, store room
      Ordinal : property_type, sector, balcony, agePossession,
                furnishing_type, luxury_category, floor_category
    Output  : predicted price in Crores (after np.expm1 of log1p target)
    """
    if price_pipeline is None:
        return jsonify({"success": False, "message": "Model not available"}), 503

    data = request.get_json()
    try:
        # Build dataframe with exact column names the pipeline expects
        df = pd.DataFrame([{
            "property_type":  data.get("property_type", "flat"),
            "sector":         data.get("sector", "sector 1"),
            "bedRoom":        int(data.get("bedRoom", 2)),
            "bathroom":       int(data.get("bathroom", 2)),
            "balcony":        str(data.get("balcony", "1")),
            "agePossession":  data.get("agePossession", "New Property"),
            "built_up_area":  float(data.get("built_up_area", 1000)),
            "servant room":   int(data.get("servant_room", 0)),
            "store room":     int(data.get("store_room", 0)),
            "furnishing_type":data.get("furnishing_type", "unfurnished"),
            "luxury_category":data.get("luxury_category", "Low"),
            "floor_category": data.get("floor_category", "Low Floor"),
        }])

        log_price = price_pipeline.predict(df)[0]
        price_cr  = float(np.expm1(log_price))

        # Format display price
        if price_cr < 1:
            display = f"₹{round(price_cr * 100)}L"
        else:
            display = f"₹{round(price_cr, 2)} Cr"

        return jsonify({
            "success":  True,
            "price_cr": round(price_cr, 4),
            "display":  display,
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/table")
def table():
    return render_template("table.html")

# ─────────────────────────────────────────────
# API – Properties (Buy)
# ─────────────────────────────────────────────
@app.route("/api/properties")
def api_properties():
    """Returns filtered buy-properties with furnishing images."""
    sector     = request.args.get("sector", "")
    min_p      = request.args.get("min_price", 0,    type=float)
    max_p      = request.args.get("max_price", 9999, type=float)
    prop_type  = request.args.getlist("type")
    bedrooms   = request.args.getlist("bedrooms")
    furnishing = request.args.getlist("furnishing")
    sort       = request.args.get("sort", "asc")

    sql  = """
        SELECT p.*, u.name as owner_name,
               i.i1,i.i2,i.i3,i.i4,i.i5,i.i6
        FROM Property p
        LEFT JOIN Users u ON p.UserID = u.UserId
        LEFT JOIN Image i ON LOWER(p.Furnishing_type) = LOWER(i.Furnishing_type)
        WHERE p.priceCr BETWEEN ? AND ?
    """
    args = [min_p, max_p]

    if sector:
        sql += " AND LOWER(p.sector) = LOWER(?)"
        args.append(sector)
    if prop_type:
        ph = ",".join("?" * len(prop_type))
        sql += f" AND LOWER(p.property_type) IN ({ph})"
        args.extend([t.lower() for t in prop_type])
    if furnishing:
        ph = ",".join("?" * len(furnishing))
        sql += f" AND LOWER(p.Furnishing_type) IN ({ph})"
        args.extend([f.lower() for f in furnishing])
    if bedrooms:
        conds = []
        for b in bedrooms:
            conds.append("p.bedroom >= 4" if b == "4+" else f"p.bedroom = {int(b)}")
        sql += " AND (" + " OR ".join(conds) + ")"

    sql += f" ORDER BY p.priceCr {'ASC' if sort=='asc' else 'DESC'} LIMIT 200"
    rows = query(sql, args)
    return jsonify([dict(r) for r in rows])

# ─────────────────────────────────────────────
# API – Properties (Rent)
# ─────────────────────────────────────────────
@app.route("/api/rentals")
def api_rentals():
    """Returns filtered rental properties."""
    sector     = request.args.get("sector", "")
    min_r      = request.args.get("min_price", 0,     type=float)
    max_r      = request.args.get("max_price", 99999, type=float)
    prop_type  = request.args.getlist("type")
    bedrooms   = request.args.getlist("bedrooms")
    furnishing = request.args.getlist("furnishing")
    sort       = request.args.get("sort", "asc")

    sql  = """
        SELECT p.*, u.name as owner_name,
               i.i1,i.i2,i.i3,i.i4,i.i5,i.i6
        FROM Property p
        LEFT JOIN Users u ON p.UserID = u.UserId
        LEFT JOIN Image i ON LOWER(p.Furnishing_type) = LOWER(i.Furnishing_type)
        WHERE p.Rent BETWEEN ? AND ?
    """
    args = [min_r, max_r]

    if sector:
        sql += " AND LOWER(p.sector) = LOWER(?)"
        args.append(sector)
    if prop_type:
        ph = ",".join("?" * len(prop_type))
        sql += f" AND LOWER(p.property_type) IN ({ph})"
        args.extend([t.lower() for t in prop_type])
    if furnishing:
        ph = ",".join("?" * len(furnishing))
        sql += f" AND LOWER(p.Furnishing_type) IN ({ph})"
        args.extend([f.lower() for f in furnishing])
    if bedrooms:
        conds = []
        for b in bedrooms:
            conds.append("p.bedroom >= 4" if b == "4+" else f"p.bedroom = {int(b)}")
        sql += " AND (" + " OR ".join(conds) + ")"

    sql += f" ORDER BY p.Rent {'ASC' if sort=='asc' else 'DESC'} LIMIT 200"
    rows = query(sql, args)
    return jsonify([dict(r) for r in rows])

# ─────────────────────────────────────────────
# API – Sectors & Societies
# ─────────────────────────────────────────────
@app.route("/api/sectors")
def api_sectors():
    """Return all unique sectors sorted alphabetically."""
    rows = query("SELECT DISTINCT sector FROM Property ORDER BY sector")
    return jsonify([r["sector"] for r in rows])

@app.route("/api/societies")
def api_societies():
    """Return societies filtered by sector (for dependent dropdown on map)."""
    sector = request.args.get("sector", "")
    if sector:
        rows = query(
            "SELECT DISTINCT society FROM Property WHERE LOWER(sector)=LOWER(?) ORDER BY society",
            [sector]
        )
    else:
        rows = query("SELECT DISTINCT society FROM Property ORDER BY society")
    return jsonify([r["society"] for r in rows])

# ─────────────────────────────────────────────
# API – Map
# ─────────────────────────────────────────────
@app.route("/api/map/sectors")
def api_map_sectors():
    """Average PricePerSquare per sector."""
    rows = query("""
        SELECT sector,
               ROUND(AVG(PricePerSquare),2) as avg_price,
               COUNT(*) as count
        FROM Property
        GROUP BY sector
        ORDER BY sector
    """)
    return jsonify([dict(r) for r in rows])

@app.route("/api/map/societies")
def api_map_societies():
    """Average PricePerSquare per society, optionally filtered by sector."""
    sector = request.args.get("sector", "")
    if sector:
        rows = query("""
            SELECT society, sector,
                   ROUND(AVG(PricePerSquare),2) as avg_price,
                   COUNT(*) as count
            FROM Property
            WHERE LOWER(sector)=LOWER(?)
            GROUP BY society
        """, [sector])
    else:
        rows = query("""
            SELECT society, sector,
                   ROUND(AVG(PricePerSquare),2) as avg_price,
                   COUNT(*) as count
            FROM Property
            GROUP BY society
        """)
    return jsonify([dict(r) for r in rows])

# ─────────────────────────────────────────────
# API – Users / Auth
# ─────────────────────────────────────────────
@app.route("/api/users")
def api_users():
    """Return all users without passwords."""
    rows = query("""
        SELECT UserId,name,email,gender,age,
               occupation,organisation,orgAddress,orgSector,Status
        FROM Users ORDER BY UserId
    """)
    return jsonify([dict(r) for r in rows])

@app.route("/api/login", methods=["POST"])
def api_login():
    """Verify credentials and return user info."""
    data = request.get_json()
    user = query(
        "SELECT * FROM Users WHERE email=? AND Password=?",
        [data.get("email","").strip(), data.get("password","").strip()],
        one=True
    )
    if user:
        u = dict(user)
        u.pop("Password", None)
        return jsonify({"success": True, "user": u})
    return jsonify({"success": False, "message": "Invalid email or password"}), 401

@app.route("/api/signup", methods=["POST"])
def api_signup():
    """Register new user with auto UserId and Status='no'."""
    data   = request.get_json()
    max_id = query("SELECT MAX(UserId) as m FROM Users", one=True)["m"] or 0
    try:
        execute("""
            INSERT INTO Users
            (UserId,name,email,gender,age,Password,occupation,organisation,orgAddress,orgSector,Status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (max_id+1, data.get("name"), data.get("email"), data.get("gender"),
              data.get("age"), data.get("password"), data.get("occupation"),
              data.get("organisation"), data.get("orgAddress"), data.get("orgSector"), "no"))
        return jsonify({"success": True, "userId": max_id+1})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Email already registered"}), 400

@app.route("/api/profile/<int:user_id>")
def api_profile(user_id):
    """Return a single user profile (no password)."""
    user = query(
        "SELECT UserId,name,email,gender,age,occupation,organisation,orgAddress,orgSector,Status FROM Users WHERE UserId=?",
        [user_id], one=True
    )
    return jsonify(dict(user)) if user else (jsonify({"error": "Not found"}), 404)

@app.route("/api/flatmate")
def api_flatmate():
    """Return users with same orgSector and Status='yes'."""
    org_sector = request.args.get("orgSector", "")
    rows = query("""
        SELECT UserId,name,email,gender,age,occupation,organisation,orgAddress,orgSector,Status
        FROM Users WHERE LOWER(orgSector)=LOWER(?) AND Status='yes'
    """, [org_sector])
    return jsonify([dict(r) for r in rows])

@app.route("/api/flatmate/update", methods=["POST"])
def api_flatmate_update():
    """Set user Status to 'yes'."""
    data = request.get_json()
    execute("UPDATE Users SET Status='yes' WHERE UserId=?", [data.get("userId")])
    return jsonify({"success": True})

# ─────────────────────────────────────────────
# API – Chat
# ─────────────────────────────────────────────
@app.route("/api/chat/conversations")
def api_conversations():
    """Return all unique conversations for a user."""
    uid = request.args.get("userId", type=int)
    rows = query("""
        SELECT DISTINCT
            CASE WHEN senderId=? THEN recieverId ELSE senderId END as otherId,
            u.name as otherName
        FROM Chat c
        JOIN Users u ON u.UserId =
            CASE WHEN c.senderId=? THEN c.recieverId ELSE c.senderId END
        WHERE senderId=? OR recieverId=?
        ORDER BY c.time DESC
    """, [uid, uid, uid, uid])
    return jsonify([dict(r) for r in rows])

@app.route("/api/chat/messages")
def api_messages():
    """Return all messages between two users."""
    uid = request.args.get("userId",  type=int)
    oid = request.args.get("otherId", type=int)
    rows = query("""
        SELECT c.*, u.name as senderName
        FROM Chat c JOIN Users u ON c.senderId = u.UserId
        WHERE (senderId=? AND recieverId=?) OR (senderId=? AND recieverId=?)
        ORDER BY c.time ASC
    """, [uid, oid, oid, uid])
    return jsonify([dict(r) for r in rows])

@app.route("/api/chat/send", methods=["POST"])
def api_send_message():
    """Save a new chat message."""
    data   = request.get_json()
    msg_id = execute(
        "INSERT INTO Chat (senderId,recieverId,message,time) VALUES (?,?,?,?)",
        (data.get("senderId"), data.get("recieverId"),
         data.get("message"), datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    return jsonify({"success": True, "id": msg_id})

# ─────────────────────────────────────────────
# API – Sell (List a new property)
# ─────────────────────────────────────────────
@app.route("/api/sell", methods=["POST"])
def api_sell():
    """Insert a new property listing into the Property table."""
    data = request.get_json()
    try:
        execute("""
            INSERT INTO Property
            (property_type,society,sector,priceCr,area,bedroom,bathroom,
             balcony,StudyRoom,servantRoom,floorNum,agePossession,
             Furnishing_type,Luxury_category,UserID,PricePerSquare,Rent)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data.get("property_type"), data.get("society"), data.get("sector"),
            data.get("priceCr"), data.get("area"), data.get("bedroom"),
            data.get("bathroom"), data.get("balcony"), data.get("StudyRoom"),
            data.get("servantRoom"), data.get("floorNum"), data.get("agePossession"),
            data.get("Furnishing_type"), data.get("Luxury_category"), data.get("UserID"),
            data.get("PricePerSquare"), data.get("Rent")
        ))
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ─────────────────────────────────────────────
# API – Table Viewer
# ─────────────────────────────────────────────
ALLOWED_TABLES = {"Property", "Image", "Users", "Chat"}

@app.route("/api/table/<table_name>")
def api_table(table_name):
    """Return all rows of a table for the viewer page."""
    if table_name not in ALLOWED_TABLES:
        return jsonify({"error": "Table not allowed"}), 403
    if table_name == "Users":
        rows = query("SELECT UserId,name,email,gender,age,occupation,organisation,orgAddress,orgSector,Status FROM Users")
    else:
        rows = query(f"SELECT * FROM {table_name}")
    if not rows:
        return jsonify({"columns": [], "rows": []})
    return jsonify({"columns": list(rows[0].keys()), "rows": [dict(r) for r in rows]})

# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
