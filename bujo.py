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

# --- 2. STYLE ET FORÇAGE MODE CLAIR ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-color: white !important;
    }}

    /* Fix iPad et zones de texte */
    div[data-baseweb="textarea"], div[data-baseweb="input"], 
    .stTextArea textarea, .stTextInput input, .stNumberInput input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1b5e20 !important;
        border-radius: 12px !important;
        border: 1px solid #f06292 !important;
        -webkit-text-fill-color: #1b5e20 !important;
    }}

    .stTabs, .bujo-block, .cal-card {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #c8e6c9;
    }}

    h1, h2, h3, p, label, .stMarkdown {{ color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }}
    
    .stButton>button {{ 
        background-color: #f06292 !important; color: white !important;
        border-radius: 25px !important; border: none !important;
        font-weight: bold !important; width: 100%;
    }}

    .p-header {{ background-color: #f06292 !important; color: white !important; padding: 10px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; }}
    .post-it {{ background: rgba(255, 249, 196, 0.95); padding: 15px; border-left: 6px solid #fbc02d; font-family: 'Indie Flower', cursive; color: #5d4037 !important; border-radius: 5px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 Mon Bullet Journal</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal") or (code == "2125"):
            if code == "2125":
                st.session_state.user_data = {"Nom": "MeyLune", "Acces": "OUI"}
                st.rerun()
            elif sh:
                try:
                    users = sh.worksheet("Utilisateurs").get_all_records()
                    for u in users:
                        if str(u['Code']) == str(code):
                            st.session_state.user_data = {"Nom": u['Nom'], "Acces": u['Accès Journal']}
                            st.rerun()
                except: st.error("Connexion base de données impossible.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
user_nom = st.session_state.user_data['Nom']
tabs = st.tabs(["🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS", "✍️ JOURNAL"])

# --- ONGLET SEMAINE (Restauré et Flexible) ---
with tabs[0]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    now = datetime.now()
    start_week = (now.date() - timedelta(days=now.weekday())) + timedelta(weeks=st.session_state.w_off)
    
    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    if col_nav1.button("⬅️ Semaine Précédente"): st.session_state.w_off -= 1; st.rerun()
    if col_nav3.button("Semaine Suivante ➡️"): st.session_state.w_off += 1; st.rerun()
    
    mois_fr_list = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    titre_semaine = f"Semaine {start_week.isocalendar()[1]} - {mois_fr_list[start_week.month-1]} {start_week.year}"
    col_nav2.markdown(f"<h3 style='text-align:center;'>{titre_semaine}</h3>", unsafe_allow_html=True)

    col_g, col_d = st.columns([3, 1.2])
    sem_notes = {}
    jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    with col_g:
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    d = start_week + timedelta(days=i+j)
                    d_str = d.strftime("%d/%m/%Y")
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{jours_fr[i+j]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        sem_notes[d_str] = st.text_area("Note", height=100, key=f"wk_{d_str}", label_visibility="collapsed")
        
        if st.button("💾 SAUVEGARDER TOUTE LA SEMAINE"):
            if sh:
                for dk, txt in sem_notes.items():
                    if txt.strip(): sh.worksheet("Note").append_row([dk, user_nom, txt])
                st.success("Semaine enregistrée ! ✨")

    with col_d:
        st.markdown('<div class="post-it"><b>🍎 Menu</b></div>', unsafe_allow_html=True)
        m_vals = [st.text_input(j[:3], key=f"m_{j}") for j in jours_fr]
        if st.button("💾 Sauver Menu"):
            if sh: sh.worksheet("Menu").append_row([start_week.strftime("%d/%m/%Y"), user_nom] + m_vals)
            st.success("Menu sauvegardé !")

# --- ONGLET ANNEE (Français & Aligné) ---
with tabs[1]:
    st.markdown("<h2 style='text-align:center;'>Calendrier Annuel 2026</h2>", unsafe_allow_html=True)
    jours_tete = "Lu Ma Me Je Ve Sa Di"
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                # On génère le calendrier pour le mois
                cal_raw = calendar.TextCalendar(firstweekday=0).formatmonth(2026, m_idx)
                cal_lines = cal_raw.splitlines()[2:] # On enlève les titres anglais
                corps_cal = "<br>".join(cal_lines)
                st.markdown(f"""
                <div class="cal-card">
                    <div class="p-header">{mois_fr_list[m_idx-1].upper()}</div>
                    <div style="text-align:center; font-family:monospace; font-size:16px; color:black; line-height:1.5;">
                        <b style="color:#f06292;">{jours_tete}</b><br>{corps_cal}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- ONGLET TRACKERS (Santé & Lecture) ---
with tabs[2]:
    cat = st.radio("Choisir catégorie", ["🌿 Santé", "📖 Lecture"], horizontal=True)
    if cat == "🌿 Santé":
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        st.slider("💧 Verres d'eau", 0, 12, 6)
        st.slider("😴 Sommeil (heures)", 0, 12, 8)
        st.checkbox("🏃 Séance de sport faite")
        st.button("Sauvegarder Santé")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        st.subheader("📚 Ma Fiche de Lecture")
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.text_input("Titre du livre")
            st.text_input("Auteur")
            st.date_input("Date de début")
        with col_l2:
            st.file_uploader("Prendre une photo / Capture", type=['jpg', 'png'])
            st.select_slider("Ma note", options=["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"])
        
        st.write("💭 Sentiments :")
        s_cols = st.columns(2)
        s_cols[0].checkbox("Coup de cœur ❤️")
        s_cols[1].checkbox("À lire absolument")
        st.text_area("Notes / Citations / Playlist")
        st.button("Ajouter à ma bibliothèque")
        st.markdown('</div>', unsafe_allow_html=True)

# --- COURSES ---
with tabs[3]:
    st.markdown("### 🛒 Ma Liste")
    items_def = ["Lait", "Oeufs", "Pain", "Fruits", "Légumes", "Eau"]
    cols_c = st.columns(6)
    for i, it in enumerate(items_def):
        if cols_c[i].button(it):
            if sh: sh.worksheet("Courses").append_row([it, user_nom]); st.rerun()
    autre = st.text_input("➕ Ajouter autre chose :")
    if st.button("Ajouter"):
        if sh: sh.worksheet("Courses").append_row([autre, user_nom]); st.rerun()

# --- STICKERS ---
with tabs[4]:
    st.markdown("### 🎨 Planche Stickers")
    st.write("Clique sur un sticker pour décorer virtuellement (effet ballons) !")
    stickers = ["🌸", "🌿", "⭐", "🍃", "🍎", "🥑", "📅", "✨", "🎀", "🍪"]
    cols_s = st.columns(5)
    for i, s in enumerate(stickers):
        if cols_s[i % 5].button(s, key=f"st_{i}"): st.balloons()

# --- JOURNAL ---
with tabs[5]:
    if st.session_state.user_data['Acces'] == "OUI":
        st.markdown(f"### ✍️ Mes pensées du {now.strftime('%d/%m/%Y')}")
        note_p = st.text_area("", height=250, key="journal_note", label_visibility="collapsed")
        if st.button("Enregistrer Pensée"):
            if sh and note_p: sh.worksheet("Journal").append_row([now.strftime("%d/%m/%Y"), user_nom, note_p]); st.success("Sauvé !")
