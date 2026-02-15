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
    except: return None

sh = init_connection()

# --- 2. DESIGN ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    [data-testid="stSidebar"] { display: none; }
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3, p, label { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }
    
    /* Inputs */
    div[data-baseweb="input"], .stTextArea textarea, .stTextInput input {
        background-color: white !important; border: 2px solid #c8e6c9 !important;
        border-radius: 12px !important; color: #1b5e20 !important;
    }

    /* Boutons */
    .stButton>button { background-color: #1b5e20 !important; border-radius: 20px !important; border: none !important; }
    .stButton>button p { color: white !important; font-weight: bold !important; }

    /* Post-it & Blocs */
    .post-it { background: #fff9c4; padding: 25px; border-left: 6px solid #fbc02d; font-family: 'Indie Flower', cursive; font-size: 1.3rem; color: #5d4037 !important; border-radius: 4px; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .bujo-block { background: white; padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    
    /* Grille Semaine */
    .p-header { background-color: #f06292; color: white !important; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    .p-cell { background-color: white; min-height: 120px; padding: 10px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; margin-bottom: 15px; }
    .event-tag { background: #fff1f3; border-left: 4px solid #f06292; padding: 5px 8px; margin-bottom: 5px; border-radius: 4px; font-size: 0.9rem; color: #ad1457 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code = st.text_input("Code secret :", type="password")
        if st.button("Entrer"):
            if code == "2125": st.session_state.user_data = {"Nom": "MeyLune", "Rôle": "Admin"}; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
user = st.session_state.user_data
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ONGLET JOURNAL (AVEC HISTORIQUE) ---
with tabs[0]:
    st.markdown(f"### ✨ Mon Journal du {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown('<div class="post-it">Écris ici tes gratitudes ou tes pensées...</div>', unsafe_allow_html=True)
    note_du_jour = st.text_area("", placeholder="Cher journal...", height=200, label_visibility="collapsed")
    
    if st.button("Sauvegarder ma pensée"):
        if note_du_jour:
            try:
                ws_j = sh.worksheet("Journal")
                ws_j.append_row([datetime.now().strftime("%d/%m/%Y"), note_du_jour])
                st.success("Pensée enregistrée dans tes archives ! ✨")
            except: st.error("L'onglet 'Journal' est introuvable sur Google Sheets.")
    
    st.markdown("---")
    with st.expander("📖 Consulter mon historique"):
        try:
            ws_j = sh.worksheet("Journal")
            hist = pd.DataFrame(ws_j.get_all_records()).iloc[::-1] # Plus récent en premier
            for _, row in hist.head(5).iterrows():
                st.info(f"**Le {row['Date']}** : {row['Note']}")
        except: st.write("Aucun historique pour le moment.")

# --- ONGLET SEMAINE (DÉJÀ CORRIGÉ) ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    today = datetime.now().date()
    start_week = (today - timedelta(days=today.weekday())) + timedelta(weeks=st.session_state.w_off)
    st.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)
    
    # Affichage de la grille (logique identique à la précédente pour les cases internes)
    try:
        ws_n = sh.worksheet("Note")
        df_n = pd.DataFrame(ws_n.get_all_values()[1:], columns=ws_n.get_all_values()[0])
        days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    d = start_week + timedelta(days=i+j)
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{days_fr[i+j]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        evts = df_n[df_n.iloc[:, 0] == d.strftime("%d/%m/%Y")]
                        content = '<div class="p-cell">'
                        for _, r in evts.iterrows():
                            content += f'<div class="event-tag"><b>{r.iloc[1]}</b> : {r.iloc[3]}</div>'
                        content += '</div>'
                        st.markdown(content, unsafe_allow_html=True)
    except: st.info("Prêt pour tes rendez-vous.")
    
    with st.expander("➕ Ajouter un évènement"):
        with st.form("evt_f"):
            f_d = st.date_input("Date")
            f_h = st.text_input("Heure")
            f_n = st.text_input("Quoi ?")
            if st.form_submit_button("Ajouter"):
                sh.worksheet("Note").append_row([f_d.strftime("%d/%m/%Y"), f_h, "Note", f_n])
                st.rerun()

# --- ONGLET COURSES (NOUVEAU) ---
with tabs[3]:
    st.markdown("### 🛒 Liste de Courses")
    c_in, c_list = st.columns([1, 2])
    
    with c_in:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        nouvel_article = st.text_input("Ajouter un article :")
        if st.button("Ajouter à la liste"):
            if nouvel_article:
                sh.worksheet("Courses").append_row([nouvel_article])
                st.rerun()
        if st.button("🗑️ Vider la liste"):
            ws_c = sh.worksheet("Courses")
            ws_c.clear(); ws_c.append_row(["Article"]) # On garde l'en-tête
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c_list:
        try:
            items = sh.worksheet("Courses").get_all_records()
            if items:
                for item in items:
                    st.checkbox(item['Article'], key=f"check_{item['Article']}")
            else: st.write("La liste est vide ! 🌿")
        except: st.error("Onglet 'Courses' introuvable.")

# --- TRACKERS & STICKERS ---
with tabs[2]: st.write("Trackers en cours...")
with tabs[4]: 
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%201.jpg")
