import streamlit as st
import requests

st.set_page_config(page_title="Recherche Gel des Avoirs - API Officielle", page_icon="🔒")
st.title("🔍 Recherche directe via l’API de l’État")

# Formulaire de recherche
nom = st.text_input("Nom recherché (obligatoire)").strip()
prenom = st.text_input("Prénom (optionnel)").strip()

# Requête à l'API publique
@st.cache_data
def rechercher(nom, prenom=None):
    url = "https://gels-avoirs.dgtresor.gouv.fr/ApiPublic/api/v1/recherche/criteres"
    params = {"nom": nom}
    if prenom:
        params["prenom"] = prenom
    headers = {
        "User-Agent": "OtterWise/RechercheGelsApp"
    }

    try:
        r = requests.get(url, params=params, headers=headers)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# Bouton de recherche
if st.button("Rechercher"):
    if not nom:
        st.warning("⚠️ Merci d’indiquer un nom.")
    else:
        resultats = rechercher(nom.upper(), prenom)

        if "error" in resultats:
            st.error(f"Erreur lors de la requête : {resultats['error']}")
        elif not resultats:
            st.info("Aucun résultat trouvé.")
        else:
            st.success(f"{len(resultats)} résultat(s) trouvé(s) :")
            for personne in resultats:
                st.markdown("---")
                st.write(f"👤 **{personne.get('nom', '')} {personne.get('prenom', '')}**")
                st.write(f"📅 Né le {personne.get('dateNaissance', 'N/A')} à {personne.get('lieuNaissance', 'N/A')}")
                st.write(f"⚖️ Fondement juridique : {personne.get('fondementJuridique', 'N/A')}")
                st.write(f"📌 Motif(s) : {personne.get('motifsSanction', 'Aucun')}")
