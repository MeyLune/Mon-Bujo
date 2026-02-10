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
ws_notes = sh.worksheet("Note")
ws_fin = sh.worksheet("Finances")
ws_conf = sh.worksheet("Config")

# ==========================================
# 2. DESIGN & STYLE
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
    .bujo-card { background-color: rgba(255, 255, 255, 0.15); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.2); margin-bottom: 20px; color: white; }
    .handwritten-note { background-color: #fff9c4; font-family: 'Caveat', cursive; font-size: 24px; padding: 20px; border-radius: 5px; border-left: 6px solid #fbc02d; color: #5d4037 !important; box-shadow: 3px 3px 10px rgba(0,0,0,0.2); }
    [data-testid="stSidebar"] { background-color: #0e1a15 !important; border-right: 2px solid #d4a373; }
    .stat-card { background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; text-align: center; color: #1a2e26; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
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
    st.markdown('<div style="color:#d4a373; text-align:center;">✨ Espace Stickers<br>🍃 🌸 🦋 🥥</div>', unsafe_allow_html=True)

st.markdown(f'<div class="header-banner"><h1>Journal de {user_name}</h1></div>', unsafe_allow_html=True)

# --- PAGE DAILY LOG ---
if page == "📅 Daily Log":
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
            st.markdown(f"**{n[2]}** {n[3]}  *(🕒 {n[1]})*")

    st.markdown("### 🖋️ Note à la main ici")
    note_libre = st.text_area("Tape ici...", label_visibility="collapsed")
    st.markdown(f'<div class="handwritten-note">{note_libre}</div>', unsafe_allow_html=True)

# --- PAGE FINANCES ---
elif page == "💰 Finances":
    st.title("💹 Gestion Budgétaire")
    
    # 1. SÉLECTION PÉRIODE
    mois_liste = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    col_m, col_a = st.columns(2)
    sel_mois = col_m.selectbox("Choisir le mois", mois_liste, index=datetime.now().month - 1)
    sel_annee = col_a.selectbox("Choisir l'année", [2025, 2026, 2027], index=1)

    # 2. AJOUT OPÉRATION
    with st.expander("➕ Ajouter une opération", expanded=False):
        # Ordre demandé : Revenu, Charge Fixe, Dépense
        cat = st.selectbox("Catégorie", ["Revenu", "Charge Fixe", "Dépense"])
        col_l, col_v = st.columns(2)
        label = col_l.text_input("Libellé")
        valeur = col_v.number_input("Montant €", min_value=0.0)
        
        if st.button("Ajouter au mois de " + sel_mois):
            # Format dans Sheets : Mois | Année | Catégorie | Libellé | Montant
            ws_fin.append_row([sel_mois, str(sel_annee), cat, label, valeur])
            st.success("Enregistré !")
            st.rerun()

    st.write("---")

    # 3. RÉCUPÉRATION DES DONNÉES DU MOIS
    all_fin = ws_fin.get_all_records()
    df = pd.DataFrame(all_fin)
    
    if not df.empty:
        # Filtrage
        df_mois = df[(df['Mois'] == sel_mois) & (df['Année'].astype(str) == str(sel_annee))]
        
        # Calculs
        def to_float(x): return float(str(x).replace(',', '.')) if x else 0.0
        
        rev = sum(df_mois[df_mois['Catégorie'] == 'Revenu']['Montant €'].apply(to_float))
        fix = sum(df_mois[df_mois['Catégorie'] == 'Charge Fixe']['Montant €'].apply(to_float))
        dep = sum(df_mois[df_mois['Catégorie'] == 'Dépense']['Montant €'].apply(to_float))
        total_dep = fix + dep
        reste = rev - total_dep

        # 4. CARTES VISUELLES (RÉSUMÉ)
        st.markdown(f"### 📊 Résumé de {sel_mois} {sel_annee}")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="stat-card"><b>💰 Revenus</b><br><span style="font-size:20px; color:green">+{rev} €</span></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-card"><b>🏠 Fixe</b><br><span style="font-size:20px; color:orange">-{fix} €</span></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="stat-card"><b>🛒 Dépenses</b><br><span style="font-size:20px; color:red">-{dep} €</span></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="stat-card"><b>✨ Reste</b><br><span style="font-size:20px; color:blue">{reste} €</span></div>', unsafe_allow_html=True)

        # 5. HISTORIQUE DU MOIS
        st.write("")
        st.markdown(f"#### 📜 Historique détaillé")
        if not df_mois.empty:
            st.dataframe(df_mois[['Catégorie', 'Libellé', 'Montant €']], use_container_width=True)
            
            # 6. GÉNÉRATION PDF
            if st.button("📥 Générer le rapport PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt=f"Rapport Budget - {sel_mois} {sel_annee}", ln=True, align='C')
                pdf.set_font("Arial", size=12)
                pdf.ln(10)
                pdf.cell(200, 10, txt=f"Total Revenus : {rev} EUR", ln=True)
                pdf.cell(200, 10, txt=f"Total Charges Fixes : {fix} EUR", ln=True)
                pdf.cell(200, 10, txt=f"Total Depenses : {dep} EUR", ln=True)
                pdf.cell(200, 10, txt=f"Reste a vivre : {reste} EUR", ln=True)
                pdf.ln(5)
                pdf.cell(200, 10, txt="Details des operations :", ln=True)
                for index, row in df_mois.iterrows():
                    pdf.cell(200, 8, txt=f"- {row['Catégorie']} : {row['Libellé']} ({row['Montant €']} EUR)", ln=True)
                
                pdf_output = pdf.output(dest='S').encode('latin-1')
                st.download_button(label="Clicker ici pour télécharger", data=pdf_output, file_name=f"Budget_{sel_mois}.pdf", mime="application/pdf")
        else:
            st.info("Aucune donnée pour ce mois.")

# --- PAGE CONFIG ---
elif page == "⚙️ Config":
    st.title("⚙️ Paramètres")
    new_name = st.text_input("Ton prénom :", user_name)
    if st.button("Sauvegarder"):
        ws_conf.update_acell('A2', new_name)
        st.rerun()
