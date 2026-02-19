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
    except Exception: return None

sh = init_connection()

# --- 2. LOGIQUE PRÉNOM PERSONNALISÉ ---
user_name = "MeyLune"
try:
    # On récupère le prénom du dernier utilisateur ayant validé une mission
    data_tribu = sh.worksheet("Menage").get_all_records()
    if data_tribu:
        user_name = data_tribu[-1].get("Qui ?", "MeyLune").split(" ")[0]
except:
    pass

# --- 3. FONCTIONS ---
def save_gs(ws_n, row):
    try: sh.worksheet(ws_n).append_row(row)
    except: pass

def load_gs(ws_n):
    try: return sh.worksheet(ws_n).get_all_records()
    except: return []

def delete_gs(ws_n, idx):
    try: sh.worksheet(ws_n).delete_rows(idx + 2)
    except: pass

def get_circled_num(n):
    circled = {i: chr(9311 + i) for i in range(1, 21)}
    circled.update({21: "㉑", 22: "㉒", 23: "㉓", 24: "㉔", 25: "㉕", 26: "㉖", 27: "㉗", 28: "㉘", 29: "㉙", 30: "㉚", 31: "㉛"})
    return circled.get(n, str(n))

# --- 4. DESIGN & OPTIMISATION CASES ---
st.set_page_config(page_title=f"Bujo de {user_name}", layout="wide")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@500;700&family=Great+Vibes&display=swap');
    
    :root {{ 
        --rose: #F48FB1; --sapin: #1B3022; --peche: #FFAB91; 
        --vert-doux: #B2DFDB; --postit-jaune: #FFF9C4; --postit-vert: #E0F2F1; 
    }}

    .stApp {{ background: linear-gradient(180deg, var(--peche) 0%, #FCE4EC 40%, #FFFFFF 100%) !important; }}

    /* TEXTE GENERAL */
    html, body, [class*="st-"] {{
        font-family: 'Dancing Script', cursive !important;
        color: var(--sapin) !important;
        font-size: 1.1rem;
    }}

    /* OPTIMISATION DES CASES POUR LA CALLIGRAPHIE */
    input, textarea, [data-baseweb="input"], [data-baseweb="select"] > div {{
        background-color: white !important;
        color: var(--sapin) !important;
        -webkit-text-fill-color: var(--sapin) !important;
        border: 2px solid var(--rose) !important;
        border-radius: 12px !important;
        font-family: 'Dancing Script' !important;
        font-size: 1.5rem !important; /* Agrandissement pour que ça tombe juste */
        line-height: 1.6 !important;
        padding: 5px 15px !important;
    }}

    /* ONGLETS */
    .stTabs [data-baseweb="tab-list"] {{ 
        display: flex; justify-content: center !important; 
        gap: 30px; margin-bottom: 50px !important; 
    }}
    .stTabs button {{
        font-family: 'Great Vibes', cursive !important;
        font-size: 2rem !important;
    }}

    .titre-calli {{ font-family: 'Great Vibes' !important; font-size: 4.5rem; color: var(--sapin); text-align: center; margin-bottom: 30px; }}
    .sous-titre-calli {{ font-size: 2.8rem; margin-top: 20px; }}
    
    .post-it {{ 
        background: white; border-radius: 15px; padding: 20px; margin-bottom: 12px; 
        border-left: 10px solid var(--rose); box-shadow: 3px 3px 10px rgba(0,0,0,0.05);
        font-size: 1.4rem;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="titre-calli">🌸 L\'Univers de {user_name}</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- TAB 1: JOURNAL ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("Ecris ici...", height=150, key="txt_pensee_unique", label_visibility="collapsed")
        if st.button("💾 Sauver pensée", key="btn_pensee_unique"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data[-5:])):
            idx = len(j_data)-1-i
            st.markdown(f'<div class="post-it">{e.get("Texte", "")}</div>', unsafe_allow_html=True)
            bj1, bj2, _ = st.columns([1, 1, 5])
            bj1.button("✏️", key=f"edit_j_{idx}")
            if bj2.button("🗑️", key=f"del_j_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("Petit bonheur...", height=150, key="txt_grat_unique", label_visibility="collapsed")
        if st.button("🙏 Sauver gratitude", key="btn_grat_unique"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data[-5:])):
            idx_g = len(g_data)-1-i
            st.markdown(f'<div class="post-it" style="border-left-color: #D4AF37; background: #FFFDE7;"><i>{e.get("Texte", "")}</i></div>', unsafe_allow_html=True)
            bg1, bg2, _ = st.columns([1, 1, 5])
            bg1.button("✏️", key=f"edit_g_{idx_g}")
            if bg2.button("🗑️", key=f"del_g_{idx_g}"): delete_gs("Gratitude", idx_g); st.rerun()

# --- TAB 2: SEMAINE ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    st.markdown(f'<div style="text-align:center; font-family:\'Great Vibes\'; font-size:2.8rem; padding:15px;">Semaine du {start.strftime("%d/%m")} au {(start + timedelta(days=6)).strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    s_data = load_gs("Semaine")
    cols = st.columns(7)
    for i, j in enumerate(jours):
        d_str = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div style="text-align:center; font-weight:bold; font-size:1.6rem; color:var(--sapin); border-bottom: 2px solid var(--vert-doux);">{j}</div>', unsafe_allow_html=True)
            p_in = st.text_area("P", key=f"p_input_{i}", height=120, label_visibility="collapsed", placeholder="Planning")
            m_in = st.text_input("🍴", key=f"m_input_{i}", label_visibility="collapsed", placeholder="Menu")
            if st.button("💾", key=f"btn_save_sem_{i}"): save_gs("Semaine", [d_str, p_in, m_in]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == d_str:
                    if row.get('Planning'): st.markdown(f'<div style="background:var(--postit-jaune); padding:8px; border-radius:5px; margin-top:5px; font-size:1.1rem;">{row.get("Planning")}</div>', unsafe_allow_html=True)
                    if row.get('Menu'): st.markdown(f'<div style="background:var(--postit-vert); padding:8px; border-radius:5px; margin-top:5px; font-size:1.1rem;">🥗 {row.get("Menu")}</div>', unsafe_allow_html=True)

# --- TAB 3: ANNEE ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier Annuel 2026</div>', unsafe_allow_html=True)
    ce1, ce2, ce3 = st.columns([1, 2, 1])
    n_d = ce1.date_input("Date", key="cal_date_unique")
    n_e = ce2.text_input("Evénement", key="cal_event_unique")
    if ce3.button("✨ Ajouter", key="btn_cal_unique"):
        if n_e: save_gs("Evenements", [n_d.strftime("%d/%m/%Y"), n_e]); st.rerun()
    # (Logique calendrier inchangée pour respecter la structure)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    for r in range(4):
        cols_a = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_a[c]:
                st.markdown(f'<div style="background:var(--vert-doux); text-align:center; padding:5px; border-radius:10px 10px 0 0;">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                # ... rendu calendrier ...

# --- TAB 4: TRACKERS ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🩺 BIEN-ÊTRE", "🏠 TRIBU"])
    with tr_tabs[2]:
        st.markdown(f'<div class="sous-titre-calli">Missions Tribu {user_name}</div>', unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns(3)
        m_q = cm1.selectbox("Qui ?", ["Maman", "Papa", "Enfants"], key="sel_qui_unique")
        m_t = cm2.selectbox("Action", ["🍽️ Vaisselle", "🗑️ Poubelles", "🧹 Ménage", "🧺 Linge"], key="sel_quoi_unique")
        m_j = cm3.selectbox("Jour", jours, key="sel_jour_unique")
        if st.button("🚀 Valider", key="btn_tribu_unique"):
            save_gs("Menage", [m_j, m_t, m_q]); st.rerun()

# --- TAB 5: COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Ma Liste</div>', unsafe_allow_html=True)
    it = st.text_input("Ajouter article...", key="input_course_unique")
    if st.button("➕ Ajouter", key="btn_course_unique"):
        if it: save_gs("Courses", [it, "A faire"]); st.rerun()
