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

# Fonctions de gestion
def save_gs(ws_n, row):
    try: sh.worksheet(ws_n).append_row(row)
    except: pass

def load_gs(ws_n):
    try: return sh.worksheet(ws_n).get_all_records()
    except: return []

def delete_gs(ws_n, idx):
    try: sh.worksheet(ws_n).delete_rows(idx + 2)
    except: pass

def update_gs(ws_n, idx, col, val):
    try: sh.worksheet(ws_n).update_cell(idx + 2, col, val)
    except: pass

def get_circled_num(n):
    circled = {i: chr(9311 + i) for i in range(1, 21)}
    circled.update({21: "㉑", 22: "㉒", 23: "㉓", 24: "㉔", 25: "㉕", 26: "㉖", 27: "㉗", 28: "㉘", 29: "㉙", 30: "㉚", 31: "㉛"})
    return circled.get(n, str(n))

# --- 2. STYLE & DESIGN (Spécial iPad & Rose) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&display=swap');
    :root { --rose: #F48FB1; --sapin: #1B3022; --vert: #B2DFDB; --or: #D4AF37; }
    
    .stApp { 
        background: linear-gradient(135deg, #fdf2f5 0%, #fce4ec 100%) !important;
        background-attachment: fixed;
    }

    /* Correction cases noires iPad */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, textarea, input {
        background-color: white !important;
        color: var(--sapin) !important;
        border: 2px solid var(--rose) !important;
        border-radius: 12px !important;
    }
    
    p, label, span, li, div, .stMarkdown { 
        font-family: 'Comfortaa' !important; 
        color: var(--sapin) !important; 
    }

    .titre-calli { font-family: 'Dancing Script'; font-size: 3.5rem; color: var(--sapin); text-align: center; }
    .sous-titre-calli { font-family: 'Dancing Script'; font-size: 2.2rem; color: var(--sapin); }
    
    .card-jour { background: white; border: 2px solid var(--rose); border-radius: 15px; padding: 15px; margin-bottom: 15px; }
    .header-jour { background: var(--vert); color: var(--sapin); text-align: center; font-weight: bold; border-radius: 10px; padding: 5px; margin-bottom: 10px; }
    .sticker-nom { background: var(--vert); color: var(--sapin); border-radius: 20px; padding: 2px 8px; font-weight: bold; border: 1px solid var(--rose); font-size: 0.75rem; text-align: center;}
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if 'shopping' not in st.session_state: st.session_state.shopping = []

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ✍️ JOURNAL ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("...", height=150, key="in_j_final", label_visibility="collapsed")
        if st.button("💾 Enregistrer pensée", key="btn_j_final"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data)):
            idx = len(j_data) - 1 - i
            txt = e.get("Texte", "")
            if txt and str(txt).lower() != "none":
                st.markdown(f'<div style="background:white; padding:12px; border-left:8px solid var(--rose); border-radius:10px; margin-bottom:8px;">{txt}</div>', unsafe_allow_html=True)
                if st.button("🗑️", key=f"dj_fin_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("...", height=150, key="in_g_final", label_visibility="collapsed")
        if st.button("🙏 Enregistrer gratitude", key="btn_g_final"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data)):
            idx_g = len(g_data) - 1 - i
            txt_g = e.get("Texte", "")
            if txt_g and str(txt_g).lower() != "none":
                st.markdown(f'<div style="background:white; padding:12px; border-left:8px solid var(--or); border-radius:10px; margin-bottom:8px;"><i>{txt_g}</i></div>', unsafe_allow_html=True)
                if st.button("🗑️", key=f"dg_fin_{idx_g}"): delete_gs("Gratitude", idx_g); st.rerun()

# --- 🗓️ SEMAINE ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    s_data = load_gs("Semaine")
    l1, l2 = st.columns(3), st.columns(4)
    all_cols = l1 + l2
    for i, j in enumerate(jours):
        curr_d = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with all_cols[i]:
            st.markdown(f'<div class="card-jour"><div class="header-jour">{j} {curr_d[:5]}</div>', unsafe_allow_html=True)
            p_in = st.text_area("Note", key=f"ps_final_{i}", height=80, label_visibility="collapsed", placeholder="Planning...")
            m_in = st.text_input("Menu", key=f"ms_final_{i}", label_visibility="collapsed", placeholder="🍴 Menu...")
            if st.button("💾", key=f"sv_final_{i}"):
                if p_in or m_in: save_gs("Semaine", [curr_d, p_in, m_in]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == curr_d:
                    st.markdown(f"<small>• {row.get('Planning')}<br>🍴 {row.get('Menu')}</small>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 📅 ANNEE ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                st.markdown(f'<div style="background:var(--rose); color:white; padding:5px; text-align:center; border-radius:12px 12px 0 0; font-weight:bold;">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m_idx)
                res = "Lu Ma Me Je Ve Sa Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "   "
                        else: line += f"{get_circled_num(d)} " if f"{m_idx}-{d}" in marked else f"{d:2} "
                    res += line + "\n"
                st.markdown(f'<div style="font-family:monospace; background:white; padding:10px; border:1px solid var(--rose); border-radius:0 0 12px 12px; white-space:pre; text-align:center; font-size:0.8rem;">{res}</div>', unsafe_allow_html=True)

# --- 📊 TRACKERS (LECTURE + SANTÉ + RESPONSABILITÉS) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🩺 SANTÉ", "🏠 RESPONSABILITÉS"])
    
    with tr_tabs[0]: # Lecture
        st.markdown('<div class="sous-titre-calli">📚 Ma Bibliothèque</div>', unsafe_allow_html=True)
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.text_input("Titre", key="read_t_f")
            st.text_input("Auteur", key="read_a_f")
        with col_l2:
            st.slider("Ma Note / 10", 0, 10, 5, key="read_n_f")
        st.button("💾 Sauver Lecture", key="btn_read_final")

    with tr_tabs[1]: # Santé
        st.markdown('<div class="sous-titre-calli">🩺 Mon Bien-être</div>', unsafe_allow_html=True)
        ch1, ch2 = st.columns(2)
        with ch1:
            st.selectbox("Humeur", ["Souriante ✨", "Fatiguée 😴", "Stressée 😰", "Besoin de calme 🧘"], key="h_mood_f")
            st.number_input("Verres d'eau 💧", 0, 15, 0, key="h_water_f")
        with ch2:
            st.text_area("Notes", key="h_notes_f")
        st.button("💾 Enregistrer Santé", key="btn_h_final")

    with tr_tabs[2]: # Responsabilités (3 Enfants)
        st.markdown('<div class="sous-titre-calli">🏠 Missions de la Tribu</div>', unsafe_allow_html=True)
        membres = ["Maman 🌸", "Papa 👔", "Enfant 1 👦", "Enfant 2 👧", "Enfant 3 👶"]
        user_active = st.selectbox("Qui fait la mission ?", membres, key="select_tribe_final")
        
        m_data = load_gs("Menage")
        jours_m = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        
        cols_m = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
        cols_m[0].write("**Missions**")
        for i, j_m in enumerate(jours_m): cols_m[i+1].write(f"**{j_m[:2]}**")
        
        for idx_m, row_m in enumerate(m_data):
            cm = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
            cm[0].write(row_m.get('Tache'))
            for d_m_idx, j_m_nom in enumerate(jours_m):
                val = str(row_m.get(j_m_nom, ""))
                if val == "" or val.lower() == "none":
                    if cm[d_m_idx+1].button("✨", key=f"fin_m_{idx_m}_{d_m_idx}"):
                        update_gs("Menage", idx_m, d_m_idx + 2, user_active); st.rerun()
                else:
                    cm[d_m_idx+1].markdown(f"<div class='sticker-nom'>{val[:2]}</div>", unsafe_allow_html=True)

# --- 🛒 COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    rapide = ["🍞 Pain", "🥛 Lait", "🍎 Fruits", "🍝 Pâtes", "🍚 Riz", "🥣 Céréales"]
    cols_r = st.columns(len(rapide))
    for idx, r in enumerate(rapide):
        if cols_r[idx].button(r, key=f"rf_final_{idx}"):
            st.session_state.shopping.append(r); st.rerun()
    it = st.text_input("Autre chose ?", key="c_add_final")
    if st.button("➕ Ajouter", key="btn_c_final"):
        if it: st.session_state.shopping.append(it); st.rerun()
    for i, item in enumerate(st.session_state.shopping):
        ca, cb = st.columns([5, 1])
        ca.checkbox(item, key=f"chf_final_{i}")
        if cb.button("🗑️", key=f"dcf_final_{i}"):
            st.session_state.shopping.pop(i); st.rerun()

# --- 🎨 STICKERS ---
with tabs[5]:
    st.markdown('<div class="sous-titre-calli">🎨 Mes Stickers</div>', unsafe_allow_html=True)
