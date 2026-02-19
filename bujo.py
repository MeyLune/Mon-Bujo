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

# --- 2. DESIGN DOUX : ROSE POUDRÉ & VERT D'EAU ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    
    /* Dégradé doux Rose vers Vert d'eau par-dessus ton image */
    .stApp {{
        background: linear-gradient(135deg, rgba(255, 209, 220, 0.7), rgba(209, 255, 240, 0.7)), url("{fond_url}");
        background-size: cover;
        background-attachment: fixed;
    }}

    /* TEXTE VERT SAPIN TRÈS FONCÉ POUR LISIBILITÉ */
    h1, h2, h3, p, label, .stMarkdown {{ 
        color: #2d4f3a !important; 
        font-family: 'Comfortaa', cursive;
    }}

    /* BOUTONS ROSE DOUX */
    .stButton>button {{
        background-color: #e5989b !important;
        color: white !important;
        border-radius: 15px !important;
        border: none !important;
        padding: 8px 20px !important;
        font-weight: bold !important;
        transition: 0.3s;
    }}
    .stButton>button:hover {{ transform: scale(1.02); background-color: #b5838d !important; }}

    /* ONGLETS STYLISÉS */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background-color: transparent !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.6) !important;
        border-radius: 10px 10px 0 0 !important;
        padding: 10px 20px !important;
        color: #2d4f3a !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: white !important;
        border-bottom: 3px solid #e5989b !important;
    }}

    /* INPUTS BLANCS NETS */
    div[data-baseweb="textarea"], div[data-baseweb="input"], .stTextArea textarea, .stTextInput input {{
        background-color: white !important;
        color: #1b3022 !important;
        border-radius: 12px !important;
        border: 1px solid #e5989b !important;
    }}

    .p-header {{ 
        background-color: #b5838d !important; 
        color: white !important; 
        padding: 8px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold;
    }}

    .cal-box {{
        font-family: 'Courier Prime', monospace !important;
        background-color: white; padding: 15px; border-radius: 0 0 12px 12px;
        color: #2d4f3a !important; font-size: 16px !important;
        white-space: pre; border: 1px solid #e5989b;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>✨ Mon Univers MeyLune</h1>", unsafe_allow_html=True)
    code = st.text_input("Code secret :", type="password")
    if st.button("Entrer") or code == "2125":
        st.session_state.user_data = {"Nom": "MeyLune"}
        st.rerun()
    st.stop()

user_nom = st.session_state.user_data['Nom']
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- JOURNAL ---
with tabs[0]:
    st.markdown(f"### 🖋️ Mes Pensées - {datetime.now().strftime('%d/%m/%Y')}")
    note_j = st.text_area("Libère ton esprit ici...", height=300, label_visibility="collapsed")
    if st.button("💾 Sauvegarder dans le journal"):
        if sh: sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), user_nom, note_j])
        st.success("C'est enregistré avec douceur ! ✨")

# --- SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {mois_fr[start_week.month-1]}</h3>", unsafe_allow_html=True)

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
                        st.text_area("Txt", height=100, key=f"note_sem_{d}", label_visibility="collapsed")
    with col_d:
        st.markdown('<div style="background:#fff9c4; padding:15px; border-radius:10px; border-left:5px solid #fbc02d; color:#5d4037;">🍎 <b>Menu</b></div>', unsafe_allow_html=True)
        [st.text_input(j[:3], key=f"menu_sem_{j}") for j in jours]

# --- ANNEE ---
with tabs[2]:
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                tc = calendar.TextCalendar(firstweekday=0)
                cal_str = tc.formatmonth(2026, m_idx)
                clean_cal = "Lu Ma Me Je Ve Sa Di\n" + "\n".join(cal_str.splitlines()[2:])
                st.markdown(f'<div class="p-header">{mois_fr[m_idx-1].upper()}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="cal-box">{clean_cal}</div>', unsafe_allow_html=True)

# --- TRACKERS & LECTURE ---
with tabs[3]:
    cat = st.radio("Catégorie", ["🌿 Santé", "📖 Lecture"], horizontal=True)
    if cat == "📖 Lecture":
        st.markdown('<div style="background:white; padding:20px; border-radius:15px; border:1px solid #e5989b;">', unsafe_allow_html=True)
        t_liv = st.text_input("TITRE DU LIVRE")
        a_liv = st.text_input("AUTEUR")
        img = st.file_uploader("📸 Couverture", type=['jpg','png','jpeg'])
        if img: st.image(img, width=120)
        st.write("Émotions :")
        c_emo = st.columns(4)
        c_emo[0].select_slider("💧", options=[1,2,3,4,5], key="emo1")
        c_emo[1].select_slider("🌶️", options=[1,2,3,4,5], key="emo2")
        c_emo[2].select_slider("😊", options=[1,2,3,4,5], key="emo3")
        c_emo[3].select_slider("❤️", options=[1,2,3,4,5], key="emo4")
        if st.button("📥 Ajouter à ma collection"):
            st.success("Livre enregistré !")
        st.markdown('</div>', unsafe_allow_html=True)

# --- COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses")
    rapides = ["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]
    cols_c = st.columns(6)
    for i, it in enumerate(rapides):
        if cols_c[i].button(it):
            if sh: sh.worksheet("Courses").append_row([it, user_nom]); st.rerun()
    
    st.markdown("---")
    autre = st.text_input("➕ Ajouter un autre article :")
    if st.button("Ajouter à la liste"):
        if sh and autre:
            sh.worksheet("Courses").append_row([autre, user_nom]); st.rerun()

# --- STICKERS ---
with tabs[5]:
    st.markdown("### 🎨 Ma Planche")
    stickers = ["🌸", "🌿", "⭐", "🍃", "🍎", "🥑", "📅", "✨", "🎀", "🍪"]
    cols_s = st.columns(5)
    for i, s in enumerate(stickers):
        if cols_s[i % 5].button(s, key=f"stk_btn_{i}"): st.balloons()
