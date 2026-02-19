import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import calendar
import pandas as pd

# --- 1. CONNEXION (Base de référence) ---
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

# --- 2. FONCTIONS (Base de référence) ---
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

# --- 3. STYLE & DESIGN (Optimisation iPad & Calligraphie) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Great+Vibes&display=swap');
    
    :root { 
        --rose: #F48FB1; --sapin: #1B3022; --peche: #FFAB91; 
        --menthe: #B2DFDB; --menthe-claire: #E0F2F1; 
    }

    /* Dégradé Diagonal */
    .stApp { background: linear-gradient(135deg, #FCE4EC 0%, #F48FB1 35%, #B2DFDB 100%) !important; }

    .titre-calli { font-family: 'Great Vibes', cursive !important; font-size: 4.5rem; color: var(--sapin); text-align: center; }
    .sous-titre-calli { font-family: 'Dancing Script', cursive !important; font-size: 2.8rem; color: var(--sapin); }
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] button { 
        font-family: 'Dancing Script', cursive !important; 
        font-size: 1.8rem !important; 
        color: var(--sapin) !important; 
    }

    /* Forçage Inputs & Menus Déroulants (Anti-Noir) */
    input, textarea, [data-baseweb="input"], [data-baseweb="select"] > div {
        background-color: var(--menthe-claire) !important;
        color: var(--sapin) !important;
        border: 2px solid var(--menthe) !important;
        border-radius: 12px !important;
        font-family: 'Dancing Script', cursive !important;
        font-size: 1.2rem !important;
    }

    /* Post-it Journal avec écriture calligraphiée Sapin */
    .post-it { 
        background: white; border-radius: 15px; padding: 18px; margin-bottom: 12px; 
        border-left: 10px solid var(--rose); box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
        font-family: 'Dancing Script', cursive !important;
        font-size: 1.4rem !important;
        color: var(--sapin) !important;
        line-height: 1.2;
    }

    /* Tableau Missions Contraste */
    .mission-table {
        background-color: var(--menthe-claire) !important;
        border-radius: 15px;
        padding: 10px;
        color: var(--sapin) !important;
    }

    .stButton>button { background-color: var(--rose) !important; color: white !important; border-radius: 15px !important; border: none !important; }

    /* Calendrier Grille */
    .cal-table { width: 100%; border-collapse: collapse; color: var(--sapin) !important; background: rgba(255, 255, 255, 0.5); border-radius: 0 0 15px 15px; }
    .cal-table th { border-bottom: 1px solid var(--menthe); padding: 5px; font-size: 0.8rem; }
    .cal-table td { text-align: center; padding: 6px; font-size: 0.9rem; }
    .marked-day { background-color: var(--rose); color: white !important; border-radius: 50%; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

if 'shop' not in st.session_state: st.session_state.shop = []

st.markdown('<div class="titre-calli">🌸 L\'Univers de MeyLune</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- TAB 1: JOURNAL (Calligraphie & Post-it Fix) ---
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

# --- TAB 2: SEMAINE (Inchangé) ---
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

# --- TAB 3: ANNEE (Base de référence) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier Annuel 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m = r*3 + c + 1
            with cols[c]:
                st.markdown(f'<div style="background:var(--menthe); text-align:center; padding:5px; border-radius:10px 10px 0 0; font-family:\'Dancing Script\';">{calendar.month_name[m].upper()}</div>', unsafe_allow_html=True)
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

# --- TAB 4: TRACKERS (Missions Mise à Jour) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS"])
    with tr_tabs[2]:
        st.markdown('<div class="sous-titre-calli">Missions Tribu</div>', unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns(3)
        mq = cm1.selectbox("Qui ?", ["Maman", "Papa", "Enfants"], key="mq")
        
        # Nouvelles Actions ajoutées
        actions_liste = [
            "Vaisselle", "Plier le linge", "Étendre le linge", 
            "Rangement chambre", "Nettoyage SdB/WC", "Nettoyage sol", 
            "Poubelles", "Cuisine"
        ]
        ma = cm2.selectbox("Action", actions_liste, key="ma")
        
        mj = cm3.selectbox("Jour", jours, key="mj")
        
        # Calcul de la date réelle du jour choisi dans la semaine en cours
        current_monday = datetime.now().date() - timedelta(days=datetime.now().weekday())
        target_date = current_monday + timedelta(days=jours.index(mj))
        
        if st.button("🚀 Valider Mission"):
            save_gs("Menage", [target_date.strftime("%d/%m/%Y"), ma, mq])
            st.rerun()
        
        st.markdown("### 📋 Récapitulatif")
        df_m = pd.DataFrame(load_gs("Menage"))
        if not df_m.empty:
            # Affichage contrasté
            st.markdown('<div class="mission-table">', unsafe_allow_html=True)
            st.table(df_m.tail(7))
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 5: COURSES (Inchangé) ---
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
