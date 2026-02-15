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

# --- 2. DESIGN & STYLE (SANS NOIR) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3, p, label { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }

    /* Forçage des zones de saisie en blanc */
    div[data-baseweb="input"], div[data-baseweb="textarea"], select {
        background-color: white !important;
        border: 2px solid #c8e6c9 !important;
        border-radius: 12px !important;
    }
    input, textarea {
        color: #1b5e20 !important;
        -webkit-text-fill-color: #1b5e20 !important;
    }

    /* Bouton vert "Valider" */
    .stButton>button {
        background-color: #1b5e20 !important;
        color: white !important;
        border-radius: 25px !important;
        height: 3em !important;
        width: 100% !important;
        font-weight: bold !important;
    }
    
    .bujo-block { background: white; padding: 25px; border-radius: 25px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 3. SYSTÈME DE LOGIN SÉCURISÉ ---
if "user_data" not in st.session_state:
    st.session_state.user_data = None

def login_procedure(code_entre):
    if sh:
        try:
            # On récupère l'onglet Utilisateurs
            ws = sh.worksheet("Utilisateurs")
            data = ws.get_all_records()
            if not data:
                return None
                
            # On nettoie les noms de colonnes pour éviter les erreurs de lecture
            df = pd.DataFrame(data)
            df.columns = [c.strip().capitalize() for c in df.columns]
            
            # On vérifie si la colonne 'Code' existe bien après nettoyage
            if 'Code' in df.columns:
                df['Code'] = df['Code'].astype(str).str.strip()
                match = df[df['Code'] == str(code_entre).strip()]
                if not match.empty:
                    return match.iloc[0].to_dict()
            else:
                st.error(f"Colonne 'Code' introuvable. Colonnes vues : {list(df.columns)}")
        except Exception as e:
            st.error(f"Erreur technique : {e}")
    return None

# --- ÉCRAN DE DÉMARRAGE ---
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1, 1])
    with col_center:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code_saisi = st.text_input("Entre ton code personnel :", type="password")
        if st.button("Valider"): # Texte du bouton mis à jour
            user = login_procedure(code_saisi)
            if user:
                st.session_state.user_data = user
                st.rerun()
            else:
                st.error("Accès refusé.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SI CONNECTÉ ---
user = st.session_state.user_data
st.success(f"Bienvenue {user['Nom']} !")

if st.button("🔒 Déconnexion"):
    st.session_state.user_data = None
    st.rerun()
