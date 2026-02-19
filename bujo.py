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

# INITIALISATION DES VARIABLES (Évite les erreurs rouges)
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

# --- 2. STYLE "LUNAIRE" (ROSE/VERT & ANTI-BUG IPAD) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&display=swap');
    :root { --rose: #F48FB1; --sapin: #1B3022; --vert: #B2DFDB; --or: #D4AF37; }
    
    .stApp { background: linear-gradient(180deg, #fce4ec 0%, #e0f2f1 100%) !important; background-attachment: fixed; }
    
    /* Correction iPad : Force le fond blanc et texte noir */
    div[data-baseweb="select"], div[data-baseweb="input"], input, textarea, select, .stSelectbox {
        background-color: white !important; color: black !important; border: 2px solid var(--rose) !important;
    }

    .titre-calli { font-family: 'Dancing Script'; font-size: 3.5rem; color: var(--sapin); text-align: center; margin-bottom: 20px;}
    .sous-titre-calli { font-family: 'Dancing Script'; font-size: 2.2rem; color: var(--sapin); }
    
    .mission-day-box { background: white; border: 2px solid var(--rose); border-radius: 12px; padding: 10px; margin-bottom: 10px; min-height: 150px; }
    .sticker-info { background: var(--vert); color: var(--sapin); padding: 5px; border-radius: 8px; margin-top: 5px; font-size: 0.85rem; border: 1px solid var(--rose); text-align: center; }
    .post-it { background: #fffde7; border-left: 10px solid var(--or); padding: 15px; border-radius: 5px; color: black; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- ✍️ JOURNAL & GRATITUDE (Complet) ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data, g_data = load_gs("Journal"), load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("...", height=150, key="j_in", label_visibility="collapsed")
        if st.button("💾 Enregistrer pensée", key="j_btn"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data)):
            st.markdown(f'<div style="background:white; padding:10px; border-left:5px solid var(--rose); border-radius:10px; margin-bottom:5px;">{e.get("Texte", e.get("Note", ""))}</div>', unsafe_allow_html=True)
            if st.button("🗑️", key=f"dj_{i}"): delete_gs("Journal", len(j_data)-1-i); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("...", height=150, key="g_in", label_visibility="collapsed")
        if st.button("🙏 Enregistrer gratitude", key="g_btn"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data)):
            st.markdown(f'<div style="background:white; padding:10px; border-left:5px solid var(--or); border-radius:10px; margin-bottom:5px;"><i>{e.get("Texte", "")}</i></div>', unsafe_allow_html=True)
            if st.button("🗑️", key=f"dg_{i}"): delete_gs("Gratitude", len(g_data)-1-i); st.rerun()

# --- 🗓️ SEMAINE (Complet) ---
with tabs[1]:
    start_w = datetime.now().date() - timedelta(days=datetime.now().weekday())
    s_data = load_gs("Semaine")
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    cols_s = st.columns(7)
    for i, j in enumerate(jours):
        d_str = (start_w + timedelta(days=i)).strftime("%d/%m/%Y")
        with cols_s[i]:
            st.markdown(f'<div style="background:var(--vert); text-align:center; border-radius:10px; font-weight:bold; padding:5px;">{j} {d_str[:5]}</div>', unsafe_allow_html=True)
            p_in = st.text_area("Plan", key=f"p_{i}", height=100, label_visibility="collapsed")
            m_in = st.text_input("🍴 Menu", key=f"m_{i}", label_visibility="collapsed")
            if st.button("💾", key=f"sb_{i}"):
                save_gs("Semaine", [d_str, p_in, m_in]); st.rerun()
            for row in s_data:
                if str(row.get("Date")) == d_str:
                    st.markdown(f"<small>• {row.get('Planning','')}<br>🍴 {row.get('Menu','')}</small>", unsafe_allow_html=True)

# --- 📅 ANNEE (Complet avec Suppression) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    for r in range(4):
        cols_a = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols_a[c]:
                st.markdown(f'<div style="background:var(--rose); color:white; text-align:center; border-radius:10px 10px 0 0; padding:2px;">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m_idx)
                res = "Lu Ma Me Je Ve Sa Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "   "
                        else: line += f"{get_circled_num(d)} " if f"{m_idx}-{d}" in marked else f"{d:2} "
                    res += line + "\n"
                st.markdown(f'<div style="font-family:monospace; background:white; padding:10px; border:1px solid var(--rose); border-radius:0 0 10px 10px; white-space:pre; text-align:center; font-size:0.85rem;">{res}</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sous-titre-calli">📍 Gérer les événements</div>', unsafe_allow_html=True)
    ce1, ce2 = st.columns(2)
    ev_d = ce1.date_input("Choisir une date", key="new_ev_date")
    ev_n = ce2.text_input("Nom de l'événement", key="new_ev_name")
    if st.button("➕ Ajouter au calendrier", key="add_ev"):
        save_gs("Evenements", [ev_d.strftime("%d/%m/%Y"), ev_n]); st.rerun()
    for i, e in enumerate(evs):
        ca, cb = st.columns([5, 1])
        ca.write(f"📅 {e.get('Date')} : {e.get('Evenement')}")
        if cb.button("🗑️", key=f"dev_{i}"): delete_gs("Evenements", i); st.rerun()

# --- 📊 TRACKERS (SANTÉ & BIBLIO & MISSIONS) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 BIBLIOTHÈQUE", "🩺 BIEN-ÊTRE", "🏠 MISSIONS TRIBU"])
    
    with tr_tabs[0]: # Bibliothèque (Complet)
        st.markdown('<div class="sous-titre-calli">Ma Fiche de Lecture</div>', unsafe_allow_html=True)
        cl1, cl2 = st.columns(2)
        titre = cl1.text_input("Titre", key="bk_t")
        auteur = cl1.text_input("Auteur", key="bk_a")
        date_l = cl1.date_input("Date de lecture", key="bk_d")
        note = cl2.slider("Note / 10", 0, 10, 5)
        avis = st.text_area("Résumé & Avis", key="bk_av")
        if st.button("💾 Enregistrer le livre", key="bk_save"):
            save_gs("Lectures", [date_l.strftime("%d/%m/%Y"), titre, auteur, note, avis]); st.rerun()
        if st.checkbox("📖 Voir l'historique de lecture"):
            for b in reversed(load_gs("Lectures")):
                st.markdown(f'<div style="background:white; padding:10px; border-radius:10px; margin-bottom:5px; border:1px solid var(--rose);"><b>{b.get("Titre")}</b> - {b.get("Auteur")} | ⭐ {b.get("Note")}/10<br><small>{b.get("Avis")}</small></div>', unsafe_allow_html=True)

    with tr_tabs[1]: # Bien-être (Restauré)
        st.markdown('<div class="sous-titre-calli">Mon Équilibre</div>', unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        with cs1:
            humeur = st.selectbox("Humeur", ["Radieuse ☀️", "Paisible ☁️", "Fatiguée 🔋", "Sensible 🌙"], key="h_mood")
            eau = st.number_input("Verres d'eau 💧", 0, 15, 0, key="h_water")
        with cs2:
            energie = st.select_slider("Énergie", ["Bas", "Moyen", "Top!"], key="h_nrg")
            vitamines = st.checkbox("Vitamines / Soins pris ✅", key="h_vit")
        if st.button("Sauvegarder santé", key="h_save"):
            save_gs("Sante", [datetime.now().strftime("%d/%m/%Y"), humeur, eau, energie, vitamines]); st.success("Santé enregistrée !")

    with tr_tabs[2]: # Missions Tribu (Optimisé iPad 2 lignes)
        st.markdown('<div class="sous-titre-calli">Missions de la Tribu</div>', unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns(3)
        qui = cm1.selectbox("Qui ?", ["Enfant 1 👦", "Enfant 2 👧", "Enfant 3 👶", "Maman 🌸", "Papa 👔"], key="m_qui")
        d_m = cm2.date_input("Date", key="m_date")
        t_m = cm3.selectbox("Mission ?", ["🍽️ Vaisselle", "🗑️ Poubelles", "🧹 Balai", "🔌 Aspirateur", "🧼 Serpillière", "✨ Poussière", "🥣 Débarrasser", "🚿 Salle de bain", "🚽 Toilettes", "🧸 Chambres"], key="m_t")
        if st.button("🚀 Valider la mission", key="m_btn"):
            save_gs("Menage", [t_m, d_m.strftime("%d/%m/%Y"), qui]); st.rerun()
        
        m_data = load_gs("Menage")
        st.write("---")
        # Affichage iPad : 4 jours puis 3 jours
        for r_i in [0, 4]:
            r_cols = st.columns(4 if r_i == 0 else 3)
            for i in range(len(r_cols)):
                day_idx = r_i + i
                if day_idx < 7:
                    ds = (start_w + timedelta(days=day_idx)).strftime("%d/%m/%Y")
                    with r_cols[i]:
                        st.markdown(f'<div class="mission-day-box"><center><b>{jours[day_idx]}</b><br><small>{ds[:5]}</small></center>', unsafe_allow_html=True)
                        for m in m_data:
                            if ds in str(m.values()):
                                st.markdown(f'<div class="sticker-info"><b>{m.get("Tache", m.get("Mission", ""))}</b><br>{m.get("Mardi", m.get("Qui", ""))}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

# --- 🛒 COURSES (Restauré avec Favoris + Post-it) ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    cl, cr = st.columns([1, 1])
    with cl:
        st.write("✨ **Favoris rapides :**")
        favs = ["🍞 Pain", "🥛 Lait", "🍎 Fruits", "🍚 Riz", "🥣 Céréales", "🧻 Papier toilette", "🧼 Savon"]
        f_cols = st.columns(2)
        for idx, f in enumerate(favs):
            if f_cols[idx % 2].button(f"+ {f}", key=f"fav_{idx}"):
                if f not in st.session_state.shopping: st.session_state.shopping.append(f); st.rerun()
        st.write("---")
        autre = st.text_input("Autre article...", key="shop_in")
        if st.button("➕ Ajouter", key="shop_add"):
            if autre: st.session_state.shopping.append(autre); st.rerun()
        if st.button("🗑️ Vider tout", key="shop_clear"): st.session_state.shopping = []; st.rerun()
    with cr:
        st.markdown('<div class="post-it"><b>📝 À ACHETER :</b><br><br>', unsafe_allow_html=True)
        for i, item in enumerate(st.session_state.shopping):
            ci1, ci2 = st.columns([4, 1])
            ci1.write(f"☐ {item}")
            if ci2.button("❌", key=f"del_c_{i}"):
                st.session_state.shopping.pop(i); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
