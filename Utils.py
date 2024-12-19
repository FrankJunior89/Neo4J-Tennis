import json
import streamlit as st
import pandas as pd
from  Database import Database
import matplotlib.pyplot as plt
import altair as alt


def load_credentials(file_path):

    with open(file_path, 'r') as file:
        credentials = json.load(file)

    return credentials

credentials = load_credentials('.gitignore/credentials.json')

URL = credentials['NEO4J_URI']
USER = credentials['NEO4J_USERNAME']
PASSWORD = credentials['NEO4J_PASSWORD']


db = Database(URL,USER,PASSWORD)


players = pd.read_csv('data/competitors.csv')
coachs = pd.read_csv('data/coachs.csv',sep=";")
nations = pd.read_csv('data/nations.csv')


def general():


    with open('data/general.json', 'r',encoding='utf-8') as f:
        data = json.load(f)

    labels = [label['label'] for label in data['labels']]

    selected_label = st.selectbox("Select a label", labels)

    selected_label_data = next(label for label in data['labels'] if label['label'] == selected_label)

    st.write(f"### {selected_label} Details")

    st.write("#### Description")

    st.write(selected_label_data['description'])

    st.write("#### Attributes:")
    st.write(selected_label_data['attributes'])

    st.write("#### Relationships:")
    for relationship in selected_label_data['relationships']:
        st.write(f"- **{relationship['type']}** --> {relationship['target']}")




def perfomance_globale_joueurs():
    st.header("Performance Globale des Joueurs", divider=True)
    
    view_option = st.radio("perf_globale vue", ("Vue générale", "Vue personnalisée"),label_visibility="hidden")

    if view_option == "Vue générale":

        st.write("Cette requête calcule le pourcentage de victoires des joueurs pour une ou plusieurs années spécifiées par l'utilisateur en se limitant aux joueurs ayant disputé plus d’un nombre minimal de matchs également défini par l’utilisateur. Elle retourne le nom des joueurs, le nombre total de matchs joués, le nombre total de victoires, et le pourcentage de victoires, triés par ordre décroissant de pourcentage de victoires.")

        years = st.multiselect("Year :",[2022,2023,2024],default=[2024])

        min_matches = st.number_input("Nombre matchs (min):", min_value=0, value=100, step=10)
        
        st.markdown("#### Requête")

        requete = f"""
            MATCH (c:COMPETITOR)-[r:PLAYED]->(g:GAME)-[:HAPPENED_IN]->(s:SEASON)
            WHERE s.year IN {years}
            WITH c, 
                COUNT(g) AS total_matches, 
                SUM(CASE WHEN g.winner_id = c.id THEN 1 ELSE 0 END) AS total_wins
            WHERE total_matches > {min_matches}
            WITH c.name AS player_name, 
                total_matches, 
                total_wins, 
                ROUND((TOFLOAT(total_wins) / total_matches) * 100, 2) AS win_percentage
            RETURN player_name, 
                total_matches, 
                total_wins, 
                win_percentage
            ORDER BY win_percentage DESC
            LIMIT 10
        """
        st.markdown(f"```cypher\n{requete}\n```")


        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            players_df =pd.DataFrame(result)

            st.dataframe(players_df)
            

    else:

        st.write("Cette requête calcule le nombre total de matchs et de victoires ainsi que le pourcentage de victoires pour le joueur sélectionné, uniquement pour les années données par l'utilisateur.")
        
        years = st.multiselect("Year  :",[2022,2023,2024],default=[2024])

        player_option = st.selectbox("Choix du joueur", sorted(players['name']), index=sorted(players['name']).index("Alcaraz Carlos")) 

        if player_option != None:
            
            st.markdown("#### Requête")

            requete = f"""
                MATCH (c:COMPETITOR)-[r:PLAYED]->(g:GAME)-[:HAPPENED_IN]->(s:SEASON)
                WHERE s.year IN {years} AND c.name = '{player_option}'
                WITH c, 
                    COUNT(g) AS total_matches, 
                    SUM(CASE WHEN g.winner_id = c.id THEN 1 ELSE 0 END) AS total_wins
                WITH c.name AS player_name, 
                    total_matches, 
                    total_wins, 
                    ROUND((TOFLOAT(total_wins) / total_matches) * 100, 2) AS win_percentage
                RETURN player_name, 
                    total_matches, 
                    total_wins, 
                    win_percentage
                ORDER BY win_percentage DESC
            """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            players_df =pd.DataFrame(result)

            st.dataframe(players_df)
   

def meilleur_ami():
    st.header("Mon meilleur Ami", divider=True)

    st.write("Cette requête affiche le duo avec lequel un joueur donné (entré par l'utilisateur) a remporté le plus de matchs. Elle calcule le nombre total de matchs joués avec ce duo, ainsi que le nombre de victoires. Le duo avec le plus de victoires est affiché en premier.")

    st.markdown("#### Requête")

    player_option = st.selectbox("Choix du joueur", sorted(players['name']), index=sorted(players['name']).index("Alcaraz Carlos"))

    if player_option != None:
    
        requete = """
        MATCH (p:COMPETITOR {name: '"""+ str(player_option) + """'})-[:MEMBER]->(d:DUO)-[:PLAYED]->(g:GAME)
        WITH p, d, g,
        CASE 
            WHEN g.winner_id = d.competitor_id THEN 1 
            ELSE 0 
        END AS win
        WITH p, d, 
        COUNT(g) AS total_games, 
        SUM(win) AS total_wins
        RETURN p.name AS player_name,
        d.competitor_name AS duo_name,
        total_games,
        total_wins
        ORDER BY total_wins DESC
        LIMIT 1;
        """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            #st.text('Exécution de la requête...')
            result = db.execute_query(requete)

            if len(result) > 0:
                ami = result[0]['duo_name'].split('/')[1]
                nb_games = result[0]['total_games']
                nb_wins = result[0]['total_wins']

                st.text(f"Player's best duo: {ami}\nTotal games played: {nb_games}\nTotal wins: {nb_wins}")
            else:
                st.text('Pas de duos enregistré pour ce joueur')

def classement_coachs():
    st.header("Classement des Coachs", divider=True)

    view_option = st.radio("coach vue", ("Vue générale", "Vue personnalisée"),label_visibility="hidden")

    if view_option == "Vue générale":

        st.write("Cette requête donne la liste des 10 entraîneurs ayant le meilleur taux de victoires moyen pour les matchs de leurs joueurs. Elle calcule le taux de victoires pour chaque entraîneur en fonction des matchs gagnés par leurs joueurs, et trie les entraîneurs par leur taux de victoires moyen, du plus élevé au plus bas.")

        st.markdown("#### Requête")

        requete = """
                    MATCH (c:COACH)-[:COACHS]->(p:COMPETITOR)-[:PLAYED]->(g:GAME)
            WHERE g.winner_id IS NOT NULL
            WITH c, p, g,
                CASE 
                    WHEN g.winner_id = p.id THEN 1 
                    ELSE 0 
                END AS win
            WITH c, p, COUNT(g) AS total_games, SUM(win) AS total_wins
            WITH c, 
                AVG(toFloat(total_wins) / total_games) AS avg_win_rate
            RETURN c.`Featured Coaches` AS coach_name, avg_win_rate
            ORDER BY avg_win_rate DESC
            LIMIT 10;
        """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
                #st.text('Exécution de la requête...')
                result = db.execute_query(requete)

                coachs_df = pd.DataFrame(result)

                st.dataframe(coachs_df)

    else:

        st.write("Cette requête donne le taux de victoires moyen et le nombre total de matchs joués par les joueurs d'un entraîneur sélectionné par l’utilisateur. Elle calcule le taux de victoires moyen de l'entraîneur basé sur les matchs gagnés par ses joueurs puis trie les résultats en fonction du taux de victoires moyen.")

        coach_option = st.selectbox("Choix du Coach", coachs['coach_name'])

        if coach_option != None:
            st.markdown("#### Requête")

            requete = """
                        MATCH (c:COACH {`Featured Coaches`: '""" + coach_option +"""'})-[:COACHS]->(p:COMPETITOR)-[:PLAYED]->(g:GAME)
                WHERE g.winner_id IS NOT NULL
                WITH c, p, g,
                    CASE 
                        WHEN g.winner_id = p.id THEN 1 
                        ELSE 0 
                    END AS win
                WITH c, p, COUNT(g) AS total_games, SUM(win) AS total_wins
                WITH c,total_games,
                    AVG(toFloat(total_wins) / total_games) AS avg_win_rate
                RETURN c.`Featured Coaches` AS coach_name, avg_win_rate , total_games
                ORDER BY avg_win_rate DESC
                LIMIT 10;
            """
            st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
                #st.text('Exécution de la requête...')
                result = db.execute_query(requete)

                if len(result) > 0:
                     name = result[0]['coach_name']
                     wins = result[0]['avg_win_rate']
                     nb_games = result[0]['total_games']
                     
                     st.text(f"Coach: {name}\nTotal games : {nb_games}\nWin_Rate: {wins}")
                
                else: 
                     st.text('Pas de matchs/joueurs renseignés ')

def compet_favoris_par_nation():
    st.header("Competitions favorites des Nations", divider=True)

    st.write ("Cette requête donne les 5 compétitions où la nation sélectionnée a remporté le plus de victoires. Elle affiche le nom de la compétition et le nombre de victoires.")

    nation_option = st.selectbox("Nation", nations['country'])

    if nation_option != None:
         
            st.markdown("#### Requête")

            requete = """
                MATCH (g:GAME)
                WITH 
                    CASE 
                        WHEN g.winner_id = g.competitor1_id THEN g.competitor1_country
                        WHEN g.winner_id = g.competitor2_id THEN g.competitor2_country
                    END AS winner_country,
                    g.`competition_name` AS competition_name,
                    COUNT(g) AS wins
                WHERE winner_country = '""" + nation_option + """'
                RETURN competition_name, wins
                ORDER BY wins DESC
                LIMIT 5;
            """
            st.markdown(f"```cypher\n{requete}\n```")

            if st.button("Exécuter la requête"):
                #st.text('Exécution de la requête...')
                result = db.execute_query(requete)

                if len(result) > 0:
                    nations_df = pd.DataFrame(result)
                    st.dataframe(nations_df)
                
                else: 
                     st.text('Pas de joueurs renseignés')  


def men_vs_women():
    st.header("Men vs Women", divider=True)

    st.write("Cette requête calcule la moyenne de différentes statistiques de jeu (comme les aces, les doubles fautes, les points gagnés au premier et au second service, les jeux gagnés et les points gagnés) pour les joueurs, en séparant les résultats par sexe. Elle retourne ces moyennes pour chaque sexe (hommes et femmes) et trie les résultats par sexe.")

    st.markdown("#### Requête")

    requete ="""
                     MATCH (p:COMPETITOR)-[:PLAYED]->(g:GAME)
                    WHERE g.statistics IS NOT NULL
                    WITH p.gender AS gender, apoc.convert.fromJsonMap(g.statistics) AS stats
                    WITH gender, stats.totals.competitors[0].statistics AS metrics
                    RETURN gender,
                        AVG(toFloat(metrics.aces)) AS avg_aces,
                        AVG(toFloat(metrics.double_faults)) AS avg_double_faults,
                        AVG(toFloat(metrics.first_serve_points_won)) AS avg_first_serve_points_won,
                        AVG(toFloat(metrics.second_serve_points_won)) AS avg_second_serve_points_won,
                        AVG(toFloat(metrics.games_won)) AS avg_games_won,
                        AVG(toFloat(metrics.points_won)) AS avg_points_won
                    ORDER BY gender;
            """
    st.markdown(f"```cypher\n{requete}\n```")

    if st.button("Exécuter la requête"):
        result = db.execute_query(requete)
        
        df = pd.DataFrame(result)

        st.dataframe(df.set_index('gender').T)
     
def service_and_meteo():

    st.header("Influence de la Météo sur le Service", divider=True)
    
    st.write("Cette requête donne la moyenne des statistiques de jeu (comme les aces, les breakpoints gagnés, les fautes doubles, etc.) pour les compétitions ayant eu lieu lorsque la vitesse du vent est inférieure à une valeur maximale, l'humidité est inférieure à une autre valeur maximale et la radiation solaire est supérieure à une valeur minimale (ces valeurs étant fournies par l'utilisateur).")

    windspeed_threshold = st.number_input("Windspeed (max)", min_value=0.0, value=15.0, step=1.0)
    humidity_threshold = st.number_input("Humidity (max):", min_value=0.0, max_value=100.0, value=60.0, step=1.0)
    solarradiation_threshold = st.number_input("Solar Radiation (max):", min_value=0.0, value=200.0, step=10.0)

    st.markdown("#### Requête")

    requete = f"""
                MATCH (g:GAME), (w:WEATHER)
                WHERE g.city_name = w.city 
                AND date(g.start_time) = date(w.datetime)
                AND w.windspeed < {windspeed_threshold}
                AND w.humidity < {humidity_threshold}
                AND w.solarradiation > {solarradiation_threshold}
                WITH apoc.convert.fromJsonMap(g.statistics) AS stats
                WITH stats.totals.competitors[0].statistics AS metric1, 
                    stats.totals.competitors[1].statistics AS metric2
                WHERE metric1.aces IS NOT NULL AND metric2.aces IS NOT NULL
                WITH 
                    AVG(toFloat((metric1.aces + metric2.aces) / 2)) AS avg_aces,
                    AVG(toFloat((metric1.breakpoints_won + metric2.breakpoints_won) / 2)) AS avg_breakpoints_won,
                    AVG(toFloat((metric1.double_faults + metric2.double_faults) / 2)) AS avg_double_faults,
                    AVG(toFloat((metric1.first_serve_points_won + metric2.first_serve_points_won) / 2)) AS avg_first_serve_points_won,
                    AVG(toFloat((metric1.first_serve_successful + metric2.first_serve_successful) / 2)) AS avg_first_serve_successful,
                    AVG(toFloat((metric1.games_won + metric2.games_won) / 2)) AS avg_games_won,
                    AVG(toFloat((metric1.points_won + metric2.points_won) / 2)) AS avg_points_won,
                    AVG(toFloat((metric1.service_games_won + metric2.service_games_won) / 2)) AS avg_service_games_won,
                    AVG(toFloat((metric1.service_points_won + metric2.service_points_won) / 2)) AS avg_service_points_won
                RETURN 
                    avg_aces,
                    avg_breakpoints_won,
                    avg_double_faults,
                    avg_first_serve_points_won,
                    avg_first_serve_successful,
                    avg_games_won,
                    avg_points_won,
                    avg_service_games_won,
                    avg_service_points_won

    """

    st.markdown(f"```cypher\n{requete}\n```")

    if st.button("Exécuter la requête"):
        result = db.execute_query(requete)
        
        #st.dataframe(result)
        st.write(f"#### Conditions")
        st.text(f"Windspeed < {windspeed_threshold}\nHumidity < {humidity_threshold}\nSolar Radiation < {solarradiation_threshold}\n\n\n")
        st.write(f"#### Service Metrics")
        st.write(f"**Average Aces:** {result[0]['avg_aces']:.2f}")
        st.write(f"**Average Breakpoints Won:** {result[0]['avg_breakpoints_won']:.2f}")
        st.write(f"**Average Double Faults:** {result[0]['avg_double_faults']:.2f}")
        st.write(f"**Average First Serve Points Won:** {result[0]['avg_first_serve_points_won']:.2f}")
        st.write(f"**Average First Serve Successful:** {result[0]['avg_first_serve_successful']:.2f}")
        st.write(f"**Average Games Won:** {result[0]['avg_games_won']:.2f}")
        st.write(f"**Average Points Won:** {result[0]['avg_points_won']:.2f}")
        st.write(f"**Average Service Games Won:** {result[0]['avg_service_games_won']:.2f}")
        st.write(f"**Average Service Points Won:** {result[0]['avg_service_points_won']:.2f}")

def perf_tournoi_majeurs():
    st.header("Performance en Tournois Majeurs", divider=True)

    view_option = st.radio("perf_tournoi_majeurs vue", ("Vue générale", "Vue personnalisée"),label_visibility="hidden")

    if view_option == "Vue générale":

        st.write("Cette requête calcule pour chaque joueur : le pourcentage de victoires dans les compétitions de type 'Grand Slam' durant les années choisies par l'utilisateur. Elle affiche le nombre total de matchs joués, le nombre de victoires et le pourcentage de victoires trié par pourcentage décroissant.")

        years = st.multiselect("Year :",[2022,2023,2024],default=[2024])

        
        st.markdown("#### Requête")

        requete = f"""
                MATCH (c:COMPETITOR)-[r:PLAYED]->(g:GAME)-[:HAPPENED_IN]->(s:SEASON)
                MATCH (g)-[:IS_A_GAME_OF]->(comp:COMPETITION)
                WHERE s.year IN {years}
                AND comp.level = "grand_slam"
                WITH c, 
                    COUNT(g) AS total_matches, 
                    SUM(CASE WHEN g.winner_id = c.id THEN 1 ELSE 0 END) AS total_wins
                WITH c.name AS player_name, 
                    total_matches, 
                    total_wins, 
                    ROUND((TOFLOAT(total_wins) / total_matches) * 100, 2) AS win_percentage
                RETURN player_name, 
                    total_matches, 
                    total_wins, 
                    win_percentage
                ORDER BY win_percentage DESC, total_wins DESC
                LIMIT 10
        """
        st.markdown(f"```cypher\n{requete}\n```")


        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            players_df =pd.DataFrame(result)

            st.dataframe(players_df)
            

    else:

        st.write("Cette requête calcule pour un joueur choisi par l'utilisateur : le pourcentage de victoires dans les compétitions de type 'Grand Slam' pour chaque année sélectionnée. Elle affiche le nombre total de matchs joués, le nombre de victoires et le pourcentage de victoires trié par année et par pourcentage de victoires décroissant.")
        
        years = st.multiselect("Year   ",[2022,2023,2024],default=[2024])

        player_option = st.selectbox("Choix du joueur", sorted(players['name']), index=sorted(players['name']).index("Alcaraz Carlos"))

        if player_option != None:
            
            st.markdown("#### Requête")

            requete = f"""
                    MATCH (c:COMPETITOR)-[r:PLAYED]->(g:GAME)-[:HAPPENED_IN]->(s:SEASON)
                    MATCH (g)-[:IS_A_GAME_OF]->(comp:COMPETITION)
                    WHERE s.year IN {years}
                    AND comp.level = "grand_slam"
                    AND c.name = '{player_option}'
                    WITH s.year AS year,
                    COLLECT(DISTINCT comp.name) AS competition_names,
                    COUNT(g) AS total_matches,
                    SUM(CASE WHEN g.winner_id = c.id THEN 1 ELSE 0 END) AS total_wins
                    WITH year,
                    apoc.text.join(competition_names, '\n') AS competition_names,
                    total_matches,
                    total_wins,
                    ROUND((TOFLOAT(total_wins) / total_matches) * 100, 2) AS win_percentage
                    RETURN year,
                    competition_names,
                    total_matches,
                    total_wins,
                    win_percentage
                    ORDER BY year DESC, win_percentage DESC
            """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            players_df =pd.DataFrame(result)

            st.dataframe(players_df)

def perf_by_age():
    st.header("Performance par Age", divider=True)

    view_option = st.radio("perf_by_age vue", ("Vue générale", "Vue personnalisée"),label_visibility="hidden")

    if view_option == "Vue générale":

        st.write("Cette requête affiche les 10 premiers joueurs, triés par âge au moment de leur passage professionnel en calculant l'écart entre l'année de leur passage professionnel (pro_year) et leur année de naissance (birth_year). Elle retourne le nom du joueur, l'année de leur passage professionnel, leur année de naissance et leur âge au moment de leur passage professionnel.")
        
        st.markdown("#### Requête")

        requete = """
                MATCH (c:COMPETITOR)
                WHERE c.pro_year IS NOT NULL AND c.date_of_birth IS NOT NULL
                WITH c,
                TOINTEGER(c.pro_year) AS pro_year,
                TOINTEGER(SUBSTRING(toString(c.date_of_birth), 0, 4)) AS birth_year,
                c.name AS player_name
                WITH player_name,
                toString(pro_year) AS pro_year,       
                toString(birth_year) AS birth_year,
                (pro_year - birth_year) AS age_at_pro
                RETURN player_name,
                pro_year,
                birth_year,
                age_at_pro
                ORDER BY age_at_pro ASC
                LIMIT 10
            """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            players_df =pd.DataFrame(result)

            st.dataframe(players_df)




    else:
        st.write("Cette requête affiche les informations pour un joueur spécifique dont le nom est fourni par l'utilisateur. Elle calcule l'âge du joueur au moment de son passage professionnel en fonction de son année de naissance et de son année de passage professionnel. Elle retourne le nom du joueur, l'année de son passage professionnel, son année de naissance et son âge au moment de son passage professionnel.")

        player_option = st.selectbox("Choix du joueur", sorted(players['name']), index=sorted(players['name']).index("Alcaraz Carlos"))

        if player_option != None:


            st.markdown("#### Requête")

            requete = f"""
                    MATCH (c:COMPETITOR)
                    WHERE c.name = '{player_option}'
                    AND c.pro_year IS NOT NULL 
                    AND c.date_of_birth IS NOT NULL
                    WITH c, 
                        TOINTEGER(c.pro_year) AS pro_year, 
                        TOINTEGER(SUBSTRING(toString(c.date_of_birth), 0, 4)) AS birth_year
                    WITH c.name AS player_name, 
                        toString(pro_year) AS pro_year,       
                        toString(birth_year) AS birth_year,
                        (pro_year - birth_year) AS age_at_pro
                    RETURN player_name, 
                        pro_year, 
                        birth_year, 
                        age_at_pro
                """
            st.markdown(f"```cypher\n{requete}\n```")

            if st.button("Exécuter la requête"):
                result = db.execute_query(requete)

                players_df =pd.DataFrame(result)

                st.dataframe(players_df)

def evolution_age():
    st.header("Performance en Fonction de l'age", divider=True)

    st.write("Cette requête affiche les statistiques de matchs pour un joueur spécifique dont le nom est fourni par l'utilisateur, pour chaque année de saison. Elle calcule le nombre total de matchs joués, le nombre de victoires, le pourcentage de victoires, ainsi que l'âge du joueur à chaque année de saison. Les résultats sont triés par année et par âge du joueur.")

    player_option = st.selectbox("Choix du joueur", sorted(players['name']), index=sorted(players['name']).index("Alcaraz Carlos"))

    if player_option != None:


            st.markdown("#### Requête")

            requete = f"""
                        MATCH (c:COMPETITOR)-[r:PLAYED]->(g:GAME)-[:HAPPENED_IN]->(s:SEASON)
                        WHERE c.name = '{player_option}'
                        WITH c, 
                            COUNT(g) AS total_matches, 
                            SUM(CASE WHEN g.winner_id = c.id THEN 1 ELSE 0 END) AS total_wins,
                            c.date_of_birth AS dob, 
                            s.year AS year
                        WITH year, 
                            total_matches, 
                            total_wins, 
                            ROUND((TOFLOAT(total_wins) / total_matches) * 100, 2) AS win_percentage,
                            (year - TOINTEGER(SUBSTRING(toString(dob), 0, 4))) AS age
                        RETURN year, 
                            age, 
                            total_matches, 
                            total_wins, 
                            win_percentage
                        ORDER BY year, age
                """
            st.markdown(f"```cypher\n{requete}\n```")

            if st.button("Exécuter la requête"):
                result = db.execute_query(requete)
                
                players_df =pd.DataFrame(result)
                # st.dataframe(players_df)
                players_df['age'] = players_df['age'].astype(int)

                # Transformation des données pour Altair
                data_melted = players_df.melt(id_vars=["age"], 
                                            value_vars=["total_wins", "total_matches"], 
                                            var_name="Metric", 
                                            value_name="Count")

                # Création du graphique Altair
                chart = alt.Chart(data_melted).mark_bar().encode(
                    x=alt.X("age:O", title="Age"),  # Axe X : les années
                    y=alt.Y("Count:Q", title="Count"),  # Axe Y : les valeurs (correctif ici)
                    color=alt.Color("Metric:N", title="Metric"),  # Couleurs pour différencier les métriques
                    xOffset=alt.XOffset("Metric:N", sort=["total_wins", "total_matches"])  # Décalage horizontal pour afficher côte à côte
                ).properties(
                    width=600,
                    height=400,
                    title="Comparison of Wins and Matches"
                )
                # Affichage dans Streamlit
                st.altair_chart(chart, use_container_width=True)

                #st.dataframe(players_df)

                # st.bar_chart(players_df, x="year", y="total_wins")

def perf_by_ranking():
    st.header("Performance en Fonction du ranking", divider=True)

    view_option = st.radio("perf_by_ranking vue", ("Vue générale", "Vue personnalisée"),label_visibility="hidden")

    if view_option == "Vue générale":
        st.write("Cette requête affiche les statistiques de performance pour un joueur lorsqu'il est considéré comme le favori dans un match, en fonction de son classement en simple. Elle calcule le nombre total de matchs joués en tant que favori, le nombre de victoires en tant que favori et le pourcentage de victoires. Les résultats sont triés par pourcentage de victoires, du plus élevé au plus bas.")

        st.markdown("#### Requête")

        requete = """
                    MATCH (p1:COMPETITOR)-[r1:PLAYED]->(g:GAME)<-[r2:PLAYED]-(p2:COMPETITOR)
                    WHERE p1.highest_singles_ranking IS NOT NULL
                    AND p2.highest_singles_ranking IS NOT NULL
                    AND p1.highest_singles_ranking < p2.highest_singles_ranking
                    WITH p1,
                    p2,
                    g,
                    r1,
                    p1.highest_singles_ranking AS ranking_favorite,
                    p2.highest_singles_ranking AS ranking_underdog,
                    CASE WHEN g.winner_id = p1.id THEN 1 ELSE 0 END AS win_as_favorite
                    WITH p1.name AS player_name,
                    COUNT(g) AS total_matches_as_favorite,
                    SUM(win_as_favorite) AS wins_as_favorite,
                    ROUND(TOFLOAT(SUM(win_as_favorite)) / COUNT(g) * 100, 2) AS win_percentage_as_favorite
                    WHERE total_matches_as_favorite > 0
                    RETURN player_name,
                    total_matches_as_favorite,
                    wins_as_favorite,
                    win_percentage_as_favorite
                    ORDER BY win_percentage_as_favorite DESC, wins_as_favorite DESC
            """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            results_df =pd.DataFrame(result)

            st.dataframe(results_df)

    else:
        st.write("Cette requête affiche les statistiques de performance pour un joueur donné lorsqu'il est considéré comme le favori dans un match, en fonction de son classement en simple. Elle calcule le nombre total de matchs joués en tant que favori, le nombre de victoires en tant que favori et le pourcentage de victoires. Les résultats ne sont affichés que si le joueur a joué des matchs en tant que favori.")

        player_option = st.selectbox("Choix du joueur", sorted(players['name']), index=sorted(players['name']).index("Alcaraz Carlos"))

        if player_option != None:
                    requete = f"""
                        MATCH (p1:COMPETITOR)-[r1:PLAYED]->(g:GAME)<-[r2:PLAYED]-(p2:COMPETITOR)
                        WHERE p1.name = '{player_option}'
                        AND p1.highest_singles_ranking IS NOT NULL
                        AND p2.highest_singles_ranking IS NOT NULL
                        AND p1.highest_singles_ranking < p2.highest_singles_ranking
                        WITH p1, 
                            p2, 
                            g, 
                            r1, 
                            p1.highest_singles_ranking AS ranking_favorite, 
                            p2.highest_singles_ranking AS ranking_underdog,
                            CASE WHEN g.winner_id = p1.id THEN 1 ELSE 0 END AS win_as_favorite
                        WITH p1.name AS player_name,
                            COUNT(g) AS total_matches_as_favorite,
                            SUM(win_as_favorite) AS wins_as_favorite,
                            ROUND(TOFLOAT(SUM(win_as_favorite)) / COUNT(g) * 100, 2) AS win_percentage_as_favorite
                        WHERE total_matches_as_favorite > 0
                        RETURN player_name,
                            total_matches_as_favorite,
                            wins_as_favorite,
                            win_percentage_as_favorite
            """
                    st.markdown(f"```cypher\n{requete}\n```")

                    if st.button("Exécuter la requête"):
                        result = db.execute_query(requete)

                        results_df =pd.DataFrame(result)

                        st.dataframe(results_df)

def meilleur_ennemi():
    
    st.header("Meilleurs Ennemis", divider=True)

    st.write("Cette requête affiche les statistiques des 5 principaux rivaux contre lesquels un joueur donné (entré par l'utilisateur) a perdu le plus de matchs. Elle calcule le nombre total de matchs joués contre chaque rival, le nombre de défaites et le pourcentage de défaites contre chaque rival. Les résultats sont triés par pourcentage de défaites et nombre de matchs joués.")

    st.markdown("#### Requête")

    player_option = st.selectbox("Choix du joueur", sorted(players['name']), index=sorted(players['name']).index("Alcaraz Carlos"))

    if player_option != None:
    
        requete = """
                MATCH (p1:COMPETITOR {name: '""" + player_option + """'})-[r1:PLAYED]->(g:GAME)<-[r2:PLAYED]-(p2:COMPETITOR)
                WHERE g.winner_id = p2.id
                WITH p1, p2, COUNT(g) AS losses
                MATCH (p1)-[:PLAYED]->(common_game:GAME)<-[:PLAYED]-(p2)
                WITH p1, p2, losses, COUNT(common_game) AS total_matches_against
                WITH p1.name AS player_name, 
                    p2.name AS rival_name,
                    total_matches_against, 
                    losses, 
                    ROUND(TOFLOAT(losses) / total_matches_against * 100, 2) AS loss_percentage
                RETURN player_name, 
                    rival_name, 
                    total_matches_against, 
                    losses, 
                    loss_percentage
                ORDER BY loss_percentage DESC, total_matches_against DESC
                LIMIT 5
        """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            #st.text('Exécution de la requête...')
            result = db.execute_query(requete)

            results_df =pd.DataFrame(result)

            st.dataframe(results_df)

def analyse_blessures():
     
     st.header("Blessures", divider=True)
     
     view_option = st.radio("analysis_blessures vue", ("Vue générale", "Vue personnalisée"),label_visibility="hidden")
     
     if view_option == "Vue générale":

        st.write("Cette requête donne la répartition des types de blessures des compétiteurs en affichant chaque type de blessure et le pourcentage qu'il représente par rapport au nombre total de blessures. Les types de blessures sont triés par pourcentage, du plus élevé au plus bas.")

        st.markdown("#### Requête")

        requete = """
                                    MATCH (p:COMPETITOR)-[i:INJURED]->(c:COMPETITION)
                WITH i.Injury AS injury_type, COUNT(i) AS injury_count
                WITH COLLECT(injury_type) AS injury_types, COLLECT(injury_count) AS injury_counts
                WITH REDUCE(total_injuries = 0, count IN injury_counts | total_injuries + count) AS total_injuries,
                injury_types, injury_counts
                UNWIND RANGE(0, SIZE(injury_types) - 1) AS idx
                WITH injury_types[idx] AS injury_type, injury_counts[idx] AS injury_count, total_injuries
                RETURN injury_type,
                ROUND(TOFLOAT(injury_count) / total_injuries * 100, 2) AS injury_percentage
                ORDER BY injury_percentage DESC
            """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            results_df =pd.DataFrame(result)

            st.dataframe(results_df)

     else:
        st.write("Cette requête donne les types de blessures subies par le joueur sélectionné ainsi que le nombre total de blessures pour chaque année. Les résultats sont triés par année de manière décroissante.")

        player_option = st.selectbox("Choix du joueur", sorted(players['name']), index=sorted(players['name']).index("Alcaraz Carlos"))

        if player_option != None:
                    requete = f"""
                MATCH (p:COMPETITOR)-[inj:INJURED]->(c:COMPETITION)
                WHERE p.name = '{player_option}' AND inj.Injury IS NOT NULL
                WITH p.name AS player_name,
                    substring(inj.`Injury Date`, 6, 4) AS injury_year, 
                    COLLECT(inj.Injury) AS injury_types, 
                    COUNT(inj) AS total_injuries 
                RETURN player_name,
                    injury_year,
                    injury_types,
                    total_injuries
                ORDER BY injury_year DESC
            """
                    st.markdown(f"```cypher\n{requete}\n```")

                    if st.button("Exécuter la requête"):
                        result = db.execute_query(requete)

                        results_df =pd.DataFrame(result)

                        st.dataframe(results_df)

def stats_finales():
     
     st.header("Statistiques des Finales", divider=True)

     view_option = st.radio("perf_by_age vue", ("Vue générale", "Vue personnalisée"),label_visibility="hidden")

     if view_option == "Vue générale":

        st.write("Cette requête donne le nombre de finales jouées, gagnées et perdues pour chaque joueur ainsi que leur pourcentage de victoires en finale. Les résultats sont triés par nombre de finales gagnées de manière décroissante.")
        
        st.markdown("#### Requête")

        requete = """
                MATCH (p:COMPETITOR)-[:PLAYED]->(g:GAME)
                WHERE apoc.convert.fromJsonMap(g.sport_event_context).round.name = 'final'
                WITH p, 
                    COUNT(g) AS nb_finales,
                    COUNT(CASE WHEN g.winner_id = p.id THEN 1 END) AS finales_won,
                    COUNT(CASE WHEN g.loser_id = p.id THEN 1 END) AS finales_lost
                WITH p, nb_finales, finales_won, finales_lost, 
                    (finales_won * 1.0 / nb_finales) AS avg
                RETURN p.name AS player, nb_finales, finales_won, finales_lost, avg
                ORDER BY finales_won DESC, nb_finales DESC
            """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            players_df =pd.DataFrame(result)

            st.dataframe(players_df)

     else:
          st.write("Cette requête donne le nombre de finales jouées, gagnées et perdues par le joueur sélectionné ainsi que le pourcentage de victoires en finale. Les résultats sont triés par nombre de finales gagnées, du plus grand au plus petit.")
          player_option = st.selectbox("Choix du joueur", sorted(players['name']), index=sorted(players['name']).index("Alcaraz Carlos"))

          if player_option != None:
            
                requete = """
                        MATCH (p:COMPETITOR {name: '""" + player_option + """'})-[:PLAYED]->(g:GAME)
                WHERE apoc.convert.fromJsonMap(g.sport_event_context).round.name = 'final'
                WITH p, 
                    COUNT(g) AS nb_finales,
                    COUNT(CASE WHEN g.winner_id = p.id THEN 1 END) AS finales_won,
                    COUNT(CASE WHEN g.loser_id = p.id THEN 1 END) AS finales_lost
                WITH p, nb_finales, finales_won, finales_lost, 
                    (finales_won * 1.0 / nb_finales) AS avg
                RETURN p.name AS player, nb_finales, finales_won, finales_lost, avg
                ORDER BY finales_won DESC
                """
                st.markdown(f"```cypher\n{requete}\n```")

                if st.button("Exécuter la requête"):
                    #st.text('Exécution de la requête...')
                    result = db.execute_query(requete)

                    results_df =pd.DataFrame(result)

                    st.dataframe(results_df)

def sponsoring():
     
     st.header("Shoes Sponsoring", divider=True)

     st.write("Cette requête donne le nombre d'athlètes qui jouent avec une marque de raquette spécifique. Elle liste les marques de raquettes et le nombre d'athlètes associés à chaque marque, trié par le nombre d'athlètes, de la marque la plus populaire à la moins populaire.")

     st.markdown("#### Requête")

     requete = """
                            MATCH (c:COMPETITOR)
                WHERE c.Racket IS NOT NULL 
                RETURN c.Racket AS rack_brand, COUNT(c) AS number_of_athletes
                ORDER BY number_of_athletes DESC;
            """
     st.markdown(f"```cypher\n{requete}\n```")

     if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            result_df =pd.DataFrame(result)

            st.dataframe(result_df.head())
     

def perf_by_surface():
     
     st.header("Performance par Surface de Jeu", divider=True)

     view_option = st.radio("perf_globale vue", ("Vue générale", "Vue personnalisée"),label_visibility="hidden")

     if view_option == "Vue générale":

        st.write("Cette requête calcule les statistiques moyennes de performance des joueurs en fonction du type de surface (par exemple, gazon, terre battue) des compétitions. Les statistiques incluent le nombre moyen d'aces, de doubles fautes, les points gagnés sur le premier et le second service, les jeux gagnés, et les points gagnés. Les résultats sont triés par type de surface.")
        
        st.markdown("#### Requête")

        requete = """
                            MATCH (p:COMPETITOR)-[:PLAYED]->(g:GAME)-[:HAPPENED_IN]->(s:SEASON)-[:IS_EDITION_OF]->(c:COMPETITION)
                WHERE g.statistics IS NOT NULL AND c.Surface IS NOT NULL
                WITH c.Surface AS surface, apoc.convert.fromJsonMap(g.statistics) AS stats
                WITH surface, stats.totals.competitors[0].statistics AS metrics
                RETURN surface,
                ROUND(AVG(toFloat(metrics.aces)), 2) AS avg_aces,
                ROUND(AVG(toFloat(metrics.double_faults)), 2) AS avg_double_faults,
                ROUND(AVG(toFloat(metrics.first_serve_points_won)), 2) AS avg_first_serve_points_won,
                ROUND(AVG(toFloat(metrics.second_serve_points_won)), 2) AS avg_second_serve_points_won,
                ROUND(AVG(toFloat(metrics.games_won)), 2) AS avg_games_won,
                ROUND(AVG(toFloat(metrics.points_won)), 2) AS avg_points_won
                ORDER BY surface
        """
        st.markdown(f"```cypher\n{requete}\n```")


        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            players_df =pd.DataFrame(result)

            st.dataframe(players_df)
            

     else:

        st.write("Cette requête calcule, pour un joueur choisi par l'utilisateur, les statistiques moyennes de performance en fonction des types de surface des compétitions. Elle inclut le pourcentage moyen de victoires, le nombre moyen d'aces, de doubles fautes, les points gagnés sur le premier et le second service, les jeux gagnés, et les points gagnés. Les résultats sont triés par type de surface.")

        player_option = st.selectbox("Choix du joueur", sorted(players['name']), index=sorted(players['name']).index("Alcaraz Carlos"))

        if player_option != None:
            
            st.markdown("#### Requête")

            requete = f"""
                    MATCH (p:COMPETITOR)-[:PLAYED]->(g:GAME)-[:HAPPENED_IN]->(s:SEASON)-[:IS_EDITION_OF]->(c:COMPETITION)
                    WHERE p.name = '{player_option}' AND g.statistics IS NOT NULL AND c.Surface IS NOT NULL
                    WITH c.Surface AS surface, 
                        apoc.convert.fromJsonMap(g.statistics) AS stats,
                        COUNT(g) AS total_matches,
                        SUM(CASE WHEN g.winner_id = p.id THEN 1 ELSE 0 END) AS total_wins
                    WITH surface, total_matches, total_wins, stats.totals.competitors[0].statistics AS metrics
                    RETURN surface,
                        ROUND(AVG(toFloat((total_wins * 1.0 / total_matches) * 100)), 2) AS win_percentage,
                        ROUND(AVG(toFloat(metrics.aces)), 2) AS avg_aces,
                        ROUND(AVG(toFloat(metrics.double_faults)), 2) AS avg_double_faults,
                        ROUND(AVG(toFloat(metrics.first_serve_points_won)), 2) AS avg_first_serve_points_won,
                        ROUND(AVG(toFloat(metrics.second_serve_points_won)), 2) AS avg_second_serve_points_won,
                        ROUND(AVG(toFloat(metrics.games_won)), 2) AS avg_games_won,
                        ROUND(AVG(toFloat(metrics.points_won)), 2) AS avg_points_won
                    ORDER BY surface;
            """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            players_df =pd.DataFrame(result)

            st.dataframe(players_df)

def nation_formation():
    st.header("Corrélation nb joueurs/licenciés", divider=True)
    
    view_option = st.radio("analysis_blessures vue", ("Vue générale", "Vue personnalisée"),label_visibility="hidden")

    # Sélection de la variable pour l'axe des abscisses
    x_axis_option = st.selectbox(
        "Choisir la variable pour l'axe des abscisses",
        ("heures EPS en primaire", "population en 2018", "licenciés en 2018")
    )

    column_mapping = {
            "heures EPS en primaire": "hours_of_sport",
            "population en 2018": "population",
            "licenciés en 2018": "licencies"
        }

    if view_option == "Vue générale":

        st.write("Cette requête donne des statistiques pour chaque pays, en fonction de la variable choisie par l'utilisateur (soit les heures EPS en primaire, la population en 2018 ou les licenciés en 2018). Elle inclut le nombre total de matchs, le nombre total de victoires, le nombre total de joueurs et le pourcentage de victoires, tout cela trié par le pourcentage de victoires décroissant.")

        st.markdown("#### Requête")

        x_axis_column = column_mapping[x_axis_option]

        requete = f"""
MATCH (c:COMPETITOR)-[r:PLAYED]->(g:GAME)-[:HAPPENED_IN]->(s:SEASON)
MATCH (n:NATION)
WHERE n.country_code2 = c.country_code
AND n.hours_of_sport IS NOT NULL
AND n.population_2018 IS NOT NULL
AND n.licensees_2018 IS NOT NULL
WITH c.country AS country, 
     n.hours_of_sport AS hours_of_sport,
     n.population_2018 AS population,
     n.licensees_2018 AS licencies,
     COUNT(g) AS total_matches, 
     SUM(CASE WHEN g.winner_id = c.id THEN 1 ELSE 0 END) AS total_wins, 
     COUNT(DISTINCT c.id) AS total_players
WITH country, 
     hours_of_sport,
     population,
     licencies,
     total_matches AS total_matches_by_country,
     total_wins AS total_wins_by_country,
     total_players AS total_players_by_country,
     ROUND((TOFLOAT(total_wins) / total_matches) * 100, 2) AS win_percentage_by_country
RETURN country, 
       hours_of_sport,
       population,
       licencies,
       total_matches_by_country,
       total_wins_by_country,
       total_players_by_country,
       win_percentage_by_country
ORDER BY win_percentage_by_country DESC
        """
        
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)
            results_df = pd.DataFrame(result)

            # Filtrage des données pour s'assurer que la variable choisie n'est pas nulle
            # Appliquer le filtrage sur le DataFrame après avoir récupéré les résultats
            results_df = results_df[results_df[x_axis_column].notnull()]

            # Vérifier si le DataFrame après filtrage n'est pas vide
            if results_df.empty:
                st.warning(f"Aucun résultat valide pour {x_axis_option}.")
            else:
                # Affichage du nuage de points avec étiquettes
                fig, ax = plt.subplots(figsize=(10, 6))

                # Tracé des points
                scatter = ax.scatter(
                    results_df[x_axis_column], 
                    results_df['total_players_by_country'], 
                    c='blue', 
                    label='Pays'
                )

                # Ajout des étiquettes pour chaque point
                for i, country in enumerate(results_df['country']):  # Supposons que la colonne 'country' contient les noms des pays
                    ax.annotate(
                        country, 
                        (results_df[x_axis_column].iloc[i], results_df['total_players_by_country'].iloc[i]),
                        textcoords="offset points",  # Décale le texte
                        xytext=(5, 5),  # Distance du texte par rapport au point
                        ha='left',  # Alignement horizontal
                        fontsize=8,  # Taille de la police pour éviter la surcharge visuelle
                        color='black'  # Couleur des étiquettes
                    )

                # Configuration des axes et du titre
                ax.set_xlabel(x_axis_option.replace('_', ' ').title())  # Met en forme le titre de l'axe X
                ax.set_ylabel('Nombre de joueurs')  # Titre de l'axe Y
                ax.set_title(f'Nuage de points: {x_axis_option.replace("_", " ").title()} vs Nombre de joueurs')  # Titre du graphique

                # Affichage dans Streamlit
                st.pyplot(fig)


            # Affichage des 10 premiers résultats pour débogage
            st.dataframe(results_df.head(10)) 

    else:

        st.write("Cette requête donne des statistiques pour un pays spécifique choisi par l'utilisateur. Elle inclut le nombre total de matchs joués par les compétiteurs de ce pays, le nombre total de victoires, le nombre total de joueurs et le pourcentage de victoires. Les résultats sont triés par le pourcentage de victoires décroissant en fonction de la variable choisie (comme heures EPS en primaire, population en 2018 ou licenciés en 2018).")

        country_option = st.selectbox("Choix du pays", nations['country'])

        if country_option:  # Vérifie qu'un pays a été sélectionné
            requete = f"""
        MATCH (c:COMPETITOR)-[r:PLAYED]->(g:GAME)-[:HAPPENED_IN]->(s:SEASON)
        MATCH (n:NATION)
        WHERE n.country_code2 = c.country_code
        AND c.country = '{country_option}'
        WITH c.country AS country, 
            n.hours_of_sport AS hours_of_sport,
            COUNT(g) AS total_matches, 
            SUM(CASE WHEN g.winner_id = c.id THEN 1 ELSE 0 END) AS total_wins, 
            COUNT(DISTINCT c.id) AS total_players
        WITH country, 
            hours_of_sport,
            total_matches AS total_matches_by_country,
            total_wins AS total_wins_by_country,
            total_players AS total_players_by_country,
            ROUND((TOFLOAT(total_wins) / total_matches) * 100, 2) AS win_percentage_by_country
        RETURN country, 
            hours_of_sport,
            total_matches_by_country,
            total_wins_by_country,
            total_players_by_country,
            win_percentage_by_country
        ORDER BY win_percentage_by_country DESC
        LIMIT 10
            """
            # Affiche la requête dans Streamlit
            st.markdown(f"```cypher\n{requete}\n```")

            # Bouton pour exécuter la requête
            if st.button("Exécuter la requête"):
                result = db.execute_query(requete)  # Exécute la requête dans la base de données
                results_df = pd.DataFrame(result)  # Convertit le résultat en DataFrame
                st.dataframe(results_df)          # Affiche le DataFrame dans Streamlit

def profil_meteo():
    st.header("Corrélation météo/résultat", divider=True)
    
    # view_option = st.radio("analysis_blessures vue", ("Vue générale", "Vue personnalisée"),label_visibility="hidden")
    requete_nation = """
    MATCH (w:WEATHER)
WITH 
    split(w.name, ",") AS nameParts, 
    w.humidity AS humidity, 
    w.solarradiation AS solarradiation,
    w.temp AS temp, 
    w.tempmax AS tempmax, 
    w.tempmin AS tempmin, 
    w.windspeed AS windspeed
WITH 
    trim(nameParts[-1]) AS lastPartOfName,
    humidity, solarradiation, temp, tempmax, tempmin, windspeed
WITH 
    CASE 
        WHEN lastPartOfName = "United Kingdom" THEN "Great Britain" 
        WHEN lastPartOfName = "Italia" THEN "Italy" 
        WHEN lastPartOfName = "México" THEN "Mexico" 
        WHEN lastPartOfName = "United States" THEN "USA" 
        WHEN lastPartOfName = "Chine" THEN "China" 
        WHEN lastPartOfName = "España" THEN "Spain" 
        WHEN lastPartOfName = "Serbie" THEN "Serbia" 
        ELSE lastPartOfName 
    END AS Country
return distinct Country
"""
    nation_meteo = db.execute_query(requete_nation)
    nation_meteo_df = pd.DataFrame(nation_meteo)
    # Sélection de la variable pour l'axe des abscisses
    # x_axis_option = st.selectbox(
    #     "Choisir la variable pour l'axe des abscisses",
    #     ("heures EPS en primaire", "population en 2018", "licenciés en 2018")
    # )

    # if view_option == "Vue générale":

#         st.write("Cette requête donne des statistiques pour chaque pays, en fonction de la variable choisie par l'utilisateur (soit les heures EPS en primaire, la population en 2018 ou les licenciés en 2018). Elle inclut le nombre total de matchs, le nombre total de victoires, le nombre total de joueurs et le pourcentage de victoires, tout cela trié par le pourcentage de victoires décroissant.")

#         st.markdown("#### Requête")

#         x_axis_column = column_mapping[x_axis_option]

#         requete = f"""
# MATCH (c:COMPETITOR)-[r:PLAYED]->(g:GAME)-[:HAPPENED_IN]->(s:SEASON)
# MATCH (n:NATION)
# WHERE n.country_code2 = c.country_code
# AND n.hours_of_sport IS NOT NULL
# AND n.population_2018 IS NOT NULL
# AND n.licensees_2018 IS NOT NULL
# WITH c.country AS country, 
#      n.hours_of_sport AS hours_of_sport,
#      n.population_2018 AS population,
#      n.licensees_2018 AS licencies,
#      COUNT(g) AS total_matches, 
#      SUM(CASE WHEN g.winner_id = c.id THEN 1 ELSE 0 END) AS total_wins, 
#      COUNT(DISTINCT c.id) AS total_players
# WITH country, 
#      hours_of_sport,
#      population,
#      licencies,
#      total_matches AS total_matches_by_country,
#      total_wins AS total_wins_by_country,
#      total_players AS total_players_by_country,
#      ROUND((TOFLOAT(total_wins) / total_matches) * 100, 2) AS win_percentage_by_country
# RETURN country, 
#        hours_of_sport,
#        population,
#        licencies,
#        total_matches_by_country,
#        total_wins_by_country,
#        total_players_by_country,
#        win_percentage_by_country
# ORDER BY win_percentage_by_country DESC
#         """
        
#         st.markdown(f"```cypher\n{requete}\n```")

#         if st.button("Exécuter la requête"):
#             result = db.execute_query(requete)
#             results_df = pd.DataFrame(result)

#             # Filtrage des données pour s'assurer que la variable choisie n'est pas nulle
#             # Appliquer le filtrage sur le DataFrame après avoir récupéré les résultats
#             results_df = results_df[results_df[x_axis_column].notnull()]

#             # Vérifier si le DataFrame après filtrage n'est pas vide
#             if results_df.empty:
#                 st.warning(f"Aucun résultat valide pour {x_axis_option}.")
#             else:
#                 # Affichage du nuage de points avec étiquettes
#                 fig, ax = plt.subplots(figsize=(10, 6))

#                 # Tracé des points
#                 scatter = ax.scatter(
#                     results_df[x_axis_column], 
#                     results_df['total_players_by_country'], 
#                     c='blue', 
#                     label='Pays'
#                 )

#                 # Ajout des étiquettes pour chaque point
#                 for i, country in enumerate(results_df['country']):  # Supposons que la colonne 'country' contient les noms des pays
#                     ax.annotate(
#                         country, 
#                         (results_df[x_axis_column].iloc[i], results_df['total_players_by_country'].iloc[i]),
#                         textcoords="offset points",  # Décale le texte
#                         xytext=(5, 5),  # Distance du texte par rapport au point
#                         ha='left',  # Alignement horizontal
#                         fontsize=8,  # Taille de la police pour éviter la surcharge visuelle
#                         color='black'  # Couleur des étiquettes
#                     )

#                 # Configuration des axes et du titre
#                 ax.set_xlabel(x_axis_option.replace('_', ' ').title())  # Met en forme le titre de l'axe X
#                 ax.set_ylabel('Nombre de joueurs')  # Titre de l'axe Y
#                 ax.set_title(f'Nuage de points: {x_axis_option.replace("_", " ").title()} vs Nombre de joueurs')  # Titre du graphique

#                 # Affichage dans Streamlit
#                 st.pyplot(fig)


#             # Affichage des 10 premiers résultats pour débogage
#             st.dataframe(results_df.head(10)) 

    # else:

    st.write("Cette requête en contient 2 puisqu'elle cherche à établir une corrélation entre le nombre de victoire de joueurs dont la nationnalité serait proche du pays dans lequel il joue selon certains indicateurs climatiques.")

    country_option = st.selectbox("Choix du pays", nation_meteo_df['Country'],index=sorted(nation_meteo_df['Country']).index("USA"))

    if country_option:  # Vérifie qu'un pays a été sélectionné
        requete_game = f"""
MATCH (m:GAME)
WHERE m.country_name = "{country_option}"
UNWIND [m.competitor1_country, m.competitor2_country] AS country
WITH country, 
     m, 
     CASE 
         WHEN m.winner_id = m.competitor1_id THEN m.competitor1_country
         WHEN m.winner_id = m.competitor2_id THEN m.competitor2_country
         ELSE NULL
     END AS winner_country
WITH 
    country, 
    COUNT(*) AS games_played, 
    SUM(CASE WHEN country = winner_country THEN 1 ELSE 0 END) AS games_won
RETURN 
    country, 
    games_played, 
    games_won, 
    (games_won * 1.0 / games_played) AS win_ratio
ORDER BY win_ratio DESC;
        """
        requete_meteo = f"""
// Partie 1 : Calcul des moyennes par pays avec remplacement des noms spécifiques
MATCH (w:WEATHER)
WITH 
    split(w.name, ",") AS nameParts, 
    w.humidity AS humidity, 
    w.solarradiation AS solarradiation,
    w.temp AS temp, 
    w.tempmax AS tempmax, 
    w.tempmin AS tempmin, 
    w.windspeed AS windspeed
WITH 
    trim(nameParts[-1]) AS lastPartOfName,
    humidity, solarradiation, temp, tempmax, tempmin, windspeed
WITH 
    CASE 
        WHEN lastPartOfName = "United Kingdom" THEN "Great Britain" 
        WHEN lastPartOfName = "Italia" THEN "Italy" 
        WHEN lastPartOfName = "México" THEN "Mexico" 
        WHEN lastPartOfName = "United States" THEN "USA" 
        WHEN lastPartOfName = "Chine" THEN "China" 
        WHEN lastPartOfName = "España" THEN "Spain" 
        WHEN lastPartOfName = "Serbie" THEN "Serbia" 
        ELSE lastPartOfName 
    END AS Country,
    avg(humidity) AS avgHumidity, 
    avg(solarradiation) AS avgSolarRadiation, 
    avg(temp) AS avgTemp, 
    avg(tempmax) AS avgTempMax, 
    avg(tempmin) AS avgTempMin, 
    avg(windspeed) AS avgWindSpeed

// Partie 2 : Création d une collection avec toutes les moyennes
WITH collect({{
    country: Country, 
    avgHumidity: avgHumidity, 
    avgSolarRadiation: avgSolarRadiation, 
    avgTemp: avgTemp, 
    avgTempMax: avgTempMax, 
    avgTempMin: avgTempMin, 
    avgWindSpeed: avgWindSpeed
}}) AS weatherData

// Partie 3 : Sélection du pays de référence (à modifier selon le besoin)
WITH weatherData,
     '{country_option}' AS referenceCountry  // Changez ici le pays de référence

// Partie 4 : Extraction des données du pays de référence
WITH weatherData,
     referenceCountry,
     [x IN weatherData WHERE x.country = referenceCountry][0] AS refCountryData

// Partie 5 : Calcul de la distance euclidienne et du score global pour chaque pays
UNWIND weatherData AS countryData
WITH countryData,
     referenceCountry,
     refCountryData,
     SQRT(
        (countryData.avgHumidity - refCountryData.avgHumidity) * (countryData.avgHumidity - refCountryData.avgHumidity) +
        (countryData.avgSolarRadiation - refCountryData.avgSolarRadiation) * (countryData.avgSolarRadiation - refCountryData.avgSolarRadiation) +
        (countryData.avgTemp - refCountryData.avgTemp) * (countryData.avgTemp - refCountryData.avgTemp) +
        (countryData.avgTempMax - refCountryData.avgTempMax) * (countryData.avgTempMax - refCountryData.avgTempMax) +
        (countryData.avgTempMin - refCountryData.avgTempMin) * (countryData.avgTempMin - refCountryData.avgTempMin) +
        (countryData.avgWindSpeed - refCountryData.avgWindSpeed) * (countryData.avgWindSpeed - refCountryData.avgWindSpeed)
     ) AS euclideanDistance,
     // Calcul du score global normalisé
     (
        countryData.avgHumidity + 
        countryData.avgSolarRadiation / 10 +  // Normalisé car échelle différente
        countryData.avgTemp + 
        countryData.avgTempMax + 
        countryData.avgTempMin + 
        countryData.avgWindSpeed
     ) AS globalScore
WHERE countryData.country <> referenceCountry

// Partie 6 : Retour des résultats triés par distance
RETURN 
    countryData.country AS Country,
    round(euclideanDistance * 100) / 100 AS Distance,
    round(globalScore * 100) / 100 AS GlobalScore,
    round(countryData.avgHumidity * 100) / 100 AS Humidity,
    round(countryData.avgSolarRadiation * 100) / 100 AS SolarRadiation,
    round(countryData.avgTemp * 100) / 100 AS Temperature,
    round(countryData.avgTempMax * 100) / 100 AS TempMax,
    round(countryData.avgTempMin * 100) / 100 AS TempMin,
    round(countryData.avgWindSpeed * 100) / 100 AS WindSpeed
ORDER BY Distance ASC
        """
        # Affiche la requête dans Streamlit
        st.markdown(f"```cypher\n{requete_game}\n```")
        st.markdown(f"```cypher\n{requete_meteo}\n```")

#### Requête pour les matchs
        # Bouton pour exécuter la requête
        if st.button("Exécuter la requête"):
            # Exécution de la requête et création du DataFrame
            result_game = db.execute_query(requete_game)
            result_game_df = pd.DataFrame(result_game)
            result_game_df = pd.merge(result_game_df, nation_meteo_df, left_on='country', right_on='Country')
            # Transformation des données pour Altair
            data_melted = result_game_df.melt(
                id_vars=["country"], 
                value_vars=["games_won", "games_played"],
                var_name="Metric", 
                value_name="Count"
            )

            # Création du graphique Altair
            chart = alt.Chart(data_melted).mark_bar().encode(
                x=alt.X("country:N", title="Pays"),  # Changé de 'year' à 'country'
                y=alt.Y("Count:Q", title="Nombre de matchs"),
                color=alt.Color(
                    "Metric:N",
                    title="Type",
                    scale=alt.Scale(
                        domain=["games_won", "games_played"],
                        range=["#2ecc71", "#3498db"]  # Vert pour les victoires, bleu pour le total
                    )
                ),
                xOffset="Metric:N",  # Pour les barres côte à côte
                tooltip=[
                    alt.Tooltip("country:N", title="Pays"),
                    alt.Tooltip("Metric:N", title="Type"),
                    alt.Tooltip("Count:Q", title="Nombre de matchs")
                ]
            ).properties(
                width=600,
                height=400,
                title="Matchs gagnés vs total par pays"
            ).configure_axis(
                labelAngle=-45  # Rotation des labels pour une meilleure lisibilité
            )

            # Affichage dans Streamlit
            st.altair_chart(chart, use_container_width=True)

            # Transformation des données pour Altair
            data_melted = result_game_df.melt(
                id_vars=["country"], 
                value_vars=["win_ratio"],  # Utilisation de la variable 'Distance'
                var_name="Metric", 
                value_name="Count"
            )

            # Création du graphique Altair
            chart = alt.Chart(data_melted).mark_bar().encode(
                x=alt.X("country:N", title="Pays"),  # Changé de 'year' à 'country'
                y=alt.Y("Count:Q", title="win_ratio"),
                color=alt.Color(
                    "Metric:N",
                    title="Métrique",
                    scale=alt.Scale(
                        domain=["win_ratio"],  # Remplace 'games_won' et 'games_played' par 'Distance'
                        range=["#e74c3c"]  # Choix d'une couleur pour 'Distance' (par exemple, rouge)
                    )
                ),
                tooltip=[
                    alt.Tooltip("country:N", title="Pays"),
                    alt.Tooltip("Metric:N", title="Métrique"),
                    alt.Tooltip("Count:Q", title="win_ratio")
                ]
            ).properties(
                width=600,
                height=400,
                title="Ratio de victoire par pays"
            ).configure_axis(
                labelAngle=-45  # Rotation des labels pour une meilleure lisibilité
            )

            # Affichage dans Streamlit
            st.altair_chart(chart, use_container_width=True)

#### Requête pour la météo
            # Exécution de la requête et création du DataFrame
            result_meteo = db.execute_query(requete_meteo)
            result_meteo_df = pd.DataFrame(result_meteo)
            # st.dataframe(nation_meteo_df)
            result_meteo_df = pd.merge(result_meteo_df, nation_meteo_df, on='Country')
            # st.dataframe(result_meteo_df)
            # Transformation des données pour Altair, en utilisant Distance
            data_melted = result_meteo_df.melt(
                id_vars=["Country"], 
                value_vars=["Distance"],  # Utilisation de la variable 'Distance'
                var_name="Metric", 
                value_name="Count"
            )

            # Création du graphique Altair
            chart = alt.Chart(data_melted).mark_bar().encode(
                x=alt.X("Country:N", title="Pays"),  # Changé de 'year' à 'country'
                y=alt.Y("Count:Q", title="Distance"),
                color=alt.Color(
                    "Metric:N",
                    title="Métrique",
                    scale=alt.Scale(
                        domain=["Distance"],  # Remplace 'games_won' et 'games_played' par 'Distance'
                        range=["#e74c3c"]  # Choix d'une couleur pour 'Distance' (par exemple, rouge)
                    )
                ),
                tooltip=[
                    alt.Tooltip("Country:N", title="Pays"),
                    alt.Tooltip("Metric:N", title="Métrique"),
                    alt.Tooltip("Count:Q", title="Distance")
                ]
            ).properties(
                width=600,
                height=400,
                title="Distance par pays"
            ).configure_axis(
                labelAngle=-45  # Rotation des labels pour une meilleure lisibilité
            )

            # Affichage dans Streamlit
            st.altair_chart(chart, use_container_width=True)
