import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import datetime
import math
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import urllib.parse

st.set_page_config(page_title="GharMool – Smart Property Intelligence",
                   page_icon="🏡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;600;700;800;900&display=swap');
:root{--gold:#f5a623;--gold2:#e8880a;--teal:#00c6a7;--red:#ff4d6d;--blue:#4895ef;
      --bg:#07090f;--bg2:#0e1219;--bg3:#141923;--border:rgba(245,166,35,0.15);
      --text:#e8eaf0;--muted:#7a8499;}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background-color:var(--bg)!important;color:var(--text)!important;}
.stApp{background:radial-gradient(ellipse at top left,#0d1520 0%,#07090f 70%)!important;}
.hero{background:linear-gradient(135deg,#0d1a2e 0%,#1a2d1a 50%,#0d1a2e 100%);
      border:1px solid var(--border);border-radius:24px;padding:2.5rem 3rem;
      margin-bottom:2rem;position:relative;overflow:hidden;}
.hero::before{content:'';position:absolute;top:-60px;right:-60px;width:250px;height:250px;
              border-radius:50%;background:radial-gradient(circle,rgba(245,166,35,0.08),transparent 70%);}
.hero::after{content:'';position:absolute;bottom:-40px;left:-40px;width:180px;height:180px;
             border-radius:50%;background:radial-gradient(circle,rgba(0,198,167,0.06),transparent 70%);}
.hero-title{font-family:'Poppins',sans-serif!important;font-size:2.6rem!important;font-weight:900!important;
            background:linear-gradient(135deg,#fff 0%,#f5a623 60%,#00c6a7 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0.3rem!important;}
.hero-sub{font-size:1rem;color:var(--muted);margin-top:0.4rem;}
.badge{display:inline-block;background:rgba(245,166,35,0.12);border:1px solid rgba(245,166,35,0.3);
       border-radius:50px;padding:4px 14px;font-size:0.78rem;color:var(--gold);margin-bottom:0.8rem;}
.gcard{background:rgba(14,18,25,0.85);border:1px solid var(--border);border-radius:18px;
       padding:1.6rem;margin-bottom:1.2rem;backdrop-filter:blur(12px);transition:all 0.3s ease;}
.gcard:hover{border-color:rgba(245,166,35,0.3);box-shadow:0 12px 40px rgba(0,0,0,0.4);}
.gcard-title{font-family:'Poppins',sans-serif;font-size:1rem;font-weight:700;color:var(--gold);
             margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;}
.kpi{background:linear-gradient(135deg,var(--bg2),var(--bg3));border:1px solid var(--border);
     border-radius:16px;padding:1.4rem;text-align:center;position:relative;overflow:hidden;}
.kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
             background:linear-gradient(90deg,var(--gold),var(--teal));}
.kpi-val{font-size:1.7rem;font-weight:800;color:var(--gold);}
.kpi-lab{font-size:0.78rem;color:var(--muted);margin-top:0.2rem;}
.kpi-icon{font-size:1.8rem;margin-bottom:0.4rem;}
.stButton>button{background:rgba(245,166,35,0.08)!important;color:var(--muted)!important;
                 border:1px solid rgba(245,166,35,0.2)!important;border-radius:12px!important;
                 font-weight:500!important;transition:all 0.25s!important;font-size:0.88rem!important;}
.stButton>button:hover{background:rgba(245,166,35,0.18)!important;color:var(--gold)!important;
                       border-color:var(--gold)!important;transform:translateY(-1px)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--bg2)!important;border-radius:12px!important;
    padding:4px!important;border:1px solid var(--border)!important;gap:4px!important;}
.stTabs [data-baseweb="tab"]{color:var(--muted)!important;border-radius:8px!important;
    font-weight:500!important;font-size:0.88rem!important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,var(--gold2),var(--gold))!important;
    color:#000!important;font-weight:700!important;}
::-webkit-scrollbar{width:5px;}::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--gold2);border-radius:3px;}
.info-row{display:flex;justify-content:space-between;padding:0.5rem 0;
          border-bottom:1px solid rgba(255,255,255,0.04);font-size:0.9rem;}
.info-row:last-child{border-bottom:none;}
.info-label{color:var(--muted);}.info-val{color:var(--text);font-weight:600;}
.val-banner{background:linear-gradient(135deg,rgba(245,166,35,0.12),rgba(0,198,167,0.08));
            border:2px solid var(--gold);border-radius:18px;padding:1.8rem 2rem;text-align:center;}
.val-price{font-family:'Poppins',sans-serif;font-size:2.8rem;font-weight:900;
           color:var(--gold);text-shadow:0 0 30px rgba(245,166,35,0.3);}
</style>
""", unsafe_allow_html=True)

# ── RATES DATABASE ────────────────────────────────────────────
CITY_BASE_RATES = {
    "mumbai":28000,"navi mumbai":9500,"thane":8500,
    "delhi":14000,"new delhi":18000,"south delhi":35000,
    "bengaluru":8500,"bangalore":8500,"pune":7200,
    "hyderabad":6500,"chennai":6800,"kolkata":5500,
    "gurugram":9000,"gurgaon":9000,"noida":7000,
    "greater noida":4800,"faridabad":5500,
    "ahmedabad":4500,"jaipur":4200,"lucknow":3800,
    "surat":4800,"kanpur":2800,"nagpur":3800,
    "indore":4500,"bhopal":3500,"vadodara":4000,
    "coimbatore":4200,"vizag":4000,"visakhapatnam":4000,
    "patna":3000,"ranchi":2800,"raipur":2800,
    "kochi":6000,"cochin":6000,"thiruvananthapuram":4800,
    "chandigarh":6200,"ludhiana":3800,"amritsar":3500,
    "nashik":3800,"aurangabad":3200,"solapur":2700,
    "madurai":3500,"trichy":3200,"salem":2800,
    "mysuru":5000,"mysore":5000,"hubli":3200,
    "mangalore":5200,"mangaluru":5200,"bhubaneswar":4000,
    "guwahati":3800,"dehradun":5200,"shimla":5500,
    "jodhpur":3200,"udaipur":3500,"ajmer":2800,
    "prayagraj":3000,"allahabad":3000,"ghaziabad":5200,
    "muzaffarnagar":2500,"meerut":3200,"saharanpur":2200,
    "bareilly":2600,"moradabad":2400,"aligarh":2500,
    "mathura":2800,"agra":3000,"firozabad":2000,
    "gorakhpur":2800,"varanasi":3200,"hapur":2800,
    "bulandshahr":2600,"shamli":2000,"khatauli":2200,
    "jhansi":2200,"etawah":1900,"shahjahanpur":2000,
    "default_urban":2200,"default_rural":900,
}

AREA_MULTIPLIERS = {
    "malabar hill":3.2,"cuffe parade":3.0,"worli":2.5,"bandra":2.2,
    "juhu":2.0,"powai":1.4,"andheri":1.1,"borivali":0.9,"lower parel":2.0,
    "lutyens":3.5,"defence colony":2.8,"vasant vihar":2.5,"hauz khas":2.2,
    "lajpat nagar":1.6,"dwarka":0.9,"rohini":0.85,"saket":1.8,"greater kailash":2.0,
    "indiranagar":1.9,"koramangala":1.8,"whitefield":1.4,"hsr layout":1.6,
    "jayanagar":1.5,"electronic city":1.0,"sarjapur":1.2,"marathahalli":1.3,
    "jubilee hills":2.2,"banjara hills":2.0,"hitech city":1.6,"gachibowli":1.5,
    "koregaon park":1.8,"kalyani nagar":1.6,"wakad":1.2,"hinjewadi":1.3,
    "anna nagar":1.7,"t nagar":1.6,"adyar":1.8,"velachery":1.3,
    "dlf":1.8,"golf course":2.1,"sohna road":1.1,
    "civil lines":1.3,"cantonment":1.4,"model town":1.2,"shastri nagar":1.1,
}

FEATURE_PREMIUMS = {
    "balcony":0.025,"terrace":0.04,"storeroom":0.015,"pooja_room":0.015,
    "servant_qr":0.035,"parking":0.03,"lift":0.025,"gym":0.015,
    "pool":0.04,"garden":0.03,"security":0.015,
    "furnished":0.10,"semi_furnished":0.05,
}

PROPERTY_TYPE_MULT = {
    "Independent House / Villa":1.20,"Apartment / Flat":1.00,
    "Builder Floor":1.05,"Penthouse":1.35,"Studio Apartment":0.92,
    "Row House":1.12,"Duplex":1.15,"Commercial Property":1.30,
    "Agricultural / Plot":0.40,
}

AGE_DISCOUNT = {
    "New / Under Construction":1.05,"0-2 years":1.00,"3-5 years":0.95,
    "6-10 years":0.88,"11-20 years":0.78,"20+ years":0.65,
}

FLOOR_MULT = {
    "Ground Floor":0.96,"1st - 3rd":1.00,"4th - 8th":1.03,
    "9th - 15th":1.06,"16th+":1.10,"N/A (House)":1.00,
}

CITY_GROWTH_RATES = {
    "hyderabad":11.5,"bengaluru":10.8,"bangalore":10.8,
    "pune":9.5,"ahmedabad":9.0,"mumbai":8.5,"delhi":7.8,
    "gurugram":9.2,"gurgaon":9.2,"noida":8.8,"chennai":7.5,"kolkata":6.8,
    "indore":9.5,"dehradun":8.8,"kochi":8.0,"chandigarh":7.5,
    "lucknow":7.2,"ghaziabad":7.8,"jaipur":7.0,"surat":7.5,"nagpur":7.0,
    "muzaffarnagar":5.5,"meerut":6.0,"saharanpur":5.0,"bareilly":5.5,
    "moradabad":5.0,"aligarh":5.2,"mathura":5.8,"agra":6.0,
    "varanasi":6.2,"prayagraj":5.8,"gorakhpur":5.5,"kanpur":5.5,
    "default":5.5,
}

CITY_DEV_INDEX = {
    "bengaluru":{"metro":85,"it_hub":98,"infra":75,"startup":95},
    "bangalore":{"metro":85,"it_hub":98,"infra":75,"startup":95},
    "hyderabad":{"metro":80,"it_hub":90,"infra":78,"startup":82},
    "pune":{"metro":70,"it_hub":85,"infra":72,"startup":78},
    "mumbai":{"metro":92,"it_hub":80,"infra":88,"startup":75},
    "delhi":{"metro":90,"it_hub":70,"infra":85,"startup":70},
    "chennai":{"metro":75,"it_hub":80,"infra":70,"startup":72},
    "gurugram":{"metro":72,"it_hub":78,"infra":70,"startup":68},
    "noida":{"metro":75,"it_hub":65,"infra":70,"startup":60},
    "lucknow":{"metro":55,"it_hub":40,"infra":58,"startup":42},
    "jaipur":{"metro":50,"it_hub":45,"infra":55,"startup":48},
    "indore":{"metro":48,"it_hub":52,"infra":55,"startup":50},
    "meerut":{"metro":40,"it_hub":25,"infra":42,"startup":22},
    "muzaffarnagar":{"metro":20,"it_hub":10,"infra":30,"startup":12},
    "agra":{"metro":35,"it_hub":20,"infra":40,"startup":18},
    "varanasi":{"metro":30,"it_hub":18,"infra":38,"startup":15},
    "default":{"metro":25,"it_hub":18,"infra":28,"startup":15},
}

CITY_ALIASES = {
    "bengaluru":"bengaluru","bangalore":"bengaluru",
    "bengaluru central city corporation":"bengaluru",
    "bangalore east":"bengaluru","bengaluru urban":"bengaluru",
    "mumbai city":"mumbai","greater mumbai":"mumbai","brihan mumbai":"mumbai",
    "delhi":"delhi","new delhi":"new delhi",
    "national capital territory of delhi":"delhi",
    "hyderabad":"hyderabad","secunderabad":"hyderabad",
    "pune city":"pune","pimpri-chinchwad":"pune",
    "chennai":"chennai","madras":"chennai","greater chennai":"chennai",
    "kolkata":"kolkata","calcutta":"kolkata",
    "gurugram":"gurugram","gurgaon":"gurugram",
    "noida":"noida","greater noida":"greater noida",
    "ahmedabad":"ahmedabad","surat":"surat","vadodara":"vadodara",
    "jaipur":"jaipur","jodhpur":"jodhpur","udaipur":"udaipur",
    "lucknow":"lucknow","kanpur":"kanpur","agra":"agra",
    "varanasi":"varanasi","prayagraj":"prayagraj","allahabad":"prayagraj",
    "meerut":"meerut","ghaziabad":"ghaziabad","muzaffarnagar":"muzaffarnagar",
    "saharanpur":"saharanpur","bareilly":"bareilly","moradabad":"moradabad",
    "aligarh":"aligarh","mathura":"mathura","gorakhpur":"gorakhpur",
    "chandigarh":"chandigarh","ludhiana":"ludhiana","amritsar":"amritsar",
    "kochi":"kochi","cochin":"kochi","ernakulam":"kochi",
    "thiruvananthapuram":"thiruvananthapuram","trivandrum":"thiruvananthapuram",
    "indore":"indore","bhopal":"bhopal","nagpur":"nagpur",
    "dehradun":"dehradun","coimbatore":"coimbatore",
    "madurai":"madurai","trichy":"trichy",
    "mysuru":"mysuru","mysore":"mysuru",
    "mangaluru":"mangaluru","mangalore":"mangaluru",
    "bhubaneswar":"bhubaneswar","guwahati":"guwahati","patna":"patna",
}

# ── GEOCODING ─────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def geocode_address(address_str):
    try:
        geo = Nominatim(user_agent="gharmool_final_v4")
        loc = geo.geocode(address_str + ", India", timeout=12, language="en")
        if loc:
            return {"lat":loc.latitude,"lon":loc.longitude,
                    "full_address":loc.address,"raw":loc.raw}
    except Exception:
        pass
    return None

@st.cache_data(ttl=600, show_spinner=False)
def reverse_geocode(lat, lon):
    try:
        geo = Nominatim(user_agent="gharmool_rev_v4")
        loc = geo.reverse((lat, lon), timeout=12, language="en")
        if loc:
            return {"full_address":loc.address,"raw":loc.raw}
    except Exception:
        pass
    return None

def extract_city(raw_data):
    addr = raw_data.get("address", {}) if raw_data else {}
    for key in ["city","town","city_district","municipality","county","district"]:
        val = addr.get(key, "")
        if val:
            v = val.lower().strip()
            return CITY_ALIASES.get(v, v)
    sd = addr.get("state_district","")
    if sd:
        v = sd.lower().strip()
        if v in CITY_ALIASES: return CITY_ALIASES[v]
        if v in CITY_BASE_RATES: return v
    display = raw_data.get("display_name","")
    for alias in CITY_ALIASES:
        if alias in display.lower():
            return CITY_ALIASES[alias]
    return ""

def extract_area(raw_data):
    addr = raw_data.get("address", {}) if raw_data else {}
    for key in ["neighbourhood","suburb","quarter","village","hamlet","road","residential"]:
        val = addr.get(key,"")
        if val: return val.lower().strip()
    return ""

def extract_state(raw_data):
    addr = raw_data.get("address",{}) if raw_data else {}
    return addr.get("state","")

def extract_pincode(raw_data):
    addr = raw_data.get("address",{}) if raw_data else {}
    pc = addr.get("postcode","")
    return pc if pc else "N/A"

def get_per_sqft_rate(city, area):
    city_l = city.lower().strip()
    area_l = area.lower().strip()
    base = CITY_BASE_RATES.get(city_l, CITY_BASE_RATES["default_urban"])
    area_mult = 1.0
    # ✅ CRITICAL FIX: only match if area is non-empty
    if area_l:
        for ak, mult in AREA_MULTIPLIERS.items():
            if len(ak) >= 4 and (ak in area_l or area_l in ak):
                area_mult = mult
                break
    return int(base * area_mult)

def get_city_tier(city):
    t1 = ["mumbai","delhi","bengaluru","bangalore","hyderabad","pune",
          "chennai","kolkata","gurugram","gurgaon","noida"]
    t2 = ["ahmedabad","jaipur","lucknow","surat","indore","chandigarh",
          "kochi","dehradun","bhubaneswar","guwahati","nagpur","ghaziabad"]
    c = city.lower().strip()
    if c in t1: return 1
    if c in t2: return 2
    return 3

# ── VALUATION ─────────────────────────────────────────────────
def calculate_valuation(sqft,bedrooms,bathrooms,toilets,balconies,terrace,
                        storeroom,pooja_room,servant_qr,parking,lift,gym,
                        pool,garden,security,furnishing,prop_type,age,floor,rate):
    base_val   = sqft * rate
    type_mult  = PROPERTY_TYPE_MULT.get(prop_type, 1.0)
    age_mult   = AGE_DISCOUNT.get(age, 0.88)
    floor_mult = FLOOR_MULT.get(floor, 1.0)
    feats = {"balcony":bool(balconies),"terrace":terrace,"storeroom":storeroom,
             "pooja_room":pooja_room,"servant_qr":servant_qr,"parking":parking,
             "lift":lift,"gym":gym,"pool":pool,"garden":garden,"security":security}
    feat_total = sum(FEATURE_PREMIUMS.get(f,0) for f,v in feats.items() if v)
    feat_total += FEATURE_PREMIUMS["balcony"] * (min(balconies,2) - (1 if balconies>0 else 0))
    if furnishing=="Fully Furnished":   feat_total += FEATURE_PREMIUMS["furnished"]
    elif furnishing=="Semi Furnished":  feat_total += FEATURE_PREMIUMS["semi_furnished"]
    room_bonus = (min(bedrooms,6)*0.03) + (bathrooms*0.01) + (toilets*0.008)
    feat_room  = min(feat_total + room_bonus, 0.45)
    val = int(base_val * type_mult * age_mult * floor_mult * (1 + feat_room))
    breakdown = {
        "Base (Area x Rate)":  int(base_val),
        "Property Type":       int(base_val*(type_mult-1)),
        "Age Adjustment":      int(base_val*type_mult*(age_mult-1)),
        "Floor Bonus":         int(base_val*type_mult*age_mult*(floor_mult-1)),
        "Rooms Premium":       int(base_val*type_mult*age_mult*floor_mult*room_bonus),
        "Features Premium":    int(base_val*type_mult*age_mult*floor_mult*feat_total),
    }
    return val, breakdown

# ── MAP ───────────────────────────────────────────────────────
def build_map(lat, lon, address="Property"):
    m = folium.Map(location=[lat,lon], zoom_start=15, tiles=None, control_scale=True)
    folium.TileLayer("https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                     attr="Google Satellite",name="Satellite",max_zoom=21).add_to(m)
    folium.TileLayer("https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                     attr="Google Maps",name="Road Map",max_zoom=21).add_to(m)
    folium.TileLayer("OpenStreetMap",name="OSM").add_to(m)
    folium.LayerControl().add_to(m)
    icon_html="""<div style="background:linear-gradient(135deg,#f5a623,#e8880a);
        width:36px;height:36px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);
        border:3px solid white;box-shadow:0 4px 15px rgba(245,166,35,0.6);"></div>"""
    folium.Marker([lat,lon],
        tooltip=folium.Tooltip(f"<b>📍 {address[:60]}</b>",sticky=True),
        popup=folium.Popup(
            f"<div style='font-family:sans-serif;width:220px;'>"
            f"<b style='color:#f5a623;'>📍 Property</b><br><small>{address}</small><br><br>"
            f"<b>Lat:</b> {lat:.5f}<br><b>Lon:</b> {lon:.5f}</div>",max_width=250),
        icon=folium.DivIcon(html=icon_html,icon_size=(36,36),icon_anchor=(18,36))
    ).add_to(m)
    folium.Circle([lat,lon],radius=100,color="#f5a623",fill=True,
                  fill_color="#f5a623",fill_opacity=0.08,weight=2,
                  dash_array="6,4").add_to(m)
    return m

# ── FLOOR PLAN ────────────────────────────────────────────────
def generate_floor_plan(bedrooms,bathrooms,toilets,balconies,terrace,
                        storeroom,pooja_room,servant_qr,sqft,prop_name="My Property"):
    fig,ax=plt.subplots(figsize=(14,10))
    fig.patch.set_facecolor("#0e1219"); ax.set_facecolor("#0e1219")
    ax.set_xlim(0,100); ax.set_ylim(0,70); ax.set_aspect("equal"); ax.axis("off")
    for x in range(0,101,5): ax.axvline(x,color="#1a2535",linewidth=0.4,zorder=0)
    for y in range(0,71,5):  ax.axhline(y,color="#1a2535",linewidth=0.4,zorder=0)
    C={"wall":"#f5a623","wall_bg":"#1a1000","bed":"#0a2235","bed_bd":"#4895ef",
       "bath":"#072235","bath_bd":"#00c6a7","liv":"#0a1a10","liv_bd":"#2ea043",
       "kit":"#1a0a20","kit_bd":"#a855f7","text":"#ffffff","dim":"#f5a623"}
    def room(x,y,w,h,label,sub="",bg="#0a0a1a",bd="#f5a623",icon=""):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="square,pad=0",
                     facecolor=bg,edgecolor=bd,linewidth=2,zorder=2))
        cx,cy=x+w/2,y+h/2
        if icon: ax.text(cx,cy+0.8,icon,ha="center",va="center",fontsize=10,color=C["text"],zorder=5)
        ax.text(cx,cy-(0.8 if icon else 0),label,ha="center",va="center",fontsize=7.5,
                fontweight="bold",color=C["text"],zorder=5,fontfamily="monospace")
        if sub: ax.text(cx,cy-2.2-(0.8 if icon else 0),sub,ha="center",va="center",
                        fontsize=5.5,color="#888",zorder=5,fontstyle="italic")
    def door(x,y,size=3,d="right"):
        kw=dict(color=C["dim"],linewidth=1.2,zorder=6)
        if d=="right":
            ax.add_patch(mpatches.Arc((x,y),size,size,angle=0,theta1=0,theta2=90,**kw))
            ax.plot([x,x],[y,y+size/2],**kw)
        elif d=="left":
            ax.add_patch(mpatches.Arc((x,y),size,size,angle=0,theta1=90,theta2=180,**kw))
            ax.plot([x,x],[y,y+size/2],**kw)
        elif d=="up":
            ax.add_patch(mpatches.Arc((x,y),size,size,angle=0,theta1=0,theta2=90,**kw))
            ax.plot([x,x+size/2],[y,y],**kw)
    ax.add_patch(FancyBboxPatch((2,2),96,66,boxstyle="square,pad=0",
                 facecolor=C["wall_bg"],edgecolor=C["wall"],linewidth=3,zorder=1))
    rooms=[("LIVING ROOM","🛋",2,22,28,24,C["liv"],C["liv_bd"]),
           ("KITCHEN","🍳",2,2,20,18,C["kit"],C["kit_bd"]),
           ("DINING","🍽",22,2,16,18,C["liv"],"#4ade80")]
    num_beds=min(bedrooms,6)
    bed_labels=["MASTER BED","BED 2","BED 3","BED 4","BED 5","BED 6"]
    if num_beds<=2:
        for i,pos in enumerate([(38,38),(60,38)][:num_beds]):
            rooms.append((bed_labels[i],"🛏",pos[0],pos[1],20,30,C["bed"],C["bed_bd"]))
    elif num_beds<=4:
        for i,pos in enumerate([(38,46),(60,46),(38,22),(60,22)][:num_beds]):
            rooms.append((bed_labels[i],"🛏",pos[0],pos[1],20,22,C["bed"],C["bed_bd"]))
    else:
        for i,pos in enumerate([(38,50),(60,50),(38,30),(60,30),(38,10),(60,10)][:num_beds]):
            rooms.append((bed_labels[i],"🛏",pos[0],pos[1],20,18,C["bed"],C["bed_bd"]))
    bath_defs=[("BATHROOM 1","🚿"),("BATHROOM 2","🚿"),("TOILET 1","🚽"),("TOILET 2","🚽"),("TOILET 3","🚽")]
    for i in range(min(bathrooms+toilets,5)):
        rooms.append((bath_defs[i][0],bath_defs[i][1],82,2+i*13,16,11,C["bath"],C["bath_bd"]))
    if balconies>=1: rooms.append(("BALCONY 1","🌿",2,48,28,10,"#050f0a","#2ea043"))
    if balconies>=2: rooms.append(("BALCONY 2","🌿",2,58,28,10,"#050f0a","#2ea043"))
    misc=[]
    if storeroom:  misc.append(("STORE","📦","#1a1008","#a78bfa"))
    if pooja_room: misc.append(("POOJA","🪔","#1a0808","#f97316"))
    if servant_qr: misc.append(("SERVANT","🏠","#0a0a0a","#888"))
    for i,(ml,mi,mbg,mbd) in enumerate(misc[:3]):
        rooms.append((ml,mi,2+i*18,60,16,8,mbg,mbd))
    for label,icon,rx,ry,rw,rh,rbg,rbd in rooms:
        rw=min(rw,98-rx); rh=min(rh,68-ry)
        if rw>0 and rh>0:
            room(rx,ry,rw,rh,label,f"~{int(sqft*rw*rh/(96*66))} sqft",rbg,rbd,icon)
    door(28,30,3,"right"); door(38,54,3,"left"); door(82,25,3,"up")
    ax.annotate("",xy=(98,0.5),xytext=(2,0.5),arrowprops=dict(arrowstyle="<->",color=C["dim"],lw=0.8))
    ax.text(50,1.5,f"Width ~{int(math.sqrt(sqft*1.25))} ft",fontsize=5,color=C["dim"],ha="center")
    ax.annotate("",xy=(95,67),xytext=(95,63),arrowprops=dict(arrowstyle="->",color=C["wall"],lw=2))
    ax.text(95,68,"N",ha="center",va="center",color=C["wall"],fontsize=10,fontweight="bold")
    ax.plot([3,13],[1.2,1.2],color="#888",lw=2)
    ax.plot([3,3],[0.9,1.5],color="#888",lw=1.5); ax.plot([13,13],[0.9,1.5],color="#888",lw=1.5)
    ax.text(8,0.3,"Scale",ha="center",fontsize=5,color="#888")
    ax.text(50,69.5,f"GHARMOOL FLOOR PLAN  —  {prop_name.upper()}",
            ha="center",va="center",fontsize=9,fontweight="bold",color=C["wall"],fontfamily="monospace")
    ax.text(50,68.5,
            f"Area:{sqft} sqft | {bedrooms}BHK | {bathrooms}Bath | {balconies}Balcony | {datetime.date.today()}",
            ha="center",va="center",fontsize=6,color="#888",fontfamily="monospace")
    ax.legend(handles=[mpatches.Patch(color=C["bed_bd"],label="Bedrooms"),
                        mpatches.Patch(color=C["bath_bd"],label="Baths"),
                        mpatches.Patch(color=C["liv_bd"],label="Living"),
                        mpatches.Patch(color=C["kit_bd"],label="Kitchen")],
              loc="lower right",fontsize=6,fancybox=True,
              facecolor="#0e1219",edgecolor=C["wall"],labelcolor="white",framealpha=0.9)
    plt.tight_layout(pad=0.3)
    buf=io.BytesIO()
    fig.savefig(buf,format="png",dpi=160,bbox_inches="tight",facecolor="#0e1219",edgecolor="none")
    buf.seek(0); plt.close(fig)
    return buf

# ── FORECAST ──────────────────────────────────────────────────
def generate_forecast(val, city, years=15):
    city_l = city.lower().strip()
    rate   = CITY_GROWTH_RATES.get(city_l, CITY_GROWTH_RATES["default"])
    idx    = CITY_DEV_INDEX.get(city_l, CITY_DEV_INDEX["default"])
    tier   = get_city_tier(city_l)
    dev    = (idx["metro"]+idx["it_hub"]+idx["infra"]+idx["startup"])/400.0
    adj    = rate * (0.8 + dev*0.4)
    if tier==3: adj = min(adj, 7.0)
    now  = datetime.date.today().year
    yrs  = list(range(now, now+years+1))
    opt  = [val*((1+adj*1.25/100)**i) for i in range(years+1)]
    base = [val*((1+adj/100)**i)      for i in range(years+1)]
    cons = [val*((1+adj*0.70/100)**i) for i in range(years+1)]
    return yrs, opt, base, cons, adj

def forecast_chart(yrs, opt, base, cons, val, city):
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=yrs,y=opt,name="Optimistic",
        line=dict(color="#06d6a0",width=2.5,dash="dot"),
        fill="tonexty",fillcolor="rgba(6,214,160,0.06)"))
    fig.add_trace(go.Scatter(x=yrs,y=base,name="Base Case",
        line=dict(color="#f5a623",width=3),
        fill="tonexty",fillcolor="rgba(245,166,35,0.08)"))
    fig.add_trace(go.Scatter(x=yrs,y=cons,name="Conservative",
        line=dict(color="#ff4d6d",width=2.5,dash="dash")))
    fig.add_hline(y=val,line_dash="dot",line_color="#888",
                  annotation_text="Current",annotation_font_color="#888",
                  annotation_position="top left")
    for i,yr in enumerate(yrs):
        if yr in [yrs[0]+5,yrs[0]+10,yrs[-1]]:
            fig.add_annotation(x=yr,y=base[i],
                text=f"Rs.{base[i]/1e7:.2f}Cr",
                showarrow=True,arrowhead=2,arrowcolor="#f5a623",
                font=dict(color="#f5a623",size=11),
                bgcolor="rgba(14,18,25,0.9)",bordercolor="#f5a623",borderwidth=1,borderpad=4)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaf0",family="Inter"),
        xaxis=dict(title="Year",showgrid=True,gridcolor="rgba(255,255,255,0.05)",color="#7a8499"),
        yaxis=dict(title="Value (Rs.)",showgrid=True,gridcolor="rgba(245,166,35,0.08)",
                   color="#7a8499",tickformat=",.0f"),
        legend=dict(bgcolor="rgba(14,18,25,0.9)",bordercolor="#f5a623",
                    borderwidth=1,font=dict(color="#e8eaf0")),
        height=420,margin=dict(t=30,b=40,l=20,r=20),hovermode="x unified",
        hoverlabel=dict(bgcolor="#0e1219",bordercolor="#f5a623",font_color="#e8eaf0"))
    return fig

def dev_radar(city):
    idx=CITY_DEV_INDEX.get(city.lower(),CITY_DEV_INDEX["default"])
    cats=["Metro","IT Hub","Infrastructure","Startup"]
    vals=[idx["metro"],idx["it_hub"],idx["infra"],idx["startup"]]
    fig=go.Figure(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],
        fill="toself",fillcolor="rgba(245,166,35,0.12)",
        line=dict(color="#f5a623",width=2),marker=dict(size=7,color="#f5a623")))
    fig.update_layout(
        polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True,range=[0,100],color="#7a8499",
                            gridcolor="rgba(255,255,255,0.07)"),
            angularaxis=dict(color="#e8eaf0")),
        paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#e8eaf0",family="Inter"),
        title=dict(text=f"Development Index — {city.title()}",
                   font=dict(color="#f5a623",size=14)),
        height=340,margin=dict(t=50,b=10))
    return fig

# ── SESSION STATE ─────────────────────────────────────────────
for k,v in {"geo_result":None,"valuation":0,"per_sqft":0,"city_name":"",
            "area_name":"","full_address":"","state_name":"","pincode":""}.items():
    if k not in st.session_state: st.session_state[k]=v

# ── HERO ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="badge">🏡 India's Smart Property Intelligence Platform</div>
  <div class="hero-title">GharMool</div>
  <div class="hero-sub">Location-aware valuation · Architectural floor plans · 15-year forecasts · Live map</div>
</div>
""", unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5=st.tabs([
    "📍 Location & Map","🏠 Property Details & Value",
    "🏗️ Floor Plan","📈 Price Forecast","📊 Market Intelligence"])

# ════════════════════════════════════════════════════
# TAB 1
# ════════════════════════════════════════════════════
with tab1:
    st.markdown("### 📍 Enter Your Property Location")
    col_inp,col_map=st.columns([1.1,2])

    with col_inp:
        st.markdown('<div class="gcard">',unsafe_allow_html=True)
        st.markdown('<div class="gcard-title">🔍 Location Search</div>',unsafe_allow_html=True)

        method=st.radio("Mode",["📝 Address / Locality","📌 Lat / Lon"],
                        horizontal=True,key="search_mode")

        if method=="📝 Address / Locality":
            addr_in=st.text_input(
                "Enter Address, Area or Pincode",
                placeholder="e.g.  Civil Lines, Muzaffarnagar   or   Koramangala, Bangalore",
                key="addr_input_v4")
            if st.button("🔍 Find on Map",use_container_width=True,key="find_btn"):
                if addr_in.strip():
                    with st.spinner("Searching..."):
                        res=geocode_address(addr_in.strip())
                    if res:
                        raw=res.get("raw",{})
                        st.session_state.geo_result   =res
                        st.session_state.city_name    =extract_city(raw)
                        st.session_state.area_name    =extract_area(raw)
                        st.session_state.full_address =res.get("full_address","")
                        st.session_state.state_name   =extract_state(raw)
                        st.session_state.pincode      =extract_pincode(raw)
                        st.session_state.per_sqft     =get_per_sqft_rate(
                            st.session_state.city_name,st.session_state.area_name)
                        st.success("✅ Location found!")
                    else:
                        st.error("❌ Not found. Add city name e.g. 'Civil Lines, Muzaffarnagar'")
                else:
                    st.warning("Please enter an address.")
        else:
            c1,c2=st.columns(2)
            lat_in=c1.number_input("Latitude", value=28.3909,format="%.5f",key="lat_in")
            lon_in=c2.number_input("Longitude",value=77.7061,format="%.5f",key="lon_in")
            if st.button("📌 Fetch Address",use_container_width=True,key="rev_btn"):
                with st.spinner("Reverse geocoding..."):
                    res=reverse_geocode(lat_in,lon_in)
                if res:
                    raw=res.get("raw",{})
                    st.session_state.geo_result   ={"lat":lat_in,"lon":lon_in,
                        "full_address":res["full_address"],"raw":raw}
                    st.session_state.city_name    =extract_city(raw)
                    st.session_state.area_name    =extract_area(raw)
                    st.session_state.full_address =res["full_address"]
                    st.session_state.state_name   =extract_state(raw)
                    st.session_state.pincode      =extract_pincode(raw)
                    st.session_state.per_sqft     =get_per_sqft_rate(
                        st.session_state.city_name,st.session_state.area_name)
                    st.success("✅ Address found!")
                else:
                    st.error("❌ Could not reverse geocode.")

        st.markdown("</div>",unsafe_allow_html=True)

        if st.session_state.geo_result:
            gr=st.session_state.geo_result
            lat_g,lon_g=gr.get("lat",0),gr.get("lon",0)
            gmaps_q=urllib.parse.quote(st.session_state.full_address)
            tier_lbl=["🥇 Tier 1","🥈 Tier 2","🥉 Tier 3"][get_city_tier(st.session_state.city_name)-1]
            st.markdown(f"""
            <div class="gcard" style="border-color:rgba(0,198,167,0.3);">
              <div class="gcard-title">📋 Detected Address</div>
              <div class="info-row"><span class="info-label">📍 Area</span>
                <span class="info-val">{st.session_state.area_name.title() if st.session_state.area_name else '—'}</span></div>
              <div class="info-row"><span class="info-label">🏙️ City</span>
                <span class="info-val">{st.session_state.city_name.title() if st.session_state.city_name else '—'}</span></div>
              <div class="info-row"><span class="info-label">🗺️ State</span>
                <span class="info-val">{st.session_state.state_name if st.session_state.state_name else '—'}</span></div>
              <div class="info-row"><span class="info-label">📮 PIN Code</span>
                <span class="info-val">{st.session_state.pincode}</span></div>
              <div class="info-row"><span class="info-label">🌐 Lat / Lon</span>
                <span class="info-val">{lat_g:.4f}, {lon_g:.4f}</span></div>
              <div class="info-row"><span class="info-label">🏆 City Tier</span>
                <span class="info-val">{tier_lbl}</span></div>
              <div style="margin-top:0.8rem;border-top:1px solid rgba(245,166,35,0.15);padding-top:0.8rem;">
                <div style="color:#7a8499;font-size:0.75rem;margin-bottom:0.2rem;">ESTIMATED RATE (2024)</div>
                <div style="color:#f5a623;font-weight:800;font-size:1.5rem;">Rs.{st.session_state.per_sqft:,} / sq ft</div>
              </div>
            </div>
            <div class="gcard" style="padding:1rem;">
              <div class="gcard-title">🔗 Google Maps</div>
              <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
                <a href="https://www.google.com/maps/search/?api=1&query={gmaps_q}" target="_blank"
                   style="background:rgba(66,133,244,0.15);border:1px solid #4285f4;color:#4285f4;
                          padding:6px 12px;border-radius:8px;font-size:0.8rem;text-decoration:none;">🗺️ Maps</a>
                <a href="https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat_g},{lon_g}" target="_blank"
                   style="background:rgba(234,67,53,0.15);border:1px solid #ea4335;color:#ea4335;
                          padding:6px 12px;border-radius:8px;font-size:0.8rem;text-decoration:none;">🚶 Street</a>
                <a href="https://www.google.com/maps/search/schools+near/@{lat_g},{lon_g},15z" target="_blank"
                   style="background:rgba(0,198,167,0.15);border:1px solid #00c6a7;color:#00c6a7;
                          padding:6px 12px;border-radius:8px;font-size:0.8rem;text-decoration:none;">🏫 Nearby</a>
                <a href="https://www.google.com/maps/dir/?api=1&destination={lat_g},{lon_g}" target="_blank"
                   style="background:rgba(245,166,35,0.15);border:1px solid #f5a623;color:#f5a623;
                          padding:6px 12px;border-radius:8px;font-size:0.8rem;text-decoration:none;">🧭 Route</a>
              </div>
            </div>""",unsafe_allow_html=True)

    with col_map:
        if st.session_state.geo_result:
            gr=st.session_state.geo_result
            m=build_map(gr["lat"],gr["lon"],address=st.session_state.full_address)
            st.markdown('<div style="border-radius:16px;overflow:hidden;border:1px solid rgba(245,166,35,0.2);">',unsafe_allow_html=True)
            st_folium(m,width="100%",height=520,returned_objects=[])
            st.markdown("</div>",unsafe_allow_html=True)
            st.markdown(f"""<div style="background:rgba(14,18,25,0.9);border:1px solid rgba(245,166,35,0.2);
                border-radius:10px;padding:0.8rem 1rem;margin-top:0.8rem;font-size:0.82rem;color:#7a8499;">
              📍 <strong style="color:#e8eaf0;">{st.session_state.full_address}</strong></div>""",
                unsafe_allow_html=True)
        else:
            m0=folium.Map(location=[20.5937,78.9629],zoom_start=5,
                tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",attr="Google Satellite")
            st.markdown('<div style="border-radius:16px;overflow:hidden;border:1px solid rgba(245,166,35,0.15);">',unsafe_allow_html=True)
            st_folium(m0,width="100%",height=520,returned_objects=[])
            st.markdown("</div>",unsafe_allow_html=True)
            st.info("👆 Upar address likho aur Find on Map dabao.")

# ════════════════════════════════════════════════════
# TAB 2
# ════════════════════════════════════════════════════
with tab2:
    if not st.session_state.geo_result:
        st.warning("⚠️ Pehle **📍 Location & Map** tab mein address search karo.")
    else:
        city_disp=st.session_state.city_name.title()
        tier_lbl2=["🥇 Tier 1","🥈 Tier 2","🥉 Tier 3"][get_city_tier(st.session_state.city_name)-1]
        st.markdown(f"### 🏠 Property Details — {city_disp}")
        st.markdown(f"<p style='color:#7a8499;'>Market rate: <strong style='color:#f5a623;'>Rs.{st.session_state.per_sqft:,}/sqft</strong> &nbsp;|&nbsp; {tier_lbl2}</p>",unsafe_allow_html=True)

        col_form,col_result=st.columns([1.3,1.7])
        with col_form:
            with st.form("pform_v4"):
                st.markdown("**📐 Area & Type**")
                c1,c2=st.columns(2)
                sqft     =c1.number_input("Total Area (sq ft)",100,50000,1200,50)
                prop_name=c2.text_input("Property Name","My Home")
                prop_type=st.selectbox("Property Type",list(PROPERTY_TYPE_MULT.keys()))
                c1,c2=st.columns(2)
                age  =c1.selectbox("Property Age",list(AGE_DISCOUNT.keys()))
                floor=c2.selectbox("Floor Level",list(FLOOR_MULT.keys()))
                st.markdown("**🛏️ Rooms**")
                c1,c2,c3=st.columns(3)
                bedrooms =c1.number_input("Bedrooms", 0,20,3,1)
                bathrooms=c2.number_input("Bathrooms",0,15,2,1)
                toilets  =c3.number_input("Toilets",  0,15,1,1)
                st.markdown("**🌿 Extra Spaces**")
                c1,c2,c3=st.columns(3)
                balconies =c1.number_input("Balconies",0,10,1,1)
                terrace   =c2.checkbox("Terrace")
                storeroom =c3.checkbox("Store Room")
                c1,c2,c3=st.columns(3)
                pooja_room=c1.checkbox("Pooja Room")
                servant_qr=c2.checkbox("Servant Qtr.")
                garden    =c3.checkbox("Garden/Lawn")
                st.markdown("**🏢 Amenities**")
                c1,c2,c3=st.columns(3)
                parking =c1.checkbox("Parking",value=True)
                lift    =c2.checkbox("Lift")
                gym     =c3.checkbox("Gym")
                c1,c2=st.columns(2)
                pool    =c1.checkbox("Pool")
                security=c2.checkbox("24x7 Security",value=True)
                furnishing=st.selectbox("Furnishing",
                    ["Unfurnished","Semi Furnished","Fully Furnished"])
                st.markdown("---")
                rate_override=st.number_input(
                    "🔧 Override Rate (Rs./sqft) — 0 = auto",0,500000,0,100)
                submitted=st.form_submit_button("💰 Calculate Valuation",use_container_width=True)

        with col_result:
            if submitted:
                use_rate=rate_override if rate_override>0 else st.session_state.per_sqft
                val,breakdown=calculate_valuation(
                    sqft,bedrooms,bathrooms,toilets,balconies,terrace,storeroom,
                    pooja_room,servant_qr,parking,lift,gym,pool,garden,security,
                    furnishing,prop_type,age,floor,use_rate)
                st.session_state.valuation=val
                for k2,v2 in [("prop_sqft",sqft),("prop_beds",bedrooms),
                               ("prop_baths",bathrooms),("prop_toilets",toilets),
                               ("prop_balconies",balconies),("prop_terrace",terrace),
                               ("prop_store",storeroom),("prop_pooja",pooja_room),
                               ("prop_servant",servant_qr),("prop_name",prop_name)]:
                    st.session_state[k2]=v2
                crore=val/1e7; lac=(val%1e7)/1e5; eff=int(val/sqft)
                st.markdown(f"""
                <div class="val-banner">
                  <div style="font-size:0.8rem;color:#7a8499;margin-bottom:0.4rem;">ESTIMATED MARKET VALUE</div>
                  <div class="val-price">Rs.{val:,}</div>
                  <div style="font-size:1.1rem;color:#e8eaf0;margin:0.4rem 0;">
                    ~ {crore:.2f} Crore &nbsp;|&nbsp; {int(crore)} Cr {int(lac)} Lac
                  </div>
                  <div style="font-size:0.8rem;color:#7a8499;">
                    📍 {st.session_state.area_name.title() or city_disp}, {city_disp}
                    &nbsp;·&nbsp; Rs.{eff:,}/sqft effective
                  </div>
                </div>""",unsafe_allow_html=True)
                st.markdown("<br>",unsafe_allow_html=True)
                c1,c2,c3,c4=st.columns(4)
                for col,ico,vk,lk in [(c1,"📐",f"{sqft:,}","sqft"),
                                       (c2,"💰",f"Rs.{use_rate:,}","Rate/sqft"),
                                       (c3,"🛏",f"{bedrooms}BHK","Config"),
                                       (c4,"📅",age.split()[0],"Age")]:
                    col.markdown(f'<div class="kpi"><div class="kpi-icon">{ico}</div>'
                                 f'<div class="kpi-val">{vk}</div>'
                                 f'<div class="kpi-lab">{lk}</div></div>',unsafe_allow_html=True)
                st.markdown("<br>",unsafe_allow_html=True)
                bd_vals=[max(0,v) for v in breakdown.values()]
                fig_bd=go.Figure(go.Bar(
                    x=list(breakdown.keys()),y=bd_vals,
                    marker_color=["#4895ef","#f5a623","#ff4d6d","#00c6a7","#a855f7","#2ea043"],
                    text=[f"Rs.{v:,}" if v!=0 else "—" for v in bd_vals],
                    textposition="outside",textfont=dict(color="#e8eaf0",size=9)))
                fig_bd.update_layout(title="💡 Valuation Breakdown",
                    paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e8eaf0",size=10),
                    xaxis=dict(showgrid=False,color="#7a8499",tickangle=-20),
                    yaxis=dict(gridcolor="rgba(245,166,35,0.07)",color="#7a8499"),
                    height=280,margin=dict(t=40,b=70),title_font=dict(color="#f5a623"))
                st.plotly_chart(fig_bd,use_container_width=True)
                mr=int(val*0.0025); ay=round(mr*12/val*100,2)
                st.markdown(f"""
                <div class="gcard" style="border-color:rgba(0,198,167,0.3);">
                  <div class="gcard-title">🏷️ Rental & Yield</div>
                  <div class="info-row"><span class="info-label">Monthly Rent</span>
                    <span class="info-val" style="color:#00c6a7;">Rs.{mr:,}</span></div>
                  <div class="info-row"><span class="info-label">Annual Yield</span>
                    <span class="info-val" style="color:#00c6a7;">{ay}%</span></div>
                  <div class="info-row"><span class="info-label">Annual Income</span>
                    <span class="info-val">Rs.{mr*12:,}</span></div>
                  <div class="info-row"><span class="info-label">Break-even</span>
                    <span class="info-val">~{int(val/(mr*12))} years</span></div>
                </div>""",unsafe_allow_html=True)
            elif st.session_state.valuation>0:
                v=st.session_state.valuation
                st.markdown(f"""<div class="val-banner">
                  <div style="font-size:0.8rem;color:#7a8499;">LAST VALUE</div>
                  <div class="val-price">Rs.{v:,}</div>
                  <div style="color:#e8eaf0;">~ {v/1e7:.2f} Crore</div></div>""",
                    unsafe_allow_html=True)
                st.info("Form bharke Calculate dabao to refresh karo.")
            else:
                st.info("👈 Property details bharke Calculate Valuation dabao.")

# ════════════════════════════════════════════════════
# TAB 3
# ════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🏗️ Architectural Floor Plan Generator")
    col_fp1,col_fp2=st.columns([1,2.5])
    with col_fp1:
        st.markdown('<div class="gcard">',unsafe_allow_html=True)
        st.markdown('<div class="gcard-title">⚙️ Settings</div>',unsafe_allow_html=True)
        fp_beds     =st.number_input("Bedrooms", 0,8, st.session_state.get("prop_beds",3),1,key="fpb")
        fp_baths    =st.number_input("Bathrooms",0,6, st.session_state.get("prop_baths",2),1,key="fpba")
        fp_toilets  =st.number_input("Toilets",  0,6, st.session_state.get("prop_toilets",1),1,key="fpt")
        fp_balconies=st.number_input("Balconies",0,4, st.session_state.get("prop_balconies",1),1,key="fpbl")
        fp_terrace  =st.checkbox("Terrace",   value=st.session_state.get("prop_terrace",False),key="fptr")
        fp_store    =st.checkbox("Store Room",value=st.session_state.get("prop_store",False),key="fpst")
        fp_pooja    =st.checkbox("Pooja Room",value=st.session_state.get("prop_pooja",False),key="fppo")
        fp_servant  =st.checkbox("Servant Qtr",value=st.session_state.get("prop_servant",False),key="fpse")
        fp_sqft     =st.number_input("Area (sqft)",200,50000,st.session_state.get("prop_sqft",1200),100,key="fpsq")
        fp_name     =st.text_input("Property Name",st.session_state.get("prop_name","My Property"),key="fpnm")
        gen_btn     =st.button("🏗️ Generate Floor Plan",use_container_width=True,key="gen_fp")
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("""<div class="gcard" style="font-size:0.82rem;color:#7a8499;">
          <div class="gcard-title">📖 Legend</div>
          🔵 Bedrooms &nbsp; 🟢 Living/Dining<br>
          🟣 Kitchen &nbsp;&nbsp; 🩵 Bathrooms<br>
          🧭 N = North Direction
        </div>""",unsafe_allow_html=True)
    with col_fp2:
        if gen_btn or st.session_state.get("fp_generated"):
            with st.spinner("Generating floor plan..."):
                buf=generate_floor_plan(fp_beds,fp_baths,fp_toilets,fp_balconies,
                    fp_terrace,fp_store,fp_pooja,fp_servant,fp_sqft,fp_name)
                st.session_state["fp_generated"]=True
                st.session_state["fp_buf"]=buf.getvalue()
        if st.session_state.get("fp_buf"):
            img=st.session_state["fp_buf"]
            st.image(img,use_container_width=True,caption="GharMool Architectural Floor Plan")
            st.download_button("⬇️ Download PNG",data=img,
                file_name=f"GharMool_{fp_name.replace(' ','_')}.png",
                mime="image/png",use_container_width=True)
            st.markdown("""<div class="gcard" style="border-color:rgba(0,198,167,0.3);margin-top:1rem;">
              <div class="gcard-title">💡 Architect Tips</div>
              <div style="font-size:0.85rem;color:#e8eaf0;line-height:1.9;">
                🌞 <strong>Orientation:</strong> Living room East-facing for morning sunlight.<br>
                🌬️ <strong>Ventilation:</strong> Opposite wall windows for cross-ventilation.<br>
                🚿 <strong>Wet Areas:</strong> Bathrooms group karo — plumbing cost bachega.<br>
                🍳 <strong>Kitchen:</strong> L-shape ya U-shape layout best hota hai.<br>
                🌿 <strong>Balcony:</strong> North-facing Indian summers mein thanda rehta hai.<br>
                💡 <strong>Vastu:</strong> Master bed SW, Kitchen SE, Pooja NE mein rakho.
              </div></div>""",unsafe_allow_html=True)
        else:
            st.markdown("""<div style="border:2px dashed rgba(245,166,35,0.25);border-radius:18px;
                height:400px;display:flex;align-items:center;justify-content:center;
                flex-direction:column;color:#7a8499;">
              <div style="font-size:3rem;margin-bottom:1rem;">🏗️</div>
              <div style="font-size:1.1rem;font-weight:600;">Rooms configure karo aur Generate dabao</div>
              <div style="font-size:0.85rem;margin-top:0.5rem;">Engineer-quality floor plan yahan ayega</div>
            </div>""",unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 4
# ════════════════════════════════════════════════════
with tab4:
    st.markdown("### 📈 Property Price Forecast")
    city_fc=st.session_state.city_name or "muzaffarnagar"
    val_fc =st.session_state.valuation if st.session_state.valuation>0 else 2500000
    col_fc1,col_fc2=st.columns([1,2.5])
    with col_fc1:
        st.markdown('<div class="gcard">',unsafe_allow_html=True)
        st.markdown('<div class="gcard-title">⚙️ Settings</div>',unsafe_allow_html=True)
        fc_val  =st.number_input("Current Value (Rs.)",100000,1000000000,max(val_fc,500000),50000)
        fc_city =st.text_input("City",city_fc.title() or "Muzaffarnagar")
        fc_years=st.slider("Forecast Years",5,15,15)
        st.markdown("</div>",unsafe_allow_html=True)
        gr2=CITY_GROWTH_RATES.get(fc_city.lower().strip(),CITY_GROWTH_RATES["default"])
        tier_fc=get_city_tier(fc_city.lower().strip())
        tl=["🥇 Tier 1 — High Growth","🥈 Tier 2 — Moderate","🥉 Tier 3 — Steady"][tier_fc-1]
        st.markdown(f"""<div class="gcard" style="border-color:rgba(0,198,167,0.3);">
          <div class="gcard-title">📊 City Growth Profile</div>
          <div class="info-row"><span class="info-label">Tier</span><span class="info-val">{tl}</span></div>
          <div class="info-row"><span class="info-label">CAGR</span>
            <span class="info-val" style="color:#00c6a7;">{gr2:.1f}% / yr</span></div>
          <div class="info-row"><span class="info-label">5yr Est.</span>
            <span class="info-val">Rs.{int(fc_val*(1+gr2/100)**5):,}</span></div>
          <div class="info-row"><span class="info-label">10yr Est.</span>
            <span class="info-val">Rs.{int(fc_val*(1+gr2/100)**10):,}</span></div>
          <div class="info-row"><span class="info-label">15yr Est.</span>
            <span class="info-val" style="color:#f5a623;">Rs.{int(fc_val*(1+gr2/100)**15):,}</span></div>
        </div>""",unsafe_allow_html=True)
    with col_fc2:
        yrs,opt,base,cons,adj=generate_forecast(fc_val,fc_city.strip(),fc_years)
        st.plotly_chart(forecast_chart(yrs,opt,base,cons,fc_val,fc_city),use_container_width=True)
        rows=[]
        for i,yr in enumerate(yrs):
            if i%3==0 or i==len(yrs)-1:
                rows.append({"Year":yr,
                             "Conservative":f"Rs.{int(cons[i]):,}",
                             "Base Case":f"Rs.{int(base[i]):,}",
                             "Optimistic":f"Rs.{int(opt[i]):,}",
                             "Gain(Base)":f"+{int((base[i]/fc_val-1)*100)}%"})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

# ════════════════════════════════════════════════════
# TAB 5
# ════════════════════════════════════════════════════
with tab5:
    st.markdown("### 📊 Market Intelligence & Development Index")
    city_mi=st.session_state.city_name or "muzaffarnagar"
    col_mi1,col_mi2=st.columns([1.5,2])
    with col_mi1:
        st.plotly_chart(dev_radar(city_mi),use_container_width=True)
        cc=["mumbai","delhi","bengaluru","hyderabad","pune","chennai","gurugram","kolkata","ahmedabad","jaipur"]
        rc=[CITY_BASE_RATES.get(c,3000) for c in cc]
        fig_cmp=go.Figure(go.Bar(x=[c.title() for c in cc],y=rc,
            marker=dict(color=rc,colorscale=[[0,"#ff4d6d"],[0.5,"#f5a623"],[1,"#00c6a7"]]),
            text=[f"Rs.{r:,}" for r in rc],textposition="outside",
            textfont=dict(size=9,color="#e8eaf0")))
        fig_cmp.add_hline(
            y=st.session_state.per_sqft if st.session_state.per_sqft>0 else 2500,
            line_dash="dot",line_color="#f5a623",
            annotation_text=f"Your City ({city_mi.title()})",
            annotation_font_color="#f5a623")
        fig_cmp.update_layout(title="💹 Rate Comparison (Rs./sqft)",
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eaf0"),
            xaxis=dict(showgrid=False,color="#7a8499",tickangle=-30),
            yaxis=dict(gridcolor="rgba(245,166,35,0.07)",color="#7a8499"),
            height=340,margin=dict(t=40,b=80),title_font=dict(color="#f5a623"))
        st.plotly_chart(fig_cmp,use_container_width=True)
    with col_mi2:
        area_keys =["Premium (2x)","Good (1.4x)","Standard (1x)","Developing (0.8x)"]
        area_mults=[2.0,1.4,1.0,0.8]
        ptype_keys=list(PROPERTY_TYPE_MULT.keys())[:6]
        ptype_mults=[PROPERTY_TYPE_MULT[k] for k in ptype_keys]
        base_r=st.session_state.per_sqft if st.session_state.per_sqft>0 else 2500
        sqft_ref=st.session_state.get("prop_sqft",1500)
        z_data=[[int(base_r*am*pm*sqft_ref/1e5) for pm in ptype_mults] for am in area_mults]
        # ✅ FIXED colorbar — no deprecated titlefont
        fig_hm=go.Figure(go.Heatmap(
            z=z_data,
            x=[k.split("/")[0].strip()[:16] for k in ptype_keys],
            y=area_keys,
            colorscale=[[0,"#0a0a1a"],[0.35,"#7a2040"],[0.7,"#d4a000"],[1,"#00c6a7"]],
            text=[[f"Rs.{v}L" for v in row] for row in z_data],
            texttemplate="%{text}",textfont=dict(size=10,color="#fff"),
            hovertemplate="Area:<b>%{y}</b><br>Type:<b>%{x}</b><br>~<b>Rs.%{z}L</b><extra></extra>",
            colorbar=dict(
                title=dict(text="Lakhs (Rs.)",font=dict(color="#e8eaf0")),
                thickness=12,tickfont=dict(color="#e8eaf0"))))
        fig_hm.update_layout(
            title=f"🔥 Value Matrix — {sqft_ref} sqft in {city_mi.title()} (Rs. Lakhs)",
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eaf0"),
            xaxis=dict(color="#7a8499",tickangle=-20),yaxis=dict(color="#7a8499"),
            height=320,margin=dict(t=50,b=60),title_font=dict(color="#f5a623"))
        st.plotly_chart(fig_hm,use_container_width=True)
        cities_gr=["bengaluru","hyderabad","pune","mumbai","delhi",
                   "meerut","muzaffarnagar","lucknow","agra","varanasi"]
        gr_vals=[CITY_GROWTH_RATES.get(c,5.5) for c in cities_gr]
        fig_gr=go.Figure(go.Bar(x=[c.title() for c in cities_gr],y=gr_vals,
            marker=dict(color=gr_vals,colorscale=[[0,"#ff4d6d"],[0.5,"#f5a623"],[1,"#06d6a0"]]),
            text=[f"{v:.1f}%" for v in gr_vals],textposition="outside",
            textfont=dict(size=10,color="#e8eaf0")))
        fig_gr.update_layout(title="📈 Annual Appreciation by City (CAGR)",
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eaf0"),
            xaxis=dict(showgrid=False,color="#7a8499",tickangle=-30),
            yaxis=dict(gridcolor="rgba(245,166,35,0.07)",color="#7a8499",
                       range=[0,max(gr_vals)*1.25]),
            height=300,margin=dict(t=40,b=80),title_font=dict(color="#f5a623"))
        st.plotly_chart(fig_gr,use_container_width=True)

st.markdown("---")
st.markdown("""<div style="text-align:center;color:#7a8499;font-size:0.82rem;padding:1rem;">
  🏡 <strong style="color:#f5a623;">GharMool</strong> — India's Smart Property Intelligence Platform |
  OpenStreetMap · Nominatim · Plotly · Matplotlib |
  <em>Estimates only — consult registered valuer for official assessment</em>
</div>""",unsafe_allow_html=True)
