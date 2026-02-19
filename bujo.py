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

# --- 2. STYLE & FIX ALIGNEMENT (IPAD OPTIMIZ) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&family=Courier+Prime&display=swap');
    
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-attachment: fixed;
        background-color: white !important;
    }}

    /* Forçage du thème clair pour éviter le noir des captures */
    div[data-baseweb="textarea"], div[data-baseweb="input"], .stTextArea textarea, .stTextInput input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #5d4037 !important;
        -webkit-text-fill-color: #5d4037 !important;
        border: 1.5px solid #f06292 !important;
        border-radius: 15px !important;
    }}

    /* Alignement parfait du calendrier */
    .cal-box {{
        font-family: 'Courier Prime', monospace !important;
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        line-height: 1.4;
        font-size: 16px !important;
        white-space: pre;
        display: flex;
        justify-content: center;
    }}

    .lecture-card {{
        background-color: #fdf5e6 !important;
        border: 2px solid #d2b48c !important;
        border-radius: 15px;
        padding: 20px;
    }}

    .p-header {{ 
        background-color: #f06292 !important; 
        color: white !important; 
        padding: 10px; 
        text-align: center; 
        border-radius: 12px 12px 0 0; 
        font-weight: bold; 
    }}

    h1, h2, h3, label {{ color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    code = st.text_input("Entre ton code secret :", type="password")
    if st.button("Ouvrir mon journal") or code == "2125":
        st.session_state.user_data = {"Nom": "MeyLune"}
        st.rerun()
    st.stop()

user_nom = st.session_state.user_data['Nom']
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- JOURNAL ---
with tabs[0]:
    st.markdown(f"### 🖋️ Pensées du {datetime.now().strftime('%d/%m/%Y')}")
    note_j = st.text_area("Aujourd'hui...", height=300, label_visibility="collapsed")
    if st.button("💾 Enregistrer"):
        if sh: sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), user_nom, note_j])
        st.success("Enregistré ! ✨")

# --- SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    
    mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {mois_fr[start_week.month-1]} {start_week.year}</h3>", unsafe_allow_html=True)

    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    col_g, col_d = st.columns([3, 1.2])
    with col_g:
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    d = start_week + timedelta(days=i+j)
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{jours[i+j]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        st.text_area("Note", height=100, key=f"wk_{d}", label_visibility="collapsed")
    with col_d:
        st.markdown('<div class="post-it">🍎 <b>Menu</b></div>', unsafe_allow_html=True)
        [st.text_input(j[:3], key=f"m_{j}") for j in jours]

# --- ANNEE (FIX ALIGNEMENT) ---
with tabs[2]:
    st.markdown("<h2 style='text-align:center;'>Calendrier 2026</h2>", unsafe_allow_html=True)
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                # On utilise TextCalendar pour un alignement parfait
                tc = calendar.TextCalendar(firstweekday=0)
                cal_str = tc.formatmonth(2026, m_idx)
                lines = cal_str.splitlines()
                # On nettoie pour n'avoir que les jours et les dates
                clean_cal = "Lu Ma Me Je Ve Sa Di\n" + "\n".join(lines[2:])
                
                st.markdown(f'<div class="p-header">{mois_fr[m_idx-1].upper()}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="cal-box">{clean_cal}</div>', unsafe_allow_html=True)

# --- TRACKERS & LECTURE ---
with tabs[3]:
    cat = st.radio("Mode", ["📊 Santé", "📖 Lecture"], horizontal=True)
    if cat == "📖 Lecture":
        st.markdown('<div class="lecture-card">', unsafe_allow_html=True)
        st.markdown("### 📖 Ma Fiche de Lecture")
        cl1, cl2 = st.columns([2, 1])
        with cl1:
            t_l = st.text_input("TITRE")
            a_l = st.text_input("AUTEUR")
            st.select_slider("NOTE / 10", options=list(range(1, 11)))
        with cl2:
            img = st.file_uploader("📸 Photo", type=['jpg','png'])
            if img: st.image(img, width=120)
        
        st.markdown("---")
        # Les curseurs comme sur ta capture
        c_s1, c_s2, c_s3, c_s4 = st.columns(4)
        c_s1.select_slider("💧 Triste", options=[1,2,3,4,5])
        c_s2.select_slider("🌶️ Spicy", options=[1,2,3,4,5])
        c_s3.select_slider("😊 Rire", options=[1,2,3,4,5])
        c_s4.select_slider("❤️ Love", options=[1,2,3,4,5])
        
        st.text_area("🎵 Playlist & Notes")
        if st.button("📥 Enregistrer le livre"):
            if sh and t_l:
                sh.worksheet("Lectures").append_row([t_l, a_l, datetime.now().strftime("%d/%m/%Y")])
                st.success("Livre ajouté !")
        st.markdown('</div>', unsafe_allow_html=True)
