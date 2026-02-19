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

# --- 2. DESIGN HARMONIEUX & DASHBOARD ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    .stApp {
        background-image: url("https://img.freepik.com/photos-gratuite/fond-fleurs-aquarelle-peint-main_23-2148405975.jpg");
        background-size: cover;
        background-attachment: fixed;
    }

    .main-container {
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 30px;
        padding: 30px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        margin: 5px;
    }

    /* Onglets */
    .stTabs [data-baseweb="tab-list"] { background-color: #fce4ec; border-radius: 20px; padding: 8px; }
    .stTabs [data-baseweb="tab"] { color: #ad1457 !important; font-family: 'Comfortaa'; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #f06292 !important; color: white !important; border-radius: 12px; }

    /* Grille Semaine */
    .p-header { background-color: #f06292; color: white !important; padding: 8px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    
    /* Calendrier Annuel */
    .cal-box { background: white; border-radius: 20px; overflow: hidden; margin-bottom: 20px; border: 2px solid #f8bbd0; }
    .cal-title { background: #f06292; color: white !important; text-align: center; padding: 5px; font-weight: bold; }
    .cal-content { padding: 10px; font-family: monospace; text-align: center; color: #1b5e20; line-height: 1.2; }

    /* Boutons */
    .stButton>button { background: #1b5e20 !important; color: white !important; border-radius: 25px !important; border: none !important; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        st.markdown('<div style="background:white; padding:20px; border-radius:20px; border:1px solid #c8e6c9;">', unsafe_allow_html=True)
        code = st.text_input("Code secret :", type="password")
        if st.button("Entrer"):
            if code == "2125": st.session_state.user_data = {"Nom": "MeyLune"}; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. STRUCTURE ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)
user = st.session_state.user_data
st.markdown(f"<h1 style='text-align:center;'>🌸 Journal de {user['Nom']}</h1>", unsafe_allow_html=True)

tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE 2026", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ONGLET 1 : JOURNAL ---
with tabs[0]:
    st.markdown(f"### ✨ Aujourd'hui, {datetime.now().strftime('%d/%m/%Y')}")
    note_j = st.text_area("Ma pensée...", height=150, label_visibility="collapsed")
    if st.button("Sauvegarder ma pensée"):
        sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), note_j])
        st.success("C'est enregistré !")
    with st.expander("📖 Historique"):
        hist = pd.DataFrame(sh.worksheet("Journal").get_all_records()).iloc[::-1]
        for _, r in hist.head(5).iterrows(): st.info(f"**{r['Date']}** : {r['Note']}")

# --- ONGLET 2 : SEMAINE + MENU ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c_n1, c_n2, c_n3 = st.columns([1, 2, 1])
    if c_n1.button("⬅️"): st.session_state.w_off -= 1
    if c_n3.button("➡️"): st.session_state.w_off += 1
    c_n2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)

    col_g, col_m = st.columns([3, 1])
    with col_g: # GRILLE
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
    with col_m: # MENU
        st.markdown('<div style="background:#fff9c4; padding:15px; border-radius:15px; border-left:5px solid #fbc02d; color:#5d4037; font-family:\'Indie Flower\'"><b>🍎 Menu Semaine</b></div>', unsafe_allow_html=True)
        for j in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]:
            st.text_input(j, key=f"menu_{j}_{st.session_state.w_off}")

# --- ONGLET 3 : ANNEE 2026 ---
with tabs[2]:
    st.markdown("### 📅 Calendrier Annuel")
    for r in range(4):
        cols_c = st.columns(3)
        for c in range(3):
            m = r * 3 + c + 1
            with cols_c[c]:
                st.markdown(f'<div class="cal-box"><div class="cal-title">{calendar.month_name[m].upper()}</div><div class="cal-content">{calendar.month(2026, m).split(chr(10), 1)[1].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)

# --- ONGLET 4 : TRACKERS ---
with tabs[3]:
    st.markdown("### 📊 Mes Trackers")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div style="background:white; padding:20px; border-radius:20px; border:1px solid #c8e6c9;">💧 Eau (Verres)', unsafe_allow_html=True)
        st.slider("", 0, 12, 0, key="water")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div style="background:white; padding:20px; border-radius:20px; border:1px solid #c8e6c9;">🌿 Bien-être', unsafe_allow_html=True)
        st.checkbox("Méditation"); st.checkbox("Lecture"); st.checkbox("Sport")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ONGLET 5 : COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses")
    c_add, c_list = st.columns([1, 2])
    with c_add:
        it = st.text_input("Ajouter article :")
        if st.button("Ajouter"):
            if it: sh.worksheet("Courses").append_row([it]); st.rerun()
        if st.button("🗑️ Vider"):
            ws_c = sh.worksheet("Courses"); ws_c.clear(); ws_c.append_row(["Article"]); st.rerun()
    with c_list:
        try:
            for r in sh.worksheet("Courses").get_all_records(): st.checkbox(r['Article'], key=f"c_{r['Article']}")
        except: st.write("Liste vide.")

# --- ONGLET 6 : STICKERS ---
with tabs[5]:
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%201.jpg")

st.markdown('</div>', unsafe_allow_html=True)
