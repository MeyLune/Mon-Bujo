import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ==========================================
# 1. CONNEXION GOOGLE SHEETS
# ==========================================
def init_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    # On utilise les secrets configurés dans Streamlit Cloud
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open("db_bujo")

try:
    sh = init_connection()
    ws_notes = sh.worksheet("Notes")
    ws_fin = sh.worksheet("Finances")
    ws_conf = sh.worksheet("Config")
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

# ==========================================
# 2. DESIGN ENCHANTÉ (VOTRE STYLE)
# ==========================================
st.set_page_config(page_title="Mon BuJo Enchanté", layout="wide")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
<style>
    .stApp { background: linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%); background-attachment: fixed; }
    .header-banner { background-color: white; padding: 15px; border-radius: 50px; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .header-banner h1 { color: #1a2e26 !important; margin: 0; font-family: 'Playfair Display', serif; font-size: 32px; }
    .bujo-card { background-color: rgba(255, 255, 255, 0.94); padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
    .handwritten-note { background-color: #fff9c4; font-family: 'Caveat', cursive; font-size: 26px; padding: 25px; border-radius: 5px; border-left: 6px solid #fbc02d; color: #5d4037 !important; margin-top: 20px; }
    [data-testid="stSidebar"] { background-color: #0e1a15 !important; border-right: 3px solid #d4a373; }
    .sticker-zone { text-align: center; border: 2px dashed #d4a373; padding: 10px; border-radius: 15px; margin-top: 20px; color: #d4a373; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LOGIQUE NAVIGATION
# ==========================================
with st.sidebar:
    # On récupère le nom de l'utilisateur depuis Config (Cellule A1)
    user_name = ws_conf.acell('A1').value or "MeyLune"
    st.markdown(f"# 🌿 {user_name}")
    page = st.radio("Navigation", ["📅 Daily Log", "💰 Finances", "⚙️ Config"])
    st.markdown('<div class="sticker-zone">✨ Espace Stickers<br>🍃 🌸 🦋 🥥</div>', unsafe_allow_html=True)

st.markdown(f'<div class="header-banner"><h1>Journal de {user_name}</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="bujo-card">', unsafe_allow_html=True)

# --- PAGE DAILY LOG ---
if page == "📅 Daily Log":
    st.subheader(f"Aujourd'hui, le {datetime.now().strftime('%d %B')}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        txt = st.text_input("Note ou tâche...", key="new_note")
    with col2:
        sym = st.selectbox("Type", ["🍃 Note", "📌 Tâche", "✨ Événement", "♡"])
    
    if st.button("Enregistrer"):
        if txt:
            # Sauvegarde réelle sur Google Sheets
            ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), sym, txt])
            st.success("Note sauvegardée !")
            st.rerun()

    st.write("---")
    # Affichage des 10 dernières notes depuis Sheets
    all_notes = ws_notes.get_all_values()
    if len(all_notes) > 0:
        for n in reversed(all_notes[-10:]):
            st.markdown(f"**{n[2]}** {n[3]}  *(🕒 {n[1]})*")

# --- PAGE FINANCES ---
elif page == "💰 Finances":
    st.title("💹 Gestion Budget")
    cat = st.selectbox("Catégorie", ["Revenu", "Charge Fixe", "Variable"])
    col_n, col_m = st.columns(2)
    nom_f = col_n.text_input("Libellé")
    mnt_f = col_m.number_input("Montant €", min_value=0.0)
    
    if st.button("Enregistrer l'opération"):
        ws_fin.append_row([datetime.now().strftime("%B"), cat, nom_f, mnt_f])
        st.success("Donnée financière enregistrée !")
        st.rerun()
    
    # Calcul rapide
    data_fin = ws_fin.get_all_records()
    if data_fin:
        rev = sum(float(item['Montant €']) for item in data_fin if item['Catégorie'] == 'Revenu')
        dep = sum(float(item['Montant €']) for item in data_fin if item['Catégorie'] != 'Revenu')
        st.metric("Reste à vivre", f"{rev - dep} €", delta=f"-{dep} €")

# --- PAGE CONFIG ---
elif page == "⚙️ Config":
    st.title("⚙️ Paramètres")
    new_name = st.text_input("Ton Prénom", user_name)
    if st.button("Mettre à jour"):
        ws_conf.update_acell('A1', new_name)
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
