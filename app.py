"""
SmartEstate AI — Complete Single-File Merged Application
India's #1 AI-Powered Real Estate Portal (Self-Contained)
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import re
import hashlib
from datetime import datetime
from PIL import Image

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
                "joined": "2024-01-01"
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
                "joined": "2024-02-10"
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
                "lat": 28.6139, "lng": 77.3689, "description": "Spacious 3BHK apartment with premium interiors, modular kitchen, and panoramic city view. Located in a prime gated society near metro station.",
                "amenities": ["gym", "swimming_pool", "parking", "24x7_security", "elevator", "power_backup", "clubhouse", "garden"],
                "images": [], "owner_name": "Rajesh Sharma", "owner_phone": "9876543210",
                "owner_whatsapp": "9876543210", "owner_email": "rajesh@example.com",
                "posted_by": "user_001", "posted_date": "2024-01-15", "views": 342, "leads": 18,
                "possession": "ready", "age_years": 3, "facing": "East", "approved": True
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
                "possession": "ready", "age_years": 5, "facing": "North", "approved": True
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
                "possession": "immediate", "age_years": 1, "facing": "East", "approved": True
            },
            {
                "id": "prop_004", "title": "Cozy 1BHK Studio Apartment in Bandra, Mumbai", "type": "apartment",
                "listing_type": "rent", "city": "Mumbai", "area": "Bandra West", "state": "Maharashtra",
                "pincode": "400050", "price": 45000, "price_per_sqft": 90, "size_sqft": 500,
                "bhk": 1, "bedrooms": 1, "bathrooms": 1, "parking": 0, "floor": 6, "total_floors": 12,
                "furnishing": "fully-furnished", "status": "available", "verified": False, "premium": False,
                "lat": 19.0607, "lng": 72.8362, "description": "Sea-facing cozy 1BHK studio apartment in Bandra. Fully equipped kitchen, prime location, walking distance from Carter Road promenade.",
                "amenities": ["security", "elevator", "power_backup", "wifi", "ac"],
                "images": [], "owner_name": "Pooja Mehta", "owner_phone": "9812345678",
                "owner_whatsapp": "9812345678", "owner_email": "pooja@example.com",
                "posted_by": "user_002", "posted_date": "2024-03-10", "views": 210, "leads": 12,
                "possession": "ready", "age_years": 8, "facing": "West", "approved": True
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
            },
            {
                "id": "proj_002",
                "name": "DLF Cyber Residences",
                "builder": "DLF Limited",
                "city": "Gurgaon",
                "area": "Sector 54",
                "state": "Haryana",
                "status": "newly_launched",
                "type": "residential",
                "price_range": "₹1.5Cr - ₹3.5Cr",
                "bhk_options": ["2 BHK", "3 BHK", "4 BHK"],
                "total_units": 600,
                "available_units": 240,
                "possession_date": "June 2028",
                "rera_no": "HRERA2024-912",
                "rating": 4,
                "progress_percent": 15,
                "description": "Modern smart homes located next to Cyber City. High rental demand, ideal for IT professionals.",
                "highlights": ["Smart Home Tech", "Near Cyber Hub", "Clubhouse 50k sqft"],
                "lat": 28.4312, "lng": 77.1084
            }
        ]
        with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_projects, f, indent=2)

    # 4. Mock Enquiries
    if not os.path.exists(ENQ_FILE) or os.path.getsize(ENQ_FILE) < 10:
        with open(ENQ_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stApp"] {
    background: linear-gradient(135deg, #0a0a16 0%, #0d1428 50%, #0a0a16 100%);
    color: #e8e8f0; font-family: 'Inter', sans-serif; min-height: 100vh;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { background: #0d1128 !important; border-right: 1px solid rgba(212,175,55,0.2); }
h1 { font-family: 'Playfair Display', serif !important; color: #fff !important; }
h2, h3 { color: #d4af37 !important; font-weight: 700; }

.stButton > button {
    background: linear-gradient(135deg, #d4af37, #f0d060) !important;
    color: #0a0a16 !important; border: none !important;
    border-radius: 8px !important; font-weight: 700 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(212,175,55,0.3) !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; }

.prop-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(212,175,55,0.15);
    border-radius: 16px; padding: 1.2rem; margin-bottom: 1rem;
    transition: all 0.3s ease;
}
.prop-card:hover {
    border-color: rgba(212,175,55,0.5);
    background: rgba(255,255,255,0.07);
    transform: translateY(-3px);
}
.price-badge {
    background: linear-gradient(135deg, #d4af37, #f0d060);
    color: #0a0a16; font-size: 18px; font-weight: 800;
    padding: 6px 14px; border-radius: 8px; display: inline-block;
}
.badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 600; margin-right: 4px;
}
.badge-verified { background: rgba(0,200,100,0.2); color: #00c864; border: 1px solid rgba(0,200,100,0.3); }
.badge-rent { background: rgba(100,150,255,0.2); color: #6496ff; border: 1px solid rgba(100,150,255,0.3); }
.badge-buy { background: rgba(255,150,0,0.2); color: #ff9600; border: 1px solid rgba(255,150,0,0.3); }

.hero-section {
    background: linear-gradient(135deg, rgba(212,175,55,0.1) 0%, transparent 60%);
    border: 1px solid rgba(212,175,55,0.2); border-radius: 24px;
    padding: 3rem 2rem; text-align: center; margin-bottom: 2rem;
}
.stat-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(212,175,55,0.2);
    border-radius: 16px; padding: 1.5rem; text-align: center; transition: all 0.3s;
}
.stat-card:hover { border-color: #d4af37; background: rgba(212,175,55,0.08); }
.stat-number { font-size: 2.2rem; font-weight: 800; color: #d4af37; }
.stat-label { font-size: 13px; color: #aaa; margin-top: 4px; }
.info-box {
    background: rgba(212,175,55,0.08); border: 1px solid rgba(212,175,55,0.25);
    border-radius: 12px; padding: 1rem 1.2rem; margin: 0.8rem 0;
}
.tag {
    display: inline-block; background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15); border-radius: 20px;
    padding: 3px 10px; font-size: 12px; color: #ccc; margin: 2px;
}
.ai-response {
    background: rgba(212,175,55,0.05); border: 1px solid rgba(212,175,55,0.2);
    border-left: 4px solid #d4af37; border-radius: 12px; padding: 1.5rem;
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
    <div style="font-size:12px;color:#888">India's #1 AI-Powered Real Estate Platform</div>
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

def property_card_html(p: dict) -> str:
    price_str = format_price(p.get("price", 0), p.get("listing_type", "buy"))
    verified = "✅ Verified" if p.get("verified") else ""
    premium = "💎 Premium" if p.get("premium") else ""
    lt = p.get("listing_type", "buy").upper()
    bhk = f"{p.get('bhk','')}BHK · " if p.get("bhk") else ""
    sqft = f"{p.get('size_sqft','')} sqft" if p.get("size_sqft") else ""

    return f"""
<div class="prop-card fade-in">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
        <span style="font-size:15px;font-weight:700;color:#fff;flex:1;margin-right:8px">{p.get('title','')[:50]}</span>
        <span class="price-badge">{price_str}</span>
    </div>
    <div style="font-size:12px;color:#aaa;margin-bottom:10px">
        📍 {p.get('area','')}, {p.get('city','')} &nbsp;·&nbsp;
        {bhk}{sqft}
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">
        <span class="badge badge-{'rent' if lt=='RENT' else 'buy'}">{lt}</span>
        {f'<span class="badge badge-verified">{verified}</span>' if verified else ''}
        <span class="badge" style="background:rgba(255,255,255,0.05);color:#ccc">{p.get('furnishing','').replace("-"," ").title()}</span>
        {f'<span class="badge" style="background:rgba(212,175,55,0.2);color:#d4af37">{premium}</span>' if premium else ''}
    </div>
    <div style="font-size:13px;color:#ccc;line-height:1.5">{str(p.get('description',''))[:120]}...</div>
</div>"""

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
# Database / Data Helpers
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
# AI Calculations & Query Parsing
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
    variance = 1 + ((area_hash % 25) - 12) / 100  # ±12% variance

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
    budget = params.get("budget", 5000000)
    bhk = params.get("bhk", 2)

    if gemini_key and GEMINI_AVAILABLE:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prop_summary = "\n".join([f"- {p['title']} | ₹{p['price']:,} | {p['area']}, {p['city']}" for p in properties[:5]])
            prompt = f"""You are SmartEstate AI - India's best real estate consultant.
User Query: "{query}"
Available Properties: {prop_summary}
Provide consultation with: Areas in {city}, Top matching properties, 5-Yr Growth Rate, EMI Estimate, Loan Advice, Investment Score out of 10. Format nicely using markdown."""
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            pass

    # Fallback Algorithmic consultation response
    city_key = city.lower()
    growth = CITY_GROWTH.get(city_key, 8.0)
    matching = [p for p in properties if city_key in p.get("city", "").lower()][:3]
    props_text = "\n".join([f"  • **{p['title']}** in {p['area']} | 💰 {format_price(p['price'])}" for p in matching]) if matching else "No exact matches. Try another city!"

    return f"""## 🏙️ Best Areas in {city}
- Sector 62 / Sector 137 / Sector 150 for high connectivity & rental demand.
- Emerging Township Zones for maximum future appreciation.

## 🏠 Top Matching Properties
{props_text}

## 📈 Future Price Growth (5 Year Prediction)
- Annual Capital Appreciation: **{growth}% p.a.**
- Expected value of your ₹{budget:,} budget: **₹{round(budget * ((1 + growth/100)**5)):,}** in 5 years.

## 💰 EMI & Loan Advice
- Estimated Monthly EMI: **{format_price(calculate_emi(budget * 0.8, 8.5, 20)['emi'])}** (Based on 80% loan at 8.5% interest for 20 years).
- Recommended Banks: **SBI (8.4%)** for best rates, **HDFC (8.5%)** for fast processing.

## 📊 Investment Score: 8.5/10 — Excellent Choice
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

# Set config
st.set_page_config(
    page_title="SmartEstate AI — India's #1 Real Estate Portal",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        <div style="font-size:11px;color:#666;margin-top:2px">India's #1 AI Real Estate Portal</div>
    </div>
    """, unsafe_allow_html=True)

    # Simple Navigation Links
    pages_list = [
        "🏡 Home", "🔍 Search Properties", "🤖 AI Advisor", "📤 Post Property",
        "📊 Owner Dashboard", "🏗️ Builders Projects", "💰 Finance Calculators",
        "❤️ My Wishlist", "🛡️ Admin Panel"
    ]
    
    current_idx = 0
    for idx, p_name in enumerate(pages_list):
        if st.session_state["page"] in p_name:
            current_idx = idx

    selected_nav = st.radio("Navigation Menu", pages_list, index=current_idx)
    st.session_state["page"] = selected_nav.split(" ", 1)[1]

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
    <div class="hero-section fade-in">
        <div style="font-size:13px;color:#d4af37;font-weight:600;letter-spacing:2px;margin-bottom:12px">
            🤖 AI-POWERED REAL ESTATE PORTAL
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
    st.markdown('<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(212,175,55,0.2);border-radius:16px;padding:1.5rem;margin-bottom:2rem">', unsafe_allow_html=True)
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
    cols_proj = st.columns(len(projs[:2]))
    for idx, pr in enumerate(projs[:2]):
        with cols_proj[idx]:
            st.markdown(f"""
            <div class="prop-card">
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
                st.session_state["page"] = "Builders Projects"
                st.rerun()

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
                                _save_data(USERS_FILE, users)
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
            <span class="badge badge-verified">✅ Verified Listings</span>
            <span class="badge" style="background:#d4af37;color:#0a0a16;font-weight:700">Price: {format_price(p['price'], p.get('listing_type','buy'))}</span>
        </div>
        <p>{p['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    dt1, dt2, dt3, dt4 = st.tabs(["📊 AI Price Valuation", "🗺️ Location Map", "💰 Home Loan EMI", "📩 Contact Owner"])
    
    with dt1:
        st.markdown("#### 🤖 SmartEstate AI Valuation Engine")
        est = estimate_price(p['city'], p['area'], p['size_sqft'], p.get('bhk', 2), p.get('type','apartment'))
        inv = investment_score(p['city'], p['area'], p.get('type','apartment'), p['price'])
        
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
                <div class="stat-label">Investment Rating</div>
                <div class="stat-number" style="color:#00c864">{inv['score']}/10</div>
                <div style="font-size:12px;color:#aaa">{inv['verdict']}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Appreciation Rate</div>
                <div class="stat-number">+{inv['appreciation_pct']}%</div>
                <div style="font-size:12px;color:#aaa">Expected yield p.a.</div>
            </div>
            """, unsafe_allow_html=True)

        if PLOTLY_OK:
            fut = future_price(p['price'], p['city'])
            years = list(fut["predictions"].keys())
            vals = [p['price']] + [fut["predictions"][y] for y in years]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[0]+years, y=vals, mode="lines+markers", line=dict(color="#d4af37", width=3)))
            fig.update_layout(title="5-Year Appreciation Forecast", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#fff")
            st.plotly_chart(fig, use_container_width=True)
            
    with dt2:
        st.markdown("#### Google Satellite / Maps Coordinates")
        if FOLIUM_OK and p.get("lat"):
            m = create_single_property_map(p['lat'], p['lng'], p['title'])
            st_folium(m, width="100%", height=400)
        else:
            st.warning("Maps coordinates not configured properly.")
            
    with dt3:
        st.markdown("#### 💰 Home Loan EMI Calculator")
        loan_amount = st.slider("Loan Principal (₹)", min_value=100000, max_value=int(p['price']), value=int(p['price']*0.8))
        loan_rate = st.slider("Interest Rate (% p.a.)", min_value=6.0, max_value=15.0, value=8.5, step=0.1)
        loan_tenure = st.slider("Tenure (Years)", min_value=5, max_value=30, value=20)
        
        emi_out = calculate_emi(loan_amount, loan_rate, loan_tenure)
        
        st.markdown(f"""
        <div class="info-box">
            <h4>Estimated Monthly EMI: <span style="color:#d4af37">{format_price(emi_out['emi'])}</span></h4>
            <p>Total Principal: {format_price(emi_out['principal'])} | Total Interest Payable: <span style="color:#ff5050">{format_price(emi_out['total_interest'])}</span></p>
            <p>Total Amount Payable: <span style="color:#00c864">{format_price(emi_out['total_payment'])}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
    with dt4:
        st.markdown("#### 📩 Send Enquiry directly to Owner")
        if is_logged_in():
            with st.form("enq_form"):
                msg = st.text_area("Your message", value="Hi, I am interested in this listing. Please call me.")
                if st.form_submit_button("Send Enquiry"):
                    save_enquiry(p['id'], st.session_state['user']['id'], "Interested in buying/renting", msg)
                    st.success("Enquiry submitted successfully!")
        else:
            st.info("Please login to send enquiries directly.")

# ─────────────────────────────────────────────────────────────
# PAGE: AI ADVISOR / CONSULTANT
# ─────────────────────────────────────────────────────────────
def render_ai_consultant():
    st.markdown("### 🤖 SmartEstate AI Advisor (NLP Search)")
    st.markdown("<p style='color:#aaa'>Ask questions in plain Hindi or English. E.g., 'Delhi me 3BHK flat buy karna hai 70 lakh budget me'</p>", unsafe_allow_html=True)

    with st.expander("⚙️ Enable Advanced Gemini API responses"):
        key = st.text_input("Enter Gemini API Key", type="password")
        if key:
            st.session_state["gemini_key"] = key
            st.success("Gemini API key loaded!")

    query = st.text_area("What are you looking for today?", placeholder="Type your query...")
    if st.button("🤖 Generate Recommendations", type="primary"):
        if query.strip():
            with st.spinner("AI is analyzing local micro-markets..."):
                all_p = get_all_properties()
                res = ai_consult(query, all_p, gemini_key=st.session_state.get("gemini_key"))
                st.markdown(f"<div class='ai-response'>{res}</div>", unsafe_allow_html=True)
        else:
            st.warning("Please type your search request first.")

# ─────────────────────────────────────────────────────────────
# PAGE: POST PROPERTY
# ─────────────────────────────────────────────────────────────
def render_post_property():
    st.markdown("### 📤 Upload Your Property")
    if not is_logged_in():
        st.warning("🔐 Please login from the sidebar first to post properties.")
        st.stop()
        
    user = st.session_state["user"]
    
    with st.form("post_prop_form"):
        title = st.text_input("Title *", placeholder="e.g. Elegant 3BHK in Sector 137, Noida")
        col_a, col_b = st.columns(2)
        with col_a:
            p_type = st.selectbox("Type", ["apartment", "villa", "plot", "office", "shop"])
            city = st.text_input("City *", placeholder="e.g. Noida")
            state = st.text_input("State", placeholder="e.g. Uttar Pradesh")
        with col_b:
            listing = st.selectbox("Listed for", ["buy", "rent"])
            area = st.text_input("Area *", placeholder="e.g. Sector 137")
            price = st.number_input("Price (₹) *", min_value=1000)
            
        sqft = st.number_input("Sqft Size *", min_value=100)
        bhk = st.selectbox("BHK", [1, 2, 3, 4, 5])
        desc = st.text_area("Description")
        
        st.markdown("**Choose Listing Plan**")
        plan = st.radio("Upload Plan", ["Free (Standard)", "Featured Plan (₹499/mo) - 💎 Premium badge"])
        
        if st.form_submit_button("🚀 Post Property Listing"):
            if not title or not city or not area or price <= 0:
                st.error("Please fill all mandatory fields.")
            else:
                loc = geocode(f"{area}, {city}, {state}, India")
                new_p = {
                    "id": f"prop_{int(datetime.now().timestamp())}",
                    "title": title, "type": p_type, "listing_type": listing,
                    "city": city, "area": area, "state": state,
                    "pincode": "", "price": price, "price_per_sqft": round(price/sqft), "size_sqft": sqft,
                    "bhk": bhk, "bedrooms": bhk, "bathrooms": bhk - 1 if bhk > 1 else 1, "parking": 1,
                    "floor": 1, "total_floors": 4, "furnishing": "unfurnished", "status": "available",
                    "verified": False, "premium": "Featured" in plan, "lat": loc["lat"], "lng": loc["lng"],
                    "description": desc, "amenities": ["parking", "security"], "images": [],
                    "owner_name": user["name"], "owner_phone": user["phone"], "owner_whatsapp": user["phone"],
                    "owner_email": user["email"], "posted_by": user["id"],
                    "posted_date": datetime.now().strftime("%Y-%m-%d"), "views": 0, "leads": 0,
                    "possession": "ready", "age_years": 0, "facing": "East", "approved": False
                }
                save_property(new_p)
                st.success("Submitted! Property is pending approval from Admin.")
                st.balloons()

# ─────────────────────────────────────────────────────────────
# PAGE: OWNER DASHBOARD
# ─────────────────────────────────────────────────────────────
def render_dashboard():
    st.markdown("### 📊 Owner / Agent Dashboard")
    if not is_logged_in():
        st.warning("🔐 Please login from the sidebar first.")
        st.stop()
        
    user = st.session_state["user"]
    my_props = get_properties_by_user(user["id"])
    
    st.markdown(f"**Manage listings for {user['name']}**")
    
    t1, t2 = st.tabs(["Properties Listed", "KYC & Details"])
    with t1:
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
                if pr["status"] == "available":
                    if st.button("Mark as Sold / Rented", key=f"sold_{pr['id']}"):
                        update_property(pr["id"], {"status": "sold"})
                        st.success("Status updated!")
                        st.rerun()
                if st.button("Delete Property", key=f"del_{pr['id']}"):
                    delete_property(pr["id"])
                    st.warning("Property deleted.")
                    st.rerun()
    with t2:
        st.markdown("#### KYC Verification Portal")
        if user.get("kyc_verified"):
            st.success("✅ Your profile is verified! Listings display the verified badge.")
        else:
            st.warning("⏳ Upload ID proof to verify your account.")
            st.file_uploader("Upload Aadhaar Card / PAN Card")
            if st.button("Submit KYC Documents"):
                st.success("Documents uploaded! Admin will verify soon.")

# ─────────────────────────────────────────────────────────────
# PAGE: BUILDERS PROJECTS
# ─────────────────────────────────────────────────────────────
def render_projects():
    st.markdown("### 🏗️ Premium Builders Colonies & Projects")
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
elif st.session_state["page"] == "AI Advisor":
    render_ai_consultant()
elif st.session_state["page"] == "Post Property":
    render_post_property()
elif st.session_state["page"] == "Owner Dashboard":
    render_dashboard()
elif st.session_state["page"] == "Builders Projects":
    render_projects()
elif st.session_state["page"] == "Finance Calculators":
    render_finance()
elif st.session_state["page"] == "My Wishlist":
    render_wishlist()
elif st.session_state["page"] == "Admin Panel":
    render_admin()
