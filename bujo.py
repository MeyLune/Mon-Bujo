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

# Fonctions outils
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

# --- 2. STYLE & DESIGN PEAUFINÉ ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Great+Vibes&family=Comfortaa:wght@400;700&display=swap');
    
    :root { 
        --rose: #F48FB1; 
        --sapin: #1B3022; 
        --peche: #FFAB91; 
        --vert-doux: #B2DFDB; 
        --postit-jaune: #FFF9C4; 
        --postit-vert: #E0F2F1; 
    }

    .stApp { background: linear-gradient(180deg, var(--peche) 0%, #FCE4EC 40%, #FFFFFF 100%) !important; }

    /* MENU ONGLETS CENTRÉ & CALLIGRAPHIE */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center !important;
        gap: 30px;
        background-color: transparent !important;
    }
    .stTabs button {
        font-family: 'Great Vibes', cursive !important;
        font-size: 2rem !important;
        color: var(--sapin) !important;
        background: rgba(255,255,255,0.4) !important;
        border: none !important;
        transition: 0.3s;
    }
    .stTabs button:hover { color: var(--rose) !important; transform: scale(1.05); }

    /* TEXTES & TITRES */
    .titre-calli { font-family: 'Dancing Script' !important; font-size: 3.8rem; color: var(--sapin); text-align: center; }
    .sous-titre-calli, .stMarkdown h3 { font-family: 'Dancing Script' !important; font-size: 2.8rem; color: var(--sapin); margin: 15px 0; }
    label, .stCheckbox span { font-family: 'Dancing Script' !important; font-size: 1.5rem !important; color: var(--sapin) !important; }
    
    * { font-family: 'Comfortaa', sans-serif !important; color: #1B3022 !important; }

    /* POST-ITS */
    .post-it { background: white; border-radius: 12px; padding: 15px; margin-bottom: 5px; border-left: 8px solid var(--rose); box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .postit-planning { background: var(--postit-jaune); padding: 10px; border-radius: 4px; border-bottom-right-radius: 18px; box-shadow: 2px 2px 5px rgba(0,0,0,0.08); margin-top: 8px; font-size: 0.8rem; border-left: 3px solid #FBC02D; }
    .postit-menu { background: var(--postit-vert); padding: 6px; border-radius: 5px; margin-top: 5px; font-size: 0.8rem; font-weight: bold; border-left: 3px solid #80CBC4; }
    .postit-course { background: #E1F5FE; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #03A9F4; display: flex; justify-content: space-between; align-items: center;}

    /* BOUTONS & INPUTS */
    .stButton>button { background: white !important; border: 2px solid var(--rose) !important; border-radius: 20px !important; color: var(--sapin) !important;}
    input, textarea, [data-baseweb="input"] { background: white !important; border-radius: 12px !important; border: 1px solid #ddd !important; }

    .cal-header-vert { background: var(--vert-doux) !important; color: var(--sapin) !important; text-align: center; border-radius: 10px 10px 0 0; padding: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

if 'shopping' not in st.session_state: st.session_state.shopping = []

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- ✍️ JOURNAL ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("Libère ton esprit...", height=100, key="j_in", label_visibility="collapsed")
        if st.button("💾 Sauver pensée", key="btn_j"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data[-5:])):
            idx = len(j_data)-1-i
            st.markdown(f'<div class="post-it">{e.get("Texte", "")}</div>', unsafe_allow_html=True)
            bj1, bj2, _ = st.columns([1, 1, 5])
            if bj1.button("✏️", key=f"ej_{idx}"): pass 
            if bj2.button("🗑️", key=f"dj_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("Petit bonheur...", height=100, key="g_in", label_visibility="collapsed")
        if st.button("🙏 Sauver gratitude", key="btn_g"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data[-5:])):
            idx_g = len(g_data)-1-i
            st.markdown(f'<div class="post-it" style="border-left-color: #D4AF37; background: #FFFDE7;"><i>{e.get("Texte", "")}</i></div>', unsafe_allow_html=True)
            bg1, bg2, _ = st.columns([1, 1, 5])
            if bg1.button("✏️", key=f"eg_{idx_g}"): pass
            if bg2.button("🗑️", key=f"dg_{idx_g}"): delete_gs("Gratitude", idx_g); st.rerun()

# --- 🗓️ SEMAINE (Pas de changement logique, juste style post-it maintenu) ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    st.markdown(f'<div style="text-align:center; font-family:\'Dancing Script\'; font-size:2.2rem; padding:15px;">Semaine du {start.strftime("%d/%m")} au {(start + timedelta(days=6)).strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    s_data = load_gs("Semaine")
    cols = st.columns(7)
    for i, j in enumerate(jours):
        d_str = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div style="text-align:center; font-weight:bold; font-family:\'Dancing Script\'; font-size:1.4rem;">{j}</div>', unsafe_allow_html=True)
            p_in = st.text_area("P", key=f"p_{i}", height=100, label_visibility="collapsed", placeholder="Note...")
            m_in = st.text_input("🍴", key=f"m_{i}", label_visibility="collapsed", placeholder="Menu")
            if st.button("💾", key=f"sv_{i}"): save_gs("Semaine", [d_str, p_in, m_in]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == d_str:
                    if row.get('Planning'): st.markdown(f'<div class="postit-planning">📌 {row.get("Planning")}</div>', unsafe_allow_html=True)
                    if row.get('Menu'): st.markdown(f'<div class="postit-menu">🥗 {row.get("Menu")}</div>', unsafe_allow_html=True)

# --- 📅 ANNEE (Vert Doux conservé) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier Annuel 2026</div>', unsafe_allow_html=True)
    ce1, ce2, ce3 = st.columns([1, 2, 1])
    n_d = ce1.date_input("Date", key="ann_d")
    n_e = ce2.text_input("Evénement", key="ann_e")
    if ce3.button("Ajouter", key="ann_b"):
        if n_e: save_gs("Evenements", [n_d.strftime("%d/%m/%Y"), n_e]); st.rerun()
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    for r in range(4):
        cols_a = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_a[c]:
                st.markdown(f'<div class="cal-header-vert">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m_idx)
                res = "Lu Ma Me Je Ve Sa Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "   "
                        else: line += f"{get_circled_num(d)} " if f"{m_idx}-{d}" in marked else f"{d:2} "
                    res += line + "\n"
                st.markdown(f'<div style="font-family:monospace; background:white; padding:10px; border-radius:0 0 10px 10px; border:1px solid var(--vert-doux); white-space:pre; text-align:center; font-size:0.8rem;">{res}</div>', unsafe_allow_html=True)

# --- 📊 TRACKERS (Lecture & Santé) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS"])
    with tr_tabs[0]:
        st.markdown('<div class="sous-titre-calli">Ma Bibliothèque</div>', unsafe_allow_html=True)
        l_t = st.text_input("Titre du livre", key="lt")
        if st.button("💾 Sauver Livre"):
            if l_t: save_gs("Lecture", [datetime.now().strftime("%d/%m/%Y"), l_t, "", "", 5, ""]); st.rerun()
        l_data = load_gs("Lecture")
        for b in reversed(l_data): st.markdown(f'<div class="post-it">📔 {b.get("Titre")}</div>', unsafe_allow_html=True)
    with tr_tabs[1]:
        st.markdown('<div class="sous-titre-calli">Mon Bilan Santé</div>', unsafe_allow_html=True)
        mig = st.select_slider("Migraine", options=["Aucune", "Gêne", "Douleur", "Intense", "Crise"])
        if st.button("Sauver Santé"): save_gs("Sante", [datetime.now().strftime("%d/%m/%Y"), "", mig]); st.success("Noté !")

# --- 🛒 COURSES (FAVORIS RESTAURÉS + POST-ITS) ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Ma Liste de Courses</div>', unsafe_allow_html=True)
    
    # Boutons rapides restaurés
    favoris = ["🍞 Pain", "🥛 Lait", "🥚 Oeufs", "🍎 Fruits", "🍝 Pâtes"]
    cols_fav = st.columns(len(favoris))
    for i, f in enumerate(favoris):
        if cols_fav[i].button(f, key=f"fav_{i}"):
            st.session_state.shopping.append(f)
            st.rerun()
            
    it = st.text_input("Ajouter un article spécifique...", key="shop_in")
    if st.button("➕ Ajouter à la liste"):
        if it: 
            st.session_state.shopping.append(it)
            st.rerun()
            
    st.markdown("---")
    # Affichage sous forme de post-its bleus
    for i, item in enumerate(st.session_state.shopping):
        with st.container():
            col_a, col_b = st.columns([6, 1])
            col_a.markdown(f'<div class="postit-course">🛒 {item}</div>', unsafe_allow_html=True)
            if col_b.button("🗑️", key=f"del_c_{i}"):
                st.session_state.shopping.pop(i)
                st.rerun()
