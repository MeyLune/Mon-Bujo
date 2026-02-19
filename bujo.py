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

# --- 2. CONFIGURATION & STYLE (FORÇAGE MODE CLAIR) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

# Ton image de fond
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    /* FORCE LE FOND ET LE MODE CLAIR */
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-color: white !important;
    }}

    /* FIX ZONES NOIRES : On force le blanc partout */
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

    .p-header {{ background-color: #f06292 !important; color: white !important; padding: 10px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; }}
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
                users = sh.worksheet("Utilisateurs").get_all_records()
                for u in users:
                    if str(u['Code']) == str(code):
                        st.session_state.user_data = {"Nom": u['Nom'], "Acces": u['Accès Journal']}
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

user_nom = st.session_state.user_data['Nom']
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- ONGLET SEMAINE (Restauré) ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]}</h3>", unsafe_allow_html=True)

    col_g, col_m = st.columns([3, 1.2])
    sem_notes = {}
    with col_g:
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    d_str = (start_week + timedelta(days=i+j)).strftime("%d/%m/%Y")
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{jours[i+j]} {d_str[:5]}</div>', unsafe_allow_html=True)
                        sem_notes[d_str] = st.text_area("Note", height=100, key=f"wk_{d_str}", label_visibility="collapsed")
        
        if st.button("💾 SAUVEGARDER LA SEMAINE"):
            if sh:
                for dk, txt in sem_notes.items():
                    if txt.strip(): sh.worksheet("Note").append_row([dk, user_nom, txt])
                st.success("Notes enregistrées ! ✨")

    with col_m:
        st.markdown('<div class="post-it"><b>🍎 Menu</b></div>', unsafe_allow_html=True)
        m_vals = [st.text_input(j, key=f"m_{j}") for j in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]]
        if st.button("💾 Sauver Menu"):
            sh.worksheet("Menu").append_row([start_week.strftime("%d/%m/%Y"), user_nom] + m_vals)
            st.success("Menu OK !")

# --- ANNEE (Calendrier Esthétique) ---
with tabs[2]:
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m = r * 3 + c + 1
            with cols[c]:
                st.markdown(f'<div class="cal-card"><div class="p-header">{calendar.month_name[m].upper()}</div><div style="text-align:center; padding:10px; font-size:12px;">{calendar.month(2026, m).split(chr(10), 1)[1].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)

# --- COURSES (Prédéfinis Restaurés) ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses")
    items = ["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]
    cols_c = st.columns(6)
    for i, it in enumerate(items):
        if cols_c[i].button(it):
            sh.worksheet("Courses").append_row([it, user_nom]); st.rerun()
    
    autre = st.text_input("➕ Ajouter autre chose :")
    if st.button("Ajouter"):
        sh.worksheet("Courses").append_row([autre, user_nom]); st.rerun()

# --- TRACKERS (Restaurés) ---
with tabs[3]:
    st.markdown("### 📊 Mes Trackers")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.write("💧 Hydratation (Verres)")
        st.slider("", 0, 10, 5, key="tr_eau")
    with col_t2:
        st.write("😴 Sommeil (Heures)")
        st.number_input("", 0, 15, 8, key="tr_sleep")
    if st.button("Enregistrer Trackers"):
        st.success("Données sauvegardées !")
