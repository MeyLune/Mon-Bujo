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
    /* Suppression Sidebar */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
    
    /* Fond Forestier */
    .stApp { background: linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%); background-attachment: fixed; }
    
    /* Titres et Textes */
    h1, h2, h3, h4 { font-family: 'Comfortaa', cursive !important; color: white !important; }
    .header-banner { background: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 40px; margin-bottom: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); text-align: center; }
    .header-banner h1 { color: #1a2e26 !important; margin: 0; font-size: 2.2rem; }
    .date-display { font-family: 'Caveat', cursive; font-size: 1.8rem; color: #f1f1f1; text-align: center; margin-bottom: 20px; }

    /* Navigation Horizontale */
    div.stRadio > div { flex-direction: row; justify-content: center; gap: 10px; margin-bottom: 20px; }
    div.stRadio label { font-family: 'Comfortaa', sans-serif !important; background: rgba(255, 255, 255, 0.1) !important; color: white !important; padding: 10px 20px !important; border-radius: 15px !important; border: 1px solid rgba(255,255,255,0.2) !important; }

    /* Inputs Vert sur Noir pour Contraste iPad */
    input, textarea, [data-baseweb="select"] div { color: #00ffd9 !important; -webkit-text-fill-color: #00ffd9 !important; font-weight: bold !important; font-family: 'Comfortaa' !important; }
    div[data-baseweb="input"], div[data-baseweb="select"], .stTextArea textarea { background-color: #000 !important; border: 1px solid #00ffd9 !important; border-radius: 12px !important; }

    /* Blocs Journal */
    .journal-box { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2); margin-bottom: 15px; }
    .affirmation-box { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 20px; border-left: 5px solid #00ffd9; font-family: 'Caveat'; font-size: 1.4rem; color: #fff; }

    /* Boutons */
    .stButton>button { background-color: #00ffd9 !important; color: #1a2e26 !important; border-radius: 15px; font-weight: bold; border: none; width: 100%; }
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
        pdf.cell(40, 10, f"{row['Montant €']} €", 1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 4. INTERFACE PRINCIPALE
# ==========================================
try: user_name = ws_conf.acell('A2').value or "MeyLune"
except: user_name = "MeyLune"

st.markdown(f'<div class="header-banner"><h1>Journal de {user_name}</h1></div>', unsafe_allow_html=True)

# Barre de Navigation
page = st.radio("", ["📅 Année", "🌿 Semaine", "✍️ Mon Journal", "💰 Budget", "⚙️ Config"], 
                index=2, label_visibility="collapsed")

st.markdown(f'<div class="date-display">Nous sommes le {datetime.now().strftime("%d %B %Y")}</div>', unsafe_allow_html=True)

# --- PAGE ANNÉE ---
if page == "📅 Année":
    st.markdown("### 🗺️ Vue d'ensemble 2026")
    cols = st.columns(3)
    mois_an = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    for i, m in enumerate(mois_an):
        with cols[i % 3]:
            st.button(m, use_container_width=True, key=f"yr_{m}")

# --- PAGE SEMAINE ---
elif page == "🌿 Semaine":
    st.markdown(f"### 🗓️ Semaine {datetime.now().strftime('%W')}")
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    cols = st.columns(7)
    for i, d in enumerate(days):
        with cols[i]:
            st.markdown(f"**{d}**")
            st.button("📖", key=f"wk_{d}")

# --- PAGE MON JOURNAL (Mise en page demandée) ---
elif page == "✍️ Mon Journal":
    col_g, col_d = st.columns([1.2, 1], gap="large")

    with col_g:
        st.markdown('<div class="journal-box"><h4>Mon Humeur</h4>', unsafe_allow_html=True)
        humeur = st.select_slider("", options=["😢", "😟", "😐", "🙂", "✨", "🔥"], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="affirmation-box">"Je suis capable de réaliser mes rêves."</div>', unsafe_allow_html=True)
        affirmation = st.text_input("Affirmation du jour", placeholder="Ta propre pensée positive...", label_visibility="collapsed")

        st.markdown("<br><h4>Comment je me sens ?</h4>", unsafe_allow_html=True)
        feelings = st.text_area("Détaille tes émotions...", height=100, label_visibility="collapsed")

    with col_d:
        st.markdown('<div class="journal-box" style="text-align:center;"><h4>Mon Programme</h4>', unsafe_allow_html=True)
        heures = ["08h00", "12h00", "16h00", "20h00"]
        for h in heures:
            st.text_input(f"🕒 {h}", placeholder=f"Quoi de neuf à {h} ?", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")
    st.markdown("### 🖋️ Notes & Tâches Rapides")
    c1, c2 = st.columns([3, 1])
    with c1: note_txt = st.text_input("Note ou tâche...", key="quick_note")
    with c2: note_type = st.selectbox("Type", ["🍃 Note", "📌 Tâche", "💡 Idée"], key="quick_type")
    
    if st.button("Ancrer dans mon journal"):
        if note_txt:
            ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), note_type, note_txt])
            st.rerun()

    st.markdown("#### 📜 Historique du jour")
    rows = ws_notes.get_all_values()
    if len(rows) > 1:
        for n in reversed(rows[1:]):
            if n[0] == datetime.now().strftime("%d/%m/%Y"):
                st.markdown(f"**{n[2]}** : {n[3]} <span style='color:gray; font-size:0.8rem;'>(🕒 {n[1]})</span>", unsafe_allow_html=True)

# --- PAGE BUDGET ---
elif page == "💰 Budget":
    st.markdown("### 🪙 Gestion Budgétaire")
    
    with st.expander("➕ Ajouter une opération", expanded=False):
        c1, c2, c3 = st.columns(3)
        cat = c1.selectbox("Type", ["Revenu", "Charge Fixe", "Dépense"])
        lab = c2.text_input("Libellé")
        val = c3.number_input("Montant €", step=0.01)
        if st.button("Ajouter à la base"):
            ws_fin.append_row([datetime.now().strftime("%B"), str(datetime.now().year), cat, lab, val])
            st.rerun()

    data = ws_fin.get_all_records()
    if data:
        df = pd.DataFrame(data)
        st.write("#### 📜 Historique (Modifiable)")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        col_s1, col_s2 = st.columns(2)
        if col_s1.button("💾 Sauvegarder les modifications"):
            ws_fin.clear()
            ws_fin.append_row(["Mois", "Année", "Catégorie", "Libellé", "Montant €"])
            ws_fin.append_rows(edited_df.values.tolist())
            st.success("Enregistré !")

        pdf_data = create_pdf(df, "Février", "2026")
        col_s2.download_button("📥 Rapport PDF", pdf_data, "budget.pdf", "application/pdf")

# --- PAGE CONFIG ---
elif page == "⚙️ Config":
    st.markdown("### ⚙️ Paramètres")
    new_name = st.text_input("Prénom :", user_name)
    if st.button("Mettre à jour"):
        ws_conf.update_acell('A2', new_name)
        st.rerun()
