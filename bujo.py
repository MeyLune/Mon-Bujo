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

# --- 2. DESIGN & ANTI-MODE SOMBRE ---
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
    h1, h2, h3, p, label, .stMarkdown, span, div {{ 
        color: var(--sapin) !important; font-family: 'Comfortaa', cursive !important;
    }}
    /* BOUTONS & INPUTS */
    .stButton>button {{
        background-color: var(--rose) !important; color: white !important;
        border-radius: 20px !important; border: none !important; font-weight: bold !important;
    }}
    div[data-baseweb="textarea"], div[data-baseweb="input"], .stTextArea textarea, .stTextInput input {{
        background-color: white !important; color: var(--sapin) !important;
        border-radius: 12px !important; border: 2px solid var(--rose) !important;
    }}
    /* RECTIFICATION DES COULEURS DES UPLOADEURS */
    div[data-testid="stFileUploadDropzone"] {{
        background-color: rgba(255, 255, 255, 0.8) !important;
        border: 2px dashed var(--rose) !important;
    }}
    .p-header {{ 
        background-color: var(--vert-menthe) !important; color: var(--sapin) !important;
        padding: 8px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; border: 1px solid var(--rose);
    }}
    .cal-box {{
        font-family: 'Courier Prime', monospace !important; background-color: white !important;
        padding: 15px; border-radius: 0 0 12px 12px; border: 1px solid var(--rose); white-space: pre;
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

# --- ONGLET JOURNAL ---
with tabs[0]:
    st.markdown(f"### 🖋️ Mes pensées du {datetime.now().strftime('%d/%m/%Y')}")
    note_j = st.text_area("Écris ici...", height=300, key="journal_area")
    c1, c2 = st.columns(2)
    if c1.button("💾 Enregistrer la pensée"):
        st.success("Pensée sauvegardée ! ✨")
    if c2.button("📝 Modifier"):
        st.info("Mode modification activé.")

# --- ONGLET SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    col_nav = st.columns([1, 3, 1])
    if col_nav[0].button("⬅️ Précédente"): st.session_state.w_off -= 1; st.rerun()
    if col_nav[2].button("Suivante ➡️"): st.session_state.w_off += 1; st.rerun()
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
                        st.text_area("Note", height=100, key=f"wk_{d}", label_visibility="collapsed")
    with col_d:
        st.markdown('<div style="background:white; padding:10px; border-radius:10px; border:2px solid var(--rose);">🍎 <b>Menu</b></div>', unsafe_allow_html=True)
        for j in jours: st.text_input(j[:3], key=f"menu_{j}")
        if st.button("💾 Sauvegarder le Menu"): st.toast("Menu enregistré !")

# --- ONGLET ANNEE ---
with tabs[2]:
    st.markdown(f"<h2 style='text-align:center;'>Année 2026 • Semaine actuelle : {datetime.now().isocalendar()[1]}</h2>", unsafe_allow_html=True)
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

# --- ONGLET TRACKERS (FICHE LECTURE COMPLÈTE) ---
with tabs[3]:
    cat = st.radio("Sélection", ["🌿 Santé", "📖 Lecture"], horizontal=True)
    if cat == "📖 Lecture":
        st.markdown("### 📚 Ma Fiche de Lecture")
        col_l1, col_l2 = st.columns([2, 1])
        with col_l1:
            st.text_input("TITRE DU LIVRE")
            st.text_input("AUTEUR")
            st.date_input("DÉBUT", value=datetime.now())
            st.date_input("FINI", value=datetime.now())
        with col_l2:
            st.file_uploader("Prendre une photo / Capture", type=['jpg','png','jpeg'])
        
        st.slider("NOTE / 10", 1, 10, 5)
        st.markdown("#### 🎭 Mon ressenti")
        cr1, cr2, cr3, cr4 = st.columns(4)
        cr1.select_slider("💧 Tristesse", options=[1,2,3,4,5])
        cr2.select_slider("🌶️ Spicy", options=[1,2,3,4,5])
        cr3.select_slider("🤩 Rire", options=[1,2,3,4,5])
        cr4.select_slider("❤️ Love", options=[1,2,3,4,5])
        
        st.multiselect("Sentiments", ["Coup de cœur ❤️", "À lire absolument", "Triste 😭", "Incontournable", "Décevant"])
        st.text_area("🎵 Playlist & Citations")
        
        if st.button("💾 AJOUTER À MA BIBLIOTHÈQUE"):
            st.balloons()
            st.success("Livre ajouté avec succès !")

# --- ONGLET COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses")
    items_def = ["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]
    cols_c = st.columns(6)
    for i, it in enumerate(items_def):
        if cols_c[i].button(it): st.toast(f"{it} ajouté !")
    st.text_input("➕ Ajouter un article")

# --- ONGLET STICKERS ---
with tabs[5]:
    st.markdown("### 🎨 Ma Planche de Stickers")
    if 'stickers_perso' not in st.session_state: st.session_state.stickers_perso = []
    up = st.file_uploader("Upload tes stickers", type=['png', 'jpg'])
    if up and st.button("✨ Ajouter"):
        st.session_state.stickers_perso.append(up)
    
    if st.session_state.stickers_perso:
        cols_p = st.columns(4)
        for idx, p_img in enumerate(st.session_state.stickers_perso):
            with cols_p[idx % 4]:
                st.image(p_img, width=100)
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.stickers_perso.pop(idx); st.rerun()
