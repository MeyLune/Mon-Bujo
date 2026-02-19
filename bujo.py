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

# --- 2. FONCTIONS DE GESTION (STRICTEMENT IDENTIQUES A TA VERSION NICKEL) ---
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

# --- 3. DESIGN & CORRECTIFS COULEURS ---
st.set_page_config(page_title="Mon Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Great+Vibes&display=swap');
    
    :root { --rose: #F48FB1; --sapin: #1B3022; --peche: #FFAB91; --vert: #B2DFDB; }

    .stApp { background: linear-gradient(180deg, var(--peche) 0%, #FCE4EC 40%, #FFFFFF 100%) !important; }

    /* TITRES & ONGLETS */
    .titre-calli { font-family: 'Great Vibes', cursive !important; font-size: 4.8rem; color: var(--sapin); text-align: center; padding: 20px; }
    .sous-titre-calli { font-family: 'Great Vibes', cursive !important; font-size: 3rem; color: var(--sapin); }
    .stTabs [data-baseweb="tab-list"] button { font-family: 'Great Vibes' !important; font-size: 2.2rem !important; color: var(--sapin) !important; }

    /* TEXTE STANDARD POUR LA LISIBILITE */
    p, label, span, input, textarea, div[data-baseweb="select"] { 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; 
    }

    /* FIX BOUTONS : ROSE AVEC TEXTE BLANC (PLUS DE NOIR) */
    .stButton>button {
        background-color: var(--rose) !important;
        color: white !important;
        border-radius: 15px !important;
        border: none !important;
        font-weight: bold !important;
    }

    /* FIX INPUTS POUR IPAD */
    input, textarea, [data-baseweb="select"] > div {
        background-color: white !important;
        color: var(--sapin) !important;
        border: 2px solid var(--rose) !important;
        border-radius: 10px !important;
    }

    /* CALENDRIER : POLICE FIXE POUR ALIGNEMENT PARFAIT */
    .cal-box {
        font-family: 'Courier New', Courier, monospace !important;
        background: white;
        padding: 10px;
        border-radius: 0 0 10px 10px;
        border: 1px solid var(--vert);
        white-space: pre;
        text-align: center;
        font-size: 0.9rem;
        color: black !important;
    }

    .post-it { 
        background: white; border-radius: 15px; padding: 15px; margin-bottom: 10px; 
        border-left: 8px solid var(--rose); box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

user_name = "MeyLune"
st.markdown(f'<div class="titre-calli">🌸 L\'Univers de {user_name}</div>', unsafe_allow_html=True)

tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- TAB 1: JOURNAL & GRATITUDE (Base Nickel Rétablie) ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("Libère ton esprit...", height=150, key="j_in", label_visibility="collapsed")
        if st.button("💾 Sauver pensée", key="btn_j"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data[-5:])):
            idx = len(j_data)-1-i
            st.markdown(f'<div class="post-it">{e.get("Texte")}</div>', unsafe_allow_html=True)
            bj1, bj2, _ = st.columns([1, 1, 5])
            if bj2.button("🗑️", key=f"dj_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("Petit bonheur...", height=150, key="g_in", label_visibility="collapsed")
        if st.button("🙏 Sauver gratitude", key="btn_g"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data[-5:])):
            idx_g = len(g_data)-1-i
            st.markdown(f'<div class="post-it" style="border-left-color: #D4AF37;">{e.get("Texte")}</div>', unsafe_allow_html=True)
            bg2, _ = st.columns([1, 6])
            if bg2.button("🗑️", key=f"dg_{idx_g}"): delete_gs("Gratitude", idx_g); st.rerun()

# --- TAB 2: SEMAINE (Ta version Nickel) ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    st.markdown(f'<div style="text-align:center; font-family:\'Great Vibes\'; font-size:2.8rem; padding:15px;">Semaine du {start.strftime("%d/%m")}</div>', unsafe_allow_html=True)
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    s_data = load_gs("Semaine")
    cols = st.columns(7)
    for i, j in enumerate(jours):
        d_str = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div style="text-align:center; background:var(--vert); border-radius:5px; padding:5px; font-weight:bold;">{j}</div>', unsafe_allow_html=True)
            p_in = st.text_input("Note", key=f"p_{i}", label_visibility="collapsed")
            m_in = st.text_input("🍴", key=f"m_{i}", label_visibility="collapsed")
            if st.button("💾", key=f"sv_{i}"): save_gs("Semaine", [d_str, p_in, m_in]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == d_str:
                    if row.get('Planning'): st.info(row.get('Planning'))
                    if row.get('Menu'): st.success(row.get('Menu'))

# --- TAB 3: ANNEE (Calendrier Alignement Parfait) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier Annuel 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    for r in range(4):
        cols_a = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_a[c]:
                st.markdown(f'<div style="background:var(--rose); color:white; text-align:center; padding:5px; border-radius:10px 10px 0 0; font-weight:bold;">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m_idx)
                res = "Lu Ma Me Je Ve Sa Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "   "
                        else: line += f"{get_circled_num(d)} " if f"{m_idx}-{d}" in marked else f"{d:2} "
                    res += line + "\n"
                st.markdown(f'<pre class="cal-box">{res}</pre>', unsafe_allow_html=True)

# --- TAB 4: TRACKERS (Fiche Lecture Complète) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS"])
    with tr_tabs[0]:
        st.markdown('<div class="sous-titre-calli">Ma Bibliothèque</div>', unsafe_allow_html=True)
        colL1, colL2 = st.columns(2)
        l_titre = colL1.text_input("Titre")
        l_auteur = colL2.text_input("Auteur")
        l_genre = st.selectbox("Genre", ["Roman", "Bien-être", "Cuisine", "Thriller", "Autre"])
        l_cit = st.text_area("Passage marquant ou avis")
        if st.button("💾 Sauver Livre"):
            save_gs("Lecture", [datetime.now().strftime("%d/%m/%Y"), l_titre, l_auteur, l_genre, 5, l_cit]); st.rerun()
        l_data = load_gs("Lecture")
        for i, b in enumerate(reversed(l_data)):
            idx_l = len(l_data)-1-i
            with st.expander(f"📔 {b.get('Titre')} - {b.get('Auteur')}"):
                st.write(f"**Genre:** {b.get('Genre')} | **Avis:** {b.get('Citation', b.get('Note'))}")
                if st.button("🗑️ Supprimer", key=f"dl_{idx_l}"): delete_gs("Lecture", idx_l); st.rerun()

    with tr_tabs[2]:
        st.markdown('<div class="sous-titre-calli">Missions Tribu</div>', unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns(3)
        mq = cm1.selectbox("Qui ?", ["Maman", "Papa", "Enfants"], key="mq")
        ma = cm2.selectbox("Action", ["Vaisselle", "Poubelles", "Linge", "Ménage"], key="ma")
        mj = cm3.selectbox("Jour", jours, key="mj")
        if st.button("🚀 Valider Mission"): save_gs("Menage", [mj, ma, mq]); st.rerun()

# --- TAB 5: COURSES (Stickers Rétablis) ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    if 'shop' not in st.session_state: st.session_state.shop = []
    
    favs = ["🍞 Pain", "🥛 Lait", "🥚 Oeufs", "🍎 Fruits", "🍝 Pâtes"]
    cols_f = st.columns(len(favs))
    for i, f in enumerate(favs):
        if cols_f[i].button(f, key=f"fav_{i}"): st.session_state.shop.append(f); st.rerun()
        
    it = st.text_input("Autre article...", key="sh_in")
    if st.button("➕ Ajouter"):
        if it: st.session_state.shop.append(it); st.rerun()
        
    for i, item in enumerate(st.session_state.shop):
        c_a, c_b = st.columns([6, 1])
        c_a.markdown(f'<div style="background:#E1F5FE; padding:10px; border-radius:10px; margin-bottom:5px;">🛒 {item}</div>', unsafe_allow_html=True)
        if c_b.button("🗑️", key=f"dc_{i}"): st.session_state.shop.pop(i); st.rerun()
