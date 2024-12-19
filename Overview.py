# from Utils import load_credentials,perfomance_globale_joueurs,meilleur_ami,classement_coachs,compet_favoris_par_nation,men_vs_women,service_and_meteo,perf_tournoi_majeurs,perf_by_age,evolution_age,perf_by_ranking,meilleur_ennemi,analyse_blessures,stats_finales,sponsoring,perf_by_surface,general,nation_formation
from Utils import *
from Database import Database
import streamlit as st
import pandas as pd

# Load players data
players = pd.read_csv('data/competitors.csv')

# Image URL
image_url = 'logo.png'

# Load image if necessary
# image = Image.open(image_url)
# st.image(image, width=100)

# Sidebar for navigation
option = st.sidebar.radio(
    "Requetes : ",
    [
        "Général",
        "Performance Globale des Joueurs",
        "Performance par Surface de Jeu",
        "Performance en Tournois Majeurs",
        "Tennis & Précocité",
        "Perfomance en fonction de l'age",
        "Performance en Fonction du Ranking",
        "Mes Meilleurs Ennemis",
        "Mon Meilleur Ami",
        "Blessures",
        "Statistiques des Finales",
        "Nation (Compétitions favorites)",
        "Influence de la Météo sur le Service",
        "Nation & Formation",
        "Sponsoring",
        "Classement des Coachs",
        "Profil Météo",
        "Men vs Women"
    ]
)

# App Header
if option == "Général":
    st.header("Notre Graphe")
    general()



# Performance Globale des Joueurs
elif option == "Performance Globale des Joueurs":
    perfomance_globale_joueurs()

# Performance par Surface de Jeu
elif option == "Performance par Surface de Jeu":
    perf_by_surface()


# Performance en Tournois Majeurs
elif option == "Performance en Tournois Majeurs":
    perf_tournoi_majeurs()

# Performance en Fonction de l'Age
elif option == "Tennis & Précocité":
    perf_by_age()

elif option == "Perfomance en fonction de l'age":
    evolution_age()

# Performance en Fonction du Ranking
elif option == "Performance en Fonction du Ranking":
    perf_by_ranking()

# Mes Meilleurs Ennemis
elif option == "Mes Meilleurs Ennemis":
    meilleur_ennemi()

# Mon Meilleur Ami
elif option == "Mon Meilleur Ami":
    meilleur_ami()

# Blessures
elif option == "Blessures":
    analyse_blessures()

elif option == "Statistiques des Finales":
    stats_finales()

# Nation
elif option == "Nation (Compétitions favorites)":
    compet_favoris_par_nation()

# Influence de la Météo sur le Service
elif option == "Influence de la Météo sur le Service":
    service_and_meteo()

# Le Court Favori des Nations/Joueurs
elif option == "Le Court Favori des Nations/Joueurs":
    st.header("Le Court Favori des Nations/Joueurs", divider=True)
    # Add relevant content for this section

# La Performance et la Raquette
elif option == "Sponsoring":
    sponsoring()

# Classement des Coachs
elif option == "Classement des Coachs":
    classement_coachs()

# Profil Météo
elif option == "Profil Météo":
    # st.header("Profil Météo", divider=True)
    # Add relevant content for this section
    #profil_meteo()
    pass

# Men vs Women
elif option == "Men vs Women":
    men_vs_women()

elif option == "Nation & Formation":
    nation_formation()
