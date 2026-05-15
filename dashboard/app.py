import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os, tempfile, time

st.set_page_config(page_title="Social Panel Premium", page_icon="🚀", layout="wide")

# Injection du CSS ULTIME (Animations, Gradients mouvants, Glassmorphism avancé)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Animation du fond d'écran */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Animation d'entrée des éléments */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Pulsation lumineuse pour les boutons */
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 10px rgba(139, 92, 246, 0.4); }
        50% { box-shadow: 0 0 25px rgba(236, 72, 153, 0.8); }
        100% { box-shadow: 0 0 10px rgba(139, 92, 246, 0.4); }
    }

    /* Animation flottante */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e1b4b, #31103f, #090914);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: white;
    }
    
    header, footer {visibility: hidden;}
    
    /* Application de l'animation d'entrée en cascade */
    div[data-testid="stVerticalBlock"] > div {
        animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        opacity: 0;
    }
    div[data-testid="stVerticalBlock"] > div:nth-child(1) { animation-delay: 0.1s; }
    div[data-testid="stVerticalBlock"] > div:nth-child(2) { animation-delay: 0.2s; }
    div[data-testid="stVerticalBlock"] > div:nth-child(3) { animation-delay: 0.3s; }
    div[data-testid="stVerticalBlock"] > div:nth-child(4) { animation-delay: 0.4s; }
    
    /* Cartes (Metrics) avec effet Neon & Float */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: float 6s ease-in-out infinite;
    }
    /* Décalage temporel pour le flottement des cartes */
    div[data-testid="metric-container"]:nth-child(odd) { animation-delay: 1s; }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-10px) scale(1.03);
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(236, 72, 153, 0.5);
        box-shadow: 0 20px 40px -10px rgba(236, 72, 153, 0.4);
    }
    
    /* Boutons Primaires Ultra Modernes */
    button[kind="primary"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        animation: pulseGlow 3s infinite;
    }
    button[kind="primary"]:hover {
        transform: translateY(-3px) scale(1.05);
        background: linear-gradient(135deg, #7c3aed 0%, #db2777 100%) !important;
        box-shadow: 0 10px 30px rgba(236, 72, 153, 0.8) !important;
    }
    
    /* Inputs avec lueur */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        color: white !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within, .stTextArea textarea:focus {
        border-color: #ec4899 !important;
        box-shadow: 0 0 15px rgba(236, 72, 153, 0.3) !important;
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(10, 10, 20, 0.85) !important;
        backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Titres avec gradient animé */
    h1, h2, h3 {
        background: linear-gradient(to right, #a78bfa, #f472b6, #38bdf8);
        background-size: 200% auto;
        color: #000;
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientBG 4s linear infinite;
        font-weight: 800 !important;
    }
    
    /* Customiser les onglets */
    button[data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: rgba(139, 92, 246, 0.2) !important;
        border-radius: 8px !important;
        border-bottom: 3px solid #ec4899 !important;
    }
</style>
""", unsafe_allow_html=True)

default_api_url = os.environ.get("API_URL", "http://localhost:8000/api/v1")
API_URL = st.sidebar.text_input("API URL", default_api_url)

def api_get(path):
    try:
        return requests.get(f"{API_URL}{path}", timeout=5).json()
    except:
        return None

def api_post(path, data=None, files=None):
    try:
        if files:
            return requests.post(f"{API_URL}{path}", files=files, timeout=15).json()
        return requests.post(f"{API_URL}{path}", json=data or {}, timeout=10).json()
    except:
        return None

def api_delete(path):
    try:
        return requests.delete(f"{API_URL}{path}", timeout=5).json()
    except:
        return None

st.sidebar.title("🚀 Boost Panel")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", [
    "🏠 Vue d'ensemble", 
    "📋 Comptes", 
    "🎯 Campagnes", 
    "📅 Contenu & Calendrier",
    "💬 Messagerie & Auto-DM"
])

# --- VUE D'ENSEMBLE ---
if page == "🏠 Vue d'ensemble":
    st.title("🏠 Vue d'ensemble")
    
    # Fake premium stats for demo
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Nouveaux Followers (30j)", "+ 1,240", "12%")
    c2.metric("❤️ Engagement (30j)", "14.2K", "8%")
    c3.metric("🎯 Actions Réalisées", "45,892")
    
    # Calculate real active accounts or fake it for demo
    total_accs = "0"
    try:
        data = api_get("/stats")
        if data:
            total_accs = str(data.get("active", 8))
    except:
        pass
    c4.metric("📱 Comptes Actifs", f"{total_accs} (Illimité)")

    st.markdown("---")
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("📈 Croissance Estimée")
        fig = px.line(x=["Semaine 1", "Semaine 2", "Semaine 3", "Semaine 4"], 
                      y=[100, 350, 780, 1240], 
                      labels={"x": "Temps", "y": "Followers"})
        st.plotly_chart(fig, use_container_width=True)
    with c_right:
        st.subheader("🎯 Performances des Campagnes")
        fig2 = px.pie(values=[45, 25, 20, 10], names=["Expert (IG)", "Smart (IG)", "Twitter Boost", "Threads"])
        st.plotly_chart(fig2, use_container_width=True)


# --- COMPTES ---
elif page == "📋 Comptes":
    st.title("📋 Gestion des comptes (Illimité) ♾️")
    data = api_get("/accounts")
    if data and "accounts" in data:
        df = pd.DataFrame(data["accounts"])
        if not df.empty:
            cols = ["id", "username", "platform", "status", "daily_actions", "total_actions"]
            avail = [c for c in cols if c in df.columns]
            st.dataframe(df[avail], use_container_width=True)
        else:
            st.info("Aucun compte connecté.")
    
    with st.expander("➕ Connecter un nouveau compte"):
        with st.form("add"):
            c1, c2 = st.columns(2)
            with c1:
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                plat = st.selectbox("Plateforme", ["instagram", "threads", "twitter"])
            with c2:
                proxy = st.text_input("Proxy (optionnel)")
                tags = st.text_input("Tags (séparés par ,)")
            if st.form_submit_button("Connecter", type="primary"):
                r = api_post("/accounts", {
                    "username": u, "password": p, "platform": plat,
                    "proxy": proxy or None,
                    "tags": [t.strip() for t in tags.split(",")] if tags else []
                })
                if r:
                    st.success(f"✅ {u} ajouté")
                    time.sleep(1)
                    st.rerun()


# --- CAMPAGNES ---
elif page == "🎯 Campagnes":
    st.title("🎯 Créer une Campagne d'Acquisition")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("1. Configuration")
        camp_name = st.text_input("Nom de la campagne", "Campagne Été 2026")
        camp_type = st.radio("Type de campagne", ["🤖 SMART (IA Automatique - 100 cibles/j)", "🎯 EXPERT (Ciblage Manuel - 150 cibles/j)"], horizontal=True)
        
        st.markdown("### 2. Ciblage")
        if "EXPERT" in camp_type:
            cibles_concurrents = st.text_area("Concurrents à cibler (usernames sans @)")
            cibles_hashtags = st.text_area("Hashtags de niche (sans #)")
            cibles_lieux = st.text_input("Localisation (ex: Paris, France)")
        else:
            st.info("L'IA analysera votre profil et ciblera automatiquement les utilisateurs les plus pertinents de votre niche.")
            niche = st.text_input("Mots-clés de votre niche (ex: mode, fitness, tech)")
            
        st.markdown("### 3. Fonctionnalités Activées")
        c1, c2, c3, c4 = st.columns(4)
        auto_like = c1.checkbox("👍 Auto-Like", value=True)
        auto_follow = c2.checkbox("👤 Auto-Follow", value=True)
        auto_comment = c3.checkbox("💬 Auto-Comment")
        story_view = c4.checkbox("👁️ Story View", value=True)
        
        c5, c6, c7, c8 = st.columns(4)
        auto_dm = c5.checkbox("💌 Welcome DM")
        auto_unfollow = c6.checkbox("♻️ Auto-Unfollow")
        analytics = c7.checkbox("📊 Analytics+")
        safe_mode = c8.checkbox("🛡️ Safe Mode (Anti-Ban)", value=True)

    with col2:
        st.subheader("Aperçu")
        st.info(f"**Nom:** {camp_name}\n\n**Mode:** {camp_type.split(' ')[0]}\n\n**Croissance est.:** Très rapide 🚀\n\n**Risque:** {'Faible' if safe_mode else 'Moyen'}")
        
        if st.button("🚀 Lancer la Campagne", type="primary", use_container_width=True):
            st.success("Campagne enregistrée ! (Simulation UI)")
            st.balloons()


# --- CONTENU ---
elif page == "📅 Contenu & Calendrier":
    st.title("📅 Gestion de Contenu")
    
    tabs = st.tabs(["📝 Programmer un Post", "🗓️ Calendrier", "📱 Aperçu du Grid"])
    
    with tabs[0]:
        st.subheader("Nouveau Post / Reel")
        col_img, col_txt = st.columns(2)
        with col_img:
            st.file_uploader("Importer une photo/vidéo", type=["jpg", "png", "mp4"])
        with col_txt:
            st.text_area("Légende", height=150)
            st.date_input("Date de publication")
            st.time_input("Heure de publication")
            st.button("📅 Programmer", type="primary")
            
    with tabs[1]:
        st.subheader("Planning de la semaine")
        st.info("Un calendrier interactif sera bientôt affiché ici (intégration en cours).")
        
    with tabs[2]:
        st.subheader("Aperçu du Profil (Grid Preview)")
        st.image("https://via.placeholder.com/600x400.png?text=Grid+Preview+Placeholder", use_container_width=True)


# --- MESSAGERIE ---
elif page == "💬 Messagerie & Auto-DM":
    st.title("💬 Boîte de réception & Auto-Reply")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Conversations")
        st.selectbox("Filtrer par compte", ["MonCompte_Pro", "Agence_Test"])
        st.button("📥 Inbox: Client A", use_container_width=True)
        st.button("📥 Inbox: Prospect B", use_container_width=True)
        st.button("📥 Inbox: Partenaire C", use_container_width=True)
        
    with col2:
        st.subheader("Chat")
        st.chat_message("user").write("Bonjour, je suis intéressé par vos services !")
        st.chat_message("assistant").write("Bonjour ! Laissez-moi vous envoyer notre brochure.")
        st.chat_input("Écrire un message...")
        
    st.markdown("---")
    st.subheader("🤖 Auto-Reply & Welcome DM")
    st.checkbox("Activer l'envoi d'un DM à chaque nouveau follower")
    st.text_area("Message de bienvenue", "Salut ! Merci pour le follow. Voici un code promo de 10% : BIENVENUE10")
    st.button("Enregistrer les règles", type="primary")
