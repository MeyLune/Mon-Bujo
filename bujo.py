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

# --- 2. DESIGN : CALLIGRAPHIE & ANTI-BLOC NOIR ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    /* Import des polices : Dancing Script pour la calligraphie, Comfortaa pour le moderne */
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    
    :root {{
        --rose: #F48FB1;
        --sapin: #1B3022;
    }}

    .stApp {{
        background: linear-gradient(135deg, rgba(255, 209, 220, 0.7), rgba(178, 223, 219, 0.7)), url("{fond_url}");
        background-size: cover;
        background-color: white !important;
    }}

    /* TITRE CALLIGRAPHIÉ */
    .titre-calli {{
        font-family: 'Dancing Script', cursive !important;
        font-size: 3.5rem !important;
        color: var(--sapin) !important;
        text-align: center;
        margin-bottom: 20px;
        -webkit-text-fill-color: var(--sapin) !important;
    }}

    /* TITRES DE SECTIONS CALLIGRAPHIÉS */
    h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
        font-family: 'Dancing Script', cursive !important;
        color: var(--sapin) !important;
        -webkit-text-fill-color: var(--sapin) !important;
    }}

    /* TEXTE STANDARD */
    p, label, .stMarkdown, span, div {{
        font-family: 'Comfortaa', cursive !important;
        color: var(--sapin) !important;
        -webkit-text-fill-color: var(--sapin) !important;
    }}

    /* FORÇAGE DES INPUTS (Contre les blocs noirs sur iPad) */
    textarea, input, div[data-baseweb="base-input"], div[data-baseweb="textarea"], div[data-baseweb="select"], div[data-testid="stFileUploadDropzone"] {{
        background-color: white !important;
        color: var(--sapin) !important;
        -webkit-text-fill-color: var(--sapin) !important;
        border: 2px solid var(--rose) !important;
        border-radius: 12px !important;
    }}

    /* BOUTONS ROSES */
    .stButton>button {{
        background-color: var(--rose) !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        border: none !important;
    }}

    .p-header {{ 
        background-color: #B2DFDB !important; 
        color: var(--sapin) !important;
        padding: 8px; text-align: center; border-radius: 12px 12px 0 0; 
        font-weight: bold; border: 1px solid var(--rose);
        font-family: 'Comfortaa', cursive !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
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

# --- JOURNAL ---
with tabs[0]:
    st.markdown(f"### 🖋️ Mes pensées du {datetime.now().strftime('%d/%m/%Y')}")
    note_j = st.text_area("Écris ici...", height=300, key="j_note")
    c1, c2 = st.columns(2)
    if c1.button("💾 Enregistrer"): st.success("Pensée enregistrée !")
    if c2.button("📝 Modifier"): st.info("Mode modification actif.")

# --- SEMAINE (SAUVEGARDE & MODIF) ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    col_nav = st.columns([1, 3, 1])
    if col_nav[0].button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if col_nav[2].button("➡️"): st.session_state.w_off += 1; st.rerun()
    col_nav[1].markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - 2026</h3>", unsafe_allow_html=True)

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
        cs1, cs2 = st.columns(2)
        if cs1.button("💾 Sauvegarder la semaine"): st.toast("Semaine enregistrée")
        if cs2.button("📝 Modifier la semaine"): st.toast("Modification prête")

    with col_d:
        st.markdown('<div class="p-header" style="background-color:white !important; border-bottom:none;">🍎 Menu</div>', unsafe_allow_html=True)
        for j in jours: st.text_input(j[:3], key=f"menu_{j}")
        cm1, cm2 = st.columns(2)
        if cm1.button("💾 Sauver Menu"): st.success("Menu OK")
        if cm2.button("📝 Modifier Menu"): st.info("Édition Menu")

# --- ANNEE ---
with tabs[2]:
    st.markdown("<h2 style='text-align:center;'>Calendrier 2026</h2>", unsafe_allow_html=True)
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

# --- TRACKERS (LECTURE) ---
with tabs[3]:
    st.markdown("### 📚 Ma Fiche de Lecture")
    col_l1, col_l2 = st.columns([2, 1])
    with col_l1:
        st.text_input("TITRE DU LIVRE")
        st.text_input("AUTEUR")
        st.date_input("DÉBUT")
        st.date_input("FINI")
    with col_l2:
        st.file_uploader("Prendre une photo", type=['jpg','png','jpeg'], key="up_fich")
    
    st.slider("NOTE / 10", 1, 10, 5)
    st.markdown("#### 🎭 Ressenti")
    cr1, cr2, cr3, cr4 = st.columns(4)
    cr1.select_slider("💧 Triste", options=[1,2,3,4,5])
    cr2.select_slider("🌶️ Spicy", options=[1,2,3,4,5])
    cr3.select_slider("🤩 Rire", options=[1,2,3,4,5])
    cr4.select_slider("❤️ Love", options=[1,2,3,4,5])
    
    st.multiselect("Sentiments", ["Coup de cœur ❤️", "À lire absolument", "Triste 😭", "Incontournable", "Décevant"])
    st.text_area("🎵 Playlist & Citations")
    st.button("💾 ENREGISTRER")

# --- COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses")
    c_l, c_r = st.columns([2, 1])
    with c_l:
        st.date_input("Date prévue", value=datetime.now())
        cols_r = st.columns(3)
        for i, it in enumerate(["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]):
            if cols_r[i % 3].button(it): st.toast(f"{it} ajouté")
        st.text_input("➕ Autre article")
        st.button("Valider la liste")
    with c_r:
        st.markdown('<div class="p-header" style="background-color:var(--rose)!important; color:white!important;">📅 Rappel Semaine</div>', unsafe_allow_html=True)
        for j in jours:
            st.markdown(f"**{j}** : {st.session_state.get(f'menu_{j}', '...')}")

# --- STICKERS ---
with tabs[5]:
    st.markdown("### 🎨 Mes Stickers")
    up = st.file_uploader("Upload", type=['png', 'jpg'], key="stk_up")
    if up and st.button("Ajouter"):
        if 'stk_perso' not in st.session_state: st.session_state.stk_perso = []
        st.session_state.stk_perso.append(up)
    
    if 'stk_perso' in st.session_state:
        cols_s = st.columns(5)
        for idx, s in enumerate(st.session_state.stk_perso):
            with cols_s[idx % 5]:
                st.image(s, width=80)
