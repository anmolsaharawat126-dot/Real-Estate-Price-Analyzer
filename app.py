import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import datetime
import json
import random
import math
import io
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import time
import urllib.parse

st.set_page_config(
    page_title="GharMool – Smart Property Intelligence",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;600;700;800;900&display=swap');
:root {
    --gold:#f5a623;--gold2:#e8880a;--teal:#00c6a7;--red:#ff4d6d;--blue:#4895ef;
    --bg:#07090f;--bg2:#0e1219;--bg3:#141923;--border:rgba(245,166,35,0.15);
    --text:#e8eaf0;--muted:#7a8499;
}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background-color:var(--bg)!important;color:var(--text)!important;}
.stApp{background:radial-gradient(ellipse at top left,#0d1520 0%,#07090f 70%)!important;}
.hero{background:linear-gradient(135deg,#0d1a2e 0%,#1a2d1a 50%,#0d1a2e 100%);border:1px solid var(--border);border-radius:24px;padding:2.5rem 3rem;margin-bottom:2rem;position:relative;overflow:hidden;}
.hero::before{content:'';position:absolute;top:-60px;right:-60px;width:250px;height:250px;border-radius:50%;background:radial-gradient(circle,rgba(245,166,35,0.08),transparent 70%);}
.hero::after{content:'';position:absolute;bottom:-40px;left:-40px;width:180px;height:180px;border-radius:50%;background:radial-gradient(circle,rgba(0,198,167,0.06),transparent 70%);}
.hero-title{font-family:'Poppins',sans-serif!important;font-size:2.6rem!important;font-weight:900!important;background:linear-gradient(135deg,#ffffff 0%,#f5a623 60%,#00c6a7 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0.3rem!important;}
.hero-sub{font-size:1rem;color:var(--muted);margin-top:0.4rem;}
.badge{display:inline-block;background:rgba(245,166,35,0.12);border:1px solid rgba(245,166,35,0.3);border-radius:50px;padding:4px 14px;font-size:0.78rem;color:var(--gold);margin-bottom:0.8rem;}
.gcard{background:rgba(14,18,25,0.85);border:1px solid var(--border);border-radius:18px;padding:1.6rem;margin-bottom:1.2rem;backdrop-filter:blur(12px);transition:all 0.3s ease;}
.gcard:hover{border-color:rgba(245,166,35,0.3);box-shadow:0 12px 40px rgba(0,0,0,0.4);}
.gcard-title{font-family:'Poppins',sans-serif;font-size:1rem;font-weight:700;color:var(--gold);margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;}
.kpi{background:linear-gradient(135deg,var(--bg2),var(--bg3));border:1px solid var(--border);border-radius:16px;padding:1.4rem;text-align:center;position:relative;overflow:hidden;}
.kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--gold),var(--teal));}
.kpi-val{font-size:1.7rem;font-weight:800;color:var(--gold);}
.kpi-lab{font-size:0.78rem;color:var(--muted);margin-top:0.2rem;}
.kpi-icon{font-size:1.8rem;margin-bottom:0.4rem;}
.stButton>button{background:rgba(245,166,35,0.08)!important;color:var(--muted)!important;border:1px solid rgba(245,166,35,0.2)!important;border-radius:12px!important;font-weight:500!important;transition:all 0.25s!important;font-size:0.88rem!important;}
.stButton>button:hover{background:rgba(245,166,35,0.18)!important;color:var(--gold)!important;border-color:var(--gold)!important;transform:translateY(-1px)!important;}
.stNumberInput input,.stTextInput input,.stSelectbox select,.stTextArea textarea{background:rgba(245,166,35,0.04)!important;border:1px solid var(--border)!important;border-radius:10px!important;color:var(--text)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--bg2)!important;border-radius:12px!important;padding:4px!important;border:1px solid var(--border)!important;gap:4px!important;}
.stTabs [data-baseweb="tab"]{color:var(--muted)!important;border-radius:8px!important;font-weight:500!important;font-size:0.88rem!important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,var(--gold2),var(--gold))!important;color:#000!important;font-weight:700!important;}
::-webkit-scrollbar{width:5px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:var(--gold2);border-radius:3px;}
[data-testid="stMetricValue"]{color:var(--gold)!important;font-size:1.5rem!important;}
.info-row{display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:0.9rem;}
.info-row:last-child{border-bottom:none;}
.info-label{color:var(--muted);}
.info-val{color:var(--text);font-weight:600;}
.val-banner{background:linear-gradient(135deg,rgba(245,166,35,0.12),rgba(0,198,167,0.08));border:2px solid var(--gold);border-radius:18px;padding:1.8rem 2rem;text-align:center;}
.val-price{font-family:'Poppins',sans-serif;font-size:2.8rem;font-weight:900;color:var(--gold);text-shadow:0 0 30px rgba(245,166,35,0.3);}
</style>
""", unsafe_allow_html=True)

CITY_BASE_RATES = {
    "mumbai":28000,"navi mumbai":9500,"thane":8500,
    "delhi":14000,"new delhi":18000,"south delhi":35000,
    "bengaluru":8500,"bangalore":8500,
    "pune":7200,"hyderabad":6500,"chennai":6800,
    "kolkata":5500,"gurugram":9000,"gurgaon":9000,
    "noida":7000,"greater noida":4800,"faridabad":5500,
    "ahmedabad":4500,"jaipur":4200,"lucknow":4000,
    "surat":4800,"kanpur":3200,"nagpur":3800,
    "indore":4500,"bhopal":3800,"vadodara":4000,
    "coimbatore":4200,"vizag":4000,"visakhapatnam":4000,
    "patna":3500,"ranchi":3200,"raipur":3000,
    "kochi":6000,"cochin":6000,"thiruvananthapuram":5000,
    "chandigarh":6500,"ludhiana":4000,"amritsar":3800,
    "agra":3200,"varanasi":3500,"meerut":3200,
    "nashik":4200,"aurangabad":3500,"solapur":3000,
    "madurai":3800,"trichy":3500,"salem":3200,
    "mysuru":5000,"mysore":5000,"hubli":3500,
    "mangalore":5500,"mangaluru":5500,"bhubaneswar":4200,
    "guwahati":4000,"dehradun":5500,"shimla":6000,
    "jodhpur":3500,"udaipur":3800,"ajmer":3000,
    "allahabad":3200,"prayagraj":3200,"ghaziabad":5500,
    "default_urban":2800,"default_rural":1200,
}

AREA_MULTIPLIERS = {
    "malabar hill":3.2,"cuffe parade":3.0,"worli":2.5,"bandra":2.2,
    "juhu":2.0,"powai":1.3,"andheri":1.1,"borivali":0.9,
    "lutyens":3.5,"defence colony":2.8,"vasant vihar":2.5,"hauz khas":2.2,
    "lajpat nagar":1.6,"dwarka":0.9,"rohini":0.8,
    "indiranagar":1.9,"koramangala":1.8,"whitefield":1.4,"hsr layout":1.6,
    "jayanagar":1.5,"electronic city":1.0,
    "jubilee hills":2.2,"banjara hills":2.0,"hitech city":1.6,
    "gachibowli":1.5,"secunderabad":1.2,
    "koregaon park":1.8,"kalyani nagar":1.6,"wakad":1.2,"hinjewadi":1.3,
    "anna nagar":1.7,"t nagar":1.6,"adyar":1.8,"velachery":1.3,
    "dlf":1.8,"golf course":2.1,"sohna road":1.1,
}

FEATURE_PREMIUMS = {
    "balcony":0.03,"terrace":0.05,"storeroom":0.02,"pooja_room":0.02,
    "servant_qr":0.04,"parking":0.04,"lift":0.03,"gym":0.02,
    "pool":0.05,"garden":0.04,"security":0.02,"furnished":0.12,"semi_furnished":0.06,
}

PROPERTY_TYPE_MULT = {
    "Independent House / Villa":1.25,"Apartment / Flat":1.00,
    "Builder Floor":1.08,"Penthouse":1.40,"Studio Apartment":0.90,
    "Row House":1.15,"Duplex":1.20,"Commercial Property":1.35,"Agricultural / Plot":0.45,
}

AGE_DISCOUNT = {
    "New / Under Construction":1.05,"0-2 years":1.00,"3-5 years":0.95,
    "6-10 years":0.88,"11-20 years":0.78,"20+ years":0.65,
}

FLOOR_MULT = {
    "Ground Floor":0.95,"1st - 3rd":1.00,"4th - 8th":1.03,
    "9th - 15th":1.06,"16th+":1.10,"N/A (House)":1.00,
}

CITY_GROWTH_RATES = {
    "mumbai":9.5,"delhi":8.5,"bengaluru":11.2,"bangalore":11.2,
    "hyderabad":12.5,"pune":10.8,"chennai":8.2,"kolkata":7.5,
    "gurugram":9.8,"gurgaon":9.8,"noida":9.2,"ahmedabad":9.5,
    "indore":11.0,"kochi":9.0,"chandigarh":8.5,"dehradun":10.2,"default":7.5,
}

CITY_DEVELOPMENT_INDEX = {
    "bengaluru":{"metro":85,"it_hub":98,"infra":75,"startup":95},
    "bangalore":{"metro":85,"it_hub":98,"infra":75,"startup":95},
    "hyderabad":{"metro":80,"it_hub":90,"infra":78,"startup":82},
    "pune":{"metro":70,"it_hub":85,"infra":72,"startup":78},
    "mumbai":{"metro":92,"it_hub":80,"infra":88,"startup":75},
    "delhi":{"metro":90,"it_hub":70,"infra":85,"startup":70},
    "chennai":{"metro":75,"it_hub":80,"infra":70,"startup":72},
    "default":{"metro":55,"it_hub":45,"infra":50,"startup":40},
}

@st.cache_data(ttl=300,show_spinner=False)
def geocode_address(address_str):
    try:
        geolocator=Nominatim(user_agent="gharmool_app_v1")
        location=geolocator.geocode(address_str+", India",timeout=8,language="en")
        if location:
            return {"lat":location.latitude,"lon":location.longitude,
                    "full_address":location.address,"raw":location.raw}
    except Exception:
        pass
    return None

@st.cache_data(ttl=300,show_spinner=False)
def reverse_geocode(lat,lon):
    try:
        geolocator=Nominatim(user_agent="gharmool_rev_v1")
        location=geolocator.reverse((lat,lon),timeout=8,language="en")
        if location:
            return {"full_address":location.address,"raw":location.raw}
    except Exception:
        pass
    return None

CITY_ALIASES = {
    "bengaluru":"bengaluru","bangalore":"bengaluru",
    "bengaluru central city corporation":"bengaluru","bangalore east":"bengaluru","bengaluru urban":"bengaluru",
    "mumbai city":"mumbai","greater mumbai":"mumbai",
    "delhi":"delhi","new delhi":"new delhi",
    "hyderabad":"hyderabad","secunderabad":"hyderabad",
    "pune city":"pune","pimpri-chinchwad":"pune",
    "chennai":"chennai","madras":"chennai",
    "kolkata":"kolkata","calcutta":"kolkata",
    "gurugram":"gurugram","gurgaon":"gurugram",
    "noida":"noida","greater noida":"greater noida",
    "ahmedabad":"ahmedabad","jaipur":"jaipur","lucknow":"lucknow","indore":"indore",
    "chandigarh":"chandigarh","kochi":"kochi","cochin":"kochi","dehradun":"dehradun",
}

def extract_city(raw_data):
    addr=raw_data.get("address",{}) if raw_data else {}
    for key in ["city","town","city_district","village","municipality","county","state_district"]:
        val=addr.get(key,"")
        if val:
            v=val.lower().strip()
            if v in CITY_ALIASES: return CITY_ALIASES[v]
            return v
    display=raw_data.get("display_name","")
    for known in CITY_ALIASES:
        if known in display.lower(): return CITY_ALIASES[known]
    return ""

def extract_area(raw_data):
    addr=raw_data.get("address",{}) if raw_data else {}
    for key in ["neighbourhood","suburb","quarter","residential","village","road","pedestrian"]:
        val=addr.get(key,"")
        if val: return val.lower().strip()
    return ""

def extract_state(raw_data):
    addr=raw_data.get("address",{}) if raw_data else {}
    return addr.get("state","")

def extract_pincode(raw_data):
    addr=raw_data.get("address",{}) if raw_data else {}
    pc=addr.get("postcode","")
    return pc if pc else "N/A"

def get_per_sqft_rate(city,area):
    city_l=city.lower().strip()
    area_l=area.lower().strip()
    base=CITY_BASE_RATES.get(city_l,CITY_BASE_RATES["default_urban"])
    area_mult=1.0
    for area_key,mult in AREA_MULTIPLIERS.items():
        if area_key in area_l or area_l in area_key:
            area_mult=mult
            break
    return int(base*area_mult)

def calculate_valuation(sqft,bedrooms,bathrooms,toilets,balconies,terrace,
                        storeroom,pooja_room,servant_qr,parking,lift,gym,
                        pool,garden,security,furnishing,prop_type,age,floor,per_sqft_rate):
    base_val=sqft*per_sqft_rate
    type_mult=PROPERTY_TYPE_MULT.get(prop_type,1.0)
    age_mult=AGE_DISCOUNT.get(age,0.88)
    floor_mult=FLOOR_MULT.get(floor,1.0)
    features={"balcony":balconies,"terrace":terrace,"storeroom":storeroom,
              "pooja_room":pooja_room,"servant_qr":servant_qr,"parking":parking,
              "lift":lift,"gym":gym,"pool":pool,"garden":garden,"security":security}
    feature_total=0
    for feat,has_feat in features.items():
        if has_feat: feature_total+=FEATURE_PREMIUMS.get(feat,0)
    if furnishing=="Fully Furnished": feature_total+=FEATURE_PREMIUMS["furnished"]
    elif furnishing=="Semi Furnished": feature_total+=FEATURE_PREMIUMS["semi_furnished"]
    room_bonus=(bedrooms*0.04)+(bathrooms*0.015)+(toilets*0.01)
    final_mult=type_mult*age_mult*floor_mult*(1+feature_total+room_bonus)
    valuation=int(base_val*final_mult)
    breakdown={
        "Base (Area x Rate)":int(base_val),
        "Property Type Adj.":int(base_val*(type_mult-1)),
        "Age Adjustment":int(base_val*type_mult*(age_mult-1)),
        "Floor Bonus":int(base_val*type_mult*age_mult*(floor_mult-1)),
        "Rooms Premium":int(base_val*type_mult*age_mult*floor_mult*room_bonus),
        "Features Premium":int(base_val*type_mult*age_mult*floor_mult*feature_total),
    }
    return valuation,breakdown

def build_map(lat,lon,address="Your Property",zoom=15):
    m=folium.Map(location=[lat,lon],zoom_start=zoom,tiles=None,control_scale=True)
    folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                     attr="Google Satellite",name="Satellite",max_zoom=21).add_to(m)
    folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                     attr="Google Maps",name="Road Map",max_zoom=21).add_to(m)
    folium.TileLayer(tiles="OpenStreetMap",name="OSM").add_to(m)
    folium.LayerControl().add_to(m)
    icon_html="""<div style="background:linear-gradient(135deg,#f5a623,#e8880a);width:36px;height:36px;
    border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:3px solid white;
    box-shadow:0 4px 15px rgba(245,166,35,0.6);"></div>"""
    marker_icon=folium.DivIcon(html=icon_html,icon_size=(36,36),icon_anchor=(18,36))
    folium.Marker([lat,lon],
        tooltip=folium.Tooltip(f"<b>📍 {address[:60]}</b>",sticky=True),
        popup=folium.Popup(f"""<div style='font-family:sans-serif;width:220px;'>
            <b style='color:#f5a623;'>📍 Property Location</b><br>
            <small>{address}</small><br><br>
            <b>Lat:</b> {lat:.5f}<br><b>Lon:</b> {lon:.5f}</div>""",max_width=250),
        icon=marker_icon).add_to(m)
    folium.Circle([lat,lon],radius=100,color="#f5a623",fill=True,
                  fill_color="#f5a623",fill_opacity=0.08,weight=2,
                  dash_array="6,4",tooltip="~100m radius").add_to(m)
    return m

def generate_floor_plan(bedrooms,bathrooms,toilets,balconies,terrace,
                        storeroom,pooja_room,servant_qr,sqft,prop_name="My Property"):
    fig,ax=plt.subplots(figsize=(14,10))
    fig.patch.set_facecolor("#0e1219")
    ax.set_facecolor("#0e1219")
    ax.set_xlim(0,100);ax.set_ylim(0,70);ax.set_aspect("equal");ax.axis("off")
    for x in range(0,101,5): ax.axvline(x,color="#1a2535",linewidth=0.4,zorder=0)
    for y in range(0,71,5): ax.axhline(y,color="#1a2535",linewidth=0.4,zorder=0)
    C_WALL="#f5a623";C_WALL_BG="#1a1000"
    C_BED="#0a2235";C_BED_BD="#4895ef"
    C_BATH="#072235";C_BATH_BD="#00c6a7"
    C_LIVING="#0a1a10";C_LIVING_BD="#2ea043"
    C_KITCHEN="#1a0a20";C_KITCHEN_BD="#a855f7"
    C_TEXT="#ffffff";C_DIM="#f5a623";C_DOOR="#f5a623"

    def draw_room(x,y,w,h,label,sublabel="",bg_col="#0a0a1a",bd_col="#f5a623",icon="",wall_thick=2):
        room=FancyBboxPatch((x,y),w,h,boxstyle="square,pad=0",
                            facecolor=bg_col,edgecolor=bd_col,linewidth=wall_thick,zorder=2)
        ax.add_patch(room)
        cx,cy=x+w/2,y+h/2
        if icon: ax.text(cx,cy+0.8,icon,ha="center",va="center",fontsize=10,color=C_TEXT,zorder=5)
        ax.text(cx,cy-(0.8 if icon else 0),label,ha="center",va="center",fontsize=7.5,
                fontweight="bold",color=C_TEXT,zorder=5,fontfamily="monospace")
        if sublabel:
            ax.text(cx,cy-2.2-(0.8 if icon else 0),sublabel,ha="center",va="center",
                    fontsize=5.5,color="#888",zorder=5,fontstyle="italic")

    def draw_door(x,y,size=3,direction="right"):
        if direction=="right":
            arc=mpatches.Arc((x,y),size,size,angle=0,theta1=0,theta2=90,color=C_DOOR,linewidth=1.2,zorder=6)
            ax.add_patch(arc);ax.plot([x,x],[y,y+size/2],color=C_DOOR,lw=1.2,zorder=6)
        elif direction=="left":
            arc=mpatches.Arc((x,y),size,size,angle=0,theta1=90,theta2=180,color=C_DOOR,linewidth=1.2,zorder=6)
            ax.add_patch(arc);ax.plot([x,x],[y,y+size/2],color=C_DOOR,lw=1.2,zorder=6)
        elif direction=="up":
            arc=mpatches.Arc((x,y),size,size,angle=0,theta1=0,theta2=90,color=C_DOOR,linewidth=1.2,zorder=6)
            ax.add_patch(arc);ax.plot([x,x+size/2],[y,y],color=C_DOOR,lw=1.2,zorder=6)

    outer=FancyBboxPatch((2,2),96,66,boxstyle="square,pad=0",
                         facecolor=C_WALL_BG,edgecolor=C_WALL,linewidth=3,zorder=1)
    ax.add_patch(outer)
    rooms=[]
    rooms.append(("LIVING ROOM","🛋",2,22,28,24,C_LIVING,C_LIVING_BD))
    rooms.append(("KITCHEN","🍳",2,2,20,18,C_KITCHEN,C_KITCHEN_BD))
    rooms.append(("DINING","🍽",22,2,16,18,C_LIVING,"#4ade80"))
    bed_labels=["MASTER BED","BED ROOM 2","BED ROOM 3","BED ROOM 4","BED ROOM 5","BED ROOM 6"]
    num_beds=min(bedrooms,6)
    if num_beds<=2:
        bed_positions=[(38,38),(60,38)][:num_beds]
        for i in range(num_beds):
            bx,by=bed_positions[i]
            rooms.append((bed_labels[i],"🛏",bx,by,20,30,C_BED,C_BED_BD))
    elif num_beds<=4:
        bed_positions=[(38,46),(60,46),(38,22),(60,22)][:num_beds]
        for i in range(num_beds):
            bx,by=bed_positions[i]
            rooms.append((bed_labels[i],"🛏",bx,by,20,22,C_BED,C_BED_BD))
    else:
        bed_positions=[(38,50),(60,50),(38,30),(60,30),(38,10),(60,10)][:num_beds]
        for i in range(num_beds):
            bx,by=bed_positions[i]
            rooms.append((bed_labels[i],"🛏",bx,by,20,18,C_BED,C_BED_BD))
    num_bath=min(bathrooms+toilets,5)
    bath_labels=["BATHROOM 1","BATHROOM 2","TOILET 1","TOILET 2","TOILET 3"]
    bath_icons=["🚿","🚿","🚽","🚽","🚽"]
    for i in range(num_bath):
        rooms.append((bath_labels[i],bath_icons[i],82,2+i*13,16,11,C_BATH,C_BATH_BD))
    if balconies>=1: rooms.append(("BALCONY 1","🌿",2,48,28,10,"#050f0a","#2ea043"))
    if balconies>=2: rooms.append(("BALCONY 2","🌿",2,58,28,10,"#050f0a","#2ea043"))
    misc_rooms=[]
    if storeroom: misc_rooms.append(("STORE ROOM","📦","#1a1008","#a78bfa"))
    if pooja_room: misc_rooms.append(("POOJA ROOM","🪔","#1a0808","#f97316"))
    if servant_qr: misc_rooms.append(("SERVANT QR","🏠","#0a0a0a","#888"))
    for i,(mlab,mic,mbg,mbd) in enumerate(misc_rooms[:3]):
        rooms.append((mlab,mic,2+i*18,60,16,8,mbg,mbd))
    for room_info in rooms:
        label,icon,rx,ry,rw,rh,rbg,rbd=room_info
        rw=min(rw,98-rx);rh=min(rh,68-ry)
        if rw>0 and rh>0:
            sqft_room=int(sqft*rw*rh/(96*66))
            draw_room(rx,ry,rw,rh,label,f"~{sqft_room} sq ft",rbg,rbd,icon)
    draw_door(28,30,3,"right");draw_door(38,54,3,"left");draw_door(82,25,3,"up")
    mx,my=(2+98)/2,0.5
    ax.annotate("",xy=(98,0.5),xytext=(2,0.5),arrowprops=dict(arrowstyle="<->",color=C_DIM,lw=0.8))
    ax.text(mx,1.5,f"Total Width ~{int(math.sqrt(sqft*1.25))} ft",fontsize=5,color=C_DIM,ha="center")
    ax.annotate("",xy=(95,67),xytext=(95,63),arrowprops=dict(arrowstyle="->",color=C_WALL,lw=2))
    ax.text(95,68,"N",ha="center",va="center",color=C_WALL,fontsize=10,fontweight="bold")
    ax.plot([3,13],[1.2,1.2],color="#888",lw=2)
    ax.plot([3,3],[0.9,1.5],color="#888",lw=1.5);ax.plot([13,13],[0.9,1.5],color="#888",lw=1.5)
    ax.text(8,0.3,"Scale",ha="center",fontsize=5,color="#888")
    ax.text(50,69.5,f"GHARMOOL ARCHITECTURAL FLOOR PLAN  -  {prop_name.upper()}",
            ha="center",va="center",fontsize=9,fontweight="bold",color=C_WALL,fontfamily="monospace")
    ax.text(50,68.5,f"Area:{sqft} sqft | {bedrooms}BHK | {bathrooms}Baths | {balconies}Balcony | {datetime.date.today()}",
            ha="center",va="center",fontsize=6,color="#888",fontfamily="monospace")
    legend_items=[mpatches.Patch(color=C_BED_BD,label="Bedrooms"),
                  mpatches.Patch(color=C_BATH_BD,label="Baths"),
                  mpatches.Patch(color=C_LIVING_BD,label="Living/Dining"),
                  mpatches.Patch(color=C_KITCHEN_BD,label="Kitchen")]
    ax.legend(handles=legend_items,loc="lower right",fontsize=6,fancybox=True,
              facecolor="#0e1219",edgecolor=C_WALL,labelcolor="white",framealpha=0.9)
    plt.tight_layout(pad=0.3)
    buf=io.BytesIO()
    fig.savefig(buf,format="png",dpi=160,bbox_inches="tight",facecolor="#0e1219",edgecolor="none")
    buf.seek(0);plt.close(fig)
    return buf

def generate_price_forecast(current_val,city,years=15):
    city_l=city.lower().strip()
    base_rate=CITY_GROWTH_RATES.get(city_l,CITY_GROWTH_RATES["default"])
    dev_idx=CITY_DEVELOPMENT_INDEX.get(city_l,CITY_DEVELOPMENT_INDEX["default"])
    dev_boost=(dev_idx["metro"]+dev_idx["it_hub"]+dev_idx["infra"]+dev_idx["startup"])/400
    adj_rate=base_rate*(0.7+dev_boost*0.6)
    now=datetime.date.today().year
    year_list=list(range(now,now+years+1))
    optimistic=[current_val*((1+(adj_rate*1.35)/100)**i) for i in range(years+1)]
    base_case=[current_val*((1+adj_rate/100)**i) for i in range(years+1)]
    conservative=[current_val*((1+(adj_rate*0.65)/100)**i) for i in range(years+1)]
    return year_list,optimistic,base_case,conservative,adj_rate

def build_forecast_chart(year_list,optimistic,base_case,conservative,current_val,city):
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=year_list,y=optimistic,name="Optimistic",
        line=dict(color="#06d6a0",width=2.5,dash="dot"),fill="tonexty",fillcolor="rgba(6,214,160,0.06)"))
    fig.add_trace(go.Scatter(x=year_list,y=base_case,name="Base Case",
        line=dict(color="#f5a623",width=3),fill="tonexty",fillcolor="rgba(245,166,35,0.08)"))
    fig.add_trace(go.Scatter(x=year_list,y=conservative,name="Conservative",
        line=dict(color="#ff4d6d",width=2.5,dash="dash")))
    fig.add_hline(y=current_val,line_dash="dot",line_color="#888",
                  annotation_text="Current Value",annotation_position="top left",annotation_font_color="#888")
    for yi,yr in enumerate(year_list):
        if yr in [year_list[0]+5,year_list[0]+10,year_list[-1]]:
            fig.add_annotation(x=yr,y=base_case[yi],text=f"Rs.{base_case[yi]/1e7:.1f}Cr",
                showarrow=True,arrowhead=2,arrowcolor="#f5a623",font=dict(color="#f5a623",size=11),
                bgcolor="rgba(14,18,25,0.9)",bordercolor="#f5a623",borderwidth=1,borderpad=4)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaf0",family="Inter"),
        xaxis=dict(title="Year",showgrid=True,gridcolor="rgba(255,255,255,0.05)",color="#7a8499"),
        yaxis=dict(title="Property Value (Rs.)",showgrid=True,gridcolor="rgba(245,166,35,0.08)",
                   color="#7a8499",tickformat=",.0f"),
        legend=dict(bgcolor="rgba(14,18,25,0.9)",bordercolor="#f5a623",borderwidth=1,font=dict(color="#e8eaf0")),
        height=420,margin=dict(t=30,b=40,l=20,r=20),hovermode="x unified",
        hoverlabel=dict(bgcolor="#0e1219",bordercolor="#f5a623",font_color="#e8eaf0"))
    return fig

def build_development_radar(city):
    city_l=city.lower()
    idx=CITY_DEVELOPMENT_INDEX.get(city_l,CITY_DEVELOPMENT_INDEX["default"])
    categories=["Metro Connectivity","IT Hub Score","Infrastructure","Startup Ecosystem"]
    values=[idx["metro"],idx["it_hub"],idx["infra"],idx["startup"]]
    fig=go.Figure(go.Scatterpolar(r=values+[values[0]],theta=categories+[categories[0]],
        fill="toself",fillcolor="rgba(245,166,35,0.12)",line=dict(color="#f5a623",width=2),
        marker=dict(size=7,color="#f5a623"),name=city))
    fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(visible=True,range=[0,100],color="#7a8499",gridcolor="rgba(255,255,255,0.07)"),
        angularaxis=dict(color="#e8eaf0")),paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaf0",family="Inter"),
        title=dict(text=f"Development Index - {city.title()}",font=dict(color="#f5a623",size=14)),
        height=340,margin=dict(t=50,b=10))
    return fig

for key,default in {"geo_result":None,"valuation":0,"per_sqft":0,"city_name":"",
                    "area_name":"","full_address":"","state_name":"","pincode":""}.items():
    if key not in st.session_state: st.session_state[key]=default

st.markdown("""
<div class="hero">
  <div class="badge">🏡 India's Smart Property Intelligence Platform</div>
  <div class="hero-title">GharMool</div>
  <div class="hero-sub">Location-aware valuation · Architectural floor plans · 15-year forecasts · Live map</div>
</div>
""",unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5=st.tabs(["📍 Location & Map","🏠 Property Details & Value","🏗️ Floor Plan","📈 Price Forecast","📊 Market Intelligence"])

with tab1:
    st.markdown("### 📍 Enter Your Property Location")
    col_inp,col_map=st.columns([1.1,2])
    with col_inp:
        st.markdown('<div class="gcard">',unsafe_allow_html=True)
        st.markdown('<div class="gcard-title">🔍 Location Search</div>',unsafe_allow_html=True)
        search_method=st.radio("Search by",["📝 Address / Locality","📌 Lat / Lon"],horizontal=True,label_visibility="collapsed")
        if search_method=="📝 Address / Locality":
            addr_input=st.text_input("Enter Address",placeholder="e.g. Indiranagar, Bangalore",key="addr_input")
            if st.button("🔍 Find on Map",use_container_width=True):
                if addr_input.strip():
                    with st.spinner("Locating..."):
                        result=geocode_address(addr_input.strip())
                    if result:
                        st.session_state.geo_result=result
                        raw=result.get("raw",{})
                        st.session_state.city_name=extract_city(raw)
                        st.session_state.area_name=extract_area(raw)
                        st.session_state.full_address=result.get("full_address","")
                        st.session_state.state_name=extract_state(raw)
                        st.session_state.pincode=extract_pincode(raw)
                        st.session_state.per_sqft=get_per_sqft_rate(st.session_state.city_name,st.session_state.area_name)
                        st.success("✅ Location found!")
                    else:
                        st.error("❌ Could not find. Try specific address.")
        else:
            c1,c2=st.columns(2)
            lat_in=c1.number_input("Latitude",value=12.9716,format="%.5f")
            lon_in=c2.number_input("Longitude",value=77.5946,format="%.5f")
            if st.button("📌 Fetch Address",use_container_width=True):
                with st.spinner("Reverse geocoding..."):
                    result=reverse_geocode(lat_in,lon_in)
                if result:
                    raw=result.get("raw",{})
                    st.session_state.geo_result={"lat":lat_in,"lon":lon_in,"full_address":result["full_address"],"raw":raw}
                    st.session_state.city_name=extract_city(raw)
                    st.session_state.area_name=extract_area(raw)
                    st.session_state.full_address=result["full_address"]
                    st.session_state.state_name=extract_state(raw)
                    st.session_state.pincode=extract_pincode(raw)
                    st.session_state.per_sqft=get_per_sqft_rate(st.session_state.city_name,st.session_state.area_name)
                    st.success("✅ Address found!")
                else:
                    st.error("❌ Could not reverse geocode.")
        st.markdown("</div>",unsafe_allow_html=True)
        if st.session_state.geo_result:
            gr=st.session_state.geo_result
            st.markdown(f"""
            <div class="gcard" style="border-color:rgba(0,198,167,0.3);">
              <div class="gcard-title">📋 Detected Address</div>
              <div class="info-row"><span class="info-label">📍 Area</span><span class="info-val">{st.session_state.area_name.title() or '—'}</span></div>
              <div class="info-row"><span class="info-label">🏙️ City</span><span class="info-val">{st.session_state.city_name.title() or '—'}</span></div>
              <div class="info-row"><span class="info-label">🗺️ State</span><span class="info-val">{st.session_state.state_name or '—'}</span></div>
              <div class="info-row"><span class="info-label">📮 PIN</span><span class="info-val">{st.session_state.pincode or '—'}</span></div>
              <div class="info-row"><span class="info-label">🌐 Lat/Lon</span><span class="info-val">{gr.get('lat',0):.4f}, {gr.get('lon',0):.4f}</span></div>
              <div class="info-row" style="margin-top:0.8rem;border-top:1px solid rgba(245,166,35,0.15);padding-top:0.8rem;">
                <span class="info-label">💰 Est. Rate (2024)</span>
                <span style="color:#f5a623;font-weight:800;font-size:1.1rem;">Rs.{st.session_state.per_sqft:,} / sq ft</span>
              </div>
            </div>""",unsafe_allow_html=True)
            gmaps_q=urllib.parse.quote(st.session_state.full_address)
            lat_g,lon_g=gr.get("lat",0),gr.get("lon",0)
            st.markdown(f"""
            <div class="gcard" style="padding:1rem;">
              <div class="gcard-title">🔗 Open in Google Maps</div>
              <div style="display:flex;gap:0.6rem;flex-wrap:wrap;">
                <a href="https://www.google.com/maps/search/?api=1&query={gmaps_q}" target="_blank"
                   style="background:rgba(66,133,244,0.15);border:1px solid #4285f4;color:#4285f4;
                          padding:6px 14px;border-radius:8px;font-size:0.82rem;text-decoration:none;">🗺️ Maps</a>
                <a href="https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat_g},{lon_g}" target="_blank"
                   style="background:rgba(234,67,53,0.15);border:1px solid #ea4335;color:#ea4335;
                          padding:6px 14px;border-radius:8px;font-size:0.82rem;text-decoration:none;">🚶 Street View</a>
                <a href="https://www.google.com/maps/search/schools+near/@{lat_g},{lon_g},15z" target="_blank"
                   style="background:rgba(0,198,167,0.15);border:1px solid #00c6a7;color:#00c6a7;
                          padding:6px 14px;border-radius:8px;font-size:0.82rem;text-decoration:none;">🏥 Nearby</a>
                <a href="https://www.google.com/maps/dir/?api=1&destination={lat_g},{lon_g}" target="_blank"
                   style="background:rgba(245,166,35,0.15);border:1px solid #f5a623;color:#f5a623;
                          padding:6px 14px;border-radius:8px;font-size:0.82rem;text-decoration:none;">🧭 Directions</a>
              </div>
            </div>""",unsafe_allow_html=True)
    with col_map:
        if st.session_state.geo_result:
            gr=st.session_state.geo_result
            m=build_map(gr["lat"],gr["lon"],address=st.session_state.full_address)
            st.markdown('<div style="border-radius:16px;overflow:hidden;border:1px solid rgba(245,166,35,0.2);">',unsafe_allow_html=True)
            st_folium(m,width="100%",height=500,returned_objects=[])
            st.markdown("</div>",unsafe_allow_html=True)
            st.markdown(f"""<div style="background:rgba(14,18,25,0.9);border:1px solid rgba(245,166,35,0.2);
                border-radius:10px;padding:0.8rem 1rem;margin-top:0.8rem;font-size:0.82rem;color:#7a8499;">
              📍 <strong style="color:#e8eaf0;">{st.session_state.full_address}</strong></div>""",unsafe_allow_html=True)
        else:
            m_default=folium.Map(location=[20.5937,78.9629],zoom_start=5,
                tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",attr="Google Satellite")
            st.markdown('<div style="border-radius:16px;overflow:hidden;border:1px solid rgba(245,166,35,0.15);">',unsafe_allow_html=True)
            st_folium(m_default,width="100%",height=500,returned_objects=[])
            st.markdown("</div>",unsafe_allow_html=True)
            st.info("👆 Enter your address above to pin your property on the map.")

with tab2:
    if not st.session_state.geo_result:
        st.warning("⚠️ Please go to 📍 Location & Map tab first and search your address.")
    else:
        st.markdown(f"### 🏠 Property Details — {st.session_state.city_name.title()}")
        st.markdown(f"<p style='color:#7a8499;'>Market rate: <strong style='color:#f5a623;'>Rs.{st.session_state.per_sqft:,}/sqft</strong></p>",unsafe_allow_html=True)
        col_form,col_result=st.columns([1.3,1.7])
        with col_form:
            with st.form("property_form"):
                st.markdown("**📐 Area & Type**")
                c1,c2=st.columns(2)
                sqft=c1.number_input("Total Area (sq ft)",100,50000,1200,50)
                prop_name=c2.text_input("Property Name","My Home")
                prop_type=st.selectbox("Property Type",list(PROPERTY_TYPE_MULT.keys()))
                c1,c2=st.columns(2)
                age=c1.selectbox("Age of Property",list(AGE_DISCOUNT.keys()))
                floor=c2.selectbox("Floor",list(FLOOR_MULT.keys()))
                st.markdown("**🛏️ Rooms**")
                c1,c2,c3=st.columns(3)
                bedrooms=c1.number_input("Bedrooms",0,20,3,1)
                bathrooms=c2.number_input("Bathrooms",0,15,2,1)
                toilets=c3.number_input("Toilets",0,15,1,1)
                st.markdown("**🌿 Extra Spaces**")
                c1,c2,c3=st.columns(3)
                balconies=c1.number_input("Balconies",0,10,1,1)
                terrace=c2.checkbox("Terrace",value=False)
                storeroom=c3.checkbox("Store Room",value=False)
                c1,c2,c3=st.columns(3)
                pooja_room=c1.checkbox("Pooja Room",value=False)
                servant_qr=c2.checkbox("Servant Qtr.",value=False)
                garden=c3.checkbox("Garden/Lawn",value=False)
                st.markdown("**🏢 Amenities**")
                c1,c2,c3=st.columns(3)
                parking=c1.checkbox("Parking",value=True)
                lift=c2.checkbox("Lift/Elevator",value=False)
                gym=c3.checkbox("Gym",value=False)
                c1,c2=st.columns(2)
                pool=c1.checkbox("Swimming Pool",value=False)
                security=c2.checkbox("24x7 Security",value=True)
                furnishing=st.selectbox("Furnishing",["Unfurnished","Semi Furnished","Fully Furnished"])
                rate_override=st.number_input("Custom Rate (Rs./sqft, 0=auto)",0,500000,0,500)
                submitted=st.form_submit_button("💰 Calculate Valuation",use_container_width=True)
        with col_result:
            if submitted:
                use_rate=rate_override if rate_override>0 else st.session_state.per_sqft
                val,breakdown=calculate_valuation(sqft,bedrooms,bathrooms,toilets,balconies,
                    terrace,storeroom,pooja_room,servant_qr,parking,lift,gym,
                    pool,garden,security,furnishing,prop_type,age,floor,use_rate)
                st.session_state.valuation=val
                st.session_state["prop_sqft"]=sqft;st.session_state["prop_beds"]=bedrooms
                st.session_state["prop_baths"]=bathrooms;st.session_state["prop_toilets"]=toilets
                st.session_state["prop_balconies"]=balconies;st.session_state["prop_terrace"]=terrace
                st.session_state["prop_store"]=storeroom;st.session_state["prop_pooja"]=pooja_room
                st.session_state["prop_servant"]=servant_qr;st.session_state["prop_name"]=prop_name
                crore=val/1e7;lac=(val%1e7)/1e5;per_sqft_eff=int(val/sqft)
                st.markdown(f"""
                <div class="val-banner">
                  <div style="font-size:0.85rem;color:#7a8499;margin-bottom:0.4rem;">ESTIMATED MARKET VALUE</div>
                  <div class="val-price">Rs.{val:,}</div>
                  <div style="font-size:1.1rem;color:#e8eaf0;margin:0.3rem 0;">~ {crore:.2f} Crore | {int(crore)} Cr {int(lac)} Lac</div>
                  <div style="font-size:0.85rem;color:#7a8499;margin-top:0.5rem;">
                    📍 {st.session_state.area_name.title()}, {st.session_state.city_name.title()} · Rs.{per_sqft_eff:,}/sqft effective
                  </div>
                </div>""",unsafe_allow_html=True)
                st.markdown("<br>",unsafe_allow_html=True)
                c1,c2,c3,c4=st.columns(4)
                for col,ico,val_k,lab_k in [(c1,"📐",f"{sqft:,}","Area (sqft)"),(c2,"💰",f"Rs.{use_rate:,}","Rate/sqft"),(c3,"🛏",f"{bedrooms}BHK","Config"),(c4,"📅",age.split()[0],"Age")]:
                    col.markdown(f'<div class="kpi"><div class="kpi-icon">{ico}</div><div class="kpi-val">{val_k}</div><div class="kpi-lab">{lab_k}</div></div>',unsafe_allow_html=True)
                st.markdown("<br>",unsafe_allow_html=True)
                bd_labels=list(breakdown.keys());bd_values=[max(0,v) for v in breakdown.values()]
                colors_bd=["#4895ef","#f5a623","#ff4d6d","#00c6a7","#a855f7","#2ea043"]
                fig_bd=go.Figure(go.Bar(x=bd_labels,y=bd_values,marker_color=colors_bd,
                    text=[f"Rs.{v:,}" if v>0 else "—" for v in bd_values],textposition="outside",textfont=dict(color="#e8eaf0",size=10)))
                fig_bd.update_layout(title="💡 Valuation Breakdown",paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#e8eaf0"),
                    xaxis=dict(showgrid=False,color="#7a8499",tickangle=-20),
                    yaxis=dict(gridcolor="rgba(245,166,35,0.07)",color="#7a8499"),
                    height=300,margin=dict(t=40,b=60),title_font=dict(color="#f5a623"))
                st.plotly_chart(fig_bd,use_container_width=True)
                monthly_rent=int(val*0.0025);annual_yield=round((monthly_rent*12/val)*100,2)
                st.markdown(f"""
                <div class="gcard" style="border-color:rgba(0,198,167,0.3);">
                  <div class="gcard-title">🏷️ Rental & Yield</div>
                  <div class="info-row"><span class="info-label">Monthly Rent</span><span class="info-val" style="color:#00c6a7;">Rs.{monthly_rent:,}</span></div>
                  <div class="info-row"><span class="info-label">Annual Yield</span><span class="info-val" style="color:#00c6a7;">{annual_yield}%</span></div>
                  <div class="info-row"><span class="info-label">Annual Income</span><span class="info-val">Rs.{monthly_rent*12:,}</span></div>
                  <div class="info-row"><span class="info-label">Break-even</span><span class="info-val">~{int(val/(monthly_rent*12))} years</span></div>
                </div>""",unsafe_allow_html=True)
            elif st.session_state.valuation>0:
                val=st.session_state.valuation;crore=val/1e7
                st.markdown(f'<div class="val-banner"><div style="font-size:0.85rem;color:#7a8499;">LAST VALUE</div><div class="val-price">Rs.{val:,}</div><div style="font-size:1rem;color:#e8eaf0;">~ {crore:.2f} Crore</div></div>',unsafe_allow_html=True)
                st.info("Fill form and click Calculate to refresh.")
            else:
                st.info("👈 Fill property details and click Calculate Valuation.")

with tab3:
    st.markdown("### 🏗️ Architectural Floor Plan Generator")
    col_fp1,col_fp2=st.columns([1,2.5])
    with col_fp1:
        st.markdown('<div class="gcard">',unsafe_allow_html=True)
        st.markdown('<div class="gcard-title">⚙️ Floor Plan Settings</div>',unsafe_allow_html=True)
        fp_beds=st.number_input("Bedrooms",0,8,st.session_state.get("prop_beds",3),1,key="fp_beds")
        fp_baths=st.number_input("Bathrooms",0,6,st.session_state.get("prop_baths",2),1,key="fp_baths")
        fp_toilets=st.number_input("Toilets",0,6,st.session_state.get("prop_toilets",1),1,key="fp_toilets")
        fp_balconies=st.number_input("Balconies",0,4,st.session_state.get("prop_balconies",1),1,key="fp_balconies")
        fp_terrace=st.checkbox("Terrace",value=st.session_state.get("prop_terrace",False),key="fp_terrace")
        fp_store=st.checkbox("Store Room",value=st.session_state.get("prop_store",False),key="fp_store")
        fp_pooja=st.checkbox("Pooja Room",value=st.session_state.get("prop_pooja",False),key="fp_pooja")
        fp_servant=st.checkbox("Servant Qtr",value=st.session_state.get("prop_servant",False),key="fp_servant")
        fp_sqft=st.number_input("Total Area (sqft)",200,50000,st.session_state.get("prop_sqft",1200),100,key="fp_sqft")
        fp_name=st.text_input("Property Name",st.session_state.get("prop_name","My Property"),key="fp_name")
        gen_btn=st.button("🏗️ Generate Floor Plan",use_container_width=True)
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown('<div class="gcard" style="font-size:0.8rem;color:#7a8499;"><div class="gcard-title">📖 Legend</div>🔵 Bedrooms &nbsp; 🟢 Living<br>🟣 Kitchen &nbsp; 🩵 Baths<br>🧭 N = North</div>',unsafe_allow_html=True)
    with col_fp2:
        if gen_btn or st.session_state.get("floor_plan_generated"):
            with st.spinner("🏗️ Generating..."):
                buf=generate_floor_plan(fp_beds,fp_baths,fp_toilets,fp_balconies,
                    fp_terrace,fp_store,fp_pooja,fp_servant,fp_sqft,fp_name)
                st.session_state["floor_plan_generated"]=True
                st.session_state["floor_plan_buf"]=buf.getvalue()
        if st.session_state.get("floor_plan_buf"):
            img_bytes=st.session_state["floor_plan_buf"]
            st.image(img_bytes,use_container_width=True,caption="GharMool Architectural Floor Plan")
            st.download_button("⬇️ Download Floor Plan (PNG)",data=img_bytes,
                file_name=f"GharMool_FloorPlan_{fp_name.replace(' ','_')}.png",mime="image/png",use_container_width=True)
            st.markdown("""<div class="gcard" style="border-color:rgba(0,198,167,0.3);margin-top:1rem;">
              <div class="gcard-title">💡 Architect Tips</div>
              <div style="font-size:0.85rem;color:#e8eaf0;line-height:1.7;">
                🌞 <strong>Orientation:</strong> Living room facing East for morning sunlight.<br>
                🌬️ <strong>Ventilation:</strong> Cross-ventilation — windows on opposite walls.<br>
                🚿 <strong>Wet Areas:</strong> Group bathrooms back-to-back to reduce plumbing cost.<br>
                🍳 <strong>Kitchen:</strong> L-shaped or U-shaped layout is most efficient.<br>
                🌿 <strong>Balcony:</strong> North-facing stays cooler in Indian summers.<br>
                💡 <strong>Vastu:</strong> Master bed in South-West, Kitchen in South-East.
              </div></div>""",unsafe_allow_html=True)
        else:
            st.markdown("""<div style="border:2px dashed rgba(245,166,35,0.25);border-radius:18px;
                height:400px;display:flex;align-items:center;justify-content:center;
                flex-direction:column;color:#7a8499;">
              <div style="font-size:3rem;margin-bottom:1rem;">🏗️</div>
              <div style="font-size:1.1rem;font-weight:600;">Configure rooms and click Generate</div>
              <div style="font-size:0.85rem;margin-top:0.5rem;">Engineer-quality floor plan will appear here</div>
            </div>""",unsafe_allow_html=True)

with tab4:
    st.markdown("### 📈 15-Year Property Price Forecast")
    city_for_fc=st.session_state.city_name if st.session_state.city_name else "bengaluru"
    val_for_fc=st.session_state.valuation if st.session_state.valuation>0 else 8000000
    col_fc1,col_fc2=st.columns([1,2.5])
    with col_fc1:
        st.markdown('<div class="gcard">',unsafe_allow_html=True)
        st.markdown('<div class="gcard-title">⚙️ Forecast Settings</div>',unsafe_allow_html=True)
        fc_val=st.number_input("Current Value (Rs.)",100000,1000000000,max(val_for_fc,2000000),100000)
        fc_city=st.text_input("City",city_for_fc.title() or "Bangalore")
        fc_years=st.slider("Forecast Years",5,15,15)
        st.button("📊 Run Forecast",use_container_width=True)
        st.markdown("</div>",unsafe_allow_html=True)
        growth_r=CITY_GROWTH_RATES.get(fc_city.lower().strip(),CITY_GROWTH_RATES["default"])
        st.markdown(f"""<div class="gcard" style="border-color:rgba(0,198,167,0.3);">
          <div class="gcard-title">📊 City Growth Data</div>
          <div class="info-row"><span class="info-label">Avg CAGR</span><span class="info-val" style="color:#00c6a7;">{growth_r:.1f}%</span></div>
          <div class="info-row"><span class="info-label">Tier</span><span class="info-val">{"Tier 1" if growth_r>=9 else "Tier 2" if growth_r>=7.5 else "Tier 3"}</span></div>
          <div class="info-row"><span class="info-label">10yr Projection</span><span class="info-val">Rs.{int(fc_val*(1+growth_r/100)**10):,}</span></div>
        </div>""",unsafe_allow_html=True)
    with col_fc2:
        yr_list,opt,base,cons,adj_r=generate_price_forecast(fc_val,fc_city.strip(),fc_years)
        fig_fc=build_forecast_chart(yr_list,opt,base,cons,fc_val,fc_city)
        st.plotly_chart(fig_fc,use_container_width=True)
        rows=[]
        for i,yr in enumerate(yr_list):
            if i%3==0 or i==len(yr_list)-1:
                rows.append({"Year":yr,"Conservative":f"Rs.{int(cons[i]):,}","Base Case":f"Rs.{int(base[i]):,}",
                             "Optimistic":f"Rs.{int(opt[i]):,}","Gain(Base)":f"+{int((base[i]/fc_val-1)*100)}%"})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

with tab5:
    st.markdown("### 📊 Market Intelligence & Development Index")
    city_mi=st.session_state.city_name if st.session_state.city_name else "bengaluru"
    col_mi1,col_mi2=st.columns([1.5,2])
    with col_mi1:
        st.plotly_chart(build_development_radar(city_mi),use_container_width=True)
        compare_cities=["mumbai","delhi","bengaluru","hyderabad","pune","chennai","gurugram","kolkata","ahmedabad","jaipur"]
        rates_cmp=[CITY_BASE_RATES.get(c,3000) for c in compare_cities]
        fig_cmp=go.Figure(go.Bar(x=[c.title() for c in compare_cities],y=rates_cmp,
            marker=dict(color=rates_cmp,colorscale=[[0,"#ff4d6d"],[0.5,"#f5a623"],[1,"#00c6a7"]]),
            text=[f"Rs.{r:,}" for r in rates_cmp],textposition="outside",textfont=dict(size=9,color="#e8eaf0")))
        fig_cmp.add_hline(y=st.session_state.per_sqft if st.session_state.per_sqft>0 else 8500,
            line_dash="dot",line_color="#f5a623",annotation_text="Your Location",annotation_font_color="#f5a623")
        fig_cmp.update_layout(title="💹 Base Rate by City (Rs./sqft)",paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#e8eaf0"),
            xaxis=dict(showgrid=False,color="#7a8499",tickangle=-30),
            yaxis=dict(gridcolor="rgba(245,166,35,0.07)",color="#7a8499"),
            height=340,margin=dict(t=40,b=80),title_font=dict(color="#f5a623"))
        st.plotly_chart(fig_cmp,use_container_width=True)
    with col_mi2:
        area_keys=["Premium (2x+)","Good Locality (1.5x)","Standard (1x)","Developing (0.8x)"]
        area_mults=[2.0,1.5,1.0,0.8]
        ptype_keys=list(PROPERTY_TYPE_MULT.keys())[:6]
        ptype_mults=[PROPERTY_TYPE_MULT[k] for k in ptype_keys]
        base_r=st.session_state.per_sqft if st.session_state.per_sqft>0 else 8500
        sqft_ref=st.session_state.get("prop_sqft",1200)
        z_data=[[int(base_r*am*pm*sqft_ref/1e5) for pm in ptype_mults] for am in area_mults]
        fig_hm=go.Figure(go.Heatmap(z=z_data,x=[k.split("/")[0].strip()[:18] for k in ptype_keys],y=area_keys,
            colorscale=[[0,"#0a0a1a"],[0.4,"#7a2040"],[0.7,"#d4a000"],[1,"#00c6a7"]],
            text=[[f"Rs.{v}L" for v in row] for row in z_data],texttemplate="%{text}",
            textfont=dict(size=10,color="#fff"),
            hovertemplate="Area:<b>%{y}</b><br>Type:<b>%{x}</b><br>Est:<b>Rs.%{z}L</b><extra></extra>",
            colorbar=dict(title="Lakhs",thickness=12,tickfont=dict(color="#e8eaf0"),titlefont=dict(color="#e8eaf0"))))
        fig_hm.update_layout(title=f"🔥 Value Matrix — {sqft_ref} sqft in {city_mi.title()} (Rs. Lakhs)",
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#e8eaf0"),
            xaxis=dict(color="#7a8499",tickangle=-20),yaxis=dict(color="#7a8499"),
            height=340,margin=dict(t=50,b=60),title_font=dict(color="#f5a623"))
        st.plotly_chart(fig_hm,use_container_width=True)
        cities_gr=["bengaluru","hyderabad","pune","mumbai","delhi","chennai","kolkata","ahmedabad","dehradun","kochi"]
        gr_vals=[CITY_GROWTH_RATES.get(c,7.5) for c in cities_gr]
        fig_gr=go.Figure(go.Bar(x=[c.title() for c in cities_gr],y=gr_vals,
            marker=dict(color=gr_vals,colorscale=[[0,"#ff4d6d"],[0.5,"#f5a623"],[1,"#06d6a0"]]),
            text=[f"{v:.1f}%" for v in gr_vals],textposition="outside",textfont=dict(size=10,color="#e8eaf0")))
        fig_gr.update_layout(title="📈 Avg Annual Appreciation by City (CAGR)",paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#e8eaf0"),
            xaxis=dict(showgrid=False,color="#7a8499",tickangle=-30),
            yaxis=dict(gridcolor="rgba(245,166,35,0.07)",color="#7a8499",range=[0,max(gr_vals)*1.2]),
            height=300,margin=dict(t=40,b=80),title_font=dict(color="#f5a623"))
        st.plotly_chart(fig_gr,use_container_width=True)

st.markdown("---")
st.markdown("""<div style="text-align:center;color:#7a8499;font-size:0.82rem;padding:1rem;">
  🏡 <strong style="color:#f5a623;">GharMool</strong> — India's Smart Property Intelligence Platform |
  Powered by OpenStreetMap · Nominatim · Plotly · Matplotlib |
  <em>Valuations are estimates — consult a registered valuer for official assessment</em>
</div>""",unsafe_allow_html=True)
