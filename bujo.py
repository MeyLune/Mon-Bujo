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
    
    div[data-baseweb="input"], .stTextArea textarea, .stTextInput input, div[data-baseweb="select"] {
        background-color: white !important; border: 2px solid #c8e6c9 !important;
        border-radius: 12px !important; color: #1b5e20 !important;
    }

    .stButton>button { background-color: #1b5e20 !important; border-radius: 20px !important; border: none !important; }
    .stButton>button p { color: white !important; font-weight: bold !important; }

    .p-header { background-color: #f06292; color: white !important; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    .p-cell { background-color: white; min-height: 150px; padding: 10px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; margin-bottom: 20px; }
    .event-tag { background: #fff1f3; border-left: 4px solid #f06292; padding: 5px 8px; margin-bottom: 5px; border-radius: 4px; font-size: 0.9rem; color: #ad1457 !important; }
    
    .post-it { background: #fff9c4; padding: 25px; border-left: 6px solid #fbc02d; font-family: 'Indie Flower', cursive; font-size: 1.3rem; color: #5d4037 !important; border-radius: 4px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .bujo-block { background: white; padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
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
st.title(f"Journal de {user['Nom']}")
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- JOURNAL ---
with tabs[0]:
    st.markdown(f"### ✨ Aujourd'hui, {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown('<div class="post-it">Écris tes gratitudes ou pensées du jour...</div>', unsafe_allow_html=True)
    note_txt = st.text_area("", height=200, label_visibility="collapsed", key="journal_note")
    if st.button("Sauvegarder ma pensée"):
        if note_txt:
            sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), note_txt])
            st.success("Pensée enregistrée ! ✨")

# --- SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    c_n1, c_n2, c_n3 = st.columns([1, 2, 1])
    if c_n1.button("⬅️"): st.session_state.w_off -= 1
    if c_n3.button("➡️"): st.session_state.w_off += 1
    c_n2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)
    
    try:
        ws_n = sh.worksheet("Note")
        df_n = pd.DataFrame(ws_n.get_all_values()[1:], columns=ws_n.get_all_values()[0])
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    d = start_week + timedelta(days=i+j)
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{days[i+j]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        evts = df_n[df_n.iloc[:, 0] == d.strftime("%d/%m/%Y")]
                        content = '<div class="p-cell">'
                        for _, r in evts.iterrows():
                            content += f'<div class="event-tag"><b>{r.iloc[1]}</b> : {r.iloc[3]}</div>'
                        content += '</div>'
                        st.markdown(content, unsafe_allow_html=True)
    except: st.info("Prêt pour tes rendez-vous.")

# --- TRACKERS ---
with tabs[2]:
    st.markdown("### 📊 Mes Suivis")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="bujo-block">💧 Verres d\'eau', unsafe_allow_html=True)
        eau = st.slider("Quantité", 0, 12, 0, key="water_input")
        if st.button("Enregistrer Eau"): st.success(f"{eau} verres notés !")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="bujo-block">🌿 Bien-être', unsafe_allow_html=True)
        st.checkbox("Méditation", key="medit")
        st.checkbox("Lecture", key="read")
        st.checkbox("Sport", key="sport")
        if st.button("Valider Bien-être"): st.success("Bravo pour tes efforts !")
        st.markdown('</div>', unsafe_allow_html=True)

# --- COURSES ---
with tabs[3]:
    st.markdown("### 🛒 Liste de Courses & Suivi")
    
    col_date, col_add = st.columns(2)
    with col_date:
        st.markdown('<div class="bujo-block">🗓️ Prochaines Courses', unsafe_allow_html=True)
        date_course = st.date_input("Date prévue :", value=datetime.now())
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_add:
        st.markdown('<div class="bujo-block">➕ Ajout Manuel', unsafe_allow_html=True)
        art = st.text_input("Article :", placeholder="Ex: Fraises...")
        if st.button("Ajouter à la liste"):
            if art: sh.worksheet("Courses").append_row([art]); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 Ma Liste interactive")
    
    col_pre, col_final = st.columns([1, 1])
    with col_pre:
        st.markdown("**Indispensables (Prédéfini) :**")
        indis = ["Lait", "Oeufs", "Pain", "Beurre", "Pâtes", "Fruits"]
        for i in indis:
            if st.checkbox(i, key=f"pre_{i}"):
                if st.button(f"Confirmer {i}"): 
                    sh.worksheet("Courses").append_row([i]); st.rerun()
                    
    with col_final:
        st.markdown("**Ma liste actuelle :**")
        try:
            items = sh.worksheet("Courses").get_all_records()
            for it in items: st.checkbox(it['Article'], key=f"list_{it['Article']}")
            if st.button("🗑️ Vider la liste complète"):
                ws_c = sh.worksheet("Courses"); ws_c.clear(); ws_c.append_row(["Article"]); st.rerun()
        except: st.write("Liste vide 🌿")

# --- STICKERS ---
with tabs[4]:
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%201.jpg")
