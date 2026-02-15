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
    except:
        return None

sh = init_connection()

# --- 2. DESIGN & CSS (Restauré et Amélioré) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3 { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }
    
    /* Style Post-it pour le Pencil */
    .post-it {
        background: #fff9c4;
        padding: 20px;
        border-left: 5px solid #fbc02d;
        font-family: 'Indie Flower', cursive;
        font-size: 1.2rem;
        color: #5d4037;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
        border-radius: 2px;
        min-height: 200px;
    }
    
    .bujo-block { background: white; padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    .p-header { background-color: #f06292; color: white; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    .p-cell { background-color: white; min-height: 150px; padding: 10px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; margin-bottom: 20px; }
    .event-tag { background: #fff1f3; border-left: 4px solid #f06292; padding: 5px; margin-bottom: 5px; border-radius: 4px; font-size: 0.8rem; color: #ad1457; }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIQUE D'ACCÈS ---
def check_consultant_access(tab_name):
    if "consultant_auth" not in st.session_state: st.session_state.consultant_auth = False
    if not st.session_state.consultant_auth:
        st.markdown(f'<div class="bujo-block"><h3>🔒 Section protégée</h3>', unsafe_allow_html=True)
        pwd = st.text_input(f"Code pour {tab_name} :", type="password", key=f"pwd_{tab_name}")
        if pwd == "MEY2026":
            st.session_state.consultant_auth = True
            st.rerun()
        return False
    return True

# --- 4. NAVIGATION ---
st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
tab_j, tab_s, tab_b = st.tabs(["✍️ MON JOURNAL", "📅 SEMAINE", "💰 BUDGET"])

# --- PAGE JOURNAL ---
with tab_j:
    st.markdown(f"### ✨ Aujourd'hui, le {datetime.now().strftime('%d %B %Y')}")
    
    sub_tab_day, sub_tab_track = st.tabs(["📖 Ma Journée", "📊 Trackers"])
    
    with sub_tab_day:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown('<h3>📝 Note Libre (Style Post-it)</h3>', unsafe_allow_html=True)
            st.markdown('<div class="post-it">Écris ici tes pensées ou utilise ton Pencil...</div>', unsafe_allow_html=True)
            note_libre = st.text_area("", placeholder="Note tes inspirations...", label_visibility="collapsed", key="note_pencil")
            
        with col2:
            st.markdown('<div class="bujo-block"><h3>😊 Humeur & Intentions</h3>', unsafe_allow_html=True)
            humeur = st.select_slider("Mon énergie", options=["🔋 Vide", "😐", "🙂", "✨", "🔥"], value="🙂")
            intention = st.text_input("Mon intention du jour :")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="bujo-block"><h3>📌 Ajout Rapide</h3>', unsafe_allow_html=True)
            c1, c2 = st.columns([2, 1])
            n_txt = c1.text_input("Quoi ?", key="quick_q")
            n_typ = c2.selectbox("Type", ["Note", "RDV", "Tâche"], key="quick_t")
            if st.button("Ancrer au Journal", use_container_width=True):
                if sh:
                    sh.worksheet("Note").append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), n_typ, n_txt])
                    st.success("C'est noté !")
            st.markdown('</div>', unsafe_allow_html=True)

    with sub_tab_track:
        st.markdown("### 📈 Mes Suivis Personnalisés")
        
        # Initialisation des trackers dans la session
        if 'my_trackers' not in st.session_state:
            st.session_state.my_trackers = ["💧 Eau", "🧘 Méditation", "🍎 Fruits", "🚶 10k Pas"]
        
        # Affichage des trackers
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        cols_t = st.columns(len(st.session_state.my_trackers))
        for idx, tracker in enumerate(st.session_state.my_trackers):
            with cols_t[idx]:
                st.checkbox(tracker, key=f"check_{tracker}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Ajouter/Modifier des trackers
        with st.expander("⚙️ Personnaliser mes trackers"):
            new_t = st.text_input("Nom du nouveau tracker (ex: 📖 Lecture)")
            if st.button("Ajouter"):
                st.session_state.my_trackers.append(new_t)
                st.rerun()
            if st.button("Réinitialiser"):
                st.session_state.my_trackers = ["💧 Eau", "🧘 Méditation"]
                st.rerun()

# --- PAGES SEMAINE & BUDGET (Protégées) ---
with tab_s:
    if check_consultant_access("Semaine"):
        st.info("Grille hebdomadaire optimisée en 2 colonnes (iPad ready).")
        # [Ici le code de la grille que nous avons fait précédemment]

with tab_b:
    if check_consultant_access("Budget"):
        st.info("Gestionnaire financier sécurisé.")
        # [Ici le code du budget que nous avons fait précédemment]
