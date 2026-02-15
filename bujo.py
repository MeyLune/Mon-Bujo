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
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None

sh = init_connection()

# --- 2. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); }
    h1, h2, h3 { color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }
    
    /* Onglets iPad optimisés */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: rgba(255,255,255,0.6); border-radius: 12px 12px 0 0;
        padding: 10px 20px; color: #2e7d32; border: 1px solid #c8e6c9;
    }
    .stTabs [aria-selected="true"] { background-color: #4caf50 !important; color: white !important; }

    /* Blocs & Cartes Semaine */
    .bujo-block { background: white; padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .p-header { background-color: #f06292; color: white; padding: 8px; text-align: center; border-radius: 10px 10px 0 0; font-size: 0.9rem; }
    .p-cell { background-color: white; min-height: 180px; padding: 10px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; margin-bottom: 10px; }
    .event-tag { background: #fff1f3; border-left: 3px solid #f06292; padding: 4px 8px; margin-bottom: 6px; border-radius: 4px; font-size: 0.75rem; color: #ad1457; line-height: 1.2; }
</style>
""", unsafe_allow_html=True)

if not sh:
    st.stop()

# --- 3. LOGIQUE D'ACCÈS CONSULTANT ---
def check_consultant_access():
    if "consultant_auth" not in st.session_state:
        st.session_state.consultant_auth = False
    
    if not st.session_state.consultant_auth:
        st.warning("🔒 Cette section est protégée.")
        pwd = st.text_input("Entrez le Code Consultant :", type="password")
        if pwd == "MEY2026": # Ton code à modifier si besoin
            st.session_state.consultant_auth = True
            st.rerun()
        return False
    return True

# --- 4. NAVIGATION PRINCIPALE ---
st.markdown("<h1 style='text-align:center;'>🌿 MeyLune Bujo</h1>", unsafe_allow_html=True)
tab_j, tab_s, tab_b = st.tabs(["🔒 JOURNAL INTIME", "📅 SEMAINE", "💰 BUDGET"])

# --- TAB 1 : JOURNAL INTIME (Privé - Pas de code, accès direct pour toi) ---
with tab_j:
    st.markdown("### ✍️ Mon espace secret")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        humeur = st.select_slider("Mon énergie", options=["✨", "🙂", "😐", "😟", "🔋"])
        pensee = st.text_area("Pensée du jour (ne sera pas partagée)", height=150)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3590/3590660.png", width=150) # Petit icône déco
        st.info("Cette page est strictement personnelle et n'est pas visible avec le code consultant.")

# --- TAB 2 : SEMAINE (Accessible via Code) ---
with tab_s:
    if check_consultant_access():
        st.subheader("Planning Hebdomadaire")
        
        # Navigation Semaine
        if 'w_off' not in st.session_state: st.session_state.w_off = 0
        c1, c2, c3 = st.columns([1, 2, 1])
        if c1.button("⬅️ Précédent"): st.session_state.w_off -= 1
        if c3.button("Suivant ➡️"): st.session_state.w_off += 1
        
        start_d = (datetime.now() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
        c2.markdown(f"<p style='text-align:center;'><b>Semaine du {start_d.strftime('%d/%m/%Y')}</b></p>", unsafe_allow_html=True)

        # Récupération des données Note
        ws_notes = sh.worksheet("Note")
        data = ws_notes.get_all_values()
        
        # Correction de la grille
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            
            # Affichage en 2 lignes pour l'iPad (4 colonnes puis 3 colonnes) pour éviter que ce soit trop serré
            row1 = st.columns(4)
            row2 = st.columns(3)
            all_cols = row1 + row2
            
            for i in range(7):
                curr = start_d + timedelta(days=i)
                d_str = curr.strftime("%d/%m/%Y")
                
                with all_cols[i]:
                    st.markdown(f'<div class="p-header">{days_fr[i]} {curr.strftime("%d/%m")}</div>', unsafe_allow_html=True)
                    events_html = ""
                    # Filtrage sécurisé
                    day_events = df[df.iloc[:, 0] == d_str]
                    for _, r in day_events.iterrows():
                        # r[1]=Heure, r[2]=Type, r[3]=Texte
                        events_html += f'<div class="event-tag"><b>{r.iloc[1]}</b> | {r.iloc[3]}</div>'
                    
                    st.markdown(f'<div class="p-cell">{events_html}</div>', unsafe_allow_html=True)

# --- TAB 3 : BUDGET (Accessible via Code) ---
with tab_b:
    if check_consultant_access():
        st.subheader("Gestion du Budget")
        ws_fin = sh.worksheet("Finances")
        fin_data = ws_fin.get_all_records()
        
        if fin_data:
            df_f = pd.DataFrame(fin_data)
            edited_df = st.data_editor(df_f, num_rows="dynamic", use_container_width=True)
            if st.button("Enregistrer les modifications"):
                ws_fin.clear()
                ws_fin.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
                st.success("Données financières mises à jour !")
