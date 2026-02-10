import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
from fpdf import FPDF
import base64

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
    [data-testid="stSidebar"] { display: none !important; }
    .stApp { background: linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%); background-attachment: fixed; }
    
    h1, h2, h3, .header-text { font-family: 'Comfortaa', cursive !important; color: white !important; text-align: center; }
    .header-banner { background: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 40px; margin-bottom: 10px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); text-align: center; }
    .header-banner h1 { color: #1a2e26 !important; margin: 0; font-size: 2rem; }
    .date-display { font-family: 'Caveat', cursive; font-size: 1.6rem; color: #f1f1f1; text-align: center; margin-bottom: 20px; }

    /* Navigation */
    div.stRadio > div { flex-direction: row; justify-content: center; gap: 10px; }
    div.stRadio label { font-family: 'Comfortaa', sans-serif !important; background: rgba(255, 255, 255, 0.1) !important; color: white !important; padding: 10px 15px !important; border-radius: 15px !important; border: 1px solid rgba(255,255,255,0.2) !important; }

    /* Inputs Vert sur Noir pour iPad */
    input, textarea, [data-baseweb="select"] div { color: #00ffd9 !important; -webkit-text-fill-color: #00ffd9 !important; font-weight: bold !important; font-family: 'Comfortaa' !important; }
    div[data-baseweb="input"], div[data-baseweb="select"], .stTextArea textarea { background-color: #000 !important; border: 1px solid #00ffd9 !important; border-radius: 12px !important; }

    /* Boutons */
    .stButton>button { background-color: #00ffd9 !important; color: #1a2e26 !important; border-radius: 15px; font-weight: bold; border: none; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. FONCTIONS OUTILS
# ==========================================
def create_pdf(df_mois, mois, annee):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Rapport Financier - {mois} {annee}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Categorie", 1)
    pdf.cell(80, 10, "Libelle", 1)
    pdf.cell(40, 10, "Montant", 1)
    pdf.ln()
    pdf.set_font("Arial", '', 12)
    for index, row in df_mois.iterrows():
        pdf.cell(60, 10, str(row['Catégorie']), 1)
        pdf.cell(80, 10, str(row['Libellé']), 1)
        pdf.cell(40, 10, f"{row['Montant €']} e", 1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 4. INTERFACE PRINCIPALE
# ==========================================
try: user_name = ws_conf.acell('A2').value or "MeyLune"
except: user_name = "MeyLune"

st.markdown(f'<div class="header-banner"><h1>Journal de {user_name}</h1></div>', unsafe_allow_html=True)

page = st.radio("", ["📅 Année", "🌿 Semaine", "✍️ Mon Journal", "💰 Budget", "⚙️ Config"], 
                index=2, label_visibility="collapsed")

st.markdown(f'<div class="date-display">Nous sommes le {datetime.now().strftime("%d %B %Y")}</div>', unsafe_allow_html=True)

# --- VUE ANNUELLE ---
if page == "📅 Année":
    st.markdown("### 🗺️ Vue d'ensemble 2026")
    cols = st.columns(3)
    mois_an = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    for i, m in enumerate(mois_an):
        with cols[i % 3]:
            if st.button(m, use_container_width=True):
                st.info(f"Visualisation des notes de {m} en cours de développement...")

# --- VUE SEMAINE ---
elif page == "🌿 Semaine":
    st.markdown(f"### 🗓️ Semaine du {datetime.now().strftime('%W')}")
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    cols = st.columns(7)
    for i, d in enumerate(days):
        cols[i].markdown(f"**{d}**")
        cols[i].button("📖", key=f"btn_{d}")

# --- MON JOURNAL (Ex-Daily Log) ---
elif page == "✍️ Mon Journal":
    st.markdown("### 🍃 Ma Bulle du Jour")
    col1, col2 = st.columns([3, 1])
    with col1:
        txt = st.text_input("Comment te sens-tu ?", placeholder="Écris ici...")
    with col2:
        sym = st.selectbox("Humeur", ["🍃 Douceur", "📌 À faire", "✨ Magique", "🔥 Urgent"])
    
    if st.button("Ancrer cette pensée"):
        if txt:
            ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), sym, txt])
            st.rerun()

    st.write("---")
    rows = ws_notes.get_all_values()
    if len(rows) > 1:
        for n in reversed(rows[1:]):
            st.markdown(f"**{n[2]}** : {n[3]} *(🕒 {n[1]})*")

# --- BUDGET (Avec Historique & PDF) ---
elif page == "💰 Budget":
    st.markdown("### 🪙 Mes Petites Finances")
    
    # Formulaire d'ajout
    with st.expander("➕ Ajouter une opération", expanded=False):
        c1, c2, c3 = st.columns(3)
        cat = c1.selectbox("Type", ["Revenu", "Charge Fixe", "Dépense"])
        lab = c2.text_input("Libellé")
        val = c3.number_input("Montant", step=1.0)
        if st.button("Enregistrer l'opération"):
            ws_fin.append_row([datetime.now().strftime("%B"), str(datetime.now().year), cat, lab, val])
            st.rerun()

    # Historique & Modification
    data = ws_fin.get_all_records()
    if data:
        df = pd.DataFrame(data)
        st.write("#### Historique du mois")
        edited_df = st.data_editor(df, num_rows="dynamic")
        
        if st.button("💾 Sauvegarder les modifications"):
            ws_fin.clear()
            ws_fin.append_row(["Mois", "Année", "Catégorie", "Libellé", "Montant €"])
            ws_fin.append_rows(edited_df.values.tolist())
            st.success("Base de données mise à jour !")

        # PDF
        pdf_data = create_pdf(df, "Février", "2026")
        st.download_button("📥 Télécharger le rapport PDF", pdf_data, file_name="budget.pdf", mime="application/pdf")

# --- CONFIG ---
elif page == "⚙️ Config":
    st.markdown("### 🛠️ Personnalisation")
    new_name = st.text_input("Changer mon nom d'utilisateur :", user_name)
    if st.button("Valider"):
        ws_conf.update_acell('A2', new_name)
        st.rerun()
