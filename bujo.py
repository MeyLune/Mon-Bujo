import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

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

# --- 2. DESIGN (OPTIMISÉ IPAD & CONTRASTE) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    [data-testid="stSidebar"] { display: none; }
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3, p, label { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }
    
    /* Correction Contrastes Champs (Fond blanc, texte vert) */
    div[data-baseweb="input"], .stTextArea textarea, .stTextInput input, div[data-baseweb="select"] {
        background-color: white !important;
        border: 2px solid #c8e6c9 !important;
        border-radius: 12px !important;
        color: #1b5e20 !important;
        -webkit-text-fill-color: #1b5e20 !important;
    }

    /* Boutons (Texte blanc forcé) */
    .stButton>button { background-color: #1b5e20 !important; border-radius: 20px !important; border: none !important; padding: 10px 20px !important; }
    .stButton>button p { color: white !important; font-weight: bold !important; font-size: 1.1rem !important; }

    /* Styles Grille Hebdomadaire */
    .p-header { background-color: #f06292; color: white !important; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    .p-cell { 
        background-color: white; 
        min-height: 150px; 
        padding: 10px; 
        border: 1px solid #fce4ec; 
        border-radius: 0 0 10px 10px; 
        margin-bottom: 20px; 
    }
    .event-tag { background: #fff1f3; border-left: 4px solid #f06292; padding: 5px 8px; margin-bottom: 5px; border-radius: 4px; font-size: 0.9rem; color: #ad1457 !important; }
    
    /* Post-it Journal */
    .post-it { background: #fff9c4; padding: 25px; border-left: 6px solid #fbc02d; font-family: 'Indie Flower', cursive; font-size: 1.3rem; color: #5d4037 !important; border-radius: 4px; margin-bottom: 15px; }
    .bujo-block { background: white; padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION & LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None

def login_procedure(code_entre):
    if sh:
        try:
            ws = sh.worksheet("Utilisateurs")
            df = pd.DataFrame(ws.get_all_records())
            df.columns = [c.strip().capitalize() for c in df.columns]
            df['Code'] = df['Code'].astype(str).str.strip()
            match = df[df['Code'] == str(code_entre).strip()]
            return match.iloc[0].to_dict() if not match.empty else None
        except: return None
    return None

if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code_saisi = st.text_input("Code personnel :", type="password")
        if st.button("Accéder au Journal"):
            user = login_procedure(code_saisi)
            if user:
                st.session_state.user_data = user
                st.rerun()
            else: st.error("Code erroné")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
user = st.session_state.user_data
col_t, col_l = st.columns([4, 1])
with col_t: st.markdown(f"<h1>Journal de {user['Nom']}</h1>", unsafe_allow_html=True)
with col_l:
    if st.button("🔒 Déconnexion"):
        st.session_state.user_data = None; st.rerun()

menu = ["✍️ JOURNAL", "🗓️ SEMAINE", "📊 TRACKERS", "🎨 STICKERS", "🛒 COURSES"]
if user.get('Accès journal') == "OUI" or user.get('Accès Journal') == "OUI":
    menu.append("💰 BUDGET PRIVÉ")

tabs = st.tabs(menu)

# --- ONGLET 1 : JOURNAL ---
with tabs[0]:
    st.markdown(f"### ✨ {datetime.now().strftime('%d %B %Y')}")
    st.markdown('<div class="post-it">Comment te sens-tu aujourd\'hui ?</div>', unsafe_allow_html=True)
    st.text_area("Ma pensée", height=200, label_visibility="collapsed", key="note_j")
    if st.button("Ancrer au Journal"): st.success("C'est enregistré !")

# --- ONGLET 2 : SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    
    # Calcul des infos de semaine (Numéro + Année)
    today = datetime.now().date()
    start_week = (today - timedelta(days=today.weekday())) + timedelta(weeks=st.session_state.w_off)
    num_semaine = start_week.isocalendar()[1]
    annee = start_week.year
    
    c_n1, c_n2, c_n3 = st.columns([1, 2, 1])
    if c_n1.button("⬅️ Précédente"): st.session_state.w_off -= 1
    if c_n3.button("Suivante ➡️"): st.session_state.w_off += 1
    c_n2.markdown(f"<h3 style='text-align:center;'>Semaine {num_semaine} - {annee}</h3>", unsafe_allow_html=True)

    # Lecture Google Sheets (Onglet Note)
    try:
        ws_notes = sh.worksheet("Note")
        data = ws_notes.get_all_values()
        df_notes = pd.DataFrame(data[1:], columns=data[0])
    except: df_notes = pd.DataFrame(columns=["Date", "Heure", "Type", "Note"])

    # Grille Hebdomadaire
    days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    for i in range(0, 7, 2):
        cols = st.columns(2)
        for j in range(2):
            if (i+j) < 7:
                curr_date = start_week + timedelta(days=i+j)
                day_str = curr_date.strftime("%d/%m/%Y")
                with cols[j]:
                    st.markdown(f'<div class="p-header">{days_fr[i+j]} {curr_date.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                    evts = df_notes[df_notes.iloc[:, 0] == day_str]
                    
                    # Construction du contenu INTERNE de la case
                    html_content = '<div class="p-cell">'
                    if not evts.empty:
                        for _, r in evts.iterrows():
                            html_content += f'<div class="event-tag"><b>{r.iloc[1]}</b> : {r.iloc[3]}</div>'
                    html_content += '</div>'
                    st.markdown(html_content, unsafe_allow_html=True)

    # Formulaire collaboratif
    with st.expander("➕ Ajouter un rendez-vous / Évènement"):
        with st.form("new_evt"):
            f_date = st.date_input("Date", value=today)
            f_time = st.text_input("Heure (ex: 10h00)")
            f_type = st.selectbox("Catégorie", ["Rdv", "Famille", "Travail", "Loisir"])
            f_note = st.text_input("Description")
            if st.form_submit_button("Valider l'entrée"):
                ws_notes.append_row([f_date.strftime("%d/%m/%Y"), f_time, f_type, f_note])
                st.success("Ajouté !"); st.rerun()

# --- ONGLET 3 : TRACKERS ---
with tabs[2]:
    st.markdown("### 📊 Mes Trackers")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="bujo-block">💧 Verres d\'eau', unsafe_allow_html=True)
        st.slider("", 0, 12, 0, key="eau_slider")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="bujo-block">🌿 Bien-être', unsafe_allow_html=True)
        st.checkbox("Méditation")
        st.checkbox("Lecture")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ONGLET 4 : STICKERS ---
with tabs[3]:
    st.markdown("### 🎨 Planches de Stickers")
    col_a, col_b = st.columns(2)
    with col_a:
        st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%202.jpg", caption="Pack Cosy")
    with col_b:
        st.image("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/stickers%201.jpg", caption="Pack Organisation")

# --- ONGLET 5 : COURSES ---
with tabs[4]:
    st.markdown('<div class="bujo-block"><h3>🛒 Liste de Courses</h3><p>À venir ce soir...</p></div>', unsafe_allow_html=True)

# --- ONGLET 6 : BUDGET (SI ACCÈS) ---
if len(tabs) > 5:
    with tabs[5]:
        st.markdown("### 🔒 Budget Personnel")
        try:
            ws_f = sh.worksheet("Finances")
            df_f = pd.DataFrame(ws_f.get_all_records())
            st.data_editor(df_f, use_container_width=True)
        except: st.error("Feuille 'Finances' introuvable.")
