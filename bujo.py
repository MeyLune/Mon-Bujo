import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import calendar

# --- 1. CONNEXION & LOGIQUE ---
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

# --- 2. STYLE ET POLICE ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@400;700&display=swap');
    
    :root { --rose: #F48FB1; --sapin: #1B3022; --peche: #FFCCBC; --vert: #B2DFDB; }

    .stApp { 
        background: linear-gradient(180deg, #FFCCBC 0%, #FCE4EC 40%, #FFFFFF 100%) !important;
    }

    /* POLICE PARTOUT */
    * { font-family: 'Comfortaa', sans-serif !important; color: #1B3022 !important; }
    .titre-calli { font-family: 'Dancing Script' !important; font-size: 3.8rem; color: var(--sapin); text-align: center; margin-bottom: 20px; }
    .sous-titre-calli { font-family: 'Dancing Script' !important; font-size: 2.5rem; color: var(--sapin); }

    /* FIX INPUTS NOIRS */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, textarea, input {
        background-color: white !important;
        color: #1B3022 !important;
        border: 2px solid var(--rose) !important;
        -webkit-text-fill-color: #1B3022 !important;
    }

    /* BOUTONS */
    .stButton>button {
        background-color: white !important;
        border: 2px solid var(--rose) !important;
        border-radius: 20px !important;
        color: #1B3022 !important;
        font-weight: bold !important;
    }

    .card-jour { background: rgba(255,255,255,0.8); border: 2px solid var(--rose); border-radius: 20px; padding: 15px; margin-bottom: 10px; min-height: 250px; }
    .header-jour { background: var(--vert); color: var(--sapin); text-align: center; font-weight: bold; border-radius: 10px; padding: 5px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

if 'shopping' not in st.session_state: st.session_state.shopping = []

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- TAB 1 : JOURNAL ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("Aujourd'hui...", height=150, key="j_in", label_visibility="collapsed")
        if st.button("💾 Sauvegarder", key="j_btn"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data[-5:])):
            idx = len(j_data)-1-i
            st.info(e.get("Texte", ""))
            if st.button("🗑️", key=f"dj_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("Reconnaissante pour...", height=150, key="g_in", label_visibility="collapsed")
        if st.button("🙏 Enregistrer", key="g_btn"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        st.markdown('<div style="background:#FFF9C4; padding:20px; border-left:10px solid #D4AF37; border-radius:10px;"><b>Mes petits bonheurs :</b><br>', unsafe_allow_html=True)
        for e in reversed(g_data[-5:]): st.write(f"• {e.get('Texte','')}")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2 : SEMAINE (DÉCOMPACTÉ) ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    end = start + timedelta(days=6)
    st.markdown(f'<div style="text-align:center;"><b>Semaine du {start.strftime("%d/%m")} au {end.strftime("%d/%m/%Y")}</b></div>', unsafe_allow_html=True)
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    s_data = load_gs("Semaine")
    
    cols = st.columns(7)
    for i, j in enumerate(jours):
        d_str = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div class="card-jour"><div class="header-jour">{j}</div>', unsafe_allow_html=True)
            p_in = st.text_area("Note", key=f"p_{i}", height=100, label_visibility="collapsed", placeholder="Planning")
            m_in = st.text_input("🍴", key=f"m_{i}", label_visibility="collapsed", placeholder="Menu")
            c_s1, c_s2 = st.columns(2)
            if c_s1.button("💾", key=f"sv_{i}"): save_gs("Semaine", [d_str, p_in, m_in]); st.rerun()
            if c_s2.button("🗑️", key=f"cl_{i}"): # Simulation d'effaçage (envoi ligne vide)
                save_gs("Semaine", [d_str, "", ""]); st.rerun()
            
            for row in s_data:
                if str(row.get("Date")) == d_str:
                    st.markdown(f"<small>• {row.get('Planning','')}<br><b>🍴 {row.get('Menu','')}</b></small>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3 : ANNEE (ÉVÉNEMENTS RÉTABLIS) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    
    # Formulaire d'ajout
    with st.expander("📅 Ajouter une Date Importante"):
        ce1, ce2, ce3 = st.columns([2,3,1])
        new_d = ce1.date_input("Date")
        new_e = ce2.text_input("Événement / Anniversaire")
        if ce3.button("Ajouter"):
            save_gs("Evenements", [new_d.strftime("%d/%m/%Y"), new_e]); st.rerun()

    for r in range(4):
        cols_a = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_a[c]:
                st.markdown(f'<div style="background:var(--rose); color:white !important; text-align:center; border-radius:10px 10px 0 0;">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m_idx)
                res = "Lu Ma Me Je Ve Sa Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "   "
                        else: line += f"{get_circled_num(d)} " if f"{m_idx}-{d}" in marked else f"{d:2} "
                    res += line + "\n"
                st.markdown(f'<div style="font-family:monospace; background:white; padding:10px; border:1px solid var(--rose); border-radius:0 0 10px 10px; white-space:pre; text-align:center; font-size:0.8rem;">{res}</div>', unsafe_allow_html=True)

# --- TAB 4 : TRACKERS DÉTAILLÉS ---
with tabs[3]:
    tr_t = st.tabs(["📚 LECTURE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS TRIBU"])
    
    with tr_t[0]: # Lecture détaillée
        st.markdown('<div class="sous-titre-calli">Ma Bibliothèque</div>', unsafe_allow_html=True)
        c_l1, c_l2 = st.columns(2)
        titre = c_l1.text_input("Titre du livre")
        auteur = c_l1.text_input("Auteur")
        genre = c_l2.selectbox("Genre", ["Roman", "Bien-être", "Cuisine", "Travail"])
        note = c_l2.select_slider("Note", range(11), value=5)
        citation = st.text_area("Citation ou note marquante")
        if st.button("💾 Sauver Livre"):
            save_gs("Lecture", [datetime.now().strftime("%d/%m/%Y"), titre, auteur, genre, note, citation]); st.success("Ajouté !")

    with tr_t[1]: # Bien-être complet
        st.markdown('<div class="sous-titre-calli">Mon Équilibre</div>', unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        sport = cs1.text_input("Sport quotidien (Marche, Yoga, etc.)")
        migraine = cs2.select_slider("Suivi Migraine", options=["Aucune", "Légère", "Moyenne", "Forte", "Crise"])
        humeur = st.selectbox("Humeur", ["Radieuse ☀️", "Paisible ☁️", "Fatiguée 🔋", "Stressée 🌙"])
        eau = st.slider("Verres d'eau 💧", 0, 15, 6)
        if st.button("💾 Sauver Santé"):
            save_gs("Sante", [datetime.now().strftime("%d/%m/%Y"), sport, migraine, humeur, eau]); st.success("Bilan enregistré !")

    with tr_t[2]: # Missions Tribu (Qui / Quoi / Jour)
        st.markdown('<div class="sous-titre-calli">Gestion de la Tribu</div>', unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns(3)
        m_qui = cm1.selectbox("Qui ?", ["Maman 🌸", "Papa 👔", "Enfant 1 👦", "Enfant 2 👧", "Enfant 3 👶"])
        m_quoi = cm2.selectbox("Tâche ?", ["🍽️ Vaisselle", "🗑️ Poubelles", "🧹 Ménage", "🔌 Aspirateur", "🧺 Linge"])
        m_jour = cm3.selectbox("Jour ?", jours)
        if st.button("🚀 Valider la Mission"):
            # Ici on peut soit updater le tableau existant, soit sauver une nouvelle ligne
            save_gs("Menage_Log", [m_jour, m_quoi, m_qui]); st.rerun()
        
        st.write("---")
        m_log = load_gs("Menage_Log")
        cols_m = st.columns(7)
        for idx, j_n in enumerate(jours):
            with cols_m[idx]:
                st.markdown(f"**{j_n}**")
                for entry in m_log:
                    if entry.get("Jour") == j_n:
                        st.markdown(f"<div style='background:var(--vert); padding:5px; border-radius:5px; font-size:0.7rem;'>{entry.get('Tache')}<br><b>{entry.get('Qui')}</b></div>", unsafe_allow_html=True)

# --- TAB 5 : COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    rapide = ["🍞 Pain", "🥛 Lait", "🍎 Fruits", "🍝 Pâtes", "🍚 Riz"]
    cr = st.columns(len(rapide))
    for i, r in enumerate(rapide):
        if cr[i].button(r, key=f"fav_{i}"): st.session_state.shopping.append(r); st.rerun()
    
    it = st.text_input("Autre chose ?", key="c_in")
    if st.button("➕ Ajouter"):
        if it: st.session_state.shopping.append(it); st.rerun()
    
    st.markdown("---")
    for i, item in enumerate(st.session_state.shopping):
        ca, cb = st.columns([5, 1])
        ca.checkbox(item, key=f"ch_{i}")
        if cb.button("🗑️", key=f"del_{i}"): st.session_state.shopping.pop(i); st.rerun()
