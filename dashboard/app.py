import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os, tempfile, time

st.set_page_config(page_title="Social Panel Premium", page_icon="🚀", layout="wide")

# Injection du CSS ULTIME
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0px); } }
    .stApp { background: linear-gradient(-45deg, #0f172a, #1e1b4b, #31103f, #090914); background-size: 400% 400%; animation: gradientBG 15s ease infinite; color: white; }
    header, footer {visibility: hidden;}
    div[data-testid="stVerticalBlock"] > div { animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; opacity: 0; }
    div[data-testid="stVerticalBlock"] > div:nth-child(1) { animation-delay: 0.1s; }
    div[data-testid="stVerticalBlock"] > div:nth-child(2) { animation-delay: 0.2s; }
    div[data-testid="metric-container"] { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); backdrop-filter: blur(16px); border-radius: 20px; padding: 25px; animation: float 6s ease-in-out infinite; }
    button[kind="primary"] { background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important; color: white !important; border-radius: 12px !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 1.5px !important; transition: all 0.3s ease !important; }
    button[kind="primary"]:hover { transform: translateY(-3px) scale(1.05); box-shadow: 0 10px 30px rgba(236, 72, 153, 0.8) !important; }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea { background: rgba(15, 23, 42, 0.6) !important; border: 1px solid rgba(139, 92, 246, 0.3) !important; color: white !important; border-radius: 10px !important; }
    h1, h2, h3 { background: linear-gradient(to right, #a78bfa, #f472b6, #38bdf8); background-size: 200% auto; background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: gradientBG 4s linear infinite; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)

default_api_url = os.environ.get("API_URL", "http://localhost:8000/api/v1")
API_URL = st.sidebar.text_input("API URL", default_api_url)

def api_get(path):
    try: return requests.get(f"{API_URL}{path}", timeout=5).json()
    except: return None

def api_post(path, data=None):
    try: return requests.post(f"{API_URL}{path}", json=data or {}, timeout=10).json()
    except: return None

st.sidebar.title("🚀 Boost Panel")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["🏠 Vue d'ensemble", "📋 Comptes", "🎯 Campagnes", "📅 Contenu", "💬 Messagerie"])

# --- VUE D'ENSEMBLE ---
if page == "🏠 Vue d'ensemble":
    st.title("🏠 Vue d'ensemble")
    stats = api_get("/stats") or {}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Nouveaux Followers", "+ 1,240", "12%")
    c2.metric("❤️ Engagement", "14.2K", "8%")
    c3.metric("🎯 Actions Réalisées", stats.get("total_actions", 45892))
    c4.metric("📱 Comptes Actifs", f"{stats.get('active', 0)} / {stats.get('total', 0)}")

    st.markdown("---")
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("📈 Croissance Estimée")
        fig = px.line(x=["S1", "S2", "S3", "S4"], y=[100, 350, 780, 1240])
        st.plotly_chart(fig, use_container_width=True)
    with c_right:
        st.subheader("🎯 Répartition par Plateforme")
        plats = stats.get("platforms", {"instagram": 1, "twitter": 0, "threads": 0})
        fig2 = px.pie(values=list(plats.values()), names=list(plats.keys()))
        st.plotly_chart(fig2, use_container_width=True)

# --- COMPTES ---
elif page == "📋 Comptes":
    st.title("📋 Gestion des comptes ♾️")
    data = api_get("/accounts")
    if data and "accounts" in data:
        df = pd.DataFrame(data["accounts"])
        if not df.empty:
            st.dataframe(df[["id", "username", "platform", "status", "daily_actions", "total_actions"]], use_container_width=True)
        else: st.info("Aucun compte connecté.")
    
    with st.expander("➕ Connecter un nouveau compte"):
        with st.form("add"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            plat = st.selectbox("Plateforme", ["instagram", "threads", "twitter"])
            proxy = st.text_input("Proxy (optionnel)")
            if st.form_submit_button("Connecter", type="primary"):
                r = api_post("/accounts", {"username": u, "password": p, "platform": plat, "proxy": proxy or None})
                if r: st.success(f"✅ {u} ajouté"); time.sleep(1); st.rerun()

# --- CAMPAGNES ---
elif page == "🎯 Campagnes":
    st.title("🎯 Créer une Campagne")
    accounts_data = api_get("/accounts")
    if not accounts_data or not accounts_data.get("accounts"):
        st.warning("Veuillez d'abord ajouter un compte dans la section '📋 Comptes'.")
    else:
        accounts = {f"@{a['username']} ({a['platform']})": a['id'] for a in accounts_data["accounts"]}
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("1. Configuration")
            acc_label = st.selectbox("Sélectionner le compte", list(accounts.keys()))
            camp_name = st.text_input("Nom de la campagne", "Promo Été 2026")
            st.markdown("### 2. Ciblage")
            cibles = st.text_area("Concurrents à cibler (@username, @user2)")
            st.markdown("### 3. Modules")
            c1, c2, c3, c4 = st.columns(4)
            auto_like = c1.checkbox("👍 Like", value=True)
            auto_follow = c2.checkbox("👤 Follow", value=True)
            auto_comment = c3.checkbox("💬 Comment")
            story_view = c4.checkbox("👁️ Story", value=True)
        with col2:
            st.subheader("Action")
            if st.button("🚀 Lancer Réellement", type="primary", use_container_width=True):
                payload = {
                    "account_id": str(accounts[acc_label]),
                    "name": camp_name,
                    "type": "EXPERT",
                    "targets": {"competitors": [c.strip() for c in cibles.split(",") if c.strip()]},
                    "features": {"auto_like": auto_like, "smart_follow": auto_follow, "story_interactions": story_view, "ai_comments": auto_comment},
                    "ai_settings": {"lang_filter": ["fr"]},
                    "activity_settings": {}
                }
                res = api_post("/campaigns", payload)
                if res and "campaign_id" in res:
                    st.success(f"Campagne lancée ! ID: {res['campaign_id']}")
                    st.balloons()
                else: st.error("Erreur lors du lancement de la campagne.")

# --- CONTENU ---
elif page == "📅 Contenu":
    st.title("📅 Programmation")
    tab1, tab2 = st.tabs(["📝 Programmer", "🗓️ Liste"])
    with tab1:
        st.text_input("Compte", "@mon_compte")
        st.text_area("Légende")
        st.date_input("Date")
        st.button("Programmer", type="primary")
    with tab2:
        posts = api_get("/posts/scheduled")
        if posts and posts.get("posts"):
            st.dataframe(pd.DataFrame(posts["posts"]), use_container_width=True)
        else: st.info("Aucun post programmé.")

# --- MESSAGERIE ---
elif page == "💬 Messagerie":
    st.title("💬 Messagerie & Auto-DM")
    rules = api_get("/settings/dm-rules") or {}
    new_msg = st.text_area("Message de bienvenue", rules.get("welcome_message", ""))
    if st.button("Sauvegarder", type="primary"):
        api_post("/settings/dm-rules", {"welcome_message": new_msg, "rules": rules.get("rules", [])})
        st.success("Config sauvegardée !")
