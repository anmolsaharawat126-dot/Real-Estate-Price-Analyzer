import streamlit as st
import pandas as pd
import numpy as np
    "📐 3D Market Space",
    "⚖️ Option Comparator",
    "💰 Loan & ROI Matrix",
    "📜 Valuation Archives"
    "📜 Valuation Archives",
    "🏛️ Tax & Costs",
    "🤝 Deal Negotiator",
    "🔥 Investment Heatmap",
    "🏆 Certificate"
]
cols = st.columns(5)
cols = st.columns(len(nav_buttons))
for index, tab_name in enumerate(nav_buttons):
    is_active = (st.session_state.current_view == tab_name)
    btn_text = f"⚜️ {tab_name}" if is_active else tab_name
                save_records([])
                st.rerun()
# ═════════════════════════════════════════════════════════════════════════════
# TAB 6: STATE-WISE TAX & CLOSING COST CALCULATOR
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_view == "🏛️ Tax & Costs":
    st.markdown("<h2 style='color:#d4af37;'>🏛️ State-wise Tax & Closing Cost Calculator</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8a99ad;'>Compute all government charges, duties, and on-road property price for your selected Indian metro.</p>", unsafe_allow_html=True)
    STATE_TAX_DATA = {
        "Mumbai (Maharashtra)": {"stamp": 6.0, "reg": 1.0, "gst_ready": 5.0, "gst_uc": 12.0, "metro": "MMRDA Cess: 1%"},
        "Delhi (NCT)": {"stamp": 6.0, "reg": 1.0, "gst_ready": 5.0, "gst_uc": 12.0, "metro": "DMRC Surcharge: 0.5%"},
        "Gurugram (Haryana)": {"stamp": 7.0, "reg": 1.0, "gst_ready": 5.0, "gst_uc": 12.0, "metro": "Haryana Urban Dev: 0.5%"},
        "Bangalore (Karnataka)": {"stamp": 5.6, "reg": 1.0, "gst_ready": 5.0, "gst_uc": 12.0, "metro": "BBMP Cess: 0.5%"},
        "Hyderabad (Telangana)": {"stamp": 4.0, "reg": 0.5, "gst_ready": 5.0, "gst_uc": 12.0, "metro": "GHMC Surcharge: 0.5%"},
        "Chennai (Tamil Nadu)": {"stamp": 7.0, "reg": 1.0, "gst_ready": 5.0, "gst_uc": 12.0, "metro": "CMDA Levy: 0.5%"},
        "Pune (Maharashtra)": {"stamp": 6.0, "reg": 1.0, "gst_ready": 5.0, "gst_uc": 12.0, "metro": "PMC Cess: 1%"},
    }
    col_tc1, col_tc2 = st.columns([1.2, 1.8])
    with col_tc1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**📍 Property Details**")
        tax_city = st.selectbox("Select City / State", list(STATE_TAX_DATA.keys()), key="tax_city")
        tax_price = st.number_input("Base Property Price (₹)", min_value=500000, max_value=500000000, value=8500000, step=100000, key="tax_price")
        prop_status = st.radio("Property Status", ["Ready-to-Move", "Under Construction"], horizontal=True, key="tax_status")
        brokerage_pct = st.slider("Brokerage % (negotiable)", 0.0, 3.0, 1.0, 0.1, key="tax_brokerage")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_tc2:
        td = STATE_TAX_DATA[tax_city]
        stamp_amt   = tax_price * td["stamp"] / 100
        reg_amt     = tax_price * td["reg"] / 100
        gst_rate    = td["gst_ready"] if prop_status == "Ready-to-Move" else td["gst_uc"]
        gst_amt     = tax_price * gst_rate / 100
        broker_amt  = tax_price * brokerage_pct / 100
        legal_misc  = tax_price * 0.005  # 0.5% fixed legal/misc
        total_extra = stamp_amt + reg_amt + gst_amt + broker_amt + legal_misc
        on_road     = tax_price + total_extra
        rows_data = [
            ("🏠 Base Property Price",     tax_price,    "#e0f0ff"),
            (f"📝 Stamp Duty ({td['stamp']}%)", stamp_amt, "#f77f00"),
            (f"📋 Registration Fee ({td['reg']}%)", reg_amt, "#f77f00"),
            (f"🧾 GST ({gst_rate}% – {prop_status})", gst_amt, "#ef476f"),
            (f"🤝 Brokerage ({brokerage_pct}%)",  broker_amt, "#d4af37"),
            ("⚖️ Legal / Misc (0.5%)",     legal_misc,   "#8a99ad"),
            ("🔖 " + td["metro"],          0,            "#8a99ad"),
        ]
        table_rows = "".join([
            f"<tr><td style='padding:8px 12px; color:{c};'>{n}</td><td style='padding:8px 12px; text-align:right; color:{c}; font-weight:600;'>₹{int(v):,}</td></tr>"
            for n, v, c in rows_data
        ])
        st.markdown(f"""
        <div class="glass-card">
          <div style='font-size:1.1rem; font-weight:700; color:#d4af37; margin-bottom:1rem;'>💰 Cost Breakdown — {tax_city}</div>
          <table style='width:100%; border-collapse:collapse;'>
            <thead>
              <tr style='border-bottom:1px solid rgba(212,175,55,0.3);'>
                <th style='padding:8px 12px; text-align:left; color:#8a99ad; font-weight:600;'>Charge Head</th>
                <th style='padding:8px 12px; text-align:right; color:#8a99ad; font-weight:600;'>Amount</th>
              </tr>
            </thead>
            <tbody>{table_rows}</tbody>
          </table>
          <hr style='border-color:rgba(212,175,55,0.2); margin:1rem 0;'>
          <div style='display:flex; justify-content:space-between; align-items:center;'>
            <div style='font-size:1rem; color:#8a99ad;'>Total Extra Charges</div>
            <div style='font-size:1.2rem; font-weight:700; color:#ef476f;'>₹{int(total_extra):,}</div>
          </div>
          <div style='display:flex; justify-content:space-between; align-items:center; margin-top:0.8rem; padding:1rem; background:rgba(212,175,55,0.08); border-radius:12px; border:1px solid rgba(212,175,55,0.3);'>
            <div style='font-size:1.1rem; color:#d4af37; font-weight:700;'>🏆 On-Road Property Price</div>
            <div style='font-size:1.8rem; font-weight:800; color:#d4af37;'>₹{int(on_road):,}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        # Donut chart
        labels = ["Base Price", "Stamp Duty", "Registration", "GST", "Brokerage", "Legal/Misc"]
        values = [tax_price, stamp_amt, reg_amt, gst_amt, broker_amt, legal_misc]
        colors = ["#1a1f35", "#f77f00", "#ef476f", "#d4af37", "#00f5d4", "#8a99ad"]
        fig_donut = go.Figure(go.Pie(
            labels=labels, values=values, hole=0.55,
            marker=dict(colors=colors, line=dict(color="#050609", width=2)),
            textinfo="percent", textfont=dict(color="#fff", size=11),
            hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>",
        ))
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e0f4ff"),
            annotations=[dict(text=f"₹{int(on_road/1e7):.1f}Cr", font_size=18, showarrow=False, font_color="#d4af37")],
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e0f0ff")),
            height=320, margin=dict(t=10, b=10)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
# ═════════════════════════════════════════════════════════════════════════════
# TAB 7: AI DEAL NEGOTIATOR SIMULATOR
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_view == "🤝 Deal Negotiator":
    st.markdown("<h2 style='color:#d4af37;'>🤝 AI Deal Negotiator Simulator</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8a99ad;'>Simulate a live negotiation with AI seller/broker personas. Craft your pitch and see if the deal closes!</p>", unsafe_allow_html=True)
    PERSONAS = {
        "Mr. Rajan — Stubborn Old-School Landlord 🏚️": {
            "desc": "Emotional, traditional. Values family connections, cash payments, and quick no-fuss handovers. Hates investors.",
            "weights": {"price_ratio": 0.45, "down_pct": 0.25, "timeline": 0.15, "strategy": 0.15},
            "strategy_boost": {"Family Story & Emotional Appeal": 20, "Cash Deal Offer": 15, "ROI / Investment Pitch": -10, "Developer Comparison Pressure": -5},
        },
        "Pooja — Eager Commission Broker 💼": {
            "desc": "Commission-focused. Loves fast closings and bonus incentives. Responds well to enthusiasm and quick decisions.",
            "weights": {"price_ratio": 0.30, "down_pct": 0.15, "timeline": 0.35, "strategy": 0.20},
            "strategy_boost": {"Cash Deal Offer": 10, "Quick Close Promise": 25, "ROI / Investment Pitch": 5, "Family Story & Emotional Appeal": 0},
        },
        "Vikram — Analytical VC Seller 📊": {
            "desc": "Data-driven. Demands logical ROI justification and structured payment plans. Won't budge without numbers.",
            "weights": {"price_ratio": 0.35, "down_pct": 0.20, "timeline": 0.10, "strategy": 0.35},
            "strategy_boost": {"ROI / Investment Pitch": 30, "Developer Comparison Pressure": 15, "Cash Deal Offer": 5, "Family Story & Emotional Appeal": -15},
        },
    }
    col_neg1, col_neg2 = st.columns([1.3, 1.7])
    with col_neg1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**🎯 Your Offer Details**")
        persona_name = st.selectbox("Select Seller / Broker", list(PERSONAS.keys()), key="neg_persona")
        asking_price = st.number_input("Seller's Asking Price (₹)", value=12000000, step=100000, key="neg_asking")
        offer_price  = st.number_input("Your Offer Price (₹)",     value=10500000, step=100000, key="neg_offer")
        down_pct     = st.slider("Down Payment (%)", 10, 80, 30, 5, key="neg_down")
        timeline_mo  = st.slider("Closure Timeline (months)", 1, 24, 3, 1, key="neg_timeline")
        strategy     = st.selectbox("Your Pitch Strategy",
            ["Family Story & Emotional Appeal", "Cash Deal Offer", "Quick Close Promise",
             "ROI / Investment Pitch", "Developer Comparison Pressure"], key="neg_strategy")
        neg_notes    = st.text_area("Your Opening Statement", placeholder="Write your opening pitch here...", key="neg_notes")
        run_neg      = st.button("🚀 Send Offer & Negotiate", use_container_width=True, key="run_neg")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_neg2:
        p = PERSONAS[persona_name]
        st.markdown(f"""
        <div class="glass-card" style="border-color:rgba(0,245,212,0.25);">
          <div style='font-size:1.1rem; font-weight:700; color:#00f5d4; margin-bottom:0.5rem;'>{persona_name}</div>
          <div style='font-size:0.9rem; color:#8a99ad; margin-bottom:1rem;'>{p['desc']}</div>
          <div style='display:grid; grid-template-columns:1fr 1fr; gap:0.6rem;'>
            <div style='background:rgba(0,245,212,0.05); border-radius:8px; padding:0.7rem; text-align:center;'><div style='font-size:0.7rem; color:#8a99ad;'>PRICE SENSITIVITY</div><div style='color:#d4af37; font-weight:700;'>{int(p['weights']['price_ratio']*100)}%</div></div>
            <div style='background:rgba(0,245,212,0.05); border-radius:8px; padding:0.7rem; text-align:center;'><div style='font-size:0.7rem; color:#8a99ad;'>DOWN PMT WEIGHT</div><div style='color:#d4af37; font-weight:700;'>{int(p['weights']['down_pct']*100)}%</div></div>
            <div style='background:rgba(0,245,212,0.05); border-radius:8px; padding:0.7rem; text-align:center;'><div style='font-size:0.7rem; color:#8a99ad;'>TIMELINE WEIGHT</div><div style='color:#d4af37; font-weight:700;'>{int(p['weights']['timeline']*100)}%</div></div>
            <div style='background:rgba(0,245,212,0.05); border-radius:8px; padding:0.7rem; text-align:center;'><div style='font-size:0.7rem; color:#8a99ad;'>STRATEGY WEIGHT</div><div style='color:#d4af37; font-weight:700;'>{int(p['weights']['strategy']*100)}%</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if run_neg:
            price_ratio   = min(offer_price / asking_price, 1.0)
            price_score   = max(0, (price_ratio - 0.80) / 0.20) * 100
            down_score    = min(100, (down_pct / 50) * 100)
            timeline_score = max(0, 100 - (timeline_mo - 1) * 4)
            strat_bonus    = p["strategy_boost"].get(strategy, 0)
            strategy_score = max(0, min(100, 50 + strat_bonus))
            raw = (
                p["weights"]["price_ratio"]  * price_score +
                p["weights"]["down_pct"]      * down_score +
                p["weights"]["timeline"]      * timeline_score +
                p["weights"]["strategy"]      * strategy_score
            )
            acceptance_prob = min(95, max(5, raw))
            if acceptance_prob >= 70:
                outcome = "✅ DEAL ACCEPTED!"
                color   = "#06d6a0"
                msg     = "Congratulations! The seller is ready to sign. Proceed to due diligence and legal documentation."
            elif acceptance_prob >= 45:
                outcome = "🤔 COUNTER-OFFER LIKELY"
                color   = "#f77f00"
                msg     = f"The seller will likely counter. Consider improving your down payment or shortening the timeline."
            else:
                outcome = "❌ OFFER REJECTED"
                color   = "#ef233c"
                msg     = "The seller is not interested. Re-evaluate your price or change your pitch strategy."
            st.markdown(f"""
            <div style='background:rgba({"6,214,160" if acceptance_prob>=70 else "247,127,0" if acceptance_prob>=45 else "239,35,60"},0.1);
                        border:2px solid {color}; border-radius:16px; padding:1.5rem; text-align:center; margin-top:1rem;'>
              <div style='font-size:1.8rem; font-weight:800; color:{color};'>{outcome}</div>
              <div style='font-size:3rem; font-weight:900; color:{color}; margin:0.5rem 0;'>{acceptance_prob:.0f}%</div>
              <div style='font-size:0.85rem; color:#8a99ad;'>Acceptance Probability</div>
              <div style='font-size:0.9rem; color:#cbd5e1; margin-top:1rem;'>{msg}</div>
            </div>
            """, unsafe_allow_html=True)
            # Breakdown gauge chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=acceptance_prob,
                title={"text": "Deal Acceptance Probability", "font": {"color": "#e0f0ff", "size": 14}},
                number={"suffix": "%", "font": {"color": color, "size": 40}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#8a99ad"},
                    "bar": {"color": color, "thickness": 0.25},
                    "bgcolor": "#0d1117",
                    "steps": [
                        {"range": [0, 45],  "color": "rgba(239,35,60,0.12)"},
                        {"range": [45, 70], "color": "rgba(247,127,0,0.12)"},
                        {"range": [70, 100],"color": "rgba(6,214,160,0.12)"},
                    ],
                },
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e0f0ff"),
                height=240, margin=dict(t=30, b=10, l=20, r=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            # Component bar
            comp_names  = ["Price Score", "Down Pmt Score", "Timeline Score", "Strategy Score"]
            comp_vals   = [price_score, down_score, timeline_score, strategy_score]
            comp_colors = ["#d4af37" if v >= 60 else "#ef476f" for v in comp_vals]
            fig_bars = go.Figure(go.Bar(
                x=comp_names, y=comp_vals,
                marker_color=comp_colors,
                text=[f"{v:.0f}" for v in comp_vals], textposition="outside",
                textfont=dict(color="#e0f0ff")
            ))
            fig_bars.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e0f0ff"), yaxis=dict(range=[0, 115], gridcolor="rgba(212,175,55,0.1)"),
                xaxis=dict(showgrid=False), height=240, margin=dict(t=20, b=20)
            )
            st.plotly_chart(fig_bars, use_container_width=True)
# ═════════════════════════════════════════════════════════════════════════════
# TAB 8: INVESTMENT SENSITIVITY HEATMAP
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_view == "🔥 Investment Heatmap":
    st.markdown("<h2 style='color:#d4af37;'>🔥 Investment Sensitivity Heatmap</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8a99ad;'>See how 5-Year Return on Equity (ROE) shifts across different mortgage interest rates and annual property appreciation rates.</p>", unsafe_allow_html=True)
    col_hm1, col_hm2 = st.columns([1, 3])
    with col_hm1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**⚙️ Parameters**")
        hm_price     = st.number_input("Property Price (₹)", value=10000000, step=500000, key="hm_price")
        hm_down_pct  = st.slider("Down Payment (%)", 10, 50, 20, 5, key="hm_down")
        hm_loan_yrs  = st.slider("Loan Tenure (years)", 5, 30, 20, 1, key="hm_years")
        hm_rent_mo   = st.number_input("Monthly Rent Saved (₹)", value=30000, step=1000, key="hm_rent")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_hm2:
        interest_rates   = [r/10 for r in range(60, 125, 5)]   # 6.0% to 12.0%
        appreciation_rates = [a/10 for a in range(40, 125, 5)] # 4.0% to 12.0%
        down_payment = hm_price * hm_down_pct / 100
        loan_amount  = hm_price - down_payment
        roe_matrix = []
        for app_rate in appreciation_rates:
            row = []
            for int_rate in interest_rates:
                r_monthly  = int_rate / 100 / 12
                n_payments = hm_loan_yrs * 12
                if r_monthly > 0:
                    emi = loan_amount * r_monthly * (1 + r_monthly)**n_payments / ((1 + r_monthly)**n_payments - 1)
                else:
                    emi = loan_amount / n_payments
                total_interest_5yr = (emi * 60) - (loan_amount - loan_amount * (1 - (1 + r_monthly)**(-60 + n_payments)) / ((1 + r_monthly)**n_payments - 1) if r_monthly > 0 else loan_amount * 60 / n_payments)
                future_val   = hm_price * ((1 + app_rate / 100) ** 5)
                capital_gain = future_val - hm_price
                rent_benefit = hm_rent_mo * 12 * 5
                net_return   = capital_gain + rent_benefit - (emi * 60 - loan_amount)
                equity_invested = down_payment
                roe = (net_return / equity_invested) * 100
                row.append(round(roe, 1))
            roe_matrix.append(row)
        x_labels = [f"{r:.1f}%" for r in interest_rates]
        y_labels = [f"{a:.1f}%" for a in appreciation_rates]
        fig_heat = go.Figure(go.Heatmap(
            z=roe_matrix,
            x=x_labels,
            y=y_labels,
            colorscale=[
                [0.0,  "#ef233c"],
                [0.25, "#f77f00"],
                [0.5,  "#d4af37"],
                [0.75, "#00f5d4"],
                [1.0,  "#06d6a0"],
            ],
            text=[[f"{v:.0f}%" for v in row] for row in roe_matrix],
            texttemplate="%{text}",
            textfont=dict(size=10, color="#fff"),
            hovertemplate="Interest Rate: <b>%{x}</b><br>Appreciation: <b>%{y}</b><br>5-Yr ROE: <b>%{z:.1f}%</b><extra></extra>",
            colorbar=dict(
                title="5-Yr ROE (%)",
                titlefont=dict(color="#e0f0ff"),
                tickfont=dict(color="#e0f0ff"),
                thickness=14,
            )
        ))
        fig_heat.update_layout(
            xaxis=dict(title="Mortgage Interest Rate", tickfont=dict(color="#8a99ad"), titlefont=dict(color="#d4af37")),
            yaxis=dict(title="Annual Appreciation Rate", tickfont=dict(color="#8a99ad"), titlefont=dict(color="#d4af37")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e0f0ff"),
            height=520,
            margin=dict(t=20, b=60, l=20, r=20)
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        # Best/Worst scenario summary
        flat_roe = [v for row in roe_matrix for v in row]
        best_roe = max(flat_roe)
        worst_roe = min(flat_roe)
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; padding:1rem; border-color:rgba(6,214,160,0.4);">
              <div style='font-size:0.75rem; color:#8a99ad;'>BEST CASE 5-Yr ROE</div>
              <div style='font-size:1.8rem; font-weight:800; color:#06d6a0;'>{best_roe:.0f}%</div>
              <div style='font-size:0.75rem; color:#8a99ad;'>Low rates + High appreciation</div>
            </div>""", unsafe_allow_html=True)
        with col_s2:
            mid_roe = flat_roe[len(flat_roe)//2]
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; padding:1rem; border-color:rgba(212,175,55,0.4);">
              <div style='font-size:0.75rem; color:#8a99ad;'>MID SCENARIO ROE</div>
              <div style='font-size:1.8rem; font-weight:800; color:#d4af37;'>{mid_roe:.0f}%</div>
              <div style='font-size:0.75rem; color:#8a99ad;'>Baseline conditions</div>
            </div>""", unsafe_allow_html=True)
        with col_s3:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; padding:1rem; border-color:rgba(239,35,60,0.4);">
              <div style='font-size:0.75rem; color:#8a99ad;'>WORST CASE 5-Yr ROE</div>
              <div style='font-size:1.8rem; font-weight:800; color:#ef233c;'>{worst_roe:.0f}%</div>
              <div style='font-size:0.75rem; color:#8a99ad;'>High rates + Low appreciation</div>
            </div>""", unsafe_allow_html=True)
# ═════════════════════════════════════════════════════════════════════════════
# TAB 9: PRINTABLE VALUATION CERTIFICATE
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_view == "🏆 Certificate":
    st.markdown("<h2 style='color:#d4af37;'>🏆 Printable Valuation Certificate</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8a99ad;'>Generate an official HTML appraisal certificate for any property configuration and download it instantly.</p>", unsafe_allow_html=True)
    col_cert1, col_cert2 = st.columns([1.2, 1.8])
    with col_cert1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**📋 Certificate Details**")
        cert_loc   = st.selectbox("Location", ["South Mumbai (Malabar Hill)", "Gurugram Golf Course Road",
            "South Delhi (Vasant Vihar)", "Bangalore Indiranagar", "Hyderabad Jubilee Hills",
            "Pune Koregaon Park", "Standard Suburban Sector"], key="cert_loc")
        cert_ptype = st.selectbox("Property Type", ["Ultra-Luxury Penthouse", "Modern Glass Villa",
            "Contemporary Apartment", "Classical Grand Mansion"], key="cert_ptype")
        cert_area  = st.number_input("Carpet Area (sqft)", 400, 10000, 2200, 100, key="cert_area")
        cert_beds  = st.selectbox("Bedrooms (BHK)", [1,2,3,4,5,6], index=2, key="cert_beds")
        cert_baths = st.selectbox("Bathrooms", [1,2,3,4,5], index=2, key="cert_baths")
        LPI = {"South Mumbai (Malabar Hill)": 3.5, "Gurugram Golf Course Road": 2.2,
               "South Delhi (Vasant Vihar)": 2.8, "Bangalore Indiranagar": 1.8,
               "Hyderabad Jubilee Hills": 1.9, "Pune Koregaon Park": 1.5, "Standard Suburban Sector": 1.0}
        PTM = {"Ultra-Luxury Penthouse": 1.4, "Modern Glass Villa": 1.6,
               "Contemporary Apartment": 1.0, "Classical Grand Mansion": 1.8}
        base_v = model.predict(pd.DataFrame({"area": [cert_area], "bedrooms": [cert_beds], "bathrooms": [cert_baths]}))[0]
        cert_val = int(base_v * LPI.get(cert_loc, 1.0) * PTM.get(cert_ptype, 1.0))
        st.markdown(f"""
        <div style='margin-top:1rem; padding:1rem; background:rgba(212,175,55,0.08);
             border:1px solid rgba(212,175,55,0.3); border-radius:12px; text-align:center;'>
          <div style='font-size:0.75rem; color:#8a99ad;'>ESTIMATED VALUATION</div>
          <div style='font-size:2rem; font-weight:800; color:#d4af37;'>₹{cert_val:,}</div>
        </div>
        """, unsafe_allow_html=True)
        cert_html = generate_html_certificate(cert_loc, cert_ptype, cert_area, cert_beds, cert_baths, cert_val)
        st.download_button(
            "⬇️ Download Appraisal Certificate (HTML)",
            cert_html.encode("utf-8"),
            file_name=f"EstateX_Certificate_{cert_loc[:10].replace(' ','_')}.html",
            mime="text/html",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with col_cert2:
        # Live preview using certificate HTML in an iframe-style render
        today = datetime.date.today().strftime("%B %d, %Y")
        cert_id = f"EX-{random.randint(100000, 999999)}"
        st.markdown(f"""
        <div style="background:#0c0e14; border:3px solid #d4af37; border-radius:16px; padding:2.5rem; font-family:'Times New Roman', serif; text-align:center;">
          <div style="border:1px solid rgba(212,175,55,0.4); padding:2rem; border-radius:10px;">
            <div style="float:right; font-size:11px; color:#8a99ad;">CERTIFICATE NO: {cert_id}</div>
            <div style="font-size:1.8rem; font-weight:800; color:#d4af37; letter-spacing:2px; margin-bottom:0.3rem;">⚜️ ESTATEX APPRAISAL CERTIFICATE ⚜️</div>
            <div style="font-size:0.75rem; text-transform:uppercase; color:#8a99ad; letter-spacing:4px; margin-bottom:2rem;">Official Valuation Declaration</div>
            <div style="font-size:0.9rem; line-height:1.8; color:#cbd5e0; margin-bottom:1.5rem;">
              This document formally certifies the machine-learning derived market appraisal for the premium residential asset configured below.
              Valuation has been computed using multi-variable regression planes adjusted for local state surcharges and location premium indexes.
            </div>
            <div style="font-size:2.5rem; color:#d4af37; font-weight:bold; text-shadow:0 0 15px rgba(212,175,55,0.4); margin:1.5rem 0;">₹{cert_val:,}</div>
            <table style="width:80%; margin:0 auto 1.5rem auto; border-collapse:collapse; text-align:left;">
              <tr><td style="padding:8px; color:#d4af37; font-weight:bold;">Location</td><td style="padding:8px; color:#e0f0ff;">{cert_loc}</td></tr>
              <tr><td style="padding:8px; color:#d4af37; font-weight:bold;">Classification</td><td style="padding:8px; color:#e0f0ff;">{cert_ptype}</td></tr>
              <tr><td style="padding:8px; color:#d4af37; font-weight:bold;">Carpet Area</td><td style="padding:8px; color:#e0f0ff;">{cert_area} Sq Ft</td></tr>
              <tr><td style="padding:8px; color:#d4af37; font-weight:bold;">BHK</td><td style="padding:8px; color:#e0f0ff;">{cert_beds} Bedrooms</td></tr>
              <tr><td style="padding:8px; color:#d4af37; font-weight:bold;">Bathrooms</td><td style="padding:8px; color:#e0f0ff;">{cert_baths} Bathrooms</td></tr>
              <tr><td style="padding:8px; color:#d4af37; font-weight:bold;">Appraisal Date</td><td style="padding:8px; color:#e0f0ff;">{today}</td></tr>
            </table>
            <div style="display:flex; justify-content:space-around; margin-top:2rem; padding-top:1.5rem; border-top:1px solid rgba(212,175,55,0.3);">
              <div style="text-align:center;">
                <div style="width:160px; border-top:1px solid rgba(212,175,55,0.5); padding-top:8px; color:#8a99ad; font-size:12px;">EstateX ML Engine</div>
                <div style="color:#8a99ad; font-size:11px;">Authorized Digital Seal</div>
              </div>
              <div style="text-align:center;">
                <div style="width:160px; border-top:1px solid rgba(212,175,55,0.5); padding-top:8px; color:#8a99ad; font-size:12px;">Rajan Sethi</div>
                <div style="color:#8a99ad; font-size:11px;">Senior Registrar Audit</div>
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
st.markdown("<br><hr style='border-top: 1px solid rgba(212, 175, 55, 0.15);'>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; font-size:0.80rem; color:#8a99ad;'>⚜️ EstateX Premium Real Estate Analytics System | Custom Linear Regression Model | V2.5 Luxury Edition</div>", unsafe_allow_html=True)
