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

# --- 2. DESIGN AVEC FOND GITHUB ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

# REMPLACE l'URL ci-dessous par ton lien Raw GitHub si tu veux ton image précise
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/fond_fleuri.jpg" 

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    [data-testid="stSidebar"] { display: none; }
    
    /* Arrière-plan téléchargé depuis GitHub */
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-attachment: fixed;
    }}
    
    /* On rend les blocs légèrement translucides pour le style */
    .stTabs, .bujo-block, .p-cell-interactive, .cal-card {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 15px;
        padding: 10px;
    }}

    h1, h2, h3, p, label, .stMarkdown {{ color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }}
    
    /* Boutons et Inputs */
    .stButton>button {{ 
        background-color: #1b5e20 !important; 
        border-radius: 20px !important; 
        color: white !important;
    }}
    .stButton>button p {{ color: white !important; font-weight: bold !important; }}

    /* Grille Semaine & Calendrier */
    .p-header, .cal-card-header {{ 
        background-color: #f06292; 
        color: white !important; 
        padding: 10px; 
        text-align: center; 
        border-radius: 10px 10px 0 0; 
        font-weight: bold; 
    }}
    
    .cal-card {{ border: 2px solid #f8bbd0; margin-bottom: 20px; }}
    .cal-card-body {{ padding: 10px; font-family: monospace; text-align: center; color: #1b5e20; line-height: 1.4; }}
    
    .post-it {{ 
        background: rgba(255, 249, 196, 0.95); padding: 20px; border-left: 6px solid #fbc02d; 
        font-family: 'Indie Flower', cursive; color: #5d4037 !important; 
        border-radius: 4px; 
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center; background:white; padding:20px; border-radius:20px;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        st.markdown('<div style="background:white; padding:20px; border-radius:20px; border:1px solid #c8e6c9;">', unsafe_allow_html=True)
        code = st.text_input("Code secret :", type="password")
        if st.button("Entrer"):
            if code == "2125": st.session_state.user_data = {"Nom": "MeyLune"}; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
user = st.session_state.user_data
st.title(f"Journal de {user['Nom']}")
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- CONTENU DES ONGLETS (Fonctionnalités préservées) ---
with tabs[0]: # JOURNAL
    st.markdown(f"### ✨ Aujourd'hui, {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown('<div class="post-it">Écris tes gratitudes...</div>', unsafe_allow_html=True)
    note_txt = st.text_area("", placeholder="Cher journal...", height=150, key="j_note")
    if st.button("Sauvegarder ma pensée"):
        sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), note_txt])
        st.success("Enregistré ! ✨")

with tabs[1]: # SEMAINE
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    c_n1, c_n2, c_n3 = st.columns([1, 2, 1])
    if c_n1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c_n3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c_n2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]}</h3>", unsafe_allow_html=True)
    
    col_g, col_m = st.columns([3, 1])
    with col_g:
        ws_n = sh.worksheet("Note")
        df_n = pd.DataFrame(ws_n.get_all_values()[1:], columns=ws_n.get_all_values()[0])
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    d = start_week + timedelta(days=i+j)
                    d_str = d.strftime("%d/%m/%Y")
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{calendar.day_name[i+j].capitalize()} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        evts = df_n[df_n.iloc[:, 0] == d_str]
                        val_init = "\n".join([f"{r.iloc[1]} {r.iloc[3]}" for _, r in evts.iterrows()])
                        txt_in = st.text_area("Note", value=val_init, height=100, key=f"in_{d_str}", label_visibility="collapsed")
                        if st.button("Sauver", key=f"sv_{d_str}"):
                            ws_n.append_row([d_str, datetime.now().strftime("%H:%M"), "Note", txt_in])
                            st.rerun()
    with col_m:
        st.markdown('<div class="post-it"><b>🍎 Menu</b></div>', unsafe_allow_html=True)
        for j in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]:
            st.text_input(j, key=f"m_{j}_{st.session_state.w_off}")

with tabs[2]: # ANNEE
    st.markdown("### 📅 Calendrier 2026")
    for r in range(4):
        cols_c = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_c[c]:
                st.markdown(f'<div class="cal-card"><div class="cal-card-header">{calendar.month_name[m_idx].upper()}</div><div class="cal-card-body">{calendar.month(2026, m_idx).split(chr(10), 1)[1].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)

with tabs[3]: # TRACKERS
    st.markdown('<div style="background:white; padding:20px; border-radius:15px;">📊 Mes Suivis</div>', unsafe_allow_html=True)
    st.slider("Eau", 0, 12, 0)

with tabs[4]: # COURSES
    it = st.text_input("➕ Ajouter article :")
    if st.button("Ajouter"):
        if it: sh.worksheet("Courses").append_row([it]); st.rerun()
    try:
        for r in sh.worksheet("Courses").get_all_records(): st.checkbox(r['Article'], key=f"c_{r['Article']}")
    except: st.write("Liste vide.")

with tabs[5]: # STICKERS
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%201.jpg")
