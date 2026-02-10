import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

# 1. CONNEXION
def init_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_info = {
        "type": "service_account", "project_id": "airy-semiotics-486311-v5",
        "private_key": st.secrets["MY_PRIVATE_KEY"], "client_email": st.secrets["MY_CLIENT_EMAIL"],
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    client = gspread.authorize(Credentials.from_service_account_info(creds_info, scopes=scope))
    return client.open("db_bujo")

sh = init_connection()
ws_notes, ws_fin, ws_conf = sh.worksheet("Note"), sh.worksheet("Finances"), sh.worksheet("Config")

# 2. STYLE & ONGLETS (iPad Friendly)
st.set_page_config(page_title="MeyLune Bujo", layout="wide")
st.markdown("""
<style>
    /* Onglets larges comme demandé */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px; background-color: #ffffff; border-radius: 15px 15px 0 0;
        padding: 10px 30px; border: 1px solid #e0e0e0; font-weight: bold; color: #2e7d32;
    }
    .stTabs [aria-selected="true"] { background-color: #4caf50 !important; color: white !important; }
    
    /* Design Planning Rose */
    .p-header { background-color: #f06292; color: white; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    .p-cell { background-color: white; min-height: 250px; padding: 10px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; margin-bottom: 10px; }
    .event { background: #fff1f3; border-left: 4px solid #f06292; padding: 5px; margin-bottom: 5px; border-radius: 4px; font-size: 0.8rem; color: #ad1457; }
</style>
""", unsafe_allow_html=True)

# 3. NAVIGATION PAR ONGLETS DIRECTS
tab_j, tab_s, tab_a, tab_b = st.tabs(["✍️ JOURNAL", "🌿 SEMAINE", "📅 ANNÉE", "💰 BUDGET"])

# --- JOURNAL (Humeur + Notes) ---
with tab_j:
    st.write(f"### Aujourd'hui, le {datetime.now().strftime('%d/%m/%Y')}")
    col1, col2 = st.columns(2)
    with col1:
        humeur = st.select_slider("Mon Humeur", options=["😢", "😐", "🙂", "✨"])
        note = st.text_input("Une pensée ?")
        # CORRECTION : On utilise des noms simples sans emojis pour éviter le KeyError
        type_n = st.selectbox("Style", ["Note", "RDV", "Tache"])
        if st.button("Enregistrer"):
            ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), type_n, note])
            st.success("C'est noté !")

# --- SEMAINE (Sélecteur + Planning Rose) ---
with tab_s:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️ Précédente"): st.session_state.w_off -= 1
    if c3.button("Suivante ➡️"): st.session_state.w_off += 1
    
    curr_start = (datetime.now() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    c2.markdown(f"<h3 style='text-align:center;'>Semaine du {curr_start.strftime('%d/%m')}</h3>", unsafe_allow_html=True)

    # Récupération sécurisée (Anti-KeyError)
    data = ws_notes.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0]) if len(data) > 1 else pd.DataFrame(columns=["Date", "Heure", "Type", "Note"])
    
    cols = st.columns(7)
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    for i in range(7):
        d = curr_start + timedelta(days=i)
        d_str = d.strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div class="p-header">{days[i]}<br>{d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            events = ""
            if not df.empty and "Date" in df.columns:
                # Filtrage souple pour éviter les plantages d'emojis
                mask = (df["Date"] == d_str) & (df["Type"].str.contains("RDV", na=False))
                for _, r in df[mask].iterrows():
                    events += f'<div class="event"><b>{r["Heure"]}</b><br>{r["Note"]}</div>'
            st.markdown(f'<div class="p-cell">{events}</div>', unsafe_allow_html=True)

# --- BUDGET (Historique + Édition) ---
with tab_b:
    st.markdown("### 💰 Gestion Budgétaire")
    df_f = pd.DataFrame(ws_fin.get_all_records())
    if not df_f.empty:
        new_df = st.data_editor(df_f, num_rows="dynamic", use_container_width=True)
        if st.button("Sauvegarder le budget"):
            ws_fin.clear()
            ws_fin.update([new_df.columns.values.tolist()] + new_df.values.tolist())
            st.success("Budget synchronisé !")
