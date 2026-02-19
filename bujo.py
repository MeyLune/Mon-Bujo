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

# --- 2. CONFIGURATION DE LA PAGE & DESIGN (FOND D'ÉCRAN AVEC 0.JPG) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

# Lien direct vers votre image sur GitHub
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    /* On masque les éléments inutiles de Streamlit */
    [data-testid="stSidebar"] {{ display: none; }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    
    /* APPLICATION DU FOND D'ÉCRAN "AVEC 0.JPG" */
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* CORRECTION DES COULEURS (On supprime le noir et on met du blanc translucide) */
    .stApp {{ color: #1b5e20; font-family: 'Comfortaa', cursive; }}
    
    /* Blocs de contenu */
    .stTabs, .bujo-block, div[data-baseweb="textarea"], div[data-baseweb="input"] {{
        background-color: rgba(255, 255, 255, 0.85) !important;
        border-radius: 20px !important;
        border: 1px solid #c8e6c9 !important;
        color: #1b5e20 !important;
    }}

    /* Forcer la couleur du texte dans les zones de saisie */
    textarea, input {{
        color: #1b5e20 !important;
    }}

    /* Style des titres */
    h1, h2, h3 {{ color: #1b5e20 !important; text-shadow: 1px 1px 2px white; }}

    /* Boutons roses comme les fleurs */
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
        border-radius: 10px 10px 0 0 !important;
        color: #1b5e20 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: #f06292 !important;
        color: white !important;
    }}

    /* Le fameux Post-it */
    .post-it {{ 
        background: rgba(255, 249, 196, 0.95); 
        padding: 20px; 
        border-left: 6px solid #fbc02d; 
        font-family: 'Indie Flower', cursive; 
        font-size: 1.2rem; 
        color: #5d4037 !important; 
        border-radius: 5px;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. SYSTÈME DE CODE PIN ---
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

# --- 4. NAVIGATION ET CONTENU ---
user = st.session_state.user_data
st.title(f"🌸 Journal de {user['Nom']}")
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ONGLET JOURNAL ---
with tabs[0]:
    st.markdown(f"### ✨ Aujourd'hui, {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown('<div class="post-it">Quelles sont tes gratitudes aujourd\'hui ?</div>', unsafe_allow_html=True)
    note_txt = st.text_area("", placeholder="Cher journal...", height=200, key="j_note", label_visibility="collapsed")
    if st.button("Sauvegarder dans le Cloud"):
        if note_txt and sh:
            sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), note_txt])
            st.success("C'est enregistré ! ✨")

# --- ONGLET SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c_n1, c_n2, c_n3 = st.columns([1, 2, 1])
    if c_n1.button("⬅️ Semaine précédente"): st.session_state.w_off -= 1; st.rerun()
    if c_n3.button("Semaine suivante ➡️"): st.session_state.w_off += 1; st.rerun()
    c_n2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)

    col_g, col_m = st.columns([3, 1])
    with col_g:
        try:
            ws_n = sh.worksheet("Note")
            data = ws_n.get_all_values()
            df_n = pd.DataFrame(data[1:], columns=data[0])
        except:
            df_n = pd.DataFrame(columns=["Date", "Heure", "Type", "Note"])

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
                        if st.button("Sauver", key=f"sv_{d_str}"):
                            st.toast("Note enregistrée ! (Simulé)")

    with col_m:
        st.markdown('<div class="post-it"><b>🍎 Menu de la Semaine</b></div>', unsafe_allow_html=True)
        for jour in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]:
            st.text_input(jour, key=f"m_{jour}_{st.session_state.w_off}")

# --- ONGLET ANNEE ---
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
                    <pre style="font-family:monospace; font-size:12px; line-height:1.2;">{calendar.month(2026, m_idx).split(chr(10), 1)[1]}</pre>
                </div>
                """, unsafe_allow_html=True)

# --- ONGLET STICKERS ---
with tabs[5]:
    st.markdown("### 🎨 Ma Collection de Stickers")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%201.jpg")
