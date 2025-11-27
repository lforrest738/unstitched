import streamlit as st
import time
import random
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# ==========================================
# 1. CONFIGURATION & DATA MOCKS
# ==========================================

st.set_page_config(
    page_title="Unstitched",
    page_icon="🧵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Mock Data (Replaces JSON files) ---
BRANDS_DB = [
    {"name": "FastFashionCo", "risk_score": 85, "origin": "Multiple High Risk Regions"},
    {"name": "EcoThread", "risk_score": 10, "origin": "Portugal"},
    {"name": "GenericBrand", "risk_score": 60, "origin": "China"},
    {"name": "GreenStitch", "risk_score": 5, "origin": "UK"},
    {"name": "UrbanTrend", "risk_score": 75, "origin": "Bangladesh"}
]

CHARITIES_DB = [
    {"name": "Unseen", "mission": "Working towards a world without slavery.", "id": "unseen"},
    {"name": "Hope for Justice", "mission": "Ending human trafficking and modern slavery.", "id": "hfj"},
    {"name": "World Vision", "mission": "Helping the most vulnerable children overcome poverty.", "id": "wv"},
    {"name": "Save the Children", "mission": "Keeping children safe, healthy and learning.", "id": "stc"}
]

MARKETPLACE_ITEMS = [
    {"id": 1, "title": "Vintage Denim Jacket", "price": 25.00, "seller": "SarahSews", "icon": "🧥", "rating": "A"},
    {"id": 2, "title": "Upcycled Tee", "price": 12.50, "seller": "GreenGuy", "icon": "👕", "rating": "A+"},
    {"id": 3, "title": "Chunky Knit Sweater", "price": 18.00, "seller": "RetroFit", "icon": "🧶", "rating": "B"},
    {"id": 4, "title": "Hemp Cargo Pants", "price": 30.00, "seller": "EcoWarrior", "icon": "👖", "rating": "A"},
]

# ==========================================
# 2. UTILITY FUNCTIONS (Logic)
# ==========================================

def calculate_ethical_score(brand, material, origin):
    """Calculates a mock risk percentage (0-100%). Higher = Higher Risk."""
    base_risk = 0
    
    # Material Risk
    if "Polyester" in material or "Rayon" in material:
        base_risk += 30
    elif "Organic" in material:
        base_risk += 5
    else:
        base_risk += 20
        
    # Origin Risk
    high_risk_origins = ["China", "Bangladesh", "Vietnam"]
    if any(country in origin for country in high_risk_origins):
        base_risk += 40
    elif "Portugal" in origin or "UK" in origin:
        base_risk += 10
    else:
        base_risk += 25
        
    # Brand History Mock
    if brand == "FastFashionCo": base_risk += 20
    elif brand == "EcoThread": base_risk -= 10

    return max(1, min(99, base_risk))

def get_risk_explanation(score):
    if score > 70:
        return "High Risk: Indicators often linked to labour exploitation detected."
    elif score > 40:
        return "Medium Risk: Some transparency, but materials/origin pose concerns."
    else:
        return "Low Risk: Looks good! Likely a more ethical supply chain."

def scan_label_mock(image):
    """Simulates AI extraction."""
    time.sleep(1.5) # Simulate processing delay
    
    materials = ["Cotton", "Polyester", "Rayon", "Organic Cotton", "Nylon"]
    brands = ["FastFashionCo", "EcoThread", "UrbanTrend", "Unknown Label"]
    origins = ["Made in China", "Made in Bangladesh", "Made in Portugal", "Made in UK"]

    return {
        "material": random.choice(materials),
        "brand": random.choice(brands),
        "origin": random.choice(origins)
    }

# ==========================================
# 3. STATE & STYLING
# ==========================================

# Initialize State
if 'user_role' not in st.session_state: st.session_state.user_role = None
if 'subscription' not in st.session_state: st.session_state.subscription = 'Free'
if 'accessibility_mode' not in st.session_state: st.session_state.accessibility_mode = False
if 'scan_history' not in st.session_state: st.session_state.scan_history = []
if 'guest_scans' not in st.session_state: st.session_state.guest_scans = 0

def inject_css():
    """Injects CSS based on accessibility settings."""
    # Palette: Teal(#2A9D8F), Coral(#E76F51), Cream(#FFEEDB), DeepGreen(#264653)
    
    is_access = st.session_state.accessibility_mode
    font_size = "18px" if is_access else "16px"
    bg_color = "#FFFFFF" if is_access else "#FFEEDB"
    text_color = "#000000" if is_access else "#264653"
    card_bg = "#F0F0F0" if is_access else "#FFFFFF"

    st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg_color}; }}
        h1, h2, h3, h4 {{ color: {text_color} !important; font-family: 'Helvetica Neue', sans-serif; }}
        p, div, label, span, li {{ color: {text_color} !important; font-size: {font_size}; }}
        
        /* Mobile Nav & Buttons */
        .stButton>button {{
            background-color: #2A9D8F; color: white !important;
            border-radius: 25px; border: none; padding: 10px 24px;
            width: 100%; font-weight: bold;
        }}
        .stButton>button:hover {{ background-color: #264653; }}
        
        /* Cards */
        .custom-card {{
            background-color: {card_bg}; padding: 15px; border-radius: 15px;
            margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        }}
        .risk-card {{
            background-color: #FFEEDB; padding: 20px; border-radius: 15px;
            border: 2px solid #264653; margin-bottom: 20px;
        }}
    </style>
    """, unsafe_allow_html=True)

inject_css()

# ==========================================
# 4. COMPONENT FUNCTIONS
# ==========================================

def render_scanner():
    st.header("📸 Behind the Label")
    st.write("Scan a clothing label to reveal its true cost.")
    
    if st.session_state.user_role == 'Guest' and st.session_state.guest_scans >= 10:
        st.error("You've used your 10 free scans! Please sign up.")
        return

    img_file = st.camera_input("Take a picture of the label")
    
    if img_file:
        with st.spinner("AI is analyzing text & materials..."):
            data = scan_label_mock(img_file)
            risk = calculate_ethical_score(data['brand'], data['material'], data['origin'])
            
            if st.session_state.user_role == 'Guest':
                st.session_state.guest_scans += 1
            
            # Save history
            st.session_state.scan_history.append({"risk": risk, "brand": data['brand']})

        # Results
        st.markdown(f"""
        <div class="risk-card">
            <h3 style="margin-top:0;">Analysis Complete</h3>
            <p><strong>Brand:</strong> {data['brand']}</p>
            <p><strong>Material:</strong> {data['material']}</p>
            <p><strong>Origin:</strong> {data['origin']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Ethical Risk Score")
        col1, col2 = st.columns([3, 1])
        col1.progress(risk / 100)
        col2.markdown(f"**{risk}%**")
        
        st.info(f"💡 {get_risk_explanation(risk)}")
        st.caption("Disclaimer: Percentages are estimates based on publicly available supply chain data.")
        
        st.subheader("♻️ Better Options")
        st.success(f"Don't throw it away! Check the Shop for {data['material']} upcycling ideas.")

def render_shop():
    st.header("🛍️ Simple Shop")
    st.write("Buy, sell, and swap pre-loved ethical fashion.")

    if st.session_state.user_role == 'Guest':
        st.warning("🔒 Guests can browse but cannot buy. Sign in to purchase!")
    
    with st.expander("Filter Options"):
        st.selectbox("Size", ["S", "M", "L", "XL"])
        st.selectbox("Material", ["Cotton", "Denim", "Wool"])

    cols = st.columns(2)
    for i, item in enumerate(MARKETPLACE_ITEMS):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="custom-card">
                <div style="font-size: 40px; text-align: center;">{item['icon']}</div>
                <h4 style="margin: 5px 0; font-size: 16px;">{item['title']}</h4>
                <p style="color: #E76F51; font-weight: bold;">£{item['price']:.2f}</p>
                <p style="font-size: 12px; color: #666;">By: {item['seller']}</p>
                <span style="background-color: #2A9D8F; color: white; padding: 2px 8px; border-radius: 8px; font-size: 10px;">Rating: {item['rating']}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"View", key=f"btn_{item['id']}"):
                if st.session_state.user_role == 'Guest':
                    st.toast("Sign in to buy!")
                else:
                    st.toast(f"Added {item['title']} to cart!")

def render_donations():
    st.header("🤝 Give Back")
    st.write("Support charities fighting child labour.")
    
    if st.session_state.user_role == 'Guest':
        st.error("Please sign in to donate.")
        return

    for char in CHARITIES_DB:
        with st.container():
            st.markdown(f"### {char['name']}")
            st.write(char['mission'])
            c1, c2, c3 = st.columns(3)
            if c1.button("£5", key=f"d5_{char['id']}"): st.balloons()
            if c2.button("£10", key=f"d10_{char['id']}"): st.balloons()
            if c3.button("Custom", key=f"dc_{char['id']}"): st.write("Custom amount")
            st.divider()

def render_subscription():
    st.header("🪡 Join 'Needles' Premium")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("""
        - 🎨 **Colour Analysis Tool**
        - 👗 **Outfit Planner**
        - 🚨 **Brand Alerts**
        - 🏆 **Notice Board Access**
        - ❤️ **£1.50/mo to charity**
        """)
    with c2:
        st.markdown("## £4.99")
        st.caption("per month")
        if st.session_state.subscription == 'Free':
            if st.button("Start Trial"):
                st.session_state.subscription = 'Needles'
                st.success("Welcome to the club! 🎉")
                time.sleep(1)
                st.rerun()
        else:
            st.success("You are a Member!")

def render_dashboard():
    st.header("📊 Impact Dashboard")
    if not st.session_state.scan_history:
        st.info("No scan data yet. Go scan some labels!")
        return

    df = pd.DataFrame(st.session_state.scan_history)
    avg_risk = df['risk'].mean()
    st.metric("Average Risk Score Encountered", f"{avg_risk:.1f}%")

    fig = px.bar(df, x='brand', y='risk', title="Risk Score by Brand", color='risk', 
                 color_continuous_scale=['#2A9D8F', '#E76F51'])
    st.plotly_chart(fig, use_container_width=True)

def render_notice_board():
    st.header("📌 Community Notice Board")
    if st.session_state.subscription != 'Needles':
        st.warning("This area is for 'Needles' subscribers only.")
        st.info("Unlock it in the Profile tab!")
        return

    st.subheader("Weekly Challenge: Denim")
    c1, c2 = st.columns(2)
    with c1: st.image("https://placehold.co/300x300/264653/FFF?text=Before", caption="User: EcoWarrior99")
    with c2: 
        st.image("https://placehold.co/300x300/E76F51/FFF?text=After", caption="Tote Bag Result!")
        st.button("Vote ❤️")

def render_onboarding():
    st.image("https://placehold.co/600x200/2A9D8F/FFF?text=Unstitched", use_container_width=True)
    st.title("Wear Your Values.")
    
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    with tab1:
        if st.button("Sign In (Demo)"):
            st.session_state.user_role = 'User'
            st.rerun()
    with tab2:
        st.text_input("Name")
        st.multiselect("Priorities", ["Child Labour", "Sustainability", "Price"])
        if st.button("Create Account"):
            st.session_state.user_role = 'User'
            st.rerun()
            
    st.divider()
    if st.button("Continue as Guest", type="secondary"):
        st.session_state.user_role = 'Guest'
        st.rerun()

# ==========================================
# 5. MAIN APP EXECUTION
# ==========================================

if st.session_state.user_role is None:
    render_onboarding()
else:
    # Top Bar
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown(f"**Hi, {st.session_state.user_role}!**")
        if st.session_state.subscription == 'Needles': st.badge("Needles Member 🪡")
    with c2:
        # Accessibility Toggle
        on = st.toggle('Aa', value=st.session_state.accessibility_mode)
        if on != st.session_state.accessibility_mode:
            st.session_state.accessibility_mode = on
            st.rerun()

    # Navigation
    selected = option_menu(
        menu_title=None,
        options=["Scan", "Shop", "Board", "Donate", "Profile"],
        icons=["camera", "bag", "clipboard", "heart", "person"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#E76F51", "font-size": "18px"}, 
            "nav-link": {"font-size": "12px", "text-align": "center", "margin": "0px"},
            "nav-link-selected": {"background-color": "#264653"},
        }
    )

    st.divider()

    if selected == "Scan": render_scanner()
    elif selected == "Shop": render_shop()
    elif selected == "Board": render_notice_board()
    elif selected == "Donate": render_donations()
    elif selected == "Profile":
        render_dashboard()
        st.divider()
        render_subscription()
        if st.button("Log Out"):
            st.session_state.user_role = None
            st.rerun()
            
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.caption("Unstitched © 2024. Building a better future, one thread at a time.")
