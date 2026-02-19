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

# --- 2. STYLE (Version qui fonctionnait) ---
st.set_page_config(page_title="Mon Bujo", layout="wide", initial_sidebar_state="collapsed")

# URL brute qui fonctionnait
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    /* On force le blanc sur les zones de texte pour éviter le noir */
    .stTextArea textarea, .stTextInput input {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #1b5e20 !important;
    }}
    .stTabs {{ background-color: rgba(255, 255, 255, 0.8) !important; border-radius: 20px; padding: 20px; }}
    h1, h2, h3, label {{ color: #1b5e20 !important; font-family: 'Comfortaa'; }}
    .stButton>button {{ background-color: #f06292 !important; color: white !important; border-radius: 20px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None

if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 Bienvenue dans ton Journal</h1>", unsafe_allow_html=True)
    code = st.text_input("Code secret :", type="password")
    if st.button("Entrer"):
        if code == "2125":
            st.session_state.user_data = {"Nom": "MeyLune", "Acces": "OUI"}
            st.rerun()
        # (Optionnel : ajout de la vérification Sheet ici si besoin)
    st.stop()

# --- 4. NAVIGATION ---
user_nom = st.session_state.user_data['Nom']
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- SEMAINE (Avec ta nouvelle ergonomie !) ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    st.markdown(f"### Semaine {start_week.isocalendar()[1]}")
    
    col_g, col_d = st.columns([3, 1])
    semaine_txt = {}
    
    with col_g:
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for j_nom in jours:
            d = start_week + timedelta(days=jours.index(j_nom))
            d_s = d.strftime("%d/%m/%Y")
            st.markdown(f"**{j_nom} {d.strftime('%d/%m')}**")
            semaine_txt[d_s] = st.text_area("Note", key=f"s_{d_s}", label_visibility="collapsed", height=80)
        
        st.markdown("---")
        # TES DEUX BOUTONS CENTRALISÉS
        b_save, b_mod = st.columns(2)
        if b_save.button("💾 TOUT SAUVEGARDER LA SEMAINE"):
            if sh:
                for date_key, texte in semaine_txt.items():
                    if texte.strip(): sh.worksheet("Note").append_row([date_key, user_nom, texte])
                st.success("Semaine enregistrée ! ✨")
        if b_mod.button("🔄 MODIFIER / CORRIGER"):
            st.rerun()

# --- ANNEE (Avec historique en tableau BLANC) ---
with tabs[2]:
    st.markdown("### 📅 Vue Annuelle 2026")
    # Calendrier simplifié pour éviter les bugs
    st.write(calendar.month(2026, datetime.now().month))
    
    st.markdown("### 📜 Historique")
    try:
        data = sh.worksheet("Journal").get_all_records()
        # st.table force un affichage blanc propre sur PC et iPad
        st.table(pd.DataFrame(data).tail(10)) 
    except: st.info("Historique vide.")

# --- COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses")
    # On garde la structure simple
    st.write("Prêt pour la personnalisation !")
