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

def update_gs(ws_n, idx, col, val):
    try: sh.worksheet(ws_n).update_cell(idx + 2, col, val)
    except: pass

def get_circled_num(n):
    circled = {i: chr(9311 + i) for i in range(1, 21)}
    circled.update({21: "㉑", 22: "㉒", 23: "㉓", 24: "㉔", 25: "㉕", 26: "㉖", 27: "㉗", 28: "㉘", 29: "㉙", 30: "㉚", 31: "㉛"})
    return circled.get(n, str(n))

# --- 2. STYLE DESIGN (Spécial iPad & Couleurs Pêche) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&display=swap');
    :root { --rose: #F48FB1; --sapin: #1B3022; --peche: #FFAB91; --vert: #B2DFDB; }
    
    .stApp { 
        background: linear-gradient(180deg, var(--peche) 0%, #fce4ec 40%, #e0f2f1 100%) !important;
        background-attachment: fixed;
    }

    /* PROTECTION ANTI-TEXTE BLANC (iPad/Safari) */
    p, span, div, label, li, h1, h2, h3, .stMarkdown {
        color: #1B3022 !important; 
        -webkit-text-fill-color: #1B3022 !important;
        font-family: 'Comfortaa' !important;
    }

    /* CHAMPS DE SAISIE : Fond blanc, texte noir */
    input, textarea, [data-baseweb="input"], [data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
        -webkit-text-fill-color: black !important;
        border: 2px solid var(--rose) !important;
        border-radius: 12px !important;
    }

    /* BOUTONS : Fond blanc, contour rose, texte noir */
    .stButton>button {
        background-color: white !important;
        color: black !important;
        border: 2px solid var(--rose) !important;
        border-radius: 10px !important;
    }

    .titre-calli { font-family: 'Dancing Script'; font-size: 3.5rem; color: var(--sapin); text-align: center; }
    .sous-titre-calli { font-family: 'Dancing Script'; font-size: 2.2rem; color: var(--sapin); }
    
    .card-jour { background: white; border: 2px solid var(--rose); border-radius: 15px; padding: 15px; margin-bottom: 15px; }
    .header-jour { background: var(--vert); color: var(--sapin); text-align: center; font-weight: bold; border-radius: 10px; padding: 5px; }
    .sticker-nom { background: var(--vert); color: var(--sapin); border-radius: 20px; padding: 2px 8px; font-weight: bold; border: 1px solid var(--rose); font-size: 0.75rem; text-align: center;}
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
        t_j = st.text_area("...", height=120, key="in_j", label_visibility="collapsed")
        if st.button("💾 Sauver pensée", key="btn_j"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data[-5:])):
            idx = len(j_data) - 1 - i
            st.markdown(f'<div style="background:white; padding:10px; border-left:8px solid var(--rose); border-radius:10px; margin-bottom:5px; color:black;">{e.get("Texte", "")}</div>', unsafe_allow_html=True)
            if st.button("🗑️", key=f"dj_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("...", height=120, key="in_g", label_visibility="collapsed")
        if st.button("🙏 Sauver gratitude", key="btn_g"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        st.markdown('<div style="background:#FFF9C4; padding:15px; border-left:8px solid #D4AF37; border-radius:10px; color:black;"><b>Mes bonheurs :</b>', unsafe_allow_html=True)
        for e in reversed(g_data[-5:]):
            st.write(f"• {e.get('Texte', '')}")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 🗓️ SEMAINE ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    s_data = load_gs("Semaine")
    cols_s = st.columns(7)
    for i, j in enumerate(jours):
        curr_d = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols_s[i]:
            st.markdown(f'<div class="card-jour"><div class="header-jour">{j}</div>', unsafe_allow_html=True)
            p_in = st.text_area("P", key=f"p_{i}", height=70, label_visibility="collapsed")
            m_in = st.text_input("🍴", key=f"m_{i}", label_visibility="collapsed")
            if st.button("💾", key=f"s_{i}"):
                save_gs("Semaine", [curr_d, p_in, m_in]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == curr_d:
                    st.markdown(f"<small style='color:black;'>• {row.get('Planning')}<br>🍴 {row.get('Menu')}</small>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 📅 ANNEE ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    for r in range(4):
        cols_a = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_a[c]:
                st.markdown(f'<div style="background:var(--rose); color:white !important; -webkit-text-fill-color:white !important; text-align:center; border-radius:10px 10px 0 0;">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m_idx)
                res = "Lu Ma Me Je Ve Sa Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "   "
                        else: line += f"{get_circled_num(d)} " if f"{m_idx}-{d}" in marked else f"{d:2} "
                    res += line + "\n"
                st.markdown(f'<div style="font-family:monospace; background:white; color:black; padding:10px; border:1px solid var(--rose); border-radius:0 0 10px 10px; white-space:pre; text-align:center; font-size:0.8rem;">{res}</div>', unsafe_allow_html=True)

# --- 📊 TRACKERS (SANTÉ & LECTURE) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS"])
    with tr_tabs[0]:
        st.markdown('<div class="sous-titre-calli">📚 Ma Bibliothèque</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        titre = col1.text_input("Titre")
        statut = col2.selectbox("Statut", ["En cours", "Terminé", "Coup de cœur"])
        citation = st.text_area("Citation favorite")
        if st.button("💾 Sauver Livre"):
            save_gs("Lecture", [datetime.now().strftime("%d/%m/%Y"), titre, statut, citation]); st.success("Livre sauvé !")
            
    with tr_tabs[1]:
        st.markdown('<div class="sous-titre-calli">🩺 Mon Bien-être</div>', unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        sport = cs1.text_input("Sport du jour (Marche, Yoga...)")
        migraine = cs2.select_slider("Migraine", options=["Aucune", "Gêne", "Douleur", "Intense"])
        if st.button("💾 Sauver Santé"):
            save_gs("Sante", [datetime.now().strftime("%d/%m/%Y"), sport, migraine]); st.success("Santé enregistrée !")

    with tr_tabs[2]:
        st.markdown('<div class="sous-titre-calli">🏠 Missions Tribu</div>', unsafe_allow_html=True)
        m_data = load_gs("Menage")
        membres = ["Maman 🌸", "Papa 👔", "Enfant 1 👦", "Enfant 2 👧", "Enfant 3 👶"]
        qui = st.selectbox("Qui valide ?", membres)
        # Affichage simplifié par mission
        for idx, row in enumerate(m_data):
            st.write(f"📍 **{row.get('Tache')}**")
            mc = st.columns(7)
            for d_idx in range(7):
                if mc[d_idx].button("✨", key=f"m_{idx}_{d_idx}"):
                    update_gs("Menage", idx, d_idx + 2, qui); st.rerun()

# --- 🛒 COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    rapide = ["🍞 Pain", "🥛 Lait", "🍎 Fruits", "🍝 Pâtes", "🍚 Riz"]
    cr = st.columns(len(rapide))
    for i, r in enumerate(rapide):
        if cr[i].button(r, key=f"cr_{i}"): st.session_state.shopping.append(r); st.rerun()
    
    it = st.text_input("Ajouter...")
    if st.button("➕ Ajouter"):
        if it: st.session_state.shopping.append(it); st.rerun()
    
    st.markdown("---")
    for i, item in enumerate(st.session_state.shopping):
        ca, cb = st.columns([5, 1])
        ca.checkbox(item, key=f"ch_{i}")
        if cb.button("🗑️", key=f"del_{i}"): st.session_state.shopping.pop(i); st.rerun()
