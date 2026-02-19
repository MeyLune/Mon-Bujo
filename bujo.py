import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd
import calendar

# --- 1. CONNEXION À GOOGLE SHEETS ---
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
    except Exception as e:
        st.error(f"Erreur Connexion Google Sheets : {e}")
        return None

sh = init_connection()

# --- 2. DESIGN GLOBAL (ANTI-NOIR & FOND FLORAL) ---
st.set_page_config(page_title="MeyLune Bullet Journal", layout="wide", initial_sidebar_state="collapsed")

fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    /* FORCE LE FOND D'ÉCRAN */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-image: url("{fond_url}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    /* FORCE LE BLANC POUR TOUTES LES ENTRÉES (Correction iPad/Dark Mode) */
    div[data-baseweb="textarea"], div[data-baseweb="input"], 
    .stTextArea textarea, .stTextInput input, .stNumberInput input, 
    [data-testid="stDataFrame"], [data-testid="stTable"] {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1b5e20 !important;
        border: 2px solid #f06292 !important;
        border-radius: 15px !important;
        -webkit-text-fill-color: #1b5e20 !important;
    }}

    /* Conteneurs Translucides */
    .stTabs, .bujo-block, .cal-card {{
        background-color: rgba(255, 255, 255, 0.88) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        border: 1px solid #c8e6c9 !important;
    }}

    h1, h2, h3, p, label, .stMarkdown {{ color: #1b5e20 !important; font-family: 'Comfortaa', cursive; font-weight: bold; }}
    
    /* Boutons Roses MeyLune */
    .stButton>button {{ 
        background-color: #f06292 !important; color: white !important;
        border-radius: 25px !important; border: none !important;
        padding: 10px 25px !important; font-weight: bold !important; width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}

    .p-header {{ background-color: #f06292 !important; color: white !important; padding: 10px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; }}
    .post-it {{ background: rgba(255, 249, 196, 0.95); padding: 15px; border-left: 6px solid #fbc02d; font-family: 'Indie Flower', cursive; color: #5d4037 !important; border-radius: 5px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. AUTHENTIFICATION ---
if "user_data" not in st.session_state: st.session_state.user_data = None

if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center; background:white; padding:20px; border-radius:20px;'>🌿 Mon Bullet Journal</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code_saisi = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal"):
            login_ok = False
            try:
                users = sh.worksheet("Utilisateurs").get_all_records()
                for u in users:
                    if str(u['Code']) == str(code_saisi):
                        st.session_state.user_data = {"Nom": u['Nom'], "Acces": u['Accès Journal']}
                        login_ok = True; break
            except:
                if code_saisi == "2125": # Secours
                    st.session_state.user_data = {"Nom": "MeyLune", "Acces": "OUI"}
                    login_ok = True
            
            if login_ok: st.rerun()
            else: st.error("Code incorrect ou erreur de base de données. 🌸")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
user_nom = st.session_state.user_data['Nom']
st.markdown(f"<h1 style='background:white; padding:10px; border-radius:15px; text-align:center;'>🌸 Journal de {user_nom}</h1>", unsafe_allow_html=True)

tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ONGLET 1 : JOURNAL ---
with tabs[0]:
    if st.session_state.user_data['Acces'] == "OUI":
        st.markdown(f"### ✨ Aujourd'hui, {datetime.now().strftime('%d/%m/%Y')}")
        st.markdown('<div class="post-it">Comment te sens-tu aujourd\'hui ?</div>', unsafe_allow_html=True)
        note_j = st.text_area("", height=200, key="j_note", label_visibility="collapsed")
        if st.button("💾 Enregistrer ma pensée"):
            if note_j and sh:
                sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), user_nom, note_j])
                st.success("Enregistré avec succès ! 🌸")
    else: st.warning("Tu n'as pas l'accès pour écrire dans ce journal. 🔒")

# --- ONGLET 2 : SEMAINE (iPad Optimized) ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️ Précédente"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("Suivante ➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 1.2])
    semaine_data = {}
    with col_left:
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    d = start_week + timedelta(days=i+j)
                    d_str = d.strftime("%d/%m/%Y")
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{jours[i+j]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        semaine_data[d_str] = st.text_area("Note", height=100, key=f"s_{d_str}", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        b_col1, b_col2 = st.columns(2)
        if b_col1.button("💾 TOUT SAUVEGARDER LA SEMAINE"):
            if sh:
                for date_k, text in semaine_data.items():
                    if text.strip(): sh.worksheet("Note").append_row([date_k, user_nom, text])
                st.success("Semaine enregistrée ! ✨")
        if b_col2.button("🔄 MODIFIER / RAFRAÎCHIR"): st.rerun()

    with col_right:
        st.markdown('<div class="post-it"><b>🍎 Menu</b></div>', unsafe_allow_html=True)
        m_list = [st.text_input(j, key=f"menu_{j}") for j in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]]
        if st.button("💾 Sauver Menu"):
            sh.worksheet("Menu").append_row([start_week.strftime("%d/%m/%Y"), user_nom] + m_list)
            st.success("Menu OK !")

# --- ONGLET 3 : ANNEE & HISTORIQUE ---
with tabs[2]:
    st.markdown("### 📅 Vue Annuelle 2026")
    for r in range(4):
        cols_an = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_an[c]:
                st.markdown(f'<div class="cal-card"><div class="p-header">{calendar.month_name[m_idx].upper()}</div><div style="text-align:center; padding:10px;">{calendar.month(2026, m_idx).split(chr(10), 1)[1].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📜 Historique du Journal")
    try:
        df_hist = pd.DataFrame(sh.worksheet("Journal").get_all_records())
        st.table(df_hist.tail(10)) # st.table est plus blanc sur iPad
    except: st.info("Historique non disponible.")

# --- ONGLET 4 : TRACKERS ---
with tabs[3]:
    st.markdown("### 📊 Mes Trackers")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        st.markdown('<div class="bujo-block"><b>🌿 BIEN-ÊTRE</b>', unsafe_allow_html=True)
        st.checkbox("Méditation"); st.checkbox("Sport"); st.checkbox("Yoga")
        st.markdown('</div>', unsafe_allow_html=True)
    with tr2:
        st.markdown('<div class="bujo-block"><b>💧 EAU</b>', unsafe_allow_html=True)
        eau = st.slider("Verres bus", 0, 12, 0)
        if st.button("Valider Eau"): st.success("Hydratation notée !")
        st.markdown('</div>', unsafe_allow_html=True)
    with tr3:
        st.markdown('<div class="bujo-block"><b>📚 LECTURE</b>', unsafe_allow_html=True)
        st.text_input("Livre en cours")
        st.number_input("Page", min_value=0)
        st.button("Mettre à jour lecture")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ONGLET 5 : COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses")
    items_pre = ["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]
    cols_c = st.columns(6)
    for i, it in enumerate(items_pre):
        if cols_c[i].button(it):
            sh.worksheet("Courses").append_row([it, user_nom]); st.rerun()
    st.divider()
    autre = st.text_input("➕ Ajouter autre chose :")
    if st.button("Ajouter à la liste"):
        if autre: sh.worksheet("Courses").append_row([autre, user_nom]); st.rerun()
    try:
        for c in sh.worksheet("Courses").get_all_records(): st.checkbox(c['Article'], key=f"check_{c['Article']}")
    except: st.write("Ta liste est vide.")

# --- ONGLET 6 : STICKERS ---
with tabs[5]:
    st.markdown("### 🎨 Ma Collection")
    st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
    if st.button("🚪 Se déconnecter"):
        st.session_state.user_data = None
        st.rerun()
