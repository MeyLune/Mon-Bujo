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

# --- 2. DESIGN (FORÇAGE DU BLANC SUR LES BOUTONS) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3, p, label { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }

    /* Forçage des entrées en blanc */
    div[data-baseweb="input"], div[data-baseweb="textarea"], select {
        background-color: white !important;
        border: 2px solid #c8e6c9 !important;
        border-radius: 12px !important;
    }
    input, textarea { color: #1b5e20 !important; -webkit-text-fill-color: #1b5e20 !important; }

    /* RÉPARATION DES BOUTONS (Texte Blanc Visible) */
    .stButton>button {
        background-color: #1b5e20 !important;
        border-radius: 25px !important;
        border: none !important;
        padding: 10px 20px !important;
    }
    .stButton>button p {
        color: white !important; /* Force la couleur du texte à l'intérieur du bouton */
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }

    /* Styles Bujo */
    .post-it {
        background: #fff9c4; padding: 25px; border-left: 6px solid #fbc02d;
        font-family: 'Indie Flower', cursive; font-size: 1.3rem; color: #5d4037 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-radius: 4px;
    }
    .bujo-block { background: white; padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    .p-header { background-color: #f06292; color: white !important; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    .p-cell { background-color: white; min-height: 150px; padding: 15px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; margin-bottom: 20px; }
    .event-tag { background: #fff1f3; border-left: 4px solid #f06292; padding: 5px; margin-bottom: 5px; border-radius: 4px; color: #ad1457 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIQUE DE CONNEXION ---
if "user_data" not in st.session_state:
    st.session_state.user_data = None

def login_procedure(code_entre):
    if sh:
        try:
            ws = sh.worksheet("Utilisateurs")
            df = pd.DataFrame(ws.get_all_records())
            df.columns = [c.strip().capitalize() for c in df.columns]
            df['Code'] = df['Code'].astype(str).str.strip()
            match = df[df['Code'] == str(code_entre).strip()]
            if not match.empty:
                return match.iloc[0].to_dict()
        except:
            pass
    return None

# --- ÉCRAN DE LOGIN ---
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1, 1])
    with col_center:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code_saisi = st.text_input("Code personnel :", type="password")
        if st.button("Valider"):
            user = login_procedure(code_saisi)
            if user:
                st.session_state.user_data = user
                st.rerun()
            else:
                st.error("Accès refusé")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. RÉINTÉGRATION DES FONCTIONNALITÉS ---
user = st.session_state.user_data
st.markdown(f"<h1 style='text-align:center;'>Journal de {user['Nom']}</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"### 👤 {user['Nom']}")
    if st.button("🔒 Déconnexion"):
        st.session_state.user_data = None
        st.rerun()

# Menu dynamique
menu = ["📅 SEMAINE", "🛒 COURSES"]
if user.get('Accès journal') == "OUI" or user.get('Accès Journal') == "OUI":
    menu.insert(0, "✍️ MON JOURNAL")
    menu.append("💰 BUDGET PRIVÉ")

tabs = st.tabs(menu)
idx = 0

# --- ONGLET : JOURNAL ---
if "✍️ MON JOURNAL" in menu:
    with tabs[idx]:
        st.markdown(f"### ✨ Agenda du {datetime.now().strftime('%d %B')}")
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            st.markdown('<div class="post-it">Écris ici tes pensées ou utilise ton Pencil...</div>', unsafe_allow_html=True)
            st.text_area("Note", label_visibility="collapsed", height=200, key="note_j")
        with col_j2:
            st.markdown('<div class="bujo-block"><h3>📊 Trackers</h3>', unsafe_allow_html=True)
            st.checkbox("💧 Eau", key="c1")
            st.checkbox("🧘 Méditation", key="c2")
            st.markdown('</div>', unsafe_allow_html=True)
    idx += 1

# --- ONGLET : SEMAINE ---
with tabs[idx]:
    st.markdown("### 🗓️ Vue Hebdomadaire")
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️ Précédente"): st.session_state.w_off -= 1
    if c3.button("Suivante ➡️"): st.session_state.w_off += 1
    
    start_d = (datetime.now() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    c2.markdown(f"<p style='text-align:center;'>Semaine du {start_d.strftime('%d/%m')}</p>", unsafe_allow_html=True)

    try:
        data = sh.worksheet("Note").get_all_values()
        df_notes = pd.DataFrame(data[1:], columns=data[0])
        days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    curr = start_d + timedelta(days=i+j)
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{days_fr[i+j]} {curr.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        evs = ""
                        day_df = df_notes[df_notes.iloc[:, 0] == curr.strftime("%d/%m/%Y")]
                        for _, r in day_df.iterrows():
                            evs += f'<div class="event-tag"><b>{r.iloc[1]}</b> - {r.iloc[3]}</div>'
                        st.markdown(f'<div class="p-cell">{evs}</div>', unsafe_allow_html=True)
    except:
        st.info("Ajoute des notes dans ton tableau 'Note' pour les voir ici.")
idx += 1

# --- ONGLET : COURSES ---
with tabs[idx]:
    st.markdown('<div class="bujo-block"><h3>🛒 Liste de Courses & Budget Famille</h3>', unsafe_allow_html=True)
    st.write("Section partagée avec toute la maison.")
    st.markdown('</div>', unsafe_allow_html=True)
idx += 1

# --- ONGLET : BUDGET PRIVÉ ---
if "💰 BUDGET PRIVÉ" in menu:
    with tabs[idx]:
        st.markdown("### 🔒 Finances Détaillées")
        try:
            ws_f = sh.worksheet("Finances")
            df_f = pd.DataFrame(ws_f.get_all_records())
            st.data_editor(df_f, use_container_width=True)
        except:
            st.error("Onglet 'Finances' introuvable.")
