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

# --- 2. FONCTIONS DE GESTION (HISTORIQUE & SUPPRESSION) ---
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

# --- 3. PERSONNALISATION PRÉNOM ---
user_name = "MeyLune"
try:
    missions = load_gs("Menage")
    if missions: user_name = missions[-1].get("Qui ?", "MeyLune").split(" ")[0]
except: pass

# --- 4. DESIGN & FIX CALLIGRAPHIE IPAD ---
st.set_page_config(page_title=f"Bujo de {user_name}", layout="wide")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@500;700&family=Great+Vibes&display=swap');
    
    :root {{ 
        --rose: #F48FB1; --sapin: #1B3022; --peche: #FFAB91; 
        --vert-doux: #B2DFDB; --postit-jaune: #FFF9C4; --postit-vert: #E0F2F1; 
    }}

    .stApp {{ background: linear-gradient(180deg, var(--peche) 0%, #FCE4EC 40%, #FFFFFF 100%) !important; }}

    /* FORCE LA CALLIGRAPHIE PARTOUT */
    html, body, [class*="st-"], label, .stMarkdown p {{
        font-family: 'Dancing Script', cursive !important;
        color: var(--sapin) !important;
    }}

    /* FIX DES CASES POUR QUE LA POLICE NE DÉBORDE PAS */
    input, textarea, [data-baseweb="input"], [data-baseweb="select"] > div {{
        background-color: white !important;
        color: var(--sapin) !important;
        -webkit-text-fill-color: var(--sapin) !important;
        border: 2px solid var(--rose) !important;
        border-radius: 12px !important;
        font-family: 'Dancing Script' !important;
        font-size: 1.5rem !important; 
        line-height: 1.5 !important;
        padding: 10px !important;
    }}

    /* ONGLETS CENTRÉS EN GREAT VIBES */
    .stTabs [data-baseweb="tab-list"] {{ 
        display: flex; justify-content: center !important; 
        gap: 30px; margin-bottom: 50px !important; 
    }}
    .stTabs button {{
        font-family: 'Great Vibes', cursive !important;
        font-size: 2.2rem !important;
        color: var(--sapin) !important;
        background: transparent !important;
        border: none !important;
    }}

    .titre-calli {{ font-family: 'Great Vibes' !important; font-size: 4.8rem; color: var(--sapin); text-align: center; margin-bottom: 30px; }}
    .sous-titre-calli {{ font-family: 'Great Vibes' !important; font-size: 3rem; margin-top: 15px; }}
    
    /* STYLE POST-IT RÉTABLI */
    .post-it {{ 
        background: white; border-radius: 15px; padding: 15px; margin-bottom: 10px; 
        border-left: 8px solid var(--rose); box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }}
    .postit-planning {{ background: var(--postit-jaune); padding: 10px; border-radius: 4px; border-left: 4px solid #FBC02D; font-size: 1.1rem; margin-top: 5px; }}
    .postit-menu {{ background: var(--postit-vert); padding: 8px; border-radius: 5px; border-left: 4px solid #80CBC4; font-size: 1.1rem; }}
    .postit-course {{ background: #E1F5FE; padding: 10px; border-radius: 8px; border-left: 5px solid #03A9F4; }}

    /* CALENDRIER ANNUEL VERT DOUX */
    .cal-header-vert {{ background: var(--vert-doux) !important; color: var(--sapin) !important; text-align: center; border-radius: 10px 10px 0 0; padding: 8px; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

if 'shopping' not in st.session_state: st.session_state.shopping = []

st.markdown(f'<div class="titre-calli">🌸 L\'Univers de {user_name}</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- TAB 1: JOURNAL & GRATITUDE (Avec Boutons Modif/Suppr) ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("Libère ton esprit...", height=120, key="j_in", label_visibility="collapsed")
        if st.button("💾 Sauver pensée", key="btn_j"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data[-5:])):
            idx = len(j_data)-1-i
            st.markdown(f'<div class="post-it">{e.get("Texte", "")}</div>', unsafe_allow_html=True)
            bj1, bj2, _ = st.columns([1, 1, 5])
            bj1.button("✏️", key=f"ej_{idx}")
            if bj2.button("🗑️", key=f"dj_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("Petit bonheur...", height=120, key="g_in", label_visibility="collapsed")
        if st.button("🙏 Sauver gratitude", key="btn_g"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data[-5:])):
            idx_g = len(g_data)-1-i
            st.markdown(f'<div class="post-it" style="border-left-color: #D4AF37; background: #FFFDE7;"><i>{e.get("Texte", "")}</i></div>', unsafe_allow_html=True)
            bg1, bg2, _ = st.columns([1, 1, 5])
            bg1.button("✏️", key=f"eg_{idx_g}")
            if bg2.button("🗑️", key=f"dg_{idx_g}"): delete_gs("Gratitude", idx_g); st.rerun()

# --- TAB 2: SEMAINE (Restauration Complète) ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    st.markdown(f'<div style="text-align:center; font-size:2.8rem; padding:20px;">Semaine du {start.strftime("%d/%m")} au {(start + timedelta(days=6)).strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    s_data = load_gs("Semaine")
    cols = st.columns(7)
    for i, j in enumerate(jours):
        d_str = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div style="text-align:center; font-weight:bold; font-size:1.6rem; border-bottom: 2px solid var(--vert-doux);">{j}</div>', unsafe_allow_html=True)
            p_in = st.text_area("P", key=f"p_{i}", height=120, label_visibility="collapsed", placeholder="Note...")
            m_in = st.text_input("🍴", key=f"m_{i}", label_visibility="collapsed", placeholder="Menu")
            if st.button("💾", key=f"sv_{i}"): save_gs("Semaine", [d_str, p_in, m_in]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == d_str:
                    if row.get('Planning'): st.markdown(f'<div class="postit-planning">📌 {row.get("Planning")}</div>', unsafe_allow_html=True)
                    if row.get('Menu'): st.markdown(f'<div class="postit-menu">🥗 {row.get("Menu")}</div>', unsafe_allow_html=True)

# --- TAB 3: ANNEE (Restauration Complète Vert Doux + Cercles) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier Annuel 2026</div>', unsafe_allow_html=True)
    ce1, ce2, ce3 = st.columns([1, 2, 1])
    n_d = ce1.date_input("Date", key="ann_d")
    n_e = ce2.text_input("Evénement", key="ann_e")
    if ce3.button("✨ Ajouter", key="ann_b"):
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
                st.markdown(f'<div style="font-family:monospace; background:white; padding:10px; border-radius:0 0 10px 10px; border:1px solid var(--vert-doux); white-space:pre; text-align:center; font-size:0.8rem; color:black !important;">{res}</div>', unsafe_allow_html=True)

# --- TAB 4: TRACKERS (Restauration Complète 3 Sous-onglets) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS TRIBU"])
    with tr_tabs[0]:
        st.markdown('<div class="sous-titre-calli">Ma Bibliothèque</div>', unsafe_allow_html=True)
        l_t = st.text_input("Titre", key="lt")
        l_a = st.text_input("Auteur", key="la")
        if st.button("💾 Sauver Livre", key="btn_l"):
            if l_t: save_gs("Lecture", [datetime.now().strftime("%d/%m/%Y"), l_t, l_a, "", 5, ""]); st.rerun()
        l_data = load_gs("Lecture")
        for i, b in enumerate(reversed(l_data[-5:])): 
            st.markdown(f'<div class="post-it">📔 {b.get("Titre")} - {b.get("Auteur")}</div>', unsafe_allow_html=True)
    with tr_tabs[1]:
        st.markdown('<div class="sous-titre-calli">Mon Bilan Santé</div>', unsafe_allow_html=True)
        eau = st.slider("Verres d'eau 💧", 0, 15, 6, key="eau_s")
        mig = st.select_slider("Migraine", options=["Aucune", "Gêne", "Douleur", "Intense", "Crise"], key="mig_s")
        if st.button("💾 Sauver Santé", key="btn_s"): save_gs("Sante", [datetime.now().strftime("%d/%m/%Y"), "", eau, mig, ""]); st.success("Noté !")
    with tr_tabs[2]:
        st.markdown('<div class="sous-titre-calli">Missions Tribu</div>', unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns(3)
        m_q = cm1.selectbox("Qui ?", ["Maman", "Papa", "Enfants"], key="mq")
        m_t = cm2.selectbox("Action", ["Vaisselle", "Poubelles", "Ménage", "Linge"], key="mt")
        m_j = cm3.selectbox("Jour", jours, key="mj")
        if st.button("🚀 Valider", key="btn_trib"): save_gs("Menage", [m_j, m_t, m_q]); st.rerun()

# --- TAB 5: COURSES (Restauration Favoris + Post-its) ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    favs = ["🍞 Pain", "🥛 Lait", "🥚 Oeufs", "🍎 Fruits", "🍝 Pâtes"]
    cols_f = st.columns(len(favs))
    for i, f in enumerate(favs):
        if cols_f[i].button(f, key=f"f_{i}"): st.session_state.shopping.append(f); st.rerun()
    it = st.text_input("Ajouter article...", key="shop_in")
    if st.button("➕ Ajouter", key="btn_sh"):
        if it: st.session_state.shopping.append(it); st.rerun()
    st.markdown("---")
    for i, item in enumerate(st.session_state.shopping):
        c_a, c_b = st.columns([6, 1])
        c_a.markdown(f'<div class="postit-course">🛒 {item}</div>', unsafe_allow_html=True)
        if c_b.button("🗑️", key=f"dc_{i}"): st.session_state.shopping.pop(i); st.rerun()
