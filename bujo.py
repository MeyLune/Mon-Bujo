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
    except:
        return None

sh = init_connection()

# --- 2. DESIGN OPTIMISÉ IPAD (SANS SIDEBAR) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    /* Supprime la barre latérale pour gagner de la place sur iPad */
    [data-testid="stSidebar"] { display: none; }
    
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3, p, label, .stMarkdown { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }

    /* FIX NOIR : Forçage du fond blanc et texte vert sur TOUS les champs */
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"], .stTextArea textarea, .stTextInput input {
        background-color: white !important;
        border: 2px solid #c8e6c9 !important;
        border-radius: 12px !important;
        color: #1b5e20 !important;
        -webkit-text-fill-color: #1b5e20 !important;
    }

    /* Bouton Déconnexion & Valider avec texte blanc */
    .stButton>button {
        background-color: #1b5e20 !important;
        border-radius: 20px !important;
        border: none !important;
    }
    .stButton>button p { color: white !important; font-weight: bold !important; }

    /* Post-it */
    .post-it {
        background: #fff9c4; padding: 25px; border-left: 6px solid #fbc02d;
        font-family: 'Indie Flower', cursive; font-size: 1.3rem; color: #5d4037 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-radius: 4px; margin-bottom: 10px;
    }
    .bujo-block { background: white; padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state:
    st.session_state.user_data = None

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
            else: st.error("Code erroné")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. APPLICATION PRINCIPALE ---
user = st.session_state.user_data

# Titre et bouton de déconnexion alignés
col_t, col_btn = st.columns([4, 1])
with col_t:
    st.markdown(f"<h1>Journal de {user['Nom']}</h1>", unsafe_allow_html=True)
with col_btn:
    if st.button("🔒 Déconnexion"):
        st.session_state.user_data = None
        st.rerun()

# Menu des onglets (Le Tracker devient un onglet)
menu = ["📅 SEMAINE", "🛒 COURSES"]
if user.get('Accès journal') == "OUI" or user.get('Accès Journal') == "OUI":
    menu.insert(0, "✍️ MON JOURNAL")
    menu.insert(1, "📊 TRACKERS")
    menu.append("💰 BUDGET PRIVÉ")

tabs = st.tabs(menu)
idx = 0

# --- ONGLET : MON JOURNAL ---
if "✍️ MON JOURNAL" in menu:
    with tabs[idx]:
        st.markdown(f"### ✨ Aujourd'hui, le {datetime.now().strftime('%d %B %Y')}")
        st.markdown('<div class="post-it">Écris ici tes pensées ou tes inspirations...</div>', unsafe_allow_html=True)
        st.text_area("Note libre", label_visibility="collapsed", height=300, key="note_libre")
        if st.button("Ancrer au Journal"):
            st.success("Note enregistrée !")
    idx += 1

# --- ONGLET : TRACKERS ---
if "📊 TRACKERS" in menu:
    with tabs[idx]:
        st.markdown("### 📊 Mes suivis quotidiens")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
            st.write("💧 Hydratation")
            st.slider("Verres d'eau", 0, 10, 0)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
            st.write("🧘 Bien-être")
            st.checkbox("Méditation")
            st.checkbox("Lecture")
            st.markdown('</div>', unsafe_allow_html=True)
    idx += 1

# --- ONGLET : SEMAINE ---
with tabs[idx]:
    st.markdown("### 🗓️ Ma Semaine")
    # (La grille de la semaine s'affiche ici)
idx += 1

# --- ONGLET : COURSES ---
with tabs[idx]:
    st.markdown("### 🛒 Liste de Courses")
idx += 1

# --- ONGLET : BUDGET PRIVÉ ---
if "💰 BUDGET PRIVÉ" in menu:
    with tabs[idx]:
        st.markdown("### 🔒 Finances Détaillées")
