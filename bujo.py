import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
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

# --- 2. DESIGN : CALLIGRAPHIE & POST-ITS ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    
    :root {{
        --rose: #F48FB1;
        --sapin: #1B3022;
        --or: #D4AF37;
    }}

    .stApp {{
        background: linear-gradient(135deg, rgba(255, 209, 220, 0.7), rgba(178, 223, 219, 0.7)), url("{fond_url}");
        background-size: cover;
        background-attachment: fixed;
        background-color: white !important;
    }}

    .titre-calli {{
        font-family: 'Dancing Script', cursive !important;
        font-size: 3.5rem !important;
        color: var(--sapin) !important;
        text-align: center;
        -webkit-text-fill-color: var(--sapin) !important;
    }}
    
    .sous-titre-calli {{
        font-family: 'Dancing Script', cursive !important;
        font-size: 2.2rem !important;
        color: var(--sapin) !important;
        -webkit-text-fill-color: var(--sapin) !important;
        margin-top: 10px;
        margin-bottom: 10px;
    }}

    p, label, .stMarkdown, span, div {{
        font-family: 'Comfortaa', cursive !important;
        color: var(--sapin) !important;
        -webkit-text-fill-color: var(--sapin) !important;
    }}

    textarea, input, div[data-baseweb="base-input"], div[data-baseweb="textarea"], div[data-baseweb="select"], div[data-testid="stFileUploadDropzone"] {{
        background-color: white !important;
        color: var(--sapin) !important;
        border: 2px solid var(--rose) !important;
        border-radius: 12px !important;
    }}

    .stButton>button {{
        background-color: var(--rose) !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        border: none !important;
    }}

    .post-it {{
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 5px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }}

    .p-header {{ 
        background-color: #B2DFDB !important; 
        color: var(--sapin) !important;
        padding: 8px; text-align: center; border-radius: 12px 12px 0 0; 
        font-weight: bold; border: 1px solid var(--rose);
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN & TITRE ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal") or code == "2125":
            st.session_state.user_data = {"Nom": "MeyLune"}
            st.rerun()
    st.stop()

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ONGLET JOURNAL ---
with tabs[0]:
    col_j1, col_j2 = st.columns(2)
    
    with col_j1:
        st.markdown(f'<div class="sous-titre-calli">🖋️ Mes pensées du {datetime.now().strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
        # Saisie Pensées
        if 'input_pensee' not in st.session_state: st.session_state.input_pensee = ""
        
        def save_pensee():
            txt = st.session_state.temp_p_input
            if txt:
                if 'list_pensees' not in st.session_state: st.session_state.list_pensees = []
                st.session_state.list_pensees.insert(0, {"text": txt, "date": datetime.now().strftime("%H:%M")})
                st.session_state.input_pensee = "" # Vide le texte après
                st.toast("Pensée épinglée ! ✨")

        st.text_area("Libère ton esprit...", height=150, key="temp_p_input", label_visibility="collapsed")
        st.button("💾 Enregistrer la pensée", on_click=save_pensee)
        
        st.markdown("---")
        # Affichage Pensées
        if 'list_pensees' in st.session_state:
            for idx, entry in enumerate(st.session_state.list_pensees):
                bg = "rgba(255, 209, 220, 0.6)" if idx % 2 == 0 else "rgba(178, 223, 219, 0.6)"
                border = "#F48FB1" if idx % 2 == 0 else "#80CBC4"
                st.markdown(f'<div class="post-it" style="background-color: {bg}; border-left: 10px solid {border};"><small>{entry["date"]}</small><br>{entry["text"]}</div>', unsafe_allow_html=True)
                c_mod, _ = st.columns([1, 4])
                c_mod.button("Modifier", key=f"mp_{idx}", help="Petit bouton de modif")

    with col_j2:
        st.markdown(f'<div class="sous-titre-calli">✨ Gratitude pour aujourd\'hui</div>', unsafe_allow_html=True)
        # Saisie Gratitude
        def save_gratitude():
            txt = st.session_state.temp_g_input
            if txt:
                if 'list_gratitudes' not in st.session_state: st.session_state.list_gratitudes = []
                st.session_state.list_gratitudes.insert(0, {"text": txt, "date": datetime.now().strftime("%H:%M")})
                st.toast("Gratitude enregistrée ! 🌟")

        st.text_area("Aujourd'hui, je remercie pour...", height=150, key="temp_g_input", label_visibility="collapsed")
        st.button("🙏 Enregistrer ma gratitude", on_click=save_gratitude)

        st.markdown("---")
        # Affichage Gratitudes
        if 'list_gratitudes' in st.session_state:
            for idx, entry in enumerate(st.session_state.list_gratitudes):
                st.markdown(f'<div class="post-it" style="background-color: white; border-left: 10px solid var(--or);"><small>{entry["date"]}</small><br><i>{entry["text"]}</i></div>', unsafe_allow_html=True)
                c_mod, _ = st.columns([1, 4])
                c_mod.button("Modifier", key=f"mg_{idx}")

# --- ONGLET SEMAINE --- (Identique avec titres calligraphiés)
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    col_nav = st.columns([1, 3, 1])
    if col_nav[0].button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if col_nav[2].button("➡️"): st.session_state.w_off += 1; st.rerun()
    col_nav[1].markdown(f'<div class="sous-titre-calli" style="text-align:center;">Semaine {start_week.isocalendar()[1]} - 2026</div>', unsafe_allow_html=True)

    col_g, col_d = st.columns([3, 1.2])
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    with col_g:
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for k in range(2):
                if (i+k) < 7:
                    d = start_week + timedelta(days=i+k)
                    with cols[k]:
                        st.markdown(f'<div class="p-header">{jours[i+k]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        st.text_area("", height=100, key=f"wk_{d}", label_visibility="collapsed")

    with col_d:
        st.markdown('<div class="p-header" style="background-color:white !important;">🍎 Menu</div>', unsafe_allow_html=True)
        for j in jours: st.text_input(j[:3], key=f"menu_{j}")
        st.button("💾 Sauver Menu")

# --- ONGLET ANNEE ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier Annuel 2026</div>', unsafe_allow_html=True)
    mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                tc = calendar.TextCalendar(firstweekday=0)
                cal_str = tc.formatmonth(2026, m_idx)
                clean_cal = "Lu Ma Me Je Ve Sa Di\n" + "\n".join(cal_str.splitlines()[2:])
                st.markdown(f'<div class="p-header" style="background-color:var(--rose)!important; color:white!important;">{mois_fr[m_idx-1].upper()}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-family:\'Courier Prime\'; background:white; padding:10px; border:1px solid var(--rose); border-radius:0 0 12px 12px; white-space:pre; text-align:center;">{clean_cal}</div>', unsafe_allow_html=True)

# --- ONGLET TRACKERS ---
with tabs[3]:
    st.markdown('<div class="sous-titre-calli">📚 Ma Fiche de Lecture</div>', unsafe_allow_html=True)
    col_l1, col_l2 = st.columns([2, 1])
    with col_l1:
        st.text_input("TITRE DU LIVRE")
        st.text_input("AUTEUR")
        st.date_input("DÉBUT")
    with col_l2:
        st.file_uploader("Capture couverture", type=['jpg','png','jpeg'])
    st.slider("NOTE / 10", 1, 10, 5)
    st.button("💾 ENREGISTRER")

# --- ONGLET COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    c_l, c_r = st.columns([2, 1])
    with c_l:
        st.date_input("Date prévue", value=datetime.now())
        st.text_input("➕ Ajouter article")
        st.button("Valider la liste")
    with c_r:
        st.markdown('<div class="p-header" style="background-color:var(--rose)!important; color:white!important;">📅 Rappel Semaine</div>', unsafe_allow_html=True)
        for j in jours:
            st.markdown(f"**{j}** : {st.session_state.get(f'menu_{j}', '...')}")

# --- ONGLET STICKERS ---
with tabs[5]:
    st.markdown('<div class="sous-titre-calli">🎨 Mes Stickers</div>', unsafe_allow_html=True)
    up = st.file_uploader("Upload", type=['png', 'jpg'], key="up_s")
    if up: st.image(up, width=100)
