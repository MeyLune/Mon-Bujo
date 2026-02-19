import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
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
    except Exception: return None

sh = init_connection()

# Initialisation vitale pour éviter l'erreur "AttributeError" vue sur tes screens
if 'shopping' not in st.session_state: 
    st.session_state.shopping = []

def save_gs(ws_n, row):
    try: sh.worksheet(ws_n).append_row(row)
    except: pass

def load_gs(ws_n):
    try: return sh.worksheet(ws_n).get_all_records()
    except: return []

def delete_gs(ws_n, idx):
    try: sh.worksheet(ws_n).delete_rows(idx + 2)
    except: pass

# --- 2. STYLE ET VISIBILITÉ (FORÇAGE NOIR) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&display=swap');
    :root { --rose: #F48FB1; --sapin: #1B3022; --vert: #B2DFDB; --or: #D4AF37; }
    
    .stApp { background: linear-gradient(180deg, #fce4ec 0%, #e0f2f1 100%) !important; }

    /* FORCE LE TEXTE NOIR ET LE FOND BLANC DANS TOUS LES CHAMPS */
    input, textarea, select, .stSelectbox div, div[data-baseweb="select"] {
        background-color: white !important;
        color: #1B3022 !important; /* Vert sapin très foncé presque noir */
        -webkit-text-fill-color: #1B3022 !important;
        border: 2px solid var(--rose) !important;
        font-weight: bold !important;
    }
    
    /* Calendrier Annuel - Visibilité augmentée */
    .cal-container {
        font-family: 'Courier New', monospace;
        background: white;
        color: black !important;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid var(--rose);
        white-space: pre;
        text-align: center;
        font-size: 0.9rem;
        line-height: 1.2;
    }

    .titre-calli { font-family: 'Dancing Script'; font-size: 3.5rem; color: var(--sapin); text-align: center; }
    .sous-titre-calli { font-family: 'Dancing Script'; font-size: 2.2rem; color: var(--sapin); }
    .post-it { background: #fffde7; border-left: 10px solid var(--or); padding: 15px; color: black; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- JOURNAL ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("Ecrire ici...", key="j_in", height=100)
        if st.button("💾 Sauver pensée", key="j_btn"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data)):
            st.info(f"{e.get('Date','')} : {e.get('Texte', e.get('Note',''))}")
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("Merci pour...", key="g_in", height=100)
        if st.button("🙏 Sauver gratitude", key="g_btn"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        for e in reversed(g_data):
            st.success(e.get('Texte',''))

# --- SEMAINE ---
with tabs[1]:
    start_w = datetime.now().date() - timedelta(days=datetime.now().weekday())
    s_data = load_gs("Semaine")
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    cols = st.columns(7)
    for i, j in enumerate(jours):
        d_str = (start_w + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div style="background:var(--vert); text-align:center; border-radius:5px; padding:2px; color:black;"><b>{j}</b></div>', unsafe_allow_html=True)
            p = st.text_area("Plan", key=f"p_{i}", height=100, label_visibility="collapsed")
            m = st.text_input("🍴", key=f"m_{i}", label_visibility="collapsed")
            if st.button("💾", key=f"sb_{i}"):
                save_gs("Semaine", [d_str, p, m]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == d_str:
                    st.markdown(f"<small style='color:black;'>• {row.get('Planning','')}<br><b>🍴 {row.get('Menu','')}</b></small>", unsafe_allow_html=True)

# --- ANNEE (RESTAURATION DU CALENDRIER) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    for r in range(4):
        m_cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with m_cols[c]:
                st.markdown(f'<div style="background:var(--rose); color:white; text-align:center; border-radius:10px 10px 0 0; padding:5px;"><b>{calendar.month_name[m_idx].upper()}</b></div>', unsafe_allow_html=True)
                cal_txt = calendar.month(2026, m_idx).split('\n', 1)[1] # Enlève le nom du mois car on l'a déjà au dessus
                st.markdown(f'<div class="cal-container">{cal_txt}</div>', unsafe_allow_html=True)
    st.write("---")
    st.markdown("### 📍 Événements")
    ev_d = st.date_input("Date", key="ev_d")
    ev_n = st.text_input("Nom", key="ev_n")
    if st.button("Marquer"):
        save_gs("Evenements", [ev_d.strftime("%d/%m/%Y"), ev_n]); st.rerun()

# --- TRACKERS ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 BIBLIOTHÈQUE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS"])
    with tr_tabs[1]: # Bien-être (Restauré)
        st.markdown('<div class="sous-titre-calli">Mon Équilibre</div>', unsafe_allow_html=True)
        humeur = st.selectbox("Humeur", ["Radieuse ☀️", "Paisible ☁️", "Fatiguée 🔋", "Sensible 🌙"])
        eau = st.slider("Verres d'eau 💧", 0, 12, 4)
        energie = st.select_slider("Énergie", ["Bas", "Moyen", "Top!"])
        if st.button("Sauver Bien-être"):
            save_gs("Sante", [datetime.now().strftime("%d/%m/%Y"), humeur, eau, energie]); st.success("C'est noté !")
    
    with tr_tabs[2]: # Missions (Optimisé pour iPad selon ton image de référence)
        st.markdown('<div class="sous-titre-calli">Missions Tribu</div>', unsafe_allow_html=True)
        # On utilise les noms de colonnes vus dans ta capture Google Sheets (Tache, Lundi, Mardi...)
        m_data = load_gs("Menage")
        q = st.selectbox("Qui ?", ["Enfant 1 👦", "Enfant 2 👧", "Enfant 3 👶", "Maman 🌸", "Papa 👔"])
        t = st.selectbox("Mission ?", ["🍽️ Vaisselle", "🗑️ Poubelles", "🧹 Balai", "🔌 Aspirateur", "🧼 Serpillière"])
        d_m = st.date_input("Pour le :")
        if st.button("🚀 Valider mission"):
            save_gs("Menage", [t, d_m.strftime("%d/%m/%Y"), q]); st.rerun()

# --- COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    it = st.text_input("Ajouter un produit...", key="new_it")
    if st.button("Ajouter ➕"):
        if it: st.session_state.shopping.append(it); st.rerun()
    if st.button("Vider la liste 🗑️"):
        st.session_state.shopping = []; st.rerun()
    
    st.markdown('<div class="post-it"><b>📝 À ACHETER :</b><br>', unsafe_allow_html=True)
    for val in st.session_state.shopping:
        st.write(f"☐ {val}")
    st.markdown('</div>', unsafe_allow_html=True)
