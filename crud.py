from database import connexion_database

#===============================
# VETEMENTS
#===============================

def get_all_vetements():
    bdd = connexion_database()
    curseur = bdd.cursor()

    curseur.execute("SELECT * FROM vetement")

    rows = curseur.fetchall()

    curseur.close()
    bdd.close()

    return rows


def add_vetement(nom, type_vetement, couleur_principale, couleur_secondaire, propre):
    bdd = connexion_database()
    curseur = bdd.cursor()

    requete = """
    INSERT INTO vetement (nom, type, couleur_principale, couleur_secondaire, propre)
    VALUES (%s, %s, %s, %s, %s)
    """

    curseur.execute(requete, (nom, type_vetement, couleur_principale, couleur_secondaire, propre))

    bdd.commit()

    curseur.close()
    bdd.close()


def update_proprete_vetement(id_vetement, propre):
    bdd = connexion_database()
    curseur = bdd.cursor()

    requete = """
    UPDATE vetement
    SET propre = %s
    WHERE id_vetement = %s
    """

    curseur.execute(requete, (propre, id_vetement))

    bdd.commit()

    curseur.close()
    bdd.close()


def delete_vetement(id_vetement):
    bdd = connexion_database()
    curseur = bdd.cursor()

    curseur.execute("DELETE FROM vetement WHERE id_vetement = %s", (id_vetement,))

    bdd.commit()

    curseur.close()
    bdd.close()


#===============================
# TENUES
#===============================


def create_tenue(jour, temperature, note):
    bdd = connexion_database()
    curseur = bdd.cursor()

    requete = """
    INSERT INTO tenue (jour, temperature, note)
    VALUES (%s, %s, %s)
    RETURNING id_tenue
    """

    curseur.execute(requete, (jour, temperature, note))

    id_tenue = curseur.fetchone()[0]

    bdd.commit()

    curseur.close()
    bdd.close()

    return id_tenue


def get_all_tenues():
    bdd = connexion_database()
    curseur = bdd.cursor()

    curseur.execute("SELECT * FROM tenue")

    rows = curseur.fetchall()

    curseur.close()
    bdd.close()

    return rows


def delete_tenue(id_tenue):
    bdd = connexion_database()
    curseur = bdd.cursor()

    curseur.execute("DELETE FROM tenue WHERE id_tenue = %s", (id_tenue,))

    bdd.commit()

    curseur.close()
    bdd.close()


#===============================
# RELATION TENUES / VETEMENTS
#===============================

def add_vetement_to_tenue(id_tenue, id_vetement):
    bdd = connexion_database()
    curseur = bdd.cursor()

    requete = """
    INSERT INTO tenues_vetements (id_tenue, id_vetement)
    VALUES (%s, %s)
    """

    curseur.execute(requete, (id_tenue, id_vetement))

    bdd.commit()

    curseur.close()
    bdd.close()


def get_vetements_from_tenue(id_tenue):
    bdd = connexion_database()
    curseur = bdd.cursor()

    requete = """
    SELECT v.*
    FROM vetement v
    JOIN tenues_vetements tv
    ON v.id_vetement = tv.id_vetement
    WHERE tv.id_tenue = %s
    """

    curseur.execute(requete, (id_tenue,))

    rows = curseur.fetchall()

    curseur.close()
    bdd.close()

    return rows


def remove_vetement_from_tenue(id_tenue, id_vetement):
    bdd = connexion_database()
    curseur = bdd.cursor()

    requete = """
    DELETE FROM tenues_vetements
    WHERE id_tenue = %s AND id_vetement = %s
    """

    curseur.execute(requete, (id_tenue, id_vetement))

    bdd.commit()

    curseur.close()
    bdd.close()