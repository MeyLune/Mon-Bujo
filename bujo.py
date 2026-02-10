import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

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
    except:
        return None

sh = init_connection()

# --- 2. RESTAURATION DU DESIGN (Vert & Rose) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3 { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }
    
    /* Navigation par Onglets */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px; background-color: white; border-radius: 15px 15px 0 0;
        padding: 10px 30px; font-weight: bold; color: #2e7d32; border: 1px solid #c8e6c9;
    }
    .stTabs [aria-selected="true"] { background-color: #4caf50 !important; color: white !important; }

    /* Blocs Journal */
    .bujo-block { background: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; margin-bottom: 20px; }

    /* Grille Hebdo Rose */
    .p-header { background-color: #f06292; color: white; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    .p-cell { background-color: white; min-height: 250px; padding: 10px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; }
    .event-tag { background: #fff1f3; border-left: 4px solid #f06292; padding: 5px; margin-bottom: 5px; border-radius: 4px; font-size: 0.8rem; color: #ad1457; }
</style>
""", unsafe_allow_html=True)

if not sh:
    st.error("Lien Google Sheets rompu. Vérifie tes secrets Streamlit.")
    st.stop()

ws_notes = sh.worksheet("Note")
ws_fin = sh.worksheet("Finances")

# --- 3. NAVIGATION ---
st.markdown("<h1 style='text-align:center;'>Journal de MeyLune</h1>", unsafe_allow_html=True)
tab_j, tab_s, tab_b = st.tabs(["✍️ MON JOURNAL", "🌿 SEMAINE", "💰 BUDGET"])

# --- PAGE JOURNAL (Design restauré) ---
with tab_j:
    st.markdown(f"<p style='text-align:center;'>Nous sommes le {datetime.now().strftime('%d %B %Y')}</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="bujo-block"><h3>😊 Mon Humeur & État</h3>', unsafe_allow_html=True)
        humeur = st.select_slider("Humeur", options=["😢", "😟", "😐", "🙂", "✨", "🔥"], value="😐")
        sens = st.text_area("Comment je me sens ?", placeholder="Détaille tes émotions...")
        st.markdown('<p style="color:#e91e63; font-style:italic;">"Je suis capable de réaliser mes rêves."</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="bujo-block"><h3>📋 Mon Programme</h3>', unsafe_allow_html=True)
        prog = st.text_area("Planning de la journée", height=215, placeholder="08h00 : Méditation...")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 🖋️ Notes & RDV Rapides")
    c1, c2, c3 = st.columns([3, 1, 1])
    n_txt = c1.text_input("Nouvelle entrée...")
    n_typ = c2.selectbox("Style", ["Note", "RDV", "Tâche"])
    if c3.button("Ancrer au Journal"):
        ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), n_typ, n_txt])
        st.rerun()

# --- PAGE SEMAINE (Grille Rose & Sécurisée) ---
with tab_s:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    nav_c1, nav_c2, nav_c3 = st.columns([1, 2, 1])
    if nav_c1.button("⬅️ Semaine Précédente"): st.session_state.w_off -= 1
    if nav_c3.button("Semaine Suivante ➡️"): st.session_state.w_off += 1
    
    start_d = (datetime.now() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    nav_c2.markdown(f"<h3 style='text-align:center;'>Semaine du {start_d.strftime('%d/%m')}</h3>", unsafe_allow_html=True)

    # Lecture des données (SÉCURITÉ ANTI-KEYERROR)
    data = ws_notes.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0]) if len(data) > 1 else pd.DataFrame()

    cols = st.columns(7)
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    for i in range(7):
        curr = start_d + timedelta(days=i)
        d_str = curr.strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div class="p-header">{days[i]}<br>{curr.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            evs = ""
            if not df.empty and len(df.columns) >= 4:
                # Filtrage sur la 1ère colonne (Date)
                mask = df.iloc[:, 0] == d_str
                for _, r in df[mask].iterrows():
                    evs += f'<div class="event-tag"><b>{r.iloc[1]}</b><br>{r.iloc[3]}</div>'
            st.markdown(f'<div class="p-cell">{evs}</div>', unsafe_allow_html=True)

# --- PAGE BUDGET ---
with tab_b:
    st.markdown("### 💰 Mes Finances")
    fin_data = ws_fin.get_all_records()
    if fin_data:
        df_f = pd.DataFrame(fin_data)
        new_f = st.data_editor(df_f, num_rows="dynamic", use_container_width=True)
        if st.button("Sauvegarder Budget"):
            ws_fin.clear()
            ws_fin.update([new_f.columns.values.tolist()] + new_f.values.tolist())
            st.success("Synchronisé !")
