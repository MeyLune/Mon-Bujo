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

# --- 2. DESIGN DASHBOARD STRUCTURE ---
st.set_page_config(page_title="MeyLune Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    .stApp {
        background-image: url("https://img.freepik.com/photos-gratuite/fond-fleurs-aquarelle-peint-main_23-2148405975.jpg");
        background-size: cover;
        background-attachment: fixed;
    }

    .main-white-box {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 30px;
        padding: 25px;
        min-height: 90vh;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin: 5px;
    }

    .nav-sidebar {
        background-color: #fce4ec;
        border-radius: 20px;
        padding: 15px;
        height: 100%;
        border: 1px solid #f8bbd0;
    }

    .bujo-card {
        background: white;
        border-radius: 15px;
        border: 2px solid #f8bbd0;
        margin-bottom: 15px;
        overflow: hidden;
    }
    .bujo-card-header {
        background-color: #f06292;
        color: white !important;
        padding: 8px;
        text-align: center;
        font-weight: bold;
    }

    .stButton>button { 
        background-color: #1b5e20 !important; 
        color: white !important; 
        border-radius: 20px !important; 
        width: 100%;
        border: none !important;
    }
    .stButton>button p { color: white !important; font-weight: bold; }
    
    h1, h2, h3 { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }
</style>
""", unsafe_allow_html=True)

# --- 3. SÉCURITÉ (CODE PIN) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="main-white-box" style="max-width:500px; margin: 100px auto; text-align:center;">', unsafe_allow_html=True)
    st.markdown("## 🌿 MeyLune Bujo")
    pin = st.text_input("Entrez votre code secret :", type="password")
    if st.button("Se connecter"):
        if pin == "2125":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Code incorrect")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
if "page" not in st.session_state: 
    st.session_state.page = "🗓️ SEMAINE"

# --- 5. AFFICHAGE DU DASHBOARD ---
st.markdown('<div class="main-white-box">', unsafe_allow_html=True)
col_nav, col_content = st.columns([1, 4])

with col_nav:
    st.markdown('<div class="nav-sidebar">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:bold;'>MENU</p>", unsafe_allow_html=True)
    if st.button("✍️ JOURNAL"): st.session_state.page = "✍️ JOURNAL"; st.rerun()
    if st.button("🗓️ SEMAINE"): st.session_state.page = "🗓️ SEMAINE"; st.rerun()
    if st.button("📅 ANNEE 2026"): st.session_state.page = "📅 ANNEE 2026"; st.rerun()
    if st.button("📊 TRACKERS"): st.session_state.page = "📊 TRACKERS"; st.rerun()
    if st.button("🛒 COURSES"): st.session_state.page = "🛒 COURSES"; st.rerun()
    if st.button("🎨 STICKERS"): st.session_state.page = "🎨 STICKERS"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_content:
    # --- PAGE JOURNAL ---
    if st.session_state.page == "✍️ JOURNAL":
        st.subheader("✍️ Mon Journal")
        note_j = st.text_area("Ma pensée du jour...", height=250)
        if st.button("Enregistrer dans le Sheets"):
            sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), note_j])
            st.success("Enregistré ! ✨")

    # --- PAGE SEMAINE (Grille + Menu) ---
    elif st.session_state.page == "🗓️ SEMAINE":
        if 'w_off' not in st.session_state: st.session_state.w_off = 0
        start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
        
        c1, c2, c3 = st.columns([1,2,1])
        with c1: 
            if st.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
        with c3: 
            if st.button("➡️"): st.session_state.w_off += 1; st.rerun()
        c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)

        cg, cm = st.columns([3, 1])
        with cg: # Grille
            ws_n = sh.worksheet("Note")
            df_n = pd.DataFrame(ws_n.get_all_values()[1:], columns=ws_n.get_all_values()[0])
            days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            for i in range(0, 7, 2):
                cols_d = st.columns(2)
                for j in range(2):
                    if (i+j) < 7:
                        d = start_week + timedelta(days=i+j)
                        d_str = d.strftime("%d/%m/%Y")
                        with cols_d[j]:
                            st.markdown(f'<div class="bujo-card"><div class="bujo-card-header">{days[i+j]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                            evts = df_n[df_n.iloc[:, 0] == d_str]
                            val_init = "\n".join([f"{r.iloc[1]} {r.iloc[3]}" for _, r in evts.iterrows()])
                            txt_in = st.text_area("Note", value=val_init, height=120, key=f"in_{d_str}", label_visibility="collapsed")
                            if st.button("Sauver", key=f"sv_{d_str}"):
                                ws_n.append_row([d_str, datetime.now().strftime("%H:%M"), "Note", txt_in])
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
        with cm: # Menu Repas
            st.markdown('<div style="background:#fff9c4; padding:15px; border-radius:15px; border-left:5px solid #fbc02d; font-family:\'Indie Flower\'">🍎 <b>Menu Repas</b></div>', unsafe_allow_html=True)
            for j in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]:
                st.text_input(j, key=f"menu_{j}")

    # --- PAGE CALENDRIER ANNUEL ---
    elif st.session_state.page == "📅 ANNEE 2026":
        st.subheader("📅 Vue Annuelle 2026")
        for r in range(4):
            cols_cal = st.columns(3)
            for c in range(3):
                m = r * 3 + c + 1
                with cols_cal[c]:
                    st.markdown(f'<div class="bujo-card"><div class="bujo-card-header">{calendar.month_name[m].upper()}</div><div style="text-align:center; padding:10px; font-family:monospace;">{calendar.month(2026, m).split(chr(10), 1)[1].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)

    # --- AUTRES PAGES ---
    elif st.session_state.page == "📊 TRACKERS":
        st.subheader("📊 Mes Trackers")
        st.slider("💧 Verres d'eau", 0, 12, 0)
        st.checkbox("🧘 Méditation")
        st.checkbox("📚 Lecture")

    elif st.session_state.page == "🛒 COURSES":
        st.subheader("🛒 Liste de Courses")
        it = st.text_input("Ajouter un article :")
        if st.button("Ajouter à la liste"):
            if it: sh.worksheet("Courses").append_row([it]); st.rerun()
        try:
            for r in sh.worksheet("Courses").get_all_records(): st.checkbox(r['Article'], key=f"c_{r['Article']}")
        except: st.write("Liste vide")

    elif st.session_state.page == "🎨 STICKERS":
        st.subheader("🎨 Mes Stickers")
        st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
        st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%201.jpg")

st.markdown('</div>', unsafe_allow_html=True)
