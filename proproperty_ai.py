# ================================================================
#  ProProperty AI — Real Estate Valuation Platform
#  Final Year Project | Full-Stack ML Application
#  Stack: Python · Streamlit · Random Forest · SQLAlchemy · Plotly
# ================================================================

import os, time, hashlib, joblib, requests, base64, sqlite3
import pandas as pd
import plotly.express as px
import folium
import streamlit as st
from datetime import datetime
from sqlalchemy import create_engine, text
from streamlit_folium import st_folium
from PIL import Image


try:
 
    from streamlit_js_eval import get_geolocation
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False

# ── PAGE CONFIG ──────────────────────────────────────────────────
st.set_page_config(
    page_title="ProProperty AI",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── GLOBAL STYLES ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; color: #1e293b !important; }
.stApp { background: #f0f4ff !important; }
#MainMenu, footer, header { visibility: hidden; }

/* Force all text dark and visible - but NOT inside blue gradient divs */
p, span, h1, h2, h3, h4 { color: #1e293b !important; }
/* Nav bar and blue boxes - keep white */
[style*="linear-gradient(135deg, #1e3a8a"] *, 
[style*="linear-gradient(135deg,#1e3a8a"] * { color: white !important; }

/* Auth card */
.auth-card { background: white; border-radius: 20px; padding: 36px 32px;
    box-shadow: 0 8px 40px rgba(30,58,138,0.12); border: 1px solid #e0e7ff; }
.auth-title { font-size: 26px; font-weight: 800; color: #1e3a8a !important; text-align:center; margin-bottom:4px; }
.auth-sub { font-size: 14px; color: #475569 !important; text-align:center; margin-bottom:20px; }

/* Section headers */
.sec-head { 
    font-size: 12px; font-weight: 700; color: white !important;
    text-transform: uppercase; letter-spacing: 1.2px;
    background: linear-gradient(135deg, #1e3a8a, #1d4ed8);
    padding: 8px 16px; border-radius: 8px;
    border-bottom: none; margin: 22px 0 14px;
    display: block; }

/* Tabs - visible on mobile */
.stTabs [data-baseweb="tab-list"] { background: white !important; border-radius: 12px !important;
    padding: 4px !important; border: 1px solid #e0e7ff !important; gap: 4px !important; overflow-x: auto !important; }
.stTabs [data-baseweb="tab"] { border-radius: 8px !important; font-size: 14px !important;
    font-weight: 600 !important; color: #1e3a8a !important; padding: 10px 16px !important;
    background: transparent !important; white-space: nowrap !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #ffffff, #eef4ff); !important; color: white !important; }

/* Buttons */
.stButton > button { background: linear-gradient(135deg, #ffd700, #ffc107); !important;
    color: white !important; border: none !important; border-radius: 12px !important;
    font-weight: 700 !important; font-size: 15px !important;
    padding: 14px 20px !important; transition: all .2s !important; width: 100% !important; }
.stButton > button:hover { transform: translateY(-1px) !important; }
/* Logout Out button - distinct white style */
div[data-testid="column"]:last-child .stButton > button {
    background: white !important; color: #1e3a8a !important;
    border: 2px solid #1e3a8a !important; font-size: 13px !important;
    padding: 10px !important; }

/* Input labels - force visible */
.stTextInput label, .stSelectbox label, .stNumberInput label, .stFileUploader label {
    font-size: 14px !important; font-weight: 600 !important; color: #374151 !important; }

/* Input fields */
.stTextInput input, .stNumberInput input {
    border-radius: 10px !important; border: 1.5px solid #cbd5e1 !important;
    font-size: 15px !important; color: #1e293b !important; background: white !important; }

/* Toggle labels */
[data-testid="stToggleLabel"], .stCheckbox label {
    font-size: 14px !important; font-weight: 500 !important; color: #1e293b !important; }

/* Metrics */
[data-testid="metric-container"] { background: white !important; border: 1.5px solid #e0e7ff !important;
    border-radius: 14px !important; padding: 16px !important; box-shadow: 0 2px 8px rgba(30,58,138,0.06) !important; }
[data-testid="metric-container"] label { font-size: 12px !important; color: #64748b !important;
    font-weight: 600 !important; text-transform: uppercase !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 22px !important;
    font-weight: 800 !important; color: #1e3a8a !important; }

/* Captions */
.stCaption, [data-testid="caption"] { color: #475569 !important; font-size: 13px !important; }

/* Progress bar - multicolor */
.stProgress > div > div { background: linear-gradient(90deg,#10b981,#3b82f6,#f59e0b,#ec4899) !important;
    border-radius: 20px !important; height: 14px !important; }
.stProgress > div { background: #e2e8f0 !important; border-radius: 20px !important; height: 14px !important; }

/* Expander */
.streamlit-expanderHeader { font-size: 14px !important; font-weight: 600 !important;
    color: #1e3a8a !important; background: white !important; border-radius: 10px !important; }

/* MOBILE */
@media (max-width: 768px) {
    [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; }
    .auth-card { padding: 22px 16px !important; }
    .auth-title { font-size: 22px !important; }
    .stTextInput input, .stNumberInput input { font-size: 16px !important; min-height: 48px !important; }
    .stTextInput label, .stSelectbox label, .stNumberInput label { font-size: 15px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 12px !important; padding: 8px 10px !important; }
    [data-testid="metric-container"] { padding: 12px !important; margin-bottom: 8px !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 18px !important; }
    .stButton > button { font-size: 15px !important; min-height: 52px !important; }
    [data-testid="stToggleLabel"] { font-size: 15px !important; }
}

@media (max-width: 480px) {
    .auth-card { padding: 18px 12px !important; }
    .auth-title { font-size: 20px !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 16px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── MEDIA FOLDER ─────────────────────────────────────────────────
os.makedirs("property_media", exist_ok=True)

# ── DATABASE — SQLite (works everywhere, no setup needed) ────────
DB_PATH = "/tmp/proproperty.db"   # /tmp works on Streamlit Cloud
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
DATABASE_URL = "sqlite"


def init_db():
    with engine.connect() as con:
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                created  TEXT
            )
        """))
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS predictions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                username        TEXT,
                country         TEXT,
                state           TEXT,
                city            TEXT,
                pincode         TEXT,
                area            REAL,
                bedrooms        INTEGER,
                bathrooms       INTEGER,
                stories         INTEGER,
                parking         INTEGER,
                mainroad        INTEGER,
                guestroom       INTEGER,
                basement        INTEGER,
                hotwaterheating INTEGER,
                airconditioning INTEGER,
                prefarea        INTEGER,
                furnishing      TEXT,
                predicted_price REAL,
                price_per_sqft  REAL,
                segment         TEXT,
                lat             REAL,
                lon             REAL,
                media_paths     TEXT,
                timestamp       TEXT
            )
        """))
        con.commit()

init_db()

# ── MODEL ────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading AI model…")
def load_model():
    try:
        return joblib.load("house_model.pkl"), joblib.load("model_columns.pkl")
    except FileNotFoundError:
        return None, None

model, MODEL_COLS = load_model()

# ── AUTH ─────────────────────────────────────────────────────────
def hash_pw(pw):        return hashlib.sha256(pw.encode()).hexdigest()
def verify_pw(pw, h):   return hash_pw(pw) == h

def user_exists(u):
    with engine.connect() as con:
        return con.execute(
            text("SELECT 1 FROM users WHERE username=:u"), {"u": u}
        ).fetchone() is not None

def register_user(u, pw):
    if not u.strip():  return False, "Username cannot be empty."
    if user_exists(u): return False, "Username already taken."
    if len(pw) < 6:    return False, "Password must be at least 6 characters."
    with engine.connect() as con:
        con.execute(
            text("INSERT INTO users VALUES(:u,:p,:t)"),
            {"u": u, "p": hash_pw(pw), "t": datetime.now().isoformat()}
        )
        con.commit()
    return True, "ok"

def login_user(u, pw):
    with engine.connect() as con:
        row = con.execute(
            text("SELECT password FROM users WHERE username=:u"), {"u": u}
        ).fetchone()
    if not row:               return False, "Username not found."
    if not verify_pw(pw, row[0]): return False, "Incorrect password."
    return True, "ok"

# ── LOCATION DATA ────────────────────────────────────────────────
COUNTRY_STATES = {
    "India": ["Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh",
              "Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka",
              "Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram",
              "Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana",
              "Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Delhi","Chandigarh","Puducherry"],
    "USA":   ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
              "Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa",
              "Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan",
              "Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
              "New Hampshire","New Jersey","New Mexico","New York","North Carolina",
              "North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island",
              "South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont",
              "Virginia","Washington","West Virginia","Wisconsin","Wyoming"],
    "UK":    ["England","Scotland","Wales","Northern Ireland","London",
              "South East","South West","East of England","East Midlands",
              "West Midlands","Yorkshire","North West","North East"],
    "Canada":["Alberta","British Columbia","Manitoba","New Brunswick",
              "Newfoundland and Labrador","Nova Scotia","Ontario",
              "Prince Edward Island","Quebec","Saskatchewan",
              "Northwest Territories","Nunavut","Yukon"],
    "UAE":   ["Abu Dhabi","Dubai","Sharjah","Ajman","Umm Al Quwain","Ras Al Khaimah","Fujairah"],
    "Australia": ["New South Wales","Victoria","Queensland","South Australia",
                  "Western Australia","Tasmania","Australian Capital Territory","Northern Territory"],
}

COUNTRY_CODES = {"India":"IN","USA":"US","UK":"GB","Canada":"CA","UAE":"AE","Australia":"AU"}

# ── LOCAL COORDINATE DATABASE (no internet needed) ──────────────
# Covers major Indian pincodes + cities across all states
PINCODE_DB = {
    # Maharashtra
    "400001": ("Mumbai",        "Maharashtra", 18.9388, 72.8354),
    "400051": ("Mumbai",        "Maharashtra", 19.0596, 72.8295),
    "400070": ("Mumbai",        "Maharashtra", 19.0728, 72.8826),
    "411001": ("Pune",          "Maharashtra", 18.5196, 73.8553),
    "411014": ("Pune",          "Maharashtra", 18.5642, 73.9140),
    "411057": ("Pune",          "Maharashtra", 18.6298, 73.7997),
    "440001": ("Nagpur",        "Maharashtra", 21.1458, 79.0882),
    "431001": ("Aurangabad",    "Maharashtra", 19.8762, 75.3433),
    "422001": ("Nashik",        "Maharashtra", 19.9975, 73.7898),
    # Karnataka
    "560001": ("Bangalore",     "Karnataka",   12.9716, 77.5946),
    "560034": ("Bangalore",     "Karnataka",   12.9352, 77.6245),
    "560068": ("Bangalore",     "Karnataka",   12.9010, 77.6490),
    "575001": ("Mangalore",     "Karnataka",   12.8698, 74.8430),
    "580001": ("Hubli",         "Karnataka",   15.3647, 75.1240),
    # Tamil Nadu
    "600001": ("Chennai",       "Tamil Nadu",  13.0827, 80.2707),
    "600042": ("Chennai",       "Tamil Nadu",  13.0500, 80.2120),
    "641001": ("Coimbatore",    "Tamil Nadu",  11.0168, 76.9558),
    "625001": ("Madurai",       "Tamil Nadu",   9.9252, 78.1198),
    "620001": ("Tiruchirappalli","Tamil Nadu",  10.7905, 78.7047),
    # Delhi
    "110001": ("New Delhi",     "Delhi",       28.6139, 77.2090),
    "110011": ("New Delhi",     "Delhi",       28.5921, 77.1645),
    "110034": ("Delhi",         "Delhi",       28.7130, 77.1475),
    "110058": ("Delhi",         "Delhi",       28.6508, 77.0627),
    "110092": ("Delhi",         "Delhi",       28.6692, 77.3090),
    # Telangana
    "500001": ("Hyderabad",     "Telangana",   17.3850, 78.4867),
    "500032": ("Hyderabad",     "Telangana",   17.4435, 78.3772),
    "500081": ("Hyderabad",     "Telangana",   17.4947, 78.3996),
    "506001": ("Warangal",      "Telangana",   17.9784, 79.5941),
    # Gujarat
    "380001": ("Ahmedabad",     "Gujarat",     23.0225, 72.5714),
    "380015": ("Ahmedabad",     "Gujarat",     23.0395, 72.5070),
    "395001": ("Surat",         "Gujarat",     21.1702, 72.8311),
    "390001": ("Vadodara",      "Gujarat",     22.3072, 73.1812),
    "360001": ("Rajkot",        "Gujarat",     22.3039, 70.8022),
    # Rajasthan
    "302001": ("Jaipur",        "Rajasthan",   26.9124, 75.7873),
    "302021": ("Jaipur",        "Rajasthan",   26.8467, 75.8070),
    "313001": ("Udaipur",       "Rajasthan",   24.5854, 73.7125),
    "342001": ("Jodhpur",       "Rajasthan",   26.2389, 73.0243),
    # Uttar Pradesh
    "226001": ("Lucknow",       "Uttar Pradesh", 26.8467, 80.9462),
    "226010": ("Lucknow",       "Uttar Pradesh", 26.8728, 80.9942),
    "201001": ("Ghaziabad",     "Uttar Pradesh", 28.6692, 77.4538),
    "211001": ("Prayagraj",     "Uttar Pradesh", 25.4358, 81.8463),
    "282001": ("Agra",          "Uttar Pradesh", 27.1767, 78.0081),
    "221001": ("Varanasi",      "Uttar Pradesh", 25.3176, 82.9739),
    # West Bengal
    "700001": ("Kolkata",       "West Bengal", 22.5726, 88.3639),
    "700054": ("Kolkata",       "West Bengal", 22.5200, 88.3700),
    "700102": ("Kolkata",       "West Bengal", 22.6200, 88.4300),
    # Punjab
    "160001": ("Chandigarh",    "Chandigarh",  30.7333, 76.7794),
    "141001": ("Ludhiana",      "Punjab",      30.9010, 75.8573),
    "143001": ("Amritsar",      "Punjab",      31.6340, 74.8723),
    # Kerala
    "682001": ("Kochi",         "Kerala",       9.9312, 76.2673),
    "695001": ("Thiruvananthapuram","Kerala",   8.5241, 76.9366),
    "673001": ("Kozhikode",     "Kerala",      11.2588, 75.7804),
    # Madhya Pradesh
    "462001": ("Bhopal",        "Madhya Pradesh", 23.2599, 77.4126),
    "452001": ("Indore",        "Madhya Pradesh", 22.7196, 75.8577),
    "474001": ("Gwalior",       "Madhya Pradesh", 26.2183, 78.1828),
    # Haryana
    "122001": ("Gurgaon",       "Haryana",     28.4595, 77.0266),
    "121001": ("Faridabad",     "Haryana",     28.4089, 77.3178),
    "132001": ("Karnal",        "Haryana",     29.6857, 76.9905),
    # Andhra Pradesh
    "520001": ("Vijayawada",    "Andhra Pradesh", 16.5062, 80.6480),
    "530001": ("Visakhapatnam", "Andhra Pradesh", 17.6868, 83.2185),
    # Odisha
    "751001": ("Bhubaneswar",   "Odisha",      20.2961, 85.8245),
    "753001": ("Cuttack",       "Odisha",      20.4625, 85.8830),
    # Bihar
    "800001": ("Patna",         "Bihar",       25.5941, 85.1376),
    # Assam
    "781001": ("Guwahati",      "Assam",       26.1445, 91.7362),
    # Jharkhand
    "834001": ("Ranchi",        "Jharkhand",   23.3441, 85.3096),
    # Uttarakhand
    "248001": ("Dehradun",      "Uttarakhand", 30.3165, 78.0322),
    # Himachal Pradesh
    "171001": ("Shimla",        "Himachal Pradesh", 31.1048, 77.1734),
    # Goa
    "403001": ("Panaji",        "Goa",         15.4909, 73.8278),
}

# City → coordinates fallback
CITY_COORDS = {
    "mumbai":           (18.9388, 72.8354), "pune":         (18.5196, 73.8553),
    "bangalore":        (12.9716, 77.5946), "bengaluru":    (12.9716, 77.5946),
    "chennai":          (13.0827, 80.2707), "hyderabad":    (17.3850, 78.4867),
    "delhi":            (28.6139, 77.2090), "new delhi":    (28.6139, 77.2090),
    "kolkata":          (22.5726, 88.3639), "ahmedabad":    (23.0225, 72.5714),
    "surat":            (21.1702, 72.8311), "jaipur":       (26.9124, 75.7873),
    "lucknow":          (26.8467, 80.9462), "nagpur":       (21.1458, 79.0882),
    "patna":            (25.5941, 85.1376), "indore":       (22.7196, 75.8577),
    "bhopal":           (23.2599, 77.4126), "visakhapatnam":(17.6868, 83.2185),
    "vadodara":         (22.3072, 73.1812), "ghaziabad":    (28.6692, 77.4538),
    "ludhiana":         (30.9010, 75.8573), "agra":         (27.1767, 78.0081),
    "nashik":           (19.9975, 73.7898), "vijayawada":   (16.5062, 80.6480),
    "rajkot":           (22.3039, 70.8022), "meerut":       (28.9845, 77.7064),
    "coimbatore":       (11.0168, 76.9558), "chandigarh":   (30.7333, 76.7794),
    "amritsar":         (31.6340, 74.8723), "gurgaon":      (28.4595, 77.0266),
    "gurugram":         (28.4595, 77.0266), "noida":        (28.5355, 77.3910),
    "kochi":            ( 9.9312, 76.2673), "bhubaneswar":  (20.2961, 85.8245),
    "dehradun":         (30.3165, 78.0322), "ranchi":       (23.3441, 85.3096),
    "guwahati":         (26.1445, 91.7362), "thiruvananthapuram":(8.5241, 76.9366),
    "mangalore":        (12.8698, 74.8430), "hubli":        (15.3647, 75.1240),
    "madurai":          ( 9.9252, 78.1198), "varanasi":     (25.3176, 82.9739),
    "udaipur":          (24.5854, 73.7125), "jodhpur":      (26.2389, 73.0243),
    "gwalior":          (26.2183, 78.1828), "faridabad":    (28.4089, 77.3178),
    "panaji":           (15.4909, 73.8278), "shimla":       (31.1048, 77.1734),
    "aurangabad":       (19.8762, 75.3433), "warangal":     (17.9784, 79.5941),
    "kozhikode":        (11.2588, 75.7804), "tiruchirappalli":(10.7905, 78.7047),
    "prayagraj":        (25.4358, 81.8463), "allahabad":    (25.4358, 81.8463),
    "cuttack":          (20.4625, 85.8830), "karnal":       (29.6857, 76.9905),
    # USA major cities
    "new york":         (40.7128, -74.0060), "los angeles":  (34.0522,-118.2437),
    "chicago":          (41.8781, -87.6298), "houston":      (29.7604, -95.3698),
    "phoenix":          (33.4484,-112.0740), "philadelphia":  (39.9526, -75.1652),
    "san antonio":      (29.4241, -98.4936), "san diego":    (32.7157,-117.1611),
    "dallas":           (32.7767, -96.7970), "san francisco": (37.7749,-122.4194),
    "seattle":          (47.6062,-122.3321), "boston":       (42.3601, -71.0589),
    "miami":            (25.7617, -80.1918), "atlanta":      (33.7490, -84.3880),
    # UK
    "london":           (51.5074,  -0.1278), "manchester":   (53.4808,  -2.2426),
    "birmingham":       (52.4862,  -1.8904), "glasgow":      (55.8642,  -4.2518),
    "edinburgh":        (55.9533,  -3.1883),
    # UAE
    "dubai":            (25.2048,  55.2708), "abu dhabi":    (24.4539,  54.3773),
    "sharjah":          (25.3463,  55.4209),
}

def lookup_pincode(pincode, cc="IN"):
    """Look up city/state/coords from local DB first, then try API."""
    # 1. Check local database
    if pincode in PINCODE_DB:
        city, state, lat, lon = PINCODE_DB[pincode]
        return {"city": city, "state": state, "lat": lat, "lon": lon}
    # 2. Try external API (may fail on restricted networks)
    try:
        r = requests.get(f"https://api.zippopotam.us/{cc}/{pincode}", timeout=4)
        if r.status_code == 200:
            place = r.json()["places"][0]
            return {
                "city":  place.get("place name", ""),
                "state": place.get("state", ""),
                "lat":   float(place.get("latitude",  0)),
                "lon":   float(place.get("longitude", 0)),
            }
    except Exception:
        pass
    return {}

def geocode_address(city, state, country):
    """Get lat/lon from city name using local DB first, then API."""
    # 1. Check local city database
    key = city.strip().lower()
    if key in CITY_COORDS:
        return CITY_COORDS[key]
    # Try partial match
    for name, coords in CITY_COORDS.items():
        if key in name or name in key:
            return coords
    # 2. Try external geocoding API
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": f"{city},{state},{country}", "format": "json", "limit": 1},
            headers={"User-Agent": "ProPropertyAI/1.0"},
            timeout=5
        )
        if r.status_code == 200 and r.json():
            d = r.json()[0]
            return float(d["lat"]), float(d["lon"])
    except Exception:
        pass
    return 0.0, 0.0

# ── PREDICTION ───────────────────────────────────────────────────
def build_input(inp):
    df = pd.DataFrame(0, index=[0], columns=MODEL_COLS)
    df["area"]                = inp["area"]
    df["bedrooms"]            = inp["bedrooms"]
    df["bathrooms"]           = inp["bathrooms"]
    df["stories"]             = inp["stories"]
    df["parking"]             = inp["parking"]
    df["mainroad_yes"]        = int(inp["mainroad"])
    df["guestroom_yes"]       = int(inp["guestroom"])
    df["basement_yes"]        = int(inp["basement"])
    df["hotwaterheating_yes"] = int(inp["hotwaterheating"])
    df["airconditioning_yes"] = int(inp["airconditioning"])
    df["prefarea_yes"]        = int(inp["prefarea"])
    if inp["furnishing"] == "Semi-Furnished":
        if "furnishingstatus_semi-furnished" in df.columns:
            df["furnishingstatus_semi-furnished"] = 1
    elif inp["furnishing"] == "Unfurnished":
        if "furnishingstatus_unfurnished" in df.columns:
            df["furnishingstatus_unfurnished"] = 1
    return df

def price_segment(p):
    if   p < 3_000_000:  return "Affordable",  "🟢"
    elif p < 8_000_000:  return "Mid-Range",    "🟡"
    elif p < 20_000_000: return "Premium",      "🟠"
    else:                return "Luxury",        "🔴"

def save_prediction(username, inp, price, segment, lat, lon, media_paths=""):
    ppsf = price / inp["area"] if inp["area"] else 0
    with engine.connect() as con:
        con.execute(text("""
            INSERT INTO predictions
              (username,country,state,city,pincode,area,bedrooms,bathrooms,
               stories,parking,mainroad,guestroom,basement,hotwaterheating,
               airconditioning,prefarea,furnishing,predicted_price,price_per_sqft,
               segment,lat,lon,media_paths,timestamp)
            VALUES
              (:username,:country,:state,:city,:pincode,:area,:bedrooms,:bathrooms,
               :stories,:parking,:mainroad,:guestroom,:basement,:hotwaterheating,
               :airconditioning,:prefarea,:furnishing,:price,:ppsf,
               :segment,:lat,:lon,:media,:ts)
        """), {
            "username":username, "country":inp["country"], "state":inp["state"],
            "city":inp["city"],  "pincode":inp["pincode"],
            "area":inp["area"],  "bedrooms":inp["bedrooms"], "bathrooms":inp["bathrooms"],
            "stories":inp["stories"], "parking":inp["parking"],
            "mainroad":int(inp["mainroad"]),   "guestroom":int(inp["guestroom"]),
            "basement":int(inp["basement"]),   "hotwaterheating":int(inp["hotwaterheating"]),
            "airconditioning":int(inp["airconditioning"]), "prefarea":int(inp["prefarea"]),
            "furnishing":inp["furnishing"], "price":price, "ppsf":ppsf,
            "segment":segment, "lat":lat, "lon":lon, "media":media_paths,
            "ts":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        con.commit()

# ── SESSION STATE ────────────────────────────────────────────────
defaults = {
    "logged_in": False, "user": "", "page": "login",
    "auto_city": "", "auto_lat": 0.0, "auto_lon": 0.0, "_last_pin": "",
    "result": None   # stores last prediction so it persists
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════════════════════════════
#  AUTH SCREENS
# ════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:

    # Full page gradient background for auth
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #1d4ed8 100%) !important; }
    .auth-card { background: rgba(255,255,255,0.08) !important; backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.2) !important; }
    .auth-title { color: white !important; }
    .auth-sub { color: rgba(255,255,255,0.75) !important; }
    .stTextInput label { color: rgba(255,255,255,0.9) !important; }
    .stTextInput input { background: rgba(255,255,255,0.1) !important;
        color: white !important; border: 1px solid rgba(255,255,255,0.3) !important; }
    .stTextInput input::placeholder { color: rgba(255,255,255,0.5) !important; }
    p, span, div, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center;padding:40px 20px 20px;'>
        <div style='font-size:64px;'>🏙️</div>
        <div style='font-size:40px;font-weight:800;color:white;letter-spacing:-1.5px;margin-top:10px;'>
            HousePrice<span style='color:#93c5fd;'>Prediction</span>
        </div>
        <div style='color:rgba(255,255,255,0.85);font-size:16px;margin-top:10px;font-weight:500;'>
            ML-Powered Real Estate Valuation Platform
        </div>
        <div style='display:flex;justify-content:center;gap:16px;margin-top:20px;flex-wrap:wrap;'>
            <div style='background:rgba(255,255,255,0.95);border:1px solid rgba(255,255,255,0.3);
                border-radius:50px;padding:8px 18px;font-size:13px;color:white;font-weight:600;'>
                🏠 Instant Price Prediction
            </div>
            <div style='background: linear-gradient(135deg, #f0e6ff, #d6ccff);border:1px solid rgba(255,255,255,0.3);
                border-radius:50px;padding:8px 18px;font-size:13px;color:white;font-weight:600;'>
                📍 Live Location Map
            </div>
            <div style='background:rgba(255,255,255,0.95);;border:1px solid rgba(255,255,255,0.3);
                border-radius:50px;padding:8px 18px;font-size:13px;color:white;font-weight:600;'>
                📊 Market Analytics
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:

        # ── LOGIN ───────────────────────────────────────────────
        if st.session_state.page == "login":
            st.markdown("""
            <div style='background:rgba(255,255,255,0.12);backdrop-filter:blur(20px);
                border:1px solid rgba(255,255,255,0.25);border-radius:20px;
                padding:30px 28px;text-align:center;margin-bottom:20px;'>
                <div style='font-size:32px;font-weight:800;color:white;'>Welcome Back 👋</div>
                <div style='font-size:15px;color:rgba(255,255,255,0.8);margin-top:6px;'>
                    Sign in to your account
                </div>
            </div>
            """, unsafe_allow_html=True)

            lu = st.text_input("👤 Username", placeholder="Enter your username", key="li_u")
            lp = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="li_p")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🚀 Login →", use_container_width=True, key="btn_login"):
                if not lu or not lp:
                    st.error("Please enter your username and password.")
                else:
                    ok, msg = login_user(lu, lp)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.user = lu
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✨ Create New Account →", use_container_width=True, key="to_reg"):
                st.session_state.page = "register"
                st.rerun()

        # ── REGISTER ────────────────────────────────────────────
        elif st.session_state.page == "register":
            st.markdown("""
            <div style='background:rgba(255,255,255,0.12);backdrop-filter:blur(20px);
                border:1px solid rgba(255,255,255,0.25);border-radius:20px;
                padding:30px 28px;text-align:center;margin-bottom:20px;'>
                <div style='font-size:32px;font-weight:800;color:white;'>Create Account 🚀</div>
                <div style='font-size:15px;color:rgba(255,255,255,0.8);margin-top:6px;'>
                    Join ProProperty AI today — it's free!
                </div>
            </div>
            """, unsafe_allow_html=True)

            ru  = st.text_input("👤 Username",         placeholder="Choose a username",     key="re_u")
            rp  = st.text_input("🔒 Password",         type="password", placeholder="Min 6 characters", key="re_p")
            rp2 = st.text_input("🔒 Confirm Password", type="password", placeholder="Repeat password",   key="re_p2")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("✅ Create Account", use_container_width=True, key="btn_reg"):
                if not ru or not rp:
                    st.error("Please fill in all fields.")
                elif rp != rp2:
                    st.error("❌ Passwords do not match.")
                else:
                    ok, _ = register_user(ru, rp)
                    if ok:
                        st.success("✅ Account created! Please log in.")
                        time.sleep(1.5)
                        st.session_state.page = "login"
                        st.rerun()
                    else:
                        st.error("❌ Username already taken. Try another.")

            if st.button("← Back to Login", use_container_width=True, key="back_login"):
                st.session_state.page = "login"
                st.rerun()

    st.stop()

# ════════════════════════════════════════════════════════════════
#  MAIN DASHBOARD
# ════════════════════════════════════════════════════════════════
# ── TOP NAVIGATION BAR ───────────────────────────────────────────
tn1, tn2 = st.columns([5, 1])
tn1.markdown(f"""
<div style='background:linear-gradient(135deg,#1e3a8a,#1d4ed8);
     padding:16px 22px;border-radius:14px;'>
    <div style='font-size:20px;font-weight:800;color:white !important;
         text-shadow:0 1px 3px rgba(0,0,0,0.2);'>
        🏙️ <span style='color:white !important;'>ProProperty AI</span>
    </div>
    <div style='font-size:13px;color:rgba(255,255,255,0.9) !important;
         margin-top:3px;font-weight:500;'>
        👤 <span style='color:rgba(255,255,255,0.9) !important;'>{st.session_state.user}</span>
    </div>
</div>
""", unsafe_allow_html=True)
if tn2.button("🚪 Logout"):
    for k in defaults:
        st.session_state[k] = defaults[k]
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

@st.cache_data(ttl=20)
def get_history():
    try:
        return pd.read_sql("SELECT * FROM predictions ORDER BY timestamp DESC", engine)
    except Exception:
        return pd.DataFrame()

df_hist = get_history()

tab_val, tab_analytics, tab_map = st.tabs([
    "💎  New Valuation", "📈  Analytics", "📍  Map Explorer"
])

# ════════════════════════════════════════════════════════════════
#  TAB 1 — VALUATION
# ════════════════════════════════════════════════════════════════
with tab_val:

    # ── LOCATION: Dropdowns + Pincode auto-fill ──────────────────
    st.markdown('<div class="sec-head">📍 Location Details</div>', unsafe_allow_html=True)

    lc1, lc2 = st.columns(2)
    country = lc1.selectbox("🌍 Country", list(COUNTRY_STATES.keys()))
    state   = lc2.selectbox(
        "🗺️ State / Province",
        ["— Select State —"] + COUNTRY_STATES.get(country, [])
    )

    lc3, lc4 = st.columns(2)
    pincode = lc3.text_input("📮 Pincode / ZIP", placeholder="Enter pincode to auto-fill city")

    # Auto-fill city from pincode
    if pincode and len(pincode.strip()) >= 4 and pincode != st.session_state["_last_pin"]:
        cc = COUNTRY_CODES.get(country, "IN")
        with st.spinner("🔍 Auto-detecting city…"):
            res = lookup_pincode(pincode.strip(), cc)
        if res:
            st.session_state.auto_city = res.get("city", "")
            st.session_state.auto_lat  = res.get("lat",  0.0)
            st.session_state.auto_lon  = res.get("lon",  0.0)
            st.session_state["_last_pin"] = pincode
            lc4.success(f"📍 Auto-detected: **{st.session_state.auto_city}**")
        else:
            lc4.info("ℹ️ Not found — enter city manually below.")
            st.session_state["_last_pin"] = pincode

    city = lc4.text_input(
        "🏙️ City",
        value=st.session_state.auto_city,
        placeholder="Auto-filled from pincode"
    )

    # ── PROPERTY DETAILS ─────────────────────────────────────────
    st.markdown('<div class="sec-head">📐 Property Details</div>', unsafe_allow_html=True)

    # 2 columns — works perfectly on mobile and desktop
    pd1, pd2 = st.columns(2)
    area      = pd1.number_input("📏 Area (sq ft)",      100, 50000, 1200, step=50)
    bedrooms  = pd2.number_input("🛏️ Bedrooms",            1,    10,    3)

    pd3, pd4 = st.columns(2)
    bathrooms = pd3.number_input("🚿 Bathrooms",            1,    10,    2)
    stories   = pd4.number_input("🏢 Floors / Stories",    1,    10,    2)

    pd5, pd6 = st.columns(2)
    parking    = pd5.number_input("🚗 Parking Spaces",     0,     5,    1)
    furnishing = pd6.selectbox("🛋️ Furnishing Status",
                               ["Fully Furnished", "Semi-Furnished", "Unfurnished"])

    # ── AMENITIES ────────────────────────────────────────────────
    st.markdown('<div class="sec-head">✅ Property Amenities</div>', unsafe_allow_html=True)
    st.caption("Toggle all features that apply to this property:")

    # 2 columns for amenities — readable on all screen sizes
    am1, am2 = st.columns(2)
    mainroad        = am1.toggle("🛣️ Main Road Access",  value=True)
    guestroom       = am2.toggle("🛏️ Guest Room")

    am3, am4 = st.columns(2)
    basement        = am3.toggle("🏚️ Basement")
    hotwaterheating = am4.toggle("🔥 Hot Water Heating")

    am5, am6 = st.columns(2)
    airconditioning = am5.toggle("❄️ Air Conditioning")
    prefarea        = am6.toggle("⭐ Preferred Area")

    # ── MEDIA UPLOAD ─────────────────────────────────────────────
    st.markdown('<div class="sec-head">📸 Property Media (Optional)</div>', unsafe_allow_html=True)
    st.caption("Upload photos or a video as proof of the property:")

    mu1, mu2 = st.columns(2)
    with mu1:
        photos = st.file_uploader(
            "📷 Property Photos (JPG / PNG)",
            type=["jpg","jpeg","png","webp"],
            accept_multiple_files=True
        )
        if photos:
            img_cols = st.columns(min(len(photos), 3))
            for i, ph in enumerate(photos[:3]):
                img_cols[i].image(Image.open(ph), use_container_width=True, caption=f"Photo {i+1}")

    with mu2:
        video = st.file_uploader("🎥 Property Video (MP4 / MOV)", type=["mp4","mov","avi"])
        if video:
            st.video(video)

    # ── GPS OVERRIDE ─────────────────────────────────────────────
    lat = st.session_state.auto_lat
    lon = st.session_state.auto_lon
    with st.expander("🛰️ GPS Coordinates (auto-filled — expand to override)"):
        if lat != 0.0:
            st.success(f"📍 Coordinates from pincode: **{lat:.4f}, {lon:.4f}**")
        if GPS_AVAILABLE:
            if st.toggle("📡 Use live device GPS instead"):
                loc = get_geolocation()
                if loc and "coords" in loc:
                    lat = loc["coords"]["latitude"]
                    lon = loc["coords"]["longitude"]
                    st.success(f"✅ Live GPS: {lat:.5f}, {lon:.5f}")
        g1, g2 = st.columns(2)
        lat = g1.number_input("Latitude",  value=float(lat),  format="%.5f")
        lon = g2.number_input("Longitude", value=float(lon), format="%.5f")

    # ── PRICE GUIDE ──────────────────────────────────────────────
    st.markdown('<div class="sec-head">💡 Price Segment Guide</div>', unsafe_allow_html=True)

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("""<div style='background:linear-gradient(135deg,#059669,#10b981);
            border-radius:12px;padding:16px;color:white;margin-bottom:8px;'>
            <div style='font-size:20px;font-weight:800;color:white;'>🟢 Affordable</div>
            <div style='font-size:15px;font-weight:700;color:white;margin-top:4px;'>Under ₹30 Lakhs</div>
            <div style='font-size:13px;color:rgba(255,255,255,0.9);margin-top:4px;'>Entry-level homes, budget apartments</div>
        </div>""", unsafe_allow_html=True)
    with g2:
        st.markdown("""<div style='background:linear-gradient(135deg,#2563eb,#3b82f6);
            border-radius:12px;padding:16px;color:white;margin-bottom:8px;'>
            <div style='font-size:20px;font-weight:800;color:white;'>🔵 Mid-Range</div>
            <div style='font-size:15px;font-weight:700;color:white;margin-top:4px;'>₹30L – ₹80 Lakhs</div>
            <div style='font-size:13px;color:rgba(255,255,255,0.9);margin-top:4px;'>Standard flats, suburban homes</div>
        </div>""", unsafe_allow_html=True)
    g3, g4 = st.columns(2)
    with g3:
        st.markdown("""<div style='background:linear-gradient(135deg,#d97706,#f59e0b);
            border-radius:12px;padding:16px;color:white;margin-bottom:8px;'>
            <div style='font-size:20px;font-weight:800;color:white;'>🟡 Premium</div>
            <div style='font-size:15px;font-weight:700;color:white;margin-top:4px;'>₹80L – ₹2 Crore</div>
            <div style='font-size:13px;color:rgba(255,255,255,0.9);margin-top:4px;'>High-end city apartments</div>
        </div>""", unsafe_allow_html=True)
    with g4:
        st.markdown("""<div style='background:linear-gradient(135deg,#be185d,#ec4899);
            border-radius:12px;padding:16px;color:white;margin-bottom:8px;'>
            <div style='font-size:20px;font-weight:800;color:white;'>💎 Luxury</div>
            <div style='font-size:15px;font-weight:700;color:white;margin-top:4px;'>Above ₹2 Crore</div>
            <div style='font-size:13px;color:rgba(255,255,255,0.9);margin-top:4px;'>Villas, penthouses, prime locations</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔮 Run AI Property Valuation", use_container_width=True):

        # Validations
        if model is None:
            st.error("❌ Model files not found. Place `house_model.pkl` and `model_columns.pkl` in the project folder.")
        elif state == "— Select State —":
            st.warning("⚠️ Please select your state from the dropdown.")
        elif not city.strip():
            st.warning("⚠️ City is required. Enter it manually or auto-fill via pincode.")
        elif area < 100:
            st.warning("⚠️ Please enter a valid area (minimum 100 sq ft).")
        else:
            # Save media files
            media_names = []
            if photos:
                for i, ph in enumerate(photos):
                    fname = f"photo_{st.session_state.user}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}.jpg"
                    with open(os.path.join("property_media", fname), "wb") as f:
                        f.write(ph.getvalue())
                    media_names.append(fname)
            if video:
                ext  = video.name.split(".")[-1]
                fname = f"video_{st.session_state.user}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                with open(os.path.join("property_media", fname), "wb") as f:
                    f.write(video.getvalue())
                media_names.append(fname)

            # Get coordinates — use pincode coords or geocode from address
            if lat == 0.0 or lon == 0.0:
                with st.spinner("📍 Locating property on map…"):
                    lat, lon = geocode_address(city, state, country)

            inputs = dict(
                country=country, state=state, city=city, pincode=pincode,
                area=float(area),     bedrooms=int(bedrooms),
                bathrooms=int(bathrooms), stories=int(stories),
                parking=int(parking), mainroad=mainroad,
                guestroom=guestroom,  basement=basement,
                hotwaterheating=hotwaterheating, airconditioning=airconditioning,
                prefarea=prefarea,    furnishing=furnishing,
            )

            with st.spinner("🤖 Running AI valuation…"):
                input_df   = build_input(inputs)
                prediction = float(model.predict(input_df)[0])
                segment, emoji = price_segment(prediction)
                low  = prediction * 0.90
                high = prediction * 1.10
                ppsf = prediction / area
                save_prediction(
                    st.session_state.user, inputs,
                    prediction, segment, lat, lon,
                    ",".join(media_names)
                )
                get_history.clear()
                # ✅ Store result in session_state so it persists across reruns
                st.session_state.result = {
                    "prediction": prediction, "segment": segment,
                    "emoji": emoji, "low": low, "high": high,
                    "ppsf": ppsf, "area": area, "bedrooms": bedrooms,
                    "bathrooms": bathrooms, "city": city, "state": state,
                    "lat": lat, "lon": lon,
                }
                time.sleep(0.3)
            st.markdown("""
<script>
// Confetti effect
const colors = ['#1d4ed8','#10b981','#f59e0b','#ec4899','#8b5cf6','#ef4444'];
for(let i=0;i<120;i++){
    const el=document.createElement('div');
    el.style.cssText=`position:fixed;top:-10px;left:${Math.random()*100}vw;
        width:${6+Math.random()*8}px;height:${6+Math.random()*8}px;
        background:${colors[Math.floor(Math.random()*colors.length)]};
        border-radius:50%;z-index:9999;pointer-events:none;
        animation:fall ${1.5+Math.random()*2}s ease-in forwards;
        transform:rotate(${Math.random()*360}deg);`;
    document.body.appendChild(el);
    setTimeout(()=>el.remove(),4000);
}
const style=document.createElement('style');
style.textContent=`@keyframes fall{to{top:110vh;transform:rotate(${Math.random()*720}deg);}}`;
document.head.appendChild(style);
</script>
""", unsafe_allow_html=True)

    # ── RESULT — shown persistently until new valuation ──────────
    if st.session_state.result:
        r = st.session_state.result
        prediction = r["prediction"]
        segment    = r["segment"]
        emoji      = r["emoji"]
        low        = r["low"]
        high       = r["high"]
        ppsf       = r["ppsf"]
        area       = r["area"]
        bedrooms   = r["bedrooms"]
        bathrooms  = r["bathrooms"]
        city       = r["city"]
        state      = r["state"]
        lat        = r["lat"]
        lon        = r["lon"]

        st.markdown("---")
        st.markdown("### 🏠 Valuation Result")

        rc1, rc2, rc3 = st.columns([2, 1, 1])
        rc1.metric(
            label="Predicted Price",
            value=f"₹{prediction:,.0f}",
            delta=f"Range: ₹{low:,.0f} – ₹{high:,.0f}"
        )
        rc2.metric("Price / Sq Ft", f"₹{ppsf:,.0f}")
        rc3.metric("Config", f"{bedrooms} BHK · {bathrooms} Bath")

        # Segment coloured banner — vivid unique colors
        seg_styles = {
            "Affordable": ("background:linear-gradient(135deg,#059669,#10b981)", "🟢", "Under ₹30 Lakhs", "Entry-level / budget property. Great for first-time buyers.", "white"),
            "Mid-Range":  ("background:linear-gradient(135deg,#2563eb,#3b82f6)", "🔵", "₹30L to ₹80 Lakhs", "Standard residential property with good amenities.", "white"),
            "Premium":    ("background:linear-gradient(135deg,#d97706,#f59e0b)", "🟡", "₹80L to ₹2 Crore", "High-end city property with modern facilities.", "white"),
            "Luxury":     ("background:linear-gradient(135deg,#be185d,#ec4899)", "💎", "Above ₹2 Crore", "Premium villa / penthouse in a prime location.", "white"),
        }
        style, s_emoji, s_range, s_desc, s_color = seg_styles.get(segment, seg_styles["Mid-Range"])
        st.markdown(f"""
        <div style='{style};border-radius:14px;padding:20px 24px;margin:12px 0;
             box-shadow:0 4px 20px rgba(0,0,0,0.15);'>
            <div style='font-size:22px;font-weight:800;color:white;'>
                {s_emoji} {segment} Segment
            </div>
            <div style='font-size:16px;color:rgba(255,255,255,0.95);font-weight:600;margin-top:4px;'>
                {s_range}
            </div>
            <div style='font-size:14px;color:rgba(255,255,255,0.85);margin-top:6px;'>
                {s_desc}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Segment progress bar
        st.caption("📊 Price Segment Position")
        seg_pct = {"Affordable": 12, "Mid-Range": 37, "Premium": 68, "Luxury": 95}
        st.progress(seg_pct.get(segment, 50))
        # 2 cols for mobile — 4 labels split across 2 rows
        sl1, sl2 = st.columns(2)
        sl1.caption("🟢 Affordable  < ₹30L")
        sl2.caption("🔵 Mid-Range  ₹30–80L")
        sl3, sl4 = st.columns(2)
        sl3.caption("🟡 Premium  ₹80L–2Cr")
        sl4.caption("🔴 Luxury  > ₹2Cr")

        st.markdown("---")

        # Property map
        if lat != 0.0 and lon != 0.0:
            st.markdown('<div class="sec-head">📍 Property Location on Map</div>', unsafe_allow_html=True)
            rmap = folium.Map(location=[lat, lon], zoom_start=14, tiles="CartoDB positron")
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(
                    f"<b>{city}, {state}</b><br>"
                    f"💰 ₹{prediction:,.0f}<br>"
                    f"📐 {area} sq ft · {bedrooms} BHK<br>"
                    f"{emoji} {segment}",
                    max_width=210
                ),
                icon=folium.Icon(color="blue", icon="home", prefix="fa")
            ).add_to(rmap)
            folium.Circle(
                location=[lat, lon], radius=600,
                color="#1d4ed8", fill=True, fill_opacity=0.08
            ).add_to(rmap)
            st_folium(rmap, use_container_width=True, height=380, key="result_map")

# ════════════════════════════════════════════════════════════════
#  TAB 2 — ANALYTICS
# ════════════════════════════════════════════════════════════════
with tab_analytics:
    st.subheader("📈 Market Analytics Dashboard")

    if df_hist.empty:
        st.info("📊 Run your first valuation to unlock analytics.")
    else:
        # KPI metrics — 2 per row for mobile friendliness
        k1, k2 = st.columns(2)
        k1.metric("Total Valuations",    f"{len(df_hist):,}")
        k2.metric("Avg Predicted Price", f"₹{df_hist['predicted_price'].mean():,.0f}")
        k3, k4 = st.columns(2)
        k3.metric("Avg Area",            f"{df_hist['area'].mean():,.0f} sq ft")
        k4.metric("Avg Price / Sq Ft",   f"₹{df_hist['price_per_sqft'].mean():,.0f}")

        st.markdown("---")

        SEG_COLORS = {
            "Affordable": "#10b981",
            "Mid-Range":  "#3b82f6",
            "Premium":    "#f59e0b",
            "Luxury":     "#ec4899",
        }

        ch1, ch2 = st.columns(2)

        # Chart 1 — State-wise bar
        fig1 = px.bar(
            df_hist, x="state", y="predicted_price", color="segment",
            barmode="group", title="🏙️ State-wise Price Distribution",
            color_discrete_map=SEG_COLORS,
            labels={"predicted_price": "Price (₹)", "state": "State"}
        )
        fig1.update_layout(
            paper_bgcolor="white", plot_bgcolor="#f0f9ff",
            font_family="Inter", title_font_size=15,
            font=dict(color="#1e293b"),
            legend_title="Segment",
            xaxis=dict(tickangle=-30)
        )
        ch1.plotly_chart(fig1, use_container_width=True)

        # Chart 2 — Scatter
        fig2 = px.scatter(
            df_hist, x="area", y="predicted_price", color="segment",
            size="bedrooms", hover_data=["city","bedrooms","furnishing"],
            title="📐 Area vs Predicted Price",
            color_discrete_map=SEG_COLORS,
            labels={"predicted_price": "Price (₹)", "area": "Area (sq ft)"}
        )
        fig2.update_layout(
            paper_bgcolor="white", plot_bgcolor="#fdf4ff",
            font_family="Inter", title_font_size=15,
            font=dict(color="#1e293b")
        )
        ch2.plotly_chart(fig2, use_container_width=True)

        # Chart 3 — Furnishing (only show if multiple furnishing types)
        if df_hist["furnishing"].nunique() > 1:
            fig3 = px.box(
                df_hist, x="furnishing", y="predicted_price", color="furnishing",
                title="🛋️ Price by Furnishing Status",
                color_discrete_sequence=["#8b5cf6", "#06b6d4", "#f43f5e"],
                labels={"predicted_price": "Price (₹)", "furnishing": "Furnishing"}
            )
        else:
            fig3 = px.bar(
                df_hist, x="furnishing", y="predicted_price", color="furnishing",
                title="🛋️ Price by Furnishing Status",
                color_discrete_sequence=["#8b5cf6"],
                labels={"predicted_price": "Price (₹)", "furnishing": "Furnishing"}
            )
        fig3.update_layout(
            paper_bgcolor="white", plot_bgcolor="#fefce8",
            font_family="Inter", showlegend=False, title_font_size=15,
            font=dict(color="#1e293b")
        )
        st.plotly_chart(fig3, use_container_width=True)

        # Chart 4 — Segment count
        seg_count = df_hist.groupby("segment")["predicted_price"].count().reset_index()
        seg_count.columns = ["segment", "count"]
        fig4 = px.bar(
            seg_count, x="segment", y="count", color="segment",
            title="🏷️ Valuations by Market Segment",
            color_discrete_map=SEG_COLORS,
            labels={"count": "Number of Valuations", "segment": "Segment"},
            text="count"
        )
        fig4.update_traces(textposition="outside", textfont_size=14)
        fig4.update_layout(
            paper_bgcolor="white", plot_bgcolor="#f0fdf4",
            font_family="Inter", showlegend=False, title_font_size=15,
            font=dict(color="#1e293b")
        )
        st.plotly_chart(fig4, use_container_width=True)

        with st.expander("📋 Full Prediction History"):
            show_cols = ["timestamp","city","state","area","bedrooms",
                         "bathrooms","furnishing","predicted_price","segment"]
            avail = [c for c in show_cols if c in df_hist.columns]
            st.dataframe(
                df_hist[avail].rename(columns={"predicted_price":"Price (₹)"}),
                use_container_width=True, hide_index=True
            )

# ════════════════════════════════════════════════════════════════
#  TAB 3 — MAP EXPLORER
# ════════════════════════════════════════════════════════════════
with tab_map:
    st.subheader("📍 All Property Locations")
    st.caption("Every property valuation with location data is plotted here. Click a pin for details.")

    df_map = pd.DataFrame()
    if not df_hist.empty:
        df_map = df_hist[
            df_hist["lat"].notna() & df_hist["lon"].notna() &
            (df_hist["lat"] != 0)  & (df_hist["lon"] != 0)
        ].copy()

    if df_map.empty:
        st.info("📍 Properties will appear here after valuations with location data.")
        m = folium.Map(location=[20.5, 78.9], zoom_start=5, tiles="CartoDB positron")
    else:
        m = folium.Map(
            location=[df_map["lat"].mean(), df_map["lon"].mean()],
            zoom_start=6, tiles="CartoDB positron"
        )
        SEG_COLOR = {"Affordable":"green","Mid-Range":"orange",
                     "Premium":"darkred","Luxury":"red"}
        SEG_EMOJI = {"Affordable":"🟢","Mid-Range":"🟡","Premium":"🟠","Luxury":"🔴"}

        for _, row in df_map.iterrows():
            color = SEG_COLOR.get(row["segment"], "blue")
            emoji = SEG_EMOJI.get(row["segment"], "🏠")

            # Inline photo thumbnail if available
            media_html = ""
            if row.get("media_paths"):
                paths = [p.strip() for p in str(row["media_paths"]).split(",") if p.strip()]
                for p in paths[:1]:
                    fp = os.path.join("property_media", p)
                    if os.path.exists(fp) and p.lower().endswith((".jpg",".jpeg",".png")):
                        with open(fp,"rb") as f:
                            b64 = base64.b64encode(f.read()).decode()
                        media_html = (
                            f'<br><img src="data:image/jpeg;base64,{b64}" '
                            f'width="180" style="border-radius:6px;margin-top:6px;"/>'
                        )

            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=folium.Popup(
                    f"<b>{row.get('city','')}, {row.get('state','')}</b><br>"
                    f"💰 ₹{row['predicted_price']:,.0f}<br>"
                    f"📐 {row['area']} sq ft · {row['bedrooms']} BHK<br>"
                    f"🛁 {row['bathrooms']} Bath · {row['stories']} Floor(s)<br>"
                    f"🛋️ {row.get('furnishing','')}<br>"
                    f"{emoji} {row['segment']}<br>"
                    f"👤 {row.get('username','')}"
                    f"{media_html}",
                    max_width=230
                ),
                icon=folium.Icon(color=color, icon="home", prefix="fa")
            ).add_to(m)

        # Map legend
        m.get_root().html.add_child(folium.Element("""
        <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
             background:white;padding:12px 18px;border-radius:10px;
             box-shadow:0 2px 14px rgba(0,0,0,0.15);font-size:13px;
             font-family:Inter,sans-serif;border:1px solid #e0e7ff;">
            <b style='color:#1e3a8a;'>Market Segment</b><br><br>
            🟢 Affordable &nbsp;&nbsp; 🟡 Mid-Range<br>
            🟠 Premium &nbsp;&nbsp;&nbsp; 🔴 Luxury
        </div>
        """))

    st_folium(m, use_container_width=True, height=580, key="explorer_map")

# ── FOOTER ───────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;color:#9ca3af;font-size:12px;
     margin-top:40px;padding:16px 0;border-top:1px solid #e0e7ff;'>
    🏙️ ProProperty AI &nbsp;·&nbsp;
    ML-Powered Real Estate Valuation &nbsp;·&nbsp; 
</div>
""", unsafe_allow_html=True)
