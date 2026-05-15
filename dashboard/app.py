import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json, time, os, tempfile

st.set_page_config(page_title="Social Panel", page_icon="📊", layout="wide")

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

st.sidebar.title("📊 Social Panel")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", [
    "🏠 Vue d'ensemble", "📋 Comptes", "⚡ Actions", "📬 Poster", "📜 Routine"
])

# --- VUE D'ENSEMBLE ---
if page == "🏠 Vue d'ensemble":
    st.title("🏠 Vue d'ensemble")
    stats = api_get("/stats")
    if stats:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("📦 Total", stats.get("total", 0))
        c2.metric("✅ Actifs", stats.get("active", 0))
        c3.metric("🔴 Bannis", stats.get("banned", 0))
        c4.metric("🎯 Aujourd'hui", stats.get("today_actions", 0))
        c5.metric("📈 Total actions", stats.get("total_actions", 0))

        st.subheader("Répartition par plateforme")
        pf = stats.get("platforms", {})
        fig = px.bar(x=list(pf.keys()), y=list(pf.values()),
                     labels={"x": "Plateforme", "y": "Comptes"},
                     color=list(pf.keys()))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Statut des comptes")
        st = stats.get("statuses", {})
        fig2 = px.pie(values=list(st.values()), names=list(st.keys()))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.error("❌ Impossible de joindre l'API")

# --- COMPTES ---
elif page == "📋 Comptes":
    st.title("📋 Gestion des comptes")
    tabs = st.tabs(["📋 Liste", "➕ Ajouter", "📥 Import CSV", "🧪 Générer tests"])

    with tabs[0]:
        data = api_get("/accounts")
        if data and "accounts" in data:
            df = pd.DataFrame(data["accounts"])
            cols = ["id", "username", "platform", "status", "daily_actions", "total_actions", "tags"]
            avail = [c for c in cols if c in df.columns]
            st.data_editor(df[avail], use_container_width=True, height=500)
            st.caption(f"{len(df)} comptes")

            with st.expander("🗑️ Supprimer un compte"):
                del_id = st.number_input("ID du compte", 1, 9999, 1)
                if st.button("Supprimer", type="primary"):
                    r = api_delete(f"/accounts/{del_id}")
                    if r:
                        st.success("Supprimé !")
                        time.sleep(0.5)
                        st.rerun()
        else:
            st.warning("Aucun compte")

    with tabs[1]:
        with st.form("add"):
            c1, c2 = st.columns(2)
            with c1:
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                plat = st.selectbox("Plateforme", ["instagram", "threads", "twitter"])
            with c2:
                proxy = st.text_input("Proxy (optionnel)")
                tags = st.text_input("Tags (séparés par ,)")
            if st.form_submit_button("➕ Ajouter", type="primary"):
                r = api_post("/accounts", {
                    "username": u, "password": p, "platform": plat,
                    "proxy": proxy or None,
                    "tags": [t.strip() for t in tags.split(",")] if tags else []
                })
                if r:
                    st.success(f"✅ {u} ajouté")
                    st.rerun()

    with tabs[2]:
        f = st.file_uploader("Fichier CSV", type="csv")
        if f:
            st.write("Format attendu : username,password,platform,proxy,tags")
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            tmp.write(f.getvalue())
            tmp.close()
            r = api_post("/accounts/import", files={"file": open(tmp.name, "rb")})
            if r:
                st.success(f"✅ {r.get('count', 0)} comptes importés")
                st.rerun()

    with tabs[3]:
        if st.button("🧪 Générer 50 comptes de test"):
            import sys
            sys.path.insert(0, ".")
            from scripts.generate_test_accounts import generate
            generate(50)
            st.success("✅ 50 comptes générés")
            st.rerun()

# --- ACTIONS ---
elif page == "⚡ Actions":
    st.title("⚡ Actions en masse")
    act = st.selectbox("Type d'action", ["like", "comment", "follow", "twitter_like", "twitter_follow"])
    target = st.text_input("Cible (hashtag sans # ou username)", "photography")
    amt = st.slider("Par compte", 1, 30, 5)

    data = api_get("/accounts")
    if data and "accounts" in data:
        opts = {f"{a['username']} (#{a['id']})": a["id"]
                for a in data["accounts"] if a.get("active") and a["status"] == "active"}
        sel = st.multiselect("Comptes", list(opts.keys()), default=list(opts.keys())[:5] if len(opts) >= 5 else list(opts.keys()))
        ids = [opts[s] for s in sel]

        if st.button("🚀 Lancer", type="primary", use_container_width=True):
            r = api_post("/actions/bulk", {"account_ids": ids, "action": act, "target": target, "amount": amt})
            if r:
                st.success(f"✅ Lancé sur {len(ids)} comptes")
                st.json(r)

# --- POSTER ---
elif page == "📬 Poster":
    st.title("📬 Poster du contenu")
    data = api_get("/accounts")
    if data and "accounts" in data:
        for plat in ["instagram", "threads", "twitter"]:
            accs = [a for a in data["accounts"] if a["platform"] == plat and a.get("active") and a["status"] == "active"]
            if accs:
                with st.expander(f"{'📸' if plat=='instagram' else '🧵' if plat=='threads' else '🐦'} {plat.title()}"):
                    opts = {a["username"]: a["id"] for a in accs}
                    sel = st.selectbox("Compte", list(opts.keys()), key=f"post_{plat}")
                    text = st.text_area("Texte", height=100, key=f"txt_{plat}")
                    if st.button("Publier", key=f"btn_{plat}", type="primary"):
                        r = api_post("/posts", {"account_id": opts[sel], "text": text, "platform": plat})
                        if r and r.get("status") == "posted":
                            st.success(f"✅ Publié sur {sel}")
                        else:
                            st.error("❌ Échec")

# --- ROUTINE ---
elif page == "📜 Routine":
    st.title("📜 Lancer une routine")
    data = api_get("/accounts")
    if data and "accounts" in data:
        opts = {f"{a['username']} (#{a['id']}) [{a['platform']}]": a["id"]
                for a in data["accounts"] if a.get("active")}
        sel = st.selectbox("Compte", list(opts.keys()))
        aid = opts[sel]
        if st.button("▶️ Lancer la routine maintenant", type="primary", use_container_width=True):
            r = api_post(f"/accounts/{aid}/run", {})
            if r:
                st.success("✅ Routine en file d'attente")
                st.json(r)
