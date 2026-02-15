import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

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
    except:
        return None

sh = init_connection()

# --- 2. DESIGN & CSS ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3 { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }
    
    .post-it {
        background: #fff9c4; padding: 20px; border-left: 5px solid #fbc02d;
        font-family: 'Indie Flower', cursive; font-size: 1.2rem; color: #5d4037;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.05); border-radius: 2px; min-height: 200px;
    }
    
    .bujo-block { background: white; padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    .p-header { background-color: #f06292; color: white; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    .p-cell { background-color: white; min-height: 150px; padding: 10px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; margin-bottom: 20px; }
    .event-tag { background: #fff1f3; border-left: 4px solid #f06292; padding: 5px; margin-bottom: 5px; border-radius: 4px; font-size: 0.8rem; color: #ad1457; }
</style>
""", unsafe_allow_html=True)

# --- 3. GESTION DES PROFILS ---
if "user_data" not in st.session_state:
    st.session_state.user_data = None

def verify_login(code_saisi):
    if sh:
        try:
            users_df = pd.DataFrame(sh.worksheet("Utilisateurs").get_all_records())
            user_match = users_df[users_df['Code'].astype(str) == str(code_saisi)]
            if not user_match.empty:
                return user_match.iloc[0].to_dict()
        except:
            pass
    return None

# --- 4. ÉCRAN DE VERROUILLAGE ---
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        code_input = st.text_input("Entre ton code personnel", type="password")
        if st.button("Se connecter", use_container_width=True):
            user = verify_login(code_input)
            if user:
                st.session_state.user_data = user
                st.rerun()
            else:
                st.error("Code invalide")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 5. APPLICATION ---
user = st.session_state.user_data
st.markdown(f"<h1 style='text-align:center;'>MeyLune Bujo</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.write(f"👤 **Bonjour {user['Nom']} !**")
    st.write(f"Rôle : {user['Rôle']}")
    if st.button("🔒 Déconnexion"):
        st.session_state.user_data = None
        st.rerun()

# Configuration des onglets
tabs_list = ["🌿 SEMAINE", "🛍️ COURSES & BUDGET PROX"]
if user['Accès Journal'] == "OUI":
    tabs_list.append("💰 BUDGET DÉTAILLÉ")
    tabs_list.insert(0, "✍️ MON JOURNAL")

tabs = st.tabs(tabs_list)
tab_idx = 0

# --- ONGLET 1 : JOURNAL (ADMIN UNIQUEMENT) ---
if user['Accès Journal'] == "OUI":
    with tabs[tab_idx]:
        st.markdown(f"### ✨ Agenda du {datetime.now().strftime('%d %B')}")
        sub1, sub2 = st.tabs(["📖 Ma Journée", "📊 Trackers"])
        with sub1:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="post-it">Mémo rapide (Apple Pencil)...</div>', unsafe_allow_html=True)
                st.text_area("", key="p_note", label_visibility="collapsed", height=150)
            with c2:
                st.markdown('<div class="bujo-block"><h3>📌 Action Rapide</h3>', unsafe_allow_html=True)
                txt = st.text_input("Nouvelle tâche/note")
                if st.button("Ajouter au Bujo"):
                    sh.worksheet("Note").append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), "Note", txt])
                    st.success("C'est fait !")
                st.markdown('</div>', unsafe_allow_html=True)
    tab_idx += 1

# --- ONGLET 2 : SEMAINE (TOUT LE MONDE) ---
with tabs[tab_idx]:
    st.subheader("Vue Hebdomadaire")
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.w_off -= 1
    if c3.button("➡️"): st.session_state.w_off += 1
    
    start_d = (datetime.now() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    c2.markdown(f"<p style='text-align:center;'><b>{start_d.strftime('%d/%m')} - {(start_d + timedelta(days=6)).strftime('%d/%m')}</b></p>", unsafe_allow_html=True)
    
    data = sh.worksheet("Note").get_all_values()
    if len(data) > 1:
        df = pd.DataFrame(data[1:], columns=data[0])
        days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i in range(0, 7, 2):
            cols = st.columns(2)
            for j in range(2):
                if (i+j) < 7:
                    curr = start_d + timedelta(days=i+j)
                    with cols[j]:
                        st.markdown(f'<div class="p-header">{days_fr[i+j]} {curr.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                        evs = ""
                        day_df = df[df.iloc[:, 0] == curr.strftime("%d/%m/%Y")]
                        for _, r in day_df.iterrows():
                            evs += f'<div class="event-tag"><b>{r.iloc[1]}</b> - {r.iloc[3]}</div>'
                        st.markdown(f'<div class="p-cell">{evs}</div>', unsafe_allow_html=True)
tab_idx += 1

# --- ONGLET 3 : COURSES & BUDGET PROX (TOUT LE MONDE) ---
with tabs[tab_idx]:
    st.markdown("### 🛍️ Gestion Collective")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown('<div class="bujo-block"><h3>🛒 Liste de courses</h3>', unsafe_allow_html=True)
        # On suppose un onglet "Courses" dans ton GSheets
        st.write("Cochez ce qu'il faut acheter :")
        items = ["Lait", "Œufs", "Pain", "Fruits"]
        for item in items: st.checkbox(item, key=f"shop_{item}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_c2:
        st.markdown('<div class="bujo-block"><h3>💸 Budget de la semaine</h3>', unsafe_allow_html=True)
        st.metric("Reste pour la semaine", "120 €", "-15 €")
        st.write("Ce budget est consultable par toute la famille.")
        st.markdown('</div>', unsafe_allow_html=True)
tab_idx += 1

# --- ONGLET 4 : BUDGET DÉTAILLÉ (ADMIN UNIQUEMENT) ---
if user['Accès Journal'] == "OUI":
    with tabs[tab_idx]:
        st.markdown("### 🔒 Finances Détaillées (Privé)")
        ws_f = sh.worksheet("Finances")
        df_f = pd.DataFrame(ws_f.get_all_records())
        st.write("Modification des revenus et charges fixes :")
        new_df = st.data_editor(df_f, num_rows="dynamic", use_container_width=True, key="admin_budget_editor")
        if st.button("Sauvegarder les comptes"):
            ws_f.clear()
            ws_f.update([new_df.columns.values.tolist()] + new_df.values.tolist())
            st.success("Données sécurisées et synchronisées !")
