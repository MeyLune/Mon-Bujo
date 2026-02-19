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
    except:
        return None

sh = init_connection()

# --- 2. STYLE ET FOND D'ÉCRAN ---
st.set_page_config(page_title="Mon Bujo", layout="wide", initial_sidebar_state="collapsed")

# Lien direct vers ton image (avec %20 pour l'espace dans "fond 0.jpg")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/fond%200.jpg"

st.markdown(f"""
<style>
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    /* Nettoyage des zones pour éviter le noir */
    div[data-baseweb="textarea"], div[data-baseweb="input"], 
    .stTextArea textarea, .stTextInput input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1b5e20 !important;
        border-radius: 12px !important;
        border: 1px solid #f06292 !important;
    }}
    .stTabs {{
        background-color: rgba(255, 255, 255, 0.88) !important;
        border-radius: 20px;
        padding: 20px;
    }}
    h1, h2, h3, label {{ color: #1b5e20 !important; font-family: 'Comfortaa'; }}
    .stButton>button {{
        background-color: #f06292 !important;
        color: white !important;
        border-radius: 25px !important;
        width: 100%;
    }}
    .p-header {{ background-color: #f06292 !important; color: white !important; padding: 10px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

# --- 3. SYSTÈME DE CONNEXION ---
if "user_data" not in st.session_state:
    st.session_state.user_data = None

if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center; background:white; padding:20px; border-radius:20px;'>🌿 Mon Bullet Journal</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        input_code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal"):
            # Secours code 2125
            if input_code == "2125":
                st.session_state.user_data = {"Nom": "MeyLune", "Acces": "OUI"}
                st.rerun()
            elif sh:
                try:
                    users_df = pd.DataFrame(sh.worksheet("Utilisateurs").get_all_records())
                    match = users_df[users_df['Code'].astype(str) == str(input_code)]
                    if not match.empty:
                        st.session_state.user_data = {"Nom": match.iloc[0]['Nom'], "Acces": match.iloc[0]['Accès Journal']}
                        st.rerun()
                    else:
                        st.error("Code inconnu... 🌸")
                except:
                    st.error("Erreur de connexion.")
    st.stop()

# --- 4. INTERFACE ---
user_nom = st.session_state.user_data['Nom']
st.title(f"🌸 Journal de {user_nom}")

tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- ONGLET SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]}</h3>", unsafe_allow_html=True)

    semaine_txt = {}
    col_g, col_d = st.columns([3, 1.2])
    with col_g:
        for i in range(7):
            d = start_week + timedelta(days=i)
            d_str = d.strftime("%d/%m/%Y")
            st.markdown(f'<div class="p-header">{d.strftime("%A %d/%m")}</div>', unsafe_allow_html=True)
            semaine_txt[d_str] = st.text_area("Note", height=100, key=f"wk_{d_str}", label_visibility="collapsed")
        
        if st.button("💾 TOUT SAUVEGARDER LA SEMAINE"):
            if sh:
                for date_k, texte in semaine_txt.items():
                    if texte.strip():
                        sh.worksheet("Note").append_row([date_k, user_nom, texte])
                st.success("C'est enregistré ! ✨")

# --- ONGLET ANNEE ---
with tabs[2]:
    st.markdown("### 📅 Calendrier 2026")
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                st.markdown(f'<div style="background:white; border-radius:15px; padding:10px; border:1px solid #f06292; color:black;">{calendar.month(2026, m_idx)}</div>', unsafe_allow_html=True)
