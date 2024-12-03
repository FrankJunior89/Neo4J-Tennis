from Utils import load_credentials
from Database import Database
import streamlit as st


credentials = load_credentials('.gitignore/credentials.json')

URL = credentials['url']
USER = credentials['user']
PASSWORD = credentials['password']


st.markdown("# Notre projet")


texte = """

Notre approche en deux étapes commencera par une analyse descriptive, où nous 
visualiserons les performances individuelles et globales, identifierons les joueurs 
dominants, les surfaces préférées, ainsi que d’autres tendances clés.

Ensuite, nous passerons à une analyse explicative, où nous essaierons de trouver des 
relations entre ces performances et l’environnement de l’athlète notamment son pays 
de provenance (*NATION*) 

**Labels :**

- *PLAYERS* : Représente les joueurs de tennis. Ces joueurs sont connectés à leurs 
nations et leurs performances dans les matchs (*GAMES*). 
- *GAMES* : Représente les matchs joués, incluant les relations de victoire (Win) ou 
de défaite (Lost), et si le match a été joué à domicile (Home) ou à l’extérieur 
(Away). 
- *COURTS* : Représente les terrains de jeu (type de surface, comme terre battue ou 
gazon), un facteur clé de performance. 
- *COMPETITION* : Représente les compétitions ou tournois, classés dans des 
CATEGORY (par exemple, Grand Chelem ou ATP 250). 
- *SEASON* : Indique la saison ou l’année des matchs pour permettre une analyse 
temporelle. 
- *NATION* : Connecté aux joueurs pour examiner les performances selon leur pays. 
Les joueurs sont reliés aux matchs par des résultats (Win ou Lost), permettant 
d’analyser les tendances individuelles. 
Les compétitions ont une hiérarchie (Parent), ce qui va nous permettre entre autres 
d’explorer les performances selon l'importance des tournois. 
Les matchs sont reliés à la surface de jeu (*COURTS*) et à la saison (*SEASON*), ce qui 
introduit des dimensions d'analyse contextuelles 





**Point sur le label NATION** : 
Ce label sera central dans notre analyse explicative. En effet, nous chercherons à établir 
une éventuelle relation entre les performances des joueurs et leur pays de provenance. 
Ce label contient des attributs clés tels que le nombre de licences de tennis, le PIB du 
pays, les audiences des compétitions et le nombre d'heures d'EPS. Ces informations 
nous permettront de mieux comprendre comment le contexte national peut influencer 
les performances sur le circuit.

"""

st.markdown(texte)

st.markdown("## Graphe")

image_path = "Graphe.png"

# Affichage d'une image locale avec Streamlit
st.image(image_path, use_column_width=True)



