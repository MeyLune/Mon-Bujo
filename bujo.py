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

# --- 2. SUPER DESIGN (Rose & Sapin) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    
    .stApp {{
        background: linear-gradient(rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.4)), url("{fond_url}");
        background-size: cover;
        background-attachment: fixed;
    }}

    /* Boutons Roses */
    .stButton>button {{
        background-color: #f06292 !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }}

    /* Zones de texte blanches */
    div[data-baseweb="textarea"], div[data-baseweb="input"], .stTextArea textarea, .stTextInput input {{
        background-color: white !important;
        color: #1b3022 !important;
        -webkit-text-fill-color: #1b3022 !important;
        border-radius: 15px !important;
        border: 2px solid #f06292 !important;
    }}

    /* En-têtes et Titres Vert Sapin */
    h1, h2, h3, label {{ 
        color: #1b3022 !important; 
        font-family: 'Comfortaa', cursive; 
    }}

    .p-header {{ 
        background-color: #f06292 !important; 
        color: white !important; 
        padding: 8px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold;
    }}

    .cal-box {{
        font-family: 'Courier Prime', monospace !important;
        background-color: white; padding: 15px; border-radius: 0 0 12px 12px;
        color: #1b3022 !important; font-size: 16px !important;
        white-space: pre; display: flex; justify-content: center;
        border: 1px solid #f06292;
    }}

    .stTabs {{ background-color: rgba(255, 255, 255, 0.7) !important; border-radius: 20px; padding: 10px; }}
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

user_nom = st.session_state.user_data['Nom']
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- JOURNAL ---
with tabs[0]:
    st.markdown(f"### 🖋️ Mon Journal - {datetime.now().strftime('%d/%m/%Y')}")
    note_j = st.text_area("Aujourd'hui...", height=300, label_visibility="collapsed")
    if st.button("💾 Enregistrer la pensée"):
        if sh: sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), user_nom, note_j])
        st.success("Pensée sauvegardée ! ✨")

# --- SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️ Précédente"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("Suivante ➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {mois_fr[start_week.month-1]}</h3>", unsafe_allow_html=True)

    col_g, col_d = st.columns([3, 1.2])
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    with col_g:
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for k in range(2):
                if (i+k) < 7:
                    d = start_week + timedelta(days=i+k)
                    with cols[k]:
                        st.markdown(f'<div class="p-header">{jours[i+k]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        st.text_area("Note", height=100, key=f"note_{d}")
    with col_d:
        st.markdown('<div style="background:#fff9c4; padding:15px; border-radius:10px; border-left:5px solid #fbc02d; color:#5d4037;">🍎 <b>Menu</b></div>', unsafe_allow_html=True)
        [st.text_input(j[:3], key=f"menu_{j}") for j in jours]

# --- ANNEE ---
with tabs[2]:
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
    cat = st.radio("Sous-catégorie", ["🌿 Santé", "📖 Lecture"], horizontal=True)
    if cat == "📖 Lecture":
        st.markdown('<div style="background:#fdf5e6; padding:20px; border-radius:15px; border:1px solid #d2b48c;">', unsafe_allow_html=True)
        t_liv = st.text_input("TITRE")
        a_liv = st.text_input("AUTEUR")
        img = st.file_uploader("📸 Photo Couverture", type=['jpg','png','jpeg'])
        if img: st.image(img, width=150)
        c_s = st.columns(4)
        c_s[0].select_slider("💧 Triste", options=[1,2,3,4,5], key="l1")
        c_s[1].select_slider("🌶️ Spicy", options=[1,2,3,4,5], key="l2")
        c_s[2].select_slider("😊 Rire", options=[1,2,3,4,5], key="l3")
        c_s[3].select_slider("❤️ Love", options=[1,2,3,4,5], key="l4")
        if st.button("📥 Enregistrer le livre"):
            if sh and t_liv:
                sh.worksheet("Lectures").append_row([t_liv, a_liv, datetime.now().strftime("%d/%m/%Y")])
                st.success("Livre ajouté ! 📚")
        st.markdown('</div>', unsafe_allow_html=True)

# --- COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses")
    items_rapides = ["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]
    cols_c = st.columns(6)
    for i, it in enumerate(items_rapides):
        if cols_c[i].button(it):
            if sh: sh.worksheet("Courses").append_row([it, user_nom]); st.rerun()
    
    autre_item = st.text_input("➕ Ajouter manuellement :")
    if st.button("Ajouter à la liste"):
        if sh and autre_item:
            sh.worksheet("Courses").append_row([autre_item, user_nom]); st.rerun()

# --- STICKERS ---
with tabs[5]:
    st.markdown("### 🎨 Ma Planche")
    stickers_list = ["🌸", "🌿", "⭐", "🍃", "🍎", "🥑", "📅", "✨", "🎀", "🍪"]
    cols_s = st.columns(5)
    for i, s in enumerate(stickers_list):
        if cols_s[i % 5].button(s, key=f"stk_{i}"): st.balloons()
