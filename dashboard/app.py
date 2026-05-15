import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os, tempfile, time

st.set_page_config(page_title="Social Panel Premium", page_icon="🚀", layout="wide")

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
    c4.metric("📱 Comptes Actifs", "8 / 10")

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
    st.title("📋 Gestion des comptes (Limite: 10)")
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
