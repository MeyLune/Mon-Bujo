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

# --- 2. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Mon Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    div[data-baseweb="textarea"], div[data-baseweb="input"], .stTextArea textarea, .stTextInput input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1b5e20 !important;
        border-radius: 12px !important;
        border: 1px solid #f06292 !important;
    }}
    .stTabs {{ background-color: rgba(255, 255, 255, 0.88) !important; border-radius: 20px; padding: 20px; }}
    h1, h2, h3, label {{ color: #1b5e20 !important; font-family: 'Comfortaa'; }}
    .stButton>button {{ background-color: #f06292 !important; color: white !important; border-radius: 25px !important; width: 100%; }}
    .p-header {{ background-color: #f06292 !important; color: white !important; padding: 10px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; }}
    .post-it {{ background: rgba(255, 249, 196, 0.95); padding: 15px; border-left: 6px solid #fbc02d; font-family: 'Indie Flower', cursive; color: #5d4037 !important; border-radius: 5px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None

if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 Mon Bullet Journal</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        input_code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal"):
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
                except: st.error("Erreur de connexion.")
    st.stop()

# --- 4. INTERFACE ---
user_nom = st.session_state.user_data['Nom']
st.title(f"🌸 Journal de {user_nom}")
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- ONGLET JOURNAL ---
with tabs[0]:
    if st.session_state.user_data['Acces'] == "OUI":
        st.markdown(f"### ✨ Aujourd'hui, {datetime.now().strftime('%d/%m/%Y')}")
        note_txt = st.text_area("Ma pensée...", height=200, key="j_note", label_visibility="collapsed")
        if st.button("✅ Enregistrer ma pensée"):
            if note_txt and sh:
                sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), user_nom, note_txt])
                st.success("C'est enregistré ! ✨")
    else: st.warning("Accès restreint au journal intime. 🔒")

# --- ONGLET SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]}</h3>", unsafe_allow_html=True)

    sem_dict = {}
    col_g, col_d = st.columns([3, 1.2])
    with col_g:
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i in range(7):
            d = start_week + timedelta(days=i)
            d_str = d.strftime("%d/%m/%Y")
            st.markdown(f'<div class="p-header">{jours[i]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            sem_dict[d_str] = st.text_area("Note", height=80, key=f"wk_{d_str}", label_visibility="collapsed")
        
        if st.button("💾 TOUT SAUVEGARDER LA SEMAINE"):
            if sh:
                for date_k, texte in sem_dict.items():
                    if texte.strip(): sh.worksheet("Note").append_row([date_k, user_nom, texte])
                st.success("Semaine enregistrée ! ✨")

    with col_d:
        st.markdown('<div class="post-it"><b>🍎 Menu</b></div>', unsafe_allow_html=True)
        m_data = [st.text_input(j, key=f"m_{j}") for j in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]]
        if st.button("Valider Menu"):
            if sh:
                sh.worksheet("Menu").append_row([start_week.strftime("%d/%m/%Y"), user_nom] + m_data)
                st.success("Menu sauvé !")

# --- ONGLET ANNEE ---
with tabs[2]:
    st.markdown("### 📅 Vue Annuelle 2026")
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                st.markdown(f'<div class="p-header">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="background:white; padding:10px; border:1px solid #f06292; text-align:center; color:black;">{calendar.month(2026, m_idx).split(chr(10), 1)[1].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

# --- ONGLET COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Ma liste")
    autre = st.text_input("Ajouter un article :")
    if st.button("Ajouter"):
        if sh: sh.worksheet("Courses").append_row([autre, user_nom]); st.rerun()
