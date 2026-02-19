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

# Fonctions de gestion universelles
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

# --- 2. STYLE IPAD & DÉGRADÉ ROSE (SANS NOIR) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&display=swap');
    :root { --rose: #F48FB1; --sapin: #1B3022; --vert: #B2DFDB; --or: #D4AF37; }
    
    .stApp { 
        background: linear-gradient(135deg, #fdf2f5 0%, #fce4ec 100%) !important;
        background-attachment: fixed;
    }

    /* Correction fonds noirs iPad pour tous les champs */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, textarea, input {
        background-color: white !important;
        color: var(--sapin) !important;
        border: 2px solid var(--rose) !important;
        border-radius: 12px !important;
    }
    
    /* Correction boutons courses pour qu'ils restent visibles */
    .stButton > button {
        background-color: white !important;
        color: var(--sapin) !important;
        border: 2px solid var(--rose) !important;
        border-radius: 15px !important;
        font-weight: bold;
    }

    p, label, span, li, div, .stMarkdown { 
        font-family: 'Comfortaa' !important; 
        color: var(--sapin) !important; 
    }

    .titre-calli { font-family: 'Dancing Script'; font-size: 3.5rem; color: var(--sapin); text-align: center; }
    .sous-titre-calli { font-family: 'Dancing Script'; font-size: 2.2rem; color: var(--sapin); }
    
    .card-jour { background: white; border: 2px solid var(--rose); border-radius: 15px; padding: 15px; margin-bottom: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .header-jour { background: var(--vert); color: var(--sapin); text-align: center; font-weight: bold; border-radius: 10px; padding: 5px; margin-bottom: 10px; }
    
    .sticker-mission { background: var(--vert); color: var(--sapin); border-radius: 15px; padding: 5px 10px; font-size: 0.8rem; margin: 2px; border: 1px solid var(--rose); display: inline-block; }
    .book-card { background: white; border: 2px solid var(--rose); border-radius: 10px; padding: 15px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
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
        t_j = st.text_area("Ma pensée...", height=150, key="j_text", label_visibility="collapsed")
        if st.button("💾 Enregistrer pensée", key="j_btn"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data)):
            idx = len(j_data) - 1 - i
            txt = e.get("Texte", "")
            if txt and str(txt).lower() != "none":
                st.markdown(f'<div style="background:white; padding:12px; border-left:8px solid var(--rose); border-radius:10px; margin-bottom:8px;">{txt}</div>', unsafe_allow_html=True)
                if st.button("🗑️", key=f"dj_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("Reconnaissance...", height=150, key="g_text", label_visibility="collapsed")
        if st.button("🙏 Enregistrer gratitude", key="g_btn"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data)):
            idx_g = len(g_data) - 1 - i
            txt_g = e.get("Texte", "")
            if txt_g and str(txt_g).lower() != "none":
                st.markdown(f'<div style="background:white; padding:12px; border-left:8px solid var(--or); border-radius:10px; margin-bottom:8px;"><i>{txt_g}</i></div>', unsafe_allow_html=True)
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
            for row in s_data:
                if str(row.get("Date")) == curr_d:
                    if str(row.get('Planning', '')).lower() != "none":
                        st.markdown(f"<small>• {row.get('Planning')}</small>", unsafe_allow_html=True)
                    if str(row.get('Menu', '')).lower() != "none":
                        st.markdown(f"<small>🍴 {row.get('Menu')}</small>", unsafe_allow_html=True)
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

# --- 📊 TRACKERS (LECTURE + SANTÉ + MISSIONS) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 BIBLIOTHÈQUE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS TRIBU"])
    
    with tr_tabs[0]: # Lecture Historique
        st.markdown('<div class="sous-titre-calli">Ma Bibliothèque Historique</div>', unsafe_allow_html=True)
        with st.expander("📖 Ajouter une fiche de lecture"):
            c1, c2 = st.columns(2)
            titre = c1.text_input("Titre", key="lib_t")
            auteur = c1.text_input("Auteur", key="lib_a")
            note = c2.slider("Note / 10", 0, 10, 5, key="lib_n")
            avis = st.text_area("Avis / Résumé", key="lib_av")
            if st.button("Enregistrer le livre", key="lib_btn"):
                save_gs("Lectures", [datetime.now().strftime("%d/%m/%Y"), titre, auteur, note, avis]); st.rerun()
        books = load_gs("Lectures")
        cols_b = st.columns(3)
        for i, b in enumerate(reversed(books)):
            with cols_b[i % 3]:
                st.markdown(f'<div class="book-card"><b>{b.get("Titre")}</b><br><small>{b.get("Auteur")}</small><br>⭐ {b.get("Note")}/10<p style="font-size:0.8rem;">{b.get("Avis")}</p></div>', unsafe_allow_html=True)

    with tr_tabs[1]: # Santé Complet
        st.markdown('<div class="sous-titre-calli">Mon Équilibre</div>', unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        with cs1:
            st.selectbox("Humeur", ["Radieuse ☀️", "Paisible ☁️", "Fatiguée 🔋", "Sensible 🌙"], key="h_mood")
            st.select_slider("Énergie", ["Bas", "Moyen", "Top!"], key="h_nrg")
        with cs2:
            st.number_input("Verres d'eau 💧", 0, 15, 0, key="h_water")
            st.checkbox("Vitamines / Soins pris ✅", key="h_vit")
        st.button("Sauvegarder santé", key="h_btn")

    with tr_tabs[2]: # Missions Tribu (Interactivité Stickers)
        st.markdown('<div class="sous-titre-calli">Tableau des Missions</div>', unsafe_allow_html=True)
        qui = st.selectbox("Qui valide ?", ["Maman 🌸", "Papa 👔", "Enfant 1 👦", "Enfant 2 👧", "Enfant 3 👶"], key="t_who")
        st.write("1. Choisis une mission :")
        t_list = ["🍽️ Vaisselle", "🗑️ Poubelles", "🧹 Balai", "🔌 Aspirateur", "🧼 Serpillière", "✨ Poussière"]
        c_stk = st.columns(6)
        for i, t in enumerate(t_list):
            if c_stk[i].button(t, key=f"stk_{i}"): st.session_state.active_tache = t
        
        st.write("2. Pose-la dans la semaine :")
        cols_h = st.columns(7)
        m_data = load_gs("Menage")
        start_w = datetime.now().date() - timedelta(days=datetime.now().weekday())
        for idx, j in enumerate(jours):
            with cols_h[idx]:
                st.markdown(f"**{j[:2]}**")
                if st.button("✨", key=f"pl_{idx}"):
                    if "active_tache" in st.session_state:
                        save_gs("Menage", [st.session_state.active_tache, (start_w + timedelta(days=idx)).strftime("%d/%m/%Y"), qui]); st.rerun()
                for m in m_data:
                    if m.get('Lundi') == (start_w + timedelta(days=idx)).strftime("%d/%m/%Y"):
                        st.markdown(f"<div class='sticker-mission'>{m.get('Tache')[:2]} {m.get('Mardi')[:2]}</div>", unsafe_allow_html=True)

# --- 🛒 COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    favs = ["🍞 Pain", "🥛 Lait", "🍎 Fruits", "🍝 Pâtes", "🍚 Riz", "🥣 Céréales"]
    cols_f = st.columns(6)
    for idx, f in enumerate(favs):
        if cols_f[idx].button(f, key=f"fav_{idx}"):
            if f not in st.session_state.shopping: st.session_state.shopping.append(f); st.rerun()
    it = st.text_input("Ajouter autre...", key="c_in")
    if st.button("➕ Ajouter", key="c_btn"):
        if it: st.session_state.shopping.append(it); st.rerun()
    for i, item in enumerate(st.session_state.shopping):
        ca, cb = st.columns([5, 1])
        ca.checkbox(item, key=f"ch_{i}")
        if cb.button("🗑️", key=f"dc_{i}"): st.session_state.shopping.pop(i); st.rerun()

# --- 🎨 STICKERS ---
with tabs[5]:
    st.markdown('<div class="sous-titre-calli">🎨 Mes Stickers</div>', unsafe_allow_html=True)
