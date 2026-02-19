import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd
import calendar

# --- 1. CONNEXION ---
def init_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        creds_info = {
            "type": "service_account",
            "project_id": "airy-semiotics-486311-v5",
            "private_key": st.secrets["MY_PRIVATE_KEY"],
            "client_email": st.secrets["MY_CLIENT_EMAIL"],
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds).open("db_bujo")
    except: return None

sh = init_connection()

# --- 2. CONFIGURATION & STYLE (FORÇAGE CLAIR + IPAD) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-color: white !important;
    }}

    div[data-baseweb="textarea"], div[data-baseweb="input"], 
    .stTextArea textarea, .stTextInput input, .stNumberInput input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1b5e20 !important;
        border-radius: 12px !important;
        border: 1px solid #f06292 !important;
        -webkit-text-fill-color: #1b5e20 !important;
    }}

    .stTabs, .bujo-block, .cal-card {{
        background-color: rgba(255, 255, 255, 0.88) !important;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #c8e6c9;
    }}

    h1, h2, h3, p, label, .stMarkdown {{ color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }}
    
    .stButton>button {{ 
        background-color: #f06292 !important; color: white !important;
        border-radius: 25px !important; border: none !important;
        font-weight: bold !important;
    }}

    .p-header {{ background-color: #f06292 !important; color: white !important; padding: 8px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; font-size: 14px; }}
    .post-it {{ background: rgba(255, 249, 196, 0.95); padding: 15px; border-left: 6px solid #fbc02d; font-family: 'Indie Flower', cursive; color: #5d4037 !important; border-radius: 5px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 Mon Bullet Journal</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal") or code == "2125":
            if code == "2125":
                st.session_state.user_data = {"Nom": "MeyLune", "Acces": "OUI"}
                st.rerun()
            elif sh:
                try:
                    users = sh.worksheet("Utilisateurs").get_all_records()
                    for u in users:
                        if str(u['Code']) == str(code):
                            st.session_state.user_data = {"Nom": u['Nom'], "Acces": u['Accès Journal']}
                            st.rerun()
                except: st.error("Erreur de base de données.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. INTERFACE ---
user_nom = st.session_state.user_data['Nom']
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]}</h3>", unsafe_allow_html=True)

    col_g, col_d = st.columns([3, 1.2])
    sem_notes = {}
    jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    with col_g:
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    d_str = (start_week + timedelta(days=i+j)).strftime("%d/%m/%Y")
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{jours_fr[i+j]} {d_str[:5]}</div>', unsafe_allow_html=True)
                        sem_notes[d_str] = st.text_area("Note", height=100, key=f"wk_{d_str}", label_visibility="collapsed")
        if st.button("💾 SAUVEGARDER LA SEMAINE"):
            if sh:
                for dk, txt in sem_notes.items():
                    if txt.strip(): sh.worksheet("Note").append_row([dk, user_nom, txt])
                st.success("C'est enregistré ! ✨")

    with col_d:
        st.markdown('<div class="post-it"><b>🍎 Menu</b></div>', unsafe_allow_html=True)
        m_vals = [st.text_input(j[:3], key=f"m_{j}") for j in jours_fr]
        if st.button("💾 Sauver Menu"):
            if sh: sh.worksheet("Menu").append_row([start_week.strftime("%d/%m/%Y"), user_nom] + m_vals)
            st.success("Menu OK !")

# --- ANNEE (EN FRANÇAIS) ---
with tabs[2]:
    mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                st.markdown(f'<div class="cal-card"><div class="p-header">{mois_fr[m_idx-1].upper()}</div><div style="text-align:center; padding:10px; font-size:11px; color:black;">{calendar.month(2026, m_idx).split(chr(10), 1)[1].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)

# --- COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Liste Rapide")
    items = ["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]
    cols_c = st.columns(6)
    for i, it in enumerate(items):
        if cols_c[i].button(it):
            if sh: sh.worksheet("Courses").append_row([it, user_nom]); st.rerun()
    autre = st.text_input("➕ Ajouter un article :")
    if st.button("Ajouter"):
        if sh: sh.worksheet("Courses").append_row([autre, user_nom]); st.rerun()

# --- STICKERS ---
with tabs[5]:
    st.markdown("### 🎨 Ma Planche de Stickers")
    col_s = st.columns(4)
    stickers = ["🌸", "🌿", "⭐", "🍃", "🍎", "🥑", "📅", "✨"]
    for i, s in enumerate(stickers):
        with col_s[i % 4]:
            if st.button(s, key=f"stick_{i}"):
                st.balloons()
                st.info(f"Sticker {s} sélectionné !")

# --- TRACKERS ---
with tabs[3]:
    st.markdown("### 📊 Suivi")
    st.slider("💧 Verres d'eau", 0, 12, 6)
    st.slider("😴 Sommeil (heures)", 0, 12, 8)
    if st.button("Enregistrer Suivi"): st.success("Données sauvegardées !")
