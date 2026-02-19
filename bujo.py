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

# --- 2. DESIGN IPAD FORCE (DÉGRADÉ + ANTI-NOIR) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&display=swap');
    :root { --rose: #F48FB1; --sapin: #1B3022; --vert: #B2DFDB; --or: #D4AF37; }
    
    .stApp { 
        background: linear-gradient(180deg, #fce4ec 0%, #e0f2f1 100%) !important;
        background-attachment: fixed !important;
    }

    /* Force le blanc sur iPad */
    div[data-baseweb="select"], div[data-baseweb="input"], input, textarea, select, .stSelectbox {
        background-color: white !important;
        color: black !important;
        border: 2px solid var(--rose) !important;
    }

    .titre-calli { font-family: 'Dancing Script'; font-size: 3.5rem; color: var(--sapin); text-align: center; }
    .sous-titre-calli { font-family: 'Dancing Script'; font-size: 2.2rem; color: var(--sapin); }
    
    .mission-box {
        background: white; border: 2px solid var(--rose); border-radius: 12px;
        padding: 10px; margin-bottom: 10px; min-height: 130px;
    }
    .post-it { 
        background: #fffde7; border-left: 10px solid var(--or); padding: 15px; border-radius: 5px; color: black;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- ✍️ JOURNAL & GRATITUDE ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data = load_gs("Journal")
    g_data = load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("Ma pensée...", key="j_in", height=100, label_visibility="collapsed")
        if st.button("💾 Sauver"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data)):
            st.markdown(f'<div style="background:white; padding:10px; border-left:5px solid var(--rose); margin-bottom:5px; border-radius:10px;">{e.get("Texte")}</div>', unsafe_allow_html=True)
            if st.button("🗑️", key=f"dj_{i}"): delete_gs("Journal", len(j_data)-1-i); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("Merci pour...", key="g_in", height=100, label_visibility="collapsed")
        if st.button("🙏 Sauver"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()

# --- 🗓️ SEMAINE ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    s_data = load_gs("Semaine")
    cols = st.columns(7)
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    for i, j in enumerate(jours):
        curr_d = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div style="background:var(--vert); text-align:center; font-weight:bold; border-radius:10px; padding:5px;">{j}</div>', unsafe_allow_html=True)
            p_in = st.text_area("Note", key=f"p_{i}", height=100, label_visibility="collapsed")
            m_in = st.text_input("🍴 Menu", key=f"m_{i}", label_visibility="collapsed")
            if st.button("💾", key=f"s_{i}"):
                save_gs("Semaine", [curr_d, p_in, m_in]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == curr_d:
                    st.markdown(f"<small>• {row.get('Planning')}<br>🍴 {row.get('Menu')}</small>", unsafe_allow_html=True)

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
                st.markdown(f'<div style="background:var(--rose); color:white; text-align:center; border-radius:10px 10px 0 0;">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m_idx)
                res = "Lu Ma Me Je Ve Sa Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "   "
                        else: line += f"{get_circled_num(d)} " if f"{m_idx}-{d}" in marked else f"{d:2} "
                    res += line + "\n"
                st.markdown(f'<div style="font-family:monospace; background:white; padding:10px; border:1px solid var(--rose); border-radius:0 0 10px 10px; white-space:pre; text-align:center;">{res}</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📍 Ajouter / Gérer Événements")
    ce1, ce2 = st.columns(2)
    dev = ce1.date_input("Date")
    nev = ce2.text_input("Nom")
    if st.button("Marquer"): save_gs("Evenements", [dev.strftime("%d/%m/%Y"), nev]); st.rerun()
    for i, e in enumerate(evs):
        col_a, col_b = st.columns([5,1])
        col_a.write(f"📅 {e.get('Date')} : {e.get('Evenement')}")
        if col_b.button("🗑️", key=f"dev_{i}"): delete_gs("Evenements", i); st.rerun()

# --- 📊 TRACKERS (LECTURE + MISSIONS) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 BIBLIOTHÈQUE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS TRIBU"])
    with tr_tabs[0]:
        st.markdown('<div class="sous-titre-calli">Ma Fiche de Lecture</div>', unsafe_allow_html=True)
        cl1, cl2 = st.columns(2)
        titre = cl1.text_input("Titre", key="l_t")
        auteur = cl1.text_input("Auteur", key="l_a")
        note = cl2.slider("Note / 10", 0, 10, 5)
        avis = st.text_area("Mon Avis", key="l_av")
        if st.button("💾 Enregistrer"):
            save_gs("Lectures", [datetime.now().strftime("%d/%m/%Y"), titre, auteur, note, avis]); st.rerun()
        if st.checkbox("📖 Voir historique bibliothèque"):
            for b in reversed(load_gs("Lectures")):
                st.write(f"**{b.get('Titre')}** - {b.get('Auteur')} ({b.get('Note')}/10)")

    with tr_tabs[2]:
        st.markdown('<div class="sous-titre-calli">Missions de la Tribu</div>', unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns(3)
        qui = cm1.selectbox("Qui ?", ["Enfant 1 👦", "Enfant 2 👧", "Enfant 3 👶", "Maman 🌸", "Papa 👔"], key="t_q")
        dm = cm2.date_input("Date", key="t_d")
        tm = cm3.selectbox("Mission ?", ["🍽️ Vaisselle", "🗑️ Poubelles", "🧹 Balai", "🔌 Aspirateur", "🧼 Serpillière", "✨ Poussière", "🥣 Débarrasser", "🚿 Salle de bain", "🧸 Chambres"], key="t_m")
        if st.button("🚀 Valider mission"):
            save_gs("Menage", [tm, dm.strftime("%d/%m/%Y"), qui]); st.rerun()
        
        m_data = load_gs("Menage")
        st.write("---")
        # Affichage en 2 lignes pour iPad
        jours_m = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        r1 = st.columns(4)
        for i in range(4):
            ds = (start + timedelta(days=i)).strftime("%d/%m/%Y")
            with r1[i]:
                st.markdown(f'<div class="mission-box"><center><b>{jours_m[i]}</b><br><small>{ds[:5]}</small></center>', unsafe_allow_html=True)
                for m in m_data:
                    if m.get('Lundi') == ds:
                        st.markdown(f'<div style="background:var(--vert); font-size:0.8rem; border-radius:5px; padding:2px; margin-top:2px; text-align:center;">{m.get("Tache")}<br><b>{m.get("Mardi")}</b></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        r2 = st.columns(3)
        for i in range(4, 7):
            ds = (start + timedelta(days=i)).strftime("%d/%m/%Y")
            with r2[i-4]:
                st.markdown(f'<div class="mission-box"><center><b>{jours_m[i]}</b><br><small>{ds[:5]}</small></center>', unsafe_allow_html=True)
                for m in m_data:
                    if m.get('Lundi') == ds:
                        st.markdown(f'<div style="background:var(--vert); font-size:0.8rem; border-radius:5px; padding:2px; margin-top:2px; text-align:center;">{m.get("Tache")}<br><b>{m.get("Mardi")}</b></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# --- 🛒 COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    cl, cr = st.columns(2)
    with cl:
        for f in ["🍞 Pain", "🥛 Lait", "🍎 Fruits", "🍚 Riz", "🥣 Céréales"]:
            if st.button(f"+ {f}"): st.session_state.shopping.append(f); st.rerun()
    with cr:
        st.markdown('<div class="post-it"><b>📝 À ACHETER :</b><br>', unsafe_allow_html=True)
        for it in st.session_state.shopping:
            st.write(f"☐ {it}")
        st.markdown('</div>', unsafe_allow_html=True)
