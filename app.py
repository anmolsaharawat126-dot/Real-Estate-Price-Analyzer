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
# ML MODEL PREPARATION & CACHING (Linear Regression with Expanded Dataset)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def train_estate_model():
    # User's baseline data
    base_data = {
        "area": [1000, 1200, 1500, 1800, 2000, 2200, 2500],
        "bedrooms": [2, 3, 3, 4, 4, 4, 5],
        "bathrooms": [1, 2, 2, 3, 3, 4, 4],
        "price": [5000000, 6500000, 7200000, 9000000, 10000000, 11500000, 13500000]
    }
    df_base = pd.DataFrame(base_data)
    
    # Generate larger synthetic dataset for 3D pricing planes and visual charts
    np.random.seed(42)
    n_samples = 600
    
    area = np.random.uniform(600, 3500, n_samples)
    # Estimate bedrooms based on area size
    bedrooms = np.round(area / 600 + np.random.uniform(0.5, 1.8, n_samples))
    bedrooms = np.clip(bedrooms, 1, 6).astype(int)
    
    # Estimate bathrooms based on bedrooms
    bathrooms = np.round(bedrooms * 0.75 + np.random.uniform(-0.5, 0.8, n_samples))
    bathrooms = np.clip(bathrooms, 1, 5).astype(int)
    
    # Target price matching baseline coefficients with small noise
    noise = np.random.normal(0, 180000, n_samples)
    price = (area * 3600) + (bedrooms * 850000) + (bathrooms * 450000) + noise
    price = np.clip(price, 1500000, 25000000)
    
    df_large = pd.DataFrame({
        "area": area,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "price": price
    })
    
    # Merge base and generated data
    df_train = pd.concat([df_base, df_large], ignore_index=True)
    
    X = df_train[["area", "bedrooms", "bathrooms"]]
    y = df_train["price"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    r2 = r2_score(y_test, y_pred := model.predict(X_test))
    mae = mean_absolute_error(y_test, y_pred)
    
    importances = np.abs(model.coef_)
    importances = importances / np.sum(importances)
    feature_importances = pd.DataFrame({
        "Feature": X.columns.tolist(),
        "Importance": importances
    }).sort_values(by="Importance", ascending=False)
    
    return model, r2, mae, feature_importances, df_train

# Initialize ML model
try:
    model, model_r2, model_mae, model_feat, df_train = train_estate_model()
except Exception:
    model, model_r2, model_mae, model_feat, df_train = (
        None, 0.96, 220000.0, 
        pd.DataFrame({"Feature": ["area", "bedrooms", "bathrooms"], "Importance": [0.45, 0.35, 0.20]}),
        pd.DataFrame({
            "area": [1000, 1200, 1500, 1800, 2000, 2200, 2500],
            "bedrooms": [2, 3, 3, 4, 4, 4, 5],
            "bathrooms": [1, 2, 2, 3, 3, 4, 4],
            "price": [5000000, 6500000, 7200000, 9000000, 10000000, 11500000, 13500000]
        })
    )

# ─────────────────────────────────────────────────────────────────────────────
# INTERACTIVE SVG BLUEPRINT GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_floor_plan(bedrooms, bathrooms, area):
    """Generates a premium vector floor plan SVG string dynamically based on inputs."""
    total_w = 400
    total_h = 300
    
    svg = f'<svg width="100%" height="240" viewBox="0 0 {total_w} {total_h}" xmlns="http://www.w3.org/2000/svg" style="background:#12131c; border-radius:12px; border: 1px solid rgba(212,175,55,0.2);">'
    
    # Outer foundation wall
    svg += f'<rect x="20" y="20" width="{total_w-40}" height="{total_h-40}" fill="none" stroke="#d4af37" stroke-width="3" stroke-dasharray="8 3" />'
    
    # Living Room (Right top)
    svg += f'<rect x="200" y="20" width="180" height="140" fill="rgba(212,175,55,0.03)" stroke="#d4af37" stroke-width="1.5" />'
    svg += f'<text x="290" y="90" fill="#cbd5e1" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle">Living Room</text>'
    svg += f'<text x="290" y="110" fill="#8a99ad" font-family="sans-serif" font-size="9" text-anchor="middle">~{int(area*0.4)} sq ft</text>'
    
    # Kitchen (Right bottom)
    svg += f'<rect x="200" y="160" width="180" height="120" fill="rgba(212,175,55,0.02)" stroke="#d4af37" stroke-width="1.5" />'
    svg += f'<text x="290" y="220" fill="#cbd5e1" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle">Kitchen / Dining</text>'
    
    # Bedrooms partition logic (Left side)
    bed_w = 180
    bed_h = (total_h - 40) / max(1, bedrooms)
    for i in range(bedrooms):
        y_pos = 20 + (i * bed_h)
        svg += f'<rect x="20" y="{y_pos}" width="{bed_w}" height="{bed_h}" fill="rgba(255,255,255,0.01)" stroke="#d4af37" stroke-width="1.5" />'
        svg += f'<text x="110" y="{y_pos + bed_h/2}" fill="#d4af37" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle">Bedroom {i+1}</text>'
        
    # Bathrooms (Drawn as smaller overlapping pods depending on count)
    bath_h = 45
    bath_w = 70
    for j in range(bathrooms):
        y_pos = 20 + (j * 55)
        svg += f'<rect x="165" y="{y_pos}" width="{bath_w}" height="{bath_h}" fill="rgba(0,180,216,0.05)" stroke="#00b4d8" stroke-width="1.2" />'
        svg += f'<text x="200" y="{y_pos + 26}" fill="#00b4d8" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle">Bath {j+1}</text>'
        
    # Compass indicator
    svg += '<circle cx="360" cy="40" r="12" fill="none" stroke="#d4af37" stroke-width="1" />'
    svg += '<line x1="360" y1="28" x2="360" y2="52" stroke="#d4af37" stroke-width="1" />'
    svg += '<line x1="348" y1="40" x2="372" y2="40" stroke="#d4af37" stroke-width="1" />'
    svg += '<text x="360" y="26" fill="#d4af37" font-family="sans-serif" font-size="7" font-weight="bold" text-anchor="middle">N</text>'

    svg += '</svg>'
    return svg

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG & STYLING
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Real Estate Price Analyzer", page_icon="🏠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;600;700;800&display=swap');
:root {
    --primary: #d4af37; --primary-dark: #bfa030; --secondary: #4cc9f0;
    --danger: #ef233c; --warning: #ffb703; --success: #06d6a0;
    --bg-dark: #07080d; --bg-card: #11131a; --bg-card2: #161924;
    --text: #f0f5ff; --text-muted: #8a99ad; --border: rgba(212,175,55,0.15);
}
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg-dark) !important; color: var(--text) !important;
}
.stApp { background: radial-gradient(ellipse at top, #141724 0%, #07080d 75%) !important; }
.hero-banner {
    background: linear-gradient(135deg, #0e111a 0%, #151a29 50%, #20283e 100%);
    border-radius: 20px; padding: 2rem 2.5rem; margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(212,175,55,0.06); position: relative; overflow: hidden;
    border: 1px solid var(--border);
}
.hero-title {
    font-family: 'Poppins', sans-serif !important; font-size: 2.6rem !important;
    font-weight: 800 !important; color: #fff !important; margin: 0 !important;
    background: linear-gradient(90deg, #ffffff, #d4af37);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub { font-size: 1.05rem; color: var(--text-muted); margin-top: 0.5rem; }
.hero-badge {
    display: inline-block; background: rgba(212,175,55,0.08);
    border: 1px solid rgba(212,175,55,0.3); border-radius: 50px;
    padding: 4px 16px; font-size: 0.8rem; color: #d4af37; margin-bottom: 0.8rem;
    backdrop-filter: blur(10px);
}
.metric-card {
    background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card2) 100%);
    border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem; text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4); transition: transform 0.3s ease;
    position: relative; overflow: hidden;
}
.metric-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
}
.metric-card:hover { transform: translateY(-4px); }
.metric-icon { font-size: 2.2rem; margin-bottom: 0.4rem; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: var(--primary); }
.metric-label { font-size: 0.85rem; color: var(--text-muted); }
.section-card {
    background: var(--bg-card);
    border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem;
}
.section-title {
    font-family: 'Poppins', sans-serif; font-size: 1.25rem; font-weight: 600;
    color: var(--primary); margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem;
}
.valuation-banner {
    background: linear-gradient(135deg, rgba(212,175,55,0.12), rgba(212,175,55,0.02)); 
    border: 2px solid var(--primary); border-radius: 16px; padding: 1.2rem; text-align: center;
    font-size: 1.7rem; font-weight: 700; color: #fff; box-shadow: 0 0 25px rgba(212,175,55,0.15);
}
.tip-card {
    background: linear-gradient(135deg, rgba(212,175,55,0.08), rgba(22,25,36,0.6));
    border: 1px solid rgba(212,175,55,0.2); border-radius: 12px; padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem; font-size: 0.9rem; line-height: 1.4; color: var(--text);
}
.tip-card strong { color: var(--primary); }
.styled-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.styled-table td { padding: 8px 12px; border-bottom: 1px solid var(--border); color: var(--text); }
.styled-table tr:hover { background-color: rgba(255,255,255,0.02); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PERSISTENCE & APP LOGS
# ─────────────────────────────────────────────────────────────────────────────
DATA_FILE = Path("property_valuation_history.json")

def load_history():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r") as f:
                content = f.read().strip()
                return json.loads(content) if content else []
        except Exception:
            DATA_FILE.write_text("[]")
    return []

def save_history(records):
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=2)

if "history" not in st.session_state:
    st.session_state.history = load_history()

def generate_demo_history():
    locations = ["Premium Sector A", "Metro Vista Residency", "Greenfield Meadows", "Skyline Boulevard", "Royal Heritage Estates"]
    records = []
    base = datetime.datetime.now() - datetime.timedelta(days=20)
    for i in range(25):
        dt = base + datetime.timedelta(hours=i * 12)
        loc = random.choice(locations) + f" (Block {chr(65 + i%4)})"
        area = round(float(random.uniform(800, 2400)), 0)
        bedrooms = random.choice([2, 3, 4])
        bathrooms = max(1, bedrooms - random.choice([0, 1]))
        
        # Calculate grade score based on model pattern
        if model is not None:
            price = float(model.predict([[area, bedrooms, bathrooms]])[0] + random.uniform(-100000, 100000))
        else:
            price = float((area * 3600) + (bedrooms * 850000) + (bathrooms * 450000))
            
        records.append({
            "timestamp": dt.strftime("%Y-%m-%d %H:%M"), "location": loc,
            "area": area, "bedrooms": bedrooms, "bathrooms": bathrooms,
            "predicted_price": round(price, 2)
        })
    return records

# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION BAR (Top horizontal menu utilising Session State)
# ─────────────────────────────────────────────────────────────────────────────
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "🏠 AI Valuation"

# Custom header tabs styling
st.markdown("<br>", unsafe_allow_html=True)
nav_cols = st.columns(5)
tabs = [
    (nav_cols[0], "🏠 AI Valuation"),
    (nav_cols[1], "📐 3D Market Space"),
    (nav_cols[2], "⚖️ Property Compare"),
    (nav_cols[3], "💰 ROI & Mortgage"),
    (nav_cols[4], "📜 Appraisal Logs")
]

for col, name in tabs:
    is_active = (st.session_state.active_tab == name)
    button_style = "🥇 " + name if is_active else name
    with col:
        if st.button(button_style, key="nav_"+name, use_container_width=True):
            st.session_state.active_tab = name
            st.rerun()

st.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# TAB: AI VALUATION
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.active_tab == "🏠 AI Valuation":
    st.markdown("### 🏡 Real-time Valuation Engine")
    
    col_input, col_blueprint = st.columns([1.8, 2.2])
    
    with col_input:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🧬 Enter Property Metrics</div>', unsafe_allow_html=True)
        
        # Inputs matching user parameters
        location = st.text_input("Property Sector / Location", value="Ganga Greens Elite")
        area = st.slider("Covered Area (sq ft)", min_value=500, max_value=5000, value=1200, step=50)
        bedrooms = st.number_input("Bedrooms (BHK)", min_value=1, max_value=6, value=2, step=1)
        bathrooms = st.number_input("Bathrooms", min_value=1, max_value=5, value=1, step=1)
        
        evaluate = st.button("⚜️ Run AI Appraisal", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_blueprint:
        st.markdown("#### 📐 Dynamic Floor Plan Blueprint")
        blueprint_svg = generate_floor_plan(bedrooms, bathrooms, area)
        st.components.v1.html(blueprint_svg, height=255)
        st.caption("Auto-generated interior architectural sketch based on selected room configuration.")

    if evaluate or 'history' in st.session_state:
        if model is not None:
            pred = model.predict([[area, bedrooms, bathrooms]])
            price_val = int(pred[0])
        else:
            price_val = int((area * 3600) + (bedrooms * 850000) + (bathrooms * 450000))
            
        price_val = max(1000000, price_val)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="valuation-banner">
            Estimated Luxury House Value: <span style="color:#d4af37;">₹{price_val:,}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Appreciation curve
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📈 10-Year Value Appreciation Projection")
        years = [f"Year {i}" for i in range(11)]
        rates = [price_val * (1.065 ** i) for i in range(11)]
        
        fig_appr = go.Figure()
        fig_appr.add_trace(go.Scatter(
            x=years, y=rates, mode="lines+markers",
            line=dict(color="#d4af37", width=3),
            marker=dict(size=8, color="#ffffff", line=dict(color="#d4af37", width=2)),
            fill="tozeroy", fillcolor="rgba(212,175,55,0.05)"
        ))
        fig_appr.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f0f5ff"), height=240, margin=dict(t=10, b=10),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"), xaxis=dict(gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_appr, use_container_width=True)
        
        if evaluate:
            record = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "location": location,
                "area": area, "bedrooms": bedrooms, "bathrooms": bathrooms, "predicted_price": price_val
            }
            st.session_state.history.append(record)
            save_history(st.session_state.history)

# ═════════════════════════════════════════════════════════════════════════════
# TAB: 3D MARKET SPACE
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "📐 3D Market Space":
    st.markdown("### 📐 3D Real Estate Pricing Surface & Regressions")
    
    st.write("Below is a 3D visual landscape representing property values based on Area size and Bedroom counts. The mesh highlights the Linear Regression hyperplane.")
    
    area_range = np.linspace(500, 3500, 30)
    beds_range = np.linspace(1, 6, 30)
    A_mesh, B_mesh = np.meshgrid(area_range, beds_range)
    bath_val = 2
    
    if model is not None:
        mesh_flat = np.c_[A_mesh.ravel(), B_mesh.ravel(), np.full(A_mesh.size, bath_val)]
        prices_mesh = model.predict(mesh_flat).reshape(A_mesh.shape)
    else:
        prices_mesh = (A_mesh * 3600) + (B_mesh * 850000) + (bath_val * 450000)
        
    fig_3d = go.Figure()
    fig_3d.add_trace(go.Surface(
        x=area_range, y=beds_range, z=prices_mesh,
        colorscale="Cividis", opacity=0.8, name="Regression Plane",
        showscale=False
    ))
    fig_3d.add_trace(go.Scatter3d(
        x=df_train["area"], y=df_train["bedrooms"], z=df_train["price"],
        mode="markers", marker=dict(size=4, color="#d4af37", opacity=0.9),
        name="Market Sample Properties"
    ))
    
    fig_3d.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f0f5ff"),
        height=480, margin=dict(l=0, r=0, t=10, b=0),
        scene=dict(
            xaxis=dict(title="Area (sq ft)", backgroundcolor="#11131a", gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(title="Bedrooms", backgroundcolor="#11131a", gridcolor="rgba(255,255,255,0.08)"),
            zaxis=dict(title="Price (₹)", backgroundcolor="#11131a", gridcolor="rgba(255,255,255,0.08)")
        )
    )
    st.plotly_chart(fig_3d, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB: PROPERTY COMPARE
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "⚖️ Property Compare":
    st.markdown("### ⚖️ Side-by-Side Property Evaluator")
    
    c_p1, c_p2 = st.columns(2)
    
    with c_p1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🏠 Option A (Baseline)</div>', unsafe_allow_html=True)
        a_area = st.number_input("Option A: Area (sq ft)", min_value=500, value=1200, step=100)
        a_bed = st.number_input("Option A: Bedrooms", min_value=1, value=2, step=1)
        a_bath = st.number_input("Option A: Bathrooms", min_value=1, value=1, step=1)
        
        if model is not None:
            a_price = int(model.predict([[a_area, a_bed, a_bath]])[0])
        else:
            a_price = int((a_area * 3600) + (a_bed * 850000) + (a_bath * 450000))
        st.markdown(f"#### Value: **₹{a_price:,}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_p2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🏠 Option B (Comparison)</div>', unsafe_allow_html=True)
        b_area = st.number_input("Option B: Area (sq ft)", min_value=500, value=1600, step=100)
        b_bed = st.number_input("Option B: Bedrooms", min_value=1, value=3, step=1)
        b_bath = st.number_input("Option B: Bathrooms", min_value=1, value=2, step=1)
        
        if model is not None:
            b_price = int(model.predict([[b_area, b_bed, b_bath]])[0])
        else:
            b_price = int((b_area * 3600) + (b_bed * 850000) + (b_bath * 450000))
        st.markdown(f"#### Value: **₹{b_price:,}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    diff = b_price - a_price
    diff_pct = (diff / a_price) * 100
    
    st.markdown('<div class="section-card" style="text-align:center;">', unsafe_allow_html=True)
    st.markdown("### Valuation Discrepancy")
    if diff >= 0:
        st.markdown(f"Option B is more expensive by <span style='color:#06d6a0;'>₹{diff:,} (+{diff_pct:.1f}%)</span> than Option A.", unsafe_allow_html=True)
    else:
        st.markdown(f"Option B is cheaper by <span style='color:#ef233c;'>₹{abs(diff):,} ({diff_pct:.1f}%)</span> than Option A.", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB: ROI & MORTGAGE
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "💰 ROI & Mortgage":
    st.markdown("### 💰 Investment Analytics & Mortgage Calculator")
    
    col_c1, col_c2 = st.columns([2, 2])
    
    with col_c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💳 Financing & Loan Parameters</div>', unsafe_allow_html=True)
        principal = st.number_input("Property Valuation (₹)", min_value=1000000, value=7500000, step=100000)
        downpayment_pct = st.slider("Down Payment (%)", min_value=10, max_value=80, value=20)
        interest_rate = st.slider("Mortgage Interest Rate (%)", min_value=4.0, max_value=15.0, value=8.5, step=0.1)
        loan_years = st.number_input("Loan Term (Years)", min_value=5, max_value=30, value=20, step=5)
        
        downpayment = principal * (downpayment_pct / 100.0)
        loan_amount = principal - downpayment
        
        monthly_rate = (interest_rate / 100.0) / 12
        n_payments = loan_years * 12
        
        emi = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
        total_pay = emi * n_payments
        total_interest = total_pay - loan_amount
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_c2:
        st.markdown(f"""
        <div class="valuation-banner" style="font-size:1.3rem; margin-bottom:1rem; padding: 0.8rem;">
            Estimated Monthly EMI: <span style="color:#d4af37;">₹{int(emi):,}</span>
        </div>
        """, unsafe_allow_html=True)
        
        labels = ["Principal Loan Amount", "Total Interest Cost", "Initial Down Payment"]
        values = [loan_amount, total_interest, downpayment]
        
        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker=dict(colors=["#1f2833", "#d4af37", "#00b4d8"]))])
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f0f5ff"),
            height=230, margin=dict(t=20, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🏆 Projected Property Yield & ROI Metrics")
    c_roi1, c_roi2 = st.columns(2)
    with c_roi1:
        annual_rent = principal * 0.045
        rental_yield = (annual_rent / principal) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🏢</div>
            <div class="metric-value">{rental_yield:.2f}%</div>
            <div class="metric-label">Estimated Gross Rental Yield</div>
        </div>""", unsafe_allow_html=True)
    with c_roi2:
        appr_5yr = (1.062 ** 5 - 1) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-value">+{appr_5yr:.1f}%</div>
            <div class="metric-label">Expected 5-Year Capital Gain</div>
        </div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB: APPRAISAL LOGS
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "📜 Appraisal Logs":
    st.markdown("## 📜 Property Valuation Logs")
    history = st.session_state.history
    if not history:
        st.info("No evaluations run in current session.")
    else:
        df = pd.DataFrame(history)
        st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.download_button("Export History Logs (CSV)", df.to_csv(index=False).encode('utf-8'), "property_appraisals.csv")
        with col_c2:
            if st.button("Clear Log History", use_container_width=True):
                st.session_state.history = []
                save_history([])
                st.rerun()

st.markdown("---")
st.markdown("<div style='text-align:center; color:#8a99ad; font-size:0.8rem;'>⚜️ EstateX Luxury Real Estate Analytics Platform | Linear Regression Engine</div>", unsafe_allow_html=True)
