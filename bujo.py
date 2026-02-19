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

# --- 2. DESIGN CORRIGÉ : ROSE PASTRL & VERT CLAIR ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    
    .stApp {{
        background: linear-gradient(135deg, rgba(fedfe7, 0.8), rgba(e0f2f1, 0.8)), url("{fond_url}");
        background-size: cover;
        background-attachment: fixed;
    }}

    /* Palette de couleurs */
    :root {{
        --rose-clair: #ffc1cc;
        --vert-eau: #b2dfdb;
        --sapin: #1b3022;
    }}

    h1, h2, h3, p, label, .stMarkdown {{ 
        color: var(--sapin) !important; 
        font-family: 'Comfortaa', cursive;
    }}

    /* Boutons Vieux Rose */
    .stButton>button {{
        background-color: #f48fb1 !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: bold !important;
    }}

    /* Inputs Blanc Opaque */
    div[data-baseweb="textarea"], div[data-baseweb="input"], .stTextArea textarea, .stTextInput input {{
        background-color: white !important;
        color: var(--sapin) !important;
        border-radius: 12px !important;
        border: 1px solid #f48fb1 !important;
    }}

    .p-header {{ 
        background-color: #80cbc4 !important; /* Vert eau foncé pour les titres */
        color: white !important; 
        padding: 8px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold;
    }}

    .cal-box {{
        font-family: 'Courier Prime', monospace !important;
        background-color: white; padding: 15px; border-radius: 0 0 12px 12px;
        color: var(--sapin) !important; font-size: 16px !important;
        white-space: pre; border: 1px solid #b2dfdb;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌸 Mon Univers Quotidien</h1>", unsafe_allow_html=True)
    code = st.text_input("Code secret :", type="password")
    if st.button("Entrer") or code == "2125":
        st.session_state.user_data = {"Nom": "MeyLune"}
        st.rerun()
    st.stop()

user_nom = st.session_state.user_data['Nom']
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- JOURNAL ---
with tabs[0]:
    st.markdown(f"### 🖋️ Mes Pensées du Jour")
    note_j = st.text_area("", height=300, key="journal_area")
    if st.button("💾 Enregistrer"):
        if sh: sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), user_nom, note_j])
        st.success("Enregistré ! ✨")

# --- SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    now = datetime.now()
    start_week = (now.date() - timedelta(days=now.weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - 2026</h3>", unsafe_allow_html=True)

    col_g, col_d = st.columns([3, 1.2])
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    with col_g:
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for k in range(2):
                if (i+k) < 7:
                    d = start_week + timedelta(days=i+k)
                    with cols[k]:
                        st.markdown(f'<div class="p-header">{jours[i+k]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        st.text_area("", height=100, key=f"s_note_{d}", label_visibility="collapsed")
    with col_d:
        st.markdown('<div style="background:#fce4ec; padding:15px; border-radius:10px; border-left:5px solid #f48fb1; color:#1b3022;">🍎 <b>Menu</b></div>', unsafe_allow_html=True)
        for j in jours: st.text_input(j[:3], key=f"menu_input_{j}")

# --- ANNEE ---
with tabs[2]:
    st.markdown(f"<h2 style='text-align:center;'>Année 2026 - Semaine actuelle : {datetime.now().isocalendar()[1]}</h2>", unsafe_allow_html=True)
    mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                tc = calendar.TextCalendar(firstweekday=0)
                cal_str = tc.formatmonth(2026, m_idx)
                clean_cal = "Lu Ma Me Je Ve Sa Di\n" + "\n".join(cal_str.splitlines()[2:])
                st.markdown(f'<div class="p-header" style="background-color:#f48fb1 !important;">{mois_fr[m_idx-1].upper()}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="cal-box">{clean_cal}</div>', unsafe_allow_html=True)

# --- TRACKERS & LECTURE ---
with tabs[3]:
    cat = st.radio("Sélection", ["🌿 Santé", "📖 Lecture"], horizontal=True)
    if cat == "📖 Lecture":
        st.markdown('<div style="background:white; padding:20px; border-radius:15px; border:2px solid #b2dfdb;">', unsafe_allow_html=True)
        st.subheader("📖 Ma Fiche de Lecture")
        tl, al = st.columns(2)
        titre_l = tl.text_input("Titre")
        auteur_l = al.text_input("Auteur")
        img = st.file_uploader("Couverture", type=['jpg','png'])
        if img: st.image(img, width=120)
        
        st.write("Ressenti :")
        c_e = st.columns(4)
        c_e[0].select_slider("💧", options=[1,2,3,4,5], key="e1")
        c_e[1].select_slider("🌶️", options=[1,2,3,4,5], key="e2")
        c_e[2].select_slider("😊", options=[1,2,3,4,5], key="e3")
        c_e[3].select_slider("❤️", options=[1,2,3,4,5], key="e4")
        if st.button("📥 Enregistrer"):
            st.success("Livre ajouté !")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.slider("💧 Verres d'eau", 0, 10, 5)
        st.slider("😴 Sommeil", 0, 12, 8)

# --- COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses")
    items = ["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]
    cols_c = st.columns(6)
    for i, it in enumerate(items):
        if cols_c[i].button(it):
            if sh: sh.worksheet("Courses").append_row([it, user_nom]); st.rerun()
    st.markdown("---")
    autre = st.text_input("➕ Autre chose ?")
    if st.button("Ajouter"):
        if sh and autre: sh.worksheet("Courses").append_row([autre, user_nom]); st.rerun()

# --- STICKERS ---
with tabs[5]:
    st.markdown("### 🎨 Planche Stickers")
    stks = ["🌸", "🌿", "⭐", "🍃", "🍎", "🥑", "📅", "✨", "🎀", "🍪"]
    cols_s = st.columns(5)
    for i, s in enumerate(stks):
        if cols_s[i % 5].button(s, key=f"k_{i}"): st.balloons()
