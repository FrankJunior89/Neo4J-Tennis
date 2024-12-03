from Utils import load_credentials , Departements
from Database import Database
import streamlit as st
from PIL import Image
import pandas as pd



players = pd.read_csv('data/competitors.csv')



image_url = 'logo.png'

#image = Image.open(image_url)

#st.image(image,width=100)  




st.header("Tennis Perfomance Analysis")




st.header("Perfomance Globale des Joueurs ",divider=True)

st.markdown("#### Vue générale")

st.markdown("#### Requete")

requete = """
MATCH (p:Player)
OPTIONAL MATCH (p)-[:WON]->(w:Game)
OPTIONAL MATCH (p)-[:LOST]->(l:Game)
WITH p, 
     COUNT(w) AS wins, 
     COUNT(l) AS losses, 
     (COUNT(w) * 1.0) / (COUNT(w) + COUNT(l)) AS winrate
ORDER BY winrate DESC
LIMIT 10
RETURN p.name AS Player, wins, losses, winrate

"""

st.markdown(f"```cypher\n{requete}\n```")

if st.button("Exécuter la requête"):
    st.text('Execution de la requete...')

st.markdown("#### Vue personnalisée")

option = st.selectbox(
    "Choix du joueur",
    players['name'],
)

st.header("Perfomance par Surface de Jeu ",divider=True)

st.header("Perfomance par Saison ",divider=True)

st.header("Perfomance en tournoi majeurs ",divider=True)

st.header("Perfomance en fonction de l'age ",divider=True)

st.header("Perfomance en fonction du ranking",divider=True)

st.header("Mes meilleurs ennemis",divider=True)





