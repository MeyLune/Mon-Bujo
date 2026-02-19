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

# --- 2. STYLE GLOBAL (FOND FLEURI + FIX COULEURS) ---
st.set_page_config(page_title="Mon Bullet Journal", layout="wide", initial_sidebar_state="collapsed")

# URL avec %20 pour l'espace dans le nom du fichier
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    .stApp {{
        background-image: url("{fond_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* FIX DES ZONES NOIRES (Inputs et Tableaux) */
    div[data-baseweb="textarea"], div[data-baseweb="input"], div[data-baseweb="select"],
    .stTextArea textarea, .stTextInput input, .stNumberInput input, 
    [data-testid="stDataFrame"] {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1b5e20 !important;
        border-radius: 12px !important;
        border: 1px solid #f06292 !important;
    }}

    /* Style des onglets et blocs */
    .stTabs, .bujo-block, .cal-card {{
        background-color: rgba(255, 255, 255, 0.85) !important;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #c8e6c9;
    }}

    h1, h2, h3, p, label, .stMarkdown {{ color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }}
    
    /* Boutons Roses */
    .stButton>button {{ 
        background-color: #f06292 !important; color: white !important;
        border-radius: 25px !important; border: none !important;
        padding: 10px 20px !important; font-weight: bold !important; width: 100%;
    }}

    .p-header {{ background-color: #f06292 !important; color: white !important; padding: 10px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; }}
    .post-it {{ background: rgba(255, 249, 196, 0.95); padding: 15px; border-left: 6px solid #fbc02d; font-family: 'Indie Flower', cursive; color: #5d4037 !important; border-radius: 5px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None

if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center; background:rgba(255,255,255,0.8); padding:20px; border-radius:20px;'>🌿 Mon Bullet Journal</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        input_code = st.text_input("Entre ton code secret :", type="password")
        if st.button("Ouvrir mon journal"):
            try:
                users_df = pd.DataFrame(sh.worksheet("Utilisateurs").get_all_records())
                match = users_df[users_df['Code'].astype(str) == str(input_code)]
                if not match.empty:
                    st.session_state.user_data = {"Nom": match.iloc[0]['Nom'], "Acces": match.iloc[0]['Accès Journal']}
                    st.rerun()
                else: st.error("Code erroné... 🌸")
            except: st.error("Problème de connexion à la liste des utilisateurs.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
user_nom = st.session_state.user_data['Nom']
st.title(f"🌸 Journal de {user_nom}")
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ONGLET 1 : JOURNAL ---
with tabs[0]:
    if st.session_state.user_data['Acces'] == "OUI":
        st.markdown(f"### ✨ {datetime.now().strftime('%d/%m/%Y')}")
        st.markdown('<div class="post-it">Écris tes gratitudes ou pensées du jour...</div>', unsafe_allow_html=True)
        note_j = st.text_area("", height=200, key="j_note", label_visibility="collapsed")
        if st.button("Sauvegarder ma pensée"):
            if note_j and sh:
                sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), user_nom, note_j])
                st.success("Enregistré ! ✨")
    else: st.warning("Accès restreint au journal. 🔒")

# --- ONGLET 2 : SEMAINE (NOUVELLE ERGONOMIE) ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)

    col_g, col_m = st.columns([3, 1.2])
    semaine_inputs = {}
    
    with col_g:
        days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    d = start_week + timedelta(days=i+j)
                    d_str = d.strftime("%d/%m/%Y")
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{days_fr[i+j]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        semaine_inputs[d_str] = st.text_area("Note", height=100, key=f"in_{d_str}", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        b_save, b_mod = st.columns(2)
        if b_save.button("💾 TOUT SAUVEGARDER LA SEMAINE"):
            if sh:
                for d_k, text in semaine_inputs.items():
                    if text.strip(): sh.worksheet("Note").append_row([d_k, user_nom, text])
                st.success("Toute la semaine a été enregistrée ! ✨")
        if b_mod.button("🔄 MODIFIER / RAFRAÎCHIR"): st.rerun()

    with col_m:
        st.markdown('<div class="post-it"><b>🍎 Menu</b></div>', unsafe_allow_html=True)
        m_data = [st.text_input(j, key=f"m_{j}") for j in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]]
        if st.button("✨ Valider mon Menu"):
            sh.worksheet("Menu").append_row([start_week.strftime("%d/%m/%Y"), user_nom] + m_data)
            st.success("Menu enregistré !")

# --- ONGLET 3 : ANNEE (COULEURS + HISTORIQUE FIXÉ) ---
with tabs[2]:
    st.markdown("### 📅 Vue Annuelle 2026")
    for r in range(4):
        cols_c = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_c[c]:
                st.markdown(f'<div class="cal-card"><div class="p-header">{calendar.month_name[m_idx].upper()}</div><div style="text-align:center; padding:10px;">{calendar.month(2026, m_idx).split(chr(10), 1)[1].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 📜 Historique & Exports")
    try:
        data_j = sh.worksheet("Journal").get_all_records()
        df_j = pd.DataFrame(data_j)
        # On force l'affichage propre pour éviter le noir
        st.dataframe(df_j, use_container_width=True)
        st.download_button("📥 Télécharger CSV", data=df_j.to_csv(index=False), file_name="mon_journal.csv")
    except: st.info("Historique vide pour le moment.")

# --- LES AUTRES ONGLETS (TRACKERS, COURSES, STICKERS) ---
with tabs[3]: st.write("Onglet Trackers prêt pour tes sous-catégories.")
with tabs[4]: st.write("Onglet Courses prêt pour la correction couleur.")
with tabs[5]: st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg")
