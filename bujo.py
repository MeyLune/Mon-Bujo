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

# --- 2. CONFIGURATION & STYLE (Rose & iPad) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&display=swap');
    :root { --rose: #F48FB1; --sapin: #1B3022; --vert: #B2DFDB; --or: #D4AF37; }
    
    .stApp { 
        background: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), 
                    url("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg");
        background-size: cover; background-attachment: fixed;
    }
    
    .titre-calli { font-family: 'Dancing Script'; font-size: 3.5rem; color: var(--sapin); text-align: center; padding: 10px; }
    .sous-titre-calli { font-family: 'Dancing Script'; font-size: 2.2rem; color: var(--sapin); }
    p, label, span, div { font-family: 'Comfortaa' !important; color: var(--sapin) !important; }
    
    .post-it { padding: 15px; border-radius: 15px; margin-bottom: 10px; border-left: 10px solid var(--rose); background: white; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .card-jour { background: rgba(255,255,255,0.9); border: 2px solid var(--rose); border-radius: 15px; padding: 10px; margin-bottom: 15px; }
    .header-jour { background: var(--vert); color: var(--sapin); text-align: center; font-weight: bold; border-radius: 10px; padding: 5px; margin-bottom: 10px; }
    
    /* Style spécifique pour le tableau ménage */
    .tache-nom { background: #fdf2f5; border: 1px solid var(--rose); border-radius: 8px; padding: 5px; font-size: 0.8rem; text-align: center; min-height: 40px; display: flex; align-items: center; justify-content: center; }
    .sticker-nom { background: var(--vert); color: var(--sapin); border-radius: 20px; padding: 2px 8px; font-size: 0.7rem; font-weight: bold; border: 1px solid var(--rose); }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if 'shopping' not in st.session_state: st.session_state.shopping = []

# --- LOGIN ---
if "user_data" not in st.session_state:
    st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal") or code == "2125":
            st.session_state.user_data = {"Nom": "MeyLune"}; st.rerun()
    st.stop()

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ✍️ JOURNAL ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("...", height=150, key="in_j", label_visibility="collapsed")
        if st.button("💾 Enregistrer pensée"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data)):
            idx = len(j_data) - 1 - i
            txt = e.get("Texte", "")
            if txt and str(txt).lower() != "none":
                st.markdown(f'<div class="post-it"><small>{e.get("Date")}</small><br>{txt}</div>', unsafe_allow_html=True)
                if st.button("🗑️", key=f"dj_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("...", height=150, key="in_g", label_visibility="collapsed")
        if st.button("🙏 Enregistrer gratitude"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data)):
            idx_g = len(g_data) - 1 - i
            txt_g = e.get("Texte", "")
            if txt_g and str(txt_g).lower() != "none":
                st.markdown(f'<div class="post-it" style="border-left-color:var(--or);"><i>{txt_g}</i></div>', unsafe_allow_html=True)
                if st.button("🗑️", key=f"dg_{idx_g}"): delete_gs("Gratitude", idx_g); st.rerun()

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
            p_in = st.text_area("Note", key=f"ps_{i}", height=80, label_visibility="collapsed", placeholder="Planning...")
            m_in = st.text_input("Menu", key=f"ms_{i}", label_visibility="collapsed", placeholder="🍴 Menu...")
            if st.button("💾", key=f"sv_{i}"):
                if p_in or m_in: save_gs("Semaine", [curr_d, p_in, m_in]); st.rerun()
            for idx_s, row in enumerate(s_data):
                if str(row.get("Date")) == curr_d:
                    st.markdown(f"<div style='font-size:0.8rem;'>• {row.get('Planning')}<br>🍴 {row.get('Menu')}</div>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"ds_{idx_s}"): delete_gs("Semaine", idx_s); st.rerun()
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

# --- 📊 TRACKERS (Ajout Ménage Interactif) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🩺 SANTÉ", "🏠 RESPONSABILITÉS"])
    
    with tr_tabs[2]:
        st.markdown('<div class="sous-titre-calli">🏠 Tableau des Missions</div>', unsafe_allow_html=True)
        # Système de Stickers Enfants/Parents
        membres = ["Maman 🌸", "Papa 👔", "Enfant 1 👦", "Enfant 2 👧"]
        col_u1, col_u2 = st.columns([1, 2])
        user_active = col_u1.selectbox("Qui s'enregistre ?", membres)
        
        with st.expander("➕ Ajouter une nouvelle mission"):
            nt = st.text_input("Nom de la tâche")
            if st.button("Ajouter au tableau"):
                if nt: save_gs("Menage", [nt, "", "", "", "", "", "", ""]); st.rerun()

        m_data = load_gs("Menage")
        jours_m = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        
        # En-tête du tableau
        cols_m = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
        cols_m[0].write("**Missions**")
        for i, j_m in enumerate(jours_m): cols_m[i+1].write(f"**{j_m[:2]}**")
        
        for idx_m, row_m in enumerate(m_data):
            cm = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
            cm[0].markdown(f"<div class='tache-nom'>{row_m.get('Tache')}</div>", unsafe_allow_html=True)
            
            for d_m_idx, j_m_nom in enumerate(jours_m):
                current_val = str(row_m.get(j_m_nom, ""))
                
                if current_val == "" or current_val.lower() == "none":
                    if cm[d_m_idx+1].button("✨", key=f"m_{idx_m}_{d_m_idx}"):
                        update_gs("Menage", idx_m, d_m_idx + 2, user_active)
                        st.rerun()
                else:
                    # Affichage du "Sticker" (Prénom seulement)
                    prenom = current_val.split()[0]
                    cm[d_m_idx+1].markdown(f"<div class='sticker-nom'>{prenom}</div>", unsafe_allow_html=True)
                    if cm[d_m_idx+1].button("🗑️", key=f"md_{idx_m}_{d_m_idx}"):
                        update_gs("Menage", idx_m, d_m_idx + 2, "")
                        st.rerun()
            st.markdown("---")

# --- 🛒 COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    it = st.text_input("Ajouter article...", key="c_add")
    if st.button("➕ Ajouter"):
        if it: st.session_state.shopping.append(it); st.rerun()
    for i, item in enumerate(st.session_state.shopping):
        ca, cb = st.columns([4, 1])
        ca.checkbox(item, key=f"ch_{i}")
        if cb.button("🗑️", key=f"dc_{i}"): st.session_state.shopping.pop(i); st.rerun()

# --- 🎨 STICKERS ---
with tabs[5]:
    st.markdown('<div class="sous-titre-calli">🎨 Mes Stickers</div>', unsafe_allow_html=True)
    st.write("Espace en attente de tes créations !")
