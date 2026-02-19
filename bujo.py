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

# --- 2. STYLE GLOBAL (PC & IPAD) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

# Correction de l'URL pour gérer l'espace sur GitHub
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    /* SUPPRESSION DU NOIR ET APPLICATION DU FOND */
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* FORCE LE BLANC SUR LES CHAMPS (Fix pour ton PC et l'iPad) */
    div[data-baseweb="textarea"], div[data-baseweb="input"], 
    .stTextArea textarea, .stTextInput input, .stNumberInput input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1b5e20 !important;
        border: 2px solid #f06292 !important;
        border-radius: 12px !important;
        -webkit-text-fill-color: #1b5e20 !important;
    }}

    /* Blocs et Onglets */
    .stTabs, .bujo-block, .cal-card {{
        background-color: rgba(255, 255, 255, 0.88) !important;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #c8e6c9;
    }}

    h1, h2, h3, p, label {{ color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }}
    
    /* Boutons MeyLune Rose */
    .stButton>button {{ 
        background-color: #f06292 !important; color: white !important;
        border-radius: 25px !important; border: none !important;
        padding: 10px 25px !important; font-weight: bold !important; width: 100%;
    }}

    .p-header {{ background-color: #f06292 !important; color: white !important; padding: 10px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; }}
    .post-it {{ background: rgba(255, 249, 196, 0.95); padding: 15px; border-left: 6px solid #fbc02d; font-family: 'Indie Flower', cursive; color: #5d4037 !important; border-radius: 5px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. SYSTÈME DE LOGIN (Via Google Sheet Utilisateurs) ---
if "user_data" not in st.session_state: st.session_state.user_data = None

if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center; background:rgba(255,255,255,0.8); padding:20px; border-radius:20px;'>🌿 Mon Bullet Journal</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code = st.text_input("Entre ton code secret :", type="password")
        if st.button("Ouvrir mon journal"):
            # Secours prioritaire (code 2125)
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
                except: st.error("Impossible de vérifier le code. Vérifie ta feuille 'Utilisateurs'.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
user_nom = st.session_state.user_data['Nom']
st.markdown(f"<h1 style='background:white; padding:10px; border-radius:15px; text-align:center;'>🌸 Journal de {user_nom}</h1>", unsafe_allow_html=True)

tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- SEMAINE (Centralisée) ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️ Semaine Précédente"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("Semaine Suivante ➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)

    col_g, col_m = st.columns([3, 1.2])
    semaine_inputs = {}
    with col_g:
        jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    d = start_week + timedelta(days=i+j)
                    d_str = d.strftime("%d/%m/%Y")
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{jours_fr[i+j]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        semaine_inputs[d_str] = st.text_area("Note", height=100, key=f"s_{d_str}", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        b_save, b_mod = st.columns(2)
        if b_save.button("💾 TOUT SAUVEGARDER"):
            if sh:
                for dk, txt in semaine_inputs.items():
                    if txt.strip(): sh.worksheet("Note").append_row([dk, user_nom, txt])
                st.success("Toute ta semaine est enregistrée ! ✨")
        if b_mod.button("🔄 MODIFIER / RAFRAÎCHIR"): st.rerun()

    with col_m:
        st.markdown('<div class="post-it"><b>🍎 Menu</b></div>', unsafe_allow_html=True)
        menu_vals = [st.text_input(j, key=f"m_{j}") for j in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]]
        if st.button("💾 Sauver Menu"):
            sh.worksheet("Menu").append_row([start_week.strftime("%d/%m/%Y"), user_nom] + menu_vals)
            st.success("Menu OK !")

# --- ANNEE (Historique Blanc) ---
with tabs[2]:
    st.markdown("### 📅 Calendrier 2026")
    for r in range(4):
        cols_an = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_an[c]:
                st.markdown(f'<div class="cal-card"><div class="p-header">{calendar.month_name[m_idx].upper()}</div><div style="text-align:center; padding:10px;">{calendar.month(2026, m_idx).split(chr(10), 1)[1].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📜 Historique")
    try:
        data_j = sh.worksheet("Journal").get_all_records()
        st.table(pd.DataFrame(data_j).tail(10)) # Plus blanc que st.dataframe
    except: st.info("Historique vide.")

# --- COURSES (Pré-sélection) ---
with tabs[4]:
    st.markdown("### 🛒 Ma Liste")
    items = ["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]
    cols_q = st.columns(6)
    for i, it in enumerate(items):
        if cols_q[i].button(it):
            sh.worksheet("Courses").append_row([it, user_nom]); st.rerun()
    autre = st.text_input("➕ Ajouter autre :")
    if st.button("Ajouter"):
        sh.worksheet("Courses").append_row([autre, user_nom]); st.rerun()
    try:
        data_c = sh.worksheet("Courses").get_all_records()
        for c in data_c: st.checkbox(c['Article'], key=f"c_{c['Article']}")
    except: st.write("Liste vide.")

# --- STICKERS ---
with tabs[5]:
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
