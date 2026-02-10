import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
from fpdf import FPDF

# ==========================================
# 1. CONNEXION & CONFIGURATION
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
# 2. STYLE ET POLICES (iPad Optimisé)
# ==========================================
st.set_page_config(page_title="Mon Bujo Nature", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Caveat:wght@400;700&display=swap" rel="stylesheet">
<style>
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
    .stApp { background: linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%); background-attachment: fixed; }
    
    h1, h2, h3, h4 { font-family: 'Comfortaa', cursive !important; color: white !important; }
    .header-banner { background: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 40px; margin-bottom: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); text-align: center; }
    .header-banner h1 { color: #1a2e26 !important; margin: 0; font-size: 2.2rem; }
    .date-display { font-family: 'Caveat', cursive; font-size: 1.8rem; color: #f1f1f1; text-align: center; margin-bottom: 20px; }

    /* Navigation */
    div.stRadio > div { flex-direction: row; justify-content: center; gap: 10px; margin-bottom: 20px; }
    div.stRadio label { font-family: 'Comfortaa', sans-serif !important; background: rgba(255, 255, 255, 0.1) !important; color: white !important; padding: 10px 20px !important; border-radius: 15px !important; border: 1px solid rgba(255,255,255,0.2) !important; }

    /* Inputs Vert sur Noir */
    input, textarea, [data-baseweb="select"] div { color: #00ffd9 !important; -webkit-text-fill-color: #00ffd9 !important; font-weight: bold !important; font-family: 'Comfortaa' !important; }
    div[data-baseweb="input"], div[data-baseweb="select"], .stTextArea textarea { background-color: #000 !important; border: 1px solid #00ffd9 !important; border-radius: 12px !important; }

    /* Blocs Spécifiques */
    .bujo-block { background: rgba(255, 255, 255, 0.08); padding: 25px; border-radius: 25px; border: 1px solid rgba(255,255,255,0.1); height: 100%; }
    .affirmation-text { font-family: 'Caveat'; font-size: 1.5rem; color: #d4a373; margin-top: 15px; font-style: italic; }

    .stButton>button { background-color: #00ffd9 !important; color: #1a2e26 !important; border-radius: 15px; font-weight: bold; border: none; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. INTERFACE
# ==========================================
try: user_name = ws_conf.acell('A2').value or "MeyLune"
except: user_name = "MeyLune"

st.markdown(f'<div class="header-banner"><h1>Journal de {user_name}</h1></div>', unsafe_allow_html=True)

page = st.radio("", ["📅 Année", "🌿 Semaine", "✍️ Mon Journal", "💰 Budget", "⚙️ Config"], 
                index=2, label_visibility="collapsed")

st.markdown(f'<div class="date-display">Nous sommes le {datetime.now().strftime("%d %B %Y")}</div>', unsafe_allow_html=True)

# --- PAGES ANNÉE / SEMAINE ---
if page == "📅 Année":
    st.markdown("### 🗺️ Vue d'ensemble 2026")
    cols = st.columns(3)
    mois_an = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    for i, m in enumerate(mois_an):
        with cols[i % 3]: st.button(m, use_container_width=True)

elif page == "🌿 Semaine":
    st.markdown(f"### 🗓️ Semaine {datetime.now().strftime('%W')}")
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    cols = st.columns(7)
    for i, d in enumerate(days):
        with cols[i]:
            st.markdown(f"**{d}**")
            st.button("📖", key=f"wk_{d}")

# --- PAGE MON JOURNAL (CORRIGÉE) ---
elif page == "✍️ Mon Journal":
    col_g, col_d = st.columns([1, 1], gap="large")

    with col_g:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        st.markdown("<h4>Mon Humeur & État</h4>", unsafe_allow_html=True)
        humeur = st.select_slider("", options=["😢", "😟", "😐", "🙂", "✨", "🔥"], value="😐", label_visibility="collapsed")
        
        # "Comment je me sens" juste en dessous de l'humeur
        sentiments = st.text_area("Comment je me sens aujourd'hui ?", placeholder="Détaille tes émotions ici...", height=150)
        
        # Affirmation en bas du bloc gauche
        st.markdown('<p class="affirmation-text">"Je suis capable de réaliser mes rêves."</p>', unsafe_allow_html=True)
        affirmation = st.text_input("Note une pensée positive :", placeholder="Écris ici...")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        st.markdown("<h4>Mon Programme</h4>", unsafe_allow_html=True)
        # Un seul grand encadré pour saisie manuelle libre
        programme_libre = st.text_area("Planning de la journée", 
                                     placeholder="08h00 : Yoga\n10h30 : Réunion\n14h00 : Projet BuJo...", 
                                     height=345)
        st.markdown('</div>', unsafe_allow_html=True)

    # Zone du bas : Notes & Tâches (inchangée car validée)
    st.write("---")
    st.markdown("### 🖋️ Notes & Tâches Rapides")
    c1, c2 = st.columns([3, 1])
    with c1: note_txt = st.text_input("Une chose à ne pas oublier ?", key="quick_note")
    with c2: note_type = st.selectbox("Type", ["🍃 Note", "📌 Tâche", "💡 Idée"], key="quick_type")
    
    if st.button("Ancrer dans mon historique"):
        if note_txt:
            ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), note_type, note_txt])
            st.rerun()

    st.markdown("#### 📜 Historique du jour")
    rows = ws_notes.get_all_values()
    if len(rows) > 1:
        for n in reversed(rows[1:]):
            if n[0] == datetime.now().strftime("%d/%m/%Y"):
                st.markdown(f"**{n[2]}** : {n[3]} <span style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>(🕒 {n[1]})</span>", unsafe_allow_html=True)

# --- PAGE BUDGET ---
elif page == "💰 Budget":
    st.markdown("### 🪙 Mes Finances")
    # (Le code budget avec éditeur et PDF reste ici tel quel...)
    with st.expander("➕ Ajouter une opération"):
        c1, c2, c3 = st.columns(3)
        cat = c1.selectbox("Type", ["Revenu", "Charge Fixe", "Dépense"])
        lab = c2.text_input("Libellé")
        val = c3.number_input("Montant €", step=0.01)
        if st.button("Enregistrer"):
            ws_fin.append_row([datetime.now().strftime("%B"), str(datetime.now().year), cat, lab, val])
            st.rerun()
    
    data = ws_fin.get_all_records()
    if data:
        df = pd.DataFrame(data)
        st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- PAGE CONFIG ---
elif page == "⚙️ Config":
    st.markdown("### ⚙️ Paramètres")
    new_name = st.text_input("Nom d'utilisateur :", user_name)
    if st.button("Valider"):
        ws_conf.update_acell('A2', new_name)
        st.rerun()
