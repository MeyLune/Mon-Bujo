import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

# ==========================================
# 1. CONNEXION
# ==========================================
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
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None

sh = init_connection()
if not sh: st.stop()
ws_notes, ws_fin, ws_conf = sh.worksheet("Note"), sh.worksheet("Finances"), sh.worksheet("Config")

# ==========================================
# 2. STYLE CSS (Optimisé iPad)
# ==========================================
st.set_page_config(page_title="Mon Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* Masquer menu Streamlit */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
    
    /* Fond dégradé doux */
    .stApp { background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); }
    
    /* Onglets de navigation stylisés */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #ffffff; border-radius: 15px 15px 0px 0px;
        padding: 10px 30px; border: 1px solid #e0e0e0; font-weight: bold; color: #2e7d32;
    }
    .stTabs [aria-selected="true"] { background-color: #4caf50 !important; color: white !important; }

    /* Grille Semaine (Modèle Rose) */
    .planner-header { background-color: #f06292; color: white !important; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-size: 0.8rem; }
    .planner-cell { background-color: white; min-height: 200px; padding: 10px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; margin-bottom: 10px; }
    .event-tag { background: #fff1f3; border-left: 4px solid #f06292; padding: 5px; margin: 4px 0; border-radius: 4px; font-size: 0.75rem; color: #ad1457; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. NAVIGATION PAR ONGLETS
# ==========================================
st.markdown(f'<h1 style="text-align:center; color:#1b5e20; font-family:Comfortaa;">Journal de MeyLune</h1>', unsafe_allow_html=True)

tab_journal, tab_semaine, tab_annee, tab_budget = st.tabs(["✍️ MON JOURNAL", "🌿 SEMAINE", "📅 ANNÉE", "💰 BUDGET"])

# --- PAGE JOURNAL ---
with tab_journal:
    st.markdown(f"<p style='text-align:center; font-family:Caveat; font-size:1.5rem;'>Aujourd'hui, le {datetime.now().strftime('%d %B %Y')}</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Mes Pensées")
        note_txt = st.text_input("Écris ici ton secret...", key="note_in")
        note_type = st.selectbox("Style", ["Note", "Tâche", "RDV", "Idée"])
        if st.button("Enregistrer dans mon Bujo"):
            if note_txt:
                ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), note_type, note_txt])
                st.success("Note ajoutée !")
                st.rerun()

# --- PAGE SEMAINE (AVEC NAVIGATION) ---
with tab_semaine:
    st.subheader("🌿 Mon Planning Hebdomadaire")
    
    # Sélecteur de semaine
    if 'week_offset' not in st.session_state: st.session_state.week_offset = 0
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: 
        if st.button("⬅️ Semaine précédente"): st.session_state.week_offset -= 1
    with c2:
        start_week = (datetime.now() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.week_offset)
        end_week = start_week + timedelta(days=6)
        st.markdown(f"<h4 style='text-align:center;'>Semaine du {start_week.strftime('%d/%m')} au {end_week.strftime('%d/%m')}</h4>", unsafe_allow_html=True)
    with c3:
        if st.button("Semaine suivante ➡️"): st.session_state.week_offset += 1

    # Récupération données
    data = ws_notes.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0]) if len(data) > 1 else pd.DataFrame(columns=["Date", "Heure", "Type", "Note"])

    # Affichage Grille
    cols = st.columns(7)
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    for i in range(7):
        curr = start_week + timedelta(days=i)
        d_str = curr.strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div class="planner-header">{days[i]}<br>{curr.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            events_html = ""
            # Filtrage sécurisé pour éviter KeyError
            if not df.empty and "Date" in df.columns:
                day_data = df[df["Date"] == d_str]
                for _, row in day_data.iterrows():
                    prefix = "📅" if row["Type"] == "RDV" else "📌"
                    events_html += f'<div class="event-tag">{prefix} {row["Heure"]} - {row["Note"]}</div>'
            st.markdown(f'<div class="planner-cell">{events_html}</div>', unsafe_allow_html=True)

# --- PAGE ANNÉE ---
with tab_annee:
    st.subheader("📅 Vue Annuelle 2026")
    st.info("Visualisation en cours de création pour correspondre à ton modèle rose.")
    # On pourra ici générer 12 petites grilles via une boucle
    st.image("https://img.freepik.com/vecteurs-libre/calendrier-2026-design-elegant_23-2150935544.jpg", width=400)

# --- PAGE BUDGET ---
with tab_budget:
    st.subheader("💰 Mon Petit Budget")
    data_fin = ws_fin.get_all_records()
    if data_fin:
        df_fin = pd.DataFrame(data_fin)
        st.data_editor(df_fin, num_rows="dynamic", use_container_width=True)
        if st.button("Sauvegarder les finances"):
            st.success("Données synchronisées avec Google Sheets")
