import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION PROFESSIONNELLE DE LA PAGE
st.set_page_config(
    page_title="HACCP Pro - Marseille",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Style CSS pour cacher le menu Streamlit par défaut pour un look "application"
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 2. SÉCURITÉ ET CONNEXION PRO
if "auth_mobile" not in st.session_state:
    st.session_state["auth_mobile"] = False

if not st.session_state["auth_mobile"]:
    # Centre le formulaire de connexion
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>HACCP Connect Pro</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Veuillez vous authentifier</p>", unsafe_allow_html=True)
        password = st.text_input("Code d'accès", type="password", help="H...2026")
        if st.button("Se connecter 🔓", use_container_width=True, type="primary"):
            if password == "Haccp2026":
                st.session_state["auth_mobile"] = True
                st.rerun()
            else:
                st.error("Code incorrect")
    st.stop()

# --- HEADER PROFESSIONNEL DE L'APPLI ---
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🛡️ HACCP Connect <span style='font-size: 0.5em; color: gray;'>Marseille</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; margin-top: -15px;'>Registre Numérique des Températures</p>", unsafe_allow_html=True)
st.markdown("---")

# --- INITIALISATION DU REGISTRE ---
if "data_mobile_cf" not in st.session_state:
    st.session_state["data_mobile_cf"] = pd.DataFrame(columns=[
        "Date/Heure", "Contrôleur", "Zone / Service", "Chambre Froide", "Température", "Statut", "Observations"
    ])

# --- STRUCTURE DES CHAMBRES FROIDES ---
STRUCTURE_HOTEL = {
    "Cuisine Centrale": [
        "Chambre 1 (Positive)", "Chambre 2 (Positive)", "Chambre 3 (Positive)", "Chambre 4 (Négative)"
    ],
    "Pâtisserie": [
        "Chambre 5 (Positive)", "Chambre 6 (Positive)", "Chambre 7 (Positive)", "Chambre 8 (Négative)"
    ],
    "Boucherie": [
        "Chambre 9 (Positive)", "Chambre 10 (Négative)", "Chambre 11 (Positive)", "Chambre 12 (Négative)", 
        "Chambre 13 (Positive)", "Chambre 14 (Négative)", "Chambre 15 (Positive)", "Chambre 16 (Négative)"
    ],
    "Food Store": [
        "Chambre 17 (Positive)", "Chambre 18 (Négative)", "Chambre 19 (Positive)", "Chambre 20 (Négative)", 
        "Chambre 21 (Positive)", "Chambre 22 (Positive)", "Chambre 23 (Positive)"
    ]
}

# --- INTERFACE DE SAISIE PROFESSIONNELLE ---
with st.container(border=True): # Encadré pro pour le formulaire
    st.markdown("### 📝 Nouveau Relevé", unsafe_allow_html=True)
    
    # Affichage Date et Heure automatiques en haut
    date_now = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.info(f"**📅 Date & Heure :** {date_now}")

    # Formulaire de saisie
    with st.form("form_haccp_pro", clear_on_submit=True):
        # Informations contrôleur et Zone
        nom_ctrl = st.text_input("👤 Nom du contrôleur", value="Khaled Dahmani", placeholder="Ex: Jean Paul")
        zone_choisie = st.selectbox("🌐 Zone / Service :", list(STRUCTURE_HOTEL.keys()), index=0)
        cf_choisie = st.selectbox("🚪 Chambre Froide :", STRUCTURE_HOTEL[zone_choisie])
        
        st.markdown("---")
        
        # Section Mesure
        c1, c2 = st.columns([1, 2])
        with c1:
            hors_service = st.checkbox("❌ Hors Service", help="Si coché, la température sera ignorée.")
        
        with c2:
            valeur_defaut = -18.0 if "Négative" in cf_choisie else 2.0
            # Si Hors service, on grise la saisie
            temperature = st.number_input(
                "🌡️ Température relevée (°C) :", 
                value=valeur_defaut, 
                step=0.5,
                disabled=hors_service
            )
        
        remarques = st.text_input("💬 Observations / Action Corrective", placeholder="Ex: Tech appelé / R.A.S")
        
        # Bouton de validation primaire
        submit = st.form_submit_button("✅ Enregistrer le Relevé", use_container_width=True, type="primary")

        if submit:
            if hors_service:
                statut = "HORS SERVICE ❌"
                temp_finale = "N/A"
                obs_finale = f"ÉQUIPEMENT HORS SERVICE. {remarques}".strip()
                st.warning(f"Chambre {cf_choisie} enregistrée comme Hors Service.")
            else:
                temp_finale = f"{temperature} °C"
                obs_finale = remarques if remarques else "R.A.S"
                
                # Vérification HACCP et affichage alerte pro
                if "Négative" in cf_choisie:
                    conform = temperature <= -18.0
                else:
                    conform = temperature <= 4.0
                
                if conform:
                    statut = "Conforme ✅"
                    st.success(f"**{cf_choisie} : {temperature} °C**. Contrôle validé.")
                else:
                    statut = "Non Conforme 🚨"
                    # Grosse alerte rouge
                    st.markdown(f"<div style='padding:15px; background-color:#FEE2E2; color:#B91C1C; border-radius:10px; border:1px solid #B91C1C; text-align:center;'><h4>⚠️ ALERTE NON-CONFORME !</h4><b>{cf_choisie}</b> est à {temperature} °C. Norme dépassée.</div><br>", unsafe_allow_html=True)
            
            # Enregistrement
            nouvelle_mesure = pd.DataFrame([{
                "Date/Heure": date_now,
                "Contrôleur": nom_ctrl,
                "Zone / Service": zone_choisie,
                "Chambre Froide": cf_choisie,
                "Température": temp_finale,
                "Statut": statut,
                "Observations": obs_finale
            }])
            
            st.session_state["data_mobile_cf"] = pd.concat([st.session_state["data_mobile_cf"], nouvelle_mesure], ignore_index=True)

# --- RECAPITULATIF ET TÉLÉCHARGEMENT PROFESSIONNEL ---
if not st.session_state["data_mobile_cf"].empty:
    st.write("---")
    
    # Titre et bouton de téléchargement côte à côte
    cap1, cap2 = st.columns([2, 1])
    with cap1:
        st.subheader("📊 Données de la Session")
    with cap2:
        csv_mobile = st.session_state["data_mobile_cf"].to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Télécharger Rapport CSV",
            data=csv_mobile,
            file_name=f"haccp_marseille_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="secondary"
        )
    
    # Affichage du tableau de manière propre
    st.dataframe(
        st.session_state["data_mobile_cf"], 
        use_container_width=True, 
        hide_index=True
    )
