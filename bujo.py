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

# --- 2. DESIGN : ROSE PASTEL -> VERT D'EAU (ANTI-MODE SOMBRE) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    
    :root {{
        --rose-pastel: #FFD1DC;
        --vert-eau: #E0F2F1;
        --sapin: #1B3022;
        --vieux-rose: #F48FB1;
        --mint-clair: #B2DFDB;
    }}

    .stApp {{
        background: linear-gradient(135deg, rgba(255, 209, 220, 0.8), rgba(178, 223, 219, 0.8)), url("{fond_url}");
        background-size: cover;
        background-attachment: fixed;
        background-color: white !important;
    }}

    /* FORÇAGE DU TEXTE SOMBRE (iPad Fix) */
    h1, h2, h3, h4, p, label, .stMarkdown, span, div {{ 
        color: var(--sapin) !important; 
        font-family: 'Comfortaa', cursive !important;
        -webkit-text-fill-color: var(--sapin) !important;
    }}

    /* BOUTONS ROSES HARMONIEUX */
    .stButton>button {{
        background-color: var(--vieux-rose) !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: bold !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}

    /* INPUTS BLANCS NETS */
    div[data-baseweb="textarea"], div[data-baseweb="input"], 
    .stTextArea textarea, .stTextInput input, .stSelectbox div {{
        background-color: white !important;
        color: var(--sapin) !important;
        -webkit-text-fill-color: var(--sapin) !important;
        border-radius: 12px !important;
        border: 2px solid var(--vieux-rose) !important;
    }}

    /* CALENDRIER MONOSPACE */
    .p-header {{ 
        background-color: var(--vieux-rose) !important; 
        color: white !important; 
        -webkit-text-fill-color: white !important;
        padding: 8px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold;
    }}

    .cal-box {{
        font-family: 'Courier Prime', monospace !important;
        background-color: white !important;
        padding: 15px; border-radius: 0 0 12px 12px;
        color: var(--sapin) !important;
        -webkit-text-fill-color: var(--sapin) !important;
        white-space: pre; display: flex; justify-content: center;
        border: 1px solid var(--vieux-rose);
    }}

    /* DESIGN ONGLETS */
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; background-color: transparent !important; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.4) !important;
        color: var(--sapin) !important;
        border-radius: 10px 10px 0 0 !important;
        padding: 10px 20px !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: white !important;
        border-bottom: 3px solid var(--vieux-rose) !important;
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
    st.markdown(f"### 🖋️ Mes Pensées du {datetime.now().strftime('%d/%m/%Y')}")
    note_j = st.text_area("Note du jour...", height=300, label_visibility="collapsed")
    if st.button("💾 Sauvegarder la pensée"):
        if sh: sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), user_nom, note_j])
        st.success("Enregistré dans tes archives ! ✨")

# --- ONGLET SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - 2026</h3>", unsafe_allow_html=True)

    col_g, col_d = st.columns([3, 1.2])
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    with col_g:
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for k in range(2):
                if (i+k) < 7:
                    d = start_week + timedelta(days=i+k)
                    with cols[k]:
                        st.markdown(f'<div class="p-header" style="background-color:var(--mint-clair) !important;">{jours[i+k]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        st.text_area("", height=100, key=f"wk_note_{d}", label_visibility="collapsed")
    with col_d:
        st.markdown('<div style="background:white; padding:15px; border-radius:10px; border:2px solid var(--vieux-rose);">🍎 <b>Menu</b></div>', unsafe_allow_html=True)
        for j in jours: st.text_input(j[:3], key=f"menu_{j}")

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
                st.markdown(f'<div class="p-header">{mois_fr[m_idx-1].upper()}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="cal-box">{clean_cal}</div>', unsafe_allow_html=True)

# --- ONGLET TRACKERS (LECTURE) ---
with tabs[3]:
    cat = st.radio("Sélection", ["🌿 Santé", "📖 Lecture"], horizontal=True)
    if cat == "📖 Lecture":
        st.markdown('<div style="background:white; padding:20px; border-radius:15px; border:2px solid var(--mint-clair);">', unsafe_allow_html=True)
        st.subheader("📖 Ma Fiche de Lecture")
        tl, al = st.columns(2)
        titre_livre = tl.text_input("Titre du livre")
        auteur_livre = al.text_input("Auteur")
        img_l = st.file_uploader("Couverture", type=['jpg','png','jpeg'])
        if img_l: st.image(img_l, width=120)
        
        c_res = st.columns(4)
        c_res[0].select_slider("💧", options=[1,2,3,4,5], key="r1")
        c_res[1].select_slider("🌶️", options=[1,2,3,4,5], key="r2")
        c_res[2].select_slider("😊", options=[1,2,3,4,5], key="r3")
        c_res[3].select_slider("❤️", options=[1,2,3,4,5], key="r4")
        if st.button("📥 Enregistrer le livre"):
            if sh and titre_livre:
                sh.worksheet("Lectures").append_row([titre_livre, auteur_livre, datetime.now().strftime("%d/%m/%Y")])
                st.success("Livre ajouté à ta bibliothèque !")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.slider("💧 Verres d'eau", 0, 10, 5)

# --- ONGLET COURSES ---
with tabs[4]:
    st.markdown("### 🛒 Liste de Courses")
    items_def = ["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]
    cols_c = st.columns(6)
    for i, it in enumerate(items_def):
        if cols_c[i].button(it):
            if sh: sh.worksheet("Courses").append_row([it, user_nom]); st.rerun()
    
    st.markdown("---")
    autre_item = st.text_input("➕ Ajouter manuellement :")
    if st.button("Ajouter à la liste"):
        if sh and autre_item:
            sh.worksheet("Courses").append_row([autre_item, user_nom]); st.rerun()

# --- ONGLET STICKERS (AVEC UPLOAD PERSO) ---
with tabs[5]:
    st.markdown("### 🎨 Ma Planche de Stickers")
    stks_emo = ["🌸", "🌿", "⭐", "🍃", "🍎", "🥑", "📅", "✨", "🎀", "🍪"]
    cols_s = st.columns(5)
    for i, s in enumerate(stks_emo):
        if cols_s[i % 5].button(s, key=f"s_btn_{i}"): st.balloons()

    st.markdown("---")
    st.markdown("#### 📥 Tes propres stickers")
    if 'stickers_perso' not in st.session_state: st.session_state.stickers_perso = []
    
    up_stk = st.file_uploader("Choisis une image", type=['png', 'jpg'], key="up_stk")
    if up_stk and st.button("✨ Ajouter à la planche"):
        st.session_state.stickers_perso.append(up_stk)
        st.success("Sticker ajouté !")

    if st.session_state.stickers_perso:
        cols_p = st.columns(4)
        for idx, p_img in enumerate(st.session_state.stickers_perso):
            with cols_p[idx % 4]:
                st.image(p_img, width=100)
                if st.button("🗑️", key=f"del_stk_{idx}"):
                    st.session_state.stickers_perso.pop(idx)
                    st.rerun()
