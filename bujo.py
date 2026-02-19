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
    except: return None

sh = init_connection()

# --- 2. DESIGN : CALLIGRAPHIE, POST-ITS & ANTI-NOIR ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    
    :root {{
        --rose: #F48FB1;
        --sapin: #1B3022;
        --or: #D4AF37;
        --vert-doux: #B2DFDB;
    }}

    .stApp {{
        background: linear-gradient(135deg, rgba(255, 209, 220, 0.7), rgba(178, 223, 219, 0.7)), url("{fond_url}");
        background-size: cover; background-attachment: fixed; background-color: white !important;
    }}

    .titre-calli {{
        font-family: 'Dancing Script', cursive !important; font-size: 3.5rem !important;
        color: var(--sapin) !important; text-align: center; -webkit-text-fill-color: var(--sapin) !important;
        margin-bottom: 10px;
    }}
    
    .sous-titre-calli {{
        font-family: 'Dancing Script', cursive !important; font-size: 2.2rem !important;
        color: var(--sapin) !important; -webkit-text-fill-color: var(--sapin) !important;
        margin-bottom: 15px;
    }}

    /* FORÇAGE DES CASES BLANCHES ET TEXTE FONCÉ */
    textarea, input, div[data-baseweb="base-input"], div[data-baseweb="textarea"], div[data-baseweb="select"] {{
        background-color: white !important; color: var(--sapin) !important;
        -webkit-text-fill-color: var(--sapin) !important;
        border: 2px solid var(--rose) !important; border-radius: 12px !important;
    }}

    /* BOUTONS ROSES FORCÉS */
    .stButton>button {{
        background-color: var(--rose) !important; color: white !important;
        -webkit-text-fill-color: white !important; border-radius: 20px !important;
        font-weight: bold !important; border: none !important;
    }}

    /* POST-ITS & ENCADRÉS */
    .post-it {{ padding: 15px; border-radius: 15px; margin-bottom: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }}
    
    .p-header {{ 
        background-color: var(--vert-doux) !important; color: var(--sapin) !important;
        padding: 8px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; border: 1px solid var(--rose);
    }}

    /* FIX POUR LES CHECKBOXES DES COURSES */
    div[data-testid="stCheckbox"] {{ color: var(--sapin) !important; }}
</style>
""", unsafe_allow_html=True)

# --- 3. INITIALISATION DES ETATS ---
if 'list_pensees' not in st.session_state: st.session_state.list_pensees = []
if 'list_gratitudes' not in st.session_state: st.session_state.list_gratitudes = []
if 'shopping_list' not in st.session_state: st.session_state.shopping_list = []
if 'p_version' not in st.session_state: st.session_state.p_version = 0
if 'g_version' not in st.session_state: st.session_state.g_version = 0
if 'edit_p_val' not in st.session_state: st.session_state.edit_p_val = ""
if 'edit_g_val' not in st.session_state: st.session_state.edit_g_val = ""

# --- LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal") or code == "2125":
            st.session_state.user_data = {"Nom": "MeyLune"}; st.rerun()
    st.stop()

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ✍️ ONGLET JOURNAL ---
with tabs[0]:
    col_j1, col_j2 = st.columns(2)
    with col_j1:
        st.markdown(f'<div class="sous-titre-calli">🖋️ Mes pensées du {datetime.now().strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
        val_p = st.text_area("Libère ton esprit...", value=st.session_state.edit_p_val, height=120, key=f"p_input_{st.session_state.p_version}", label_visibility="collapsed")
        if st.button("💾 Enregistrer la pensée", key="btn_p"):
            if val_p:
                st.session_state.list_pensees.insert(0, {"text": val_p, "time": datetime.now().strftime("%H:%M")})
                st.session_state.p_version += 1; st.session_state.edit_p_val = ""; st.rerun()

        st.markdown("---")
        for idx, entry in enumerate(st.session_state.list_pensees):
            bg = "rgba(255, 209, 220, 0.6)" if idx % 2 == 0 else "rgba(178, 223, 219, 0.6)"
            st.markdown(f'<div class="post-it" style="background-color: {bg}; border-left: 8px solid var(--rose);"><small>{entry["time"]}</small><br>{entry["text"]}</div>', unsafe_allow_html=True)
            if st.button("Modifier", key=f"edit_p_{idx}"):
                st.session_state.edit_p_val = entry["text"]; st.session_state.list_pensees.pop(idx); st.rerun()

    with col_j2:
        st.markdown(f'<div class="sous-titre-calli">✨ Gratitude pour aujourd\'hui</div>', unsafe_allow_html=True)
        val_g = st.text_area("Merci pour...", value=st.session_state.edit_g_val, height=120, key=f"g_input_{st.session_state.g_version}", label_visibility="collapsed")
        if st.button("🙏 Enregistrer ma gratitude", key="btn_g"):
            if val_g:
                st.session_state.list_gratitudes.insert(0, {"text": val_g, "time": datetime.now().strftime("%H:%M")})
                st.session_state.g_version += 1; st.session_state.edit_g_val = ""; st.rerun()

        st.markdown("---")
        for idx, entry in enumerate(st.session_state.list_gratitudes):
            st.markdown(f'<div class="post-it" style="background-color: white; border-left: 8px solid var(--or);"><small>{entry["time"]}</small><br><i>{entry["text"]}</i></div>', unsafe_allow_html=True)
            if st.button("Modifier", key=f"edit_g_{idx}"):
                st.session_state.edit_g_val = entry["text"]; st.session_state.list_gratitudes.pop(idx); st.rerun()

# --- 🗓️ ONGLET SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    col_nav = st.columns([1, 3, 1])
    if col_nav[0].button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if col_nav[2].button("➡️"): st.session_state.w_off += 1; st.rerun()
    col_nav[1].markdown(f'<div class="sous-titre-calli" style="text-align:center;">Semaine {start_week.isocalendar()[1]} - 2026</div>', unsafe_allow_html=True)

    col_g, col_d = st.columns([3, 1.2])
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    with col_g:
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for k in range(2):
                if (i+k) < 7:
                    d = start_week + timedelta(days=i+k)
                    with cols[k]:
                        st.markdown(f'<div class="p-header">{jours[i+k]} {d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        st.text_area("", height=100, key=f"wk_{d}", label_visibility="collapsed")
        c_s1, c_s2 = st.columns(2)
        c_s1.button("💾 Sauvegarder la semaine", key="save_s")
        c_s2.button("📝 Modifier", key="mod_s")

    with col_d:
        st.markdown('<div class="p-header" style="background-color:white !important;">🍎 Menu</div>', unsafe_allow_html=True)
        for j in jours: st.text_input(j[:3], key=f"menu_{j}")
        st.button("💾 Sauver Menu", key="save_m")

# --- 📅 ONGLET ANNEE ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier Annuel 2026</div>', unsafe_allow_html=True)
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                tc = calendar.TextCalendar(firstweekday=0)
                cal_str = tc.formatmonth(2026, m_idx)
                st.markdown(f'<div class="p-header" style="background-color:var(--rose)!important; color:white!important;">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-family:\'Courier Prime\'; background:white; padding:10px; border:1px solid var(--rose); border-radius:0 0 12px 12px; white-space:pre; text-align:center;">{cal_str}</div>', unsafe_allow_html=True)

# --- 📊 ONGLET TRACKERS ---
with tabs[3]:
    st.markdown('<div class="sous-titre-calli">📚 Ma Fiche de Lecture</div>', unsafe_allow_html=True)
    c_l1, c_l2 = st.columns([2, 1])
    with c_l1:
        st.text_input("TITRE")
        st.text_input("AUTEUR")
        st.date_input("DÉBUT")
    with c_l2:
        st.file_uploader("Couverture", type=['jpg','png'])
    st.slider("NOTE", 1, 10, 5)
    st.button("💾 ENREGISTRER LECTURE")

# --- 🛒 ONGLET COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    c_left, c_right = st.columns([2, 1.2])
    
    with c_left:
        st.date_input("Date prévue pour les courses", value=datetime.now(), key="course_date")
        
        # Ajout manuel
        new_item = st.text_input("Ajouter un article :", key="course_input")
        if st.button("➕ Ajouter à la liste", use_container_width=True):
            if new_item:
                st.session_state.shopping_list.append(new_item); st.rerun()
        
        st.write("---")
        st.write("✨ **Ajouts rapides :**")
        rapides = ["Lait", "Pain", "Oeufs", "Fruits", "Légumes", "Eau", "Pâtes", "Fromage"]
        cols_r = st.columns(4)
        for i, item in enumerate(rapides):
            if cols_r[i % 4].button(item, key=f"btn_{item}"):
                st.session_state.shopping_list.append(item); st.rerun()

    with c_right:
        st.markdown('<div class="p-header" style="background-color:var(--rose)!important; color:white!important;">🛍️ Ma Liste Finale</div>', unsafe_allow_html=True)
        with st.container(border=True):
            if not st.session_state.shopping_list:
                st.write("*Ta liste est vide...*")
            else:
                for idx, item in enumerate(st.session_state.shopping_list):
                    col_check, col_del = st.columns([4, 1])
                    col_check.checkbox(item, key=f"check_{idx}")
                    if col_del.button("🗑️", key=f"del_{idx}"):
                        st.session_state.shopping_list.pop(idx); st.rerun()
            
            if st.button("🗑️ Tout vider", key="clear_all"):
                st.session_state.shopping_list = []; st.rerun()
        
        st.markdown("---")
        st.markdown('<div class="p-header">📅 Menus Prévus</div>', unsafe_allow_html=True)
        for j in jours:
            menu_txt = st.session_state.get(f"menu_{j}", "...")
            st.markdown(f"**{j[:2]}** : {menu_txt}")

# --- 🎨 ONGLET STICKERS ---
with tabs[5]:
    st.markdown('<div class="sous-titre-calli">🎨 Mes Stickers</div>', unsafe_allow_html=True)
    up = st.file_uploader("Upload", type=['png', 'jpg'], key="up_final")
    if up: st.image(up, width=120)
