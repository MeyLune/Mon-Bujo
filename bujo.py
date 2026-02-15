import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

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

# --- 2. DESIGN GLOBAL (SANS BARRE NOIRE) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3, p, label { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }
    
    /* Correction Contrastes iPad */
    div[data-baseweb="input"], .stTextArea textarea, .stTextInput input {
        background-color: white !important;
        border: 2px solid #c8e6c9 !important;
        border-radius: 12px !important;
        color: #1b5e20 !important;
        -webkit-text-fill-color: #1b5e20 !important;
    }

    /* Boutons avec texte blanc éclatant */
    .stButton>button { background-color: #1b5e20 !important; border-radius: 20px !important; border: none !important; padding: 10px 20px !important; }
    .stButton>button p { color: white !important; font-weight: bold !important; font-size: 1rem !important; }

    /* Blocs Bujo */
    .post-it {
        background: #fff9c4; padding: 25px; border-left: 6px solid #fbc02d;
        font-family: 'Indie Flower', cursive; font-size: 1.3rem; color: #5d4037 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-radius: 4px;
    }
    .bujo-block { background: white; padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 3. GESTION DE LA SESSION ---
if "user_data" not in st.session_state:
    st.session_state.user_data = None

def login(code_entre):
    if sh:
        try:
            ws = sh.worksheet("Utilisateurs")
            df = pd.DataFrame(ws.get_all_records())
            df.columns = [c.strip().capitalize() for c in df.columns]
            df['Code'] = df['Code'].astype(str).str.strip()
            match = df[df['Code'] == str(code_entre).strip()]
            return match.iloc[0].to_dict() if not match.empty else None
        except: return None
    return None

if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code = st.text_input("Code secret :", type="password")
        if st.button("Valider"):
            u = login(code)
            if u: st.session_state.user_data = u; st.rerun()
            else: st.error("Code incorrect.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ET CONTENU ---
user = st.session_state.user_data
col_title, col_logout = st.columns([4, 1])
with col_title:
    st.markdown(f"<h1>Journal de {user['Nom']}</h1>", unsafe_allow_html=True)
with col_logout:
    if st.button("🔒 Déconnexion"):
        st.session_state.user_data = None; st.rerun()

# Menu complet
menu = ["✍️ JOURNAL", "📊 TRACKERS", "🗓️ SEMAINE", "🎨 STICKERS", "🛒 COURSES"]
if user.get('Accès journal') == "OUI" or user.get('Accès Journal') == "OUI":
    menu.append("💰 BUDGET PRIVÉ")

tabs = st.tabs(menu)

# --- TAB : JOURNAL ---
with tabs[0]:
    st.markdown(f"### ✨ {datetime.now().strftime('%d %B %Y')}")
    st.markdown('<div class="post-it">Écris tes pensées ou tes gratitudes...</div>', unsafe_allow_html=True)
    st.text_area("", height=250, key="journal_area", label_visibility="collapsed")
    if st.button("Enregistrer ma page"):
        st.success("C'est mémorisé ! ✨")

# --- TAB : TRACKERS ---
with tabs[1]:
    st.markdown("### 📊 Mes suivis quotidiens")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="bujo-block">💧 Hydratation (Verres)', unsafe_allow_html=True)
        st.slider("", 0, 10, 0, key="h2o")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="bujo-block">🧘 Bien-être', unsafe_allow_html=True)
        st.checkbox("Méditation")
        st.checkbox("Lecture")
        st.checkbox("Sport / Marche")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB : SEMAINE ---
with tabs[2]:
    st.markdown("### 🗓️ Vue Hebdomadaire")
    # Grille de la semaine
    st.info("Ici s'affichera ta grille avec les rendez-vous de ton Google Sheets.")

# --- TAB : STICKERS ---
with tabs[3]:
    st.markdown("### 🎨 Ma Planche de Stickers Aquarelle")
    st.write("Astuce iPad : Pour utiliser un sticker, reste appuyé dessus et fais 'Copier' ou 'Faire glisser'.")
    
    st.markdown("---")
    col_cosy, col_org = st.columns(2)
    
    with col_cosy:
        st.subheader("🌿 Pack Cosy & Douceur")
        st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg", use_container_width=True)
        st.caption("Illustrations : Café, plantes et moments cocooning.")

    with col_org:
        st.subheader("📌 Pack Organisation")
        st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%201.jpg", use_container_width=True)
        st.caption("Pratique : Bannières, rappels et post-it à thèmes.")

# --- TAB : COURSES ---
with tabs[4]:
    st.markdown('<div class="bujo-block"><h3>🛒 Liste de Courses</h3></div>', unsafe_allow_html=True)

# --- TAB : BUDGET PRIVÉ ---
if len(tabs) > 5:
    with tabs[5]:
        st.markdown("### 🔒 Finances Détaillées")
        st.write("Section accessible uniquement à MeyLune.")
