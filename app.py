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

# --- Mock Data ---
NEWS_ARTICLES = [
    {
        "title": "The True Cost of Fast Fashion",
        "content": "Every year, tens of millions of children are forced to make clothes for major brands. They are often paid little to no money.",
        "stat": "138 Million Children Affected",
        "source": "Unstitched Research"
    },
    {
        "title": "Safety in the Workplace",
        "content": "Terrible working conditions lead to injuries. Unstitched works to reduce these numbers and give children the right to education and play.",
        "stat": "106.4 Million Injured Yearly",
        "source": "Global Labor Stats"
    }
]

MARKETPLACE_ITEMS = [
    {"id": 1, "title": "Vintage Denim Jacket", "price": 25.00, "seller": "SarahSews", "icon": "🧥", "rating": "A", "desc": "Saved from landfill!"},
    {"id": 2, "title": "Upcycled Tee", "price": 12.50, "seller": "GreenGuy", "icon": "👕", "rating": "A+", "desc": "Hand-painted design."},
    {"id": 3, "title": "Chunky Knit Sweater", "price": 18.00, "seller": "RetroFit", "icon": "🧶", "rating": "B", "desc": "100% Wool."},
    {"id": 4, "title": "Hemp Cargo Pants", "price": 30.00, "seller": "EcoWarrior", "icon": "👖", "rating": "A", "desc": "Super durable."},
]

CHARITIES_DB = [
    {"name": "Unseen", "mission": "Working towards a world without slavery.", "id": "unseen"},
    {"name": "Hope for Justice", "mission": "Ending human trafficking and modern slavery.", "id": "hfj"},
    {"name": "Save the Children", "mission": "Keeping children safe, healthy and learning.", "id": "stc"}
]

# ==========================================
# 2. UTILITY FUNCTIONS
# ==========================================

def calculate_ethical_score(brand, material, origin):
    base_risk = 0
    # Simple logic to simulate the AI decision making
    if "Polyester" in material: base_risk += 30
    elif "Organic" in material: base_risk += 5
    else: base_risk += 20
    
    high_risk_origins = ["China", "Bangladesh", "Vietnam"]
    if any(country in origin for country in high_risk_origins): base_risk += 40
    elif "Portugal" in origin or "UK" in origin: base_risk += 10
    else: base_risk += 25
    
    return max(1, min(99, base_risk))

def scan_label_mock(image):
    """Simulates AI extraction."""
    time.sleep(1.5) 
    materials = ["Cotton", "Polyester", "Rayon", "Organic Cotton", "Nylon"]
    brands = ["FastFashionCo", "EcoThread", "UrbanTrend", "Shein-Like Brand", "H&M-Like Brand"]
    origins = ["Made in China", "Made in Bangladesh", "Made in Portugal", "Made in UK", "Made in Vietnam"]

    return {
        "material": random.choice(materials),
        "brand": random.choice(brands),
        "origin": random.choice(origins)
    }

# ==========================================
# 3. STATE & STYLING
# ==========================================

if 'user_role' not in st.session_state: st.session_state.user_role = None
if 'subscription' not in st.session_state: st.session_state.subscription = 'Free'
if 'accessibility_mode' not in st.session_state: st.session_state.accessibility_mode = False
if 'scan_history' not in st.session_state: st.session_state.scan_history = []
if 'guest_scans' not in st.session_state: st.session_state.guest_scans = 0

def inject_css():
    """Injects CSS based on accessibility settings."""
    is_access = st.session_state.accessibility_mode
    
    # Palette from slides + accessible mode
    bg_color = "#FFFFFF" if is_access else "#FFEEDB" # Cream
    text_color = "#000000" if is_access else "#264653" # Deep Green
    accent_teal = "#2A9D8F"
    accent_coral = "#E76F51"
    
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg_color}; }}
        h1, h2, h3, h4 {{ color: {text_color} !important; font-family: 'Helvetica Neue', sans-serif; }}
        p, div, label, span, li {{ color: {text_color} !important; font-size: {"18px" if is_access else "16px"}; }}
        
        /* Custom Cards */
        .stat-card {{
            background-color: white; padding: 20px; border-radius: 15px;
            border-left: 5px solid {accent_coral};
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;
        }}
        .shop-card {{
            background-color: white; padding: 15px; border-radius: 15px;
            margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
            text-align: center;
        }}
        .result-box {{
            background-color: {accent_teal}; color: white; padding: 15px; 
            border-radius: 10px; margin-bottom: 10px;
        }}
        .slogan-text {{
            text-align: center; font-style: italic; color: {accent_coral}; font-weight: bold;
        }}
        
        /* Buttons */
        .stButton>button {{
            background-color: {accent_teal}; color: white !important;
            border-radius: 25px; border: none; padding: 10px 24px;
            width: 100%; font-weight: bold; box-shadow: 0 4px 0 {text_color};
            transition: all 0.2s;
        }}
        .stButton>button:active {{
            transform: translateY(4px); box-shadow: none;
        }}
    </style>
    """, unsafe_allow_html=True)

inject_css()

# ==========================================
# 4. COMPONENT FUNCTIONS
# ==========================================

def render_scanner():
    st.header("📸 Behind the Label")
    st.caption("Identify materials, brands, and supply chain risks.")
    
    # Guest Limit Logic
    if st.session_state.user_role == 'Guest' and st.session_state.guest_scans >= 10:
        st.error("You've used your 10 free scans! Join Unstitched to continue.")
        return

    img_file = st.camera_input("Scan your clothing label")
    
    if img_file:
        with st.spinner("AI is analyzing supply chain data..."):
            data = scan_label_mock(img_file)
            risk = calculate_ethical_score(data['brand'], data['material'], data['origin'])
            
            if st.session_state.user_role == 'Guest':
                st.session_state.guest_scans += 1
            st.session_state.scan_history.append({"risk": risk, "brand": data['brand']})

        # --- RESULTS UI ---
        st.markdown(f"""
        <div class="stat-card">
            <h3 style="margin-top:0; color:#264653;">Analysis Results</h3>
            <p><strong>Brand:</strong> {data['brand']}</p>
            <p><strong>Origin:</strong> {data['origin']}</p>
            <p><strong>Material:</strong> {data['material']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        col1.progress(risk / 100)
        col2.metric("Risk", f"{risk}%")
        
        # Risk Logic
        if risk > 60:
            st.error(f"⚠️ High Risk of Child Labour. {data['origin']} has known supply chain issues.")
        else:
            st.success("✅ Lower Risk. This item likely has a cleaner supply chain.")
            
        st.info("💡 **Recommendation:** Don't throw this away! Even high-risk items can be upcycled to keep them out of landfill.")

def render_news():
    st.header("📰 Unstitched News")
    st.markdown("<p class='slogan-text'>\"Scan the label, stop the labour.\"</p>", unsafe_allow_html=True)
    
    st.write("Stay informed about the fight against child labour.")
    
    for article in NEWS_ARTICLES:
        st.markdown(f"""
        <div class="stat-card">
            <h4 style="color: #E76F51;">{article['stat']}</h4>
            <h5 style="margin:0;">{article['title']}</h5>
            <p style="font-size: 14px;">{article['content']}</p>
            <p style="font-size: 12px; color: grey;">Source: {article['source']}</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.subheader("How you can help")
    st.write("By using Unstitched, you are choosing transparency over exploitation.")
    
    if st.button("Donate to Support Change"):
        render_donation_modal()

def render_donation_modal():
    with st.expander("💖 Make a Donation", expanded=True):
        st.write("Donations go to Unseen, Hope for Justice, and Save the Children.")
        c1, c2, c3 = st.columns(3)
        if c1.button("£2"): st.toast("Thank you for your £2 donation! 🎉")
        if c2.button("£5"): st.toast("Thank you for your £5 donation! 🎉")
        if c3.button("£10"): st.toast("Thank you for your £10 donation! 🎉")

def render_shop():
    st.header("🛍️ Simple Shop")
    st.write("Buy, sell, and swap ethical fashion.")
    
    col1, col2 = st.columns([3, 1])
    col1.text_input("Search items...", placeholder="Vintage denim, cotton tee...")
    col2.selectbox("Sort", ["Newest", "Price: Low to High"])

    cols = st.columns(2)
    for i, item in enumerate(MARKETPLACE_ITEMS):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="shop-card">
                <div style="font-size: 40px;">{item['icon']}</div>
                <div style="font-weight: bold;">{item['title']}</div>
                <div style="color: #E76F51;">£{item['price']:.2f}</div>
                <div style="font-size: 10px; color: grey;">{item['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View", key=f"btn_{item['id']}"):
                st.toast(f"Opening details for {item['title']}...")

def render_notice_board():
    st.header("📌 Community Board")
    
    if st.session_state.subscription != 'Needles':
        st.warning("🔒 This area is for 'Needles' subscribers only.")
        st.image("https://placehold.co/600x200/E76F51/FFF?text=Join+Needles+to+Access", use_container_width=True)
        return

    st.subheader("Weekly Upcycling Competition")
    st.write("Theme: **Denim Transformation**")
    
    c1, c2 = st.columns(2)
    with c1: st.image("https://placehold.co/300x300/264653/FFF?text=Before", caption="Old Jeans")
    with c2: st.image("https://placehold.co/300x300/E76F51/FFF?text=After", caption="New Tote Bag!")
    st.button("Vote for EcoWarrior99 ❤️")

def render_profile():
    st.header("👤 My Profile")
    
    # Dashboard Section
    st.subheader("Your Impact")
    if st.session_state.scan_history:
        df = pd.DataFrame(st.session_state.scan_history)
        safe_count = len(df[df['risk'] < 40])
        st.metric("Ethical Choices Made", safe_count, delta=f"{len(df)} total scans")
    else:
        st.info("Start scanning labels to track your impact!")

    st.divider()
    
    # Subscription Section
    st.subheader("Subscription Status")
    if st.session_state.subscription == 'Free':
        st.markdown("""
        **Current Plan: Free**
        - Basic Label Scanning
        - Access Marketplace
        """)
        if st.button("Upgrade to Needles (£4.99/mo)"):
            st.session_state.subscription = 'Needles'
            st.balloons()
            st.rerun()
    else:
        st.success("You are a Needles Member! 🪡")
        st.caption("£1.50 of your sub goes to charity monthly.")

    st.divider()
    
    # About Section
    with st.expander("About Unstitched"):
        st.write("Created by **White Fox Vols**")
        st.write("Team: **Katelyn, Olivia, Victoria, Kirstie**")
        st.caption("© 2024 Unstitched. All rights reserved.")
        
    if st.button("Log Out", type="secondary"):
        st.session_state.user_role = None
        st.rerun()

# ==========================================
# 5. ONBOARDING
# ==========================================

def render_onboarding():
    st.markdown("<div style='text-align: center; font-size: 60px;'>🧵</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #264653;'>UNSTITCHED</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #E76F51;'>Scan the label,<br>stop the labour.</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Sign In", "New Account"])
    
    with tab1:
        st.text_input("Email")
        st.text_input("Password", type="password")
        if st.button("Sign In"):
            st.session_state.user_role = 'User'
            st.rerun()
            
    with tab2:
        st.text_input("Name")
        st.date_input("Date of Birth")
        if st.button("Join the Movement"):
            st.session_state.user_role = 'User'
            st.rerun()
            
    st.divider()
    if st.button("Continue as Guest"):
        st.session_state.user_role = 'Guest'
        st.rerun()

# ==========================================
# 6. MAIN APP LOGIC
# ==========================================

if st.session_state.user_role is None:
    render_onboarding()
else:
    # Header
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown(f"**Hello, {st.session_state.user_role}!**")
    with c2:
        # Accessibility Toggle
        access_label = "👁️" if not st.session_state.accessibility_mode else "Aa"
        if st.button(access_label, help="Toggle Accessibility Mode"):
            st.session_state.accessibility_mode = not st.session_state.accessibility_mode
            st.rerun()

    # Mobile-style Bottom Nav
    selected = option_menu(
        menu_title=None,
        options=["Scan", "Shop", "News", "Board", "Me"],
        icons=["camera", "bag", "newspaper", "clipboard", "person"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#E76F51", "font-size": "18px"}, 
            "nav-link": {"font-size": "11px", "text-align": "center", "margin": "0px"},
            "nav-link-selected": {"background-color": "#264653"},
        }
    )
    
    st.markdown("<hr style='margin-top: 0; margin-bottom: 20px;'>", unsafe_allow_html=True)

    if selected == "Scan": render_scanner()
    elif selected == "Shop": render_shop()
    elif selected == "News": render_news()
    elif selected == "Board": render_notice_board()
    elif selected == "Me": render_profile()
