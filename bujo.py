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

# --- 2. DESIGN : ROSE PASTEL & VERT SAPIN (LISIBILITÉ MAX) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    
    .stApp {{
        background: linear-gradient(to bottom, rgba(255, 228, 230, 0.85), rgba(255, 255, 255, 0.95)), url("{fond_url}");
        background-size: cover;
        background-attachment: fixed;
    }}

    /* TEXTE VERT SAPIN FONCÉ */
    h1, h2, h3, p, label, .stMarkdown {{ 
        color: #1b3022 !important; 
        font-family: 'Comfortaa', cursive;
        font-weight: 700 !important;
    }}

    /* INPUTS BLANCS OPAQUES */
    div[data-baseweb="textarea"], div[data-baseweb="input"], 
    .stTextArea textarea, .stTextInput input {{
        background-color: white !important;
        color: #1b3022 !important;
        -webkit-text-fill-color: #1b3022 !important;
        border: 2px solid #1b3022 !important;
        border-radius: 12px !important;
    }}

    .stTabs {{ background-color: rgba(255, 255, 255, 0.8) !important; border-radius: 20px; padding: 15px; }}

    /* EN-TÊTES ROSES */
    .p-header {{ 
        background-color: #f06292 !important; 
        color: white !important; 
        padding: 8px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; 
    }}

    /* CALENDRIER ALIGNÉ */
    .cal-box {{
        font-family: 'Courier Prime', monospace !important;
        background-color: white;
        padding: 10px; border-radius: 0 0 10px 10px;
        line-height: 1.4; font-size: 16px !important;
        color: #1b3022 !important;
        white-space: pre; display: flex; justify-content: center;
        border: 1px solid #1b3022;
    }}

    .lecture-card {{
        background-color: #fdf5e6 !important;
        border: 2px solid #d2b48c !important;
        border-radius: 15px; padding: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 Bienvenue MeyLune</h1>", unsafe_allow_html=True)
    code = st.text_input("Code secret :", type="password")
    if st.button("Ouvrir mon journal") or code == "2125":
        st.session_state.user_data = {"Nom": "MeyLune"}
        st.rerun()
    st.stop()

# --- 4. NAVIGATION DES ONGLETS ---
user_nom = st.session_state.user_data['Nom']
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- JOURNAL ---
with tabs[0]:
    st.markdown(f"### 🖋️ Journal du {datetime.now().strftime('%d/%m/%Y')}")
    note_j = st.text_area("Note du jour", height=300, label_visibility="collapsed")
    if st.button("💾 Enregistrer dans le Sheet"):
        if sh: sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), user_nom, note_j])
        st.success("Pensée sauvegardée ! ✨")

# --- SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    
    col_n1, col_n2, col_n3 = st.columns([1, 2, 1])
    if col_n1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if col_n3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    col_n2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {mois_fr[start_week.month-1]}</h3>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 1.2])
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    with col_left:
        for i in range(0, 7, 2):
            c_s = st.columns(2)
            for k in range(2):
                if (i+k) < 7:
                    d = start_week + timedelta(days=i+k)
                    with c_s[k]:
                        st.markdown(f'<div class="p-header">{jours[i+k]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        st.text_area("Txt", height=100, key=f"s_{d}", label_visibility="collapsed")
    with col_right:
        st.markdown('<div style="background:#fff9c4; padding:10px; border-radius:10px; border-left:5px solid #fbc02d; color:#5d4037;">🍎 <b>Menu</b></div>', unsafe_allow_html=True)
        [st.text_input(j[:3], key=f"menu_{j}") for j in jours]

# --- ANNEE ---
with tabs[2]:
    st.markdown("<h2 style='text-align:center;'>Calendrier 2026</h2>", unsafe_allow_html=True)
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                tc = calendar.TextCalendar(firstweekday=0)
                cal_str = tc.formatmonth(2026, m_idx)
                clean_cal = "Lu Ma Me Je Ve Sa Di\n" + "\n".join(cal_str.splitlines()[2:])
                st.markdown(f'<div class="p-header">{mois_fr[m_idx-1].upper()}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="cal-box">{clean_cal}</div>', unsafe_allow_html=True)

# --- TRACKERS & LECTURE ---
with tabs[3]:
    sub_cat = st.radio("Mode", ["🌿 Santé", "📖 Lecture"], horizontal=True)
    if sub_cat == "📖 Lecture":
        st.markdown('<div class="lecture-card">', unsafe_allow_html=True)
        st.markdown("### 📖 Ma Fiche de Lecture")
        fl1, fl2 = st.columns([2, 1])
        with fl1:
            t_liv = st.text_input("TITRE")
            a_liv = st.text_input("AUTEUR")
            st.select_slider("NOTE / 10", options=list(range(1, 11)))
        with fl2:
            img = st.file_uploader("📸 Photo", type=['jpg','png','jpeg'])
            if img: st.image(img, width=150)
        
        st.markdown("---")
        cs1, cs2, cs3, cs4 = st.columns(4)
        triste = cs1.select_slider("💧 Triste", options=[1,2,3,4,5], key="t1")
        spicy = cs2.select_slider("🌶️ Spicy", options=[1,2,3,4,5], key="t2")
        rire = cs3.select_slider("😊 Rire", options=[1,2,3,4,5], key="t3")
        love = cs4.select_slider("❤️ Love", options=[1,2,3,4,5], key="t4")
        
        notes_l = st.text_area("🎵 Playlist & Citations")
        if st.button("📥 Enregistrer dans ma bibliothèque"):
            if sh and t_liv:
                sh.worksheet("Lectures").append_row([t_liv, a_liv, datetime.now().strftime("%d/%m/%Y"), spicy, love, notes_l])
                st.success("Livre ajouté ! 📚")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.slider("💧 Eau", 0, 10, 5)
        st.slider("😴 Sommeil", 0, 12, 8)

# --- COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Courses")
    items = ["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]
    cols_c = st.columns(6)
    for i, it in enumerate(items):
        if cols_c[i].button(it):
            if sh: sh.worksheet("Courses").append_row([it, user_nom]); st.rerun()
