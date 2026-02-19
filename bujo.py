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

# --- 2. DESIGN ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    [data-testid="stSidebar"] { display: none; }
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3, p, label { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }
    
    /* Grille Semaine */
    .p-header { background-color: #f06292; color: white !important; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    
    /* Style Post-it Menu */
    .menu-postit { 
        background: #fff9c4; 
        padding: 20px; 
        border-left: 6px solid #fbc02d; 
        font-family: 'Indie Flower', cursive; 
        border-radius: 4px; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    .menu-title { font-size: 1.5rem; color: #5d4037 !important; text-align: center; margin-bottom: 10px; border-bottom: 1px dashed #fbc02d; }
    
    /* Bouton Enregistrer */
    .stButton>button { background-color: #1b5e20 !important; border-radius: 20px !important; color: white !important; width: 100%; }
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
            if code == "2125": st.session_state.user_data = {"Nom": "MeyLune", "Rôle": "Admin"}; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
user = st.session_state.user_data
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE 2026", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ONGLET SEMAINE + MENU ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    # Header Navigation
    c_n1, c_n2, c_n3 = st.columns([1, 2, 1])
    if c_n1.button("⬅️"): st.session_state.w_off -= 1
    if c_n3.button("➡️"): st.session_state.w_off += 1
    c_n2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)

    col_grille, col_menu = st.columns([3, 1]) # 3/4 pour la grille, 1/4 pour le menu

    # --- PARTIE GAUCHE : LA GRILLE ---
    with col_grille:
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
                            
                            txt_input = st.text_area("Note", value=val_init, height=100, key=f"input_{d_str}", label_visibility="collapsed")
                            if st.button("Enregistrer", key=f"save_{d_str}"):
                                ws_n.append_row([d_str, datetime.now().strftime("%H:%M"), "Note", txt_input])
                                st.rerun()
        except: st.info("Prêt pour tes notes.")

    # --- PARTIE DROITE : LE MENU POST-IT ---
    with col_menu:
        st.markdown("""
        <div class="menu-postit">
            <div class="menu-title">🍎 Menu de la Semaine</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            # On crée un dictionnaire pour stocker les repas
            jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            menu_data = {}
            
            for jour in jours:
                menu_data[jour] = st.text_input(f"{jour}", key=f"menu_{jour}_{st.session_state.w_off}")
            
            if st.button("💾 Sauver le Menu"):
                # Ici on pourrait sauvegarder dans un onglet "Menus" dédié
                st.success("Menu mis à jour !")

# --- AUTRES ONGLETS (IDENTIQUES) ---
with tabs[0]: st.write("Journal...")
with tabs[2]: # Calendrier Annuel
    st.markdown("### 📅 Année 2026")
    for row in range(4):
        cols_cal = st.columns(3)
        for col in range(3):
            m_num = row * 3 + col + 1
            with cols_cal[col]:
                st.markdown(f'<div style="text-align:center; color:#f06292; font-weight:bold;">{calendar.month_name[m_num]}</div>', unsafe_allow_html=True)
                st.code(calendar.month(2026, m_num).split('\n', 1)[1], language=None)
with tabs[3]: st.write("Trackers...")
with tabs[4]: st.write("Courses...")
with tabs[5]: 
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%201.jpg")
