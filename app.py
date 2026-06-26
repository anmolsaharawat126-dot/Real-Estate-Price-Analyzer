"""
SmartEstate AI — Complete Single-File Merged Application (v3.0)
India's #1 AI-Powered Real Estate Portal (With AI Locality Reports, Agent CRM, and Buyer Matching)
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import re
import hashlib
from datetime import datetime

# Optional imports with graceful fallbacks
try:
    import folium
    from folium.plugins import MarkerCluster
    from streamlit_folium import st_folium
    FOLIUM_OK = True
except ImportError:
    FOLIUM_OK = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from geopy.geocoders import Nominatim
    GEOPY_OK = True
except ImportError:
    GEOPY_OK = False

# ─────────────────────────────────────────────────────────────
# Directory & DB Initialization
# ─────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
UPLOADS_DIR = os.path.join(BASE, "assets", "uploads")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

PROPS_FILE = os.path.join(DATA_DIR, "properties.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
ENQ_FILE = os.path.join(DATA_DIR, "enquiries.json")
REQ_FILE = os.path.join(DATA_DIR, "requirements.json")
CALLS_FILE = os.path.join(DATA_DIR, "calls.json")
CHATS_FILE = os.path.join(DATA_DIR, "chats.json")
VISITS_FILE = os.path.join(DATA_DIR, "visits.json")
LEADS_FILE = os.path.join(DATA_DIR, "leads.json")
REMINDERS_FILE = os.path.join(DATA_DIR, "reminders.json")

# Default Mock Data Generator
def init_databases():
    # 1. Mock Users
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) < 10:
        default_users = [
            {
                "id": "user_001",
                "name": "Rajesh Sharma",
                "email": "rajesh@example.com",
                "phone": "9876543210",
                "password": hashlib.sha256("rajesh123".encode()).hexdigest(),
                "role": "owner",
                "kyc_verified": True,
                "whatsapp": "9876543210",
                "wishlist": [],
                "joined": "2024-01-01",
                "response_rate": "Fast (1 hr)"
            },
            {
                "id": "user_002",
                "name": "Arjun Malhotra",
                "email": "arjun@example.com",
                "phone": "8765432109",
                "password": hashlib.sha256("arjun123".encode()).hexdigest(),
                "role": "agent",
                "kyc_verified": True,
                "whatsapp": "8765432109",
                "wishlist": [],
                "joined": "2024-02-10",
                "agent_level": 4,
                "response_rate": "Instant (5 mins)"
            },
            {
                "id": "user_003",
                "name": "Admin SmartEstate",
                "email": "admin@smartestate.ai",
                "phone": "9999999999",
                "password": hashlib.sha256("admin123".encode()).hexdigest(),
                "role": "admin",
                "kyc_verified": True,
                "whatsapp": "9999999999",
                "wishlist": [],
                "joined": "2023-12-01"
            }
        ]
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_users, f, indent=2)

    # 2. Mock Properties
    if not os.path.exists(PROPS_FILE) or os.path.getsize(PROPS_FILE) < 10:
        default_props = [
            {
                "id": "prop_001", "title": "Luxurious 3BHK in Sector 62, Noida", "type": "apartment",
                "listing_type": "buy", "city": "Noida", "area": "Sector 62", "state": "Uttar Pradesh",
                "pincode": "201301", "price": 8500000, "price_per_sqft": 7200, "size_sqft": 1180,
                "bhk": 3, "bedrooms": 3, "bathrooms": 2, "parking": 1, "floor": 10, "total_floors": 18,
                "furnishing": "semi-furnished", "status": "available", "verified": True, "premium": True,
                "lat": 28.6273, "lng": 77.3725, "description": "Spacious 3BHK apartment with premium interiors, modular kitchen, and panoramic city view. Located in a prime gated society near metro station.",
                "amenities": ["gym", "swimming_pool", "parking", "24x7_security", "elevator", "power_backup", "clubhouse", "garden"],
                "images": [], "owner_name": "Rajesh Sharma", "owner_phone": "9876543210",
                "owner_whatsapp": "9876543210", "owner_email": "rajesh@example.com",
                "posted_by": "user_001", "posted_date": "2024-01-15", "views": 342, "leads": 18,
                "possession": "ready", "age_years": 3, "facing": "East", "approved": True,
                "aqi": 110, "ev_charging": True, "wheelchair_access": True, "sunlight_facing": "East",
                "legal_approved": True, "rera_registered": True, "hide_contact": False,
                "price_history": [8000000, 8150000, 8300000, 8400000, 8500000]
            },
            {
                "id": "prop_002", "title": "2BHK Ready to Move in Dwarka, Delhi", "type": "apartment",
                "listing_type": "buy", "city": "Delhi", "area": "Dwarka Sector 12", "state": "Delhi",
                "pincode": "110078", "price": 6800000, "price_per_sqft": 6100, "size_sqft": 1115,
                "bhk": 2, "bedrooms": 2, "bathrooms": 2, "parking": 1, "floor": 4, "total_floors": 10,
                "furnishing": "unfurnished", "status": "available", "verified": True, "premium": False,
                "lat": 28.5921, "lng": 77.0460, "description": "Beautiful 2BHK flat with ample sunlight and ventilation. Close to schools, local market and metro station. Ideal for families.",
                "amenities": ["parking", "24x7_security", "elevator", "power_backup", "garden"],
                "images": [], "owner_name": "Arjun Malhotra", "owner_phone": "8765432109",
                "owner_whatsapp": "8765432109", "owner_email": "arjun@example.com",
                "posted_by": "user_002", "posted_date": "2024-02-18", "views": 150, "leads": 5,
                "possession": "ready", "age_years": 5, "facing": "North", "approved": True,
                "aqi": 160, "ev_charging": False, "wheelchair_access": True, "sunlight_facing": "North-East",
                "legal_approved": True, "rera_registered": True, "hide_contact": True,
                "price_history": [6200000, 6400000, 6550000, 6700000, 6800000]
            },
            {
                "id": "prop_003", "title": "Premium Villa in Indiranagar, Bangalore", "type": "villa",
                "listing_type": "buy", "city": "Bangalore", "area": "Indiranagar", "state": "Karnataka",
                "pincode": "560038", "price": 28000000, "price_per_sqft": 11200, "size_sqft": 2500,
                "bhk": 4, "bedrooms": 4, "bathrooms": 4, "parking": 2, "floor": 0, "total_floors": 2,
                "furnishing": "fully-furnished", "status": "available", "verified": True, "premium": True,
                "lat": 12.9718, "lng": 77.6411, "description": "Ultra luxury 4BHK independent villa in Bangalore's posh area. Private garden, modular kitchen, home automation, and Italian marble flooring.",
                "amenities": ["gym", "swimming_pool", "parking", "24x7_security", "power_backup", "garden", "wifi", "ac"],
                "images": [], "owner_name": "Siddharth Rao", "owner_phone": "9911223344",
                "owner_whatsapp": "9911223344", "owner_email": "sid@example.com",
                "posted_by": "user_001", "posted_date": "2024-03-01", "views": 520, "leads": 34,
                "possession": "immediate", "age_years": 1, "facing": "East", "approved": True,
                "aqi": 68, "ev_charging": True, "wheelchair_access": False, "sunlight_facing": "East",
                "legal_approved": True, "rera_registered": True, "hide_contact": False,
                "price_history": [26000000, 26500000, 27000000, 27500000, 28000000]
            }
        ]
        with open(PROPS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_props, f, indent=2)

    # 3. Mock Projects
    if not os.path.exists(PROJECTS_FILE) or os.path.getsize(PROJECTS_FILE) < 10:
        default_projects = [
            {
                "id": "proj_001",
                "name": "ATS Pristine Township",
                "builder": "ATS Greens",
                "city": "Noida",
                "area": "Sector 150",
                "state": "Uttar Pradesh",
                "status": "under_construction",
                "type": "luxury_residential",
                "price_range": "₹90L - ₹2.5Cr",
                "bhk_options": ["3 BHK", "4 BHK"],
                "total_units": 450,
                "available_units": 85,
                "possession_date": "Dec 2026",
                "rera_no": "UPRERAPRJ3782",
                "rating": 5,
                "progress_percent": 65,
                "description": "Green township project offering luxury living with central golf park, sports academy and top class amenities.",
                "highlights": ["70% Green Area", "Golf Course", "Metro 2 min"],
                "lat": 28.4552, "lng": 77.5123
            }
        ]
        with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_projects, f, indent=2)

    # 4. Mock Additional Files
    for file_path in [ENQ_FILE, REQ_FILE, CALLS_FILE, CHATS_FILE, VISITS_FILE, LEADS_FILE, REMINDERS_FILE]:
        if not os.path.exists(file_path) or os.path.getsize(file_path) < 10:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    # 5. Mock CRM Leads Defaults
    if not os.path.exists(LEADS_FILE) or os.path.getsize(LEADS_FILE) < 10:
        default_leads = [
            {"id": "lead_001", "name": "Meera Sen", "phone": "9988776655", "property": "Sector 62, Noida flat", "stage": "New Leads", "agent_id": "user_002"},
            {"id": "lead_002", "name": "Vikram Malhotra", "phone": "8877665544", "property": "Dwarka Sector 12, Delhi", "stage": "Site Visit Scheduled", "agent_id": "user_002"},
            {"id": "lead_003", "name": "Ramesh Gupta", "phone": "7766554433", "property": "Indiranagar, Bangalore", "stage": "Deal Closed", "commission": 85000, "agent_id": "user_002"}
        ]
        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_leads, f, indent=2)

    # 6. Mock CRM Reminders Defaults
    if not os.path.exists(REMINDERS_FILE) or os.path.getsize(REMINDERS_FILE) < 10:
        default_reminders = [
            {"id": "rem_001", "text": "Call Meera Sen to discuss property specifications", "date": "2026-06-29", "done": False, "agent_id": "user_002"},
            {"id": "rem_002", "text": "Collect registration papers for Vikram's Dwarka visit", "date": "2026-06-30", "done": False, "agent_id": "user_002"}
        ]
        with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_reminders, f, indent=2)

init_databases()

# Data access functions
def _load_data(fpath):
    with open(fpath, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_data(fpath, data):
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ─────────────────────────────────────────────────────────────
# Styling & CSS Config
# ─────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&family=Playfair+Display:wght@700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: linear-gradient(135deg, #06060c 0%, #0d1226 50%, #06060c 100%) !important;
    color: #e2e8f0 !important; font-family: 'Inter', sans-serif; min-height: 100vh;
}
#MainMenu, footer { visibility: hidden; }
[data-testid="stSidebar"] { background: #070914 !important; border-right: 1px solid rgba(212,175,55,0.15); }
h1, h2, h3, h4 { font-family: 'Outfit', sans-serif !important; font-weight: 700; }
h1 { color: #ffffff !important; }
h2, h3 { color: #d4af37 !important; }

/* Custom Glassmorphism */
.glass-panel {
    background: rgba(255, 255, 255, 0.03) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    margin-bottom: 1.5rem !important;
    transition: all 0.3s ease !important;
}
.glass-panel:hover {
    border-color: rgba(212,175,55,0.4) !important;
    background: rgba(255, 255, 255, 0.05) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.3) !important;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeIn 0.6s ease forwards; }

@keyframes glowPulse {
    0% { box-shadow: 0 0 5px rgba(212,175,55,0.2); }
    50% { box-shadow: 0 0 20px rgba(212,175,55,0.5); }
    100% { box-shadow: 0 0 5px rgba(212,175,55,0.2); }
}
.glow-pulse { animation: glowPulse 2s infinite; }

/* Buttons styling */
.stButton > button {
    background: linear-gradient(135deg, #d4af37, #f3d060) !important;
    color: #070914 !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    padding: 10px 24px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(212,175,55,0.2) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(212,175,55,0.4) !important;
}

/* Form inputs styling */
div[data-baseweb="input"], div[data-baseweb="select"] {
    background-color: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
}
</style>
"""

NAVBAR_HTML = """
<div style="
    background: rgba(10,10,22,0.95);
    border-bottom: 1px solid rgba(212,175,55,0.3);
    padding: 12px 24px;
    display: flex; align-items: center; justify-content: space-between;
    backdrop-filter: blur(20px);
    margin-bottom: 1rem;
">
    <div style="display:flex;align-items:center;gap:10px">
        <span style="font-size:26px">🏡</span>
        <div>
            <span style="font-family:'Playfair Display',serif;font-size:22px;font-weight:700;color:#fff">Smart</span>
            <span style="font-family:'Playfair Display',serif;font-size:22px;font-weight:700;color:#d4af37">Estate</span>
            <span style="font-size:12px;color:#d4af37;margin-left:4px;vertical-align:super">AI</span>
        </div>
    </div>
    <div style="font-size:12px;color:#888">MagicBricks + 99acres + AI = Premium Portal</div>
</div>
"""

# ─────────────────────────────────────────────────────────────
# Helper & Utility Functions
# ─────────────────────────────────────────────────────────────
def format_price(price: float, listing_type: str = "buy") -> str:
    if price >= 10000000:
        s = f"₹{price/10000000:.2f} Cr"
    elif price >= 100000:
        s = f"₹{price/100000:.2f} L"
    else:
        s = f"₹{price:,.0f}"
    if listing_type == "rent":
        s += "/mo"
    return s

def get_deal_verdict(listed_price, est_price):
    diff = ((listed_price - est_price) / est_price) * 100
    if diff < -5:
        return "🟢 Great Deal", "badge-verified"
    elif diff < 10:
        return "🟡 Fair Price", "badge-deal"
    else:
        return "🔴 Overpriced", "badge-buy"

def detect_duplicates(title, area, size_sqft):
    props = get_all_properties(approved_only=False)
    for p in props:
        # Check matching area and overlapping size (within 5% range)
        size_diff = abs(p["size_sqft"] - size_sqft) / size_sqft
        if p["area"].lower() == area.lower() and size_diff < 0.05:
            return True, p["id"]
    return False, None

def get_user_badge_html(user_id: str) -> str:
    try:
        users = _load_data(USERS_FILE)
        for u in users:
            if u["id"] == user_id:
                if u.get("kyc_verified"):
                    if u.get("role") == "agent":
                        lvl = u.get("agent_level", 3)
                        return f'<span class="badge" style="background:rgba(212,175,55,0.15);color:#d4af37;border:1px solid rgba(212,175,55,0.3)">🎖️ Trusted Agent Lvl {lvl}</span>'
                    else:
                        return '<span class="badge" style="background:rgba(0,180,255,0.15);color:#00b4ff;border:1px solid rgba(0,180,255,0.3)">👑 Verified Owner</span>'
    except Exception:
        pass
    return ""

def get_response_badge_html(user_id: str) -> str:
    try:
        users = _load_data(USERS_FILE)
        for u in users:
            if u["id"] == user_id:
                rate = u.get("response_rate")
                if rate:
                    return f'<span class="badge" style="background:rgba(255,255,255,0.05);color:#eee;border:1px solid rgba(255,255,255,0.1)">⚡ {rate}</span>'
    except Exception:
        pass
    return ""

def property_card_html(p: dict) -> str:
    price_str = format_price(p.get("price", 0), p.get("listing_type", "buy"))
    verified = "✅ Verified Listing" if p.get("verified") else ""
    premium = "💎 Premium" if p.get("premium") else ""
    lt = p.get("listing_type", "buy").upper()
    bhk = f"{p.get('bhk','')}BHK · " if p.get("bhk") else ""
    sqft = f"{p.get('size_sqft','')} sqft" if p.get("size_sqft") else ""
    
    # Calculate price tag dynamically
    est = estimate_price(p['city'], p['area'], p['size_sqft'], p.get('bhk', 2), p.get('type','apartment'))
    deal_lbl, deal_cls = get_deal_verdict(p['price'], est['estimated_price'])
    
    user_badge = get_user_badge_html(p.get("posted_by",""))
    resp_badge = get_response_badge_html(p.get("posted_by",""))

    # Flat string with NO leading whitespace on any line
    img_placeholder = (
        '<div style="background:linear-gradient(135deg,#181c33,#090b14);'
        'border-radius:12px;height:160px;display:flex;align-items:center;'
        'justify-content:center;margin-bottom:12px;border:1px solid rgba(255,255,255,0.05);'
        'position:relative;">'
        '<span style="font-size:48px">🏠</span>'
        '<span style="position:absolute;top:10px;right:10px;background:rgba(0,0,0,0.65);'
        'padding:4px 8px;border-radius:6px;font-size:10px;color:#d4af37;font-weight:700;">'
        'Match Score 98%</span></div>'
    )

    card_html = (
        f'<div class="prop-card glass-panel fade-in">'
        f'{img_placeholder}'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">'
        f'<span style="font-size:16px;font-weight:700;color:#fff;flex:1;margin-right:8px">{p.get("title", "")[:50]}</span>'
        f'<span class="price-badge">{price_str}</span>'
        f'</div>'
        f'<div style="font-size:13px;color:#aaa;margin-bottom:10px">'
        f'📍 {p.get("area", "")}, {p.get("city", "")} &nbsp;·&nbsp; {bhk}{sqft}'
        f'</div>'
        f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px">'
        f'<span class="badge badge-{"rent" if lt=="RENT" else "buy"}">{lt}</span>'
        f'<span class="badge {deal_cls}">{deal_lbl}</span>'
        f'{f"<span class=\\\"badge badge-verified\\\">{verified}</span>" if verified else ""}'
        f'<span class="badge" style="background:rgba(255,255,255,0.05);color:#ccc">{p.get("furnishing", "").replace("-", " ").title()}</span>'
        f'{f"<span class=\\\"badge\\\" style=\\\"background:rgba(212,175,55,0.2);color:#d4af37\\\">{premium}</span>" if premium else ""}'
        f'{user_badge}'
        f'{resp_badge}'
        f'</div>'
        f'<div style="font-size:13px;color:#cbd5e1;line-height:1.5">{str(p.get("description", ""))[:120]}...</div>'
        f'</div>'
    )
    return card_html

def geocode(address_str):
    if not GEOPY_OK:
        return {"lat": 28.6139, "lng": 77.2090}
    try:
        geolocator = Nominatim(user_agent="smartestate_ai")
        location = geolocator.geocode(address_str, timeout=10)
        if location:
            return {"lat": location.latitude, "lng": location.longitude}
    except Exception:
        pass
    return {"lat": 28.6139, "lng": 77.2090}

# ─────────────────────────────────────────────────────────────
# Database Helpers
# ─────────────────────────────────────────────────────────────
def get_all_properties(approved_only=True):
    props = _load_data(PROPS_FILE)
    if approved_only:
        return [p for p in props if p.get("approved", False)]
    return props

def get_property_by_id(prop_id: str):
    for p in _load_data(PROPS_FILE):
        if p["id"] == prop_id:
            return p
    return None

def get_properties_by_user(user_id: str):
    return [p for p in _load_data(PROPS_FILE) if p.get("posted_by") == user_id]

def save_property(prop: dict):
    props = _load_data(PROPS_FILE)
    props.append(prop)
    _save_data(PROPS_FILE, props)

def update_property(prop_id: str, updates: dict):
    props = _load_data(PROPS_FILE)
    for p in props:
        if p["id"] == prop_id:
            p.update(updates)
    _save_data(PROPS_FILE, props)

def delete_property(prop_id: str):
    props = _load_data(PROPS_FILE)
    props = [p for p in props if p["id"] != prop_id]
    _save_data(PROPS_FILE, props)

def increment_views(prop_id: str):
    props = _load_data(PROPS_FILE)
    for p in props:
        if p["id"] == prop_id:
            p["views"] = p.get("views", 0) + 1
    _save_data(PROPS_FILE, props)

def search_properties(
    city=None, area=None, listing_type=None, prop_type=None,
    min_price=None, max_price=None, verified_only=False, premium_only=False, keyword=None
):
    props = get_all_properties(approved_only=True)
    results = []
    for p in props:
        if city and city.lower() not in p.get("city", "").lower():
            continue
        if area and area.lower() not in p.get("area", "").lower():
            continue
        if listing_type and listing_type != "all" and p.get("listing_type") != listing_type:
            continue
        if prop_type and prop_type != "all" and p.get("type") != prop_type:
            continue
        if min_price and p.get("price", 0) < min_price:
            continue
        if max_price and p.get("price", 0) > max_price:
            continue
        if verified_only and not p.get("verified", False):
            continue
        if premium_only and not p.get("premium", False):
            continue
        if keyword:
            kw = keyword.lower()
            searchable = f"{p.get('title','')} {p.get('description','')} {p.get('area','')} {p.get('city','')}".lower()
            if kw not in searchable:
                continue
        results.append(p)
    results.sort(key=lambda x: (not x.get("premium", False), not x.get("verified", False)))
    return results

def get_all_projects():
    return _load_data(PROJECTS_FILE)

def save_enquiry(prop_id: str, user_id: str, type_: str, message: str = ""):
    enqs = _load_data(ENQ_FILE)
    enqs.append({
        "id": f"enq_{len(enqs)+1:04d}",
        "prop_id": prop_id,
        "user_id": user_id,
        "type": type_,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })
    _save_data(ENQ_FILE, enqs)
    props = _load_data(PROPS_FILE)
    for p in props:
        if p["id"] == prop_id:
            p["leads"] = p.get("leads", 0) + 1
    _save_data(PROPS_FILE, props)

def get_enquiries_for_property(prop_id: str):
    return [e for e in _load_data(ENQ_FILE) if e["prop_id"] == prop_id]

# ─────────────────────────────────────────────────────────────
# Auth Operations
# ─────────────────────────────────────────────────────────────
def login(email: str, password: str):
    users = _load_data(USERS_FILE)
    h = hashlib.sha256(password.encode()).hexdigest()
    for u in users:
        if u["email"].lower() == email.lower() and u["password"] == h:
            return u
    return None

def register(name: str, email: str, phone: str, password: str, role: str = "owner"):
    users = _load_data(USERS_FILE)
    if any(u["email"].lower() == email.lower() for u in users):
        return False, "Email already registered!"
    h = hashlib.sha256(password.encode()).hexdigest()
    new_user = {
        "id": f"user_{len(users)+1:03d}_{int(datetime.now().timestamp())}",
        "name": name,
        "email": email,
        "phone": phone,
        "password": h,
        "role": role,
        "kyc_verified": False,
        "whatsapp": phone,
        "wishlist": [],
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "active": True
    }
    users.append(new_user)
    _save_data(USERS_FILE, users)
    return True, "Registered successfully!"

def is_logged_in():
    return st.session_state.get("user") is not None

# ─────────────────────────────────────────────────────────────
# AI Calculations & NLP Query parsing
# ─────────────────────────────────────────────────────────────
CITY_BASE_RATES = {
    "mumbai": 18000, "delhi": 12000, "gurgaon": 13000, "noida": 9000,
    "bangalore": 10000, "hyderabad": 8000, "pune": 8500, "default": 5000
}

CITY_GROWTH = {
    "mumbai": 8.5, "delhi": 9.0, "gurgaon": 11.0, "noida": 12.0,
    "bangalore": 13.5, "hyderabad": 14.0, "pune": 10.0, "default": 8.0
}

def estimate_price(city: str, area: str, size_sqft: float, bhk: int, prop_type: str = "apartment") -> dict:
    city_key = city.lower()
    base = CITY_BASE_RATES.get(city_key, CITY_BASE_RATES["default"])
    area_hash = int(hashlib.md5(f"{city_key}_{area.lower()}".encode()).hexdigest(), 16)
    variance = 1 + ((area_hash % 25) - 12) / 100

    type_mult = {"villa": 1.4, "farmhouse": 1.8, "plot": 0.7, "office": 1.2, "shop": 1.5, "apartment": 1.0}.get(prop_type.lower(), 1.0)
    per_sqft = base * variance * type_mult
    total = per_sqft * size_sqft
    bhk_premium = {1: 0.95, 2: 1.0, 3: 1.05, 4: 1.1}.get(bhk, 1.0)
    total *= bhk_premium

    return {
        "per_sqft_rate": round(per_sqft),
        "estimated_price": round(total),
        "low": round(total * 0.90),
        "high": round(total * 1.10),
        "confidence": "High" if city_key in CITY_BASE_RATES else "Medium"
    }

def future_price(current_price: float, city: str, years: int = 5) -> dict:
    city_key = city.lower()
    rate = CITY_GROWTH.get(city_key, CITY_GROWTH["default"]) / 100
    predictions = {}
    for y in range(1, years + 1):
        predictions[y] = round(current_price * ((1 + rate) ** y))
    return {"growth_rate_pa": CITY_GROWTH.get(city_key, CITY_GROWTH["default"]), "predictions": predictions}

def investment_score(city: str, area: str, prop_type: str, price: float) -> dict:
    city_key = city.lower()
    growth = CITY_GROWTH.get(city_key, 8.0)
    area_hash = int(hashlib.md5(f"{city_key}_{area.lower()}".encode()).hexdigest(), 16)
    area_bonus = (area_hash % 20) / 10

    base_score = min(10, (growth / 2) + area_bonus)
    rental_yield = round(2.5 + (area_hash % 30) / 20, 1)
    appreciation = round(growth + area_bonus, 1)
    risk = "Low" if base_score > 7 else ("Medium" if base_score > 5 else "High")

    return {
        "score": round(base_score, 1),
        "rental_yield_pct": rental_yield,
        "appreciation_pct": appreciation,
        "risk": risk,
        "verdict": "Excellent Investment" if base_score > 7.5 else ("Good Investment" if base_score > 5.5 else "Average Investment")
    }

def calculate_emi(principal: float, rate_pa: float, tenure_years: int) -> dict:
    r = rate_pa / (12 * 100)
    n = tenure_years * 12
    if r == 0:
        emi = principal / n
    else:
        emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
    total_payment = emi * n
    total_interest = total_payment - principal
    return {
        "emi": round(emi),
        "total_payment": round(total_payment),
        "total_interest": round(total_interest),
        "principal": principal,
        "tenure_months": n
    }

def loan_eligibility(monthly_income: float, existing_emi: float = 0, rate_pa: float = 8.5, tenure_years: int = 20) -> dict:
    max_emi = monthly_income * 0.5 - existing_emi
    if max_emi <= 0:
        return {"eligible_amount": 0, "max_emi": 0}
    r = rate_pa / (12 * 100)
    n = tenure_years * 12
    eligible = max_emi * (((1 + r) ** n) - 1) / (r * ((1 + r) ** n)) if r > 0 else max_emi * n
    return {
        "eligible_amount": round(eligible),
        "max_emi": round(max_emi)
    }

def stamp_duty(state: str, price: float, is_woman_buyer: bool = False) -> dict:
    rates = {
        "maharashtra": 6.0, "delhi": 6.0, "karnataka": 5.0,
        "uttar pradesh": 7.0, "rajasthan": 6.0, "gujarat": 4.9, "haryana": 7.0, "default": 6.0
    }
    rate = rates.get(state.lower(), rates["default"])
    if is_woman_buyer:
        rate = max(rate - 1, 3)
    reg_fee = min(price * 0.01, 30000)
    stamp = price * rate / 100
    return {
        "stamp_duty_rate": rate,
        "stamp_duty_amount": round(stamp),
        "registration_fee": round(reg_fee),
        "total_cost": round(stamp + reg_fee)
    }

def parse_query(query: str) -> dict:
    q = query.lower()
    extracted = {}
    budget_patterns = [
        r'(\d+)\s*(?:lakh|lac|l)\b',
        r'(\d+(?:\.\d+)?)\s*cr(?:ore)?\b',
        r'₹\s*(\d+(?:,\d+)*)',
        r'(\d+(?:,\d+)*)\s*(?:rs|rupees)'
    ]
    for pat in budget_patterns:
        m = re.search(pat, q)
        if m:
            val = float(m.group(1).replace(",", ""))
            if "cr" in q[max(0, m.start()-2):m.end()+5] or "crore" in q:
                val *= 10000000
            elif "lakh" in q[max(0, m.start()-2):m.end()+5] or " lac" in q or " l " in q:
                val *= 100000
            extracted["budget"] = int(val)
            break

    bhk_m = re.search(r'(\d)\s*bhk', q)
    if bhk_m:
        extracted["bhk"] = int(bhk_m.group(1))

    cities = ["noida", "delhi", "gurgaon", "mumbai", "bangalore", "bengaluru", "hyderabad", "pune"]
    for c in cities:
        if c in q:
            extracted["city"] = "Bangalore" if c == "bengaluru" else c.title()
            break
    extracted["listing_type"] = "rent" if "rent" in q or "रेंट" in q else "buy"
    return extracted

def ai_consult(query: str, properties: list, gemini_key: str = None) -> str:
    params = parse_query(query)
    city = params.get("city", "Delhi NCR")
    if "muzaffarnagar" in query.lower():
        city = "Muzaffarnagar"
    budget = params.get("budget", 5000000)
    bhk = params.get("bhk", 2)
    listing_type = params.get("listing_type", "buy")
    
    city_lower = city.lower()
    if "muzaffarnagar" in city_lower:
        best_areas = ["South Civil Lines (Premium residential)", "Jansath Road (Rapid development)", "New Mandi (Commercial hub)"]
        growth_rate = 14.5
        risk = "Low"
        verdict = "Excellent for Land/Plot Appreciation"
        score = 92
        legal = "- **RERA Certificate**: Required for Jansath Road layouts.\\n- **Title Deed Clearances**: Mandatory check for New Mandi agricultural conversions."
    elif "noida" in city_lower:
        best_areas = ["Sector 150 (Premium green township)", "Sector 62 (IT & Commercial hub)", "Sector 137 (Metro connectivity)"]
        growth_rate = 12.0
        risk = "Low"
        verdict = "Highly Recommended for Rental Yield"
        score = 88
        legal = "- **Noida Authority Lease Deed**: Ensure dues are clear.\\n- **RERA Registration**: Check builder certificate online."
    elif "bangalore" in city_lower or "bengaluru" in city_lower:
        best_areas = ["Indiranagar (Commercial demand)", "Whitefield (IT workforce hubs)", "Sarjapur Road (Rapid expansion)"]
        growth_rate = 13.5
        risk = "Medium (Water shortage in suburbs)"
        verdict = "Top Pick for IT Professionals & Co-living"
        score = 90
        legal = "- **A-Katha Certificate**: Verify municipal tax records.\\n- **OC (Occupancy Certificate)**: Mandatory for high-rises."
    else:
        best_areas = [f"{city} Central", f"Emerging {city} bypass road", f"New residential zones in {city}"]
        growth_rate = 9.0
        risk = "Medium"
        verdict = "Stable micro-market growth"
        score = 78
        legal = "- **Local Authority Approvals**: Verify layout approval map.\\n- **Encumbrance Check**: Search sub-registrar records for 13 years."

    if gemini_key and GEMINI_AVAILABLE:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prop_summary = "\\n".join([f"- {p['title']} | {format_price(p['price'])} | {p['area']}, {p['city']}" for p in properties[:5]])
            prompt = f"""You are SmartEstate AI - India's best real estate advisor.
User Query: "{query}"
Extracted Parameters: City: {city}, Budget: {budget}, BHK: {bhk}, Listing Type: {listing_type}
Available Properties: {prop_summary}
Provide a comprehensive, professional real-estate consultation. You must cover:
1. Best Areas to buy in {city} (provide specific local details)
2. Matching Properties from the database (if any) or what to look for
3. Future Growth & capital appreciation forecast (5-yr projections based on {growth_rate}% growth rate)
4. Total on-road cost estimate (including stamp duty/registration fee calculations)
5. Risk Level: {risk}
6. Legal checklist needed: {legal}
7. Investment Score: {score}/100 ({verdict})
Format using clean, modern markdown with emojis, custom bullet points, and neat spacing."""
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            pass

    matching = [p for p in properties if city_lower in p.get("city", "").lower() and p.get("price", 0) <= budget][:3]
    props_text = "\\n".join([f"  • **{p['title']}** in {p['area']} | 💰 {format_price(p['price'])}" for p in matching]) if matching else f"No exact database matches under {format_price(budget)} in {city}. Try posting a buyer requirement!"
    
    sd_calc = stamp_duty(city, budget)
    gst_calc = budget * 0.05 if listing_type == "buy" else 0
    total_est = budget + sd_calc["total_cost"] + gst_calc

    return f"""## 🏙️ Best Areas in {city}
{ "".join([f"- **{area}**: High demand zone.\\\\n" for area in best_areas]) }
## 🏠 Matching Properties (Under {format_price(budget)})
{props_text}

## 📈 Future Price Growth (5 Year Prediction)
- Annual Capital Appreciation: **{growth_rate}% p.a.**
- Expected value of your {format_price(budget)} investment: **{format_price(round(budget * ((1 + growth_rate/100)**5)))}** in 5 years.

## 💰 Final On-Road Cost Estimate
- Listed Base Price: **{format_price(budget)}**
- Stamp Duty & Registration: **{format_price(sd_calc['total_cost'])}**
- GST (5% if under-construction): **{format_price(gst_calc)}**
- **Estimated Total Cost**: <span style="color:#d4af37;font-weight:700">{format_price(total_est)}</span>

## 📅 EMI & Loan Advice
- Estimated Monthly EMI: **{format_price(calculate_emi(budget * 0.8, 8.5, 20)['emi'])}** (Based on 80% loan at 8.5% interest for 20 years).
- Recommended Banks: **SBI (8.4%)** for best rates, **HDFC (8.5%)** for fast processing.

## ⚖️ Legal Checklist & Document Audit
{legal}
- **Encumbrance Check**: Search registry office files for past 13 years.

## 🛡️ Risk & Safety Analysis
- Risk Rating: **{risk}**
- Assessment: Property ownership records are clear, low chance of registry disputes in {city}.

## 📊 Investment Score: {score}/100 — {verdict}
"""

# Map functions
def create_property_map(properties, lat, lng, zoom=12):
    m = folium.Map(location=[lat, lng], zoom_start=zoom, tiles=None)
    folium.TileLayer("https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google Road Map", name="Road Map").add_to(m)
    folium.TileLayer("https://mt1.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}", attr="Google Satellite", name="Satellite Map").add_to(m)
    for p in properties:
        plat, plng = p.get("lat", 0), p.get("lng", 0)
        if plat:
            folium.Marker(
                [plat, plng],
                popup=f"<b>{p['title']}</b><br>{format_price(p['price'])}",
                icon=folium.Icon(color="gold" if p.get("premium") else "blue", icon="home")
            ).add_to(m)
    folium.LayerControl().add_to(m)
    return m

def create_single_property_map(lat, lng, title):
    m = folium.Map(location=[lat, lng], zoom_start=15, tiles=None)
    folium.TileLayer("https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google Road Map", name="Road Map").add_to(m)
    folium.Marker([lat, lng], popup=title, icon=folium.Icon(color="red", icon="home")).add_to(m)
    folium.Circle([lat, lng], radius=400, color="#d4af37", fill=True, fill_opacity=0.1).add_to(m)
    return m

# ─────────────────────────────────────────────────────────────
# Session State Navigation
# ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "Home"
if "user" not in st.session_state:
    st.session_state["user"] = None
if "view_prop_id" not in st.session_state:
    st.session_state["view_prop_id"] = "prop_001"

# Set Config
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown(NAVBAR_HTML, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Sidebar Navigation Menu
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0;border-bottom:1px solid rgba(212,175,55,0.2);margin-bottom:1rem">
        <span style="font-size:40px">🏡</span>
        <div style="font-family:'Playfair Display',serif;font-size:22px;font-weight:700">
            <span style="color:#fff">Smart</span><span style="color:#d4af37">Estate</span>
            <sup style="color:#d4af37;font-size:10px">AI</sup>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation Links
    pages_list = [
        "🏡 Home", 
        "🔍 Search Properties", 
        "🤖 AI Advisor & Search", 
        "📊 Locality Intelligence",
        "📤 Post Property / Requirement",
        "📊 Dashboard & CRM", 
        "🏗️ Builders & Projects", 
        "💰 Finance Calculators",
        "❤️ My Wishlist", 
        "🛡️ Admin Panel"
    ]
    
    if "nav_selection" not in st.session_state:
        st.session_state["nav_selection"] = pages_list[0]

    for p_name in pages_list:
        if st.session_state["page"] in p_name:
            st.session_state["nav_selection"] = p_name

    selected_nav = st.radio("Navigation Menu", pages_list, index=pages_list.index(st.session_state["nav_selection"]))
    if selected_nav != st.session_state["nav_selection"]:
        st.session_state["nav_selection"] = selected_nav
        st.session_state["page"] = selected_nav.split(" ", 1)[1]
        st.rerun()

    st.markdown("---")

    # User Profile Section
    if is_logged_in():
        curr_user = st.session_state["user"]
        st.markdown(f"""
        <div style="background:rgba(212,175,55,0.08);border:1px solid rgba(212,175,55,0.2);border-radius:12px;padding:12px;margin-bottom:1rem">
            <div style="font-weight:700;font-size:14px">👋 {curr_user['name']}</div>
            <div style="font-size:11px;color:#aaa">{curr_user['email']}</div>
            <div style="font-size:11px;color:#d4af37;margin-top:4px">
                {'✅ KYC Verified' if curr_user.get('kyc_verified') else '⏳ KYC Pending'}
                &nbsp;·&nbsp; {curr_user.get('role','owner').title()}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Logout 🚪", use_container_width=True):
            st.session_state["user"] = None
            st.rerun()
    else:
        st.markdown("🔐 **Login / Sign Up**")
        tab_log, tab_sign = st.tabs(["Login", "Sign Up"])
        with tab_log:
            with st.form("sidebar_login"):
                email = st.text_input("Email", placeholder="user@email.com")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Log In", use_container_width=True):
                    u = login(email, password)
                    if u:
                        st.session_state["user"] = u
                        st.success("Login Successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
        with tab_sign:
            with st.form("sidebar_signup"):
                name = st.text_input("Full Name")
                email_s = st.text_input("Email Address")
                phone_s = st.text_input("Phone Number")
                pass_s = st.text_input("Password", type="password")
                role_s = st.selectbox("Role", ["buyer", "owner", "agent"])
                if st.form_submit_button("Sign Up", use_container_width=True):
                    ok, msg = register(name, email_s, phone_s, pass_s, role_s)
                    if ok:
                        st.success(msg)
                        st.session_state["user"] = login(email_s, pass_s)
                        st.rerun()
                    else:
                        st.error(msg)

# ─────────────────────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────────────────────
def render_home():
    st.markdown("""
    <div class="hero-section glass-panel fade-in">
        <div style="font-size:13px;color:#d4af37;font-weight:600;letter-spacing:2px;margin-bottom:12px">
            🤖 INDIA'S #1 AI-POWERED REAL ESTATE PORTAL
        </div>
        <h1 style="font-size:3rem;margin:0 0 12px">
            Find Your Dream Home<br>
            <span style="color:#d4af37">with Advanced AI Assistance</span>
        </h1>
        <p style="font-size:16px;color:#aaa;max-width:600px;margin:0 auto 2rem">
            India's most intelligent real estate platform. Buy, Rent, Sell — with AI price predictions,
            smart locality recommendations, and verified listings.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Search Bar
    st.markdown('<div class="glass-panel" style="padding:1.5rem;margin-bottom:2rem">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        s_city = st.text_input("City Name", placeholder="e.g. Noida, Delhi, Mumbai")
    with c2:
        s_type = st.selectbox("Listing Type", ["buy", "rent"])
    with c3:
        s_budget = st.selectbox("Max Budget", ["Any Budget", "₹50L", "₹1Cr", "₹2Cr", "₹5Cr"])
    with c4:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("🔍 Search Properties", use_container_width=True):
            st.session_state["search_city"] = s_city
            st.session_state["search_type"] = s_type
            st.session_state["page"] = "Search Properties"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Featured Listings
    st.markdown("### 💎 Featured Premium Listings")
    all_props = get_all_properties()
    premium_props = [p for p in all_props if p.get("premium")]
    
    if premium_props:
        cols = st.columns(len(premium_props[:3]))
        for idx, p in enumerate(premium_props[:3]):
            with cols[idx]:
                st.markdown(property_card_html(p), unsafe_allow_html=True)
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("👁 View Detail", key=f"home_view_{p['id']}", use_container_width=True):
                        st.session_state["view_prop_id"] = p["id"]
                        st.session_state["page"] = "Property Detail"
                        st.rerun()
                with col_b:
                    wa = f"https://wa.me/91{p.get('owner_whatsapp','9999999999')}?text=Hi, I am interested in your property."
                    st.link_button("💬 WhatsApp", wa, use_container_width=True)
    else:
        st.info("No premium listings yet.")

    # Upcoming Projects
    st.markdown("<br>### 🏗️ Newly Launched Colonies & Projects", unsafe_allow_html=True)
    projs = get_all_projects()
    if projs:
        cols_proj = st.columns(len(projs[:2]))
        for idx, pr in enumerate(projs[:2]):
            with cols_proj[idx]:
                st.markdown(f"""
                <div class="prop-card glass-panel">
                    <div style="font-size:11px;color:#d4af37;font-weight:700;text-transform:uppercase">● Under Construction</div>
                    <h4 style="color:#fff;margin:6px 0">{pr['name']}</h4>
                    <div style="font-size:12px;color:#aaa">By {pr['builder']} · {pr['area']}, {pr['city']}</div>
                    <div style="font-size:14px;color:#d4af37;font-weight:700;margin-top:8px">{pr['price_range']}</div>
                    <div style="margin-top:10px">
                        <div style="font-size:11px;color:#888">Construction Progress ({pr['progress_percent']}%)</div>
                        <div style="background:rgba(255,255,255,0.1);border-radius:10px;height:6px;overflow:hidden">
                            <div style="width:{pr['progress_percent']}%;height:100%;background:#d4af37"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View Builder Details", key=f"home_p_{pr['id']}", use_container_width=True):
                    st.session_state["page"] = "Builders & Projects"
                    st.rerun()
    else:
        st.info("No newly launched projects yet.")

# ─────────────────────────────────────────────────────────────
# PAGE: SEARCH PROPERTIES
# ─────────────────────────────────────────────────────────────
def render_search():
    st.markdown("### 🔍 Search Real Estate Directory")
    
    city_filter = st.session_state.get("search_city", "")
    type_filter = st.session_state.get("search_type", "all")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("#### Filters")
        s_c = st.text_input("Enter City", value=city_filter, key="sc_input")
        s_t = st.selectbox("Listed for", ["all", "buy", "rent"], index=["all", "buy", "rent"].index(type_filter))
        s_type = st.selectbox("Property Type", ["all", "apartment", "villa", "plot", "office"])
        
        min_p = st.number_input("Min Price (₹)", value=0)
        max_p = st.number_input("Max Price (₹)", value=100000000)
        
        v_only = st.checkbox("Verified Listings Only")
        p_only = st.checkbox("Premium Only")
        
        if st.button("Apply Filters", use_container_width=True):
            st.session_state["search_city"] = s_c
            st.session_state["search_type"] = s_t
            st.rerun()
            
    with col2:
        results = search_properties(
            city=s_c or None,
            listing_type=(None if s_t == "all" else s_t),
            prop_type=(None if s_type == "all" else s_type),
            min_price=min_p if min_p > 0 else None,
            max_price=max_p if max_p < 100000000 else None,
            verified_only=v_only,
            premium_only=p_only
        )
        
        st.markdown(f"**{len(results)} properties matching your criteria**")
        
        view_tabs = st.tabs(["🏠 List Cards", "🗺️ Map View"])
        with view_tabs[0]:
            if not results:
                st.warning("No properties matching current filters found.")
            else:
                for idx, r in enumerate(results):
                    st.markdown(property_card_html(r), unsafe_allow_html=True)
                    btn_a, btn_b, btn_c = st.columns(3)
                    with btn_a:
                        if st.button("👁 Details", key=f"search_view_{r['id']}", use_container_width=True):
                            st.session_state["view_prop_id"] = r["id"]
                            st.session_state["page"] = "Property Detail"
                            st.rerun()
                    with btn_b:
                        wa_link = f"https://wa.me/91{r.get('owner_whatsapp','9999999999')}?text=I+am+interested+in+your+property"
                        st.link_button("💬 WhatsApp", wa_link, use_container_width=True)
                    with btn_c:
                        if st.button("❤️ Add Wishlist", key=f"search_wish_{r['id']}", use_container_width=True):
                            if is_logged_in():
                                u = st.session_state["user"]
                                users = _load_data(USERS_FILE)
                                for u_data in users:
                                    if u_data["id"] == u["id"]:
                                        if r["id"] not in u_data.get("wishlist", []):
                                            u_data.setdefault("wishlist", []).append(r["id"])
                                            st.success("Added to Wishlist!")
                                users = _load_data(USERS_FILE)
                                st.session_state["user"] = next(usr for usr in users if usr["id"] == u["id"])
                            else:
                                st.error("Please login to save wishlist.")
        with view_tabs[1]:
            if FOLIUM_OK and results:
                m = create_property_map(results, results[0].get("lat", 28.6139), results[0].get("lng", 77.2090))
                st_folium(m, width="100%", height=500)
            else:
                st.info("Install folium map or try a search with matching coordinates.")

# ─────────────────────────────────────────────────────────────
# PAGE: PROPERTY DETAIL
# ─────────────────────────────────────────────────────────────
def render_detail():
    st.markdown("### 🏠 Property Detailed Analysis")
    prop_id = st.session_state.get("view_prop_id", "prop_001")
    p = get_property_by_id(prop_id)
    
    if not p:
        st.error("Property details not found!")
        if st.button("Return Home"):
            st.session_state["page"] = "Home"
            st.rerun()
        st.stop()
        
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(212,175,55,0.25);border-radius:16px;padding:1.5rem;margin-bottom:1.5rem">
        <h2>{p['title']}</h2>
        <p style="color:#aaa">📍 {p['area']}, {p['city']}, {p['state']} — {p['pincode']}</p>
        <div style="display:flex;gap:12px;margin:1rem 0">
            <span class="badge badge-verified">✅ RERA Checked</span>
            <span class="badge" style="background:#d4af37;color:#0a0a16;font-weight:700">Listed Price: {format_price(p['price'], p.get('listing_type','buy'))}</span>
        </div>
        <p>{p['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    dt1, dt2, dt3, dt4, dt5, dt6 = st.tabs([
        "📊 AI Valuation & History", "🗺️ Location & Environment", "💰 Cost Calculator & Loan", 
        "📩 Legal & Verification", "📅 Visit Scheduler", "👤 Contact Owner"
    ])
    
    # Tab 1: Valuation & History
    with dt1:
        st.markdown("#### 🤖 SmartEstate AI Valuation Engine")
        est = estimate_price(p['city'], p['area'], p['size_sqft'], p.get('bhk', 2), p.get('type','apartment'))
        inv = investment_score(p['city'], p['area'], p.get('type','apartment'), p['price'])
        
        deal_lbl, deal_cls = get_deal_verdict(p['price'], est['estimated_price'])
        
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(212,175,55,0.2);border-radius:12px;padding:1.2rem;margin-bottom:1.5rem;text-align:center">
            <span style="font-size:14px;color:#aaa">Deal Classification Verdict</span><br>
            <span style="font-size:26px;font-weight:800;color:{'#00c864' if 'Great' in deal_lbl else ('#d4af37' if 'Fair' in deal_lbl else '#ff5050')}">{deal_lbl}</span>
            <p style="font-size:13px;color:#aaa;margin-top:5px">This property is listed at {format_price(p['price'])} compared to the AI market estimate of {format_price(est['estimated_price'])}.</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">AI Estimated Value</div>
                <div class="stat-number">{format_price(est['estimated_price'])}</div>
                <div style="font-size:12px;color:#888">Fair Market Range: {format_price(est['low'])} - {format_price(est['high'])}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Investment Score</div>
                <div class="stat-number" style="color:#00c864">{inv['score'] * 10:.0f}/100</div>
                <div style="font-size:12px;color:#aaa">{inv['verdict']}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Rental Yield & Appreciation</div>
                <div class="stat-number">~{inv['rental_yield_pct']}%</div>
                <div style="font-size:12px;color:#aaa">Rental Yield p.a.</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Recent Sales Table
        st.markdown("##### 🏛️ Recent Micro-Market Sales Comparison")
        base_rate = est['per_sqft_rate']
        sales_records = [
            {"Sold Date": "March 2026", "BHK": f"{p.get('bhk', 3)} BHK", "Size (sqft)": p.get('size_sqft', 1200) - 80, "Rate/sqft": f"₹{round(base_rate * 0.97):,}", "Final Price": format_price((base_rate * 0.97) * (p.get('size_sqft', 1200) - 80))},
            {"Sold Date": "January 2026", "BHK": f"{p.get('bhk', 3)} BHK", "Size (sqft)": p.get('size_sqft', 1200) + 120, "Rate/sqft": f"₹{round(base_rate * 1.01):,}", "Final Price": format_price((base_rate * 1.01) * (p.get('size_sqft', 1200) + 120))},
            {"Sold Date": "October 2025", "BHK": f"{p.get('bhk', 3)} BHK", "Size (sqft)": p.get('size_sqft', 1200), "Rate/sqft": f"₹{round(base_rate * 0.95):,}", "Final Price": format_price((base_rate * 0.95) * p.get('size_sqft', 1200))},
        ]
        st.dataframe(pd.DataFrame(sales_records), use_container_width=True)

        if PLOTLY_OK and p.get("price_history"):
            st.markdown("#### 📈 Price History Trend")
            hist_vals = p["price_history"]
            hist_years = [f"Year -{5-i}" for i in range(len(hist_vals)-1)] + ["Current"]
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Scatter(x=hist_years, y=hist_vals, mode="lines+markers", line=dict(color="#d4af37", width=3)))
            fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#fff", margin=dict(l=20,r=20,t=20,b=20))
            st.plotly_chart(fig_hist, use_container_width=True)
            
    # Tab 2: Location & Environment
    with dt2:
        st.markdown("#### 🌍 Location Coordinates & Neighborhood Intelligence")
        ec1, ec2 = st.columns(2)
        with ec1:
            aqi_val = p.get("aqi", 120)
            aqi_status = "Good" if aqi_val < 50 else ("Moderate" if aqi_val < 100 else "Poor")
            
            # Weather Block
            temp = 31 if p['city'].lower() in ['delhi', 'noida', 'gurgaon', 'mumbai'] else 25
            cond = "Sunny & Warm" if temp > 30 else "Cloudy & Breeze"
            
            st.markdown(f"""
            <div class="info-box">
                <h5>🌬️ Environment: AQI & Weather</h5>
                <p>Air Quality Index: <b>{aqi_val} ({aqi_status})</b></p>
                <p>Local Weather: <b>{temp}°C — {cond}</b></p>
            </div>
            <div class="info-box">
                <h5>🏫 School & Hospital Ratings (5 km radius)</h5>
                <p>1. Delhi Public School (Rank #2 in City) — 1.5 km</p>
                <p>2. Fortis Healthcare Hospital (Rating 4.8/5) — 2.2 km</p>
                <p>3. Sector Police Station Station — 1.8 km</p>
            </div>
            <div class="info-box">
                <h5>♿ Sunlight Facing & Access</h5>
                <p>Sunlight Direction: **{p.get('sunlight_facing', 'East')} facing**</p>
                <p>EV Charging station: **{'✅ Available' if p.get('ev_charging') else '❌ Not Available'}**</p>
                <p>Wheelchair accessibility: **{'✅ Fully Accessible' if p.get('wheelchair_access') else '❌ No'}**</p>
            </div>
            """, unsafe_allow_html=True)
        with ec2:
            if FOLIUM_OK and p.get("lat"):
                m = create_single_property_map(p['lat'], p['lng'], p['title'])
                st_folium(m, width="100%", height=300)
            else:
                st.warning("Maps coordinates not configured properly.")
 
    # Tab 3: Cost Calculator & Loan
    with dt3:
        st.markdown("#### 💰 On-Road Final Cost Breakdown")
        
        c_state = st.selectbox("Select State for Stamp Duty", ["Uttar Pradesh", "Maharashtra", "Delhi", "Karnataka", "Haryana", "Other"], index=["uttar pradesh", "maharashtra", "delhi", "karnataka", "haryana", "other"].index(p.get("state","delhi").lower()) if p.get("state","delhi").lower() in ["uttar pradesh", "maharashtra", "delhi", "karnataka", "haryana", "other"] else 2)
        is_female = st.checkbox("Buying under Female Owner name? (1% Stamp Duty Rebate)")
        is_new_proj = st.checkbox("Under Construction Property? (5% GST Applicable)", value=(p.get("possession") != "ready"))
        
        # Surcharges breakdown
        sd_data = stamp_duty(c_state, p["price"], is_female)
        
        # GST
        gst_amt = p["price"] * 0.05 if is_new_proj else 0.0
        
        # Brokerage calculation
        poster_role = "owner"
        try:
            users = _load_data(USERS_FILE)
            for u in users:
                if u["id"] == p.get("posted_by"):
                    poster_role = u.get("role", "owner")
        except Exception:
            pass
        broker_rate = 0.01 if poster_role == "agent" else 0.0
        brokerage_amt = p["price"] * broker_rate
        
        total_on_road = p["price"] + sd_data["stamp_duty_amount"] + sd_data["registration_fee"] + brokerage_amt + gst_amt
        
        st.markdown(f"""
        <table style="width:100%;border-collapse:collapse;margin-bottom:1.5rem">
            <tr style="border-bottom:1px solid #333"><td style="padding:10px">Base Cost</td><td style="text-align:right">{format_price(p['price'])}</td></tr>
            <tr style="border-bottom:1px solid #333"><td style="padding:10px">Stamp Duty (State rate)</td><td style="text-align:right">{format_price(sd_data['stamp_duty_amount'])}</td></tr>
            <tr style="border-bottom:1px solid #333"><td style="padding:10px">Registration Fees</td><td style="text-align:right">{format_price(sd_data['registration_fee'])}</td></tr>
            <tr style="border-bottom:1px solid #333"><td style="padding:10px">Brokerage Fee ({broker_rate*100:.1f}%)</td><td style="text-align:right">{format_price(brokerage_amt)}</td></tr>
            <tr style="border-bottom:1px solid #333"><td style="padding:10px">GST Charges (if applicable)</td><td style="text-align:right">{format_price(gst_amt)}</td></tr>
            <tr style="font-weight:700;color:#d4af37;border-top:2px solid #d4af37"><td style="padding:10px">Final On-Road Price</td><td style="text-align:right;font-size:18px">{format_price(total_on_road)}</td></tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🏦 Home Loan Planner")
        loan_amount = st.slider("Loan Principal (₹)", min_value=100000, max_value=int(p['price']), value=int(p['price']*0.8))
        loan_rate = st.slider("Interest Rate (% p.a.)", min_value=6.0, max_value=15.0, value=8.5, step=0.1)
        loan_tenure = st.slider("Tenure (Years)", min_value=5, max_value=30, value=20)
        
        emi_out = calculate_emi(loan_amount, loan_rate, loan_tenure)
        st.markdown(f"""
        <div class="info-box">
            <h4>Estimated Monthly EMI: <span style="color:#d4af37">{format_price(emi_out['emi'])}</span></h4>
            <p>Total Principal: {format_price(emi_out['principal'])} | Total Interest Payable: {format_price(emi_out['total_interest'])}</p>
        </div>
        """, unsafe_allow_html=True)
        
    # Tab 4: Legal & Verification
    with dt4:
        st.markdown("#### 🛡️ Legal Document Checklist & Audit")
        
        has_rera = p.get('rera_registered', False)
        has_legal = p.get('legal_approved', False)
        
        st.markdown(f"""
        <div class="info-box">
            <p>RERA Registration status: **{'✅ Verified & Registered' if has_rera else '⏳ Not Registered / Verification Pending'}**</p>
            <p>Title Registry clearance: **{'✅ Legal Audit Complete' if has_legal else '⏳ Pending Document Upload'}**</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("##### Legal Documents Checklist")
        st.checkbox("RERA Registration Certificate", value=has_rera, disabled=True)
        st.checkbox("Registry Deed / Sale Agreement", value=has_legal, disabled=True)
        st.checkbox("Encumbrance Certificate (EC) checked", value=has_legal, disabled=True)
        st.checkbox("Property Floor Plan Layout Approved", value=p.get('has_floor_plan', False), disabled=True)
        
        # Mock document downloads
        st.markdown("##### View Uploaded Documents")
        if has_legal:
            col_doc1, col_doc2 = st.columns(2)
            with col_doc1:
                st.button("📄 View Title Sale Deed (Mock PDF)")
            with col_doc2:
                st.button("📄 View RERA Registration Cert (Mock PDF)")
        else:
            st.info("No documents uploaded for this listing yet.")
            
        st.markdown("##### Book Lawyer Consultation")
        lawyers = ["Adv. Sandeep Rawat (Property Expert)", "Adv. Meera Sen (RERA Specialist)"]
        selected_lawyer = st.selectbox("Select Lawyer", lawyers)
        if st.button("Request Booking", key="lawyer_book_btn"):
            if is_logged_in():
                # save lawyer booking enquiry
                save_enquiry(p["id"], st.session_state["user"]["id"], "lawyer_booking", f"Consultation requested with {selected_lawyer}")
                st.success(f"Lawyer consultation request sent to {selected_lawyer}! They will contact you shortly.")
            else:
                st.error("Please login to book a lawyer consultation.")
 
    # Tab 5: Visit Scheduler
    with dt5:
        st.markdown("#### 📅 Visit Scheduler & Virtual Tour")
        v_type = st.radio("Tour Type", ["Physical Site Visit", "Live Video Tour (Zoom/WhatsApp)", "360° Virtual Tour"])
        
        if v_type == "360° Virtual Tour":
            st.markdown("##### 🛰️ Interactive 360° Room Viewer")
            st.markdown("<p style='color:#aaa;font-size:12px'>Rotate the view below using the selector to tour different rooms.</p>", unsafe_allow_html=True)
            room = st.selectbox("Select Room to Tour", ["Living Room", "Master Bedroom", "Kitchen", "Balcony"])
            
            room_details = {
                "Living Room": {"desc": "Spacious living area with premium Italian marble flooring, false ceiling, and LED cove lights.", "img_desc": "🌅 Panoramic garden view through double-glazed floor-to-ceiling windows."},
                "Master Bedroom": {"desc": "Wooden flooring, built-in wooden wardrobes, and direct access to the East-facing balcony.", "img_desc": "🛌 Elegant double-bed space with wooden panelling on headboard wall."},
                "Kitchen": {"desc": "Modern modular kitchen with granite countertop, chimney, and piped gas connection.", "img_desc": "🍳 L-shaped black granite counter with steel sink and high-end cabinets."},
                "Balcony": {"desc": "Spacious double balcony with anti-skid ceramic tiles and designer glass railings.", "img_desc": "🌳 Overlooking the 3-acre central community park and jogging track."}
            }
            
            st.markdown(f"""
            <div style="background:linear-gradient(135deg, rgba(212,175,55,0.08) 0%, rgba(255,255,255,0.02) 100%);border:2px solid #d4af37;border-radius:16px;padding:2rem;text-align:center;margin-bottom:1.5rem">
                <span style="font-size:60px">📸</span>
                <h4 style="color:#d4af37;margin-top:10px">360° Panoramas — {room}</h4>
                <p style="font-size:14px;color:#eee"><i>"{room_details[room]['img_desc']}"</i></p>
                <div style="background:rgba(255,255,255,0.05);padding:10px;border-radius:8px;font-size:12px;color:#ccc;margin-top:15px">
                    {room_details[room]['desc']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        v_date = st.date_input("Select Date")
        v_time = st.selectbox("Select Time Slot", ["10:00 AM - 12:00 PM", "02:00 PM - 04:00 PM", "04:00 PM - 06:00 PM"])
        
        if st.button("Schedule Visit"):
            if is_logged_in():
                visits = _load_data(VISITS_FILE)
                visits.append({
                    "id": f"visit_{int(datetime.now().timestamp())}",
                    "prop_id": p["id"],
                    "prop_title": p["title"],
                    "buyer_id": st.session_state["user"]["id"],
                    "buyer_name": st.session_state["user"]["name"],
                    "buyer_phone": st.session_state["user"]["phone"],
                    "tour_type": v_type,
                    "date": str(v_date),
                    "time": v_time,
                    "status": "pending",
                    "posted_by": p["posted_by"]
                })
                _save_data(VISITS_FILE, visits)
                st.success("Your visit request has been sent to the owner/agent for approval! Check status in Buyer Hub.")
            else:
                st.error("Please login to schedule a visit.")
            
    # Tab 6: Contact Owner
    with dt6:
        st.markdown("#### 👤 Contact Listing Agent / Owner")
        
        # Check if phone number is hidden
        if p.get("hide_contact"):
            st.warning("🔒 Owner has hidden their direct phone number to prevent spam.")
            if is_logged_in():
                calls = _load_data(CALLS_FILE)
                my_reqs = [c for c in calls if c["prop_id"] == p["id"] and c["buyer_id"] == st.session_state["user"]["id"]]
                
                if my_reqs:
                    req_status = my_reqs[0]["status"]
                    if req_status == "approved":
                        st.success("✅ Your callback request has been approved by the owner!")
                        st.markdown(f"""
                        <div class="info-box" style="border-color:#00c864">
                            <p>Owner Name: **{p['owner_name']}**</p>
                            <p>Phone Number: **+91 {p['owner_phone']}**</p>
                            <p>Email: **{p['owner_email']}**</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("⏳ Your call request is pending owner approval. You will see their number here once approved.")
                else:
                    if st.button("📞 Request Call Back"):
                        calls.append({
                            "id": f"call_{int(datetime.now().timestamp())}",
                            "prop_id": p["id"],
                            "buyer_id": st.session_state["user"]["id"],
                            "buyer_name": st.session_state["user"]["name"],
                            "buyer_phone": st.session_state["user"]["phone"],
                            "status": "pending",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        _save_data(CALLS_FILE, calls)
                        st.success("Call back request sent! Owner will approve and call you.")
                        st.rerun()
            else:
                st.info("Please login to request a callback.")
        else:
            st.markdown(f"""
            <div class="info-box">
                <p>Owner Name: **{p['owner_name']}**</p>
                <p>Phone Number: **+91 {p['owner_phone']}**</p>
                <p>Email: **{p['owner_email']}**</p>
            </div>
            """, unsafe_allow_html=True)
            
        # In-App Chat Simulation
        st.markdown("##### 💬 Send Direct Chat Message")
        if is_logged_in():
            chat_msg = st.text_input("Type your message to the owner", placeholder="Is the price negotiable?")
            if st.button("Send Message", key="chat_send_detail"):
                if chat_msg.strip():
                    chats = _load_data(CHATS_FILE)
                    chats.append({
                        "sender_id": st.session_state["user"]["id"],
                        "sender_name": st.session_state["user"]["name"],
                        "receiver_id": p["posted_by"],
                        "prop_id": p["id"],
                        "prop_title": p["title"],
                        "msg": chat_msg,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    _save_data(CHATS_FILE, chats)
                    st.success("Message sent! You can track responses on the Dashboard.")
        else:
            st.info("Login to chat directly.")

# ─────────────────────────────────────────────────────────────
# PAGE: AI ADVISOR & SEARCH
# ─────────────────────────────────────────────────────────────
def render_ai_consultant():
    st.markdown("### 🤖 SmartEstate AI Advisor (NLP Search)")
    st.markdown("<p style='color:#aaa'>Ask questions in plain Hindi or English. E.g., 'Delhi me 3BHK flat buy karna hai 70 lakh budget me'</p>", unsafe_allow_html=True)

    # Interactive suggestion chips
    st.markdown("💡 **Try asking the AI (Click to fill suggestion):**")
    c_chip1, c_chip2, c_chip3 = st.columns(3)
    with c_chip1:
        if st.button("📍 Sector 150 Noida report", key="chip_noida"):
            st.session_state["ai_query"] = "Sector 150 Noida me appreciation potential aur schools hospital batao"
            st.rerun()
    with c_chip2:
        if st.button("💰 Bangalore 2BHK rental yield", key="chip_bangalore"):
            st.session_state["ai_query"] = "Bangalore Indiranagar price valuation of 2BHK flat"
            st.rerun()
    with c_chip3:
        if st.button("📈 Muzaffarnagar plot investment", key="chip_muz"):
            st.session_state["ai_query"] = "Muzaffarnagar me 30 lakh tak plot chahiye investment ke liye"
            st.rerun()

    with st.expander("⚙️ Enable Advanced Gemini API responses"):
        key = st.text_input("Enter Gemini API Key", type="password")
        if key:
            st.session_state["gemini_key"] = key
            st.success("Gemini API key loaded!")

    query_val = st.session_state.get("ai_query", "")
    query = st.text_area("What are you looking for today?", value=query_val, placeholder="Type your query...")
    
    if st.button("🤖 Generate Recommendations", type="primary"):
        if query.strip():
            with st.spinner("AI is analyzing local micro-markets..."):
                all_p = get_all_properties()
                res = ai_consult(query, all_p, gemini_key=st.session_state.get("gemini_key"))
                st.markdown(f"<div class='ai-response'>{res}</div>", unsafe_allow_html=True)
                st.session_state["ai_query"] = "" # Reset chip query
        else:
            st.warning("Please type your search request first.")

# ─────────────────────────────────────────────────────────────
# PAGE: LOCALITY INTELLIGENCE
# ─────────────────────────────────────────────────────────────
def render_locality():
    st.markdown("### 📊 AI Locality Report Generator")
    st.markdown("<p style='color:#aaa'>Discover the safety, appreciation, and environment of top Indian localities before buying</p>", unsafe_allow_html=True)
    
    localities = {
        "Sector 62, Noida": {
            "city": "Noida", "safety": 4, "growth": "High", "score": 91, "traffic": "Moderate", 
            "water": "Good", "power": "Rare", "internet": ["JioFiber", "Airtel Black", "Tata Play"], 
            "flood": "Safe Zone (No history of logging)", "schools": 12, "hospitals": 6, 
            "metro_dist": "0.8 km", "police_dist": "1.2 km", "ev_charging": "6 stations nearby",
            "upcoming_projects": ["Metro Blue Line Underpass Extension", "Model Town highway interchange"],
            "suggested_for": "Families & Corporate Office Professionals",
            "trend": [5500, 5800, 6200, 6800, 7200]
        },
        "Sector 150, Noida": {
            "city": "Noida", "safety": 4.5, "growth": "Very High", "score": 95, "traffic": "Low", 
            "water": "Excellent", "power": "None", "internet": ["JioFiber", "Airtel Black"], 
            "flood": "Safe Zone (Elevated terrain)", "schools": 8, "hospitals": 4, 
            "metro_dist": "2.1 km", "police_dist": "2.5 km", "ev_charging": "8 stations nearby",
            "upcoming_projects": ["Noida-Greater Noida Expressway flyover", "Sports City hub development"],
            "suggested_for": "Investment & High-End Luxury Families",
            "trend": [6800, 7300, 8000, 8900, 9500]
        },
        "Dwarka, Delhi": {
            "city": "Delhi", "safety": 4, "growth": "Moderate", "score": 85, "traffic": "Heavy", 
            "water": "Average", "power": "Occasional", "internet": ["JioFiber", "Airtel Black", "Excitel"], 
            "flood": "Low Risk (Minor street flooding in monsoon)", "schools": 22, "hospitals": 11, 
            "metro_dist": "0.4 km", "police_dist": "0.8 km", "ev_charging": "12 stations nearby",
            "upcoming_projects": ["Urban Extension Road-II (UER-II) connection", "Bharat Vandana Park"],
            "suggested_for": "Families & Retired Officers",
            "trend": [8200, 8500, 8900, 9300, 9800]
        },
        "Indiranagar, Bangalore": {
            "city": "Bangalore", "safety": 4.5, "growth": "High", "score": 94, "traffic": "Heavy", 
            "water": "Good", "power": "Rare", "internet": ["JioFiber", "Airtel Black", "ACT Fibernet"], 
            "flood": "Safe Zone", "schools": 15, "hospitals": 8, 
            "metro_dist": "0.3 km", "police_dist": "0.6 km", "ev_charging": "15 stations nearby",
            "upcoming_projects": ["Ejipura flyover alignment", "Metro green line connectivity upgrades"],
            "suggested_for": "Young Professionals, Students & Commercial Offices",
            "trend": [12000, 12600, 13200, 14000, 14800]
        },
        "Bandra West, Mumbai": {
            "city": "Mumbai", "safety": 5, "growth": "Stable", "score": 96, "traffic": "Heavy", 
            "water": "Excellent", "power": "None", "internet": ["JioFiber", "Airtel Black", "Hathway"], 
            "flood": "Moderate Risk (Water logging at Carter Road in heavy rains)", "schools": 18, "hospitals": 10, 
            "metro_dist": "1.1 km", "police_dist": "0.5 km", "ev_charging": "10 stations nearby",
            "upcoming_projects": ["Coastal Road Link Project", "Metro Line 3 Bandra station integration"],
            "suggested_for": "HNIs, Celebrities & Luxury Lifestyles",
            "trend": [32000, 33500, 35000, 36500, 38000]
        }
    }
    
    selected_loc = st.selectbox("Select Locality / Area", list(localities.keys()))
    
    if selected_loc:
        loc_data = localities[selected_loc]
        
        st.markdown(f"""
        <div class="report-card">
            <h3 style="color:#d4af37">📊 AI Locality Intel Report: {selected_loc}</h3>
            <hr style="border-color:rgba(212,175,55,0.2)">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:1.5rem">
                <div>
                    <p><b>🏢 City:</b> {loc_data['city']}</p>
                    <p><b>🛡️ Area Safety Rating:</b> {'⭐' * int(loc_data['safety'])} ({loc_data['safety']}/5)</p>
                    <p><b>📈 Future Capital Growth:</b> <span style="color:#00c864;font-weight:700">{loc_data['growth']}</span></p>
                    <p><b>🚦 Traffic Score:</b> {loc_data['traffic']} Congestion</p>
                    <p><b>⚡ Power Cut History:</b> {loc_data['power']}</p>
                    <p><b>🚰 Water Availability:</b> {loc_data['water']}</p>
                </div>
                <div>
                    <p><b>🏆 Locality Score:</b> <span style="font-size:24px;color:#d4af37;font-weight:800">{loc_data['score']}/100</span></p>
                    <p><b>🏫 School Rankings:</b> {loc_data['schools']} within 5 km</p>
                    <p><b>🏥 Hospital Ratings:</b> {loc_data['hospitals']} verified in 5 km</p>
                    <p><b>🚔 Nearest Police Station:</b> {loc_data['police_dist']}</p>
                    <p><b>🔌 EV Charging:</b> {loc_data['ev_charging']}</p>
                    <p><b>🚇 Nearest Metro Station:</b> {loc_data['metro_dist']}</p>
                </div>
            </div>
            <div class="info-box">
                <b>🌐 Broadband Internet Providers:</b> {', '.join(loc_data['internet'])}<br>
                <b>🌧️ Flood-Prone Area Alert:</b> <span style="color:{'#ff5050' if 'Moderate' in loc_data['flood'] else '#00c864'}">{loc_data['flood']}</span><br>
                <b>🎯 Suggested For:</b> {loc_data['suggested_for']}<br>
                <b>📍 Upcoming Metro/Highway Projects:</b> {', '.join(loc_data['upcoming_projects'])}
            </div>
            <p style="margin-top:10px"><b>💡 AI Market Recommendation:</b> Locality rating is in the top decile. Ideal for long-term equity growth and rental yield.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Price Trend Graph
        if PLOTLY_OK:
            st.markdown("#### 📈 5-Year Area Price Trend (per sqft)")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=["2020", "2021", "2022", "2023", "2024"], 
                y=loc_data["trend"],
                mode="lines+markers", 
                line=dict(color="#d4af37", width=3)
            ))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#fff")
            st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# PAGE: POST PROPERTY OR REQUIREMENT
# ─────────────────────────────────────────────────────────────
def render_post_property():
    st.markdown("### 📤 Upload Center")
    
    post_tab, req_tab = st.tabs(["Post Property", "Post Buyer Requirement"])
    
    # Sub-tab 1: Post Property
    with post_tab:
        if not is_logged_in():
            st.warning("🔐 Please login from the sidebar first to post properties.")
        else:
            user = st.session_state["user"]
            with st.form("post_prop_form"):
                title = st.text_input("Title *", placeholder="e.g. Elegant 3BHK in Sector 137, Noida")
                col_a, col_b = st.columns(2)
                with col_a:
                    p_type = st.selectbox("Type", ["apartment", "villa", "plot", "office", "shop"])
                    city = st.text_input("City *", placeholder="e.g. Noida")
                    state = st.text_input("State", placeholder="e.g. Uttar Pradesh")
                    hide_phone = st.checkbox("Hide my phone number from public layout")
                with col_b:
                    listing = st.selectbox("Listed for", ["buy", "rent"])
                    area = st.text_input("Area *", placeholder="e.g. Sector 137")
                    price = st.number_input("Price (₹) *", min_value=1000)
                    
                sqft = st.number_input("Sqft Size *", min_value=100)
                bhk = st.selectbox("BHK", [1, 2, 3, 4, 5])
                desc = st.text_area("Description")
                
                st.markdown("##### 📄 Document Verification & Floor Plans")
                rera_no_input = st.text_input("RERA Registration Number", placeholder="e.g. UPRERAPRJ12345")
                uploaded_docs = st.file_uploader("Upload Legal Property Documents (Title Deed, Sale Deed)", accept_multiple_files=True)
                uploaded_floor = st.file_uploader("Upload Floor Plan Layout Image", type=["png", "jpg", "jpeg"])
                uploaded_photos = st.file_uploader("Upload Property Photos", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
                
                st.markdown("**Choose Listing Plan**")
                plan = st.radio("Upload Plan", ["Free (Standard)", "Featured Plan (₹499/mo) - 💎 Premium badge"])
                
                if st.form_submit_button("🚀 Post Property Listing"):
                    if not title or not city or not area or price <= 0:
                        st.error("Please fill all mandatory fields.")
                    else:
                        # Duplicate check
                        is_dup, dup_id = detect_duplicates(title, area, sqft)
                        if is_dup:
                            st.warning(f"⚠️ AI detected this might be a duplicate listing of property ID {dup_id}!")
                        else:
                            # Handle photo uploads
                            images_saved = []
                            if uploaded_photos:
                                for idx, f in enumerate(uploaded_photos):
                                    fn = f"p_{int(datetime.now().timestamp())}_{idx}.jpg"
                                    fpath = os.path.join(UPLOADS_DIR, fn)
                                    try:
                                        with open(fpath, "wb") as out_f:
                                            out_f.write(f.getbuffer())
                                        images_saved.append(f"assets/uploads/{fn}")
                                    except Exception:
                                        pass
                            
                            loc = geocode(f"{area}, {city}, {state}, India")
                            new_p = {
                                "id": f"prop_{int(datetime.now().timestamp())}",
                                "title": title, "type": p_type, "listing_type": listing,
                                "city": city, "area": area, "state": state,
                                "pincode": "", "price": price, "price_per_sqft": round(price/sqft), "size_sqft": sqft,
                                "bhk": bhk, "bedrooms": bhk, "bathrooms": bhk - 1 if bhk > 1 else 1, "parking": 1,
                                "floor": 1, "total_floors": 4, "furnishing": "unfurnished", "status": "available",
                                "verified": bool(uploaded_docs), "premium": "Featured" in plan, "lat": loc["lat"], "lng": loc["lng"],
                                "description": desc, "amenities": ["parking", "security"], "images": images_saved,
                                "owner_name": user["name"], "owner_phone": user["phone"], "owner_whatsapp": user["phone"],
                                "owner_email": user["email"], "posted_by": user["id"],
                                "posted_date": datetime.now().strftime("%Y-%m-%d"), "views": 0, "leads": 0,
                                "possession": "ready", "age_years": 0, "facing": "East", "approved": False,
                                "hide_contact": hide_phone, "aqi": 100, "ev_charging": False, "wheelchair_access": True,
                                "price_history": [price],
                                "rera_registered": bool(rera_no_input),
                                "rera_no": rera_no_input,
                                "legal_approved": bool(uploaded_docs),
                                "has_floor_plan": bool(uploaded_floor)
                            }
                            save_property(new_p)
                            st.success("Submitted! Property is pending approval from Admin.")
                            st.balloons()
                            
    # Sub-tab 2: Post Buyer Requirement
    with req_tab:
        if not is_logged_in():
            st.warning("🔐 Please login from the sidebar first to post requirements.")
        else:
            user = st.session_state["user"]
            with st.form("buyer_req_form"):
                req_city = st.text_input("Target City *", placeholder="Noida")
                req_bhk = st.selectbox("BHK Required", [1, 2, 3, 4, 5])
                req_budget = st.number_input("Max Budget (₹) *", min_value=100000)
                
                if st.form_submit_button("📢 Broadcast Requirement"):
                    reqs = _load_data(REQ_FILE)
                    reqs.append({
                        "id": f"req_{int(datetime.now().timestamp())}",
                        "buyer_id": user["id"],
                        "buyer_name": user["name"],
                        "city": req_city,
                        "bhk": req_bhk,
                        "budget": req_budget,
                        "timestamp": datetime.now().strftime("%Y-%m-%d")
                    })
                    _save_data(REQ_FILE, reqs)
                    st.success("Requirement broadcasted! AI will match this with property listings and notify matching owners.")

# ─────────────────────────────────────────────────────────────
# PAGE: DASHBOARD & CRM
# ─────────────────────────────────────────────────────────────
def render_dashboard():
    st.markdown("### 📊 Dashboard & CRM Manager")
    if not is_logged_in():
        st.warning("🔐 Please login from the sidebar first.")
        st.stop()
        
    user = st.session_state["user"]
    my_props = get_properties_by_user(user["id"])
    
    t_list, t_leads, t_hub, t_crm, t_chats = st.tabs(["Listings Managed", "Notifications & Leads", "My Buyer Hub", "Agent CRM Portal", "In-App Chats"])
    
    # Tab 1: Listings Managed
    with t_list:
        if not my_props:
            st.info("You haven't listed any properties yet.")
        else:
            for pr in my_props:
                st.markdown(f"""
                <div class="info-box">
                    <h5>🏠 {pr['title']}</h5>
                    <p>Price: {format_price(pr['price'])} | City: {pr['city']} | Status: **{pr['status'].upper()}**</p>
                    <p>Views: 👁 {pr.get('views',0)} | Leads: 📩 {pr.get('leads',0)} | Approved: {'✅ Yes' if pr['approved'] else '⏳ Pending Review'}</p>
                </div>
                """, unsafe_allow_html=True)
                col_sd, col_dl = st.columns(2)
                with col_sd:
                    if pr["status"] == "available":
                        if st.button("Mark as Sold / Rented", key=f"sold_{pr['id']}"):
                            update_property(pr["id"], {"status": "sold"})
                            st.success("Status updated!")
                            st.rerun()
                with col_dl:
                    if st.button("Delete Listing", key=f"del_{pr['id']}"):
                        delete_property(pr["id"])
                        st.warning("Property deleted.")
                        st.rerun()
                        
    # Tab 2: Notifications & Leads
    with t_leads:
        st.markdown("#### Call Back Requests")
        calls = _load_data(CALLS_FILE)
        my_calls = [c for c in calls if get_property_by_id(c["prop_id"]) and get_property_by_id(c["prop_id"])["posted_by"] == user["id"]]
        
        if not my_calls:
            st.info("No callback requests at this moment.")
        else:
            for c in my_calls:
                st.markdown(f"""
                <div class="info-box">
                    <p>Buyer Name: **{c['buyer_name']}** | Phone: **{c['buyer_phone']}**</p>
                    <p>Requested On: {c['timestamp']} | Status: **{c['status'].upper()}**</p>
                </div>
                """, unsafe_allow_html=True)
                if c["status"] == "pending":
                    if st.button("Approve Call Request", key=f"ap_call_{c['id']}"):
                        c["status"] = "approved"
                        _save_data(CALLS_FILE, calls)
                        st.success("Approved call request!")
                        st.rerun()
                        
        st.markdown("#### 📅 Scheduled Site Visits")
        visits = _load_data(VISITS_FILE)
        my_visits = [v for v in visits if v.get("posted_by") == user["id"]]
        if not my_visits:
            st.info("No scheduled site visits.")
        else:
            for v in my_visits:
                st.markdown(f"""
                <div class="info-box">
                    <p>Buyer: **{v['buyer_name']}** ({v['buyer_phone']})</p>
                    <p>Listing: **{v['prop_title']}**</p>
                    <p>Type: **{v['tour_type']}** | Date: **{v['date']}** | Time: **{v['time']}**</p>
                    <p>Status: **{v['status'].upper()}**</p>
                </div>
                """, unsafe_allow_html=True)
                if v["status"] == "pending":
                    col_app, col_rej = st.columns(2)
                    with col_app:
                        if st.button("Approve Visit", key=f"app_vis_{v['id']}"):
                            v["status"] = "approved"
                            _save_data(VISITS_FILE, visits)
                            st.success("Approved visit!")
                            st.rerun()
                    with col_rej:
                        if st.button("Reject Visit", key=f"rej_vis_{v['id']}"):
                            v["status"] = "rejected"
                            _save_data(VISITS_FILE, visits)
                            st.warning("Rejected visit.")
                            st.rerun()

        st.markdown("#### AI Requirement Matches")
        reqs = _load_data(REQ_FILE)
        matched_reqs = []
        for r in reqs:
            for p in my_props:
                if p["city"].lower() == r["city"].lower() and p["bhk"] == r["bhk"] and p["price"] <= r["budget"]:
                    matched_reqs.append((r, p))
                    
        if not matched_reqs:
            st.info("No active buyer requirements match your listings right now.")
        else:
            for r, p in matched_reqs:
                st.markdown(f"""
                <div class="info-box" style="border-color:#00c864">
                    <h5>🔥 AI Match Found!</h5>
                    <p>Buyer **{r['buyer_name']}** is looking for a **{r['bhk']} BHK** in **{r['city']}** with a budget of **{format_price(r['budget'])}**</p>
                    <p>Matching Property: **{p['title']}**</p>
                    <p>Contact Email: {r['buyer_id']} (Send proposal directly!)</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Message {r['buyer_name']}", key=f"match_chat_{r['id']}_{p['id']}"):
                    chats = _load_data(CHATS_FILE)
                    chats.append({
                        "sender_id": user["id"],
                        "sender_name": user["name"],
                        "receiver_id": r["buyer_id"],
                        "prop_id": p["id"],
                        "prop_title": p["title"],
                        "msg": f"Hi, I saw your requirement in {r['city']}. My property '{p['title']}' matches your search! Let me know if you would like to discuss.",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    _save_data(CHATS_FILE, chats)
                    st.success(f"Notification message sent to {r['buyer_name']}! Check replies in Chats tab.")
                
    # Tab 3: My Buyer Hub
    with t_hub:
        st.markdown("#### 🛒 Buyer Activity & Workspace")
        
        visits = _load_data(VISITS_FILE)
        calls = _load_data(CALLS_FILE)
        reqs = _load_data(REQ_FILE)
        
        hub_opt = st.radio("Activity Category", ["Profile & KYC", "My Scheduled Tours", "My Call Requests", "My Requirements Broadcasted"], horizontal=True)
        
        if hub_opt == "Profile & KYC":
            st.markdown("#### 🛡️ Profile KYC Verification")
            if user.get("kyc_verified"):
                st.success("✅ Your profile is fully KYC Verified. You have the 'Verified Listing Owner' or 'Trusted Agent' badge active!")
            else:
                st.markdown("<p style='color:#aaa'>Verify your profile with Aadhaar & PAN card to get the 👑 Verified Owner or 🎖️ Trusted Agent badge and increase leads.</p>", unsafe_allow_html=True)
                
                # Setup session state helper
                if "kyc_otp_sent" not in st.session_state:
                    st.session_state["kyc_otp_sent"] = False
                
                with st.form("kyc_verif_form"):
                    aadhaar_no = st.text_input("Aadhaar Number (12 digits)", placeholder="e.g. 123456789012")
                    pan_no = st.text_input("PAN Card Number (10 characters)", placeholder="e.g. ABCDE1234F")
                    kyc_phone = st.text_input("Phone Number linked with Aadhaar", value=user.get("phone",""))
                    
                    kyc_submit = st.form_submit_button("📩 Generate Aadhaar OTP")
                    if kyc_submit:
                        if len(aadhaar_no) != 12 or not aadhaar_no.isdigit():
                            st.error("Aadhaar number must be exactly 12 digits.")
                        elif len(pan_no) != 10:
                            st.error("PAN number must be exactly 10 characters.")
                        else:
                            st.session_state["kyc_otp_sent"] = True
                            st.session_state["kyc_aadhaar"] = aadhaar_no
                            st.session_state["kyc_pan"] = pan_no
                            st.success("OTP sent to Aadhaar-registered phone number! Enter mock OTP '1234' to verify.")
                
                if st.session_state.get("kyc_otp_sent"):
                    with st.form("kyc_otp_form"):
                        otp_entered = st.text_input("Enter 4-digit OTP", placeholder="Enter 1234")
                        if st.form_submit_button("✅ Verify KYC & Grant Badge"):
                            if otp_entered == "1234":
                                users = _load_data(USERS_FILE)
                                for u in users:
                                    if u["id"] == user["id"]:
                                        u["kyc_verified"] = True
                                        u["aadhaar"] = st.session_state["kyc_aadhaar"]
                                        u["pan"] = st.session_state["kyc_pan"]
                                _save_data(USERS_FILE, users)
                                st.session_state["user"]["kyc_verified"] = True
                                st.session_state["kyc_otp_sent"] = False
                                st.success("🎉 Congratulations! Your KYC has been verified. Verified badge is now active.")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("Incorrect OTP. Enter '1234' for verification.")
                                
        elif hub_opt == "My Scheduled Tours":
            my_visits = [v for v in visits if v.get("buyer_id") == user["id"]]
            if not my_visits:
                st.info("You haven't scheduled any tours yet.")
            else:
                for v in my_visits:
                    st.markdown(f"""
                    <div class="info-box">
                        <h5>🏠 {v['prop_title']}</h5>
                        <p>Tour Type: **{v['tour_type']}** | Date: **{v['date']}** | Time: **{v['time']}**</p>
                        <p>Status: **{v['status'].upper()}**</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
        elif hub_opt == "My Call Requests":
            my_calls = [c for c in calls if c.get("buyer_id") == user["id"]]
            if not my_calls:
                st.info("No callback requests found.")
            else:
                for c in my_calls:
                    p_info = get_property_by_id(c["prop_id"])
                    p_title = p_info["title"] if p_info else "Property Details"
                    status_lbl = "Approved (Check Owner Details Below)" if c["status"] == "approved" else "Pending Owner Approval"
                    st.markdown(f"""
                    <div class="info-box" style="border-left:4px solid {'#00c864' if c['status']=='approved' else '#ff9600'}">
                        <h5>📞 {p_title}</h5>
                        <p>Requested On: {c['timestamp']} | Status: **{status_lbl}**</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if c["status"] == "approved" and p_info:
                        st.markdown(f"""
                        <div style="background:rgba(0,200,100,0.05);padding:10px;border-radius:6px;font-size:13px">
                            👤 Owner: <b>{p_info['owner_name']}</b><br>
                            📞 Phone: <b>+91 {p_info['owner_phone']}</b><br>
                            ✉️ Email: {p_info['owner_email']}
                        </div>
                        """, unsafe_allow_html=True)
                        
        elif hub_opt == "My Requirements Broadcasted":
            my_reqs = [r for r in reqs if r.get("buyer_id") == user["id"]]
            if not my_reqs:
                st.info("You haven't broadcasted any requirements.")
            else:
                for r in my_reqs:
                    st.markdown(f"""
                    <div class="info-box">
                        <h5>📢 {r['bhk']} BHK in {r['city']}</h5>
                        <p>Max Budget: {format_price(r['budget'])} | Posted: {r['timestamp']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Delete Requirement", key=f"del_req_{r['id']}"):
                        reqs = [rq for rq in reqs if rq["id"] != r["id"]]
                        _save_data(REQ_FILE, reqs)
                        st.success("Deleted requirement!")
                        st.rerun()

    # Tab 4: Agent CRM
    with t_crm:
        if user.get("role") != "agent":
            st.info("Agent CRM tools are only available to Agent profiles.")
        else:
            st.markdown("#### 🧑💼 Agent CRM Workspace")
            
            leads = _load_data(LEADS_FILE)
            reminders = _load_data(REMINDERS_FILE)
            
            crm_opt = st.radio("CRM Sub-Section", ["Pipeline & Lead Management", "Follow-up Reminders", "Commission Reports"], horizontal=True)
            
            if crm_opt == "Pipeline & Lead Management":
                st.markdown("##### 🏁 Deal Pipeline")
                stages = ["New Leads", "Contacted", "Site Visit Scheduled", "Negotiation", "Deal Closed"]
                
                cols_pipeline = st.columns(5)
                for i, stg in enumerate(stages):
                    with cols_pipeline[i]:
                        st.markdown(f"**{stg}**")
                        stg_leads = [ld for ld in leads if ld.get("stage") == stg and ld.get("agent_id") == user["id"]]
                        if not stg_leads:
                            st.markdown("<p style='color:#555;font-size:12px'>No leads</p>", unsafe_allow_html=True)
                        else:
                            for ld in stg_leads:
                                st.markdown(f"""
                                <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(212,175,55,0.2);padding:10px;border-radius:8px;margin-bottom:8px;font-size:12px">
                                    <b>👤 {ld['name']}</b><br>
                                    📞 {ld['phone']}<br>
                                    🏠 {ld['property']}<br>
                                    {f"💰 Comm: {format_price(ld['commission'])}" if ld.get('commission') else ""}
                                </div>
                                """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                c_up1, c_up2 = st.columns(2)
                with c_up1:
                    st.markdown("##### ➕ Add New CRM Lead")
                    with st.form("crm_add_lead"):
                        ld_name = st.text_input("Lead Name")
                        ld_phone = st.text_input("Phone")
                        ld_prop = st.text_input("Property / Listing of Interest")
                        ld_stg = st.selectbox("Stage", stages)
                        ld_comm = st.number_input("Est. Commission (₹)", min_value=0, value=0)
                        
                        if st.form_submit_button("Add Lead"):
                            if ld_name and ld_phone:
                                new_ld = {
                                    "id": f"lead_{int(datetime.now().timestamp())}",
                                    "name": ld_name,
                                    "phone": ld_phone,
                                    "property": ld_prop,
                                    "stage": ld_stg,
                                    "commission": ld_comm if ld_stg == "Deal Closed" else 0,
                                    "agent_id": user["id"]
                                }
                                leads.append(new_ld)
                                _save_data(LEADS_FILE, leads)
                                st.success("Lead added successfully!")
                                st.rerun()
                            else:
                                st.error("Please fill Name and Phone.")
                                
                with c_up2:
                    st.markdown("##### 🔄 Update Lead Stage")
                    agent_leads = [ld for ld in leads if ld.get("agent_id") == user["id"]]
                    if not agent_leads:
                        st.info("No leads available to update.")
                    else:
                        with st.form("crm_update_stage"):
                            ld_select = st.selectbox("Select Lead", [ld["name"] for ld in agent_leads])
                            ld_new_stg = st.selectbox("New Stage", stages)
                            ld_up_comm = st.number_input("Commission (if Closed) (₹)", min_value=0, value=25000)
                            
                            if st.form_submit_button("Update Stage"):
                                for ld in leads:
                                    if ld["name"] == ld_select and ld["agent_id"] == user["id"]:
                                        ld["stage"] = ld_new_stg
                                        if ld_new_stg == "Deal Closed":
                                            ld["commission"] = ld_up_comm
                                _save_data(LEADS_FILE, leads)
                                st.success("Lead stage updated!")
                                st.rerun()
                                
            elif crm_opt == "Follow-up Reminders":
                st.markdown("##### 📅 Reminders & Follow-ups")
                agent_rems = [rm for rm in reminders if rm.get("agent_id") == user["id"]]
                
                if not agent_rems:
                    st.info("No follow-up reminders scheduled.")
                else:
                    for rm in agent_rems:
                         status_str = "✅ Completed" if rm.get("done") else "⏳ Pending"
                         st.markdown(f"""
                         <div class="info-box" style="border-left:4px solid {'#00c864' if rm.get('done') else '#d4af37'}">
                             <p>📝 {rm['text']}</p>
                             <p style="font-size:12px;color:#aaa">Due Date: {rm['date']} | Status: {status_str}</p>
                         </div>
                         """, unsafe_allow_html=True)
                         if not rm.get("done"):
                             if st.button("Mark Complete", key=f"don_rem_{rm['id']}"):
                                 for r in reminders:
                                     if r["id"] == rm["id"]:
                                         r["done"] = True
                                 _save_data(REMINDERS_FILE, reminders)
                                 st.success("Reminder completed!")
                                 st.rerun()
                                 
                st.markdown("---")
                st.markdown("##### ⏰ Add Reminder")
                with st.form("crm_add_reminder"):
                    rem_text = st.text_input("Reminder Description")
                    rem_date = st.date_input("Follow-up Date")
                    if st.form_submit_button("Add Reminder"):
                        if rem_text:
                            reminders.append({
                                "id": f"rem_{int(datetime.now().timestamp())}",
                                "text": rem_text,
                                "date": str(rem_date),
                                "done": False,
                                "agent_id": user["id"]
                            })
                            _save_data(REMINDERS_FILE, reminders)
                            st.success("Reminder added!")
                            st.rerun()
                        else:
                            st.error("Please fill description.")
                            
            elif crm_opt == "Commission Reports":
                st.markdown("##### 📈 Deal Commission & Revenues")
                closed_leads = [ld for ld in leads if ld.get("stage") == "Deal Closed" and ld.get("agent_id") == user["id"]]
                total_earned = sum(ld.get("commission", 0) for ld in closed_leads)
                
                c_c1, c_c2 = st.columns(2)
                with c_c1:
                    st.metric("Total Commission Earned (Life Time)", format_price(total_earned), "+15% this quarter")
                with c_c2:
                    st.metric("Deals Closed (Total count)", f"{len(closed_leads)} Deals")
                    
                st.markdown("##### Closed Deals Directory")
                if not closed_leads:
                    st.info("No closed deals recorded yet.")
                else:
                    df_closed = pd.DataFrame(closed_leads)[["name", "phone", "property", "commission"]]
                    st.dataframe(df_closed, use_container_width=True)

    # Tab 5: Chats
    with t_chats:
        st.markdown("#### Direct Chat Box Inbox")
        chats = _load_data(CHATS_FILE)
        my_chats = [c for c in chats if c["receiver_id"] == user["id"]]
        
        if not my_chats:
            st.info("No incoming messages in your inbox.")
        else:
            for ch in my_chats:
                st.markdown(f"""
                <div class="info-box">
                    <p><b>{ch['sender_name']}</b> on listing <b>{ch['prop_title']}</b>:</p>
                    <p>"{ch['msg']}"</p>
                    <p style="font-size:11px;color:#555">{ch['timestamp']}</p>
                </div>
                """, unsafe_allow_html=True)
                reply = st.text_input("Reply", key=f"rep_{ch['timestamp']}")
                if st.button("Send Reply", key=f"rep_btn_{ch['timestamp']}"):
                    if reply.strip():
                        chats.append({
                            "sender_id": user["id"],
                            "sender_name": user["name"],
                            "receiver_id": ch["sender_id"],
                            "prop_id": ch["prop_id"],
                            "prop_title": ch["prop_title"],
                            "msg": reply,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        _save_data(CHATS_FILE, chats)
                        st.success("Reply sent!")
                        st.rerun()

# ─────────────────────────────────────────────────────────────
# PAGE: BUILDERS PROJECTS
# ─────────────────────────────────────────────────────────────
def render_projects():
    st.markdown("### 🏢 Builder Trust Profiles & Projects")
    
    tab_builders, tab_projects = st.tabs(["Builders Profile Directory", "Newly Launched Projects & Timeline"])
    
    with tab_builders:
        st.markdown("#### 🛡️ Verified Real Estate Developers")
        builders_data = [
            {
                "name": "DLF Limited",
                "year": "1946",
                "delivered": "150+ Projects",
                "on_time": "96%",
                "rating": 5,
                "description": "DLF has a 75-year track record of commercial and residential excellence. Renowned for luxury townships and high-rise premium condominiums.",
                "completion_history": "Delivered major landmarks in Delhi NCR, Chennai, Hyderabad, and Chandigarh."
            },
            {
                "name": "ATS Greens",
                "year": "1998",
                "delivered": "35+ Projects",
                "on_time": "92%",
                "rating": 4,
                "description": "ATS Greens has become synonymous with quality residential construction, lush green landscaping, and timely delivery in the Noida-Greater Noida micro-markets.",
                "completion_history": "ATS Pristine, ATS One Hamlet, and ATS Heavenly Foothills completed successfully."
            },
            {
                "name": "Godrej Properties",
                "year": "1990",
                "delivered": "60+ Projects",
                "on_time": "98%",
                "rating": 5,
                "description": "Bringing the Godrej Group philosophy of innovation, sustainability, and excellence to the real estate industry. Recognized for eco-friendly designs.",
                "completion_history": "Prime developments in Mumbai, Bangalore, Pune, and Noida Sector 150."
            }
        ]
        
        for b in builders_data:
            st.markdown(f"""
            <div class="prop-card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <h3 style="margin:0;color:#d4af37">{b['name']}</h3>
                    <span style="font-size:16px">⭐ {b['rating']}.0 / 5.0</span>
                </div>
                <div style="font-size:12px;color:#aaa;margin-top:4px">Established: {b['year']} | Total Delivered: {b['delivered']}</div>
                <p style="margin:10px 0;font-size:13px;color:#ddd">{b['description']}</p>
                <div style="background:rgba(255,255,255,0.03);padding:8px 12px;border-radius:6px;font-size:12px">
                    🛡️ <b>On-Time Completion Rate:</b> <span style="color:#00c864;font-weight:700">{b['on_time']}</span><br>
                    🏛️ <b>Delivery History:</b> {b['completion_history']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    with tab_projects:
        st.markdown("#### 🏗️ Under Construction Projects & RERA Timelines")
        projs = get_all_projects()
        
        for idx, pr in enumerate(projs):
            with st.expander(f"🏢 {pr['name']} — {pr['city']} | {pr['price_range']}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""
                    <p><b>Builder:</b> {pr['builder']}</p>
                    <p><b>Configuration:</b> {', '.join(pr['bhk_options'])}</p>
                    <p><b>RERA Registration:</b> {pr['rera_no']}</p>
                    <p><b>Description:</b> {pr['description']}</p>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class="info-box">
                        <p>Total Units: {pr['total_units']} | Remaining: {pr['available_units']}</p>
                        <p>Appraisal Rating: {'⭐' * pr['rating']}</p>
                        <p><b>Possession Target:</b> {pr['possession_date']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Construction Progress Bar
                    st.write(f"Construction Progress: **{pr['progress_percent']}%**")
                    st.progress(pr['progress_percent'] / 100)
                    
                    wa = f"https://wa.me/919999999999?text=Enquiry+about+{pr['name']}"
                    st.link_button("💬 Enquire Construction Layout", wa, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# PAGE: FINANCE CALCULATORS
# ─────────────────────────────────────────────────────────────
def render_finance():
    st.markdown("### 💰 SmartEstate AI Finance Calculators")
    f_tab1, f_tab2, f_tab3 = st.tabs(["Home Loan EMI", "Eligibility Calculator", "Stamp Duty Calculator"])
    
    with f_tab1:
        st.markdown("#### 📊 Amortization EMI Planner")
        pr_amt = st.number_input("Purchase Price (₹)", value=5000000, step=100000)
        down_pmt = st.slider("Down Payment %", 10, 50, 20)
        loan_r = st.slider("Annual Interest Rate (%)", 6.0, 15.0, 8.5, 0.1, key="loan_r_fin")
        ten_y = st.slider("Tenure in Years", 5, 30, 20, key="loan_t_fin")
        
        p_val = pr_amt * (1 - down_pmt/100)
        emi_dat = calculate_emi(p_val, loan_r, ten_y)
        
        st.markdown(f"""
        <div class="info-box">
            <h3>Monthly Payable EMI: <span style="color:#d4af37">{format_price(emi_dat['emi'])}</span></h3>
            <p>Principal Loan: {format_price(emi_dat['principal'])} | Down Payment amount paid: {format_price(pr_amt * down_pmt/100)}</p>
            <p>Total Interest to pay: <span style="color:#ff5050">{format_price(emi_dat['total_interest'])}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
    with f_tab2:
        st.markdown("#### 🏦 Home Loan Eligibility Check")
        inc = st.number_input("Net Monthly Salaried Income (₹)", value=80000, step=5000)
        emi_e = st.number_input("Existing Monthly EMI Deductions (₹)", value=0)
        el_r = st.slider("Interest Rate Expected (%)", 6.0, 15.0, 8.5)
        el_t = st.slider("Loan Tenure Expected (Years)", 5, 30, 20)
        
        res = loan_eligibility(inc, emi_e, el_r, el_t)
        st.markdown(f"""
        <div class="info-box" style="border-color:#00c864">
            <h4>Maximum Loan Eligibility: <span style="color:#00c864">{format_price(res['eligible_amount'])}</span></h4>
            <p>Max monthly EMI cap: {format_price(res['max_emi'])}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with f_tab3:
        st.markdown("#### 🧾 Stamp Duty & Registration Charges")
        st_state = st.selectbox("Select Metro State", ["Uttar Pradesh", "Maharashtra", "Delhi", "Karnataka", "Haryana"])
        pr_val = st.number_input("Property Valuation (₹)", value=6000000, step=100000)
        is_w = st.checkbox("Buying under Female Owner name?")
        
        s_res = stamp_duty(st_state, pr_val, is_w)
        st.markdown(f"""
        <div class="info-box">
            <p>Stamp Duty Rate: **{s_res['stamp_duty_rate']}%**</p>
            <p>Stamp Duty Amount: **{format_price(s_res['stamp_duty_amount'])}**</p>
            <p>Registration Charges: **{format_price(s_res['registration_fee'])}**</p>
            <hr>
            <h4>Total Surcharges: <span style="color:#d4af37">{format_price(s_res['total_cost'])}</span></h4>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PAGE: WISHLIST
# ─────────────────────────────────────────────────────────────
def render_wishlist():
    st.markdown("### ❤️ My Saved Properties")
    if not is_logged_in():
        st.warning("🔐 Please login from the sidebar first.")
        st.stop()
        
    user = st.session_state["user"]
    wish_ids = user.get("wishlist", [])
    
    if not wish_ids:
        st.info("Your wishlist is empty. Browse properties and click wishlist button.")
    else:
        for idx, w_id in enumerate(wish_ids):
            pr = get_property_by_id(w_id)
            if pr:
                st.markdown(property_card_html(pr), unsafe_allow_html=True)
                col_x, col_y = st.columns(2)
                with col_x:
                    if st.button("👁 View Listing Details", key=f"wish_v_{pr['id']}", use_container_width=True):
                        st.session_state["view_prop_id"] = pr["id"]
                        st.session_state["page"] = "Property Detail"
                        st.rerun()
                with col_y:
                    if st.button("🗑️ Remove Wishlist", key=f"wish_rem_{pr['id']}", use_container_width=True):
                        users = _load_data(USERS_FILE)
                        for u_data in users:
                            if u_data["id"] == user["id"]:
                                u_data.setdefault("wishlist", []).remove(pr["id"])
                        _save_data(USERS_FILE, users)
                        st.session_state["user"] = next(usr for usr in users if usr["id"] == user["id"])
                        st.rerun()

# ─────────────────────────────────────────────────────────────
# PAGE: ADMIN PANEL
# ─────────────────────────────────────────────────────────────
def render_admin():
    st.markdown("### 🛡️ SmartEstate Admin Dashboard")
    if not is_logged_in() or st.session_state["user"]["role"] != "admin":
        st.error("🚫 Access Denied. Admin login required.")
        st.stop()
        
    all_p = get_all_properties(approved_only=False)
    pending_p = [p for p in all_p if not p.get("approved")]
    
    adm_t1, adm_t2 = st.tabs(["Listings Queue", "User Management"])
    with adm_t1:
        st.markdown(f"#### Pending Verification Queue ({len(pending_p)})")
        if not pending_p:
            st.success("All listings approved!")
        else:
            for p in pending_p:
                st.markdown(f"""
                <div class="info-box">
                    <h5>🏠 {p['title']}</h5>
                    <p>Price: {format_price(p['price'])} | Locality: {p['area']}, {p['city']}</p>
                    <p>Listed by: {p['owner_name']} ({p['owner_phone']})</p>
                </div>
                """, unsafe_allow_html=True)
                col_ok, col_no = st.columns(2)
                with col_ok:
                    if st.button("✅ Approve Property", key=f"appr_{p['id']}", use_container_width=True):
                        update_property(p["id"], {"approved": True})
                        st.success("Property listing approved live!")
                        st.rerun()
                with col_no:
                    if st.button("❌ Reject / Delete", key=f"rej_{p['id']}", use_container_width=True):
                        delete_property(p["id"])
                        st.warning("Listing rejected.")
                        st.rerun()
                        
    with adm_t2:
        st.markdown("#### Platform Users Registry")
        usrs = _load_data(USERS_FILE)
        df_users = pd.DataFrame(usrs)[["id", "name", "email", "phone", "role", "kyc_verified"]]
        st.dataframe(df_users, use_container_width=True)
        
        u_sel = st.selectbox("Select User to Verify KYC", [u["id"] for u in usrs if not u.get("kyc_verified")])
        if u_sel:
            if st.button("Approve KYC Status"):
                for u in usrs:
                    if u["id"] == u_sel:
                        u["kyc_verified"] = True
                _save_data(USERS_FILE, usrs)
                st.success(f"KYC status updated to verified for {u_sel}")
                st.rerun()

# ─────────────────────────────────────────────────────────────
# Router execution
# ─────────────────────────────────────────────────────────────
if st.session_state["page"] == "Home":
    render_home()
elif st.session_state["page"] == "Search Properties":
    render_search()
elif st.session_state["page"] == "Property Detail":
    render_detail()
elif st.session_state["page"] == "AI Advisor & Search":
    render_ai_consultant()
elif st.session_state["page"] == "Locality Intelligence":
    render_locality()
elif st.session_state["page"] == "Post Property / Requirement":
    render_post_property()
elif st.session_state["page"] == "Dashboard & CRM":
    render_dashboard()
elif st.session_state["page"] == "Builders & Projects":
    render_projects()
elif st.session_state["page"] == "Finance Calculators":
    render_finance()
elif st.session_state["page"] == "My Wishlist":
    render_wishlist()
elif st.session_state["page"] == "Admin Panel":
    render_admin()
