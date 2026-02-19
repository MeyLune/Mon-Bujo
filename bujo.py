import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import calendar
import pandas as pd

# --- 1. CONNEXION (Version Nickel Inchangée) ---
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

# --- 2. FONCTIONS DE GESTION (Version Nickel Inchangée) ---
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

# --- 3. STYLE & DESIGN (Dégradé Diagonal + Fix iPad) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Great+Vibes&display=swap');
    
    :root { 
        --rose: #F48FB1; --sapin: #1B3022; --peche: #FFAB91; 
        --menthe: #B2DFDB; --menthe-claire: #E0F2F1; 
    }

    /* Dégradé Diagonal Rose vers Menthe */
    .stApp { 
        background: linear-gradient(135deg, #FCE4EC 0%, #F48FB1 35%, #B2DFDB 100%) !important; 
    }

    .titre-calli { font-family: 'Great Vibes', cursive !important; font-size: 4.5rem; color: var(--sapin); text-align: center; }
    .sous-titre-calli { font-family: 'Dancing Script', cursive !important; font-size: 2.8rem; color: var(--sapin); }
    
    /* Onglets stylisés */
    .stTabs [data-baseweb="tab-list"] button { 
        font-family: 'Dancing Script', cursive !important; 
        font-size: 1.8rem !important; 
        color: var(--sapin) !important; 
    }

    /* Forçage anti-noir pour iPad */
    input, textarea, [data-baseweb="input"], [data-baseweb="select"] > div {
        background-color: var(--menthe-claire) !important;
        color: var(--sapin) !important;
        border: 2px solid var(--menthe) !important;
        border-radius: 12px !important;
    }

    /* Boutons Roses */
    .stButton>button {
        background-color: var(--rose) !important;
        color: white !important;
        border-radius: 15px !important;
        border: none !important;
        font-weight: bold !important;
    }

    /* CALENDRIER EN GRILLE HTML (Alignement Indestructible) */
    .cal-table {
        width: 100%; border-collapse: collapse; font-family: 'Courier New', Courier, monospace;
        color: var(--sapin) !important; background: rgba(255, 255, 255, 0.5); border-radius: 0 0 15px 15px;
    }
    .cal-table th { border-bottom: 1px solid var(--menthe); padding: 5px; font-size: 0.8rem; font-weight: bold; }
    .cal-table td { text-align: center; padding: 6px; font-size: 0.9rem; }
    .cal-header-box {
        background: var(--menthe); color: var(--sapin); text-align: center;
        padding: 10px; border-radius: 15px 15px 0 0; font-family: 'Dancing Script', cursive !important;
        font-size: 1.6rem; margin-top: 15px;
    }
    .marked-day { background-color: var(--rose); color: white !important; border-radius: 50%; font-weight: bold; }

    .post-it { 
        background: white; border-radius: 15px; padding: 15px; margin-bottom: 10px; 
        border-left: 8px solid var(--rose); box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

if 'shop' not in st.session_state: st.session_state.shop = []

st.markdown('<div class="titre-calli">🌸 L\'Univers de MeyLune</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- TAB 1: JOURNAL (Nickel) ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("...", height=150, key="j_in", label_visibility="collapsed")
        if st.button("💾 Sauver pensée", key="bj"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data[-3:])):
            idx = len(j_data)-1-i
            st.markdown(f'<div class="post-it">{e.get("Texte")}</div>', unsafe_allow_html=True)
            if st.button("🗑️", key=f"dj_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("...", height=150, key="g_in", label_visibility="collapsed")
        if st.button("🙏 Sauver gratitude", key="bg"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data[-3:])):
            idx_g = len(g_data)-1-i
            st.markdown(f'<div class="post-it" style="border-left-color: #D4AF37;">{e.get("Texte")}</div>', unsafe_allow_html=True)
            if st.button("🗑️ ", key=f"dg_{idx_g}"): delete_gs("Gratitude", idx_g); st.rerun()

# --- TAB 2: SEMAINE (iPad Nickel) ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    end = start + timedelta(days=6)
    st.markdown(f'<div style="text-align:center; color:var(--sapin); font-family:\'Dancing Script\'; font-size:2.8rem;">Semaine du {start.strftime("%d/%m")} au {end.strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    s_data = load_gs("Semaine")
    r1, r2 = st.columns(4), st.columns(3)
    all_cols = r1 + r2
    for i, j in enumerate(jours):
        d_str = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with all_cols[i]:
            st.markdown(f'<div style="background:var(--menthe); padding:10px; border-radius:10px; text-align:center; font-weight:bold;">{j}</div>', unsafe_allow_html=True)
            p_in = st.text_area("Planning", key=f"p_{i}", height=100)
            m_in = st.text_input("Menu 🍴", key=f"m_{i}")
            if st.button("💾", key=f"s_{i}"): save_gs("Semaine", [d_str, p_in, m_in]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == d_str:
                    if row.get('Planning'): st.info(row.get('Planning'))
                    if row.get('Menu'): st.success(row.get('Menu'))

# --- TAB 3: ANNEE (Correction Alignement Grille) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier Annuel 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m = r*3 + c + 1
            with cols[c]:
                st.markdown(f'<div class="cal-header-box">{calendar.month_name[m].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m)
                html = '<table class="cal-table"><tr><th>Lu</th><th>Ma</th><th>Me</th><th>Je</th><th>Ve</th><th>Sa</th><th>Di</th></tr>'
                for week in cal:
                    html += '<tr>'
                    for day in week:
                        if day == 0: html += '<td></td>'
                        else:
                            is_m = f"{m}-{day}" in marked
                            style = 'class="marked-day"' if is_m else ''
                            html += f'<td {style}>{get_circled_num(day) if is_m else day}</td>'
                    html += '</tr>'
                html += '</table>'
                st.markdown(html, unsafe_allow_html=True)
    with st.expander("📌 Ajouter une date importante"):
        c_da, c_ev = st.columns([1,2])
        d_imp = c_da.date_input("Date")
        e_imp = c_ev.text_input("Événement")
        if st.button("Enregistrer l'événement"): save_gs("Evenements", [d_imp.strftime("%d/%m/%Y"), e_imp]); st.rerun()

# --- TAB 4: TRACKERS (Nickel) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS"])
    with tr_tabs[0]:
        st.markdown('<div class="sous-titre-calli">Fiche de Lecture</div>', unsafe_allow_html=True)
        cl1, cl2 = st.columns(2)
        l_t, l_a = cl1.text_input("Titre"), cl2.text_input("Auteur")
        l_g = st.selectbox("Genre", ["Roman", "Bien-être", "Cuisine", "Thriller", "BD"])
        l_n = st.select_slider("Note ⭐", options=[1,2,3,4,5], value=5)
        l_av = st.text_area("Avis")
        if st.button("💾 Enregistrer Livre"):
            save_gs("Lecture", [datetime.now().strftime("%d/%m/%Y"), l_t, l_a, l_g, l_n, l_av]); st.rerun()
        for b in reversed(load_gs("Lecture")[-5:]):
            with st.expander(f"📔 {b.get('Titre')} - {b.get('Auteur')}"):
                st.write(f"**Genre:** {b.get('Genre')} | **Note:** {b.get('Note')}⭐")
                st.write(f"**Avis:** {b.get('Avis', b.get('Citation'))}")
    with tr_tabs[1]:
        st.markdown('<div class="sous-titre-calli">Bilan Santé</div>', unsafe_allow_html=True)
        eau = st.slider("Verres d'eau 💧", 0, 12, 6)
        hum = st.select_slider("Humeur", options=["☀️", "🌤️", "☁️", "🌧️", "⛈️"])
        if st.button("Sauver Bilan"): save_gs("Sante", [datetime.now().strftime("%d/%m/%Y"), "", eau, hum]); st.success("Ok !")
    with tr_tabs[2]:
        st.markdown('<div class="sous-titre-calli">Missions Tribu</div>', unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns(3)
        mq, ma, mj = cm1.selectbox("Qui ?", ["Maman", "Papa", "Enfants"]), cm2.selectbox("Action", ["Vaisselle", "Linge", "Poubelles", "Ménage"]), cm3.selectbox("Jour", jours)
        if st.button("🚀 Valider"): save_gs("Menage", [mj, ma, mq]); st.rerun()
        df_m = pd.DataFrame(load_gs("Menage"))
        if not df_m.empty: st.table(df_m.tail(7))

# --- TAB 5: COURSES (Nickel Stickers) ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    favs = ["🍞 Pain", "🥛 Lait", "🥚 Oeufs", "🍎 Fruits", "🍝 Pâtes"]
    cols_f = st.columns(len(favs))
    for i, f in enumerate(favs):
        if cols_f[i].button(f, key=f"f_{i}"): st.session_state.shop.append(f)
    it = st.text_input("Autre article...", key="sh_in")
    if st.button("➕ Ajouter"):
        if it: st.session_state.shop.append(it); st.rerun()
    for i, item in enumerate(st.session_state.shop):
        ca, cb = st.columns([8, 1])
        ca.info(f"🛒 {item}")
        if cb.button("🗑️", key=f"dc_{i}"): st.session_state.shop.pop(i); st.rerun()
