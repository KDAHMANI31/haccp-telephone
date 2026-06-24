import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuration de la page pour Smartphone
st.set_page_config(page_title="HACCP Mobile Pro", layout="centered")

# 2. Sécurité par mot de passe
if "auth_mobile" not in st.session_state:
    st.session_state["auth_mobile"] = False

if not st.session_state["auth_mobile"]:
    st.title("🔐 Accès Cuisine - HACCP Mobile")
    password = st.text_input("Mot de passe sécurité", type="password")
    if st.button("Se connecter", use_container_width=True):
        if password == "Haccp2026":
            st.session_state["auth_mobile"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")
    st.stop()

# --- INITIALISATION DU REGISTRE EN MÉMOIRE ---
if "data_mobile_cf" not in st.session_state:
    st.session_state["data_mobile_cf"] = pd.DataFrame(columns=[
        "Date/Heure", "Contrôleur", "Zone / Service", "Chambre Froide", "Température (°C)", "Statut", "Observations"
    ])

# --- INTERFACE MOBILE ---
st.title("🌡️ Contrôle des Chambres Froides")
st.write("Saisie rapide sur le terrain pour l'hygiéniste.")

# Dictionnaire complet des Zones et de leurs Chambres Froides respectives
STRUCTURE_HOTEL = {
    "Cuisine Centrale": ["CF Viandes N°1", "CF Volailles N°2", "CF Poissons N°3", "CF Légumes N°4", "CF Plats Cuisinés"],
    "Boulangerie / Pâtisserie": ["CF Matières Premières Pâtisserie", "CF Produits Finis Pâtisserie", "Enceinte Positive Boulangerie"],
    "Boucherie": ["CF Carcasses", "CF Produits Parés"],
    "Restaurant Principal / Buffet": ["CF Jour Restaurant", "Meuble Froid Buffet Salades", "Meuble Froid Desserts"],
    "Banquet / Événementiel": ["CF Stockage Banquet", "Cellule de Refroidissement Rapide"],
    "Économat / Stockage Central": ["CF Produits Laitiers", "CF Fruits & Légumes Gros", "CF Produits Surgelés -20°C"]
}

with st.form("form_haccp_mobile", clear_on_submit=True):
    nom_ctrl = st.text_input("Nom du contrôleur", value="Khaled Dahmani")
    
    # 1. Sélection de la Zone
    zone_selectionnee = st.selectbox("Sélectionner la Zone :", list(STRUCTURE_HOTEL.keys()))
    
    # 2. Sélection de la Chambre Froide en fonction de la zone choisie
    cf_selectionnee = st.selectbox("Sélectionner l'élément / CF :", STRUCTURE_HOTEL[zone_selectionnee])
    
    # 3. Saisie de la température
    # Définition automatique de la valeur par défaut selon si c'est un congélateur ou non
    valeur_par_defaut = -18.0 if "Surgelés" in cf_selectionnee else 2.0
    temperature = st.number_input("Température relevée (°C) :", value=valeur_par_defaut, step=0.5)
    
    remarques = st.text_input("Observations / Actions Correctives (Obligatoire si Alerte 🚨)")
    
    submit = st.form_submit_button("📱 Enregistrer le contrôle", use_container_width=True)
    
    if submit:
        # Détermination des normes HACCP et Système d'Alerte
        is_congelateur = "Surgelés" in cf_selectionnee or "-20°C" in cf_selectionnee
        
        if is_congelateur:
            limite = -18.0
            est_conforme = temperature <= -18.0
            norme_texte = "Norme <= -18°C"
        else:
            limite = 4.0
            est_conforme = temperature <= 4.0
            norme_texte = "Norme <= 4°C"
            
        if est_conforme:
            statut = "CONFORME ✅"
            st.success(f"Excellent ! Température conforme pour {cf_selectionnee} ({temperature} °C).")
        else:
            statut = "🚨 ALERTE NON-CONFORME"
            st.critical(f"🚨 DANGER HACCP : La température de {cf_selectionnee} est de {temperature} °C ! ({norme_texte})")
            if not remarques:
                st.warning("⚠️ Pensez à noter l'action corrective prise (ex: Relance moteur, appel technique) dans les observations.")

        # Ajout direct dans le tableau
        nouvelle_mesure = pd.DataFrame([{
            "Date/Heure": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Contrôleur": nom_ctrl,
            "Zone / Service": zone_selectionnee,
            "Chambre Froide": cf_selectionnee,
            "Température (°C)": f"{temperature} °C",
            "Statut": statut,
            "Observations": remarques if remarques else "R.A.S"
        }])
        
        st.session_state["data_mobile_cf"] = pd.concat([st.session_state["data_mobile_cf"], nouvelle_mesure], ignore_index=True)

# --- RECAPITULATIF ET TELECHARGEMENT MOBILE ---
if not st.session_state["data_mobile_cf"].empty:
    st.write("---")
    st.subheader("📊 Mesures enregistrées dans la session")
    
    # Affichage du tableau sous forme de cartes simplifiées ou tableau léger pour mobile
    st.dataframe(st.session_state["data_mobile_cf"], use_container_width=True)
    
    # Export Excel direct depuis le smartphone
    csv_mobile = st.session_state["data_mobile_cf"].to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Télécharger le rapport de contrôle (.csv)",
        data=csv_mobile,
        file_name=f"haccp_mobile_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )
