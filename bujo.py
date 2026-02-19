import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import calendar

# --- 1. CONNEXION (Version Nickel) ---
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

# --- 2. FONCTIONS DE GESTION (Version Nickel - Suppressions incluses) ---
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

# --- 3. DESIGN CONSOLIDÉ (iPad, Menthe à l'eau & Rose Pastel) ---
st.set_page_config(page_title="Mon Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Great+Vibes&display=swap');
    
    :root { 
        --rose: #F48FB1; --sapin: #1B3022; --peche: #FFAB91; 
        --menthe: #B2DFDB; --menthe-fonce: #00695C; 
    }

    .stApp { background: linear-gradient(180deg, var(--peche) 0%, #FCE4EC 40%, #FFFFFF 100%) !important; }

    /* TITRES & ONGLETS */
    .titre-calli { font-family: 'Great Vibes', cursive !important; font-size: 4.8rem; color: var(--sapin); text-align: center; }
    .sous-titre-calli { font-family: 'Great Vibes', cursive !important; font-size: 3.2rem; color: var(--sapin); margin-top: 15px; }
    .stTabs [data-baseweb="tab-list"] button { font-family: 'Great Vibes' !important; font-size: 2.3rem !important; color: var(--sapin) !important; }

    /* LISIBILITÉ TEXTE (PAS DE BLANC SUR ROSE) */
    label, p, .stMarkdown, [data-testid="stMarkdownContainer"] p { 
        color: var(--sapin) !important; 
        font-weight: 500 !important;
    }

    /* FIX BOUTONS ROSES TEXTE BLANC */
    .stButton>button {
        background-color: var(--rose) !important;
        color: white !important;
        border-radius: 20px !important;
        padding: 12px 28px !important;
        border: none !important;
        font-weight: bold !important;
    }

    /* ENTREES IPAD PLUS GRANDES */
    input, textarea, [data-baseweb="input"], [data-baseweb="select"] > div {
        min-height: 55px !important;
        font-size: 1.2rem !important;
        background-color: white !important;
        color: var(--sapin) !important;
        border: 2px solid var(--rose) !important;
        border-radius: 12px !important;
    }

    /* CALENDRIER NICKEL MENTHE ALIGNÉ */
    .cal-grid {
        font-family: 'Courier New', Courier, monospace !important;
        background: white;
        padding: 20px;
        border-radius: 0 0 15px 15px;
        border: 2px solid var(--menthe);
        line-height: 1.6;
        text-align: left;
        color: var(--sapin) !important;
        font-size: 1.1rem;
        white-space: pre;
    }
    .cal-head {
        background: var(--menthe) !important;
        color: var(--sapin) !important;
        text-align: center;
        padding: 10px;
        font-weight: bold;
        border-radius: 15px 15px 0 0;
        font-family: 'Dancing Script', cursive !important;
        font-size: 1.7rem;
    }

    .post-it { 
        background: white; border-radius: 15px; padding: 15px; margin-bottom: 10px; 
        border-left: 8px solid var(--rose); box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        font-family: 'Dancing Script', cursive !important;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION SESSION (Pour les courses) ---
if 'shop' not in st.session_state: st.session_state.shop = []

st.markdown('<div class="titre-calli">🌸 L\'Univers de MeyLune</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- TAB 1: JOURNAL (Nickel + Suppression) ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("...", height=150, key="j_in", label_visibility="collapsed")
        if st.button("💾 Sauver pensée", key="bj"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data[-3:])):
            idx_j = len(j_data)-1-i
            st.markdown(f'<div class="post-it">{e.get("Texte")}</div>', unsafe_allow_html=True)
            if st.button("🗑️", key=f"dj_{idx_j}"): delete_gs("Journal", idx_j); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("...", height=150, key="g_in", label_visibility="collapsed")
        if st.button("🙏 Sauver gratitude", key="bg"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data[-3:])):
            idx_g = len(g_data)-1-i
            st.markdown(f'<div class="post-it" style="border-color:#D4AF37">{e.get("Texte")}</div>', unsafe_allow_html=True)
            if st.button("🗑️", key=f"dg_{idx_g}"): delete_gs("Gratitude", idx_g); st.rerun()

# --- TAB 2: SEMAINE (iPad Menthe) ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    st.markdown(f'<div style="text-align:center; color:var(--menthe-fonce); font-family:\'Great Vibes\'; font-size:3.2rem; padding:15px;">Semaine du {start.strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    s_data = load_gs("Semaine")
    cols = st.columns(7)
    for i, j in enumerate(jours):
        d_str = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div style="text-align:center; background:var(--menthe); padding:10px; border-radius:10px; font-weight:bold;">{j}</div>', unsafe_allow_html=True)
            p_in = st.text_area("Planning", key=f"p_{i}", height=120)
            m_in = st.text_input("Menu 🍴", key=f"m_{i}")
            if st.button("💾", key=f"s_{i}"): save_gs("Semaine", [d_str, p_in, m_in]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == d_str:
                    if row.get('Planning'): st.info(row.get('Planning'))
                    if row.get('Menu'): st.success(f"🥗 {row.get('Menu')}")

# --- TAB 3: ANNEE (Version Menthe Nickel) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier Annuel 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m = r*3 + c + 1
            with cols[c]:
                st.markdown(f'<div class="cal-head">{calendar.month_name[m].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m)
                txt = "Lu  Ma  Me  Je  Ve  Sa  Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "    "
                        else: line += f"{get_circled_num(d)} " if f"{m}-{d}" in marked else f"{d:2}  "
                    txt += line + "\n"
                st.markdown(f'<pre class="cal-grid">{txt}</pre>', unsafe_allow_html=True)

# --- TAB 4: TRACKERS (Fiche Lecture Détaillée + Missions) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS"])
    with tr_tabs[0]:
        st.markdown('<div class="sous-titre-calli">Fiche de Lecture</div>', unsafe_allow_html=True)
        cl1, cl2 = st.columns(2)
        l_t = cl1.text_input("Titre du livre", key="lt")
        l_a = cl2.text_input("Auteur", key="la")
        l_g = st.selectbox("Genre", ["Roman", "Bien-être", "Cuisine", "Thriller", "BD"], key="lg")
        l_note = st.select_slider("Ma note ⭐", options=[1,2,3,4,5], value=5)
        l_avis = st.text_area("Passage marquant ou avis", key="lav")
        if st.button("💾 Enregistrer la fiche"):
            save_gs("Lecture", [datetime.now().strftime("%d/%m/%Y"), l_t, l_a, l_g, l_note, l_avis]); st.rerun()
        
        st.markdown('<div class="sous-titre-calli">Ma Bibliothèque</div>', unsafe_allow_html=True)
        l_data = load_gs("Lecture")
        for i, b in enumerate(reversed(l_data)):
            idx_l = len(l_data)-1-i
            with st.expander(f"📔 {b.get('Titre')} - {b.get('Auteur')}"):
                st.markdown(f"**Genre :** {b.get('Genre')} | **Note :** {b.get('Note')} ⭐")
                st.write(f"**Avis :** {b.get('Citation', b.get('Note'))}")
                if st.button("🗑️ Supprimer livre", key=f"dl_{idx_l}"): delete_gs("Lecture", idx_l); st.rerun()

    with tr_tabs[2]:
        st.markdown('<div class="sous-titre-calli">Missions Tribu</div>', unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns(3)
        mq = cm1.selectbox("Qui ?", ["Maman", "Papa", "Enfants"], key="mq")
        ma = cm2.selectbox("Action", ["Vaisselle", "Linge", "Poubelles", "Ménage"], key="ma")
        mj = cm3.selectbox("Jour", jours, key="mj")
        if st.button("🚀 Valider Mission"): save_gs("Menage", [mj, ma, mq]); st.rerun()

# --- TAB 5: COURSES (Version Stickers Nickel) ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    favs = ["🍞 Pain", "🥛 Lait", "🥚 Oeufs", "🍎 Fruits", "🍝 Pâtes"]
    cols_f = st.columns(len(favs))
    for i, f in enumerate(favs):
        if cols_f[i].button(f, key=f"fav_{i}"): st.session_state.shop.append(f); st.rerun()
    
    it = st.text_input("Autre chose ?", key="sh_in")
    if st.button("➕ Ajouter article"):
        if it: st.session_state.shop.append(it); st.rerun()
    
    for i, item in enumerate(st.session_state.shop):
        ca, cb = st.columns([6, 1])
        ca.markdown(f'<div style="background:#E1F5FE; padding:12px; border-radius:10px; margin-bottom:5px; border-left:5px solid #03A9F4; color:black;">🛒 {item}</div>', unsafe_allow_html=True)
        if cb.button("🗑️", key=f"dc_{i}"): st.session_state.shop.pop(i); st.rerun()
