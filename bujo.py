import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd
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

# --- 2. STYLE & DESIGN ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Indie+Flower&display=swap');
    
    .stApp {{ background-image: url("{fond_url}"); background-size: cover; background-attachment: fixed; background-color: white !important; }}
    
    /* Zones de saisie style iPad */
    div[data-baseweb="textarea"], div[data-baseweb="input"], .stTextArea textarea, .stTextInput input {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #5d4037 !important; border-radius: 12px !important;
        border: 1px solid #f06292 !important;
    }}

    /* Carte Fiche de Lecture (Beige) */
    .lecture-card {{
        background-color: #fdf5e6 !important;
        border: 2px solid #d2b48c !important;
        border-radius: 15px; padding: 25px; color: #5d4037 !important;
    }}
    
    .p-header {{ background-color: #f06292 !important; color: white !important; padding: 10px; text-align: center; border-radius: 10px; font-weight: bold; }}
    h1, h2, h3, label {{ color: #1b5e20 !important; font-family: 'Comfortaa', cursive; }}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "user_data" not in st.session_state: st.session_state.user_data = None
if not st.session_state.user_data:
    st.markdown("<h1 style='text-align:center;'>🌿 Bienvenue dans ton Journal</h1>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal") or code == "2125":
            st.session_state.user_data = {"Nom": "MeyLune"}
            st.rerun()
    st.stop()

user_nom = st.session_state.user_data['Nom']
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ONGLET JOURNAL ---
with tabs[0]:
    st.markdown(f"### 🖋️ Mes pensées du {datetime.now().strftime('%d/%m/%Y')}")
    note_j = st.text_area("Aujourd'hui, je me sens...", height=300, label_visibility="collapsed")
    if st.button("💾 Enregistrer la pensée"):
        if sh: sh.worksheet("Journal").append_row([datetime.now().strftime("%d/%m/%Y"), user_nom, note_j])
        st.success("C'est noté ! ✨")

# --- ONGLET SEMAINE ---
with tabs[1]:
    if 'w_off' not in st.session_state: st.session_state.w_off = 0
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_off)
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("⬅️"): st.session_state.w_off -= 1; st.rerun()
    if c3.button("➡️"): st.session_state.w_off += 1; st.rerun()
    c2.markdown(f"<h3 style='text-align:center;'>Semaine {start_week.isocalendar()[1]} - {start_week.year}</h3>", unsafe_allow_html=True)
    
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    cols_sem = st.columns(2)
    for i, j in enumerate(jours):
        with cols_sem[i % 2]:
            st.markdown(f'<div class="p-header">{j}</div>', unsafe_allow_html=True)
            st.text_area(f"Note {j}", height=100, key=f"wk_{j}", label_visibility="collapsed")

# --- ONGLET ANNEE ---
with tabs[2]:
    mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                cal = calendar.TextCalendar(firstweekday=0).formatmonth(2026, m_idx)
                cal_body = "<br>".join(cal.splitlines()[2:])
                st.markdown(f'<div style="background:white; padding:10px; border-radius:10px; border:1px solid #f06292;"><div class="p-header">{mois_fr[m_idx-1]}</div><div style="text-align:center; font-family:monospace; font-size:14px;"><b style="color:#f06292;">Lu Ma Me Je Ve Sa Di</b><br>{cal_body}</div></div>', unsafe_allow_html=True)

# --- ONGLET TRACKERS & LECTURE ---
with tabs[3]:
    cat = st.radio("Sous-catégorie", ["📊 Santé", "📖 Lecture"], horizontal=True)
    
    if cat == "📊 Santé":
        st.slider("💧 Eau", 0, 10, 5)
        st.slider("😴 Sommeil", 0, 12, 8)
        st.checkbox("🏃 Sport")
    else:
        st.markdown('<div class="lecture-card">', unsafe_allow_html=True)
        st.markdown("## 📖 Ma Fiche de Lecture")
        col_l1, col_l2 = st.columns([2, 1])
        
        with col_l1:
            t_livre = st.text_input("TITRE DU LIVRE")
            a_livre = st.text_input("AUTEUR")
            d_debut = st.date_input("DÉBUT")
            d_fin = st.date_input("FINI")
            note_livre = st.select_slider("NOTE /10", options=list(range(1, 11)))
        
        with col_l2:
            st.write("📸 Couverture")
            img_livre = st.file_uploader("Upload", type=['jpg','png','jpeg'], label_visibility="collapsed")
            if img_livre: st.image(img_livre, width=150)

        st.markdown("### 🎭 Mon ressenti")
        c_r1, c_r2, c_r3, c_r4 = st.columns(4)
        tristesse = c_r1.select_slider("💧 Tristesse", options=[1,2,3,4,5], key="tri")
        picante = c_r2.select_slider("🌶️ Picante", options=[1,2,3,4,5], key="pic")
        humour = c_r3.select_slider("😊 Humour", options=[1,2,3,4,5], key="hum")
        romance = c_r4.select_slider("❤️ Romance", options=[1,2,3,4,5], key="rom")
        
        sentiments = st.multiselect("Sentiments", ["Coup de cœur ❤️", "À lire absolument", "M'a fait pleurer", "Ennuyeux"])
        playlist = st.text_area("🎵 Playlist / Citations / Notes")
        
        if st.button("📥 AJOUTER À MA BIBLIOTHÈQUE"):
            if sh and t_livre:
                data_l = [t_livre, a_livre, str(d_debut), str(d_fin), note_livre, ", ".join(sentiments), playlist]
                sh.worksheet("Lectures").append_row(data_l)
                st.success(f"'{t_livre}' ajouté ! ✨")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- AFFICHAGE BIBLIOTHÈQUE ---
        st.markdown("### 📚 Ma Bibliothèque")
        if sh:
            df_l = pd.DataFrame(sh.worksheet("Lectures").get_all_records())
            if not df_l.empty:
                df_l = df_l.sort_values(by="Titre")
                for _, row in df_l.iterrows():
                    with st.expander(f"📖 {row['Titre']} - {row['Auteur']}"):
                        st.write(f"**Note :** {row['Note']}/10")
                        st.write(f"**Sentiments :** {row['Sentiment']}")
                        st.info(row['Note_Playlist'])

# --- COURSES & STICKERS (Restants) ---
with tabs[4]: st.write("🛒 Liste de courses")
with tabs[5]: st.write("🎨 Planche de stickers")
