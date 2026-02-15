import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

# --- 1. CONNEXION GOOGLE SHEETS ---
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
    except:
        return None

sh = init_connection()

# --- 2. DESIGN OPTIMISÉ (SANS NOIR / MODE IPAD) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* Masquer la barre latérale pour gagner de l'espace */
    [data-testid="stSidebar"] { display: none; }
    
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3, p, label { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }

    /* Correction des zones de saisie (Fond blanc, texte vert) */
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stTextArea textarea, .stTextInput input {
        background-color: white !important;
        border: 2px solid #c8e6c9 !important;
        border-radius: 12px !important;
        color: #1b5e20 !important;
        -webkit-text-fill-color: #1b5e20 !important;
    }

    /* Boutons (Texte blanc) */
    .stButton>button {
        background-color: #1b5e20 !important;
        border-radius: 20px !important;
        border: none !important;
    }
    .stButton>button p { color: white !important; font-weight: bold !important; }

    /* Style Bujo */
    .post-it {
        background: #fff9c4; padding: 25px; border-left: 6px solid #fbc02d;
        font-family: 'Indie Flower', cursive; font-size: 1.3rem; color: #5d4037 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-radius: 4px;
    }
    .bujo-block { background: white; padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 3. SYSTÈME DE SESSION ---
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# Fonction de login ultra-souple
def login_procedure(code_entre):
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

# Écran de connexion
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code = st.text_input("Code personnel :", type="password")
        if st.button("Valider"):
            user = login_procedure(code)
            if user:
                st.session_state.user_data = user
                st.rerun()
            else: st.error("Accès refusé.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. INTERFACE PRINCIPALE ---
user = st.session_state.user_data

# Header sans barre latérale
col_t, col_btn = st.columns([4, 1])
with col_t:
    st.markdown(f"<h1>Journal de {user['Nom']}</h1>", unsafe_allow_html=True)
with col_btn:
    if st.button("🔒 Déconnexion"):
        st.session_state.user_data = None
        st.rerun()

# Menu des onglets
menu = ["✍️ MON JOURNAL", "📊 TRACKERS", "📅 SEMAINE", "🎨 STICKERS", "🛒 COURSES"]
if user.get('Accès journal') == "OUI" or user.get('Accès Journal') == "OUI":
    menu.append("💰 BUDGET PRIVÉ")

tabs = st.tabs(menu)
t_idx = 0

# --- TABS LOGIC ---
# JOURNAL
with tabs[t_idx]:
    st.markdown(f"### ✨ Aujourd'hui, le {datetime.now().strftime('%d %B %Y')}")
    st.markdown('<div class="post-it">Écris tes pensées du jour ici...</div>', unsafe_allow_html=True)
    st.text_area("Note", label_visibility="collapsed", height=250, key="note_text")
t_idx += 1

# TRACKERS
with tabs[t_idx]:
    st.markdown("### 📊 Mes Suivis")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="bujo-block">💧 Verres d\'eau', unsafe_allow_html=True)
        st.slider("", 0, 10, 0, key="water_slider")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="bujo-block">🧘 Bien-être', unsafe_allow_html=True)
        st.checkbox("Méditation")
        st.checkbox("Lecture")
        st.markdown('</div>', unsafe_allow_html=True)
t_idx += 1

# SEMAINE (Grille simplifiée pour le test)
with tabs[t_idx]:
    st.markdown("### 🗓️ Vue de la Semaine")
    st.info("Ta grille hebdomadaire s'affichera ici.")
t_idx += 1

# STICKERS (AVEC TES LIENS GITHUB)
with tabs[t_idx]:
    st.header("🎨 Ma Planche de Stickers")
    st.write("Sur iPad : Reste appuyé sur un sticker pour le copier-coller.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🌿 Pack Cosy")
        # Lien direct vers stickers 2
        st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg", use_container_width=True)
    with col_b:
        st.subheader("📌 Organisation")
        # Lien direct vers stickers 1
        st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%201.jpg", use_container_width=True)
t_idx += 1

# COURSES
with tabs[t_idx]:
    st.markdown('<div class="bujo-block"><h3>🛒 Liste de Courses</h3></div>', unsafe_allow_html=True)
t_idx += 1

# BUDGET PRIVÉ
if "💰 BUDGET PRIVÉ" in menu:
    with tabs[t_idx]:
        st.markdown("### 🔒 Finances Privées")
