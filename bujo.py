import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ==========================================
# 1. CONNEXION GOOGLE SHEETS
# ==========================================
def init_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    try:
        # Utilisation de TES clés spécifiques configurées dans tes Secrets
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
    try:
        # CORRECTION : On utilise "Note" sans 's' comme sur ton image
        ws_notes = sh.worksheet("Note")
        ws_fin = sh.worksheet("Finances")
        ws_conf = sh.worksheet("Config")
    except Exception as e:
        st.error(f"Erreur : Un onglet est introuvable. Vérifie l'orthographe : {e}")
        st.stop()
else:
    st.stop()

# ==========================================
# 2. DESIGN ENCHANTÉ
# ==========================================
st.set_page_config(page_title="Mon BuJo Enchanté", layout="wide")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
<style>
    .stApp { background: linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%); background-attachment: fixed; }
    .header-banner { background-color: white; padding: 15px; border-radius: 50px; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .header-banner h1 { color: #1a2e26 !important; margin: 0; font-family: 'Playfair Display', serif; font-size: 32px; }
    .bujo-card { background-color: rgba(255, 255, 255, 0.94); padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 20px;}
    .handwritten-note { background-color: #fff9c4; font-family: 'Caveat', cursive; font-size: 26px; padding: 25px; border-radius: 5px; border-left: 6px solid #fbc02d; color: #5d4037 !important; box-shadow: 3px 3px 10px rgba(0,0,0,0.1); }
    [data-testid="stSidebar"] { background-color: #0e1a15 !important; border-right: 3px solid #d4a373; }
    .stButton>button { background-color: #7fb79e !important; color: #1a2e26 !important; border-radius: 12px; font-weight: bold; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. NAVIGATION
# ==========================================
with st.sidebar:
    user_name = ws_conf.acell('A2').value or "MeyLune"
    st.markdown(f"# 🌿 {user_name}")
    page = st.radio("Navigation", ["📅 Daily Log", "💰 Finances", "⚙️ Config"])
    st.write("---")
    st.markdown('<div style="color:#d4a373; text-align:center; border:1px dashed #d4a373; padding:10px; border-radius:10px;">✨ Stickers OK<br>🍃 🌸 🦋 🥥</div>', unsafe_allow_html=True)

st.markdown(f'<div class="header-banner"><h1>Journal de {user_name}</h1></div>', unsafe_allow_html=True)

# --- PAGE DAILY LOG ---
if page == "📅 Daily Log":
    st.markdown('<div class="bujo-card">', unsafe_allow_html=True)
    st.subheader(f"Aujourd'hui, le {datetime.now().strftime('%d %B %Y')}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        txt = st.text_input("Nouvelle pensée...", placeholder="Écris ici...", key="in_note")
    with col2:
        sym = st.selectbox("Type", ["🍃 Note", "📌 Tâche", "✨ Événement", "♡"])
    
    if st.button("Enregistrer dans le journal"):
        if txt:
            ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), sym, txt])
            st.rerun()

    st.write("---")
    rows = ws_notes.get_all_values()
    if len(rows) > 1:
        for n in reversed(rows[1:]):
            st.markdown(f"**{n[2]}** {n[3]}  *(🕒 {n[1]})*")
    st.markdown('</div>', unsafe_allow_html=True)

    # Zone Note Libre (Post-it)
    st.markdown('<div class="handwritten-note">🖋️ Note libre :<br>C\'est ici que tu peux écrire tes pensées plus longues qui s\'affichent avec ton écriture cursive préférée.</div>', unsafe_allow_html=True)

# --- PAGE FINANCES ---
elif page == "💰 Finances":
    st.markdown('<div class="bujo-card">', unsafe_allow_html=True)
    st.title("💹 Gestion Budget")
    
    c_type = st.selectbox("Type d'opération", ["Revenu", "Charge Fixe", "Variable"])
    col_l, col_m = st.columns(2)
    f_label = col_l.text_input("Libellé (ex: Salaire, Loyer...)")
    f_amount = col_m.number_input("Montant €", min_value=0.0)
    
    if st.button("Ajouter au budget"):
        ws_fin.append_row([datetime.now().strftime("%B"), c_type, f_label, f_amount])
        st.rerun()
    
    st.write("---")
    # Calcul des totaux
    data = ws_fin.get_all_records()
    if data:
        total_rev = sum(float(str(i['Montant €']).replace(',','.')) for i in data if i['Catégorie'] == 'Revenu')
        total_dep = sum(float(str(i['Montant €']).replace(',','.')) for i in data if i['Catégorie'] != 'Revenu')
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenus", f"{total_rev} €")
        c2.metric("Dépenses", f"{total_dep} €", delta=f"-{total_dep}", delta_color="inverse")
        c3.metric("Reste à vivre", f"{total_rev - total_dep} €")
    st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE CONFIG ---
elif page == "⚙️ Config":
    st.markdown('<div class="bujo-card">', unsafe_allow_html=True)
    st.title("⚙️ Paramètres")
    new_name = st.text_input("Changer mon prénom :", user_name)
    if st.button("Enregistrer"):
        ws_conf.update_acell('A2', new_name)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
