import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd
import calendar

# --- 1. CONNEXION À GOOGLE SHEETS ---
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
    except: 
        return None

sh = init_connection()

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

# LIEN DE L'IMAGE (Corrigé pour éviter le bug de l'espace et le flou)
# On utilise l'URL brute (raw) de votre GitHub
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

# --- 3. DESIGN GLOBAL (CSS) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    /* APPLICATION DU FOND D'ÉCRAN */
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-position: center center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }}

    /* Suppression des éléments noirs de Streamlit */
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    [data-testid="stSidebar"] {{ display: none; }}
    footer {{visibility: hidden;}}

    /* Blocs blancs translucides pour iPad */
    .stTabs, .bujo-block, div[data-baseweb="textarea"], div[data-baseweb="input"], .stMarkdown {{
        background-color: rgba(255, 255, 255, 0.88) !important;
        border-radius: 20px !important;
        border: 1px solid #e1f5fe !important;
        color: #1b5e20 !important;
    }}

    /* Forcer la couleur du texte et supprimer le noir */
    h1, h2, h3, p, label, textarea, input {{ 
        color: #1b5e20 !important; 
        font-family: 'Comfortaa', cursive; 
    }}

    /* Style des boutons roses */
    .stButton>button {{ 
        background-color: #f06292 !important; 
        color: white !important; 
        border-radius: 25px !important; 
        border: none !important;
        padding: 10px 25px !important;
        font-weight: bold;
    }}

    /* Onglets de navigation */
    button[data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.6) !important;
        border-radius: 12px 12px 0 0 !important;
        color: #1b5e20 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: #f06292 !important;
        color: white !important;
    }}

    /* Le Post-it */
    .post-it {{ 
        background: rgba(255, 249, 196, 0.95); 
        padding: 20px; 
        border-left: 6px solid #fbc02d; 
        font-family: 'Indie Flower', cursive; 
        font-size: 1.2rem; 
        color: #5d4037 !important; 
        border-radius: 5px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }}
</style>
""", unsafe_allow_html=True)

# --- 4. SYSTÈME DE SÉCURITÉ (CODE PIN) ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        st.markdown('<div class="bujo-block" style="padding:30px;">', unsafe_allow_html=True)
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal"):
            if code == "2125": 
                st.session_state.user_data = {"Nom": "MeyLune"}
                st.rerun()
            else:
                st.error("Code incorrect 🌸")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 5. CONTENU PRINCIPAL ---
user = st.session_state.user_data
st.title(f"🌸 Journal de {user['Nom']}")
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ONGLET 1 : JOURNAL ---
with tabs[0]:
    st.markdown(f"### ✨ Aujourd'hui, {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown('<div class="post-it">Quelles sont tes gratitudes aujourd\'hui ?</div>', unsafe_allow_html=True)
    note_txt = st.text_area("", placeholder="Cher journal...", height=250, key="j_note", label_visibility="collapsed")
    if st.button("Sauvegarder ma pensée"):
        if note_txt and sh:
            sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), note_txt])
            st.success("Enregistré dans le cloud ! ✨")

# --- ONGLET 2 : SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c_n1, c_n2, c_n3 = st.columns([1, 2, 1])
    if c_n1.button("⬅️ Précédente"): st.session_state.w_off -= 1; st.rerun()
    if c_n3.button("Suivante ➡️"): st.session_state.w_off += 1; st.rerun()
    c_n2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)

    col_g, col_m = st.columns([3, 1])
    with col_g:
        days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    day_date = start_week + timedelta(days=i+j)
                    d_str = day_date.strftime("%d/%m/%Y")
                    with cols[j]:
                        st.markdown(f'<div style="background:#f06292; color:white; padding:8px; border-radius:10px 10px 0 0; text-align:center; font-weight:bold;">{days_fr[i+j]} {day_date.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        st.text_area(f"Note_{d_str}", height=100, key=f"in_{d_str}", label_visibility="collapsed")
    with col_m:
        st.markdown('<div class="post-it"><b>🍎 Menu</b></div>', unsafe_allow_html=True)
        for jour in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]:
            st.text_input(jour, key=f"m_{jour}_{st.session_state.w_off}")

# --- ONGLET 3 : ANNEE ---
with tabs[2]:
    st.markdown("### 📅 Calendrier 2026")
    for r in range(4):
        cols_c = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_c[c]:
                st.markdown(f"""
                <div class="bujo-block" style="text-align:center;">
                    <div style="color:#f06292; font-weight:bold; margin-bottom:10px;">{calendar.month_name[m_idx].upper()}</div>
                    <pre style="font-family:monospace; font-size:11px; line-height:1.1;">{calendar.month(2026, m_idx).split(chr(10), 1)[1]}</pre>
                </div>
                """, unsafe_allow_html=True)

# --- ONGLET 6 : STICKERS ---
with tabs[5]:
    st.markdown("### 🎨 Ma Collection")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%201.jpg")
