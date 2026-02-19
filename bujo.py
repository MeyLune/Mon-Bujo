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

# --- 2. DESIGN GLOBAL ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    [data-testid="stSidebar"] { display: none; }
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    
    h1, h2, h3, p, label, .stMarkdown { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }
    
    /* Input & Boutons */
    div[data-baseweb="input"], .stTextArea textarea, .stTextInput input {
        background-color: white !important;
        border: 2px solid #c8e6c9 !important;
        border-radius: 12px !important;
        color: #1b5e20 !important;
    }

    .stButton>button { 
        background-color: #1b5e20 !important; 
        border-radius: 20px !important; 
        border: none !important;
        padding: 5px 20px !important;
    }
    .stButton>button p { color: white !important; font-weight: bold !important; }

    /* Grille Semaine */
    .p-header { background-color: #f06292; color: white !important; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    
    /* Cartes Calendrier (Correction du Noir) */
    .cal-card {
        background-color: white;
        border: 2px solid #f8bbd0;
        border-radius: 15px;
        overflow: hidden;
        margin-bottom: 20px;
    }
    .cal-card-header {
        background-color: #f06292;
        color: white !important;
        text-align: center;
        padding: 5px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .cal-card-body {
        padding: 10px;
        font-family: monospace;
        text-align: center;
        color: #1b5e20;
        line-height: 1.4;
    }
    
    .post-it { 
        background: #fff9c4; padding: 20px; border-left: 6px solid #fbc02d; 
        font-family: 'Indie Flower', cursive; font-size: 1.2rem; color: #5d4037 !important; 
        border-radius: 4px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .bujo-block { background: white; padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code = st.text_input("Code secret :", type="password")
        if st.button("Entrer"):
            if code == "2125": st.session_state.user_data = {"Nom": "MeyLune"}; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
user = st.session_state.user_data
st.title(f"Journal de {user['Nom']}")
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ONGLET 1 : JOURNAL ---
with tabs[0]:
    st.markdown(f"### ✨ Aujourd'hui, {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown('<div class="post-it">Écris tes gratitudes ou pensées du jour...</div>', unsafe_allow_html=True)
    note_txt = st.text_area("", placeholder="Cher journal...", height=150, key="j_note")
    if st.button("Sauvegarder ma pensée"):
        sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), note_txt])
        st.success("Enregistré ! ✨")

# --- ONGLET 2 : SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(
