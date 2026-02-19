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

if 'shopping' not in st.session_state: st.session_state.shopping = []

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

# --- 2. STYLE CONSOLIDÉ ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&display=swap');
    :root { --rose: #F48FB1; --sapin: #1B3022; --vert: #B2DFDB; --or: #D4AF37; }
    
    .stApp { background: linear-gradient(180deg, #fce4ec 0%, #e0f2f1 100%) !important; }

    /* FORCE TEXTE NOIR POUR IPAD */
    input, textarea, select, div[data-baseweb="select"], div[data-baseweb="input"], .stMarkdown p {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    
    .titre-calli { font-family: 'Dancing Script'; font-size: 3.5rem; color: var(--sapin); text-align: center; }
    .sous-titre-calli { font-family: 'Dancing Script'; font-size: 2.2rem; color: var(--sapin); }
    
    /* Calendrier look papier */
    .cal-paper { background: white; border: 1px solid var(--rose); border-radius: 10px; padding: 10px; color: black; font-family: monospace; text-align: center; }
    
    /* Post-it */
    .post-it-yellow { background: #FFF9C4; border-left: 10px solid var(--or); padding: 15px; border-radius: 5px; color: black; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- JOURNAL & GRATITUDE ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("...", height=100, key="j_in", label_visibility="collapsed")
        if st.button("💾 Sauver pensée", key="j_btn"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data[-5:])):
            st.info(e.get("Texte", ""))
            if st.button("🗑️", key=f"dj_{i}"): delete_gs("Journal", len(j_data)-1-i); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("...", height=100, key="g_in", label_visibility="collapsed")
        if st.button("🙏 Sauver gratitude", key="g_btn"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        st.markdown('<div class="post-it-yellow"><b>Mes petits bonheurs :</b>', unsafe_allow_html=True)
        for e in reversed(g_data[-5:]):
            st.write(f"• {e.get('Texte', '')}")
        st.markdown('</div>', unsafe_allow_html=True)

# --- SEMAINE ---
with tabs[1]:
    start_w = datetime.now().date() - timedelta(days=datetime.now().weekday())
    s_data = load_gs("Semaine")
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    cols_s = st.columns(7)
    for i, j in enumerate(jours):
        d_str = (start_w + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols_s[i]:
            st.markdown(f'<div style="background:var(--vert); text-align:center; border-radius:5px; color:black;"><b>{j}</b></div>', unsafe_allow_html=True)
            p_in = st.text_area("Plan", key=f"p_{i}", height=100, label_visibility="collapsed")
            m_in = st.text_input("🍴", key=f"m_{i}", label_visibility="collapsed")
            if st.button("💾", key=f"sb_{i}"): save_gs("Semaine", [d_str, p_in, m_in]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == d_str:
                    st.markdown(f"<small style='color:black;'>• {row.get('Planning','')}<br><b>🍴 {row.get('Menu','')}</b></small>", unsafe_allow_html=True)

# --- ANNEE ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    for r in range(4):
        cols_a = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_a[c]:
                st.markdown(f'<div style="background:var(--rose); color:white; text-align:center; border-radius:10px 10px 0 0;">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m_idx)
                res = "Lu Ma Me Je Ve Sa Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "   "
                        else: line += f"{get_circled_num(d)} " if f"{m_idx}-{d}" in marked else f"{d:2} "
                    res += line + "\n"
                st.markdown(f'<div class="cal-paper">{res}</div>', unsafe_allow_html=True)

# --- TRACKERS (RESTAU) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 BIBLIOTHÈQUE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS"])
    with tr_tabs[1]: # Santé
        st.markdown('<div class="sous-titre-calli">Mon Équilibre</div>', unsafe_allow_html=True)
        humeur = st.selectbox("Humeur", ["Radieuse ☀️", "Paisible ☁️", "Fatiguée 🔋", "Sensible 🌙"])
        eau = st.slider("Verres d'eau 💧", 0, 12, 4)
        if st.button("Enregistrer Santé"):
            save_gs("Sante", [datetime.now().strftime("%d/%m/%Y"), humeur, eau]); st.success("C'est noté !")
    with tr_tabs[2]: # Missions
        st.markdown('<div class="sous-titre-calli">Missions Tribu</div>', unsafe_allow_html=True)
        mq, mt = st.columns(2)
        qui = mq.selectbox("Qui ?", ["Enfant 1 👦", "Enfant 2 👧", "Maman 🌸", "Papa 👔"])
        mis = mt.selectbox("Quoi ?", ["🍽️ Vaisselle", "🗑️ Poubelles", "🧹 Ménage", "🔌 Aspi"])
        if st.button("🚀 Valider"):
            save_gs("Menage", [mis, datetime.now().strftime("%d/%m/%Y"), qui]); st.rerun()

# --- COURSES (AVEC FAVORIS) ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    favs = ["🍞 Pain", "🥛 Lait", "🍎 Fruits", "🍚 Riz", "🧻 Papier toilette"]
    f_cols = st.columns(len(favs))
    for i, f in enumerate(favs):
        if f_cols[i].button(f): st.session_state.shopping.append(f); st.rerun()
    
    it = st.text_input("Ajouter un article...")
    if st.button("Ajouter ➕"):
        if it: st.session_state.shopping.append(it); st.rerun()
    
    st.markdown('<div class="post-it-yellow"><b>À ACHETER :</b><br>', unsafe_allow_html=True)
    for i, val in enumerate(st.session_state.shopping):
        c_i1, c_i2 = st.columns([5, 1])
        c_i1.write(f"☐ {val}")
        if c_i2.button("❌", key=f"del_{i}"): st.session_state.shopping.pop(i); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
