import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

# --- 1. CONNEXION SÉCURISÉE ---
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
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None

sh = init_connection()

# --- 2. DESIGN "ANTI-NOIR" & FORÇAGE COULEURS ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    
    /* Forçage des titres en Vert Forêt */
    h1, h2, h3, p, label { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }

    /* NETTOYAGE DES CHAMPS NOIRS */
    div[data-baseweb="input"], div[data-baseweb="textarea"], select {
        background-color: white !important;
        border: 2px solid #c8e6c9 !important;
        border-radius: 12px !important;
    }
    input, textarea {
        color: #1b5e20 !important;
        -webkit-text-fill-color: #1b5e20 !important;
        font-weight: bold !important;
    }

    /* Post-it pour iPad */
    .post-it {
        background: #fff9c4; padding: 25px; border-left: 6px solid #fbc02d;
        font-family: 'Indie Flower', cursive; font-size: 1.3rem; color: #5d4037 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-radius: 4px;
    }
    
    /* Blocs blancs arrondis */
    .bujo-block { background: white; padding: 25px; border-radius: 25px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    .p-header { background-color: #f06292; color: white !important; padding: 12px; text-align: center; border-radius: 15px 15px 0 0; font-weight: bold; }
    .p-cell { background-color: white; min-height: 160px; padding: 15px; border: 1px solid #fce4ec; border-radius: 0 0 15px 15px; margin-bottom: 25px; }
    .event-tag { background: #fff1f3; border-left: 4px solid #f06292; padding: 6px; margin-bottom: 6px; border-radius: 5px; font-size: 0.9rem; color: #ad1457 !important; }

    /* Boutons stylisés */
    .stButton>button {
        background-color: #1b5e20 !important;
        color: white !important;
        border-radius: 30px !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SYSTÈME DE LOGIN CORRIGÉ ---
if "user_data" not in st.session_state:
    st.session_state.user_data = None

def login_procedure(code_entre):
    if sh:
        try:
            # Récupérer les utilisateurs et transformer les codes en chaînes de caractères (String)
            users_df = pd.DataFrame(sh.worksheet("Utilisateurs").get_all_records())
            users_df['Code'] = users_df['Code'].astype(str).str.strip()
            
            match = users_df[users_df['Code'] == str(code_entre).strip()]
            if not match.empty:
                return match.iloc[0].to_dict()
        except Exception as e:
            st.error(f"Erreur de lecture du tableau : {e}")
    return None

# ÉCRAN DE LOGIN
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1, 1])
    with col_center:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code_saisi = st.text_input("Entre ton code personnel :", type="password", key="main_login")
        if st.button("Ouvrir mon Journal", use_container_width=True):
            user = login_procedure(code_saisi)
            if user:
                st.session_state.user_data = user
                st.rerun()
            else:
                st.error("Code invalide ou erreur de connexion.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. SI CONNECTÉ : CHARGEMENT DU BUJO ---
user = st.session_state.user_data
st.markdown(f"<h1 style='text-align:center;'>Journal de {user['Nom']}</h1>", unsafe_allow_html=True)

# Barre latérale (Sidebar)
with st.sidebar:
    st.markdown(f"### 👤 {user['Nom']}")
    st.write(f"Rôle : {user['Rôle']}")
    if st.button("🔒 Se déconnecter"):
        st.session_state.user_data = None
        st.rerun()

# Configuration des onglets dynamiques
menu = ["📅 SEMAINE", "🛍️ COURSES"]
if user['Accès Journal'] == "OUI":
    menu.insert(0, "✍️ MON JOURNAL")
    menu.append("💰 BUDGET PRIVÉ")

tabs = st.tabs(menu)
idx = 0

# 1. JOURNAL (ADMIN SEULEMENT)
if user['Accès Journal'] == "OUI":
    with tabs[idx]:
        st.markdown(f"### 📔 Notes du {datetime.now().strftime('%d %B %Y')}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="post-it">Écris ici avec ton Pencil...</div>', unsafe_allow_html=True)
            st.text_area("Note", label_visibility="collapsed", height=200, key="note_ipad")
        with col_b:
            st.markdown('<div class="bujo-block"><h3>📊 Suivi Humeur</h3>', unsafe_allow_html=True)
            st.select_slider("Mon énergie", options=["🔋", "😐", "🙂", "✨", "🔥"])
            st.markdown('</div>', unsafe_allow_html=True)
    idx += 1

# 2. SEMAINE (TOUS)
with tabs[idx]:
    st.markdown("### 🗓️ Ma Semaine")
    # Logique de la grille ici...
    st.info("La grille s'affichera ici une fois connecté !")
idx += 1

# 3. COURSES (TOUS)
with tabs[idx]:
    st.markdown('<div class="bujo-block"><h3>🛒 Liste de Courses</h3></div>', unsafe_allow_html=True)

# 4. BUDGET PRIVÉ (ADMIN)
if user['Accès Journal'] == "OUI":
    with tabs[idx]:
        st.markdown("### 💰 Finances Secrètes")
        st.warning("Accès réservé à MeyLune.")
