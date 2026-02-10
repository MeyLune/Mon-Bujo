import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

# --- 1. CONNEXION SÉCURISÉE ---
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
        client = gspread.authorize(creds)
        return client.open("db_bujo")
    except:
        return None

sh = init_connection()

# --- 2. STYLE IPAD & COULEURS ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")
st.markdown("""
<style>
    .stTabs [data-baseweb="tab"] { height: 60px; font-weight: bold; font-size: 18px; border-radius: 10px 10px 0 0; padding: 0 30px; }
    .stTabs [aria-selected="true"] { background-color: #f06292 !important; color: white !important; }
    .p-header { background-color: #f06292; color: white; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    .p-cell { background-color: white; min-height: 200px; padding: 10px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; }
    .event-box { background: #fff1f3; border-left: 4px solid #f06292; padding: 5px; margin-bottom: 5px; border-radius: 4px; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT DES DONNÉES (ANTI-ERREUR) ---
if sh:
    ws_notes = sh.worksheet("Note")
    ws_fin = sh.worksheet("Finances")
    # On force la création d'un DataFrame propre pour éviter le KeyError
    data = ws_notes.get_all_values()
    if len(data) > 1:
        df_notes = pd.DataFrame(data[1:], columns=data[0])
    else:
        df_notes = pd.DataFrame(columns=["Date", "Heure", "Type", "Note"])
else:
    st.error("Connexion Google Sheets impossible.")
    st.stop()

# --- 4. NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["✍️ JOURNAL", "🌿 SEMAINE", "💰 BUDGET"])

with tab1:
    st.title("Mon Journal")
    col_a, col_b = st.columns(2)
    with col_a:
        humeur = st.select_slider("Humeur", options=["😢", "😐", "🙂", "✨"])
        txt = st.text_input("Note rapide...")
        cat = st.selectbox("Type", ["Note", "RDV", "Tâche"])
        if st.button("Enregistrer"):
            ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), cat, txt])
            st.success("Enregistré !")
            st.rerun()

with tab2:
    # Gestion des semaines
    if 'offset' not in st.session_state: st.session_state.offset = 0
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.offset -= 1
    if c3.button("➡️"): st.session_state.offset += 1
    
    start_w = (datetime.now() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.offset)
    c2.subheader(f"Semaine du {start_w.strftime('%d/%m')}")

    # Grille Hebdo Rose
    cols = st.columns(7)
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    for i in range(7):
        curr = start_w + timedelta(days=i)
        d_str = curr.strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div class="p-header">{days[i]}<br>{curr.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            # Filtrage sécurisé
            events_html = ""
            day_data = df_notes[df_notes["Date"] == d_str]
            for _, row in day_data.iterrows():
                events_html += f'<div class="event-box"><b>{row["Heure"]}</b><br>{row["Note"]}</div>'
            st.markdown(f'<div class="p-cell">{events_html}</div>', unsafe_allow_html=True)

with tab3:
    st.title("Mon Budget")
    # Historique éditable
    data_f = ws_fin.get_all_records()
    if data_f:
        df_f = pd.DataFrame(data_f)
        edited = st.data_editor(df_f, num_rows="dynamic", use_container_width=True)
        if st.button("Sauvegarder Budget"):
            ws_fin.clear()
            ws_fin.update([edited.columns.values.tolist()] + edited.values.tolist())
            st.success("Budget mis à jour !")
