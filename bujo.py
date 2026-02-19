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

# --- 2. DESIGN GLOBAL (FOND "fond 0.jpg" & HARMONIE) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

# LIEN RAW CORRIGÉ (C'est ce lien qui permet l'affichage direct)
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/fond%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    /* Supprimer le menu Streamlit pour l'iPad */
    [data-testid="stSidebar"] {{ display: none; }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    
    /* APPLICATION DU FOND D'ÉCRAN (FIXE ET NET) */
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* BLOCS BLANCS TRANSLUCIDES (Pour voir le fond fleuri) */
    .stTabs, .bujo-block, .p-cell-interactive, .cal-card, div[data-baseweb="textarea"] {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 20px;
        padding: 15px;
        border: 1px solid #c8e6c9;
        margin-bottom: 20px;
    }}

    /* COULEURS DES TEXTES (Vert foncé) */
    h1, h2, h3, p, label, .stMarkdown, textarea, input {{ 
        color: #1b5e20 !important; 
        font-family: 'Comfortaa', cursive; 
    }}
    
    /* BOUTONS (Rose comme vos fleurs) */
    .stButton>button {{ 
        background-color: #f06292 !important; 
        color: white !important;
        border-radius: 25px !important; 
        border: none !important;
        padding: 10px 25px !important;
        font-weight: bold !important;
    }}

    /* EN-TÊTES SEMAINES ET CALENDRIER (Rose) */
    .p-header, .cal-card-header {{ 
        background-color: #f06292 !important; 
        color: white !important; 
        padding: 8px; 
        text-align: center; 
        border-radius: 12px 12px 0 0; 
        font-weight: bold; 
    }}
    
    /* STYLE POST-IT */
    .post-it {{ 
        background: rgba(255, 249, 196, 0.95); padding: 20px; border-left: 6px solid #fbc02d; 
        font-family: 'Indie Flower', cursive; font-size: 1.1rem; color: #5d4037 !important; 
        border-radius: 5px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN (CODE PIN) ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center; background:white; padding:20px; border-radius:20px;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
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
st.title(f"🌸 Journal de {user['Nom']}")
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ONGLET 1 : JOURNAL ---
with tabs[0]:
    st.markdown(f"### ✨ Aujourd'hui, {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown('<div class="post-it">Écris tes gratitudes ou pensées du jour...</div>', unsafe_allow_html=True)
    note_txt = st.text_area("", placeholder="Cher journal...", height=150, key="j_note", label_visibility="collapsed")
    if st.button("Sauvegarder ma pensée"):
        if note_txt and sh:
            sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), note_txt])
            st.success("C'est enregistré ! ✨")

# --- ONGLET 2 : SEMAINE + MENU ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c_n1, c_n2, c_n3 = st.columns([1, 2, 1])
    if c_n1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c_n3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c_n2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)

    col_g, col_m = st.columns([3, 1])
    with col_g:
        try:
            ws_n = sh.worksheet("Note")
            df_n = pd.DataFrame(ws_n.get_all_values()[1:], columns=ws_n.get_all_values()[0])
        except: df_n = pd.DataFrame()
        
        days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    d = start_week + timedelta(days=i+j)
                    d_str = d.strftime("%d/%m/%Y")
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{days_fr[i+j]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        st.text_area("Note", height=100, key=f"in_{d_str}", label_visibility="collapsed")
                        if st.button("Sauver", key=f"sv_{d_str}"): st.rerun()
    with col_m:
        st.markdown('<div class="post-it"><b>🍎 Menu</b></div>', unsafe_allow_html=True)
        for j in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]:
            st.text_input(j, key=f"m_{j}_{st.session_state.w_off}")

# --- ONGLET 3 : ANNEE 2026 ---
with tabs[2]:
    st.markdown("### 📅 Vue Annuelle 2026")
    for r in range(4):
        cols_c = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_c[c]:
                st.markdown(f"""
                <div class="cal-card">
                    <div class="cal-card-header">{calendar.month_name[m_idx].upper()}</div>
                    <div class="cal-card-body" style="text-align:center; font-family:monospace;">
                        {calendar.month(2026, m_idx).split(chr(10), 1)[1].replace(chr(10), '<br>')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- ONGLET 4 : TRACKERS ---
with tabs[3]:
    st.markdown("### 📊 Mes Suivis")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="bujo-block">💧 Eau (Verres)', unsafe_allow_html=True)
        eau = st.slider("", 0, 12, 0, key="w_slid")
        if st.button("Noter l'eau"): st.success(f"{eau} verres !")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="bujo-block">🌿 Bien-être', unsafe_allow_html=True)
        st.checkbox("Méditation"); st.checkbox("Lecture"); st.checkbox("Sport")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ONGLET 5 : COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses")
    item = st.text_input("➕ Ajouter article :")
    if st.button("Ajouter"):
        if item and sh: sh.worksheet("Courses").append_row([item]); st.rerun()
    try:
        for it in sh.worksheet("Courses").get_all_records():
            st.checkbox(it['Article'], key=f"c_{it['Article']}")
    except: st.write("Liste vide.")

# --- ONGLET 6 : STICKERS ---
with tabs[5]:
    st.markdown("### 🎨 Ma Collection")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%201.jpg")
