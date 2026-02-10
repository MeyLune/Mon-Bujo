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
# 2. DESIGN & STYLE (iPad & Vert d'eau)
# ==========================================
st.set_page_config(page_title="Mon BuJo Enchanté", layout="wide")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
<style>
    /* Fond principal */
    .stApp {
        background: linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%);
        background-image: url('https://www.transparenttextures.com/patterns/leaf.png'), linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%);
        background-attachment: fixed;
    }

    /* Titres et Bannières */
    .header-banner { background-color: white; padding: 15px; border-radius: 50px; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .header-banner h1 { color: #1a2e26 !important; margin: 0; font-family: 'Playfair Display', serif; }

    /* --- TRANSFORMATION VERT D'EAU --- */
    div[data-baseweb="input"], div[data-baseweb="select"], .stTextArea textarea {
        background-color: #e0f2f1 !important;
        color: #1a2e26 !important;
        border-radius: 10px !important;
        border: 1px solid #80cbc4 !important;
    }
    
    input { color: #1a2e26 !important; }

    /* --- CARTES DE STATISTIQUES --- */
    .stat-card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        border-bottom: 5px solid #d4a373;
    }
    .stat-card b { color: #1a2e26 !important; font-size: 16px; display: block; margin-bottom: 5px; }
    .stat-value { font-size: 22px; font-weight: bold; }

    /* Note manuscrite */
    .handwritten-note { background-color: #fff9c4; font-family: 'Caveat', cursive; font-size: 26px; padding: 20px; border-radius: 5px; border-left: 6px solid #fbc02d; color: #5d4037 !important; }

    /* Sidebar et Boutons */
    [data-testid="stSidebar"] { background-color: #0e1a15 !important; border-right: 2px solid #d4a373; }
    .stButton>button {
        background-color: #80cbc4 !important;
        color: #1a2e26 !important;
        border-radius: 10px;
        font-weight: bold;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. NAVIGATION
# ==========================================
with st.sidebar:
    try:
        user_name = ws_conf.acell('A2').value or "MeyLune"
    except:
        user_name = "MeyLune"
    st.markdown(f"## 🌿 {user_name}")
    page = st.radio("Navigation", ["📅 Daily Log", "💰 Finances", "⚙️ Config"])
    st.write("---")
    st.info(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

st.markdown(f'<div class="header-banner"><h1>Journal de {user_name}</h1></div>', unsafe_allow_html=True)

# --- PAGE DAILY LOG ---
if page == "📅 Daily Log":
    st.subheader(f"Aujourd'hui, le {datetime.now().strftime('%d %B %Y')}")
    col1, col2 = st.columns([3, 1])
    with col1:
        txt = st.text_input("Nouvelle pensée...", key="in_note", placeholder="Quoi de neuf ?")
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

    st.markdown("### 🖋️ Note à la main ici")
    note_libre = st.text_area("Écris ici...", label_visibility="collapsed")
    st.markdown(f'<div class="handwritten-note">{note_libre}</div>', unsafe_allow_html=True)

# --- PAGE FINANCES ---
elif page == "💰 Finances":
    st.title("💹 Gestion Budgétaire")
    
    mois_liste = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    c1, c2 = st.columns(2)
    sel_mois = c1.selectbox("Mois", mois_liste, index=datetime.now().month - 1)
    sel_annee = c2.selectbox("Année", [2025, 2026, 2027], index=1)

    with st.expander("➕ Ajouter une opération", expanded=False):
        cat = st.selectbox("Catégorie", ["Revenu", "Charge Fixe", "Dépense"])
        label = st.text_input("Libellé")
        valeur = st.number_input("Montant €", min_value=0.0, step=1.0)
        
        if st.button(f"Ajouter à {sel_mois}"):
            ws_fin.append_row([sel_mois, str(sel_annee), cat, label, valeur])
            st.success("Opération enregistrée !")
            st.rerun()

    # --- PARTIE HISTORIQUE INTERACTIF ---
    data = ws_fin.get_all_records()
    if data:
        df_full = pd.DataFrame(data)
        mask = (df_full['Mois'] == sel_mois) & (df_full['Année'].astype(str) == str(sel_annee))
        df_mois = df_full[mask].copy()

        if not df_mois.empty:
            st.write("---")
            st.write("### 📜 Historique (Modifier ou Supprimer)")
            st.info("💡 Modifie une case et clique sur 'Enregistrer'. Coche 'Suppr' pour retirer.")

            df_mois.insert(0, "Suppr", False)

            edited_df = st.data_editor(
                df_mois,
                column_config={
                    "Suppr": st.column_config.CheckboxColumn("Suppr"),
                    "Montant €": st.column_config.NumberColumn("Montant €", format="%.2f €"),
                    "Catégorie": st.column_config.SelectboxColumn("Catégorie", options=["Revenu", "Charge Fixe", "Dépense"])
                },
                disabled=["Mois", "Année"],
                hide_index=True,
                use_container_width=True
            )

            c_save, c_del = st.columns(2)
            
            if c_save.button("💾 Enregistrer les modifications"):
                updated_mois = edited_df[edited_df["Suppr"] == False].drop(columns=["Suppr"])
                final_df = pd.concat([df_full[~mask], updated_mois], ignore_index=True)
                ws_fin.clear()
                ws_fin.update([final_df.columns.values.tolist()] + final_df.values.tolist())
                st.rerun()

            if c_del.button("🗑️ Supprimer les lignes cochées"):
                remaining = edited_df[edited_df["Suppr"] == False].drop(columns=["Suppr"])
                final_df = pd.concat([df_full[~mask], remaining], ignore_index=True)
                ws_fin.clear()
                ws_fin.update([final_df.columns.values.tolist()] + final_df.values.tolist())
                st.rerun()

            # --- RÉSUMÉ VISUEL ---
            def clean_val(x): return float(str(x).replace(',', '.'))
            rev = df_mois[df_mois['Catégorie'] == 'Revenu']['Montant €'].apply(clean_val).sum()
            fix = df_mois[df_mois['Catégorie'] == 'Charge Fixe']['Montant €'].apply(clean_val).sum()
            dep = df_mois[df_mois['Catégorie'] == 'Dépense']['Montant €'].apply(clean_val).sum()
            reste = rev - fix - dep

            st.write("---")
            cols = st.columns(4)
            cols[0].markdown(f'<div class="stat-card"><b>🟢 Revenu</b><div class="stat-value" style="color:#2e7d32">{rev} €</div></div>', unsafe_allow_html=True)
            cols[1].markdown(f'<div class="stat-card"><b>🟠 Fixe</b><div class="stat-value" style="color:#e65100">{fix} €</div></div>', unsafe_allow_html=True)
            cols[2].markdown(f'<div class="stat-card"><b>🔴 Dépense</b><div class="stat-value" style="color:#c62828">{dep} €</div></div>', unsafe_allow_html=True)
            cols[3].markdown(f'<div class="stat-card" style="background:#e1f5fe"><b>💎 Reste</b><div class="stat-value" style="color:#0277bd">{reste} €</div></div>', unsafe_allow_html=True)

            # Export PDF
            if st.button("📥 Rapport PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, f"Rapport Budget - {sel_mois} {sel_annee}", ln=True, align='C')
                pdf_output = pdf.output(dest='S').encode('latin-1')
                st.download_button("Télécharger", data=pdf_output, file_name=f"Budget_{sel_mois}.pdf")
        else:
            st.info("Aucune donnée pour ce mois.")

# --- PAGE CONFIG ---
elif page == "⚙️ Config":
    st.title("⚙️ Paramètres")
    new_name = st.text_input("Changer mon prénom :", user_name)
    if st.button("Sauvegarder"):
        ws_conf.update_acell('A2', new_name)
        st.rerun()
