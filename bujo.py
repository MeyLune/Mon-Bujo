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

# --- 2. DESIGN & FORÇAGE COULEURS (FINI LE NOIR) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    :root {{
        --rose: #F48FB1; --rose-pale: #FFD1DC; --vert-menthe: #B2DFDB; --sapin: #1B3022;
    }}
    .stApp {{
        background: linear-gradient(135deg, rgba(255, 209, 220, 0.7), rgba(178, 223, 219, 0.7)), url("{fond_url}");
        background-size: cover; background-attachment: fixed; background-color: white !important;
    }}
    
    /* FORÇAGE TEXTE ET COULEUR CLAIRE PARTOUT */
    h1, h2, h3, p, label, .stMarkdown, span, div, .stSelectbox p {{ 
        color: var(--sapin) !important; font-family: 'Comfortaa', cursive !important;
        -webkit-text-fill-color: var(--sapin) !important;
    }}

    /* CORRECTION DES BLOCS NOIRS (UPLOAD & MULTISELECT) */
    div[data-testid="stFileUploadDropzone"], div[data-baseweb="select"] {{
        background-color: white !important;
        border: 2px solid var(--rose) !important;
        color: var(--sapin) !important;
    }}
    
    /* Boutons de suppression dans le multiselect */
    span[data-baseweb="tag"] {{
        background-color: var(--rose-pale) !important;
        color: var(--sapin) !important;
    }}

    .stButton>button {{
        background-color: var(--rose) !important; color: white !important;
        border-radius: 20px !important; border: none !important; font-weight: bold !important;
        -webkit-text-fill-color: white !important;
    }}

    .p-header {{ 
        background-color: var(--vert-menthe) !important; color: var(--sapin) !important;
        padding: 8px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; border: 1px solid var(--rose);
    }}

    .cal-box {{
        font-family: 'Courier Prime', monospace !important; background-color: white !important;
        padding: 10px; border-radius: 0 0 12px 12px; border: 1px solid var(--rose); white-space: pre;
        color: var(--sapin) !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌸 Mon Univers Quotidien</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal") or code == "2125":
            st.session_state.user_data = {"Nom": "MeyLune"}
            st.rerun()
    st.stop()

user_nom = st.session_state.user_data['Nom']
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- JOURNAL ---
with tabs[0]:
    st.markdown(f"### 🖋️ Mes pensées du {datetime.now().strftime('%d/%m/%Y')}")
    note_j = st.text_area("Écris ici...", height=300, key="journal_area")
    c1, c2 = st.columns(2)
    if c1.button("💾 Enregistrer"): st.success("Sauvegardé ! ✨")
    if c2.button("📝 Modifier"): st.info("Prêt pour l'édition.")

# --- SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    col_nav = st.columns([1, 3, 1])
    if col_nav[0].button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if col_nav[2].button("➡️"): st.session_state.w_off += 1; st.rerun()
    col_nav[1].markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]}</h3>", unsafe_allow_html=True)

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
        st.markdown('<div class="p-header">🍎 Menu</div>', unsafe_allow_html=True)
        for j in jours: st.text_input(j[:3], key=f"menu_{j}")
        st.button("💾 Sauver Menu", key="btn_menu")

# --- ANNEE ---
with tabs[2]:
    st.markdown(f"<h2 style='text-align:center;'>Calendrier 2026</h2>", unsafe_allow_html=True)
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
                st.markdown(f'<div class="cal-box">{clean_cal}</div>', unsafe_allow_html=True)

# --- TRACKERS (LECTURE) ---
with tabs[3]:
    cat = st.radio("Sélection", ["🌿 Santé", "📖 Lecture"], horizontal=True)
    if cat == "📖 Lecture":
        st.markdown("### 📚 Ma Fiche de Lecture")
        col_l1, col_l2 = st.columns([2, 1])
        with col_l1:
            st.text_input("TITRE DU LIVRE", key="t_liv")
            st.text_input("AUTEUR", key="a_liv")
            st.date_input("DÉBUT", value=datetime.now())
            st.date_input("FINI", value=datetime.now())
        with col_l2:
            st.file_uploader("Prendre une photo", type=['jpg','png','jpeg'], key="up_lecture")
        
        st.slider("NOTE / 10", 1, 10, 5)
        st.markdown("#### 🎭 Ressenti")
        cr1, cr2, cr3, cr4 = st.columns(4)
        cr1.select_slider("💧 Triste", options=[1,2,3,4,5])
        cr2.select_slider("🌶️ Spicy", options=[1,2,3,4,5])
        cr3.select_slider("🤩 Rire", options=[1,2,3,4,5])
        cr4.select_slider("❤️ Love", options=[1,2,3,4,5])
        
        st.multiselect("Sentiments", ["Coup de cœur ❤️", "À lire absolument", "Triste 😭", "Incontournable", "Décevant"], key="ms_sent")
        st.text_area("🎵 Playlist & Citations")
        st.button("💾 AJOUTER", key="btn_biblio")

# --- COURSES (AVEC DATE ET RAPPEL SEMAINE) ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses & Suivi")
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.date_input("Date prévue pour les courses", value=datetime.now(), key="date_course")
        items_def = ["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]
        st.write("Ajout rapide :")
        cols_rapides = st.columns(3)
        for i, it in enumerate(items_def):
            if cols_rapides[i % 3].button(it, key=f"c_{it}"): st.toast(f"{it} ajouté !")
        st.text_input("➕ Autre article :", key="in_course")
        st.button("Valider la liste", key="btn_course")

    with c_right:
        st.markdown('<div class="p-header" style="background-color:var(--rose)!important; color:white!important;">📅 Rappel Semaine</div>', unsafe_allow_html=True)
        # Petit rappel visuel des jours pour aider à planifier les menus/courses
        today_idx = datetime.now().weekday()
        for i, j in enumerate(jours):
            color = "#f48fb1" if i == today_idx else "#1B3022"
            st.markdown(f"<p style='margin-bottom:2px; color:{color}!important;'><b>{j}</b> : {st.session_state.get(f'menu_{j}', '...')}</p>", unsafe_allow_html=True)

# --- STICKERS ---
with tabs[5]:
    st.markdown("### 🎨 Stickers")
    up = st.file_uploader("Upload", type=['png', 'jpg'], key="up_stk_final")
    if up and st.button("Ajouter", key="btn_stk"):
        if 'stickers_perso' not in st.session_state: st.session_state.stickers_perso = []
        st.session_state.stickers_perso.append(up)
    
    if 'stickers_perso' in st.session_state:
        cols_p = st.columns(4)
        for idx, p_img in enumerate(st.session_state.stickers_perso):
            with cols_p[idx % 4]:
                st.image(p_img, width=80)
                if st.button("🗑️", key=f"d_{idx}"):
                    st.session_state.stickers_perso.pop(idx); st.rerun()
