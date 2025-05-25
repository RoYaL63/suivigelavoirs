import streamlit as st
import json
import difflib

@st.cache_data
def charger_donnees():
    with open("Registrenationaldesgels.json", encoding="utf-8") as f:
        data = json.load(f)

    # Cas réel : le JSON contient "Publications" > "PublicationDetail"
    publications = data.get("Publications", [])
    if not publications:
        return [], "Aucune publication"

    publication = publications[0]
    date = publication.get("Date", "inconnue")
    details = publication.get("PublicationDetail", [])

    return details, date

# Chargement des données
registre, date_pub = charger_donnees()

# UI Streamlit
st.set_page_config(page_title="Gel des avoirs", page_icon="🔒")
st.title("🔍 Registre des gels des avoirs")
st.write(f"📅 Dernière publication : **{date_pub}**")

nom = st.text_input("Nom recherché (obligatoire)").strip().upper()
prenom = st.text_input("Prénom (optionnel)").strip()
recherche_floue = st.checkbox("🔁 Activer la recherche approximative", value=True)

if st.button("Rechercher"):
    if not nom:
        st.warning("Merci de renseigner au moins un nom.")
    else:
        resultats = []

        for personne in registre:
            nom_personne = personne.get("Nom", "").upper()
            prenom_personne = ""
            naissance = motifs = fondement = ""

            for champ in personne.get("RegistreDetail", []):
                if champ["TypeChamp"] == "PRENOM":
                    prenom_personne = champ["Valeur"]
                if champ["TypeChamp"] == "DATE_DE_NAISSANCE":
                    naissance = champ["Valeur"]
                if champ["TypeChamp"] == "MOTIFS":
                    motifs = champ["Valeur"]
                if champ["TypeChamp"] == "FONDEMENT_JURIDIQUE":
                    fondement = champ["Valeur"]

            if recherche_floue:
                nom_match = difflib.get_close_matches(nom, [nom_personne], n=1, cutoff=0.7)
                prenom_match = True if not prenom else difflib.get_close_matches(prenom.lower(), [prenom_personne.lower()], n=1, cutoff=0.7)
            else:
                nom_match = nom == nom_personne
                prenom_match = True if not prenom else prenom.lower() == prenom_personne.lower()

            if nom_match and prenom_match:
                resultats.append({
                    "Nom": nom_personne,
                    "Prénom": prenom_personne,
                    "Naissance": naissance,
                    "Motif": motifs,
                    "Fondement juridique": fondement
                })

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

        if not resultats:
            st.info("Aucun résultat trouvé. Essaie une autre orthographe ou active la recherche approximative.")
