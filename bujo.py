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

def get_circled_num(n):
    circled = {i: chr(9311 + i) for i in range(1, 21)}
    circled.update({21: "㉑", 22: "㉒", 23: "㉓", 24: "㉔", 25: "㉕", 26: "㉖", 27: "㉗", 28: "㉘", 29: "㉙", 30: "㉚", 31: "㉛"})
    return circled.get(n, str(n))

# --- 2. STYLE & DESIGN IPAD (DÉGRADÉ ROSE/VERT & ANTI-NOIR) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&display=swap');
    :root { --rose: #F48FB1; --sapin: #1B3022; --vert: #B2DFDB; --or: #D4AF37; }
    
    .stApp { 
        background: linear-gradient(180deg, #fce4ec 0%, #e0f2f1 100%) !important;
        background-attachment: fixed;
    }

    /* Correction fonds blancs iPad */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, textarea, input {
        background-color: white !important;
        color: var(--sapin) !important;
        border: 2px solid var(--rose) !important;
        border-radius: 12px !important;
    }
    
    .stButton > button {
        background-color: white !important;
        color: var(--sapin) !important;
        border: 2px solid var(--rose) !important;
        border-radius: 15px !important;
    }

    p, label, span, li, div, .stMarkdown { 
        font-family: 'Comfortaa' !important; 
        color: var(--sapin) !important; 
    }

    .titre-calli { font-family: 'Dancing Script'; font-size: 3.5rem; color: var(--sapin); text-align: center; margin-bottom: 20px;}
    .sous-titre-calli { font-family: 'Dancing Script'; font-size: 2.2rem; color: var(--sapin); }
    
    .post-it-courses { 
        background: #fffde7; border-left: 10px solid var(--or); 
        padding: 20px; border-radius: 5px; box-shadow: 3px 3px 10px rgba(0,0,0,0.1);
    }

    .mission-day-box {
        background: white; border: 2px solid var(--rose); border-radius: 12px;
        padding: 10px; margin-bottom: 10px; min-height: 160px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .sticker-info { background: var(--vert); color: var(--sapin); padding: 5px; border-radius: 8px; margin-top: 5px; font-size: 0.85rem; border: 1px solid var(--rose); text-align: center; }
    
    .card-journal { background: white; padding: 12px; border-left: 8px solid var(--rose); border-radius: 10px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if 'shopping' not in st.session_state: st.session_state.shopping = []

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- ✍️ JOURNAL & GRATITUDE ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("...", height=150, key="j_in", label_visibility="collapsed")
        if st.button("💾 Enregistrer pensée", key="j_btn"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data)):
            idx = len(j_data)-1-i
            if str(e.get("Texte")).lower() != "none":
                st.markdown(f'<div class="card-journal">{e.get("Texte")}</div>', unsafe_allow_html=True)
                if st.button("🗑️", key=f"dj_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("...", height=150, key="g_in", label_visibility="collapsed")
        if st.button("🙏 Enregistrer gratitude", key="g_btn"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data)):
            idx_g = len(g_data)-1-i
            if str(e.get("Texte")).lower() != "none":
                st.markdown(f'<div class="card-journal" style="border-left-color:var(--or);"><i>{e.get("Texte")}</i></div>', unsafe_allow_html=True)
                if st.button("🗑️", key=f"dg_{idx_g}"): delete_gs("Gratitude", idx_g); st.rerun()

# --- 🗓️ SEMAINE ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    jours_sem = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    s_data = load_gs("Semaine")
    l1, l2 = st.columns(3), st.columns(4)
    all_cols = l1 + l2
    for i, j in enumerate(jours_sem):
        curr_d = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with all_cols[i]:
            st.markdown(f'<div style="background:white; border:2px solid var(--rose); border-radius:15px; padding:10px; margin-bottom:10px;">', unsafe_allow_html=True)
            st.markdown(f'<div style="background:var(--vert); text-align:center; border-radius:10px; font-weight:bold;">{j} {curr_d[:5]}</div>', unsafe_allow_html=True)
            p_in = st.text_area("Note", key=f"p_{i}", height=70, label_visibility="collapsed", placeholder="Planning...")
            m_in = st.text_input("Menu", key=f"m_{i}", label_visibility="collapsed", placeholder="🍴 Menu...")
            if st.button("💾", key=f"s_{i}"):
                if p_in or m_in: save_gs("Semaine", [curr_d, p_in, m_in]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == curr_d:
                    st.markdown(f"<small>• {row.get('Planning')}<br>🍴 {row.get('Menu')}</small>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 📅 ANNEE ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    with st.expander("📍 Marquer un événement"):
        cev1, cev2 = st.columns(2)
        dev = cev1.date_input("Date", key="ev_date")
        nev = cev2.text_input("Evénement", key="ev_name")
        if st.button("Ajouter au calendrier"): save_gs("Evenements", [dev.strftime("%d/%m/%Y"), nev]); st.rerun()

    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                st.markdown(f'<div style="background:var(--rose); color:white; padding:5px; text-align:center; border-radius:10px 10px 0 0;">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m_idx)
                res = "Lu Ma Me Je Ve Sa Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "   "
                        else: line += f"{get_circled_num(d)} " if f"{m_idx}-{d}" in marked else f"{d:2} "
                    res += line + "\n"
                st.markdown(f'<div style="font-family:monospace; background:white; padding:10px; border:1px solid var(--rose); border-radius:0 0 10px 10px; white-space:pre; text-align:center;">{res}</div>', unsafe_allow_html=True)

# --- 📊 TRACKERS (LECTURE + SANTÉ + MISSIONS) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 BIBLIOTHÈQUE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS TRIBU"])
    
    with tr_tabs[0]: # Lecture Historique
        st.markdown('<div class="sous-titre-calli">Ma Fiche de Lecture</div>', unsafe_allow_html=True)
        cl1, cl2 = st.columns(2)
        titre_l = cl1.text_input("Titre", key="l_t")
        auteur_l = cl1.text_input("Auteur", key="l_a")
        note_l = cl2.slider("Note / 10", 0, 10, 5, key="l_n")
        avis_l = st.text_area("Avis & Résumé", key="l_av")
        if st.button("💾 Enregistrer le livre", key="l_btn"):
            save_gs("Lectures", [datetime.now().strftime("%d/%m/%Y"), titre_l, auteur_l, note_l, avis_l]); st.rerun()
        
        st.markdown("---")
        if st.checkbox("📖 Consulter l'historique de ma bibliothèque"):
            books = load_gs("Lectures")
            for b in reversed(books):
                st.markdown(f'<div style="background:white; border:1px solid var(--rose); border-radius:10px; padding:10px; margin-bottom:10px;"><b>{b.get("Titre")}</b> - {b.get("Auteur")} | ⭐ {b.get("Note")}/10<br><small>{b.get("Avis")}</small></div>', unsafe_allow_html=True)

    with tr_tabs[1]: # Santé
        st.markdown('<div class="sous-titre-calli">Mon Équilibre</div>', unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        with cs1:
            st.selectbox("Humeur", ["Radieuse ☀️", "Paisible ☁️", "Fatiguée 🔋", "Sensible 🌙"], key="h_mood")
            st.number_input("Verres d'eau 💧", 0, 15, 0, key="h_water")
        with cs2:
            st.select_slider("Énergie", ["Bas", "Moyen", "Top!"], key="h_nrg")
            st.checkbox("Vitamines / Soins pris ✅", key="h_vit")
        st.button("Sauvegarder santé", key="h_save")

    with tr_tabs[2]: # Missions Tribu
        st.markdown('<div class="sous-titre-calli">Missions de la Tribu</div>', unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns(3)
        qui_m = cm1.selectbox("Qui ?", ["Enfant 1 👦", "Enfant 2 👧", "Enfant 3 👶", "Maman 🌸", "Papa 👔"])
        date_m = cm2.date_input("Date")
        taches_m = ["🍽️ Vaisselle", "🗑️ Poubelles", "🧹 Balai", "🔌 Aspirateur", "🧼 Serpillière", "✨ Poussière", "🥣 Débarrasser", "🚿 Salle de bain", "🚽 Toilettes", "🧸 Chambres"]
        tache_m = cm3.selectbox("Mission ?", taches_m)
        if st.button("🚀 Valider la mission"):
            save_gs("Menage", [tache_m, date_m.strftime("%d/%m/%Y"), qui_m]); st.rerun()
        
        st.markdown("---")
        m_data = load_gs("Menage")
        start_w = datetime.now().date() - timedelta(days=datetime.now().weekday())
        jours_m = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        cols_m = st.columns(7)
        for idx, j_n in enumerate(jours_m):
            d_s = (start_w + timedelta(days=idx)).strftime("%d/%m/%Y")
            with cols_m[idx]:
                st.markdown(f'<div class="mission-day-box"><center><b>{j_n}</b><br><small>{d_s[:5]}</small></center>', unsafe_allow_html=True)
                for m in m_data:
                    if m.get('Lundi') == d_s:
                        st.markdown(f'<div class="sticker-info"><b>{m.get("Tache")}</b><br>{m.get("Mardi").split()[0]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# --- 🛒 COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    c_l, c_r = st.columns([1, 1])
    with c_l:
        favs = ["🍞 Pain", "🥛 Lait", "🍎 Fruits", "🍚 Riz", "🥣 Céréales"]
        for f in favs:
            if st.button(f"Ajouter {f}", key=f"f_{f}"):
                if f not in st.session_state.shopping: st.session_state.shopping.append(f); st.rerun()
        n_it = st.text_input("Autre ?", key="n_it")
        if st.button("➕ Ajouter"):
            if n_it: st.session_state.shopping.append(n_it); st.rerun()
    with c_r:
        st.markdown('<div class="post-it-courses"><b>📝 À ACHETER :</b><br>', unsafe_allow_html=True)
        for i, it in enumerate(st.session_state.shopping):
            ci1, ci2 = st.columns([4, 1])
            ci1.write(f"☐ {it}")
            if ci2.button("🗑️", key=f"del_{i}"):
                st.session_state.shopping.pop(i); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
