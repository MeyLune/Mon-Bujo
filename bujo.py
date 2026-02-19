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

# --- 2. DESIGN GLOBAL (CORRECTIF COULEURS) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    [data-testid="stSidebar"] { display: none; }
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    
    /* Force les textes en vert foncé */
    h1, h2, h3, p, label, .stMarkdown { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }
    
    /* Correction Contrastes Champs */
    div[data-baseweb="input"], .stTextArea textarea, .stTextInput input, div[data-baseweb="select"] {
        background-color: white !important;
        border: 2px solid #c8e6c9 !important;
        border-radius: 12px !important;
        color: #1b5e20 !important;
    }

    /* BOUTONS : Fond vert, texte BLANC impératif */
    .stButton>button { 
        background-color: #1b5e20 !important; 
        border-radius: 20px !important; 
        border: none !important;
        padding: 5px 20px !important;
    }
    .stButton>button p { color: white !important; font-weight: bold !important; }

    /* Grille Semaine */
    .p-header { background-color: #f06292; color: white !important; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    .p-cell-interactive { background-color: white; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; margin-bottom: 20px; padding: 10px; }
    
    /* Style Post-it (Jaune) */
    .post-it { 
        background: #fff9c4; padding: 20px; border-left: 6px solid #fbc02d; 
        font-family: 'Indie Flower', cursive; font-size: 1.2rem; color: #5d4037 !important; 
        border-radius: 4px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Blocs blancs arrondis */
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
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ONGLET 1 : JOURNAL ---
with tabs[0]:
    st.markdown(f"### ✨ Aujourd'hui, {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown('<div class="post-it">Écris tes gratitudes ou pensées du jour...</div>', unsafe_allow_html=True)
    note_txt = st.text_area("", placeholder="Cher journal...", height=150, label_visibility="collapsed", key="j_note")
    if st.button("Sauvegarder ma pensée"):
        if note_txt:
            sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), note_txt])
            st.success("C'est enregistré ! ✨")
    
    with st.expander("📖 Voir mes anciennes notes"):
        try:
            hist = pd.DataFrame(sh.worksheet("Journal").get_all_records()).iloc[::-1]
            for _, r in hist.head(5).iterrows():
                st.info(f"**Le {r['Date']}** : {r['Note']}")
        except: st.write("Pas encore d'historique.")

# --- ONGLET 2 : SEMAINE + MENU REPAS ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c_n1, c_n2, c_n3 = st.columns([1, 2, 1])
    if c_n1.button("⬅️"): st.session_state.w_off -= 1
    if c_n3.button("➡️"): st.session_state.w_off += 1
    c_n2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)

    col_g, col_m = st.columns([3, 1])
    with col_g: # GRILLE
        try:
            ws_n = sh.worksheet("Note")
            df_n = pd.DataFrame(ws_n.get_all_values()[1:], columns=ws_n.get_all_values()[0])
            days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            for i in range(0, 7, 2):
                cols = st.columns(2)
                for j in range(2):
                    if (i+j) < 7:
                        d = start_week + timedelta(days=i+j)
                        d_str = d.strftime("%d/%m/%Y")
                        with cols[j]:
                            st.markdown(f'<div class="p-header">{days[i+j]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                            evts = df_n[df_n.iloc[:, 0] == d_str]
                            val_init = "\n".join([f"{r.iloc[1]} {r.iloc[3]}" for _, r in evts.iterrows()])
                            txt_in = st.text_area("Note", value=val_init, height=100, key=f"in_{d_str}", label_visibility="collapsed")
                            if st.button("Sauver", key=f"sv_{d_str}"):
                                ws_n.append_row([d_str, datetime.now().strftime("%H:%M"), "Note", txt_in])
                                st.rerun()
        except: st.info("Prêt pour tes notes.")
    
    with col_m: # MENU POST-IT
        st.markdown('<div class="post-it"><b style="color:#5d4037">🍎 Menu Semaine</b></div>', unsafe_allow_html=True)
        for j in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]:
            st.text_input(j, key=f"m_{j}_{st.session_state.w_off}")
        if st.button("Sauver Menu"): st.success("Menu noté !")

# --- ONGLET 3 : ANNEE 2026 ---
with tabs[2]:
    st.markdown("### 📅 Vue Annuelle 2026")
    for r in range(4):
        cols_c = st.columns(3)
        for c in range(3):
            m = r * 3 + c + 1
            with cols_c[c]:
                st.markdown(f'<div style="text-align:center; color:#f06292; font-weight:bold; border-bottom:1px solid #eee;">{calendar.month_name[m]}</div>', unsafe_allow_html=True)
                st.code(calendar.month(2026, m).split('\n', 1)[1], language=None)

# --- ONGLET 4 : TRACKERS ---
with tabs[3]:
    st.markdown("### 📊 Mes Suivis")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="bujo-block">💧 Eau (Verres)', unsafe_allow_html=True)
        eau = st.slider("", 0, 12, 0, key="w_slid")
        if st.button("Noter Eau"): st.success(f"{eau} verres !")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="bujo-block">🌿 Bien-être', unsafe_allow_html=True)
        st.checkbox("Méditation"); st.checkbox("Lecture"); st.checkbox("Sport")
        if st.button("Enregistrer Bien-être"): st.success("C'est fait !")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ONGLET 5 : COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses")
    c_a, c_l = st.columns([1, 2])
    with c_a:
        st.markdown('<div class="bujo-block">➕ Ajouter', unsafe_allow_html=True)
        item = st.text_input("Article :")
        if st.button("Ajouter à la liste"):
            if item: sh.worksheet("Courses").append_row([item]); st.rerun()
        if st.button("🗑️ Vider"):
            ws_c = sh.worksheet("Courses"); ws_c.clear(); ws_c.append_row(["Article"]); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c_l:
        st.markdown("**À acheter :**")
        try:
            for it in sh.worksheet("Courses").get_all_records():
                st.checkbox(it['Article'], key=f"c_{it['Article']}")
        except: st.write("Liste vide.")

# --- ONGLET 6 : STICKERS ---
with tabs[5]:
    st.markdown("### 🎨 Ma collection")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%201.jpg")
