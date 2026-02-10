import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
from fpdf import FPDF

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
# 2. DESIGN & STYLE (iPad Optimized)
# ==========================================
st.set_page_config(page_title="Mon BuJo Enchanté", layout="wide")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
<style>
    .stApp {
        background: linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%);
        background-image: url('https://www.transparenttextures.com/patterns/leaf.png'), linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%);
        background-attachment: fixed;
    }
    .header-banner { background-color: white; padding: 15px; border-radius: 50px; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .header-banner h1 { color: #1a2e26 !important; margin: 0; font-family: 'Playfair Display', serif; }
    .bujo-card { background-color: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 15px; color: #1a2e26; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .handwritten-note { background-color: #fff9c4; font-family: 'Caveat', cursive; font-size: 26px; padding: 20px; border-radius: 5px; border-left: 6px solid #fbc02d; color: #5d4037 !important; }
    [data-testid="stSidebar"] { background-color: #0e1a15 !important; border-right: 2px solid #d4a373; }
    .stat-card { background: white; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #d4a373; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. NAVIGATION
# ==========================================
with st.sidebar:
    user_name = ws_conf.acell('A2').value or "MeyLune"
    st.markdown(f"## 🌿 {user_name}")
    page = st.radio("Navigation", ["📅 Daily Log", "💰 Finances", "⚙️ Config"])
    st.write("---")
    st.info(f"📅 {datetime.now().strftime('%d %B %Y')}")

st.markdown(f'<div class="header-banner"><h1>Journal de {user_name}</h1></div>', unsafe_allow_html=True)

# --- PAGE DAILY LOG ---
if page == "📅 Daily Log":
    st.markdown('<div class="bujo-card">', unsafe_allow_html=True)
    st.subheader(f"Aujourd'hui, le {datetime.now().strftime('%d %B %Y')}")
    col1, col2 = st.columns([3, 1])
    with col1:
        txt = st.text_input("Nouvelle pensée...", key="in_note")
    with col2:
        sym = st.selectbox("Style", ["🍃 Note", "📌 Tâche", "✨ Événement", "♡"])
    
    if st.button("Enregistrer"):
        if txt:
            ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), sym, txt])
            st.rerun()

    st.write("---")
    rows = ws_notes.get_all_values()
    if len(rows) > 1:
        for n in reversed(rows[1:]):
            st.write(f"**{n[2]}** {n[3]}  *(🕒 {n[1]})*")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 🖋️ Note à la main ici")
    note_libre = st.text_area("Libre court à ton imagination...", label_visibility="collapsed")
    st.markdown(f'<div class="handwritten-note">{note_libre}</div>', unsafe_allow_html=True)

# --- PAGE FINANCES ---
elif page == "💰 Finances":
    st.title("💹 Gestion Budgétaire")
    
    # Sélection Période
    mois_liste = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    c1, c2 = st.columns(2)
    sel_mois = c1.selectbox("Choisir le mois", mois_liste, index=datetime.now().month - 1)
    sel_annee = c2.selectbox("Choisir l'année", [2025, 2026, 2027], index=1)

    # Ajout Opération
    with st.expander("➕ Ajouter une opération", expanded=False):
        cat = st.selectbox("Catégorie", ["Revenu", "Charge Fixe", "Dépense"])
        col_l, col_v = st.columns(2)
        label = col_l.text_input("Libellé (ex: Loyer, Salaire...)")
        valeur = col_v.number_input("Montant €", min_value=0.0)
        
        if st.button(f"Ajouter à {sel_mois} {sel_annee}"):
            ws_fin.append_row([sel_mois, str(sel_annee), cat, label, valeur])
            st.success("Opération ajoutée !")
            st.rerun()

    # Lecture des données
    data = ws_fin.get_all_records()
    if data:
        df = pd.DataFrame(data)
        # On s'assure que les colonnes indispensables existent pour éviter le plantage
        if 'Mois' in df.columns and 'Année' in df.columns:
            df_mois = df[(df['Mois'] == sel_mois) & (df['Année'].astype(str) == str(sel_annee))]
            
            if not df_mois.empty:
                # Calculs
                def clean_val(x): return float(str(x).replace(',', '.'))
                rev = df_mois[df_mois['Catégorie'] == 'Revenu']['Montant €'].apply(clean_val).sum()
                fix = df_mois[df_mois['Catégorie'] == 'Charge Fixe']['Montant €'].apply(clean_val).sum()
                dep = df_mois[df_mois['Catégorie'] == 'Dépense']['Montant €'].apply(clean_val).sum()
                reste = rev - fix - dep

                # Résumé Visuel
                st.write("---")
                cols = st.columns(4)
                cols[0].markdown(f'<div class="stat-card">🟢 <b>Revenu</b><br>{rev} €</div>', unsafe_allow_html=True)
                cols[1].markdown(f'<div class="stat-card">🟠 <b>Fixe</b><br>{fix} €</div>', unsafe_allow_html=True)
                cols[2].markdown(f'<div class="stat-card">🔴 <b>Dépense</b><br>{dep} €</div>', unsafe_allow_html=True)
                cols[3].markdown(f'<div class="stat-card" style="background:#e3f2fd">💎 <b>Reste</b><br>{reste} €</div>', unsafe_allow_html=True)

                # Historique
                st.write("### 📜 Historique")
                st.dataframe(df_mois[['Catégorie', 'Libellé', 'Montant €']], use_container_width=True)

                # PDF
                if st.button("📥 Télécharger le rapport PDF"):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(200, 10, f"Rapport Budget - {sel_mois} {sel_annee}", ln=True, align='C')
                    pdf.ln(10)
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, f"Revenu total : {rev} EUR", ln=True)
                    pdf.cell(200, 10, f"Dépenses : {fix+dep} EUR", ln=True)
                    pdf.cell(200, 10, f"Reste : {reste} EUR", ln=True)
                    pdf_output = pdf.output(dest='S').encode('latin-1')
                    st.download_button("Télécharger le fichier", data=pdf_output, file_name=f"Budget_{sel_mois}.pdf")
            else:
                st.info(f"Aucune donnée enregistrée pour {sel_mois} {sel_annee}.")
        else:
            st.error("Ton Google Sheets n'a pas les bonnes colonnes. Ajoute 'Mois' et 'Année' en ligne 1.")

# --- PAGE CONFIG ---
elif page == "⚙️ Config":
    st.title("⚙️ Paramètres")
    new_name = st.text_input("Changer mon prénom :", user_name)
    if st.button("Sauvegarder"):
        ws_conf.update_acell('A2', new_name)
        st.rerun()
