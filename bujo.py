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

# --- 2. STYLE & DESIGN (Spécial iPad & Rose Pêche) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@400;700&display=swap');
    
    :root { --rose: #F48FB1; --sapin: #1B3022; --peche: #FFAB91; --vert: #B2DFDB; --or: #D4AF37; }

    .stApp { 
        background: linear-gradient(180deg, var(--peche) 0%, #FCE4EC 40%, #E0F2F1 100%) !important;
        background-attachment: fixed;
    }

    /* POLICES CALLIGRAPHIQUES */
    .titre-calli, .sous-titre-calli, .stTabs button, .semaine-titre, label, .stMarkdown h3 {
        font-family: 'Dancing Script', cursive !important;
        color: var(--sapin) !important;
    }
    
    .titre-calli { font-size: 3.8rem; text-align: center; margin-bottom: 20px; }
    .sous-titre-calli { font-size: 2.8rem; margin-top: 15px; margin-bottom: 15px; }
    .stTabs button { font-size: 1.6rem !important; }

    /* TEXTE GENERAL (Anti-Blanc iPad) */
    p, span, div, li, .stMarkdown { 
        font-family: 'Comfortaa' !important; 
        color: #1B3022 !important; 
        -webkit-text-fill-color: #1B3022 !important;
    }

    /* INPUTS (Correction Noir iPad) */
    input, textarea, [data-baseweb="input"], [data-baseweb="select"] > div {
        background-color: white !important;
        color: #1B3022 !important;
        -webkit-text-fill-color: #1B3022 !important;
        border: 2px solid var(--rose) !important;
        border-radius: 15px !important;
    }

    /* BOUTONS */
    .stButton>button {
        background-color: white !important;
        border: 2px solid var(--rose) !important;
        border-radius: 20px !important;
        color: #1B3022 !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: var(--rose) !important; color: white !important; }

    /* CARTES & POST-ITS */
    .post-it { background: white; border-radius: 15px; padding: 15px; margin-bottom: 10px; border-left: 10px solid var(--rose); box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .card-jour { background: white; border: 2px solid var(--rose); border-radius: 20px; padding: 12px; min-height: 200px; }
    .header-jour { background: var(--vert); color: var(--sapin); text-align: center; font-weight: bold; border-radius: 10px; padding: 5px; margin-bottom: 10px; }
    
    .spacer { margin-top: 40px; }
</style>
""", unsafe_allow_html=True)

if 'shopping' not in st.session_state: st.session_state.shopping = []

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- 1. JOURNAL & GRATITUDE ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("Libère ton esprit...", height=120, key="j_in", label_visibility="collapsed")
        if st.button("💾 Sauver pensée", key="btn_j"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data[-5:])):
            idx = len(j_data)-1-i
            st.markdown(f'<div class="post-it">{e.get("Texte", "")}</div>', unsafe_allow_html=True)
            bc1, bc2 = st.columns([1, 5])
            if bc1.button("🗑️", key=f"dj_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("Petit bonheur...", height=120, key="g_in", label_visibility="collapsed")
        if st.button("🙏 Sauver gratitude", key="btn_g"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data[-5:])):
            idx_g = len(g_data)-1-i
            st.markdown(f'<div class="post-it" style="border-left-color: var(--or); background: #FFFDE7;"><i>{e.get("Texte", "")}</i></div>', unsafe_allow_html=True)
            if st.button("🗑️", key=f"dg_{idx_g}"): delete_gs("Gratitude", idx_g); st.rerun()

# --- 2. SEMAINE (AÉRÉ) ---
with tabs[1]:
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    end = start + timedelta(days=6)
    st.markdown(f'<div class="semaine-titre" style="text-align:center; font-size:2.8rem;">Semaine du {start.strftime("%d/%m")} au {end.strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
    
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    s_data = load_gs("Semaine")
    cols_s = st.columns(7)
    for i, j in enumerate(jours):
        d_str = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols_s[i]:
            st.markdown(f'<div class="card-jour"><div class="header-jour">{j}</div>', unsafe_allow_html=True)
            p_in = st.text_area("P", key=f"p_s_{i}", height=100, label_visibility="collapsed", placeholder="Planning")
            m_in = st.text_input("🍴", key=f"m_s_{i}", label_visibility="collapsed", placeholder="Menu")
            cs1, cs2 = st.columns(2)
            if cs1.button("💾", key=f"sv_s_{i}"): save_gs("Semaine", [d_str, p_in, m_in]); st.rerun()
            if cs2.button("🗑️", key=f"cl_s_{i}"): save_gs("Semaine", [d_str, "", ""]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == d_str:
                    st.markdown(f"<small style='color:black;'>• {row.get('Planning','')}<br><b>🍴 {row.get('Menu','')}</b></small>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 3. ANNEE (FIX FORMULAIRE) ---
with tabs[2]:
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier Annuel 2026</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div style="background:white; padding:20px; border-radius:20px; border:2px solid var(--rose);">', unsafe_allow_html=True)
        st.write("### 📅 Ajouter une Date Importante")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        new_d = ce1.date_input("Date", format="DD/MM/YYYY")
        new_e = ce2.text_input("Evénement")
        if ce3.button("✨ Enregistrer"):
            if new_e: save_gs("Evenements", [new_d.strftime("%d/%m/%Y"), new_e]); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    for r in range(4):
        cols_a = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_a[c]:
                st.markdown(f'<div style="background:var(--rose); color:white; text-align:center; border-radius:10px 10px 0 0; padding:5px;">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m_idx)
                res = "Lu Ma Me Je Ve Sa Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "   "
                        else: line += f"{get_circled_num(d)} " if f"{m_idx}-{d}" in marked else f"{d:2} "
                    res += line + "\n"
                st.markdown(f'<div style="font-family:monospace; background:white; color:black; padding:10px; border:1px solid var(--rose); border-radius:0 0 10px 10px; white-space:pre; text-align:center; font-size:0.8rem;">{res}</div>', unsafe_allow_html=True)

# --- 4. TRACKERS (LECTURE DÉTAILLÉE + SANTÉ) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE DÉTAILLÉE", "🩺 BIEN-ÊTRE & SANTÉ", "🏠 MISSIONS TRIBU"])
    
    with tr_tabs[0]:
        st.markdown('<div class="sous-titre-calli">📚 Ma Fiche de Lecture</div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div style="background:white; padding:20px; border-radius:20px; border:2px solid var(--rose);">', unsafe_allow_html=True)
            cl1, cl2 = st.columns(2)
            l_titre = cl1.text_input("Titre du livre", placeholder="Ex: L'Étranger")
            l_auteur = cl1.text_input("Auteur")
            l_genre = cl2.selectbox("Genre", ["Roman", "Développement Personnel", "Thriller", "Cuisine", "Travail"])
            l_note = cl2.select_slider("Ma Note / 10", range(11), value=5)
            l_citation = st.text_area("Passage ou citation préférée")
            if st.button("💾 Ajouter à ma bibliothèque"):
                if l_titre: 
                    save_gs("Lecture", [datetime.now().strftime("%d/%m/%Y"), l_titre, l_auteur, l_genre, l_note, l_citation])
                    st.success("Livre enregistré !")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sous-titre-calli">📖 Historique de mes Lectures</div>', unsafe_allow_html=True)
        l_data = load_gs("Lecture")
        for idx, book in enumerate(reversed(l_data)):
            with st.expander(f"📔 {book.get('Titre')} - {book.get('Auteur')}"):
                st.write(f"**Genre :** {book.get('Genre')} | **Note :** {book.get('Note')}/10")
                st.write(f"**Date :** {book.get('Date')}")
                st.info(f"💬 *{book.get('Citation')}*")
                if st.button("🗑️ Supprimer cette fiche", key=f"del_book_{idx}"):
                    delete_gs("Lecture", len(l_data)-1-idx); st.rerun()

    with tr_tabs[1]:
        st.markdown('<div class="sous-titre-calli">🩺 Mon Bilan Bien-être</div>', unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        sport = cs1.text_input("Sport / Activité", placeholder="Marche, Yoga...")
        eau = cs1.slider("Verres d'eau 💧", 0, 15, 6)
        migraine = cs2.select_slider("Suivi Migraine", options=["Aucune", "Gêne", "Douleur", "Intense", "Crise"])
        m_notes = cs2.text_area("Notes Santé", height=100)
        if st.button("💾 Enregistrer Santé"):
            save_gs("Sante", [datetime.now().strftime("%d/%m/%Y"), sport, eau, migraine, m_notes]); st.balloons()

    with tr_tabs[2]:
        st.markdown('<div class="sous-titre-calli">🏠 Missions de la Tribu</div>', unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns(3)
        m_qui = cm1.selectbox("Qui ?", ["Maman 🌸", "Papa 👔", "Enfant 1 👦", "Enfant 2 👧", "Enfant 3 👶"])
        m_tache = cm2.selectbox("Action", ["🍽️ Vaisselle", "🗑️ Poubelles", "🧹 Ménage", "🧺 Linge"])
        m_jour = cm3.selectbox("Quand ?", jours)
        if st.button("🚀 Valider Mission"):
            save_gs("Menage", [m_jour, m_tache, m_qui]); st.rerun()
        st.write("---")
        m_log = load_gs("Menage")
        cols_m = st.columns(7)
        for i, j_n in enumerate(jours):
            with cols_m[i]:
                st.markdown(f"**{j_n}**")
                for entry in m_log:
                    if entry.get("Jour") == j_n:
                        st.markdown(f"<div style='background:var(--vert); font-size:0.7rem; padding:5px; border-radius:5px; margin-bottom:3px;'>{entry.get('Tache')}<br><b>{entry.get('Qui')}</b></div>", unsafe_allow_html=True)

# --- 5. COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Ma Liste de Courses</div>', unsafe_allow_html=True)
    rapide = ["🍞 Pain", "🥛 Lait", "🍎 Fruits", "🍝 Pâtes", "🍚 Riz"]
    cr = st.columns(len(rapide))
    for i, r in enumerate(rapide):
        if cr[i].button(r, key=f"shop_{i}"): st.session_state.shopping.append(r); st.rerun()
    it = st.text_input("Ajouter un article...")
    if st.button("➕ Ajouter"):
        if it: st.session_state.shopping.append(it); st.rerun()
    st.write("---")
    for i, item in enumerate(st.session_state.shopping):
        ca, cb = st.columns([5, 1])
        ca.checkbox(item, key=f"ch_{i}")
        if cb.button("🗑️", key=f"del_c_{i}"): st.session_state.shopping.pop(i); st.rerun()
