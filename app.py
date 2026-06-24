import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime
import json
import random
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="EstateX - Ultra-Luxury Property Analytics", page_icon="⚜️", layout="wide")

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM & STYLING (Glassmorphic Noir & Champagne Gold)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Montserrat:wght@400;600;700;800;900&display=swap');

/* Main App Background Gradient */
.stApp {
    background: radial-gradient(ellipse at top, #181c2e 0%, #050609 85%) !important;
    font-family: 'Inter', sans-serif !important;
    color: #f0f5ff !important;
}

/* Titles and Headers */
h1, h2, h3, h4, h5, h6, .hero-title {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important;
}

/* Glassmorphic Container Cards */
.glass-card {
    background: rgba(17, 20, 28, 0.7);
    border: 1px solid rgba(212, 175, 55, 0.18);
    border-radius: 18px;
    padding: 1.8rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6);
    margin-bottom: 1.5rem;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.glass-card:hover {
    border-color: rgba(212, 175, 55, 0.35);
    box-shadow: 0 20px 45px rgba(212, 175, 55, 0.06);
    transform: translateY(-2px);
}

/* Sub-card Sections */
.sub-section {
    background: rgba(255, 255, 255, 0.02);
    border-left: 3px solid #d4af37;
    border-radius: 4px 10px 10px 4px;
    padding: 1rem;
    margin: 0.8rem 0;
}

/* Luxury Hero Banner Overlay */
.hero-banner {
    background: linear-gradient(135deg, rgba(14, 17, 26, 0.9) 0%, rgba(26, 32, 50, 0.85) 100%);
    border: 1px solid rgba(212, 175, 55, 0.25);
    border-radius: 20px;
    padding: 2.2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-title {
    font-size: 2.8rem !important;
    background: linear-gradient(90deg, #ffffff 30%, #d4af37 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem !important;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    background: rgba(212, 175, 55, 0.12);
    border: 1px solid rgba(212, 175, 55, 0.4);
    border-radius: 50px;
    padding: 5px 16px;
    font-size: 0.78rem;
    color: #d4af37;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 0.9rem;
}

/* Metrics and Values styling */
.glow-val {
    font-size: 2.5rem;
    font-weight: 800;
    color: #d4af37;
    text-shadow: 0 0 15px rgba(212, 175, 55, 0.4);
    font-family: 'Montserrat', sans-serif;
}
.glow-val-cyan {
    font-size: 2.2rem;
    font-weight: 800;
    color: #00f5d4;
    text-shadow: 0 0 15px rgba(0, 245, 212, 0.4);
    font-family: 'Montserrat', sans-serif;
}

/* Custom Tab Buttons Styling */
.stButton > button {
    background-color: rgba(20, 24, 38, 0.6) !important;
    color: #cbd5e1 !important;
    border: 1px solid rgba(212, 175, 55, 0.2) !important;
    border-radius: 30px !important;
    padding: 0.5rem 1.2rem !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    background: rgba(212, 175, 55, 0.15) !important;
    border-color: #d4af37 !important;
    color: #ffffff !important;
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: scale(0.98);
}

/* Table styling */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
}
th {
    background: rgba(212, 175, 55, 0.1) !important;
    color: #d4af37 !important;
    border-bottom: 1px solid rgba(212, 175, 55, 0.3) !important;
    padding: 10px !important;
    text-align: left !important;
}
td {
    padding: 10px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ML MODEL & LOCATION CONFIG
# ─────────────────────────────────────────────────────────────────────────────
LOCATIONS = {
    "South Mumbai (Malabar Hill / Cuffe Parade)": {"mult": 3.5, "city": "Mumbai", "base_sqft": 45000},
    "Gurugram Golf Course Road (DLF Phase 5)": {"mult": 2.4, "city": "Gurugram", "base_sqft": 28000},
    "South Delhi (Jor Bagh / Vasant Vihar)": {"mult": 2.9, "city": "Delhi", "base_sqft": 36000},
    "Bangalore Central (Indiranagar / Koramangala)": {"mult": 1.9, "city": "Bangalore", "base_sqft": 18000},
    "Pune Core (Koregaon Park / Kalyani Nagar)": {"mult": 1.6, "city": "Pune", "base_sqft": 14000},
    "Hyderabad Premium (Jubilee Hills)": {"mult": 2.1, "city": "Hyderabad", "base_sqft": 22000},
    "Standard Suburban District": {"mult": 1.0, "city": "Metropolitan", "base_sqft": 8000}
}

PROP_TYPES = {
    "Ultra-Luxury Glass Penthouse": {"mult": 1.45, "icon": "🏙️"},
    "Modern Architectural Glass Villa": {"mult": 1.60, "icon": "🏡"},
    "Contemporary Sky Mansion": {"mult": 1.35, "icon": "🏰"},
    "Bespoke Waterfront Estate": {"mult": 1.75, "icon": "🌊"},
    "Premium Residential Flat": {"mult": 1.00, "icon": "🏢"}
}

@st.cache_resource
def train_linear_model():
    # Base dataset mapping general properties
    base_data = {
        "area": [1000, 1200, 1500, 1800, 2000, 2200, 2500],
        "bedrooms": [2, 3, 3, 4, 4, 4, 5],
        "bathrooms": [1, 2, 2, 3, 3, 4, 4],
        "price": [5000000, 6500000, 7200000, 9000000, 10000000, 11500000, 13500000]
    }
    df_base = pd.DataFrame(base_data)
    
    # Generate larger synthetic market dataset
    np.random.seed(101)
    n_samples = 400
    area = np.random.uniform(500, 4500, n_samples)
    bedrooms = np.round(area / 700 + np.random.uniform(0.4, 1.6, n_samples))
    bedrooms = np.clip(bedrooms, 1, 6).astype(int)
    bathrooms = np.round(bedrooms * 0.8 + np.random.uniform(-0.4, 0.6, n_samples))
    bathrooms = np.clip(bathrooms, 1, 5).astype(int)
    
    # Base formula + noise
    noise = np.random.normal(0, 150000, n_samples)
    price = (area * 3500) + (bedrooms * 800000) + (bathrooms * 400000) + noise
    price = np.clip(price, 1200000, 25000000)
    
    df_large = pd.DataFrame({
        "area": area,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "price": price
    })
    
    df_all = pd.concat([df_base, df_large], ignore_index=True)
    
    X = df_all[["area", "bedrooms", "bathrooms"]]
    y = df_all["price"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    r2 = r2_score(y_test, model.predict(X_test))
    mae = mean_absolute_error(y_test, model.predict(X_test))
    
    return model, df_all, r2, mae

model, df_market, model_r2, model_mae = train_linear_model()

# ─────────────────────────────────────────────────────────────────────────────
# HIGH-FIDELITY VECTOR BLUEPRINT GENERATOR (SVG)
# ─────────────────────────────────────────────────────────────────────────────
def draw_detailed_blueprint(beds, baths, area):
    width = 460
    height = 320
    
    svg = f"""<svg width="100%" height="100%" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#070b13; border-radius:12px; border: 1px dashed rgba(212,175,55,0.3);">
    <defs>
        <!-- Engineering Blueprint Grid Pattern -->
        <pattern id="blueprint-grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(0, 245, 212, 0.05)" stroke-width="1"/>
            <path d="M 100 0 L 0 0 0 100" fill="none" stroke="rgba(0, 245, 212, 0.09)" stroke-width="1.5"/>
        </pattern>
    </defs>
    <!-- Background Grid -->
    <rect width="100%" height="100%" fill="url(#blueprint-grid)" />
    
    <!-- Outer Walls (Thick double strokes) -->
    <rect x="20" y="20" width="{width-40}" height="{height-40}" fill="none" stroke="rgba(0, 245, 212, 0.4)" stroke-width="4" />
    <rect x="23" y="23" width="{width-46}" height="{height-46}" fill="none" stroke="#d4af37" stroke-width="1.5" />
    
    <!-- Title / Metrics -->
    <text x="35" y="45" fill="rgba(0, 245, 212, 0.8)" font-family="monospace" font-size="12" font-weight="bold">ARCHITECTURAL BLUEPRINT v2.5</text>
    <text x="35" y="60" fill="rgba(255,255,255,0.4)" font-family="monospace" font-size="9">AREA: {area} SQ FT | DESIGN SCALE 1:50</text>
    """
    
    # Left Room Block (Bedrooms vertical division)
    left_x = 20
    left_w = 190
    usable_h = height - 40
    bed_h = usable_h / max(1, beds)
    
    for i in range(beds):
        y_pos = 20 + (i * bed_h)
        # Room wall
        svg += f'<rect x="{left_x}" y="{y_pos}" width="{left_w}" height="{bed_h}" fill="none" stroke="rgba(0, 245, 212, 0.3)" stroke-width="2" />'
        svg += f'<text x="{left_x + 15}" y="{y_pos + 20}" fill="#d4af37" font-family="monospace" font-size="10" font-weight="bold">BEDROOM 0{i+1}</text>'
        
        # Room dimensions helper
        room_sqft = int(area * (0.35 / max(1, beds)))
        svg += f'<text x="{left_x + 15}" y="{y_pos + 32}" fill="rgba(255,255,255,0.4)" font-family="monospace" font-size="8">~{room_sqft} SQFT</text>'
        
        # Bed furniture vector (Pillow + Mattress outline)
        bed_x = left_x + left_w - 70
        bed_y = y_pos + (bed_h / 2) - 20
        svg += f"""
        <!-- Bed Base -->
        <rect x="{bed_x}" y="{bed_y}" width="50" height="40" rx="3" fill="rgba(212, 175, 55, 0.05)" stroke="#d4af37" stroke-dasharray="2 1" stroke-width="1" />
        <!-- Pillows -->
        <rect x="{bed_x + 5}" y="{bed_y + 4}" width="14" height="10" rx="1" fill="none" stroke="#d4af37" stroke-width="1" />
        <rect x="{bed_x + 5}" y="{bed_y + 26}" width="14" height="10" rx="1" fill="none" stroke="#d4af37" stroke-width="1" />
        <!-- Duvet fold -->
        <line x1="{bed_x + 25}" y1="{bed_y}" x2="{bed_x + 25}" y2="{bed_y + 40}" stroke="#d4af37" stroke-width="1" />
        <path d="M {bed_x+25} {bed_y} C {bed_x+35} {bed_y+20}, {bed_x+35} {bed_y+20}, {bed_x+25} {bed_y+40}" fill="none" stroke="#d4af37" stroke-dasharray="2 2" stroke-width="1" />
        """
        
    # Right-Top Block: Living & Dining
    living_x = 210
    living_y = 20
    living_w = width - 230
    living_h = 160
    svg += f"""
    <rect x="{living_x}" y="{living_y}" width="{living_w}" height="{living_h}" fill="rgba(0, 245, 212, 0.02)" stroke="rgba(0, 245, 212, 0.3)" stroke-width="2" />
    <text x="{living_x + 15}" y="{living_y + 25}" fill="#d4af37" font-family="monospace" font-size="11" font-weight="bold">LIVING & LOUNGE</text>
    <text x="{living_x + 15}" y="{living_y + 38}" fill="rgba(255,255,255,0.4)" font-family="monospace" font-size="8">~{int(area * 0.4)} SQFT</text>
    
    <!-- Dining Table Vector -->
    <rect x="{living_x + 40}" y="{living_y + 60}" width="50" height="30" rx="2" fill="none" stroke="rgba(0, 245, 212, 0.4)" stroke-width="1.2" />
    <circle cx="{living_x + 30}" cy="{living_y + 75}" r="4" fill="none" stroke="rgba(0, 245, 212, 0.4)" stroke-width="1" />
    <circle cx="{living_x + 100}" cy="{living_y + 75}" r="4" fill="none" stroke="rgba(0, 245, 212, 0.4)" stroke-width="1" />
    <circle cx="{living_x + 65}" cy="{living_y + 50}" r="4" fill="none" stroke="rgba(0, 245, 212, 0.4)" stroke-width="1" />
    <circle cx="{living_x + 65}" cy="{living_y + 100}" r="4" fill="none" stroke="rgba(0, 245, 212, 0.4)" stroke-width="1" />
    
    <!-- Sofa lounge assembly -->
    <path d="M {living_x + 120} {living_y + 60} L {living_x + 120} {living_y + 120} L {living_x + 150} {living_y + 120}" fill="none" stroke="#d4af37" stroke-width="1.5" />
    <rect x="{living_x + 152}" y="{living_y + 70}" width="40" height="40" fill="none" stroke="#d4af37" stroke-dasharray="2 1" stroke-width="0.8" />
    <text x="{living_x + 172}" y="{living_y + 94}" fill="#d4af37" font-family="monospace" font-size="7" text-anchor="middle">OLED</text>
    """
    
    # Right-Bottom: Kitchen
    kitchen_x = 210
    kitchen_y = 180
    kitchen_w = 120
    kitchen_h = height - 200
    svg += f"""
    <rect x="{kitchen_x}" y="{kitchen_y}" width="{kitchen_w}" height="{kitchen_h}" fill="none" stroke="rgba(0, 245, 212, 0.3)" stroke-width="2" />
    <text x="{kitchen_x + 12}" y="{kitchen_y + 20}" fill="#d4af37" font-family="monospace" font-size="9" font-weight="bold">KITCHEN</text>
    
    <!-- Kitchen Counters and Sink -->
    <rect x="{kitchen_x + 2}" y="{kitchen_y + kitchen_h - 22}" width="{kitchen_w - 4}" height="20" fill="rgba(255,255,255,0.03)" stroke="rgba(0, 245, 212, 0.2)" stroke-width="1" />
    <rect x="{kitchen_x + 20}" y="{kitchen_y + kitchen_h - 18}" width="25" height="12" rx="1" fill="none" stroke="rgba(0, 245, 212, 0.4)" stroke-width="1" />
    <circle cx="{kitchen_x + 32}" cy="{kitchen_y + kitchen_h - 12}" r="2" fill="rgba(0, 245, 212, 0.5)" />
    """
    
    # Bathroom Pods (Drawn dynamically according to count)
    bath_container_x = 330
    bath_container_y = 180
    bath_container_w = width - 350
    bath_container_h = height - 200
    svg += f'<rect x="{bath_container_x}" y="{bath_container_y}" width="{bath_container_w}" height="{bath_container_h}" fill="none" stroke="rgba(0, 245, 212, 0.3)" stroke-width="2" />'
    
    single_bath_h = bath_container_h / max(1, baths)
    for j in range(baths):
        by_pos = bath_container_y + (j * single_bath_h)
        svg += f"""
        <rect x="{bath_container_x}" y="{by_pos}" width="{bath_container_w}" height="{single_bath_h}" fill="rgba(0, 245, 212, 0.01)" stroke="rgba(0, 245, 212, 0.2)" stroke-width="1" />
        <text x="{bath_container_x + 10}" y="{by_pos + 15}" fill="#00f5d4" font-family="monospace" font-size="8" font-weight="bold">BATH 0{j+1}</text>
        
        <!-- Bathtub shape -->
        <rect x="{bath_container_x + bath_container_w - 45}" y="{by_pos + (single_bath_h/2) - 8}" width="35" height="16" rx="8" fill="none" stroke="#00f5d4" stroke-width="1" />
        <circle cx="{bath_container_x + bath_container_w - 40}" cy="{by_pos + (single_bath_h/2)}" r="1.5" fill="#00f5d4" />
        """
        
    # Compass Rose Indicator
    compass_cx = width - 45
    compass_cy = 45
    svg += f"""
    <circle cx="{compass_cx}" cy="{compass_cy}" r="14" fill="none" stroke="#d4af37" stroke-width="1" stroke-dasharray="3 2" />
    <circle cx="{compass_cx}" cy="{compass_cy}" r="10" fill="none" stroke="#d4af37" stroke-width="1" />
    <!-- Needle -->
    <polygon points="{compass_cx},{compass_cy-13} {compass_cx+3},{compass_cy} {compass_cx},{compass_cy+13} {compass_cx-3},{compass_cy}" fill="none" stroke="#d4af37" stroke-width="1" />
    <polygon points="{compass_cx},{compass_cy-13} {compass_cx+3},{compass_cy} {compass_cx},{compass_cy}" fill="#d4af37" />
    <text x="{compass_cx}" y="{compass_cy-17}" fill="#d4af37" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle">N</text>
    """
    
    svg += "</svg>"
    return svg

# ─────────────────────────────────────────────────────────────────────────────
# HISTORICAL & SESSION VALUATION RECORDS
# ─────────────────────────────────────────────────────────────────────────────
DATA_FILE = Path("estate_records.json")

def load_records():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_records(records):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(records, f, indent=2)
    except Exception:
        pass

if "valuation_history" not in st.session_state:
    st.session_state.valuation_history = load_records()
    # Add dummy high-end valuation logs if history is empty
    if not st.session_state.valuation_history:
        sectors = list(LOCATIONS.keys())
        p_types = list(PROP_TYPES.keys())
        for _ in range(8):
            area_rand = int(random.uniform(1200, 3800))
            bhk_rand = int(random.choice([3, 4, 5]))
            bath_rand = int(max(2, bhk_rand - random.choice([0, 1])))
            loc_rand = random.choice(sectors)
            type_rand = random.choice(p_types)
            
            # Predict
            pred = model.predict([[area_rand, bhk_rand, bath_rand]])[0]
            pred *= LOCATIONS[loc_rand]["mult"]
            pred *= PROP_TYPES[type_rand]["mult"]
            
            st.session_state.valuation_history.append({
                "timestamp": (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 10), hours=random.randint(1, 24))).strftime("%Y-%m-%d %H:%M"),
                "location": loc_rand,
                "property_type": type_rand,
                "area": area_rand,
                "bedrooms": bhk_rand,
                "bathrooms": bath_rand,
                "valuation": int(pred)
            })
        save_records(st.session_state.valuation_history)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN NAVIGATION SELECTOR
# ─────────────────────────────────────────────────────────────────────────────
if "current_view" not in st.session_state:
    st.session_state.current_view = "🏠 AI Valuation Engine"

# Title Display Banner
col_banner_left, col_banner_right = st.columns([2.5, 1.5])
with col_banner_left:
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-badge">⚜️ EstateX Ultra-Luxury Edition</div>
        <div class="hero-title">EstateX Analytics Suite</div>
        <div style="font-size:1rem; color:#cbd5e1; margin-top:0.4rem;">
            Predict elite property valuations, model investment portfolios, compare configurations, and simulate 3D pricing hyperplanes.
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_banner_right:
    # Display the premium villa image generated
    if Path("luxury_villa_render.png").exists():
        st.image("luxury_villa_render.png", use_container_width=True, caption="Live Gen-AI Architectural Concept")
    else:
        st.markdown("""
        <div style="background:rgba(212,175,55,0.05); height:160px; border-radius:20px; border:1px dashed #d4af37; display:flex; align-items:center; justify-content:center;">
            <span style="color:#d4af37; font-weight:600;">Luxury Concept Render</span>
        </div>
        """, unsafe_allow_html=True)

# Styled Navigation Grid
st.markdown("<br>", unsafe_allow_html=True)
nav_buttons = [
    "🏠 AI Valuation Engine",
    "📐 3D Market Space",
    "⚖️ Option Comparator",
    "💰 Loan & ROI Matrix",
    "📜 Valuation Archives"
]
cols = st.columns(5)
for index, tab_name in enumerate(nav_buttons):
    is_active = (st.session_state.current_view == tab_name)
    btn_text = f"⚜️ {tab_name}" if is_active else tab_name
    if cols[index].button(btn_text, key=f"nav_tab_{index}", use_container_width=True):
        st.session_state.current_view = tab_name
        st.rerun()

st.markdown("<hr style='border-top: 1px solid rgba(212, 175, 55, 0.2); margin-top: 0rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1: AI VALUATION ENGINE
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.current_view == "🏠 AI Valuation Engine":
    st.markdown("<h2 style='color:#d4af37;'>🏠 AI Property Appraiser</h2>", unsafe_allow_html=True)
    
    col_inputs, col_visualizer = st.columns([1.8, 2.2])
    
    with col_inputs:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:#d4af37; margin-top:0;'>🧬 Configuration Parameters</h3>", unsafe_allow_html=True)
        
        selected_loc = st.selectbox("Elite Neighborhood Location", list(LOCATIONS.keys()))
        selected_type = st.selectbox("Architectural Property Type", list(PROP_TYPES.keys()))
        
        area_size = st.slider("Covered Carpet Area (sq ft)", min_value=500, max_value=5000, value=1500, step=50)
        bhk_count = st.number_input("Bedrooms (BHK)", min_value=1, max_value=6, value=3, step=1)
        bath_count = st.number_input("Bathrooms", min_value=1, max_value=5, value=2, step=1)
        
        st.markdown("<br>", unsafe_allow_html=True)
        trigger_valuation = st.button("🔱 Run AI Valuation", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_visualizer:
        st.markdown("#### 📐 Live Technical Blueprint Sketch")
        blueprint_code = draw_detailed_blueprint(bhk_count, bath_count, area_size)
        st.components.v1.html(blueprint_code, height=330)
        st.caption("Live structural mapping depicting double bed frames, lounge seating layout, bathroom fixtures, and blueprint scale lines.")

    # Show prediction results
    if trigger_valuation or "last_val" not in st.session_state:
        # Prediction Math
        raw_price = model.predict([[area_size, bhk_count, bath_count]])[0]
        
        loc_mult = LOCATIONS[selected_loc]["mult"]
        type_mult = PROP_TYPES[selected_type]["mult"]
        
        final_val = int(raw_price * loc_mult * type_mult)
        final_val = max(1800000, final_val)
        
        st.session_state.last_val = {
            "val": final_val, "loc": selected_loc, "type": selected_type,
            "area": area_size, "beds": bhk_count, "baths": bath_count,
            "raw": raw_price
        }
        
        # Save record
        st.session_state.valuation_history.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "location": selected_loc,
            "property_type": selected_type,
            "area": area_size,
            "bedrooms": bhk_count,
            "bathrooms": bath_count,
            "valuation": final_val
        })
        save_records(st.session_state.valuation_history)

    curr_val = st.session_state.last_val
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col_p_left, col_p_right = st.columns([2.2, 1.8])
    with col_p_left:
        st.markdown(f"""
        <div style='text-transform: uppercase; font-size:0.8rem; letter-spacing:1px; color: rgba(255,255,255,0.4);'>Appraised Market Valuation</div>
        <div class="glow-text glow-val">₹{curr_val['val']:,}</div>
        <div class="sub-section">
            <strong>Neighborhood Premium Multiplier ({curr_val['loc'].split(' (')[0]}):</strong> {LOCATIONS[curr_val['loc']]['mult']}x<br>
            <strong>Property Class Accent Factor ({curr_val['type']}):</strong> {PROP_TYPES[curr_val['type']]['mult']}x<br>
            <strong>Base Structural Prediction (ML Model):</strong> ₹{int(curr_val['raw']):,}
        </div>
        """, unsafe_allow_html=True)
        
    with col_p_right:
        # Valuation composition chart
        st.markdown("##### 🧬 Price Contribution Factor Model")
        contributions = {
            "Base Area Cost": int(curr_val['area'] * 3500),
            "BHK Bedroom Multiplier": int(curr_val['beds'] * 800000),
            "Bathrooms Allocation": int(curr_val['baths'] * 400000),
            "Location Premium Surcharge": int(curr_val['val'] - curr_val['raw'] * type_mult),
            "Architectural Surcharge": int((curr_val['raw'] * type_mult) - curr_val['raw'])
        }
        # Clean small anomalies
        contributions = {k: max(0, v) for k, v in contributions.items()}
        
        fig_bar = go.Figure(go.Bar(
            y=list(contributions.keys()), x=list(contributions.values()),
            orientation="h", marker=dict(color=["#2c3047", "#1f485c", "#0f6c82", "#d4af37", "#00f5d4"])
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#cbd5e1", size=10), height=140, margin=dict(t=5, b=5, l=5, r=5),
            xaxis=dict(showticklabels=False, gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 10-Year Compound Forecast
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#d4af37; margin-top:0;'>📈 10-Year Future Wealth Appreciation Curve</h3>", unsafe_allow_html=True)
    years = [f"Year {i}" for i in range(11)]
    vals_conservative = [curr_val['val'] * (1.062 ** i) for i in range(11)]
    vals_aggressive = [curr_val['val'] * (1.095 ** i) for i in range(11)]
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=years, y=vals_aggressive, mode="lines",
        line=dict(color="#00f5d4", width=2.5, dash="dash"),
        name="Market Bull Run Scenario (9.5% CAGR)"
    ))
    fig_line.add_trace(go.Scatter(
        x=years, y=vals_conservative, fill="tonexty", mode="lines+markers",
        line=dict(color="#d4af37", width=3.5),
        fillcolor="rgba(212, 175, 55, 0.06)",
        marker=dict(size=7, color="#070b13", line=dict(color="#d4af37", width=2)),
        name="Conservative Scenario (6.2% CAGR)"
    ))
    
    fig_line.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1"), height=240, margin=dict(t=20, b=10),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)")
    )
    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: 3D MARKET SPACE
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.current_view == "📐 3D Market Space":
    st.markdown("<h2 style='color:#d4af37;'>📐 Interactive 3D Valuation Matrix</h2>", unsafe_allow_html=True)
    st.write("Drag, rotate, and pinch to inspect the ML regression hyperplane. Adjust metrics on the left panel to witness your property position slide live across the pricing grid.")
    
    # Left slider panel and Right 3D display panel
    col_3d_inputs, col_3d_display = st.columns([1.2, 2.8])
    
    if "last_val" in st.session_state:
        init_area = st.session_state.last_val["area"]
        init_beds = st.session_state.last_val["beds"]
        init_baths = st.session_state.last_val["baths"]
        init_loc = st.session_state.last_val["loc"]
        init_type = st.session_state.last_val["type"]
    else:
        init_area, init_beds, init_baths = 1500, 3, 2
        init_loc = list(LOCATIONS.keys())[0]
        init_type = list(PROP_TYPES.keys())[0]
        
    with col_3d_inputs:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color:#d4af37; margin-top:0;'>⚙️ Live Tracker</h4>", unsafe_allow_html=True)
        live_area = st.slider("3D Area Slider", min_value=500, max_value=5000, value=init_area, step=50, key="3d_sl_area")
        live_beds = st.slider("3D BHK Slider", min_value=1, max_value=6, value=init_beds, step=1, key="3d_sl_beds")
        live_baths = st.slider("3D Baths Slider", min_value=1, max_value=5, value=init_baths, step=1, key="3d_sl_baths")
        live_loc = st.selectbox("3D Location Selection", list(LOCATIONS.keys()), key="3d_sl_loc")
        live_type = st.selectbox("3D Design Selection", list(PROP_TYPES.keys()), key="3d_sl_type")
        
        # Recalculate predictions
        raw_pred = model.predict([[live_area, live_beds, live_baths]])[0]
        live_val = int(raw_pred * LOCATIONS[live_loc]["mult"] * PROP_TYPES[live_type]["mult"])
        
        st.markdown(f"""
        <div style="margin-top:1.2rem; text-align:center;">
            <div style="font-size:0.75rem; color:#8a99ad;">VALUATION IN THIS SCENARIO</div>
            <div class="glow-val" style="font-size:1.6rem;">₹{live_val:,}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_3d_display:
        # Generate 3D grid data
        area_grid = np.linspace(500, 5000, 35)
        beds_grid = np.linspace(1, 6, 35)
        A, B = np.meshgrid(area_grid, beds_grid)
        
        # Calculate pricing plane matching selected location/property type multipliers
        flat_grid = np.c_[A.ravel(), B.ravel(), np.full(A.size, live_baths)]
        predicted_prices = model.predict(flat_grid).reshape(A.shape)
        
        # Apply multipliers
        predicted_prices = predicted_prices * LOCATIONS[live_loc]["mult"] * PROP_TYPES[live_type]["mult"]
        
        # Build 3D chart
        fig_3d = go.Figure()
        
        # 1. Add Regression Surface Plane
        fig_3d.add_trace(go.Surface(
            x=area_grid, y=beds_grid, z=predicted_prices,
            colorscale="Viridis", opacity=0.75, name="ML Regression Plane",
            showscale=False, hoverinfo="none"
        ))
        
        # 2. Add Market Samples (Apply multipliers to show representative points in similar locations)
        scaled_market_prices = df_market["price"] * LOCATIONS[live_loc]["mult"] * PROP_TYPES[live_type]["mult"]
        fig_3d.add_trace(go.Scatter3d(
            x=df_market["area"], y=df_market["bedrooms"], z=scaled_market_prices,
            mode="markers", marker=dict(size=3, color="#d4af37", opacity=0.4),
            name="Comparable Market Properties"
        ))
        
        # 3. Add Live Tracking Point representing User Slider inputs
        fig_3d.add_trace(go.Scatter3d(
            x=[live_area], y=[live_beds], z=[live_val],
            mode="markers", marker=dict(size=14, color="#00f5d4", symbol="diamond", line=dict(color="#ffffff", width=2)),
            name="Your Property Coordinate", hovertext=f"Area: {live_area} sqft<br>BHK: {live_beds}<br>Price: ₹{live_val:,}"
        ))
        
        fig_3d.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1", size=11),
            height=500, margin=dict(l=0, r=0, t=10, b=0),
            scene=dict(
                xaxis=dict(title="Area (sq ft)", backgroundcolor="#0c0f17", gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(title="Bedrooms", backgroundcolor="#0c0f17", gridcolor="rgba(255,255,255,0.06)"),
                zaxis=dict(title="Price (₹)", backgroundcolor="#0c0f17", gridcolor="rgba(255,255,255,0.06)")
            ),
            legend=dict(yanchor="top", y=0.9, xanchor="left", x=0.1)
        )
        st.plotly_chart(fig_3d, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3: OPTION COMPARATOR
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_view == "⚖️ Option Comparator":
    st.markdown("<h2 style='color:#d4af37;'>⚖️ Side-by-Side Property Comparator</h2>", unsafe_allow_html=True)
    st.write("Compare two distinct property profiles to analyze size variance, structural premiums, and cost efficiency.")
    
    col_prop_a, col_prop_b = st.columns(2)
    
    with col_prop_a:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:#d4af37; margin-top:0;'>🏠 Property Profile A</h3>", unsafe_allow_html=True)
        loc_a = st.selectbox("Location (A)", list(LOCATIONS.keys()), index=0)
        type_a = st.selectbox("Property Type (A)", list(PROP_TYPES.keys()), index=0)
        area_a = st.number_input("Area: Sq Ft (A)", min_value=500, max_value=5000, value=1200, step=100)
        bhk_a = st.number_input("Bedrooms: BHK (A)", min_value=1, max_value=6, value=2, step=1)
        bath_a = st.number_input("Bathrooms (A)", min_value=1, max_value=5, value=1, step=1)
        
        # Calculate
        price_a = int(model.predict([[area_a, bhk_a, bath_a]])[0] * LOCATIONS[loc_a]["mult"] * PROP_TYPES[type_a]["mult"])
        price_a = max(1800000, price_a)
        sqft_cost_a = int(price_a / area_a)
        
        st.markdown(f"""
        <div class="sub-section">
            <div style="font-size:0.75rem; color:#8a99ad;">VALUATION DECLARED</div>
            <div class="glow-val">₹{price_a:,}</div>
            <div style="font-size:0.85rem; margin-top:0.4rem;">Price per Sq Ft: <strong>₹{sqft_cost_a:,}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_prop_b:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:#00f5d4; margin-top:0;'>🏠 Property Profile B</h3>", unsafe_allow_html=True)
        loc_b = st.selectbox("Location (B)", list(LOCATIONS.keys()), index=1)
        type_b = st.selectbox("Property Type (B)", list(PROP_TYPES.keys()), index=1)
        area_b = st.number_input("Area: Sq Ft (B)", min_value=500, max_value=5000, value=2000, step=100)
        bhk_b = st.number_input("Bedrooms: BHK (B)", min_value=1, max_value=6, value=3, step=1)
        bath_b = st.number_input("Bathrooms (B)", min_value=1, max_value=5, value=3, step=1)
        
        # Calculate
        price_b = int(model.predict([[area_b, bhk_b, bath_b]])[0] * LOCATIONS[loc_b]["mult"] * PROP_TYPES[type_b]["mult"])
        price_b = max(1800000, price_b)
        sqft_cost_b = int(price_b / area_b)
        
        st.markdown(f"""
        <div class="sub-section" style="border-left-color: #00f5d4;">
            <div style="font-size:0.75rem; color:#8a99ad;">VALUATION DECLARED</div>
            <div class="glow-val-cyan">₹{price_b:,}</div>
            <div style="font-size:0.85rem; margin-top:0.4rem;">Price per Sq Ft: <strong>₹{sqft_cost_b:,}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Discrepancy Breakdown Card
    diff_val = price_b - price_a
    pct_val = (diff_val / price_a) * 100
    
    st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin:0;'>📊 Comparison Verdict</h3>", unsafe_allow_html=True)
    if diff_val > 0:
        st.markdown(f"<span style='font-size:1.15rem;'>Property B is priced <strong style='color:#00f5d4;'>₹{diff_val:,} ({pct_val:.1f}%)</strong> higher than Property A.</span>", unsafe_allow_html=True)
    elif diff_val < 0:
        st.markdown(f"<span style='font-size:1.15rem;'>Property B is priced <strong style='color:#d4af37;'>₹{abs(diff_val):,} ({abs(pct_val):.1f}%)</strong> lower than Property A.</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span style='font-size:1.15rem;'>Both property layouts evaluate to identical valuations.</span>", unsafe_allow_html=True)
        
    # Space efficiency / utility comparison metric
    # Score = Sqft per room unit
    score_a = int(area_a / (bhk_a + bath_a * 0.5))
    score_b = int(area_b / (bhk_b + bath_b * 0.5))
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown(f"""
        <div class="sub-section">
            <strong>Room Space Score (A):</strong> {score_a} sqft / unit<br>
            <span style="font-size:0.8rem; color:#8a99ad;">Represents the average carpet space allocated per bedroom and bathroom. Larger values mean more spacious interiors.</span>
        </div>
        """, unsafe_allow_html=True)
    with col_c2:
        st.markdown(f"""
        <div class="sub-section" style="border-left-color: #00f5d4;">
            <strong>Room Space Score (B):</strong> {score_b} sqft / unit<br>
            <span style="font-size:0.8rem; color:#8a99ad;">Represents the average carpet space allocated per bedroom and bathroom. Larger values mean more spacious interiors.</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4: LOAN & ROI MATRIX
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_view == "💰 Loan & ROI Matrix":
    st.markdown("<h2 style='color:#d4af37;'>💰 Investment Analytics & Mortgage Simulator</h2>", unsafe_allow_html=True)
    st.write("Simulate financing structures and analyze capital appreciation vs. rental yield projections.")
    
    # Fetch price from previous valuation if present
    base_val = 7500000
    if "last_val" in st.session_state:
        base_val = st.session_state.last_val["val"]
        
    col_finance_inputs, col_finance_charts = st.columns([1.5, 2.5])
    
    with col_finance_inputs:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color:#d4af37; margin-top:0;'>⚙️ Financing Parameters</h4>", unsafe_allow_html=True)
        
        sim_val = st.number_input("Simulated Property Value (₹)", min_value=1500000, max_value=150000000, value=base_val, step=500000)
        downpayment_pct = st.slider("Down Payment Percentage (%)", min_value=10, max_value=90, value=20, step=5)
        interest_rate = st.slider("Annual Mortgage Interest (%)", min_value=4.0, max_value=18.0, value=8.5, step=0.1)
        loan_years = st.selectbox("Loan Tenure Term (Years)", [5, 10, 15, 20, 25, 30], index=3)
        
        downpayment = sim_val * (downpayment_pct / 100.0)
        loan_amount = sim_val - downpayment
        
        # Monthly rates
        r = (interest_rate / 100.0) / 12
        n = loan_years * 12
        
        # EMI calculation
        emi = loan_amount * (r * (1 + r)**n) / ((1 + r)**n - 1)
        total_payment = emi * n
        total_interest = total_payment - loan_amount
        
        st.markdown(f"""
        <div class="sub-section">
            <div style="font-size:0.75rem; color:#8a99ad;">ESTIMATED MONTHLY INSTALLMENT</div>
            <div class="glow-val" style="font-size:1.8rem;">₹{int(emi):,}</div>
            <div style="font-size:0.8rem; margin-top:0.4rem; line-height:1.4;">
                Down Payment: <strong>₹{int(downpayment):,}</strong><br>
                Principal Loan: <strong>₹{int(loan_amount):,}</strong><br>
                Accumulated Interest: <strong>₹{int(total_interest):,}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_finance_charts:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color:#d4af37; margin-top:0;'>📊 Amortization Schedule & Capital Composition</h4>", unsafe_allow_html=True)
        
        # Generate Amortization data for chart
        years_arr = list(range(1, loan_years + 1))
        remaining_balance = []
        cumulative_principal = []
        cumulative_interest = []
        
        balance = loan_amount
        cum_p = 0.0
        cum_i = 0.0
        
        for y_idx in range(1, loan_years + 1):
            # Calculate interest and principal paid in one year (12 months)
            year_interest = 0.0
            year_principal = 0.0
            for _ in range(12):
                i_pay = balance * r
                p_pay = emi - i_pay
                balance -= p_pay
                year_interest += i_pay
                year_principal += p_pay
                
            cum_p += year_principal
            cum_i += year_interest
            
            remaining_balance.append(max(0.0, balance))
            cumulative_principal.append(cum_p)
            cumulative_interest.append(cum_i)
            
        # Draw Area Chart
        fig_amort = go.Figure()
        fig_amort.add_trace(go.Scatter(
            x=years_arr, y=cumulative_interest, fill='tozeroy', mode='lines',
            line=dict(color='#d4af37', width=2), name="Cumulative Interest Paid"
        ))
        fig_amort.add_trace(go.Scatter(
            x=years_arr, y=cumulative_principal, fill='tonexty', mode='lines',
            line=dict(color='#00f5d4', width=2), name="Cumulative Principal Repaid"
        ))
        fig_amort.add_trace(go.Scatter(
            x=years_arr, y=remaining_balance, mode='lines',
            line=dict(color='#ef4444', width=2, dash='dot'), name="Outstanding Loan Balance"
        ))
        
        fig_amort.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#cbd5e1", size=10), height=240, margin=dict(t=10, b=10),
            yaxis=dict(title="Amount (₹)", gridcolor="rgba(255,255,255,0.05)"),
            xaxis=dict(title="Year", gridcolor="rgba(255,255,255,0.05)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_amort, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Projected Yield Projections (Rent vs Buy modeling)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#d4af37; margin-top:0;'>🏡 Yield Analytics & Capital Projections</h3>", unsafe_allow_html=True)
    
    col_y1, col_y2, col_y3 = st.columns(3)
    
    with col_y1:
        # Rental yield model (assuming average rent at 4.2% of market value)
        rent_yield = 4.2
        annual_rent = sim_val * (rent_yield / 100)
        st.markdown(f"""
        <div class="sub-section">
            <div style="font-size:0.75rem; color:#8a99ad;">ESTIMATED ANNUAL RENT</div>
            <strong style="font-size:1.4rem; color:#d4af37;">₹{int(annual_rent):,}</strong>
            <div style="font-size:0.8rem; margin-top:0.4rem;">Gross Yield Score: <strong>{rent_yield}%</strong></div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_y2:
        # Capital appreciation (based on 7.5% average CAGR over 5 years)
        appreciation_rate = 7.5
        future_val = sim_val * ((1 + appreciation_rate/100) ** 5)
        gain = future_val - sim_val
        st.markdown(f"""
        <div class="sub-section" style="border-left-color: #00f5d4;">
            <div style="font-size:0.75rem; color:#8a99ad;">5-YEAR CAPITAL GAIN</div>
            <strong style="font-size:1.4rem; color:#00f5d4;">+₹{int(gain):,}</strong>
            <div style="font-size:0.8rem; margin-top:0.4rem;">Appreciation projection: <strong>{appreciation_rate}% CAGR</strong></div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_y3:
        # Net wealth building score after 5 years (Rent vs Buy)
        # Net profit = Gain + 5 Years rent - interest paid
        interest_paid_5yr = cumulative_interest[4] if loan_years >= 5 else cumulative_interest[-1]
        rent_saved = annual_rent * 5 * 1.05 # 5% inflation factor
        net_wealth_delta = gain + rent_saved - interest_paid_5yr
        
        st.markdown(f"""
        <div class="sub-section" style="border-left-color: #00f5d4;">
            <div style="font-size:0.75rem; color:#8a99ad;">NET WEALTH GENERATION</div>
            <strong style="font-size:1.4rem; color:#00f5d4;">₹{int(net_wealth_delta):,}</strong>
            <div style="font-size:0.8rem; margin-top:0.4rem;">Equity multiplier: <strong>{(net_wealth_delta/sim_val):.2f}x</strong></div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 5: VALUATION ARCHIVES
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_view == "📜 Valuation Archives":
    st.markdown("<h2 style='color:#d4af37;'>📜 Valuation Audit History</h2>", unsafe_allow_html=True)
    st.write("Browse historical AI appraisals logged during this server instance.")
    
    history_logs = st.session_state.valuation_history
    
    if not history_logs:
        st.info("No property configurations appraised in current session history.")
    else:
        df_logs = pd.DataFrame(history_logs)
        
        # Display clean styled table
        st.dataframe(
            df_logs.sort_values(by="timestamp", ascending=False),
            use_container_width=True,
            column_config={
                "timestamp": st.column_config.TextColumn("Appraisal Timestamp"),
                "location": st.column_config.TextColumn("Neighborhood Location"),
                "property_type": st.column_config.TextColumn("Class Type"),
                "area": st.column_config.NumberColumn("Carpet Area (sqft)", format="%d"),
                "bedrooms": st.column_config.NumberColumn("BHK Bedrooms", format="%d"),
                "bathrooms": st.column_config.NumberColumn("Baths", format="%d"),
                "valuation": st.column_config.NumberColumn("Estimated Appraisal Value (₹)", format="₹%d")
            }
        )
        
        # Stats summary cards
        avg_price = int(df_logs["valuation"].mean())
        tot_appraised = int(df_logs["valuation"].sum())
        total_runs = len(df_logs)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; padding:1.2rem;">
                <div style="font-size:0.75rem; color:#8a99ad;">TOTAL LOG RUNS</div>
                <strong style="font-size:1.6rem; color:#d4af37;">{total_runs} Records</strong>
            </div>
            """, unsafe_allow_html=True)
        with col_s2:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; padding:1.2rem;">
                <div style="font-size:0.75rem; color:#8a99ad;">AVERAGE VALUE APPRAISED</div>
                <strong style="font-size:1.6rem; color:#d4af37;">₹{avg_price:,}</strong>
            </div>
            """, unsafe_allow_html=True)
        with col_s3:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; padding:1.2rem;">
                <div style="font-size:0.75rem; color:#8a99ad;">CUMULATIVE APPRAISED PORTFOLIO</div>
                <strong style="font-size:1.6rem; color:#00f5d4;">₹{tot_appraised:,}</strong>
            </div>
            """, unsafe_allow_html=True)
            
        # Export & Clear controls
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            csv_data = df_logs.to_csv(index=False).encode("utf-8")
            st.download_button("🔱 Export Archives (CSV)", csv_data, "valuation_archives.csv", "text/csv", use_container_width=True)
        with col_c2:
            if st.button("🚫 Clear History Logs", use_container_width=True):
                st.session_state.valuation_history = []
                save_records([])
                st.rerun()

st.markdown("<br><hr style='border-top: 1px solid rgba(212, 175, 55, 0.15);'>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; font-size:0.80rem; color:#8a99ad;'>⚜️ EstateX Premium Real Estate Analytics System | Custom Linear Regression Model | V2.5 Luxury Edition</div>", unsafe_allow_html=True)
