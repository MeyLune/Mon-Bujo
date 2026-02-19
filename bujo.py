import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import calendar

# --- 1. CONNEXION GOOGLE SHEETS ---
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

# Fonctions de gestion universelles
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

# Logique des numéros cerclés pour le calendrier annuel
def get_circled_num(n):
    circled = {i: chr(9311 + i) for i in range(1, 21)}
    circled.update({21: "㉑", 22: "㉒", 23: "㉓", 24: "㉔", 25: "㉕", 26: "㉖", 27: "㉗", 28: "㉘", 29: "㉙", 30: "㉚", 31: "㉛"})
    return circled.get(n, str(n))

# --- 2. CONFIGURATION & STYLE (Optimisé iPad) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    :root { --rose: #F48FB1; --sapin: #1B3022; --or: #D4AF37; --vert: #B2DFDB; }
    
    .stApp { 
        background-color: white !important;
        background: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), 
                    url("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg");
        background-size: cover; background-attachment: fixed;
    }
    
    .titre-calli { font-family: 'Dancing Script', cursive; font-size: 3.5rem; color: var(--sapin); text-align: center; padding: 10px; }
    .sous-titre-calli { font-family: 'Dancing Script', cursive; font-size: 2.2rem; color: var(--sapin); }
    
    p, label, .stMarkdown, span, div, .stCheckbox { font-family: 'Comfortaa'; color: var(--sapin) !important; }
    
    textarea, input { 
        background-color: white !important; color: var(--sapin) !important; 
        border: 2px solid var(--rose) !important; border-radius: 12px !important; 
    }
    
    .post-it { padding: 15px; border-radius: 15px; margin-bottom: 10px; border-left: 10px solid var(--rose); background: white; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .card-jour { background: rgba(255,255,255,0.9); border: 2px solid var(--rose); border-radius: 15px; padding: 10px; margin-bottom: 15px; }
    .header-jour { background: var(--vert); color: var(--sapin); text-align: center; font-weight: bold; border-radius: 10px; padding: 5px; margin-bottom: 10px; }
    
    .stButton>button { background-color: var(--rose) !important; color: white !important; border-radius: 20px !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if 'shopping' not in st.session_state: st.session_state.shopping = []

# --- LOGIN ---
if "user_data" not in st.session_state:
    st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal") or code == "2125":
            st.session_state.user_data = {"Nom": "MeyLune"}; st.rerun()
    st.stop()

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ✍️ JOURNAL ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data = load_gs("Journal")
    g_data = load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        t_j = st.text_area("...", height=150, key="in_j", label_visibility="collapsed")
        if st.button("💾 Enregistrer pensée", key="save_j"):
            if t_j: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_j]); st.rerun()
        for i, e in enumerate(reversed(j_data)):
            idx = len(j_data) - 1 - i
            txt = e.get("Texte", "")
            if txt and str(txt).lower() != "none":
                st.markdown(f'<div class="post-it"><small>{e.get("Date")}</small><br>{txt}</div>', unsafe_allow_html=True)
                if st.button("🗑️", key=f"dj_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        t_g = st.text_area("...", height=150, key="in_g", label_visibility="collapsed")
        if st.button("🙏 Enregistrer gratitude", key="save_g"):
            if t_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), t_g]); st.rerun()
        for i, e in enumerate(reversed(g_data)):
            idx_g = len(g_data) - 1 - i
            txt_g = e.get("Texte", "")
            if txt_g and str(txt_g).lower() != "none":
                st.markdown(f'<div class="post-it" style="border-left-color:var(--or);"><i>{txt_g}</i></div>', unsafe_allow_html=True)
                if st.button("🗑️", key=f"dg_{idx_g}"): delete_gs("Gratitude", idx_g); st.rerun()

# --- 🗓️ SEMAINE (Planning + Menus avec gestion individuelle) ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    st.markdown(f'<div class="sous-titre-calli" style="text-align:center;">Semaine {start.isocalendar()[1]}</div>', unsafe_allow_html=True)
    
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    s_data = load_gs("Semaine")
    
    # Affichage en 3 + 4 pour laisser de la place au Pencil sur iPad
    l1 = st.columns(3)
    l2 = st.columns(4)
    all_cols = l1 + l2
    
    for i, j in enumerate(jours):
        curr_date = (start + timedelta(days=i)).strftime("%d/%m/%Y")
        with all_cols[i]:
            st.markdown(f'<div class="card-jour"><div class="header-jour">{j} {curr_date[:5]}</div>', unsafe_allow_html=True)
            
            p_in = st.text_area("Note", key=f"p_s_{i}", height=100, label_visibility="collapsed", placeholder="Planning...")
            m_in = st.text_input("Menu", key=f"m_s_{i}", label_visibility="collapsed", placeholder="🍴 Menu...")
            
            if st.button("💾", key=f"save_s_{i}"):
                if p_in or m_in:
                    save_gs("Semaine", [curr_date, p_in, m_in]); st.rerun()
            
            st.markdown("---")
            for idx_s, row in enumerate(s_data):
                if str(row.get("Date")) == curr_date:
                    pl = row.get('Planning', '')
                    mn = row.get('Menu', '')
                    if (pl and str(pl).lower() != "none") or (mn and str(mn).lower() != "none"):
                        st.markdown(f"<div style='font-size:0.85rem;'><b>•</b> {pl}<br><b>🍴</b> {mn}</div>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"ds_s_{idx_s}"): delete_gs("Semaine", idx_s); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 📅 ANNEE (Calendrier interactif) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                st.markdown(f'<div style="background:var(--rose); color:white; padding:5px; text-align:center; border-radius:12px 12px 0 0; font-weight:bold;">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m_idx)
                res = "Lu Ma Me Je Ve Sa Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "   "
                        else:
                            line += f"{get_circled_num(d)} " if f"{m_idx}-{d}" in marked else f"{d:2} "
                    res += line + "\n"
                st.markdown(f'<div style="font-family:\'Courier Prime\'; background:white; padding:10px; border:1px solid var(--rose); border-radius:0 0 12px 12px; white-space:pre; text-align:center; font-size:0.8rem;">{res}</div>', unsafe_allow_html=True)
    st.markdown("---")
    ca, cl = st.columns(2)
    with ca:
        sd = st.date_input("Date importante", key="d_imp")
        en = st.text_input("Événement", key="v_imp")
        if st.button("📍 Marquer"): save_gs("Evenements", [sd.strftime("%d/%m/%Y"), en]); st.rerun()
    with cl:
        for i, ev in enumerate(evs):
            ctx, cbt = st.columns([4,1])
            ctx.write(f"⭕ {ev.get('Date')} : {ev.get('Evenement')}")
            if cbt.button("🗑️", key=f"dev_{i}"): delete_gs("Evenements", i); st.rerun()

# --- 📊 TRACKERS (LECTURE & SANTE) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🩺 SANTÉ"])
    with tr_tabs[0]:
        cl1, cl2 = st.columns([2, 1])
        with cl1:
            st.text_input("Titre", key="bk_t"); st.text_input("Auteur", key="bk_a")
            st.date_input("Début", key="bk_d"); st.date_input("Fin", key="bk_f")
        with cl2: st.file_uploader("Couverture", key="bk_img")
        st.slider("Note / 10", 1, 10, 5, key="bk_n")
        st.button("💾 Sauver Lecture", key="btn_bk")
    with tr_tabs[1]:
        st.markdown('<div class="sous-titre-calli">🩺 Suivi Santé</div>', unsafe_allow_html=True)
        st.date_input("Date", key="h_d")
        st.multiselect("État", ["Forme ✨", "Fatigue 😴", "Douleurs 🤕", "Stress 😰"], key="h_e")
        st.text_area("Notes", key="h_n")
        st.button("💾 Sauver Santé", key="btn_h")

# --- 🛒 COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    rapide = ["🍞 Pain", "🥛 Lait", "🍎 Fruits", "🍝 Pâtes", "🥚 Œufs"]
    cols_r = st.columns(len(rapide))
    for idx, r in enumerate(rapide):
        if cols_r[idx].button(r, key=f"r_{idx}"): st.session_state.shopping.append(r); st.rerun()
    it = st.text_input("Ajouter article...", key="c_add")
    if st.button("➕ Ajouter"):
        if it: st.session_state.shopping.append(it); st.rerun()
    for i, item in enumerate(st.session_state.shopping):
        ca, cb = st.columns([4, 1])
        ca.checkbox(item, key=f"ch_{i}")
        if cb.button("🗑️", key=f"dc_{i}"): st.session_state.shopping.pop(i); st.rerun()

# --- 🎨 STICKERS ---
with tabs[5]:
    st.markdown('<div class="sous-titre-calli">🎨 Mes Stickers</div>', unsafe_allow_html=True)
    st.info("Espace prêt pour tes futurs stickers !")
