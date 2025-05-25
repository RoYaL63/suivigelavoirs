import streamlit as st
import json

@st.cache_data
def charger_donnees():
   with open("Registrenationaldesgels.json", encoding="utf-8") as f:
        return json.load(f)

donnees = charger_donnees()
registre = donnees.get("PublicationDetail", [])
date_pub = donnees.get("DatePublication", "inconnue")

st.set_page_config(page_title="Gel des avoirs", page_icon="🔒")
st.title("🔍 Registre des gels des avoirs")
st.write(f"📅 Dernière publication : **{date_pub}**")

nom = st.text_input("Nom recherché (obligatoire)").strip().upper()
prenom = st.text_input("Prénom (optionnel)").strip()

if st.button("Rechercher"):
    if not nom:
        st.warning("Merci de renseigner au moins un nom.")
    else:
        resultats = []

        for personne in registre:
            if personne.get("Nom", "").upper() != nom:
                continue

            infos = {"Nom": personne.get("Nom")}
            for champ in personne.get("RegistreDetail", []):
                type_champ = champ.get("TypeChamp")
                valeur = champ.get("Valeur")

                if type_champ == "PRENOM":
                    infos["Prénom"] = valeur
                if type_champ == "DATE_DE_NAISSANCE":
                    infos["Naissance"] = valeur
                if type_champ == "MOTIFS":
                    infos["Motif"] = valeur
                if type_champ == "FONDEMENT_JURIDIQUE":
                    infos["Fondement juridique"] = valeur

            if not prenom or prenom.lower() in infos.get("Prénom", "").lower():
                resultats.append(infos)

        st.write(f"✅ {len(resultats)} résultat(s) trouvé(s)")
        for r in resultats:
            st.markdown("---")
            st.write(f"**👤 {r.get('Nom')} {r.get('Prénom', '')}**")
            if r.get("Naissance"):
                st.write(f"📅 Naissance : {r['Naissance']}")
            if r.get("Motif"):
                st.write(f"📌 Motif : {r['Motif']}")
            if r.get("Fondement juridique"):
                st.write(f"⚖️ Base juridique : {r['Fondement juridique']}")
