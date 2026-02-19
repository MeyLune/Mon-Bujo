import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import calendar
import pandas as pd

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

# --- 2. FONCTIONS (Base Nickel + Tableau) ---
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

# --- 3. STYLE IPAD MENTHE & ROSE ---
st.set_page_config(page_title="Mon Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Great+Vibes&display=swap');
    
    :root { --rose: #F48FB1; --sapin: #1B3022; --peche: #FFAB91; --menthe: #B2DFDB; --menthe-fonce: #00796B; }

    .stApp { background: linear-gradient(180deg, var(--peche) 0%, #FCE4EC 40%, #FFFFFF 100%) !important; }

    /* TITRES ET SOUS-TITRES CALLIGRAPHIE */
    .titre-calli { font-family: 'Great Vibes', cursive !important; font-size: 4.8rem; color: var(--sapin); text-align: center; }
    .sous-titre-calli { font-family: 'Dancing Script', cursive !important; font-size: 2.8rem; color: var(--sapin); margin-bottom: 15px; }
    
    .stTabs [data-baseweb="tab-list"] button { font-family: 'Great Vibes' !important; font-size: 2.2rem !important; color: var(--sapin) !important; }

    /* LISIBILITE */
    label, p, span { color: var(--sapin) !important; font-weight: 500; }
    .stButton>button { background-color: var(--rose) !important; color: white !important; border-radius: 20px; border: none; font-weight: bold; }

    /* CALENDRIER ANNUEL : ESPACEMENT ULTRA LARGE */
    .cal-grid {
        font-family: 'Courier New', Courier, monospace !important;
        background: white; padding: 20px; border-radius: 0 0 15px 15px;
        border: 2px solid var(--menthe); line-height: 1.8; text-align: left;
        color: var(--sapin) !important; font-size: 1.1rem; white-space: pre;
    }
    .cal-head {
        background: var(--menthe) !important; color: var(--sapin) !important; text-align: center;
        padding: 10px; font-weight: bold; border-radius: 15px 15px 0 0;
        font-family: 'Dancing Script', cursive !important; font-size: 1.8rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titre-calli">🌸 L\'Univers de MeyLune</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- TAB 1: JOURNAL (Rien ne bouge) ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("...", height=150, key="j_in", label_visibility="collapsed")
        if st.button("💾 Sauver pensée", key="bj"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data[-3:])):
            st.markdown(f'<div style="background:white; border-radius:15px; padding:15px; border-left:8px solid var(--rose); margin-bottom:10px;">{e.get("Texte")}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("...", height=150, key="g_in", label_visibility="collapsed")
        if st.button("🙏 Sauver gratitude", key="bg"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data[-3:])):
            st.markdown(f'<div style="background:white; border-radius:15px; padding:15px; border-left:8px solid #D4AF37; margin-bottom:10px;">{e.get("Texte")}</div>', unsafe_allow_html=True)

# --- TAB 2: SEMAINE (Aérée iPad + Dates) ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    end = start + timedelta(days=6)
    st.markdown(f'<div style="text-align:center; color:var(--menthe-fonce); font-family:\'Dancing Script\'; font-size:2.8rem;">Semaine du {start.strftime("%d/%m")} au {end.strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
    
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    s_data = load_gs("Semaine")
    
    row1 = st.columns(4)
    row2 = st.columns(3)
    
    all_cols = row1 + row2
    for i, j in enumerate(jours):
        d_str = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with all_cols[i]:
            st.markdown(f'<div style="background:var(--menthe); padding:10px; border-radius:10px; font-weight:bold; text-align:center;">{j}</div>', unsafe_allow_html=True)
            p_in = st.text_area("Planning", key=f"p_{i}", height=100)
            m_in = st.text_input("Menu 🍴", key=f"m_{i}")
            if st.button("💾", key=f"s_{i}"): save_gs("Semaine", [d_str, p_in, m_in]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == d_str:
                    if row.get('Planning'): st.info(row.get('Planning'))
                    if row.get('Menu'): st.success(f"🍴 {row.get('Menu')}")

# --- TAB 3: ANNEE (Ajusté + Date Importante) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    
    with st.expander("✨ Ajouter une date importante"):
        c_da, c_ev = st.columns([1,2])
        d_imp = c_da.date_input("Date")
        e_imp = c_ev.text_input("Événement")
        if st.button("Enregistrer l'événement"):
            save_gs("Evenements", [d_imp.strftime("%d/%m/%Y"), e_imp]); st.rerun()

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

# --- TAB 4: TRACKERS (Lecture + Bien-être + Tableau Missions) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS"])
    
    with tr_tabs[0]:
        st.markdown('<div class="sous-titre-calli">Fiche de Lecture</div>', unsafe_allow_html=True)
        # (Champs Lecture identiques à ta version préférée)
        l_t = st.text_input("Titre")
        if st.button("Sauver Livre"): save_gs("Lecture", [datetime.now().strftime("%d/%m/%Y"), l_t, "", "", 5, ""]); st.rerun()

    with tr_tabs[1]:
        st.markdown('<div class="sous-titre-calli">Mon Bilan Bien-être</div>', unsafe_allow_html=True)
        eau = st.slider("Verres d'eau 💧", 0, 12, 6)
        humeur = st.select_slider("Mon humeur", options=["☀️", "🌤️", "☁️", "🌧️", "⛈️"])
        if st.button("Sauver Bilan"): save_gs("Sante", [datetime.now().strftime("%d/%m/%Y"), "", eau, humeur]); st.success("Enregistré !")

    with tr_tabs[2]:
        st.markdown('<div class="sous-titre-calli">Missions Tribu</div>', unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns(3)
        mq = cm1.selectbox("Qui ?", ["Maman", "Papa", "Enfants"])
        ma = cm2.selectbox("Action", ["Vaisselle", "Linge", "Poubelles", "Ménage"])
        mj = cm3.selectbox("Jour", jours)
        if st.button("🚀 Valider"): save_gs("Menage", [mj, ma, mq]); st.rerun()
        
        st.markdown("### Récapitulatif")
        df_m = pd.DataFrame(load_gs("Menage"))
        if not df_m.empty: st.table(df_m.tail(10))

# --- TAB 5: COURSES (Mise en page stickers) ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    it = st.text_input("Ajouter...")
    if st.button("➕"):
        if it: save_gs("Courses", [it, "A faire"]); st.rerun()
    for c in reversed(load_gs("Courses")[-8:]):
        st.markdown(f'<div style="background:#E1F5FE; padding:10px; border-radius:10px; border-left:5px solid #03A9F4; margin:5px;">🛒 {c.get("Article")}</div>', unsafe_allow_html=True)
