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

# Initialisation vitale pour corriger l'erreur rouge des captures
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

# --- 2. STYLE "ULTRA-LISIBLE" (ANTI-BUG IPAD) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&display=swap');
    :root { --rose: #F48FB1; --sapin: #1B3022; --vert: #B2DFDB; --or: #D4AF37; }
    
    .stApp { background: linear-gradient(180deg, #fce4ec 0%, #e0f2f1 100%) !important; }

    /* FORCE LE TEXTE NOIR PARTOUT (CHAMPS & BOUTONS) */
    input, textarea, select, div[data-baseweb="select"], div[data-baseweb="input"], .stButton button {
        background-color: white !important;
        color: #1B3022 !important;
        -webkit-text-fill-color: #1B3022 !important;
        border: 2px solid var(--rose) !important;
        font-weight: bold !important;
    }

    /* Calendrier Annuel - Correction Visibilité */
    .cal-box {
        font-family: 'Courier New', monospace;
        background: white !important;
        color: #000000 !important;
        padding: 10px;
        border-radius: 0 0 10px 10px;
        border: 1px solid var(--rose);
        white-space: pre;
        text-align: center;
        font-size: 0.9rem;
    }

    .titre-calli { font-family: 'Dancing Script'; font-size: 3.5rem; color: var(--sapin); text-align: center; }
    .sous-titre-calli { font-family: 'Dancing Script'; font-size: 2.2rem; color: var(--sapin); }
    .post-it { background: #fffde7; border-left: 10px solid var(--or); padding: 15px; color: black; border-radius: 5px; }
    
    /* Style pour les stickers missions */
    .sticker-mission { background: var(--vert); color: black !important; padding: 5px; border-radius: 8px; border: 1px solid var(--rose); text-align: center; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- TAB 1 : JOURNAL ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("...", height=100, key="j_in", label_visibility="collapsed")
        if st.button("Enregistrer pensée", key="j_btn"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data)):
            st.markdown(f'<div style="background:white; padding:10px; border-left:5px solid var(--rose); border-radius:10px; margin-bottom:5px; color:black;">{e.get("Texte", e.get("Note", ""))}</div>', unsafe_allow_html=True)
            if st.button("🗑️", key=f"dj_{i}"): delete_gs("Journal", len(j_data)-1-i); st.rerun()

# --- TAB 2 : SEMAINE ---
with tabs[1]:
    start_w = datetime.now().date() - timedelta(days=datetime.now().weekday())
    s_data = load_gs("Semaine")
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    cols = st.columns(7)
    for i, j in enumerate(jours):
        d_str = (start_w + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div style="background:var(--vert); text-align:center; border-radius:5px; padding:2px; color:black;"><b>{j}</b></div>', unsafe_allow_html=True)
            p = st.text_area("Plan", key=f"p_{i}", height=80, label_visibility="collapsed")
            m = st.text_input("🍴", key=f"m_{i}", label_visibility="collapsed")
            if st.button("💾", key=f"sb_{i}"): save_gs("Semaine", [d_str, p, m]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == d_str:
                    st.markdown(f"<small style='color:black;'>• {row.get('Planning','')}<br><b>🍴 {row.get('Menu','')}</b></small>", unsafe_allow_html=True)

# --- TAB 3 : ANNEE (CALENDRIER FIXÉ) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    for r in range(4):
        m_cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with m_cols[c]:
                st.markdown(f'<div style="background:var(--rose); color:white; text-align:center; border-radius:10px 10px 0 0; padding:5px;"><b>{calendar.month_name[m_idx].upper()}</b></div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m_idx)
                res = "Lu Ma Me Je Ve Sa Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "   "
                        else: line += f"{get_circled_num(d)} " if f"{m_idx}-{d}" in marked else f"{d:2} "
                    res += line + "\n"
                st.markdown(f'<div class="cal-box">{res}</div>', unsafe_allow_html=True)
    st.write("---")
    st.markdown("### 📍 Ajouter un événement")
    ce1, ce2 = st.columns(2)
    ev_d = ce1.date_input("Date", key="new_ev_date")
    ev_n = ce2.text_input("Nom de l'événement", key="new_ev_name")
    if st.button("Marquer au calendrier"):
        save_gs("Evenements", [ev_d.strftime("%d/%m/%Y"), ev_n]); st.rerun()

# --- TAB 4 : TRACKERS (BIBLIO, BIEN-ÊTRE, MISSIONS) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 BIBLIOTHÈQUE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS TRIBU"])
    
    with tr_tabs[1]: # Santé
        st.markdown('<div class="sous-titre-calli">Mon Équilibre</div>', unsafe_allow_html=True)
        humeur = st.selectbox("Humeur", ["Radieuse ☀️", "Paisible ☁️", "Fatiguée 🔋", "Sensible 🌙"])
        eau = st.slider("Verres d'eau 💧", 0, 12, 4)
        if st.button("Sauver Bien-être"):
            save_gs("Sante", [datetime.now().strftime("%d/%m/%Y"), humeur, eau]); st.success("Santé enregistrée !")

    with tr_tabs[2]: # Missions
        st.markdown('<div class="sous-titre-calli">Missions de la Tribu</div>', unsafe_allow_html=True)
        m_data = load_gs("Menage")
        q_m = st.selectbox("Qui ?", ["Enfant 1 👦", "Enfant 2 👧", "Enfant 3 👶", "Maman 🌸", "Papa 👔"], key="q_m")
        t_m = st.selectbox("Mission ?", ["🍽️ Vaisselle", "🗑️ Poubelles", "🧹 Balai", "🔌 Aspirateur"], key="t_m")
        d_m = st.date_input("Date", key="d_m")
        if st.button("Valider Mission"):
            save_gs("Menage", [t_m, d_m.strftime("%d/%m/%Y"), q_m]); st.rerun()
        
        st.write("---")
        for r_idx in [0, 4]:
            r_cols = st.columns(4)
            for i in range(4):
                if r_idx + i < 7:
                    ds = (start_w + timedelta(days=r_idx + i)).strftime("%d/%m/%Y")
                    with r_cols[i]:
                        st.markdown(f'<div style="background:white; border:2px solid var(--rose); border-radius:10px; padding:10px; min-height:120px; color:black;"><center><b>{jours[r_idx+i]}</b><br><small>{ds[:5]}</small></center>', unsafe_allow_html=True)
                        for m in m_data:
                            if ds in str(m.values()):
                                st.markdown(f'<div class="sticker-mission">{m.get("Tache", m.get("Mission",""))}<br><b>{m.get("Mardi", m.get("Qui",""))}</b></div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 5 : COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    it = st.text_input("Produit à ajouter...", key="new_it")
    if st.button("Ajouter à la liste"):
        if it: st.session_state.shopping.append(it); st.rerun()
    if st.button("Vider tout 🗑️"):
        st.session_state.shopping = []; st.rerun()
    
    st.markdown('<div class="post-it"><b>📝 À ACHETER :</b><br><br>', unsafe_allow_html=True)
    for i, val in enumerate(st.session_state.shopping):
        c_i1, c_i2 = st.columns([5, 1])
        c_i1.write(f"☐ {val}")
        if c_i2.button("❌", key=f"del_it_{i}"):
            st.session_state.shopping.pop(i); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
