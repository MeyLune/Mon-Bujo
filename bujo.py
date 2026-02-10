import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# ==========================================
# 1. CONNEXION GOOGLE SHEETS
# ==========================================
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
        client = gspread.authorize(creds)
        return client.open("db_bujo")
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None

sh = init_connection()
if sh:
    ws_notes = sh.worksheet("Note")
    ws_fin = sh.worksheet("Finances")
    ws_conf = sh.worksheet("Config")
else:
    st.stop()

# ==========================================
# 2. DESIGN & STYLE (SANS SIDEBAR + POLICES DOUCES)
# ==========================================
st.set_page_config(page_title="Mon BuJo Douceur", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Caveat:wght@400;700&display=swap" rel="stylesheet">
<style>
    /* Masquer la sidebar et le bouton de menu */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
    button[kind="headerNoSpacing"] { display: none !important; }

    /* Fond Forestier Doux */
    .stApp {
        background: linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%);
        background-attachment: fixed;
    }

    /* Titres Principaux (Comfortaa) */
    h1, h2, h3, .header-text {
        font-family: 'Comfortaa', cursive !important;
        color: white !important;
        text-align: center;
    }

    /* Bandeau Titre */
    .header-banner { 
        background: rgba(255, 255, 255, 0.95); 
        padding: 25px; 
        border-radius: 40px; 
        margin-bottom: 15px; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .header-banner h1 { color: #1a2e26 !important; margin: 0; font-size: 2.2rem; }

    /* Date Style Manuscrit */
    .date-display {
        font-family: 'Caveat', cursive;
        font-size: 1.8rem;
        color: #d4a373;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Navigation Horizontale */
    div.stRadio > div {
        flex-direction: row;
        justify-content: center;
        gap: 15px;
    }
    div.stRadio label {
        font-family: 'Comfortaa', sans-serif !important;
        background: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        padding: 12px 25px !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }

    /* Correction Saisie iPad (Vert d'eau sur Noir) */
    input, textarea, [data-baseweb="select"] div {
        color: #00ffd9 !important;
        -webkit-text-fill-color: #00ffd9 !important;
        font-weight: bold !important;
        font-size: 18px !important;
        font-family: 'Comfortaa', sans-serif !important;
    }

    div[data-baseweb="input"], div[data-baseweb="select"], .stTextArea textarea {
        background-color: #000000 !important;
        border: 2px solid #00ffd9 !important;
        border-radius: 15px !important;
    }

    /* Boutons */
    .stButton>button {
        background-color: #00ffd9 !important;
        color: #1a2e26 !important;
        border-radius: 20px;
        font-family: 'Comfortaa', sans-serif;
        font-weight: bold;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. INTERFACE CENTRALE
# ==========================================

# Récupération du nom
try: user_name = ws_conf.acell('A2').value or "MeyLune"
except: user_name = "MeyLune"

# 1. Le Titre
st.markdown(f'<div class="header-banner"><h1>Journal de {user_name}</h1></div>', unsafe_allow_html=True)

# 2. La Navigation
page = st.radio("", ["📅 Daily Log", "💰 Finances", "⚙️ Config"], label_visibility="collapsed")

# 3. La Date (Juste en dessous)
st.markdown(f'<div class="date-display">Nous sommes le {datetime.now().strftime("%d %B %Y")}</div>', unsafe_allow_html=True)

st.write("---")

# --- PAGE DAILY LOG ---
if page == "📅 Daily Log":
    st.markdown("## 🌿 Notes du jour")
    col1, col2 = st.columns([3, 1])
    with col1:
        txt = st.text_input("Une pensée ?", placeholder="Écris ici ton secret...")
    with col2:
        sym = st.selectbox("Style", ["🍃 Note", "📌 Tâche", "✨ Évent", "♡"])
    
    if st.button("Enregistrer dans mon Bujo"):
        if txt:
            ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), sym, txt])
            st.rerun()

    st.write("### Historique récent")
    rows = ws_notes.get_all_values()
    if len(rows) > 1:
        for n in reversed(rows[1:]):
            st.write(f"**{n[2]}** {n[3]}  *(🕒 {n[1]})*")

# --- PAGE FINANCES ---
elif page == "💰 Finances":
    st.markdown("## 💹 Mon Petit Budget")
    
    mois_liste = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    c1, c2 = st.columns(2)
    sel_mois = c1.selectbox("Mois", mois_liste, index=datetime.now().month - 1)
    sel_annee = c2.selectbox("Année", [2025, 2026, 2027], index=1)

    with st.expander("✨ Ajouter une ligne", expanded=True):
        cat = st.selectbox("Catégorie", ["Revenu", "Charge Fixe", "Dépense"])
        label = st.text_input("Libellé")
        valeur = st.number_input("Montant €", step=0.01, format="%.2f")
        
        if st.button(f"Ajouter à {sel_mois}"):
            ws_fin.append_row([sel_mois, str(sel_annee), cat, label, valeur])
            st.success("C'est enregistré avec succès !")
            st.rerun()

    # Calculs
    data = ws_fin.get_all_records()
    if data:
        df = pd.DataFrame(data)
        df_mois = df[(df['Mois'] == sel_mois) & (df['Année'].astype(str) == str(sel_annee))]
        if not df_mois.empty:
            rev = df_mois[df_mois['Catégorie'] == 'Revenu']['Montant €'].sum()
            dep = df_mois[df_mois['Catégorie'] != 'Revenu']['Montant €'].sum()
            st.metric("Solde restant", f"{rev-dep:.2f} €", delta=f"{rev} € revenus")

# --- PAGE CONFIG ---
elif page == "⚙️ Config":
    st.markdown("## ⚙️ Réglages")
    new_name = st.text_input("Comment dois-je t'appeler ?", user_name)
    if st.button("Mettre à jour le prénom"):
        ws_conf.update_acell('A2', new_name)
        st.success("C'est fait !")
        st.rerun()
