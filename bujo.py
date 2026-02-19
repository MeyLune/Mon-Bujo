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

# --- 2. STYLE : FOND ROSE PASTEL & FORCE L'IMAGE ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

# Ton image GitHub
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    /* ÉTAPE 1 : FOND ROSE PASTEL DE SECOURS (Si l'image ne charge pas) */
    .stApp {{
        background: linear-gradient(135deg, #fff5f8 0%, #ffe4e8 100%) !important;
        background-image: url("{fond_url}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    /* ÉTAPE 2 : ON FORCE LA TRANSPARENCE DES COUCHES STREAMLIT */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMainViewContainer"] {{
        background: transparent !important;
    }}

    /* ÉTAPE 3 : BLOCS ET BOUTONS */
    .stTabs, .bujo-block, .cal-card {{
        background-color: rgba(255, 255, 255, 0.85) !important;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #f8bbd0;
    }}

    /* CHAMPS DE SAISIE (Fin du noir !) */
    div[data-baseweb="textarea"], div[data-baseweb="input"], 
    .stTextArea textarea, .stTextInput input {{
        background-color: white !important;
        color: #880e4f !important;
        border: 1px solid #f06292 !important;
    }}

    h1, h2, h3, label {{ color: #ad1457 !important; font-family: 'Comfortaa', cursive; }}
    
    .stButton>button {{ 
        background-color: #f06292 !important; color: white !important;
        border-radius: 25px !important; border: none !important;
        font-weight: bold !important;
    }}

    .p-header {{ background-color: #f48fb1 !important; color: white !important; padding: 10px; text-align: center; border-radius: 12px 12px 0 0; }}
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
        if st.button("Ouvrir mon journal"):
            if code == "2125":
                st.session_state.user_data = {"Nom": "MeyLune", "Acces": "OUI"}
                st.rerun()
            elif sh:
                try:
                    users = sh.worksheet("Utilisateurs").get_all_records()
                    for u in users:
                        if str(u['Code']) == str(code):
                            st.session_state.user_data = {"Nom": u['Nom'], "Acces": u['Accès Journal']}
                            st.rerun()
                except: st.error("Erreur de connexion.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
user_nom = st.session_state.user_data['Nom']
st.markdown(f"<h1 style='text-align:center;'>🌸 Journal de {user_nom}</h1>", unsafe_allow_html=True)

tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- SEMAINE (Le fameux bouton unique) ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]}</h3>", unsafe_allow_html=True)

    col_g, col_m = st.columns([3, 1.2])
    semaine_inputs = {}
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
                        semaine_inputs[d_str] = st.text_area("Note", height=100, key=f"s_{d_str}", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        b_save, b_mod = st.columns(2)
        if b_save.button("💾 TOUT SAUVEGARDER"):
            if sh:
                for dk, txt in semaine_inputs.items():
                    if txt.strip(): sh.worksheet("Note").append_row([dk, user_nom, txt])
                st.success("C'est enregistré dans ton Google Sheet ! ✨")
        if b_mod.button("🔄 MODIFIER / RAFRAÎCHIR"): st.rerun()

    with col_m:
        st.markdown('<div style="background:#fff9c4; padding:15px; border-radius:10px; border-left:5px solid #fbc02d;"><b>🍎 Menu</b></div>', unsafe_allow_html=True)
        for j in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]:
            st.text_input(j, key=f"menu_{j}")
        st.button("💾 Sauver Menu")

# --- ANNEE (Historique OK) ---
with tabs[2]:
    st.markdown("### 📅 Calendrier 2026")
    for r in range(4):
        cols_an = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_an[c]:
                st.markdown(f'<div style="background:white; border-radius:15px; padding:10px; border:1px solid #f06292;"><div class="p-header">{calendar.month_name[m_idx].upper()}</div><div style="text-align:center; padding:10px;">{calendar.month(2026, m_idx).split(chr(10), 1)[1].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)
    st.divider()
    try:
        df_hist = pd.DataFrame(sh.worksheet("Journal").get_all_records())
        st.table(df_hist.tail(10)) 
    except: st.info("Historique vide.")

with tabs[5]:
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
