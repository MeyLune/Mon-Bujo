import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd
import calendar

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

# --- 2. DESIGN & CORRECTION DES ZONES NOIRES ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

# Lien vers ton image sur GitHub (nom corrigé avec %20 pour l'espace)
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    [data-testid="stSidebar"] {{ display: none; }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* CORRECTION RADICALE DU NOIR : Force le fond blanc sur tous les champs */
    div[data-baseweb="textarea"], div[data-baseweb="input"], 
    .stTextArea textarea, .stTextInput input, .stNumberInput input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1b5e20 !important;
        border-radius: 12px !important;
        border: 1px solid #f06292 !important;
        -webkit-text-fill-color: #1b5e20 !important;
    }}

    /* Blocs de contenu */
    .stTabs, .bujo-block, .cal-card {{
        background-color: rgba(255, 255, 255, 0.85) !important;
        border-radius: 20px;
        padding: 15px;
        border: 1px solid #c8e6c9;
        margin-bottom: 20px;
    }}

    h1, h2, h3, p, label, .stMarkdown {{ color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }}
    
    /* Boutons de validation (Rose) */
    .stButton>button {{ 
        background-color: #f06292 !important; 
        color: white !important;
        border-radius: 20px !important; 
        border: none !important;
        padding: 8px 20px !important;
        font-weight: bold !important;
        width: 100%;
    }}

    .p-header {{ 
        background-color: #f06292 !important; 
        color: white !important; 
        padding: 8px; 
        text-align: center; 
        border-radius: 12px 12px 0 0; 
        font-weight: bold; 
    }}
    
    .post-it {{ 
        background: rgba(255, 249, 196, 0.95); padding: 15px; border-left: 6px solid #fbc02d; 
        font-family: 'Indie Flower', cursive; color: #5d4037 !important; 
        border-radius: 5px; margin-bottom: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center; background:white; padding:20px; border-radius:20px;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal"):
            if code == "2125": st.session_state.user_data = {"Nom": "MeyLune"}; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ONGLET JOURNAL ---
with tabs[0]:
    st.markdown(f"### ✨ Aujourd'hui, {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown('<div class="post-it">Comment te sens-tu aujourd\'hui ?</div>', unsafe_allow_html=True)
    note_txt = st.text_area("", height=200, key="j_note", label_visibility="collapsed")
    if st.button("✅ Enregistrer dans le Cloud", key="save_j"):
        if note_txt and sh:
            sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), note_txt])
            st.success("C'est enregistré ! 🌸")

# --- ONGLET SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c_n1, c_n2, c_n3 = st.columns([1, 2, 1])
    if c_n1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c_n3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c_n2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)

    col_g, col_m = st.columns([3, 1.2])
    with col_g:
        days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    d = start_week + timedelta(days=i+j)
                    d_str = d.strftime("%d/%m/%Y")
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{days_fr[i+j]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        val = st.text_area("Note", height=100, key=f"in_{d_str}", label_visibility="collapsed")
                        if st.button("💾 Sauver", key=f"btn_{d_str}"):
                            if sh: sh.worksheet("Note").append_row([d_str, "RDV/Note", val]); st.success("C'est noté !")

    with col_m:
        st.markdown('<div class="post-it"><b>🍎 Menu de la Semaine</b></div>', unsafe_allow_html=True)
        m_lun = st.text_input("Lundi", key="mlun")
        m_mar = st.text_input("Mardi", key="mmar")
        m_mer = st.text_input("Mercredi", key="mmer")
        m_jeu = st.text_input("Jeudi", key="mjeu")
        m_ven = st.text_input("Vendredi", key="mven")
        m_sam = st.text_input("Samedi", key="msam")
        m_dim = st.text_input("Dimanche", key="mdim")
        if st.button("✨ Valider mon Menu"):
            if sh: sh.worksheet("Menu").append_row([start_week.strftime("%d/%m/%Y"), m_lun, m_mar, m_mer, m_jeu, m_ven, m_sam, m_dim])
            st.balloons()
            st.success("Menu enregistré !")

# --- ONGLET ANNEE + HISTORIQUE ---
with tabs[2]:
    st.markdown("### 📅 Calendrier 2026")
    for r in range(4):
        cols_c = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_c[c]:
                st.markdown(f'<div class="cal-card"><div class="cal-card-header">{calendar.month_name[m_idx].upper()}</div><div style="text-align:center;">{calendar.month(2026, m_idx).split(chr(10), 1)[1].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 📜 Historique & Exports")
    # On affiche les entrées du journal pour l'historique
    try:
        df_j = pd.DataFrame(sh.worksheet("Journal").get_all_values()[1:], columns=["Date", "Pensée"])
        st.dataframe(df_j, use_container_width=True)
        csv = df_j.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger mon Journal (CSV)", data=csv, file_name="mon_journal.csv")
    except: st.info("L'historique se remplira au fur et à mesure.")

# --- ONGLET TRACKERS ---
with tabs[3]:
    st.markdown("### 📊 Mes Trackers")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="bujo-block"><b>🌿 BIEN-ÊTRE</b>', unsafe_allow_html=True)
        st.checkbox("Méditation"); st.checkbox("Sport"); st.checkbox("Yoga")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="bujo-block"><b>💧 HYDRATATION</b>', unsafe_allow_html=True)
        eau = st.slider("Verres d'eau", 0, 12, 0)
        st.button("Valider l'eau")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="bujo-block"><b>📚 MA BIBLIOTHÈQUE</b>', unsafe_allow_html=True)
        st.text_input("Livre en cours")
        st.number_input("Page actuelle", min_value=0)
        st.button("Mettre à jour ma lecture")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ONGLET COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses")
    st.markdown("<b>Sélection Rapide :</b>", unsafe_allow_html=True)
    cols_q = st.columns(6)
    items = ["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]
    for i, it in enumerate(items):
        if cols_q[i].button(it):
            if sh: sh.worksheet("Courses").append_row([it]); st.rerun()
    
    st.divider()
    autre = st.text_input("➕ Autre article :")
    if st.button("Ajouter à la liste"):
        if autre and sh: sh.worksheet("Courses").append_row([autre]); st.rerun()
    
    try:
        data_c = sh.worksheet("Courses").get_all_records()
        for c in data_c: st.checkbox(c['Article'], key=f"check_{c['Article']}")
    except: st.write("Ta liste t'attend !")

# --- ONGLET STICKERS ---
with tabs[5]:
    st.markdown("### 🎨 Stickers")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
