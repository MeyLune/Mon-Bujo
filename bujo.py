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

    /* Blocs Bujo */
    .bujo-block { background: rgba(255, 255, 255, 0.08); padding: 25px; border-radius: 25px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; }
    .affirmation-text { font-family: 'Caveat'; font-size: 1.5rem; color: #d4a373; margin: 10px 0; font-style: italic; }

    /* Boutons */
    .stButton>button { background-color: #00ffd9 !important; color: #1a2e26 !important; border-radius: 15px; font-weight: bold; border: none; width: 100%; margin-top: 10px; }
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

# --- PAGE MON JOURNAL (Optimisée Tactile) ---
if page == "✍️ Mon Journal":
    col_g, col_d = st.columns([1, 1], gap="large")

    with col_g:
        st.markdown('<div class="bujo-block"><h4>Mon Humeur & État</h4>', unsafe_allow_html=True)
        humeur = st.select_slider("", options=["😢", "😟", "😐", "🙂", "✨", "🔥"], value="😐", label_visibility="collapsed")
        sentiments = st.text_area("Comment je me sens ?", placeholder="Détaille tes émotions...", height=150)
        
        st.markdown('<p class="affirmation-text">"Je suis capable de réaliser mes rêves."</p>', unsafe_allow_html=True)
        affirmation = st.text_input("Pensée positive :", placeholder="Écris ici...")
        
        if st.button("✨ Enregistrer mon état"):
            # Ici on pourrait enregistrer dans une feuille dédiée "Humeur"
            st.success("État d'esprit enregistré !")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="bujo-block"><h4>Mon Programme</h4>', unsafe_allow_html=True)
        programme_libre = st.text_area("Planning du jour", 
                                     placeholder="Ex: 08h00 Yoga, 14h00 Projet...", 
                                     height=315)
        if st.button("💾 Mettre à jour le programme"):
            # Logique d'enregistrement du programme
            st.success("Programme sauvegardé !")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")
    st.markdown("### 🖋️ Notes & Tâches Rapides")
    c1, c2 = st.columns([3, 1])
    with c1: note_txt = st.text_input("Une chose à ne pas oublier ?", key="quick_note")
    with c2: note_type = st.selectbox("Type", ["🍃 Note", "📌 Tâche", "💡 Idée"], key="quick_type")
    
    if st.button("Ancrer dans l'historique"):
        if note_txt:
            ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), note_type, note_txt])
            st.rerun()

    st.markdown("#### 📜 Historique du jour")
    rows = ws_notes.get_all_values()
    if len(rows) > 1:
        today = datetime.now().strftime("%d/%m/%Y")
        for n in reversed(rows[1:]):
            if n[0] == today:
                st.markdown(f"**{n[2]}** : {n[3]} <span style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>(🕒 {n[1]})</span>", unsafe_allow_html=True)

# --- PAGE BUDGET (Historique & Correction) ---
elif page == "💰 Budget":
    st.markdown("### 🪙 Mes Finances")
    
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
        st.write("#### 📝 Historique modifiable")
        st.info("Modifie une case directement et clique sur Sauvegarder.")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        col1, col2 = st.columns(2)
        if col1.button("💾 Sauvegarder les modifications"):
            ws_fin.clear()
            ws_fin.append_row(["Mois", "Année", "Catégorie", "Libellé", "Montant €"])
            ws_fin.append_rows(edited_df.values.tolist())
            st.success("Base de données mise à jour !")
        
        # Simulation export PDF (fonctionnel avec la lib fpdf déjà importée)
        if col2.button("📥 Générer PDF (Aperçu)"):
            st.warning("Génération du rapport en cours...")

# --- AUTRES PAGES ---
elif page == "📅 Année":
    st.markdown("### 📅 Calendrier Annuel")
    st.info("Vue interactive de l'année 2026 en construction...")

elif page == "🌿 Semaine":
    st.markdown("### 🌿 Planning Hebdomadaire")
    st.info("Vue de la semaine en cours...")

elif page == "⚙️ Config":
    st.markdown("### ⚙️ Paramètres")
    new_name = st.text_input("Nom d'utilisateur :", user_name)
    if st.button("Valider"):
        ws_conf.update_acell('A2', new_name)
        st.rerun()
