import streamlit as st
import time
import random
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import google.generativeai as genai
from PIL import Image

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

# Real images from Unsplash
MARKETPLACE_ITEMS = [
    {"id": 1, "title": "Vintage Denim Jacket", "price": 45.00, "seller": "SarahSews", "image": "https://images.unsplash.com/photo-1576871337632-b9aef4c17ab9?auto=format&fit=crop&w=300&q=80", "rating": "A", "desc": "Saved from landfill!", "category": "Outerwear", "style": "Vintage", "material": "Denim"},
    {"id": 2, "title": "Organic Cotton Tee", "price": 15.00, "seller": "GreenGuy", "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=300&q=80", "rating": "A+", "desc": "Hand-painted design.", "category": "Tops", "style": "Casual", "material": "Cotton"},
    {"id": 3, "title": "Chunky Knit Sweater", "price": 28.00, "seller": "RetroFit", "image": "https://images.unsplash.com/photo-1624835630669-6d843812543d?auto=format&fit=crop&w=300&q=80", "rating": "B", "desc": "100% Wool.", "category": "Tops", "style": "Vintage", "material": "Wool"},
    {"id": 4, "title": "Hemp Cargo Pants", "price": 30.00, "seller": "EcoWarrior", "image": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=300&q=80", "rating": "A", "desc": "Super durable.", "category": "Bottoms", "style": "Streetwear", "material": "Hemp"},
    {"id": 5, "title": "Floral Summer Dress", "price": 35.00, "seller": "LizzieLoops", "image": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=300&q=80", "rating": "A", "desc": "Upcycled fabric.", "category": "Dresses", "style": "Chic", "material": "Viscose"},
    {"id": 6, "title": "Retro Windbreaker", "price": 40.00, "seller": "OldSchoolCool", "image": "https://images.unsplash.com/photo-1610384104075-e05c8cf200c3?auto=format&fit=crop&w=300&q=80", "rating": "B+", "desc": "90s Original.", "category": "Outerwear", "style": "Streetwear", "material": "Polyester"},
    {"id": 7, "title": "Linen Trousers", "price": 55.00, "seller": "PureThreads", "image": "https://images.unsplash.com/photo-1584370848010-d7cc637703e6?auto=format&fit=crop&w=300&q=80", "rating": "A++", "desc": "Biodegradable.", "category": "Bottoms", "style": "Minimalist", "material": "Linen"},
    {"id": 8, "title": "Bucket Hat", "price": 12.00, "seller": "HatTrick", "image": "https://images.unsplash.com/photo-1575428652377-a2d80e2277fc?auto=format&fit=crop&w=300&q=80", "rating": "A", "desc": "Handmade.", "category": "Accessories", "style": "Streetwear", "material": "Cotton"},
    {"id": 9, "title": "Silk Scarf", "price": 20.00, "seller": "SilkySmooth", "image": "https://images.unsplash.com/photo-1584030373081-f37b7bb4fa8e?auto=format&fit=crop&w=300&q=80", "rating": "A", "desc": "Natural dyes.", "category": "Accessories", "style": "Chic", "material": "Silk"},
    {"id": 10, "title": "Patchwork Hoodie", "price": 60.00, "seller": "ReStitch", "image": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?auto=format&fit=crop&w=300&q=80", "rating": "A+", "desc": "Zero waste.", "category": "Tops", "style": "Streetwear", "material": "Cotton"},
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
    # Material Risk
    mat_lower = material.lower()
    if "polyester" in mat_lower or "nylon" in mat_lower or "acrylic" in mat_lower: base_risk += 30
    elif "organic" in mat_lower or "recycled" in mat_lower: base_risk += 5
    else: base_risk += 20
    
    # Origin Risk
    origin_lower = origin.lower()
    high_risk_origins = ["china", "bangladesh", "vietnam", "india", "cambodia"]
    if any(country in origin_lower for country in high_risk_origins): base_risk += 40
    elif "portugal" in origin_lower or "uk" in origin_lower or "italy" in origin_lower: base_risk += 10
    else: base_risk += 25
    
    return max(1, min(99, base_risk))

def scan_label_mock(image):
    """Simulates AI extraction if no API key is present."""
    time.sleep(1.5) 
    materials = ["Cotton", "Polyester", "Rayon", "Organic Cotton", "Nylon", "Denim", "Wool"]
    brands = ["FastFashionCo", "EcoThread", "UrbanTrend", "Shein-Like Brand", "H&M-Like Brand"]
    origins = ["Made in China", "Made in Bangladesh", "Made in Portugal", "Made in UK", "Made in Vietnam"]

    return {
        "material": random.choice(materials),
        "brand": random.choice(brands),
        "origin": random.choice(origins),
        "is_real": False
    }

def scan_label_real(image_file, api_key):
    """Uses Google Gemini to actually read the label. Tries multiple models."""
    # Configure API
    genai.configure(api_key=api_key)
    
    # List of models to try in order. If one fails (404), we try the next.
    models_to_try = [
        'gemini-1.5-flash', 
        'gemini-1.5-flash-latest', 
        'gemini-1.5-pro',
        'gemini-pro',  # The reliable fallback
        'gemini-pro-vision'
    ]
    
    last_error = None
    img = Image.open(image_file)
    
    prompt = """
    Analyze this clothing label. Extract the following information in strict format:
    1. Brand Name (if visible, otherwise say 'Unknown Brand')
    2. Country of Origin (e.g., Made in China)
    3. Primary Material (e.g., 100% Cotton, Polyester)
    
    Return the result as a simple string separated by pipes like this:
    Brand|Origin|Material
    """
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, img])
            text = response.text.strip()
            
            # Simple parsing
            parts = text.split('|')
            if len(parts) >= 3:
                return {
                    "brand": parts[0].strip(),
                    "origin": parts[1].strip(),
                    "material": parts[2].strip(),
                    "is_real": True
                }
        except Exception as e:
            last_error = e
            continue # Try the next model in the list
            
    # If the loop finishes and nothing worked:
    st.error(f"AI Connection Error (Tried all models): {str(last_error)}")
    return scan_label_mock(image_file)

def get_recommendations():
    """Logic to suggest items based on history and preferences."""
    all_items = pd.DataFrame(MARKETPLACE_ITEMS)
    user_styles = st.session_state.get('user_styles', [])
    scanned_materials = [s['material'] for s in st.session_state.scan_history] if st.session_state.scan_history else []
    
    scored_items = []
    
    for item in MARKETPLACE_ITEMS:
        score = 0
        if item['style'] in user_styles: score += 3
        
        # Loose matching for material
        for scan_mat in scanned_materials:
            if scan_mat.split(' ')[-1].lower() in item['material'].lower():
                score += 2
            
        scored_items.append((score, item))
    
    scored_items.sort(key=lambda x: x[0], reverse=True)
    top_picks = [item for score, item in scored_items if score > 0]
    
    if not top_picks: return random.sample(MARKETPLACE_ITEMS, 3)
    return top_picks[:3]

# ==========================================
# 3. STATE & STYLING
# ==========================================

if 'user_role' not in st.session_state: st.session_state.user_role = None
if 'subscription' not in st.session_state: st.session_state.subscription = 'Free'
if 'accessibility_mode' not in st.session_state: st.session_state.accessibility_mode = False
if 'scan_history' not in st.session_state: st.session_state.scan_history = []
if 'guest_scans' not in st.session_state: st.session_state.guest_scans = 0
if 'user_styles' not in st.session_state: st.session_state.user_styles = []
if 'api_key' not in st.session_state: st.session_state.api_key = ""

def inject_css():
    """Injects CSS based on accessibility settings."""
    is_access = st.session_state.accessibility_mode
    
    bg_color = "#FFFFFF" if is_access else "#FFEEDB" # Cream
    text_color = "#000000" if is_access else "#264653" # Deep Green
    accent_teal = "#2A9D8F"
    accent_coral = "#E76F51"
    
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg_color}; }}
        h1, h2, h3, h4 {{ color: {text_color} !important; font-family: 'Helvetica Neue', sans-serif; }}
        p, div, label, span, li {{ color: {text_color} !important; font-size: {"18px" if is_access else "16px"}; }}
        
        .stat-card {{
            background-color: white; padding: 20px; border-radius: 15px;
            border-left: 5px solid {accent_coral};
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;
        }}
        .shop-card {{
            background-color: white; border-radius: 15px; overflow: hidden;
            margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center; padding-bottom: 10px;
        }}
        .shop-card img {{
            width: 100%; height: 150px; object-fit: cover;
        }}
        .slogan-text {{
            text-align: center; font-style: italic; color: {accent_coral}; font-weight: bold;
        }}
        
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
    
    if st.session_state.user_role == 'Guest' and st.session_state.guest_scans >= 10:
        st.error("You've used your 10 free scans! Join Unstitched to continue.")
        return

    # --- API KEY HANDLING (SECRETS + INPUT) ---
    # 1. Try to get key from Streamlit Secrets (Cloud)
    if "GOOGLE_API_KEY" in st.secrets:
        st.session_state.api_key = st.secrets["GOOGLE_API_KEY"]
    
    # 2. If not in secrets, show input box
    if not st.session_state.api_key:
        with st.expander("⚙️ AI Settings (Required for Real Mode)", expanded=True):
            api_input = st.text_input("Enter Google Gemini API Key:", type="password")
            if api_input:
                st.session_state.api_key = api_input
                st.success("Key saved!")

    # --- INPUT METHOD SELECTION ---
    # Allowing toggle helps users on mobile default to the correct camera via the "Upload" dialog
    input_method = st.radio("Choose Input Method:", ["Live Camera", "Upload Photo"], horizontal=True, label_visibility="collapsed")

    img_file = None
    if input_method == "Live Camera":
        img_file = st.camera_input("Scan your clothing label")
    else:
        st.info("Tip: On mobile, 'Upload' lets you use your back camera easily.")
        img_file = st.file_uploader("Upload or take a photo", type=['jpg', 'jpeg', 'png'])
    
    if img_file:
        with st.spinner("AI is analyzing supply chain data..."):
            
            if st.session_state.api_key:
                # REAL SCAN
                data = scan_label_real(img_file, st.session_state.api_key)
            else:
                # MOCK SCAN (Fallback)
                data = scan_label_mock(img_file)
                
            risk = calculate_ethical_score(data['brand'], data['material'], data['origin'])
            
            if st.session_state.user_role == 'Guest':
                st.session_state.guest_scans += 1
            st.session_state.scan_history.append({"risk": risk, "brand": data['brand'], "material": data['material']})

        # --- RESULTS UI ---
        st.markdown(f"""
        <div class="stat-card">
            <h3 style="margin-top:0; color:#264653;">Analysis Results</h3>
            <p><strong>Brand:</strong> {data['brand']}</p>
            <p><strong>Origin:</strong> {data['origin']}</p>
            <p><strong>Material:</strong> {data['material']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not data.get('is_real'):
            st.caption("⚠️ Demo Mode. Add API key for real analysis.")
        
        col1, col2 = st.columns([3, 1])
        col1.progress(risk / 100)
        col2.metric("Risk", f"{risk}%")
        
        if risk > 60:
            st.error(f"⚠️ High Risk of Child Labour. {data['origin']} has known supply chain issues.")
            st.info(f"💡 We found better ethical items in the Shop based on this scan!")
        else:
            st.success("✅ Lower Risk. This item likely has a cleaner supply chain.")

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
    
    if st.button("Donate to Support Change"):
        render_donation_modal()

def render_donation_modal():
    with st.expander("💖 Make a Donation", expanded=True):
        st.write("Donations go to Unseen, Hope for Justice, and Save the Children.")
        c1, c2, c3 = st.columns(3)
        if c1.button("£2"): st.toast("Thank you for your £2 donation! 🎉")
        if c2.button("£5"): st.toast("Thank you for your £5 donation! 🎉")
        if c3.button("£10"): st.toast("Thank you for your £10 donation! 🎉")

def render_shop_item(item):
    st.markdown(f"""
    <div class="shop-card">
        <img src="{item['image']}" />
        <div style="padding: 10px;">
            <div style="font-weight: bold; font-size: 14px;">{item['title']}</div>
            <div style="color: #E76F51; font-weight: bold;">£{item['price']:.2f}</div>
            <div style="font-size: 10px; color: grey;">{item['desc']}</div>
            <span style="background-color: #2A9D8F; color: white; padding: 2px 8px; border-radius: 8px; font-size: 10px;">{item['rating']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_shop():
    st.header("🛍️ Simple Shop")
    
    # --- RECOMMENDATIONS SECTION ---
    st.subheader("Selected For You")
    st.caption("Based on your style and scan history")
    
    recommendations = get_recommendations()
    rec_cols = st.columns(len(recommendations))
    for i, item in enumerate(recommendations):
        with rec_cols[i]:
            render_shop_item(item)
            if st.button("View", key=f"rec_{item['id']}"):
                st.toast(f"Viewing {item['title']}")
                
    st.divider()

    # --- ALL ITEMS SECTION ---
    st.subheader("Browse All")
    col1, col2 = st.columns([3, 1])
    search = col1.text_input("Search items...", placeholder="Vintage denim, cotton tee...")
    sort_opt = col2.selectbox("Sort", ["Newest", "Price: Low to High"])

    # Filtering logic (basic)
    filtered_items = MARKETPLACE_ITEMS
    if search:
        filtered_items = [i for i in MARKETPLACE_ITEMS if search.lower() in i['title'].lower()]
    
    # Grid Layout
    cols = st.columns(2)
    for i, item in enumerate(filtered_items):
        with cols[i % 2]:
            render_shop_item(item)
            if st.button("Add to Bag", key=f"btn_{item['id']}"):
                st.toast(f"Added {item['title']} to cart!")

def render_notice_board():
    st.header("📌 Community Board")
    
    if st.session_state.subscription != 'Needles':
        st.warning("🔒 This area is for 'Needles' subscribers only.")
        st.image("https://placehold.co/600x200/E76F51/FFF?text=Join+Needles+to+Access", use_container_width=True)
        return

    st.subheader("Weekly Upcycling Competition")
    st.write("Theme: **Denim Transformation**")
    
    c1, c2 = st.columns(2)
    with c1: st.image("https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=300&q=80", caption="Before: Ripped Jeans")
    with c2: st.image("https://images.unsplash.com/photo-1598532163257-ae3c6b2524b6?auto=format&fit=crop&w=300&q=80", caption="After: Stylish Bag!")
    st.button("Vote for EcoWarrior99 ❤️")

def render_profile():
    st.header("👤 My Profile")
    
    st.subheader("Your Impact")
    if st.session_state.scan_history:
        df = pd.DataFrame(st.session_state.scan_history)
        safe_count = len(df[df['risk'] < 40])
        st.metric("Ethical Choices Made", safe_count, delta=f"{len(df)} total scans")
    else:
        st.info("Start scanning labels to track your impact!")

    st.divider()
    
    st.subheader("Subscription Status")
    if st.session_state.subscription == 'Free':
        st.markdown("**Current Plan: Free**")
        if st.button("Upgrade to Needles (£4.99/mo)"):
            st.session_state.subscription = 'Needles'
            st.balloons()
            st.rerun()
    else:
        st.success("You are a Needles Member! 🪡")
        st.caption("£1.50 of your sub goes to charity monthly.")

    st.divider()
    
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
            # Default mock styles for login
            st.session_state.user_styles = ["Vintage", "Casual"]
            st.rerun()
            
    with tab2:
        st.text_input("Name")
        st.date_input("Date of Birth")
        
        # New Recommendation Feature Input
        styles = st.multiselect("Your Style (for recommendations)", 
                              ["Vintage", "Streetwear", "Minimalist", "Chic", "Casual", "Boho"])
        
        if st.button("Join the Movement"):
            st.session_state.user_role = 'User'
            st.session_state.user_styles = styles
            st.rerun()
            
    st.divider()
    if st.button("Continue as Guest"):
        st.session_state.user_role = 'Guest'
        st.session_state.user_styles = []
        st.rerun()

# ==========================================
# 6. MAIN APP LOGIC
# ==========================================

if st.session_state.user_role is None:
    render_onboarding()
else:
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown(f"**Hello, {st.session_state.user_role}!**")
    with c2:
        access_label = "👁️" if not st.session_state.accessibility_mode else "Aa"
        if st.button(access_label, help="Toggle Accessibility Mode"):
            st.session_state.accessibility_mode = not st.session_state.accessibility_mode
            st.rerun()

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
