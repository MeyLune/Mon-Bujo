import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import calendar

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

# --- STYLE CSS "FORCE NOIRE" ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&display=swap');
    
    /* Couleurs de base */
    :root { --rose: #F48FB1; --sapin: #1B3022; --vert: #B2DFDB; --or: #D4AF37; }

    .stApp { background: linear-gradient(180deg, #fce4ec 0%, #e0f2f1 100%) !important; }

    /* FORCE LE TEXTE NOIR ABSOLU PARTOUT (iPad/PC) */
    p, span, div, label, input, textarea, [data-baseweb="select"] {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* Champs de saisie blancs avec bordures roses */
    input, textarea, [data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 2px solid var(--rose) !important;
        border-radius: 10px !important;
    }

    /* Styles Calligraphie */
    .titre-calli { font-family: 'Dancing Script'; font-size: 3.5rem; color: var(--sapin); text-align: center; padding: 20px; }
    .sous-titre-calli { font-family: 'Dancing Script'; font-size: 2.2rem; color: var(--sapin); margin-top: 10px; }

    /* Post-it Gratitude & Shopping */
    .post-it { background: #FFF9C4 !important; border-left: 10px solid var(--or) !important; padding: 15px; border-radius: 5px; color: black !important; box-shadow: 3px 3px 6px rgba(0,0,0,0.1); }
    
    /* Calendrier - Fix de la largeur et du look */
    .cal-container {
        background: white !important;
        color: black !important;
        border: 2px solid var(--rose);
        border-radius: 0 0 15px 15px;
        padding: 10px;
        font-family: 'Courier New', monospace;
        text-align: center;
        max-width: 250px;
        margin: auto;
    }
    .cal-header {
        background: var(--rose) !important;
        color: white !important;
        font-weight: bold;
        text-align: center;
        border-radius: 15px 15px 0 0;
        max-width: 250px;
        margin: auto;
        padding: 5px;
    }

    /* Missions Stickers - Force le Noir sur Vert */
    .mission-tag {
        background-color: #B2DFDB !important;
        color: #000000 !important;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid var(--rose);
        text-align: center;
        font-weight: bold;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- CONNEXION & LOGIQUE ---
def init_connection():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = {
            "type": "service_account", "project_id": "airy-semiotics-486311-v5",
            "private_key": st.secrets["MY_PRIVATE_KEY"], "client_email": st.secrets["MY_CLIENT_EMAIL"],
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds).open("db_bujo")
    except: return None

sh = init_connection()
if 'shopping' not in st.session_state: st.session_state.shopping = []

def save_gs(ws_n, row):
    try: sh.worksheet(ws_n).append_row(row)
    except: pass

def load_gs(ws_n):
    try: return sh.worksheet(ws_n).get_all_records()
    except: return []

# --- INTERFACE ---
st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- TAB 1 : JOURNAL & GRATITUDE ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data = load_gs("Journal")
    g_data = load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes Pensées</div>', unsafe_allow_html=True)
        txt_j = st.text_area("...", key="in_j", height=100, label_visibility="collapsed")
        if st.button("Enregistrer", key="btn_j"):
            if txt_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y"), txt_j]); st.rerun()
        for e in reversed(j_data[-5:]):
            st.markdown(f'<div style="background:white; padding:10px; border-radius:10px; border-left:4px solid var(--rose); margin-bottom:5px;">{e.get("Texte","")}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        txt_g = st.text_area("...", key="in_g", height=100, label_visibility="collapsed")
        if st.button("Sauver Bonheur", key="btn_g"):
            if txt_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y"), txt_g]); st.rerun()
        st.markdown('<div class="post-it"><b>Mes Gratitudes :</b><br>', unsafe_allow_html=True)
        for e in reversed(g_data[-5:]):
            st.markdown(f"• {e.get('Texte', '')}")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3 : ANNEE (CALENDRIER RÉPARÉ) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m = r * 3 + c + 1
            with cols[c]:
                st.markdown(f'<div class="cal-header">{calendar.month_name[m].upper()}</div>', unsafe_allow_html=True)
                cal_txt = calendar.month(2026, m).split('\n', 1)[1]
                st.markdown(f'<div class="cal-container"><pre style="color:black; background:white; border:none; margin:0;">{cal_txt}</pre></div>', unsafe_allow_html=True)
    st.write("---")
    # Formulaire d'événement compact
    ce1, ce2, ce3 = st.columns([2, 3, 1])
    ev_d = ce1.date_input("Le")
    ev_n = ce2.text_input("Quoi ?")
    if ce3.button("Ajouter"):
        save_gs("Evenements", [ev_d.strftime("%d/%m/%Y"), ev_n]); st.rerun()

# --- TAB 4 : MISSIONS (TEXTE NOIR FIX) ---
with tabs[3]:
    st.markdown('<div class="sous-titre-calli">🏠 Missions de la Tribu</div>', unsafe_allow_html=True)
    m_data = load_gs("Menage")
    c1, c2, c3 = st.columns(3)
    mq = c1.selectbox("Qui ?", ["Enfant 1 👦", "Enfant 2 👧", "Enfant 3 👶", "Maman 🌸", "Papa 👔"])
    mt = c2.selectbox("Mission ?", ["🍽️ Vaisselle", "🗑️ Poubelles", "🧹 Balai", "🔌 Aspirateur"])
    if c3.button("🚀 Valider"):
        save_gs("Menage", [mt, datetime.now().strftime("%d/%m/%Y"), mq]); st.rerun()
    
    st.write("---")
    # Affichage en grille
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    start_w = datetime.now().date() - timedelta(days=datetime.now().weekday())
    cols = st.columns(7)
    for i, j in enumerate(jours):
        d_str = (start_w + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div style="background:white; border:1px solid var(--rose); border-radius:10px; padding:8px; min-height:150px; text-align:center;"><b>{j}</b><br><small>{d_str[:5]}</small>', unsafe_allow_html=True)
            for m in m_data:
                if d_str in str(m.values()):
                    st.markdown(f'<div class="mission-tag">{m.get("Tache","")}<br>{m.get("Qui","")}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 5 : COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    it = st.text_input("Ajouter un article...")
    if st.button("Ajouter"):
        if it: st.session_state.shopping.append(it); st.rerun()
    st.markdown('<div class="post-it"><b>À ACHETER :</b><br>', unsafe_allow_html=True)
    for val in st.session_state.shopping:
        st.markdown(f"☐ {val}")
    st.markdown('</div>', unsafe_allow_html=True)
