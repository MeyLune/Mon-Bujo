import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

# --- 1. CONNEXION ---
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
        return gspread.authorize(creds).open("db_bujo")
    except Exception as e:
        return None

sh = init_connection()

# --- 2. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3 { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }
    .bujo-block { background: white; padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .p-header { background-color: #f06292; color: white; padding: 8px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    .p-cell { background-color: white; min-height: 150px; padding: 10px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; margin-bottom: 15px; }
    .event-tag { background: #fff1f3; border-left: 3px solid #f06292; padding: 5px; margin-bottom: 5px; border-radius: 4px; font-size: 0.8rem; color: #ad1457; }
</style>
""", unsafe_allow_html=True)

if not sh:
    st.error("Lien Google Sheets rompu.")
    st.stop()

# --- 3. FONCTION D'ACCÈS CORRIGÉE ---
def check_consultant_access(unique_key):
    if "consultant_auth" not in st.session_state:
        st.session_state.consultant_auth = False
    
    if not st.session_state.consultant_auth:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        st.warning("🔒 Section protégée")
        # L'ajout de key=unique_key règle l'erreur DuplicateElementId
        pwd = st.text_input("Entrez le Code Consultant :", type="password", key=unique_key)
        if pwd == "MEY2026":
            st.session_state.consultant_auth = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# --- 4. NAVIGATION ---
st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
tab_j, tab_s, tab_b = st.tabs(["🔒 JOURNAL INTIME", "📅 SEMAINE", "💰 BUDGET"])

with tab_j:
    st.markdown("### ✍️ Mon Journal Personnel")
    st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
    st.write("Bienvenue dans ton espace privé. Ici, pas besoin de code, c'est ton jardin secret.")
    humeur = st.select_slider("Humeur", options=["😢", "😐", "🙂", "✨"])
    st.text_area("Note intime...")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_s:
    # On passe une clé unique "auth_semaine"
    if check_consultant_access("auth_semaine"):
        st.subheader("Planning de la Semaine")
        
        # Navigation
        if 'w_off' not in st.session_state: st.session_state.w_off = 0
        c1, c2, c3 = st.columns([1, 2, 1])
        if c1.button("⬅️ Précédent"): st.session_state.w_off -= 1
        if c3.button("Suivant ➡️"): st.session_state.w_off += 1
        
        start_d = (datetime.now() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
        c2.markdown(f"<p style='text-align:center;'>Semaine du {start_d.strftime('%d/%m')}</p>", unsafe_allow_html=True)

        # Affichage iPad : 2 colonnes par ligne pour plus de lisibilité
        ws_notes = sh.worksheet("Note")
        data = ws_notes.get_all_values()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            
            for i in range(0, 7, 2): # On avance par 2 pour créer des paires
                row_cols = st.columns(2)
                for j in range(2):
                    if (i + j) < 7:
                        curr = start_d + timedelta(days=i+j)
                        d_str = curr.strftime("%d/%m/%Y")
                        with row_cols[j]:
                            st.markdown(f'<div class="p-header">{days[i+j]} {curr.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                            evs = ""
                            day_data = df[df.iloc[:, 0] == d_str]
                            for _, r in day_data.iterrows():
                                evs += f'<div class="event-tag"><b>{r.iloc[1]}</b> - {r.iloc[3]}</div>'
                            st.markdown(f'<div class="p-cell">{evs}</div>', unsafe_allow_html=True)

with tab_b:
    # On passe une clé unique "auth_budget"
    if check_consultant_access("auth_budget"):
        st.subheader("💰 Mon Budget")
        ws_fin = sh.worksheet("Finances")
        # ... reste du code budget
        st.info("Le tableau de bord financier s'affiche ici.")
