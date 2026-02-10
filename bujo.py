import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

# --- 1. CONNEXION ROBUSTE (Récupère tes accès) ---
def init_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        # On utilise exactement les clés de tes secrets
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
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None

sh = init_connection()

# --- 2. STYLE & INTERFACE ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")
st.markdown("""
<style>
    /* Onglets Roses */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px; background-color: #ffffff; border-radius: 15px 15px 0 0;
        padding: 10px 30px; border: 1px solid #e0e0e0; font-weight: bold; color: #f06292;
    }
    .stTabs [aria-selected="true"] { background-color: #f06292 !important; color: white !important; }
    
    /* Grille Planning Hebdo */
    .p-header { background-color: #f06292; color: white; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-weight: bold; }
    .p-cell { background-color: white; min-height: 250px; padding: 10px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; margin-bottom: 10px; }
    .event-tag { background: #fff1f3; border-left: 4px solid #f06292; padding: 5px; margin-bottom: 5px; border-radius: 4px; font-size: 0.85rem; color: #ad1457; }
</style>
""", unsafe_allow_html=True)

if sh:
    ws_notes = sh.worksheet("Note")
    ws_fin = sh.worksheet("Finances")
    
    # --- NAVIGATION ---
    tab_j, tab_s, tab_b = st.tabs(["✍️ JOURNAL", "🌿 SEMAINE", "💰 BUDGET"])

    # --- PAGE JOURNAL ---
    with tab_j:
        st.markdown(f"### Nous sommes le {datetime.now().strftime('%d/%m/%Y')}")
        c1, c2 = st.columns(2)
        with c1:
            humeur = st.select_slider("Mon Humeur", options=["😢", "😐", "🙂", "✨"])
            note_rapide = st.text_input("Une pensée ?")
            type_n = st.selectbox("Type", ["Note", "RDV", "Tâche"])
            if st.button("Enregistrer dans mon Bujo"):
                ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), type_n, note_rapide])
                st.success("C'est enregistré !")

    # --- PAGE SEMAINE (SÉCURISÉE) ---
    with tab_s:
        if 'w_offset' not in st.session_state: st.session_state.w_offset = 0
        
        nav1, nav2, nav3 = st.columns([1, 2, 1])
        if nav1.button("⬅️ Semaine Précédente"): st.session_state.w_offset -= 1
        if nav3.button("Semaine Suivante ➡️"): st.session_state.w_offset += 1
        
        start_w = (datetime.now() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_offset)
        nav2.markdown(f"<h3 style='text-align:center;'>Semaine du {start_w.strftime('%d/%m')}</h3>", unsafe_allow_html=True)

        # Récupération des données avec sécurité anti-KeyError
        raw_data = ws_notes.get_all_values()
        df = pd.DataFrame(raw_data[1:], columns=raw_data[0]) if len(raw_data) > 1 else pd.DataFrame()

        cols = st.columns(7)
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        
        for i in range(7):
            curr_date = start_w + timedelta(days=i)
            d_str = curr_date.strftime("%d/%m/%Y")
            with cols[i]:
                st.markdown(f'<div class="p-header">{days[i]}<br>{curr_date.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                
                # Zone de contenu
                content = ""
                if not df.empty and "Date" in df.columns:
                    # On filtre sans risque de plantage
                    day_filter = df[df["Date"] == d_str]
                    for _, row in day_filter.iterrows():
                        # On récupère les colonnes par index si le nom pose souci
                        heure = row.iloc[1] if len(row) > 1 else ""
                        texte = row.iloc[3] if len(row) > 3 else ""
                        content += f'<div class="event-tag"><b>{heure}</b>: {texte}</div>'
                
                st.markdown(f'<div class="p-cell">{content}</div>', unsafe_allow_html=True)

    # --- PAGE BUDGET ---
    with tab_b:
        st.title("Mes Finances")
        fin_data = ws_fin.get_all_records()
        if fin_data:
            df_fin = pd.DataFrame(fin_data)
            edited = st.data_editor(df_fin, num_rows="dynamic", use_container_width=True)
            if st.button("Mettre à jour Google Sheets"):
                ws_fin.clear()
                ws_fin.update([edited.columns.values.tolist()] + edited.values.tolist())
                st.success("Fichier mis à jour !")
else:
    st.warning("En attente de connexion...")
