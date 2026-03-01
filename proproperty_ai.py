
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

# ════════════════════════════════════════════════════════════════
#  GLOBAL STYLES — Bold, vibrant, fully mobile-first
# ════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

/* ── CSS DESIGN TOKENS ── */
:root {
    --navy:      #0a1628;
    --blue:      #1648ff;
    --blue-mid:  #2d6cff;
    --blue-lite: #e8efff;
    --cyan:      #00d4ff;
    --emerald:   #00c896;
    --amber:     #ffb300;
    --rose:      #ff3d6b;
    --violet:    #8b5cf6;
    --gold:      #f0a500;
    --bg:        #f2f5ff;
    --surface:   #ffffff;
    --border:    #dde3f5;
    --text:      #0d1f3c;
    --muted:     #5a6a8a;
    --radius-lg: 18px;
    --radius-md: 12px;
    --shadow-sm: 0 2px 12px rgba(22,72,255,0.08);
    --shadow-md: 0 6px 28px rgba(22,72,255,0.13);
    --shadow-lg: 0 12px 48px rgba(22,72,255,0.18);
}

/* ── BASE ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
html, body { overflow-x: hidden !important; max-width: 100vw !important; }
.main .block-container {
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
    max-width: 100% !important;
}

/* ── FORCE DARK TEXT everywhere (override Streamlit defaults) ── */
p, span, h1, h2, h3, h4, h5, h6, li, label, div {
    color: var(--text) !important;
}
/* EXCEPTION: text inside coloured gradient banners stays white */
.colored-banner * { color: white !important; }

/* ── SECTION HEADERS — vivid gradient pill ── */
.sec-head {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    font-size: 11px !important;
    font-weight: 800 !important;
    color: var(--blue) !important;
    text-transform: uppercase !important;
    letter-spacing: 1.4px !important;
    background: linear-gradient(120deg, #e8efff 0%, #d4e3ff 100%) !important;
    border-left: 4px solid var(--blue) !important;
    padding: 10px 18px !important;
    border-radius: 0 var(--radius-md) var(--radius-md) 0 !important;
    margin: 24px 0 14px !important;
    word-break: break-word !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 14px !important;
    padding: 5px !important;
    border: 1.5px solid var(--border) !important;
    gap: 3px !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    scrollbar-width: none !important;
    flex-wrap: nowrap !important;
    box-shadow: var(--shadow-sm) !important;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    color: var(--muted) !important;
    padding: 10px 16px !important;
    background: transparent !important;
    white-space: nowrap !important;
    min-width: fit-content !important;
    transition: all 0.18s !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--blue), var(--blue-mid)) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(22,72,255,0.35) !important;
}

/* ── PRIMARY BUTTON (Run Valuation) ── */
.stButton > button {
    background: linear-gradient(135deg, #1648ff, #2d6cff) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-weight: 800 !important;
    font-size: 15px !important;
    letter-spacing: 0.3px !important;
    padding: 14px 20px !important;
    transition: all .22s !important;
    width: 100% !important;
    min-height: 52px !important;
    touch-action: manipulation !important;
    box-shadow: 0 4px 18px rgba(22,72,255,0.35) !important;
    text-shadow: 0 1px 3px rgba(0,0,0,0.15) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(22,72,255,0.45) !important;
}
/* Logout button — cool white/outline style */
div[data-testid="column"]:last-child .stButton > button {
    background: rgba(255,255,255,0.15) !important;
    backdrop-filter: blur(10px) !important;
    color: white !important;
    border: 1.5px solid rgba(255,255,255,0.4) !important;
    font-size: 13px !important;
    padding: 10px 14px !important;
    min-height: 44px !important;
    box-shadow: none !important;
    text-shadow: none !important;
}

/* ── INPUT LABELS ── */
.stTextInput label, .stSelectbox label,
.stNumberInput label, .stFileUploader label {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    display: block !important;
    margin-bottom: 5px !important;
}

/* ── INPUT FIELDS — vivid focus border ── */
.stTextInput input, .stNumberInput input {
    border-radius: var(--radius-md) !important;
    border: 2px solid var(--border) !important;
    font-size: 16px !important;
    color: var(--text) !important;
    background: var(--surface) !important;
    min-height: 48px !important;
    -webkit-appearance: none !important;
    appearance: none !important;
    transition: border-color 0.18s !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(22,72,255,0.12) !important;
}
.stSelectbox > div > div {
    font-size: 16px !important;
    min-height: 48px !important;
    border-radius: var(--radius-md) !important;
    border: 2px solid var(--border) !important;
}

/* ── TOGGLES ── */
[data-testid="stToggleLabel"], .stCheckbox label {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: var(--text) !important;
}
[data-testid="stToggle"] { transform: scale(1.1) !important; }

/* ── METRIC CARDS — vivid with colored left border ── */
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-top: 4px solid var(--blue) !important;
    border-radius: var(--radius-lg) !important;
    padding: 16px 14px !important;
    box-shadow: var(--shadow-sm) !important;
    word-break: break-word !important;
    overflow: hidden !important;
    transition: transform 0.18s, box-shadow 0.18s !important;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-md) !important;
}
[data-testid="metric-container"] label {
    font-size: 11px !important;
    color: var(--muted) !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 900 !important;
    color: var(--blue) !important;
    word-break: break-all !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 11px !important;
    word-break: break-word !important;
    color: var(--emerald) !important;
}

/* ── CAPTIONS ── */
.stCaption, [data-testid="caption"] {
    color: var(--muted) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

/* ── PROGRESS BAR — vivid 4-color ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #00c896, #1648ff, #ffb300, #ff3d6b) !important;
    border-radius: 20px !important;
    height: 14px !important;
}
.stProgress > div {
    background: #e2e8f0 !important;
    border-radius: 20px !important;
    height: 14px !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: var(--blue) !important;
    background: var(--blue-lite) !important;
    border-radius: var(--radius-md) !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] { border-radius: var(--radius-md) !important; }
[data-testid="stFileUploader"] section { min-height: 80px !important; padding: 12px !important; }

/* ── PLOTLY / FOLIUM ── */
.js-plotly-plot, .plotly { max-width: 100% !important; overflow: hidden !important; }
.stFolium iframe { width: 100% !important; border-radius: var(--radius-lg) !important; }

/* ── ALERTS / INFO / SUCCESS ── */
[data-testid="stAlert"] { border-radius: var(--radius-md) !important; }

/* ════════════════════════════════════════════
   MOBILE — 768px
   ════════════════════════════════════════════ */
@media (max-width: 768px) {
    [data-testid="column"] {
        width: 100% !important; flex: 1 1 100% !important;
        min-width: 100% !important;
        padding-left: 0 !important; padding-right: 0 !important;
    }
    .main .block-container {
        padding-left: 0.6rem !important; padding-right: 0.6rem !important;
        padding-top: 0.5rem !important;
    }
    .stTextInput input, .stNumberInput input,
    .stSelectbox > div > div { font-size: 16px !important; min-height: 48px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 11px !important; padding: 8px 10px !important; }
    [data-testid="metric-container"] { padding: 12px 10px !important; margin-bottom: 8px !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 18px !important; }
    .stButton > button { min-height: 52px !important; }
    .stFolium iframe { min-height: 280px !important; }
}

/* ════════════════════════════════════════════
   SMALL PHONES — 480px
   ════════════════════════════════════════════ */
@media (max-width: 480px) {
    .main .block-container { padding-left: 0.3rem !important; padding-right: 0.3rem !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 16px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 10px !important; padding: 7px 8px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── MEDIA FOLDER & DATABASE ──────────────────────────────────────
os.makedirs("property_media", exist_ok=True)
DB_PATH = "/tmp/proproperty.db"
@st.cache_resource
def get_engine():
    return create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False},
        pool_size=1,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=300,
    )

engine = get_engine()


def init_db():
    with engine.connect() as con:
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY, password TEXT NOT NULL, created TEXT)
        """))
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT, country TEXT, state TEXT, city TEXT, pincode TEXT,
                area REAL, bedrooms INTEGER, bathrooms INTEGER, stories INTEGER,
                parking INTEGER, mainroad INTEGER, guestroom INTEGER, basement INTEGER,
                hotwaterheating INTEGER, airconditioning INTEGER, prefarea INTEGER,
                furnishing TEXT, predicted_price REAL, price_per_sqft REAL,
                segment TEXT, lat REAL, lon REAL, media_paths TEXT, timestamp TEXT)
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
def hash_pw(pw):   return hashlib.sha256(pw.encode()).hexdigest()
def verify_pw(pw, h): return hash_pw(pw) == h

def user_exists(u):
    with engine.connect() as con:
        return con.execute(text("SELECT 1 FROM users WHERE username=:u"),{"u":u}).fetchone() is not None

def register_user(u, pw):
    if not u.strip():    return False, "Username cannot be empty."
    if user_exists(u):   return False, "Username already taken."
    if len(pw) < 6:      return False, "Password must be at least 6 characters."
    with engine.connect() as con:
        con.execute(text("INSERT INTO users VALUES(:u,:p,:t)"),
                    {"u":u,"p":hash_pw(pw),"t":datetime.now().isoformat()})
        con.commit()
    return True, "ok"

def login_user(u, pw):
    with engine.connect() as con:
        row = con.execute(text("SELECT password FROM users WHERE username=:u"),{"u":u}).fetchone()
    if not row:                  return False, "Username not found."
    if not verify_pw(pw, row[0]):return False, "Incorrect password."
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
    "UK":    ["England","Scotland","Wales","Northern Ireland","London","South East",
              "South West","East of England","East Midlands","West Midlands",
              "Yorkshire","North West","North East"],
    "Canada":["Alberta","British Columbia","Manitoba","New Brunswick",
              "Newfoundland and Labrador","Nova Scotia","Ontario",
              "Prince Edward Island","Quebec","Saskatchewan",
              "Northwest Territories","Nunavut","Yukon"],
    "UAE":   ["Abu Dhabi","Dubai","Sharjah","Ajman","Umm Al Quwain","Ras Al Khaimah","Fujairah"],
    "Australia": ["New South Wales","Victoria","Queensland","South Australia",
                  "Western Australia","Tasmania","Australian Capital Territory","Northern Territory"],
}
COUNTRY_CODES = {"India":"IN","USA":"US","UK":"GB","Canada":"CA","UAE":"AE","Australia":"AU"}

PINCODE_DB = {
    "400001":("Mumbai","Maharashtra",18.9388,72.8354), "400051":("Mumbai","Maharashtra",19.0596,72.8295),
    "400070":("Mumbai","Maharashtra",19.0728,72.8826), "411001":("Pune","Maharashtra",18.5196,73.8553),
    "411014":("Pune","Maharashtra",18.5642,73.9140),   "411057":("Pune","Maharashtra",18.6298,73.7997),
    "440001":("Nagpur","Maharashtra",21.1458,79.0882),  "431001":("Aurangabad","Maharashtra",19.8762,75.3433),
    "422001":("Nashik","Maharashtra",19.9975,73.7898),
    "560001":("Bangalore","Karnataka",12.9716,77.5946), "560034":("Bangalore","Karnataka",12.9352,77.6245),
    "560068":("Bangalore","Karnataka",12.9010,77.6490), "575001":("Mangalore","Karnataka",12.8698,74.8430),
    "580001":("Hubli","Karnataka",15.3647,75.1240),
    "600001":("Chennai","Tamil Nadu",13.0827,80.2707),  "600042":("Chennai","Tamil Nadu",13.0500,80.2120),
    "641001":("Coimbatore","Tamil Nadu",11.0168,76.9558),"625001":("Madurai","Tamil Nadu",9.9252,78.1198),
    "620001":("Tiruchirappalli","Tamil Nadu",10.7905,78.7047),
    "110001":("New Delhi","Delhi",28.6139,77.2090),     "110011":("New Delhi","Delhi",28.5921,77.1645),
    "110034":("Delhi","Delhi",28.7130,77.1475),         "110058":("Delhi","Delhi",28.6508,77.0627),
    "110092":("Delhi","Delhi",28.6692,77.3090),
    "500001":("Hyderabad","Telangana",17.3850,78.4867), "500032":("Hyderabad","Telangana",17.4435,78.3772),
    "500081":("Hyderabad","Telangana",17.4947,78.3996), "506001":("Warangal","Telangana",17.9784,79.5941),
    "380001":("Ahmedabad","Gujarat",23.0225,72.5714),   "380015":("Ahmedabad","Gujarat",23.0395,72.5070),
    "395001":("Surat","Gujarat",21.1702,72.8311),       "390001":("Vadodara","Gujarat",22.3072,73.1812),
    "360001":("Rajkot","Gujarat",22.3039,70.8022),
    "302001":("Jaipur","Rajasthan",26.9124,75.7873),    "302021":("Jaipur","Rajasthan",26.8467,75.8070),
    "313001":("Udaipur","Rajasthan",24.5854,73.7125),   "342001":("Jodhpur","Rajasthan",26.2389,73.0243),
    "226001":("Lucknow","Uttar Pradesh",26.8467,80.9462),"226010":("Lucknow","Uttar Pradesh",26.8728,80.9942),
    "201001":("Ghaziabad","Uttar Pradesh",28.6692,77.4538),"211001":("Prayagraj","Uttar Pradesh",25.4358,81.8463),
    "282001":("Agra","Uttar Pradesh",27.1767,78.0081),  "221001":("Varanasi","Uttar Pradesh",25.3176,82.9739),
    "700001":("Kolkata","West Bengal",22.5726,88.3639),  "700054":("Kolkata","West Bengal",22.5200,88.3700),
    "700102":("Kolkata","West Bengal",22.6200,88.4300),
    "160001":("Chandigarh","Chandigarh",30.7333,76.7794),"141001":("Ludhiana","Punjab",30.9010,75.8573),
    "143001":("Amritsar","Punjab",31.6340,74.8723),
    "682001":("Kochi","Kerala",9.9312,76.2673),          "695001":("Thiruvananthapuram","Kerala",8.5241,76.9366),
    "673001":("Kozhikode","Kerala",11.2588,75.7804),
    "462001":("Bhopal","Madhya Pradesh",23.2599,77.4126),"452001":("Indore","Madhya Pradesh",22.7196,75.8577),
    "474001":("Gwalior","Madhya Pradesh",26.2183,78.1828),
    "122001":("Gurgaon","Haryana",28.4595,77.0266),     "121001":("Faridabad","Haryana",28.4089,77.3178),
    "132001":("Karnal","Haryana",29.6857,76.9905),
    "520001":("Vijayawada","Andhra Pradesh",16.5062,80.6480),"530001":("Visakhapatnam","Andhra Pradesh",17.6868,83.2185),
    "751001":("Bhubaneswar","Odisha",20.2961,85.8245),   "753001":("Cuttack","Odisha",20.4625,85.8830),
    "800001":("Patna","Bihar",25.5941,85.1376),          "781001":("Guwahati","Assam",26.1445,91.7362),
    "834001":("Ranchi","Jharkhand",23.3441,85.3096),     "248001":("Dehradun","Uttarakhand",30.3165,78.0322),
    "171001":("Shimla","Himachal Pradesh",31.1048,77.1734),"403001":("Panaji","Goa",15.4909,73.8278),
}

CITY_COORDS = {
    "mumbai":(18.9388,72.8354),"pune":(18.5196,73.8553),"bangalore":(12.9716,77.5946),
    "bengaluru":(12.9716,77.5946),"chennai":(13.0827,80.2707),"hyderabad":(17.3850,78.4867),
    "delhi":(28.6139,77.2090),"new delhi":(28.6139,77.2090),"kolkata":(22.5726,88.3639),
    "ahmedabad":(23.0225,72.5714),"surat":(21.1702,72.8311),"jaipur":(26.9124,75.7873),
    "lucknow":(26.8467,80.9462),"nagpur":(21.1458,79.0882),"patna":(25.5941,85.1376),
    "indore":(22.7196,75.8577),"bhopal":(23.2599,77.4126),"visakhapatnam":(17.6868,83.2185),
    "vadodara":(22.3072,73.1812),"ghaziabad":(28.6692,77.4538),"ludhiana":(30.9010,75.8573),
    "agra":(27.1767,78.0081),"nashik":(19.9975,73.7898),"vijayawada":(16.5062,80.6480),
    "rajkot":(22.3039,70.8022),"meerut":(28.9845,77.7064),"coimbatore":(11.0168,76.9558),
    "chandigarh":(30.7333,76.7794),"amritsar":(31.6340,74.8723),"gurgaon":(28.4595,77.0266),
    "gurugram":(28.4595,77.0266),"noida":(28.5355,77.3910),"kochi":(9.9312,76.2673),
    "bhubaneswar":(20.2961,85.8245),"dehradun":(30.3165,78.0322),"ranchi":(23.3441,85.3096),
    "guwahati":(26.1445,91.7362),"thiruvananthapuram":(8.5241,76.9366),
    "mangalore":(12.8698,74.8430),"hubli":(15.3647,75.1240),"madurai":(9.9252,78.1198),
    "varanasi":(25.3176,82.9739),"udaipur":(24.5854,73.7125),"jodhpur":(26.2389,73.0243),
    "gwalior":(26.2183,78.1828),"faridabad":(28.4089,77.3178),"panaji":(15.4909,73.8278),
    "shimla":(31.1048,77.1734),"aurangabad":(19.8762,75.3433),"warangal":(17.9784,79.5941),
    "kozhikode":(11.2588,75.7804),"tiruchirappalli":(10.7905,78.7047),
    "prayagraj":(25.4358,81.8463),"allahabad":(25.4358,81.8463),"cuttack":(20.4625,85.8830),
    "karnal":(29.6857,76.9905),
    "new york":(40.7128,-74.0060),"los angeles":(34.0522,-118.2437),"chicago":(41.8781,-87.6298),
    "houston":(29.7604,-95.3698),"phoenix":(33.4484,-112.0740),"philadelphia":(39.9526,-75.1652),
    "san antonio":(29.4241,-98.4936),"san diego":(32.7157,-117.1611),"dallas":(32.7767,-96.7970),
    "san francisco":(37.7749,-122.4194),"seattle":(47.6062,-122.3321),"boston":(42.3601,-71.0589),
    "miami":(25.7617,-80.1918),"atlanta":(33.7490,-84.3880),
    "london":(51.5074,-0.1278),"manchester":(53.4808,-2.2426),"birmingham":(52.4862,-1.8904),
    "glasgow":(55.8642,-4.2518),"edinburgh":(55.9533,-3.1883),
    "dubai":(25.2048,55.2708),"abu dhabi":(24.4539,54.3773),"sharjah":(25.3463,55.4209),
}


def lookup_pincode(pincode, cc="IN"):
    if pincode in PINCODE_DB:
        city, state, lat, lon = PINCODE_DB[pincode]
        return {"city": city, "state": state, "lat": lat, "lon": lon}
    try:
        r = requests.get(f"https://api.zippopotam.us/{cc}/{pincode}", timeout=4)
        if r.status_code == 200:
            place = r.json()["places"][0]
            return {"city": place.get("place name",""), "state": place.get("state",""),
                    "lat": float(place.get("latitude",0)), "lon": float(place.get("longitude",0))}
    except Exception:
        pass
    return {}


def geocode_address(city, state, country):
    key = city.strip().lower()
    if key in CITY_COORDS:
        return CITY_COORDS[key]
    for name, coords in CITY_COORDS.items():
        if key in name or name in key:
            return coords
    try:
        r = requests.get("https://nominatim.openstreetmap.org/search",
                         params={"q": f"{city},{state},{country}", "format": "json", "limit": 1},
                         headers={"User-Agent": "ProPropertyAI/1.0"}, timeout=5)
        if r.status_code == 200 and r.json():
            d = r.json()[0]
            return float(d["lat"]), float(d["lon"])
    except Exception:
        pass
    return 0.0, 0.0


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
    if   p < 3_000_000:  return "Affordable", "🟢"
    elif p < 8_000_000:  return "Mid-Range",   "🟡"
    elif p < 20_000_000: return "Premium",     "🟠"
    else:                return "Luxury",       "🔴"


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
            "username":username,"country":inp["country"],"state":inp["state"],
            "city":inp["city"],"pincode":inp["pincode"],"area":inp["area"],
            "bedrooms":inp["bedrooms"],"bathrooms":inp["bathrooms"],"stories":inp["stories"],
            "parking":inp["parking"],"mainroad":int(inp["mainroad"]),"guestroom":int(inp["guestroom"]),
            "basement":int(inp["basement"]),"hotwaterheating":int(inp["hotwaterheating"]),
            "airconditioning":int(inp["airconditioning"]),"prefarea":int(inp["prefarea"]),
            "furnishing":inp["furnishing"],"price":price,"ppsf":ppsf,
            "segment":segment,"lat":lat,"lon":lon,"media":media_paths,
            "ts":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        con.commit()


# ── SESSION STATE ────────────────────────────────────────────────
defaults = {
    "logged_in": False, "user": "", "page": "login",
    "auto_city": "", "auto_lat": 0.0, "auto_lon": 0.0, "_last_pin": "",
    "result": None
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════════════════════════════
#  AUTH SCREENS — Deep navy + electric blue + coral accent
# ════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:

    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(145deg, #020b18 0%, #061433 40%, #0a2070 75%, #1648ff 100%) !important;
    }
    .stTextInput label { color: rgba(255,255,255,0.9) !important; font-weight: 700 !important; }
    .stTextInput input {
        background: rgba(255,255,255,0.08) !important;
        color: white !important;
        border: 1.5px solid rgba(255,255,255,0.25) !important;
        border-radius: 12px !important;
    }
    .stTextInput input:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 0 3px rgba(0,212,255,0.2) !important;
    }
    .stTextInput input::placeholder { color: rgba(255,255,255,0.4) !important; }
    .stButton > button {
        background: linear-gradient(135deg, #1648ff, #00d4ff) !important;
        box-shadow: 0 6px 24px rgba(22,72,255,0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── HERO ─────────────────────────────────────────────────────
    st.markdown("""
    <div style='text-align:center;padding:clamp(24px,6vw,56px) 16px 24px;'>
        <div style='font-size:clamp(52px,11vw,80px);filter:drop-shadow(0 4px 20px rgba(22,72,255,0.6));'>🏙️</div>
        <div style='font-size:clamp(28px,7vw,52px);font-weight:900;color:white;
             letter-spacing:-1.5px;margin-top:12px;line-height:1.1;'>
            ProProperty
            <span style='background:linear-gradient(135deg,#00d4ff,#1648ff);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  background-clip:text;'>AI</span>
        </div>
        <div style='color:rgba(255,255,255,0.7);font-size:clamp(13px,3vw,17px);
             margin-top:10px;font-weight:500;letter-spacing:0.3px;'>
            ML-Powered Real Estate Valuation Platform
        </div>
        <div style='display:flex;justify-content:center;gap:10px;margin-top:20px;flex-wrap:wrap;padding:0 8px;'>
            <span style='background:rgba(22,72,255,0.3);border:1px solid rgba(0,212,255,0.4);
                border-radius:50px;padding:8px 16px;font-size:clamp(11px,2.5vw,13px);
                color:#00d4ff;font-weight:700;backdrop-filter:blur(8px);'>
                ⚡ Instant AI Prediction
            </span>
            <span style='background:rgba(0,200,150,0.2);border:1px solid rgba(0,200,150,0.4);
                border-radius:50px;padding:8px 16px;font-size:clamp(11px,2.5vw,13px);
                color:#00c896;font-weight:700;backdrop-filter:blur(8px);'>
                📍 Live Location Map
            </span>
            <span style='background:rgba(255,179,0,0.2);border:1px solid rgba(255,179,0,0.4);
                border-radius:50px;padding:8px 16px;font-size:clamp(11px,2.5vw,13px);
                color:#ffb300;font-weight:700;backdrop-filter:blur(8px);'>
                📊 Market Analytics
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    mid = st.container()
    with mid:

        # ── LOGIN ─────────────────────────────────────────────
        if st.session_state.page == "login":
            st.markdown("""
            <div style='background:rgba(255,255,255,0.06);backdrop-filter:blur(24px);
                border:1.5px solid rgba(0,212,255,0.2);border-radius:22px;
                padding:clamp(20px,5vw,32px) clamp(16px,4vw,28px);
                text-align:center;margin-bottom:20px;'>
                <div style='font-size:clamp(22px,5vw,30px);font-weight:900;color:white;'>
                    Welcome Back 👋
                </div>
                <div style='font-size:clamp(13px,3vw,15px);color:rgba(255,255,255,0.65);margin-top:6px;'>
                    Sign in to continue
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

        # ── REGISTER ──────────────────────────────────────────
        elif st.session_state.page == "register":
            st.markdown("""
            <div style='background:rgba(255,255,255,0.06);backdrop-filter:blur(24px);
                border:1.5px solid rgba(0,200,150,0.3);border-radius:22px;
                padding:clamp(20px,5vw,32px) clamp(16px,4vw,28px);
                text-align:center;margin-bottom:20px;'>
                <div style='font-size:clamp(22px,5vw,30px);font-weight:900;color:white;'>
                    Create Account 🚀
                </div>
                <div style='font-size:clamp(13px,3vw,15px);color:rgba(255,255,255,0.65);margin-top:6px;'>
                    Join ProProperty AI — it's free!
                </div>
            </div>
            """, unsafe_allow_html=True)

            ru  = st.text_input("👤 Username",         placeholder="Choose a username",      key="re_u")
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
                        st.error("❌ Username already taken.")

            if st.button("← Back to Login", use_container_width=True, key="back_login"):
                st.session_state.page = "login"
                st.rerun()

    st.stop()

# ════════════════════════════════════════════════════════════════
#  MAIN DASHBOARD
# ════════════════════════════════════════════════════════════════

# ── VIBRANT TOP NAV BAR ──────────────────────────────────────────
tn1, tn2 = st.columns([5, 1])
tn1.markdown(f"""
<div style='background:linear-gradient(135deg,#061433,#0a2070,#1648ff);
     padding:clamp(10px,2vw,16px) clamp(14px,3vw,24px);border-radius:16px;
     box-shadow:0 6px 28px rgba(22,72,255,0.35);
     border:1px solid rgba(0,212,255,0.15);'>
    <div style='display:flex;align-items:center;gap:10px;'>
        <span style='font-size:clamp(20px,4vw,28px);'>🏙️</span>
        <div>
            <div style='font-size:clamp(15px,3.2vw,20px);font-weight:900;color:white;
                 letter-spacing:-0.3px;text-shadow:0 2px 8px rgba(0,0,0,0.3);'>
                ProProperty
                <span style='background:linear-gradient(90deg,#00d4ff,#a8edff);
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                      background-clip:text;'>AI</span>
            </div>
            <div style='font-size:clamp(10px,2vw,12px);color:rgba(255,255,255,0.7);
                 font-weight:600;margin-top:1px;'>
                👤 {st.session_state.user}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
if tn2.button("🚪 Logout"):
    for k in defaults:
        st.session_state[k] = defaults[k]
    st.rerun()

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)



@st.cache_data(ttl=20)
def get_history():
    try:
        # Use an explicit connection context manager to ensure it closes
        with engine.connect() as con:
            return pd.read_sql(text("SELECT * FROM predictions ORDER BY timestamp DESC"), con)
    except Exception:
        return pd.DataFrame()


df_hist = get_history()

tab_val, tab_analytics, tab_map = st.tabs([
    "💎 Valuation", "📈 Analytics", "📍 Map"
])

# ════════════════════════════════════════════════════════════════
#  TAB 1 — VALUATION
# ════════════════════════════════════════════════════════════════
with tab_val:

    st.markdown('<div class="sec-head">📍 &nbsp;Location Details</div>', unsafe_allow_html=True)

    lc1, lc2 = st.columns(2)
    country = lc1.selectbox("🌍 Country", list(COUNTRY_STATES.keys()))
    state   = lc2.selectbox("🗺️ State / Province",
                             ["— Select State —"] + COUNTRY_STATES.get(country, []))

    lc3, lc4 = st.columns(2)
    pincode = lc3.text_input("📮 Pincode / ZIP", placeholder="Auto-fills city")

    if pincode and len(pincode.strip()) >= 4 and pincode != st.session_state["_last_pin"]:
        cc = COUNTRY_CODES.get(country, "IN")
        with st.spinner("🔍 Auto-detecting city…"):
            res = lookup_pincode(pincode.strip(), cc)
        if res:
            st.session_state.auto_city = res.get("city", "")
            st.session_state.auto_lat  = res.get("lat",  0.0)
            st.session_state.auto_lon  = res.get("lon",  0.0)
            st.session_state["_last_pin"] = pincode
            lc4.success(f"📍 **{st.session_state.auto_city}**")
        else:
            lc4.info("ℹ️ Not found — enter city below.")
            st.session_state["_last_pin"] = pincode

    city = lc4.text_input("🏙️ City", value=st.session_state.auto_city,
                          placeholder="Auto-filled from pincode")

    # ── PROPERTY DETAILS ─────────────────────────────────────────
    st.markdown('<div class="sec-head">📐 &nbsp;Property Details</div>', unsafe_allow_html=True)

    pd1, pd2 = st.columns(2)
    area      = pd1.number_input("📏 Area (sq ft)", 100, 50000, 1200, step=50)
    bedrooms  = pd2.number_input("🛏️ Bedrooms",       1,    10,    3)

    pd3, pd4 = st.columns(2)
    bathrooms = pd3.number_input("🚿 Bathrooms",       1,    10,    2)
    stories   = pd4.number_input("🏢 Floors",          1,    10,    2)

    pd5, pd6 = st.columns(2)
    parking    = pd5.number_input("🚗 Parking",        0,     5,    1)
    furnishing = pd6.selectbox("🛋️ Furnishing",
                               ["Fully Furnished", "Semi-Furnished", "Unfurnished"])

    # ── AMENITIES ────────────────────────────────────────────────
    st.markdown('<div class="sec-head">✅ &nbsp;Property Amenities</div>', unsafe_allow_html=True)
    st.caption("Toggle all features that apply to this property:")

    am1, am2 = st.columns(2)
    mainroad        = am1.toggle("🛣️ Main Road",   value=True)
    guestroom       = am2.toggle("🛏️ Guest Room")

    am3, am4 = st.columns(2)
    basement        = am3.toggle("🏚️ Basement")
    hotwaterheating = am4.toggle("🔥 Hot Water")

    am5, am6 = st.columns(2)
    airconditioning = am5.toggle("❄️ AC")
    prefarea        = am6.toggle("⭐ Preferred Area")

    # ── MEDIA UPLOAD ─────────────────────────────────────────────
    st.markdown('<div class="sec-head">📸 &nbsp;Property Media (Optional)</div>', unsafe_allow_html=True)

    mu1, mu2 = st.columns(2)
    with mu1:
        photos = st.file_uploader("📷 Photos (JPG/PNG)",
                                  type=["jpg","jpeg","png","webp"],
                                  accept_multiple_files=True,
                                  key="photo_upload")
        if photos:
            img_cols = st.columns(min(len(photos), 3))
            for i, ph in enumerate(photos[:3]):
                img_cols[i].image(ph, use_container_width=True, caption=f"Photo {i+1}")

    with mu2:
        video = st.file_uploader("🎥 Video (MP4/MOV)", type=["mp4","mov","avi"], key="video_upload")
        if video:
            st.video(video)

    # ── GPS ───────────────────────────────────────────────────────
    lat = st.session_state.auto_lat
    lon = st.session_state.auto_lon
    with st.expander("🛰️ GPS Coordinates (auto-filled — expand to override)"):
        if lat != 0.0:
            st.success(f"📍 Coordinates from pincode: **{lat:.4f}, {lon:.4f}**")
        if GPS_AVAILABLE:
            if st.toggle("📡 Use live device GPS", key="gps_toggle"):
                loc = get_geolocation()
                if loc and "coords" in loc:
                    lat = loc["coords"]["latitude"]
                    lon = loc["coords"]["longitude"]
                    st.success(f"✅ GPS: {lat:.5f}, {lon:.5f}")
        g1, g2 = st.columns(2)
        lat = g1.number_input("Latitude",  value=float(lat),  format="%.5f")
        lon = g2.number_input("Longitude", value=float(lon), format="%.5f")

    # ── PRICE SEGMENT GUIDE — vivid gradient cards ────────────────
    st.markdown('<div class="sec-head">💡 &nbsp;Price Segment Guide</div>', unsafe_allow_html=True)

    pg1, pg2 = st.columns(2)
    with pg1:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#00874a,#00c896);
            border-radius:14px;padding:clamp(12px,3vw,18px);margin-bottom:10px;
            box-shadow:0 6px 20px rgba(0,200,150,0.35);'>
            <div style='font-size:clamp(16px,3.5vw,21px);font-weight:900;color:white;'>🟢 Affordable</div>
            <div style='font-size:clamp(13px,2.8vw,16px);font-weight:700;color:rgba(255,255,255,0.95);margin-top:5px;'>Under ₹30 Lakhs</div>
            <div style='font-size:clamp(11px,2.2vw,13px);color:rgba(255,255,255,0.8);margin-top:4px;'>Entry-level & budget homes</div>
        </div>""", unsafe_allow_html=True)
    with pg2:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#1237cc,#1648ff);
            border-radius:14px;padding:clamp(12px,3vw,18px);margin-bottom:10px;
            box-shadow:0 6px 20px rgba(22,72,255,0.4);'>
            <div style='font-size:clamp(16px,3.5vw,21px);font-weight:900;color:white;'>🔵 Mid-Range</div>
            <div style='font-size:clamp(13px,2.8vw,16px);font-weight:700;color:rgba(255,255,255,0.95);margin-top:5px;'>₹30L – ₹80 Lakhs</div>
            <div style='font-size:clamp(11px,2.2vw,13px);color:rgba(255,255,255,0.8);margin-top:4px;'>Standard flats & suburbs</div>
        </div>""", unsafe_allow_html=True)
    pg3, pg4 = st.columns(2)
    with pg3:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#c97000,#ffb300);
            border-radius:14px;padding:clamp(12px,3vw,18px);margin-bottom:10px;
            box-shadow:0 6px 20px rgba(255,179,0,0.4);'>
            <div style='font-size:clamp(16px,3.5vw,21px);font-weight:900;color:white;'>🟡 Premium</div>
            <div style='font-size:clamp(13px,2.8vw,16px);font-weight:700;color:rgba(255,255,255,0.95);margin-top:5px;'>₹80L – ₹2 Crore</div>
            <div style='font-size:clamp(11px,2.2vw,13px);color:rgba(255,255,255,0.8);margin-top:4px;'>High-end city apartments</div>
        </div>""", unsafe_allow_html=True)
    with pg4:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#b5003a,#ff3d6b);
            border-radius:14px;padding:clamp(12px,3vw,18px);margin-bottom:10px;
            box-shadow:0 6px 20px rgba(255,61,107,0.4);'>
            <div style='font-size:clamp(16px,3.5vw,21px);font-weight:900;color:white;'>💎 Luxury</div>
            <div style='font-size:clamp(13px,2.8vw,16px);font-weight:700;color:rgba(255,255,255,0.95);margin-top:5px;'>Above ₹2 Crore</div>
            <div style='font-size:clamp(11px,2.2vw,13px);color:rgba(255,255,255,0.8);margin-top:4px;'>Villas, penthouses & prime</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("🔮 Run AI Property Valuation", use_container_width=True, key="btn_valuate"):
        if model is None:
            st.error("❌ Model files not found. Place `house_model.pkl` and `model_columns.pkl` in the project folder.")
        elif state == "— Select State —":
            st.warning("⚠️ Please select your state.")
        elif not city.strip():
            st.warning("⚠️ City is required.")
        elif area < 100:
            st.warning("⚠️ Please enter a valid area (min 100 sq ft).")
        else:
            media_names = []
            if photos:
                for i, ph in enumerate(photos):
                    fname = f"photo_{st.session_state.user}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}.jpg"
                    with open(os.path.join("property_media", fname), "wb") as f:
                        f.write(ph.getvalue())
                    media_names.append(fname)
            if video:
                ext   = video.name.split(".")[-1]
                fname = f"video_{st.session_state.user}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                with open(os.path.join("property_media", fname), "wb") as f:
                    f.write(video.getvalue())
                media_names.append(fname)

            if lat == 0.0 or lon == 0.0:
                with st.spinner("📍 Locating property on map…"):
                    lat, lon = geocode_address(city, state, country)

            inputs = dict(
                country=country, state=state, city=city, pincode=pincode,
                area=float(area), bedrooms=int(bedrooms), bathrooms=int(bathrooms),
                stories=int(stories), parking=int(parking), mainroad=mainroad,
                guestroom=guestroom, basement=basement, hotwaterheating=hotwaterheating,
                airconditioning=airconditioning, prefarea=prefarea, furnishing=furnishing,
            )
            with st.spinner("🤖 Running AI valuation…"):
                input_df   = build_input(inputs)
                prediction = float(model.predict(input_df)[0])
                segment, emoji = price_segment(prediction)
                low  = prediction * 0.90
                high = prediction * 1.10
                ppsf = prediction / area
                save_prediction(st.session_state.user, inputs, prediction, segment, lat, lon,
                                ",".join(media_names))
                get_history.clear()
                st.session_state.result = {
                    "prediction": prediction, "segment": segment, "emoji": emoji,
                    "low": low, "high": high, "ppsf": ppsf, "area": area,
                    "bedrooms": bedrooms, "bathrooms": bathrooms,
                    "city": city, "state": state, "lat": lat, "lon": lon,
                }
                time.sleep(0.3)
            # Confetti
            st.markdown("""
<script>
(function(){
    var c=['#1648ff','#00d4ff','#00c896','#ffb300','#ff3d6b','#8b5cf6'];
    var s=document.createElement('style');
    s.textContent='@keyframes cffall{to{top:110vh;opacity:0;transform:rotate(720deg);}}';
    document.head.appendChild(s);
    for(var i=0;i<100;i++){
        var el=document.createElement('div');
        var sz=(5+Math.random()*9)+'px';
        el.style.cssText='position:fixed;top:-12px;left:'+(Math.random()*100)+'vw;'
            +'width:'+sz+';height:'+sz+';border-radius:'+(Math.random()>0.5?'50%':'3px')+';'
            +'background:'+c[Math.floor(Math.random()*c.length)]+';'
            +'z-index:9999;pointer-events:none;'
            +'animation:cffall '+(1.5+Math.random()*2.5)+'s ease-in forwards;';
        document.body.appendChild(el);
        setTimeout(function(e){e.remove();},5000,el);
    }
})();
</script>
""", unsafe_allow_html=True)

    # ── RESULT CARD ──────────────────────────────────────────────
    if st.session_state.result:
        r          = st.session_state.result
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

        # Vivid result header
        st.markdown("""
        <div style='background:linear-gradient(135deg,#061433,#0a2070,#1648ff);
             border-radius:18px;padding:clamp(16px,4vw,24px);margin:20px 0 16px;
             box-shadow:0 10px 40px rgba(22,72,255,0.3);
             border:1px solid rgba(0,212,255,0.2);text-align:center;'>
            <div style='font-size:clamp(18px,4vw,26px);font-weight:900;color:white;
                 letter-spacing:-0.3px;'>
                🏠 AI Valuation Result
            </div>
            <div style='font-size:clamp(11px,2.5vw,13px);color:rgba(0,212,255,0.85);
                 font-weight:600;margin-top:4px;letter-spacing:0.5px;'>
                BASED ON MACHINE LEARNING MODEL
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Full-width price card first, then 2-col below — works perfectly on mobile
        st.metric("💰 Predicted Price", f"₹{prediction:,.0f}",
                  delta=f"Range: ₹{low:,.0f} – ₹{high:,.0f}")
        rc2, rc3 = st.columns(2)
        rc2.metric("📐 ₹ / Sq Ft",  f"₹{ppsf:,.0f}")
        rc3.metric("🛏️ Config",      f"{bedrooms}BHK · {bathrooms}Ba")

        # Segment banner — each segment has its own vivid gradient
        seg_cfg = {
            "Affordable": ("linear-gradient(135deg,#00874a,#00c896,#00e6a8)",
                           "🟢", "Under ₹30 Lakhs",
                           "Entry-level / budget property. Great for first-time buyers."),
            "Mid-Range":  ("linear-gradient(135deg,#1237cc,#1648ff,#2d6cff)",
                           "🔵", "₹30L to ₹80 Lakhs",
                           "Standard residential property with good amenities."),
            "Premium":    ("linear-gradient(135deg,#c97000,#ffb300,#ffd060)",
                           "🟡", "₹80L to ₹2 Crore",
                           "High-end city property with modern facilities."),
            "Luxury":     ("linear-gradient(135deg,#7b0029,#ff3d6b,#ff6b8a)",
                           "💎", "Above ₹2 Crore",
                           "Premium villa / penthouse in a prime location."),
        }
        sg, s_em, s_rng, s_dsc = seg_cfg.get(segment, seg_cfg["Mid-Range"])
        st.markdown(f"""
        <div style='background:{sg};border-radius:16px;
             padding:clamp(16px,4vw,22px) clamp(16px,4vw,26px);margin:14px 0;
             box-shadow:0 8px 32px rgba(0,0,0,0.2);'>
            <div style='font-size:clamp(18px,4.5vw,24px);font-weight:900;color:white;'>
                {s_em} {segment} Segment
            </div>
            <div style='font-size:clamp(14px,3vw,17px);color:rgba(255,255,255,0.95);
                 font-weight:700;margin-top:5px;'>{s_rng}</div>
            <div style='font-size:clamp(12px,2.5vw,14px);color:rgba(255,255,255,0.82);
                 margin-top:6px;'>{s_dsc}</div>
        </div>
        """, unsafe_allow_html=True)

        st.caption("📊 Market Segment Position")
        seg_pct = {"Affordable": 12, "Mid-Range": 37, "Premium": 68, "Luxury": 95}
        st.progress(seg_pct.get(segment, 50))
        sl1, sl2 = st.columns(2)
        sl1.caption("🟢 Affordable < ₹30L")
        sl2.caption("🔵 Mid-Range ₹30–80L")
        sl3, sl4 = st.columns(2)
        sl3.caption("🟡 Premium ₹80L–2Cr")
        sl4.caption("💎 Luxury > ₹2Cr")

        if lat != 0.0 and lon != 0.0:
            st.markdown('<div class="sec-head">📍 &nbsp;Property Location on Map</div>',
                        unsafe_allow_html=True)
            rmap = folium.Map(location=[lat, lon], zoom_start=14, tiles="CartoDB positron")
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(
                    f"<b style='font-size:14px;color:#0a1628;'>{city}, {state}</b><br>"
                    f"<span style='color:#1648ff;font-weight:700;'>💰 ₹{prediction:,.0f}</span><br>"
                    f"📐 {area} sq ft · {bedrooms} BHK<br>{emoji} {segment}",
                    max_width=210
                ),
                icon=folium.Icon(color="blue", icon="home", prefix="fa")
            ).add_to(rmap)
            folium.Circle(location=[lat, lon], radius=600,
                          color="#1648ff", fill=True, fill_opacity=0.07).add_to(rmap)
            st_folium(rmap, use_container_width=True, height=320, key="result_map")

# ════════════════════════════════════════════════════════════════
#  TAB 2 — ANALYTICS
# ════════════════════════════════════════════════════════════════
with tab_analytics:

    # Vibrant analytics header
    st.markdown("""
    <div style='background:linear-gradient(135deg,#061433,#0a2070,#1648ff);
         border-radius:16px;padding:clamp(14px,3vw,20px) clamp(16px,3vw,24px);
         margin-bottom:20px;box-shadow:0 6px 24px rgba(22,72,255,0.3);'>
        <div style='font-size:clamp(17px,4vw,22px);font-weight:900;color:white;'>
            📈 Market Analytics Dashboard
        </div>
        <div style='font-size:clamp(11px,2.5vw,13px);color:rgba(0,212,255,0.85);
             font-weight:600;margin-top:3px;'>
            REAL-TIME INSIGHTS FROM YOUR VALUATIONS
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df_hist.empty:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#f0f5ff,#e8efff);
             border-radius:16px;padding:32px 24px;text-align:center;
             border:2px dashed #b0c4ff;'>
            <div style='font-size:clamp(36px,8vw,52px);'>📊</div>
            <div style='font-size:18px;font-weight:800;color:#1648ff;margin-top:10px;'>
                No Data Yet
            </div>
            <div style='font-size:14px;color:#5a6a8a;margin-top:6px;'>
                Run your first valuation to unlock analytics
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # KPI metrics with vivid colored top borders
        st.markdown("""
        <style>
        [data-testid="metric-container"]:nth-child(1){border-top-color:#1648ff!important;}
        [data-testid="metric-container"]:nth-child(2){border-top-color:#00c896!important;}
        [data-testid="metric-container"]:nth-child(3){border-top-color:#ffb300!important;}
        [data-testid="metric-container"]:nth-child(4){border-top-color:#ff3d6b!important;}
        </style>
        """, unsafe_allow_html=True)

        k1, k2 = st.columns(2)
        k1.metric("🏠 Total Valuations",  f"{len(df_hist):,}")
        k2.metric("💰 Avg Price",          f"₹{df_hist['predicted_price'].mean():,.0f}")
        k3, k4 = st.columns(2)
        k3.metric("📏 Avg Area",           f"{df_hist['area'].mean():,.0f} sq ft")
        k4.metric("💹 Avg ₹/Sq Ft",        f"₹{df_hist['price_per_sqft'].mean():,.0f}")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        SEG_COLORS = {
            "Affordable": "#00c896",
            "Mid-Range":  "#1648ff",
            "Premium":    "#ffb300",
            "Luxury":     "#ff3d6b",
        }

        CHART_CONFIG = {"displayModeBar": False, "scrollZoom": False, "responsive": True}

        LAYOUT = dict(
            paper_bgcolor="white",
            font_family="Plus Jakarta Sans",
            font=dict(color="#0d1f3c", size=12),
            margin=dict(l=8, r=8, t=48, b=50),
            height=340,
            legend=dict(orientation="h", yanchor="bottom", y=-0.38,
                        xanchor="center", x=0.5, font=dict(size=11)),
            title_font=dict(size=14, color="#0d1f3c", family="Plus Jakarta Sans"),
        )

        # Chart 1 — State-wise bar
        fig1 = px.bar(df_hist, x="state", y="predicted_price", color="segment",
                      barmode="group", title="🏙️ State-wise Price Distribution",
                      color_discrete_map=SEG_COLORS,
                      labels={"predicted_price":"Price (₹)","state":"State"})
        fig1.update_layout(**LAYOUT, plot_bgcolor="#f4f8ff",
                           xaxis=dict(tickangle=-40, color="#0d1f3c", automargin=True,
                                      gridcolor="#e8efff"),
                           yaxis=dict(color="#0d1f3c", automargin=True, gridcolor="#e8efff"))
        st.plotly_chart(fig1, use_container_width=True, config=CHART_CONFIG)

        # Chart 2 — Area vs Price scatter
        fig2 = px.scatter(df_hist, x="area", y="predicted_price", color="segment",
                          size="bedrooms", hover_data=["city","bedrooms","furnishing"],
                          title="📐 Area vs Predicted Price",
                          color_discrete_map=SEG_COLORS,
                          labels={"predicted_price":"Price (₹)","area":"Area (sq ft)"})
        fig2.update_layout(**LAYOUT, plot_bgcolor="#fdf4ff",
                           xaxis=dict(color="#0d1f3c", automargin=True, gridcolor="#f0e8ff"),
                           yaxis=dict(color="#0d1f3c", automargin=True, gridcolor="#f0e8ff"))
        st.plotly_chart(fig2, use_container_width=True, config=CHART_CONFIG)

        # Chart 3 — Furnishing box/bar
        if df_hist["furnishing"].nunique() > 1:
            fig3 = px.box(df_hist, x="furnishing", y="predicted_price", color="furnishing",
                          title="🛋️ Price by Furnishing Status",
                          color_discrete_sequence=["#8b5cf6","#00d4ff","#ff3d6b"],
                          labels={"predicted_price":"Price (₹)","furnishing":"Furnishing"})
        else:
            fig3 = px.bar(df_hist, x="furnishing", y="predicted_price", color="furnishing",
                          title="🛋️ Price by Furnishing Status",
                          color_discrete_sequence=["#8b5cf6"],
                          labels={"predicted_price":"Price (₹)","furnishing":"Furnishing"})
        fig3.update_layout(**LAYOUT, plot_bgcolor="#fefce8", showlegend=False,
                           xaxis=dict(color="#0d1f3c", automargin=True, gridcolor="#fff3b0"),
                           yaxis=dict(color="#0d1f3c", automargin=True, gridcolor="#fff3b0"))
        st.plotly_chart(fig3, use_container_width=True, config=CHART_CONFIG)

        # Chart 4 — Segment count
        seg_count = df_hist.groupby("segment")["predicted_price"].count().reset_index()
        seg_count.columns = ["segment","count"]
        fig4 = px.bar(seg_count, x="segment", y="count", color="segment",
                      title="🏷️ Valuations by Market Segment",
                      color_discrete_map=SEG_COLORS,
                      labels={"count":"Valuations","segment":"Segment"}, text="count")
        fig4.update_layout(**LAYOUT, plot_bgcolor="#f0fff8", showlegend=False,
                           xaxis=dict(color="#0d1f3c", automargin=True, gridcolor="#c8f5e8"),
                           yaxis=dict(color="#0d1f3c", automargin=True, gridcolor="#c8f5e8"))
        st.plotly_chart(fig4, use_container_width=True, config=CHART_CONFIG)

        with st.expander("📋 Full Prediction History"):
            show_cols = ["timestamp","city","state","area","bedrooms",
                         "bathrooms","furnishing","predicted_price","segment"]
            avail = [c for c in show_cols if c in df_hist.columns]
            st.dataframe(df_hist[avail].rename(columns={"predicted_price":"Price (₹)"}),
                         use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════
#  TAB 3 — MAP EXPLORER
# ════════════════════════════════════════════════════════════════
with tab_map:

    st.markdown("""
    <div style='background:linear-gradient(135deg,#00874a,#00c896);
         border-radius:16px;padding:clamp(14px,3vw,18px) clamp(16px,3vw,22px);
         margin-bottom:20px;box-shadow:0 6px 24px rgba(0,200,150,0.3);'>
        <div style='font-size:clamp(16px,4vw,21px);font-weight:900;color:white;'>
            📍 All Property Locations
        </div>
        <div style='font-size:clamp(11px,2.5vw,13px);color:rgba(255,255,255,0.8);
             font-weight:600;margin-top:3px;'>
            TAP A PIN FOR PROPERTY DETAILS
        </div>
    </div>
    """, unsafe_allow_html=True)

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
        m = folium.Map(location=[df_map["lat"].mean(), df_map["lon"].mean()],
                       zoom_start=6, tiles="CartoDB positron")
        SEG_COLOR = {"Affordable":"green","Mid-Range":"blue","Premium":"orange","Luxury":"red"}
        SEG_EMOJI = {"Affordable":"🟢","Mid-Range":"🔵","Premium":"🟠","Luxury":"🔴"}

        for _, row in df_map.iterrows():
            color = SEG_COLOR.get(row["segment"], "blue")
            emoji = SEG_EMOJI.get(row["segment"], "🏠")
            media_html = ""
            if row.get("media_paths"):
                paths = [p.strip() for p in str(row["media_paths"]).split(",") if p.strip()]
                for p in paths[:1]:
                    fp = os.path.join("property_media", p)
                    if os.path.exists(fp) and p.lower().endswith((".jpg",".jpeg",".png")):
                        with open(fp, "rb") as f:
                            b64 = base64.b64encode(f.read()).decode()
                        media_html = (f'<br><img src="data:image/jpeg;base64,{b64}" '
                                      f'width="160" style="border-radius:6px;margin-top:6px;"/>')
            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=folium.Popup(
                    f"<b style='font-size:14px;color:#0a1628;'>{row.get('city','')}, {row.get('state','')}</b><br>"
                    f"<span style='color:#1648ff;font-weight:700;'>💰 ₹{row['predicted_price']:,.0f}</span><br>"
                    f"📐 {row['area']} sq ft · {row['bedrooms']} BHK<br>"
                    f"🛁 {row['bathrooms']} Bath · {row['stories']} Floor(s)<br>"
                    f"🛋️ {row.get('furnishing','')}<br>"
                    f"{emoji} {row['segment']}<br>"
                    f"👤 {row.get('username','')}{media_html}",
                    max_width=220
                ),
                icon=folium.Icon(color=color, icon="home", prefix="fa")
            ).add_to(m)

        m.get_root().html.add_child(folium.Element("""
        <div style="position:fixed;bottom:20px;left:16px;z-index:1000;
             background:white;padding:12px 16px;border-radius:12px;
             box-shadow:0 4px 16px rgba(0,0,0,0.15);font-size:12px;
             font-family:'Plus Jakarta Sans',sans-serif;border:1.5px solid #dde3f5;">
            <b style='color:#1648ff;font-size:13px;'>Market Segment</b><br><br>
            🟢 Affordable &nbsp; 🔵 Mid-Range<br><br>
            🟠 Premium &nbsp;&nbsp; 🔴 Luxury
        </div>
        """))

    st_folium(m, use_container_width=True, height=500, key="explorer_map")

# ── FOOTER ───────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;margin-top:40px;padding:20px 8px 10px;
     border-top:2px solid #e8efff;'>
    <div style='font-size:13px;font-weight:700;color:#1648ff;'>
        🏙️ ProProperty AI
    </div>
    <div style='font-size:11px;color:#8a9abc;margin-top:4px;font-weight:500;'>
        ML-Powered Real Estate Valuation &nbsp;·&nbsp; Final Year Project
    </div>
</div>
""", unsafe_allow_html=True)
