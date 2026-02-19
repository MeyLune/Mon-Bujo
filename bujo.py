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

# --- 2. STYLE "FLORAL" TOTAL (Correction du fond noir) ---
st.set_page_config(page_title="MeyLune Bullet Journal", layout="wide", initial_sidebar_state="collapsed")

fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    /* 1. ON SUPPRIME TOUS LES FONDS PAR DÉFAUT DE STREAMLIT */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMainViewContainer"] {{
        background: transparent !important;
    }}

    /* 2. ON APPLIQUE TON IMAGE SUR TOUT LE CORPS DE LA PAGE */
    body, html, .stApp {{
        background-image: url("{fond_url}") !important;
        background-size: cover !important;
        background-position: center center !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
    }}

    /* 3. ON FORCE LE BLANC SUR LES ÉLÉMENTS (Anti-noir iPad) */
    div[data-baseweb="textarea"], div[data-baseweb="input"], 
    .stTextArea textarea, .stTextInput input, .stNumberInput input, 
    [data-testid="stTable"], .stTabs {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #1b5e20 !important;
        border: 2px solid #f06292 !important;
        border-radius: 15px !important;
    }}

    /* Esthétique des titres et boutons */
    h1, h2, h3, label, p {{ color: #1b5e20 !important; font-family: 'Comfortaa', cursive; font-weight: bold; }}
    .stButton>button {{ background-color: #f06292 !important; color: white !important; border-radius: 25px !important; border: none !important; }}
    .p-header {{ background-color: #f06292 !important; color: white !important; padding: 10px; text-align: center; border-radius: 12px 12px 0 0; }}
</style>
""", unsafe_allow_html=True)

# --- 3. SYSTÈME DE CONNEXION ---
if "user_data" not in st.session_state: st.session_state.user_data = None

if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center; background:white; padding:20px; border-radius:20px;'>🌿 Mon Bullet Journal</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown('<div style="background:white; padding:20px; border-radius:20px; border:2px solid #f06292;">', unsafe_allow_html=True)
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal"):
            # Secours direct pour MeyLune (code 2125)
            if code == "2125":
                st.session_state.user_data = {"Nom": "MeyLune", "Acces": "OUI"}
                st.rerun()
            else:
                try:
                    users = sh.worksheet("Utilisateurs").get_all_records()
                    for u in users:
                        if str(u['Code']) == str(code):
                            st.session_state.user_data = {"Nom": u['Nom'], "Acces": u['Accès Journal']}
                            st.rerun()
                except: st.error("Erreur de connexion 🌸")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ET CONTENU ---
user_nom = st.session_state.user_data['Nom']
st.markdown(f"<h1 style='background:white; padding:10px; border-radius:15px; text-align:center;'>🌸 Journal de {user_nom}</h1>", unsafe_allow_html=True)

tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# SEMAINE (Optimisée avec boutons centralisés)
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]}</h3>", unsafe_allow_html=True)

    col_g, col_m = st.columns([3, 1.2])
    entrees = {}
    with col_g:
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    d = start_week + timedelta(days=i+j)
                    d_str = d.strftime("%d/%m/%Y")
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{jours[i+j]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        entrees[d_str] = st.text_area("Note", height=100, key=f"s_{d_str}", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        if b1.button("💾 TOUT SAUVEGARDER"):
            if sh:
                for dk, txt in entrees.items():
                    if txt.strip(): sh.worksheet("Note").append_row([dk, user_nom, txt])
                st.success("C'est enregistré ! ✨")
        if b2.button("🔄 MODIFIER / RECHARGER"): st.rerun()

# ANNEE (Corrigée et Jolie)
with tabs[2]:
    for r in range(4):
        cols_an = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_an[c]:
                st.markdown(f'<div style="background:white; border-radius:15px; padding:10px; border:1px solid #c8e6c9;"><div class="p-header">{calendar.month_name[m_idx].upper()}</div><div style="text-align:center; padding:10px;">{calendar.month(2026, m_idx).split(chr(10), 1)[1].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📜 Historique du Journal")
    try:
        df_hist = pd.DataFrame(sh.worksheet("Journal").get_all_records())
        st.table(df_hist.tail(10)) 
    except: st.info("Historique vide.")

# TRACKERS & COURSES (Simplifiés pour test fond)
with tabs[3]: st.write("### 📊 Mes Trackers (OK)")
with tabs[4]: st.write("### 🛒 Liste de Courses (OK)")
with tabs[5]: st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
