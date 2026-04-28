import instapy

# Informations de connexion
username = "votre_nom_d'utilisateur"
password = "votre_mot_de_passe"

# Création d'un objet instapy
session = instapy.Instapy(username, password)

# Recherche de comptes à suivre
search_hashtag = "#example"
comptes = session.search_hashtag(search_hashtag, limit=10)

# Suivi des comptes
for compte in comptes:
    session.follow(compte["username"])

# Fermeture de la session
session.logout()