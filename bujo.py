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

def update_gs(ws_n, idx, col, val):
    try: sh.worksheet(ws_n).update_cell(idx + 2, col, val)
    except: pass

# --- 2. LOGIQUE VISUELLE ---
def get_circled_num(n):
    circled = {i: chr(9311 + i) for i in range(1, 21)}
    circled.update({21: "㉑", 22: "㉒", 23: "㉓", 24: "㉔", 25: "㉕", 26: "㉖", 27: "㉗", 28: "㉘", 29: "㉙", 30: "㉚", 31: "㉛"})
    return circled.get(n, str(n))

# --- 3. DESIGN & POLICES ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    :root {{ --rose: #F48FB1; --sapin: #1B3022; --or: #D4AF37; --vert-pale: #B2DFDB; }}
    .stApp {{ background: linear-gradient(135deg, rgba(255,209,220,0.7), rgba(178,223,219,0.7)), url("{fond_url}"); background-size: cover; background-attachment: fixed; }}
    .titre-calli {{ font-family: 'Dancing Script', cursive !important; font-size: 3.5rem !important; color: var(--sapin) !important; text-align: center; }}
    .sous-titre-calli {{ font-family: 'Dancing Script', cursive !important; font-size: 2.2rem !important; color: var(--sapin) !important; }}
    p, label, .stMarkdown, span, div, .stCheckbox {{ font-family: 'Comfortaa', cursive !important; color: var(--sapin) !important; }}
    textarea, input {{ background-color: white !important; color: var(--sapin) !important; border: 2px solid var(--rose) !important; border-radius: 12px !important; -webkit-text-fill-color: var(--sapin) !important; }}
    .stButton>button {{ background-color: var(--rose) !important; color: white !important; border-radius: 20px !important; font-weight: bold !important; border: none !important; }}
    .post-it {{ padding: 12px; border-radius: 15px; margin-bottom: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); border-left: 10px solid var(--rose); background: rgba(255,255,255,0.8); }}
    .p-header {{ background-color: var(--vert-pale) !important; color: var(--sapin) !important; padding: 8px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; border: 1px solid var(--rose); }}
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if 'j_edit' not in st.session_state: st.session_state.j_edit = None
if 'j_val' not in st.session_state: st.session_state.j_val = ""
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

# --- ✍️ JOURNAL (Restauration Gratitude + Modif/Suppr) ---
with tabs[0]:
    col1, col2 = st.columns(2)
    j_data = load_gs("Journal")
    g_data = load_gs("Gratitude")
    
    with col1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        txt_j = st.text_area("...", value=st.session_state.j_val, height=150, key="in_j", label_visibility="collapsed")
        if st.button("💾 Enregistrer la pensée"):
            if txt_j:
                if st.session_state.j_edit is not None: update_gs("Journal", st.session_state.j_edit, 2, txt_j); st.session_state.j_edit = None; st.session_state.j_val = ""
                else: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), txt_j])
                st.rerun()
        for i, e in enumerate(reversed(j_data)):
            idx = len(j_data) - 1 - i
            st.markdown(f'<div class="post-it"><small>{e.get("Date")}</small><br>{e.get("Texte")}</div>', unsafe_allow_html=True)
            cb1, cb2 = st.columns(2)
            if cb1.button("✏️", key=f"ed_j_{idx}"): st.session_state.j_edit = idx; st.session_state.j_val = e.get("Texte"); st.rerun()
            if cb2.button("🗑️", key=f"del_j_{idx}"): delete_gs("Journal", idx); st.rerun()

    with col2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        txt_g = st.text_area("...", height=150, key="in_g", label_visibility="collapsed")
        if st.button("🙏 Enregistrer ma gratitude"):
            if txt_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), txt_g]); st.rerun()
        for i, e in enumerate(reversed(g_data)):
            idx_g = len(g_data) - 1 - i
            st.markdown(f'<div class="post-it" style="border-left-color:var(--or); background:white;"><i>{e.get("Texte")}</i></div>', unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_g_{idx_g}"): delete_gs("Gratitude", idx_g); st.rerun()

# --- 🗓️ SEMAINE (Mise en page demandée) ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    end = start + timedelta(days=6)
    num_sem = start.isocalendar()[1]
    st.markdown(f'<div class="sous-titre-calli" style="text-align:center;">Semaine {num_sem}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; font-family:Comfortaa;">Du {start.strftime("%d/%m/%Y")} au {end.strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
    
    st.markdown("### 🗓️ Mon Planning")
    cols_plan = st.columns(7)
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    for i, j in enumerate(jours):
        d_p = start + timedelta(days=i)
        with cols_plan[i]:
            st.markdown(f'<div class="p-header">{j[:3]} {d_p.strftime("%d")}/{(d_p.strftime("%m"))}</div>', unsafe_allow_html=True)
            st.text_area("", key=f"p_{i}", height=120, label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 🍎 Mes Menus")
    cols_menu = st.columns(7)
    for i, j in enumerate(jours):
        with cols_menu[i]:
            st.markdown(f'<div class="p-header" style="background:white!important;">{j[:3]}</div>', unsafe_allow_html=True)
            st.text_input("Matin", key=f"mm_{i}", label_visibility="collapsed", placeholder="Matin")
            st.text_input("Midi", key=f"mi_{i}", label_visibility="collapsed", placeholder="Midi")
            st.text_input("Soir", key=f"ms_{i}", label_visibility="collapsed", placeholder="Soir")

# --- 📅 ANNEE (Restauration) ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier Annuel 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(e['Date'], '%d/%m/%Y').month}-{datetime.strptime(e['Date'], '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
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
    # Section Gestion Dates Importantes
    st.markdown("---")
    c_add, c_list = st.columns(2)
    with c_add:
        sd = st.date_input("Nouvelle date")
        en = st.text_input("Nom de l'événement")
        if st.button("📍 Marquer"): save_gs("Evenements", [sd.strftime("%d/%m/%Y"), en]); st.rerun()
    with c_list:
        for i, ev in enumerate(evs):
            ctx, cbt = st.columns([4,1])
            ctx.write(f"⭕ {ev.get('Date')} : {ev.get('Evenement')}")
            if cbt.button("🗑️", key=f"de_{i}"): delete_gs("Evenements", i); st.rerun()

# --- 📊 TRACKERS (Fiche Lecture + Santé) ---
with tabs[3]:
    sub_tabs = st.tabs(["📚 FICHE DE LECTURE", "🩺 SANTÉ"])
    with sub_tabs[0]:
        tl1, tl2 = st.columns([2, 1])
        with tl1:
            st.text_input("TITRE DU LIVRE"); st.text_input("AUTEUR")
            st.date_input("DÉBUT LECTURE", key="l1"); st.date_input("FIN LECTURE", key="l2")
        with tl2: st.file_uploader("Couverture", type=['jpg','png'])
        st.slider("NOTE / 10", 1, 10, 5, key="note_l")
        st.button("💾 ENREGISTRER LECTURE")
    with sub_tabs[1]:
        st.markdown('<div class="sous-titre-calli">🩺 Mon Suivi Santé</div>', unsafe_allow_html=True)
        st.date_input("Date du jour")
        st.multiselect("Symptômes", ["Forme ✨", "Fatigue 😴", "Douleurs 🤕", "Stress 😰"])
        st.text_area("Notes médicales / Traitement")
        st.button("💾 ENREGISTRER SANTÉ")

# --- 🛒 COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Ma Liste</div>', unsafe_allow_html=True)
    rapide = ["🍞 Pain", "🥛 Lait", "🍎 Fruits", "🍝 Pâtes", "🥚 Œufs"]
    cols_r = st.columns(len(rapide))
    for idx, r in enumerate(rapide):
        if cols_r[idx].button(r): st.session_state.shopping.append(r); st.rerun()
    it = st.text_input("Autre article :")
    if st.button("Ajouter"):
        if it: st.session_state.shopping.append(it); st.rerun()
    for i, item in enumerate(st.session_state.shopping):
        ca, cb = st.columns([4, 1])
        ca.checkbox(item, key=f"ch_{i}")
        if cb.button("🗑️", key=f"dc_{i}"): st.session_state.shopping.pop(i); st.rerun()

# --- 🎨 STICKERS ---
with tabs[5]:
    st.markdown('<div class="sous-titre-calli">🎨 Stickers</div>', unsafe_allow_html=True)
