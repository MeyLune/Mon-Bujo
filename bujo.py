import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

# --- 1. CONNEXION (Préservée) ---
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
    except Exception as e:
        return None

sh = init_connection()

# --- 2. DESIGN & CONFIGURATION (Optimisé iPad) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3 { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }
    
    .bujo-block { background: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    
    .p-header { background-color: #f06292; color: white; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    .p-cell { background-color: white; min-height: 150px; padding: 10px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; margin-bottom: 20px; }
    .event-tag { background: #fff1f3; border-left: 4px solid #f06292; padding: 5px; margin-bottom: 5px; border-radius: 4px; font-size: 0.8rem; color: #ad1457; }
</style>
""", unsafe_allow_html=True)

if not sh:
    st.error("Lien Google Sheets rompu. Vérifie tes secrets.")
    st.stop()

# --- 3. LOGIQUE D'ACCÈS SÉLECTIF ---
def check_consultant_access(tab_name):
    """Vérifie le code avec une clé unique par onglet pour éviter les erreurs Streamlit."""
    if "consultant_auth" not in st.session_state:
        st.session_state.consultant_auth = False
    
    if not st.session_state.consultant_auth:
        st.markdown(f'<div class="bujo-block"><h3>🔒 Accès réservé</h3>', unsafe_allow_html=True)
        pwd = st.text_input(f"Entrez le code pour voir la section {tab_name} :", type="password", key=f"pwd_{tab_name}")
        if pwd == "MEY2026":
            st.session_state.consultant_auth = True
            st.rerun()
        elif pwd != "":
            st.error("Code incorrect")
        st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# --- 4. NAVIGATION ---
st.markdown("<h1 style='text-align:center;'>Journal de MeyLune</h1>", unsafe_allow_html=True)
tab_j, tab_s, tab_b = st.tabs(["✍️ MON JOURNAL", "🌿 SEMAINE", "💰 BUDGET"])

# --- PAGE JOURNAL (Privée & Intime) ---
with tab_j:
    st.markdown(f"<p style='text-align:center;'>Nous sommes le {datetime.now().strftime('%d %B %Y')}</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="bujo-block"><h3>😊 Mon Humeur</h3>', unsafe_allow_html=True)
        humeur = st.select_slider("Humeur", options=["😢", "😟", "😐", "🙂", "✨", "🔥"], value="😐", key="humeur_slider")
        sens = st.text_area("Journal intime...", placeholder="Cette section n'est jamais partagée avec le code consultant.", key="secret_note")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="bujo-block"><h3>📋 Rapide</h3>', unsafe_allow_html=True)
        n_txt = st.text_input("Ajouter une note/RDV...")
        n_typ = st.selectbox("Style", ["Note", "RDV", "Tâche"])
        if st.button("Ancrer au Journal"):
            sh.worksheet("Note").append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), n_typ, n_txt])
            st.success("Ajouté !")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE SEMAINE (Partageable avec Code) ---
with tab_s:
    if check_consultant_access("Semaine"):
        if 'w_off' not in st.session_state: st.session_state.w_off = 0
        nav_c1, nav_c2, nav_c3 = st.columns([1, 2, 1])
        if nav_c1.button("⬅️ Précédente"): st.session_state.w_off -= 1
        if nav_c3.button("Suivante ➡️"): st.session_state.w_off += 1
        
        start_d = (datetime.now() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
        nav_c2.markdown(f"<h3 style='text-align:center;'>Semaine du {start_d.strftime('%d/%m')}</h3>", unsafe_allow_html=True)

        data = sh.worksheet("Note").get_all_values()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            
            # Grille 2 par 2 pour l'iPad
            for i in range(0, 7, 2):
                cols = st.columns(2)
                for j in range(2):
                    if (i + j) < 7:
                        curr = start_d + timedelta(days=i+j)
                        d_str = curr.strftime("%d/%m/%Y")
                        with cols[j]:
                            st.markdown(f'<div class="p-header">{days_fr[i+j]} {curr.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                            evs = ""
                            mask = df.iloc[:, 0] == d_str
                            for _, r in df[mask].iterrows():
                                evs += f'<div class="event-tag"><b>{r.iloc[1]}</b> - {r.iloc[3]}</div>'
                            st.markdown(f'<div class="p-cell">{evs}</div>', unsafe_allow_html=True)

# --- PAGE BUDGET (Partageable avec Code) ---
with tab_b:
    if check_consultant_access("Budget"):
        st.markdown("### 💰 Mes Finances")
        ws_fin = sh.worksheet("Finances")
        fin_data = ws_fin.get_all_records()
        if fin_data:
            df_f = pd.DataFrame(fin_data)
            new_f = st.data_editor(df_f, num_rows="dynamic", use_container_width=True, key="editor_budget")
            if st.button("Sauvegarder Budget"):
                ws_fin.clear()
                ws_fin.update([new_f.columns.values.tolist()] + new_f.values.tolist())
                st.success("Synchronisé !")
