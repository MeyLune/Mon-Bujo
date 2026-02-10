import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ==========================================
# 1. CONNEXION GOOGLE SHEETS (SCOPES CORRIGÉS)
# ==========================================
def init_connection():
    # On ajoute le scope "drive" pour éviter l'erreur 403 (Request had insufficient authentication scopes)
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        # Utilisation de TES clés configurées dans Streamlit Cloud
        creds_info = {
            "type": "service_account",
            "project_id": "airy-semiotics-486311-v5",
            "private_key": st.secrets["MY_PRIVATE_KEY"],
            "client_email": st.secrets["MY_CLIENT_EMAIL"],
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open("db_bujo")
    except Exception as e:
        st.error(f"Erreur de connexion au tableur : {e}")
        return None

sh = init_connection()

if sh:
    try:
        # On utilise "Note" au singulier comme sur ton Google Sheets
        ws_notes = sh.worksheet("Note")
        ws_fin = sh.worksheet("Finances")
        ws_conf = sh.worksheet("Config")
    except Exception as e:
        st.error(f"Erreur : Un onglet est introuvable ({e}). Vérifie ton Google Sheets !")
        st.stop()
else:
    st.stop()

# ==========================================
# 2. DESIGN ENCHANTÉ AVEC FEUILLES EN FOND
# ==========================================
st.set_page_config(page_title="Mon BuJo Enchanté", layout="wide")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
<style>
    /* Fond dégradé avec illustrations de feuilles en arrière-plan */
    .stApp {
        background: linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%);
        background-image: 
            url('https://www.transparenttextures.com/patterns/leaf.png'), 
            linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%);
        background-attachment: fixed;
    }
    
    /* Bannière titre blanche */
    .header-banner {
        background-color: white;
        padding: 15px;
        border-radius: 50px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .header-banner h1 { 
        color: #1a2e26 !important; 
        margin: 0; 
        font-family: 'Playfair Display', serif;
        font-size: 32px; 
    }

    /* Cartes blanches pour le contenu */
    .bujo-card {
        background-color: rgba(255, 255, 255, 0.92);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.3);
    }

    /* Zone de note manuscrite (Post-it) */
    .handwritten-note {
        background-color: #fff9c4;
        font-family: 'Caveat', cursive;
        font-size: 26px;
        padding: 25px;
        border-radius: 5px;
        border-left: 6px solid #fbc02d;
        color: #5d4037 !important;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.1);
        line-height: 1.2;
    }

    /* Sidebar foncée */
    [data-testid="stSidebar"] { 
        background-color: #0e1a15 !important; 
        border-right: 3px solid #d4a373; 
    }
    
    /* Boutons */
    .stButton>button {
        background-color: #7fb79e !important;
        color: #1a2e26 !important;
        border-radius: 12px;
        font-weight: bold;
        width: 100%;
        border: 2px solid #1a2e26;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. NAVIGATION & DONNÉES DE CONFIG
# ==========================================
with st.sidebar:
    # On récupère ton prénom en A2 de l'onglet Config
    try:
        user_name = ws_conf.acell('A2').value or "MeyLune"
    except:
        user_name = "MeyLune"
        
    st.markdown(f"# 🌿 {user_name}")
    page = st.radio("Navigation", ["📅 Daily Log", "💰 Finances", "⚙️ Config"])
    st.write("---")
    st.markdown('<div style="color:#d4a373; text-align:center; border:1px dashed #d4a373; padding:10px; border-radius:10px;">✨ E
