import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import calendar

# --- 1. CONNEXION GOOGLE SHEETS ---
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
    except Exception: return None

sh = init_connection()

def save_to_gsheet(worksheet_name, data_row):
    try:
        ws = sh.worksheet(worksheet_name)
        ws.append_row(data_row)
    except: pass

def load_from_gsheet(worksheet_name):
    try:
        ws = sh.worksheet(worksheet_name)
        return ws.get_all_records()
    except: return []

# --- 2. DESIGN & POLICES (RESTAURÉS) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    
    :root {{
        --rose: #F48FB1;
        --sapin: #1B3022;
        --or: #D4AF37;
        --vert-pale: #B2DFDB;
    }}

    .stApp {{
        background: linear-gradient(135deg, rgba(255, 209, 220, 0.7), rgba(178, 223, 219, 0.7)), url("{fond_url}");
        background-size: cover; background-attachment: fixed; background-color: white !important;
    }}

    .titre-calli {{
        font-family: 'Dancing Script', cursive !important; font-size: 3.5rem !important;
        color: var(--sapin) !important; text-align: center; -webkit-text-fill-color: var(--sapin) !important;
    }}
    
    .sous-titre-calli {{
        font-family: 'Dancing Script', cursive !important; font-size: 2.2rem !important;
        color: var(--sapin) !important; -webkit-text-fill-color: var(--sapin) !important;
    }}

    p, label, .stMarkdown, span, div, .stCheckbox {{
        font-family: 'Comfortaa', cursive !important; color: var(--sapin) !important;
    }}

    /* Correction iPad pour les champs de saisie sans perdre le style */
    textarea, input {{
        background-color: white !important; color: var(--sapin) !important;
        border: 2px solid var(--rose) !important; border-radius: 12px !important;
        -webkit-text-fill-color: var(--sapin) !important;
    }}

    .stButton>button {{
        background-color: var(--rose) !important; color: white !important;
        border-radius: 20px !important; font-weight: bold !important; border: none !important;
    }}

    .post-it {{
        padding: 15px; border-radius: 15px; margin-bottom: 5px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        border-left: 10px solid var(--rose);
    }}

    .p-header {{ 
        background-color: var(--vert-pale) !important; color: var(--sapin) !important;
        padding: 8px; text-align: center; border-radius: 12px 12px 0 0; 
        font-weight: bold; border: 1px solid var(--rose);
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. INITIALISATION ---
if 'j_ver' not in st.session_state: st.session_state.j_ver = 0
if 'g_ver' not in st.session_state: st.session_state.g_ver = 0
if 'w_off' not in st.session_state: st.session_state.w_off = 0
if 'shopping_list' not in st.session_state: st.session_state.shopping_list = []

# --- LOGIN ---
if "user_data" not in st.session_state:
    st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal") or code == "2125":
            st.session_state.user_data = {"Nom": "MeyLune"}; st.rerun()
    st.stop()

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ✍️ JOURNAL ---
with tabs[0]:
    col1, col2 = st.columns(2)
    journal_entries = load_from_gsheet("Journal")
    gratitude_entries = load_from_gsheet("Gratitude")

    with col1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        new_j = st.text_area("...", height=150, key=f"j_{st.session_state.j_ver}", label_visibility="collapsed")
        if st.button("💾 Enregistrer la pensée"):
            if new_j:
                save_to_gsheet("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), new_j])
                st.session_state.j_ver += 1; st.rerun()
        for e in reversed(journal_entries):
            st.markdown(f'<div class="post-it" style="background-color: rgba(255,209,220,0.6);"><small>{e.get("Date")}</small><br>{e.get("Texte")}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        new_g = st.text_area("...", height=150, key=f"g_{st.session_state.g_ver}", label_visibility="collapsed")
        if st.button("🙏 Enregistrer ma gratitude"):
            if new_g:
                save_to_gsheet("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), new_g])
                st.session_state.g_ver += 1; st.rerun()
        for e in reversed(gratitude_entries):
            st.markdown(f'<div class="post-it" style="background-color: white; border-left-color: var(--or);"><small>{e.get("Date")}</small><br><i>{e.get("Texte")}</i></div>', unsafe_allow_html=True)

# --- 🗓️ SEMAINE ---
with tabs[1]:
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    c_nav = st.columns([1, 3, 1])
    if c_nav[0].button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c_nav[2].button("➡️"): st.session_state.w_off += 1; st.rerun()
    c_nav[1].markdown(f'<div class="sous-titre-calli" style="text-align:center;">Semaine {start_week.isocalendar()[1]}</div>', unsafe_allow_html=True)
    
    cg, cd = st.columns([3, 1.2])
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    with cg:
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for k in range(2):
                if (i+k) < 7:
                    d = start_week + timedelta(days=i+k)
                    with cols[k]:
                        st.markdown(f'<div class="p-header">{jours[i+k]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        st.text_area("", height=100, key=f"wk_{d}", label_visibility="collapsed")
        st.button("💾 Sauvegarder la semaine", key="save_w")
    with cd:
        st.markdown('<div class="p-header" style="background-color:white !important;">🍎 Menu</div>', unsafe_allow_html=True)
        for j in jours: st.text_input(j[:3], key=f"menu_{j}")
        st.button("💾 Sauver Menu", key="save_m")

# --- 📅 ANNEE ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                st.markdown(f'<div class="p-header" style="background-color:var(--rose)!important; color:white!important;">{mois_fr[m_idx-1].upper()}</div>', unsafe_allow_html=True)
                tc = calendar.TextCalendar(firstweekday=0)
                cal_str = tc.formatmonth(2026, m_idx)
                clean_cal = "Lu Ma Me Je Ve Sa Di\n" + "\n".join(cal_str.splitlines()[2:])
                st.markdown(f'<div style="font-family:\'Courier Prime\'; background:white; padding:10px; border:1px solid var(--rose); border-radius:0 0 12px 12px; white-space:pre; text-align:center;">{clean_cal}</div>', unsafe_allow_html=True)

# --- 📊 TRACKERS ---
with tabs[3]:
    st.markdown('<div class="sous-titre-calli">📚 Ma Fiche de Lecture</div>', unsafe_allow_html=True)
    tl1, tl2 = st.columns([2, 1])
    with tl1:
        st.text_input("TITRE DU LIVRE"); st.text_input("AUTEUR")
        st.date_input("DÉBUT LECTURE", key="bk_d"); st.date_input("FIN LECTURE", key="bk_f")
    with tl2: st.file_uploader("Couverture", type=['jpg','png'], key="bk_img")
    st.slider("NOTE / 10", 1, 10, 5)
    st.markdown("#### Mon Ressenti")
    tr1, tr2, tr3, tr4 = st.columns(4)
    tr1.select_slider("💧 Triste", options=[1,2,3,4,5], key="r1")
    tr2.select_slider("🌶️ Spicy", options=[1,2,3,4,5], key="r2")
    tr3.select_slider("🤩 Rire", options=[1,2,3,4,5], key="r3")
    tr4.select_slider("❤️ Love", options=[1,2,3,4,5], key="r4")
    st.button("💾 ENREGISTRER LECTURE")

# --- 🛒 COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    cl, cr = st.columns([2, 1.2])
    with cl:
        it = st.text_input("Ajouter un article", key="c_add")
        if st.button("Ajouter"):
            if it: st.session_state.shopping_list.append(it); st.rerun()
    with cr:
        st.markdown('<div class="p-header" style="background-color:var(--rose)!important; color:white!important;">📝 Ma Liste</div>', unsafe_allow_html=True)
        for i, item in enumerate(st.session_state.shopping_list):
            c1, c2 = st.columns([4, 1])
            c1.checkbox(item, key=f"c_it_{i}")
            if c2.button("🗑️", key=f"c_del_{i}"): st.session_state.shopping_list.pop(i); st.rerun()

# --- 🎨 STICKERS ---
with tabs[5]:
    st.markdown('<div class="sous-titre-calli">🎨 Mes Stickers</div>', unsafe_allow_html=True)
    st.write("Section prête pour tes PNG !")
