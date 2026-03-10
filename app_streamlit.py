import streamlit as st
import pandas as pd
import time
from crud import *

st.set_page_config(page_title="Mon Petit Dressing", layout="wide")

# ----------------------------
# SIDEBAR NAVIGATION
# ----------------------------
menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Accueil",
        "Gestion BDD",
        "Assistant",
        "Dressing",
        "Historique"
    ]
)

# ----------------------------
# PAGE ACCUEIL / DASHBOARD
# ----------------------------
if menu == "Accueil":
    st.title("Dashboard - Mon Petit Dressing")

    vetements = get_all_vetements()
    tenues = get_all_tenues()

    st.subheader("Statistiques générales")
    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre de vêtements", len(vetements))
    
    if vetements:
        types_count = pd.Series([v[2] for v in vetements]).value_counts()
        couleurs_count = pd.Series([v[3] for v in vetements]).value_counts()
        
        st.subheader("Répartition des types de vêtements")
        st.bar_chart(types_count)
        
        st.subheader("Répartition des couleurs principales")
        st.bar_chart(couleurs_count)



# ----------------------------
# PAGE GESTION BDD
# ----------------------------
elif menu == "Gestion BDD":
    st.title("Gestion des Vêtements et Tenues")
    action = st.radio("Choisir une action", ["Vêtements", "Tenues"])

    # ---------- VETEMENTS ----------
    if action == "Vêtements":
        st.subheader("Ajouter un vêtement")
        nom_vetement = st.text_input("Nom")
        type_vetement = st.selectbox("Type",["Haut simple","Haut chaud","Bas court","Bas long","Ensemble","Accessoire"])
        couleur_principale = st.text_input("Couleur principale")
        couleur_secondaire = st.text_input("Couleur secondaire")
        propre = st.checkbox("Propre", value=True)


        if st.button("Ajouter vêtement"):
            if not nom_vetement or not type_vetement or not couleur_principale:
                st.error("Veuillez remplir tous les champs obligatoires.")
            else:

                if not couleur_secondaire:
                    couleur_secondaire = couleur_principale

                add_vetement(
                    nom_vetement,
                    type_vetement,
                    couleur_principale,
                    couleur_secondaire,
                    propre
                )

                message = st.success("Vêtement ajouté !")
                time.sleep(2)
                message.empty()


        st.subheader("Supprimer un vêtement")
        vetements = get_all_vetements()
        vetement_dict = {f"{v[0]} - {v[1]}": v[0] for v in vetements}
        vetement_select = st.selectbox("Sélectionner un vêtement", list(vetement_dict.keys()))

        if st.button("Supprimer vêtement"):
            delete_vetement(vetement_dict[vetement_select])
            st.success("Vêtement supprimé !")

    # ---------- TENUES ----------
    elif action == "Tenues":
        st.subheader("Créer une tenue")

        jour = st.date_input("Jour")

        temperature = st.number_input(
            "Température",
            min_value=-20,
            max_value=50,
            value=15,
            step=1,
            format="%d"
        )

        note = st.number_input(
            "Note /10",
            min_value=0,
            max_value=10,
            value=None,
            step=1,
            format="%d")


        if st.button("Créer la tenue"):
            if temperature is None:
                st.error("Veuillez renseigner la température.")
            else:
                id_tenue = create_tenue(jour, temperature, note)
                st.success(f"Tenue créée avec ID {id_tenue}")

        
        st.subheader("Supprimer une tenue")
        tenues = get_all_tenues()
        tenue_dict = {f"{v[0]} - {v[1]}": v[0] for v in tenues}
        tenue_select = st.selectbox("Sélectionner une tenue", list(tenue_dict.keys()))

        if st.button("Supprimer tenue"):
            delete_tenue(tenue_dict[tenue_select])
            st.success("Tenue supprimé !")

        st.subheader("Associer un vêtement à une tenue")
        tenues = get_all_tenues()
        vetements = get_all_vetements()
        tenue_dict = {f"{t[0]} - {t[1]}": t[0] for t in tenues}
        vetement_dict = {f"{v[0]} - {v[1]}": v[0] for v in vetements}
        tenue_select = st.selectbox("Choisir une tenue", list(tenue_dict.keys()))
        vetement_select = st.selectbox("Choisir un vêtement", list(vetement_dict.keys()))

        if st.button("Associer"):
            add_vetement_to_tenue(tenue_dict[tenue_select], vetement_dict[vetement_select])
            st.success("Vêtement ajouté à la tenue")

# ----------------------------
# PAGE ASSISTANT
# ----------------------------
elif menu == "Assistant":
    st.title("Assistant")
    st.info("Cette page sera développée prochainement.")

# ----------------------------
# PAGE DRESSING
# ----------------------------
elif menu == "Dressing":
    st.title("Dressing")
    vetements = get_all_vetements()

    if vetements:
        df = pd.DataFrame(vetements, columns=["ID","Nom", "Type", "Couleur principale", "Couleur secondaire", "Propre"])
        st.dataframe(df)
    else:
        st.info("Aucun vêtement disponible.")

# ----------------------------
# PAGE HISTORIQUE
# ----------------------------
elif menu == "Historique":
    st.title("Historique des tenues")

    tenues = get_all_tenues()
    if tenues:
        df = pd.DataFrame(tenues, columns=["ID", "Jour", "Température", "Note"])
        df['Jour'] = pd.to_datetime(df['Jour'])
        st.subheader("Calendrier des tenues")
        st.dataframe(df.sort_values('Jour'))

        st.subheader("Détails d'une tenue")
        tenue_dict = {f"{t[0]} - {t[1]}": t[0] for t in tenues}
        tenue_select = st.selectbox("Sélectionner une tenue", list(tenue_dict.keys()))
        vetements_tenue = get_vetements_from_tenue(tenue_dict[tenue_select])
        for v in vetements_tenue:
            st.write(
                f"**Type** : {v[1]}  | **Couleur principale** : {v[2]}  | **Couleur secondaire** : {v[3]}"
            )
    else:
        st.info("Aucune tenue enregistrée.")