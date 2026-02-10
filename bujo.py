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
# 2. DESIGN & STYLE (Optimisation iPad)
# ==========================================
st.set_page_config(page_title="Mon BuJo", layout="wide")

st.markdown("""
<style>
    /* Fond et Structure */
    .stApp {
        background: linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%);
        background-attachment: fixed;
    }

    /* Bandeau Titre */
    .header-banner { 
        background-color: white; 
        padding: 20px; 
        border-radius: 30px; 
        text-align: center; 
        margin-bottom: 10px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.3); 
    }
    .header-banner h1 { color: #1a2e26 !important; font-size: 2.5rem; }

    /* --- NAVIGATION HORIZONTALE --- */
    div.stRadio > div {
        flex-direction: row;
        justify-content: center;
        background: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    div.stRadio label {
        background: transparent !important;
        color: white !important;
        padding: 10px 20px !important;
        border-radius: 10px !important;
    }

    /* --- CORRECTION VISIBILITÉ IPAD (VERT SUR NOIR) --- */
    input, textarea, [data-baseweb="select"] div {
        color: #00ffd9 !important; /* Vert d'eau néon pour visibilité max */
        -webkit-text-fill-color: #00ffd9 !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }

    div[data-baseweb="input"], div[data-baseweb="select"], .stTextArea textarea {
        background-color: #000000 !important; /* Fond noir total pour le contraste */
        border: 2px solid #00ffd9 !important;
        border-radius: 8px !important;
    }

    /* Boutons */
    .stButton>button {
        background-color: #00ffd9 !important;
        color: #1a2e26 !important;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
    }

    /* Stats Cards */
    .stat-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        color: #1a2e26;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. INTERFACE
# ==========================================

# Nom utilisateur
try: user_name = ws_conf.acell('A2').value or "MeyLune"
except: user_name = "MeyLune"

# Sidebar simplifiée
with st.sidebar:
    st.markdown(f"### 🌿 {user_name}")
    st.info(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

# Titre Principal
st.markdown(f'<div class="header-banner"><h1>Journal de {user_name}</h1></div>', unsafe_allow_html=True)

# NAVIGATION (Déplacée au centre comme demandé)
page = st.radio("", ["📅 Daily Log", "💰 Finances", "⚙️ Config"], label_visibility="collapsed")

st.write("---")

# --- PAGE DAILY LOG ---
if page == "📅 Daily Log":
    st.subheader("Daily Log")
    col1, col2 = st.columns([3, 1])
    with col1:
        txt = st.text_input("Nouvelle pensée...", placeholder="Écris ici (vert sur noir)")
    with col2:
        sym = st.selectbox("Style", ["🍃 Note", "📌 Tâche", "✨ Événement"])
    
    if st.button("Enregistrer la note"):
        if txt:
            ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), sym, txt])
            st.rerun()

    st.write("### Tes notes du jour")
    rows = ws_notes.get_all_values()
    if len(rows) > 1:
        for n in reversed(rows[1:]):
            st.write(f"**{n[2]}** {n[3]} *(🕒 {n[1]})*")

# --- PAGE FINANCES ---
elif page == "💰 Finances":
    st.subheader("Mes Finances")
    
    mois_liste = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    c1, c2 = st.columns(2)
    sel_mois = c1.selectbox("Mois", mois_liste, index=datetime.now().month - 1)
    sel_annee = c2.selectbox("Année", [2025, 2026, 2027], index=1)

    with st.expander("➕ Ajouter une opération", expanded=True):
        cat = st.selectbox("Catégorie", ["Revenu", "Charge Fixe", "Dépense"])
        label = st.text_input("Libellé")
        valeur = st.number_input("Montant €", step=0.01, format="%.2f")
        
        if st.button(f"Ajouter à {sel_mois}"):
            ws_fin.append_row([sel_mois, str(sel_annee), cat, label, valeur])
            st.success("Enregistré !")
            st.rerun()

    # Calculs rapides (Sommaire)
    data = ws_fin.get_all_records()
    if data:
        df = pd.DataFrame(data)
        df_mois = df[(df['Mois'] == sel_mois) & (df['Année'].astype(str) == str(sel_annee))]
        
        if not df_mois.empty:
            rev = df_mois[df_mois['Catégorie'] == 'Revenu']['Montant €'].sum()
            dep = df_mois[df_mois['Catégorie'] != 'Revenu']['Montant €'].sum()
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Revenus", f"{rev:.2f} €")
            col_b.metric("Dépenses", f"{dep:.2f} €")
            col_c.metric("Reste", f"{rev-dep:.2f} €")

# --- PAGE CONFIG ---
elif page == "⚙️ Config":
    st.subheader("Paramètres")
    new_name = st.text_input("Modifier mon nom :", user_name)
    if st.button("Sauvegarder"):
        ws_conf.update_acell('A2', new_name)
        st.success("Nom mis à jour !")
        st.rerun()
