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
        
        years = st.multiselect("Year  :",[2022,2023,2024],default=[2024])

        min_matches = st.number_input("Nombre matchs  (min):", min_value=0, value=100, step=10)

        player_option = st.selectbox("Choix du joueur", players['name'])

        if player_option != None:
            
            st.markdown("#### Requête")

            requete = f"""
                MATCH (c:COMPETITOR)-[r:PLAYED]->(g:GAME)-[:HAPPENED_IN]->(s:SEASON)
                WHERE s.year IN {years} AND c.name = '{player_option}'
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
            """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            players_df =pd.DataFrame(result)

            st.dataframe(players_df)
   

def meilleur_ami():
    st.header("Mon meilleur Ami", divider=True)

    st.markdown("#### Requête")

    player_option = st.selectbox("Choix du joueur", players['name'])

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
                ORDER BY win_percentage DESC
                LIMIT 10
        """
        st.markdown(f"```cypher\n{requete}\n```")


        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            players_df =pd.DataFrame(result)

            st.dataframe(players_df)
            

    else:
        
        years = st.multiselect("Year   ",[2022,2023,2024],default=[2024])

        player_option = st.selectbox("Choix du joueur", players['name'])

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
        player_option = st.selectbox("Choix du joueur", players['name'])

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

    player_option = st.selectbox("Choix du joueur", players['name'])

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

                players_df['year'] = players_df['year'].astype(int)

                # Transformation des données pour Altair
                data_melted = players_df.melt(id_vars=["year"], 
                                            value_vars=["total_wins", "total_matches"], 
                                            var_name="Metric", 
                                            value_name="Count")

                # Création du graphique Altair
                chart = alt.Chart(data_melted).mark_bar().encode(
                    x=alt.X("year:O", title="Year"),  # Axe X : les années
                    y=alt.Y("Count:Q", title="Count"),  # Axe Y : les valeurs (correctif ici)
                    color=alt.Color("Metric:N", title="Metric"),  # Couleurs pour différencier les métriques
                    xOffset="Metric:N"  # Décalage horizontal pour afficher côte à côte
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
                    ORDER BY win_percentage_as_favorite DESC
            """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            results_df =pd.DataFrame(result)

            st.dataframe(results_df)

    else:

        player_option = st.selectbox("Choix du joueur", players['name'])

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

    st.markdown("#### Requête")

    player_option = st.selectbox("Choix du joueur", players['name'])

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

        player_option = st.selectbox("Choix du joueur", players['name'])

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
                ORDER BY finales_won DESC
            """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            players_df =pd.DataFrame(result)

            st.dataframe(players_df)

     else:
          player_option = st.selectbox("Choix du joueur", players['name'])

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

     st.markdown("#### Requête")

     requete = """
                            MATCH (c:COMPETITOR)
                WHERE c.Shoes IS NOT NULL 
                RETURN c.Shoes AS shoe_brand, COUNT(c) AS number_of_athletes
                ORDER BY number_of_athletes DESC;
            """
     st.markdown(f"```cypher\n{requete}\n```")

     if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            result_df =pd.DataFrame(result)

            if not result_df.empty:

                plt.figure(figsize=(10, 6))
                plt.bar(result_df['shoe_brand'], result_df['number_of_athletes'], color='skyblue')
                plt.xlabel('Marque de Chaussures')
                plt.ylabel('Nombre d\'athlètes')
                plt.title('Histogramme des Athlètes par Marque de Chaussures')
                plt.xticks(rotation=45, ha='right')  # Rotation des labels des marques
                plt.tight_layout()
                
                # Affichage de l'histogramme
                st.pyplot(plt)
     

def perf_by_surface():
     
     st.header("Performance par Surface de Jeu", divider=True)

     view_option = st.radio("perf_globale vue", ("Vue générale", "Vue personnalisée"),label_visibility="hidden")

     if view_option == "Vue générale":
        
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

        player_option = st.selectbox("Choix du joueur", players['name'])

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
    
    if view_option == "Vue générale":
        st.markdown("#### Requête")

        requete = f"""
MATCH (c:COMPETITOR)-[r:PLAYED]->(g:GAME)-[:HAPPENED_IN]->(s:SEASON)
MATCH (n:NATION)
WHERE n.country_code2 = c.country_code  // Correspondance explicite entre COMPETITOR et NATION
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
LIMIT 10            """
        st.markdown(f"```cypher\n{requete}\n```")

        if st.button("Exécuter la requête"):
            result = db.execute_query(requete)

            results_df =pd.DataFrame(result)

            st.dataframe(results_df)

    else:

        country_option = st.selectbox("Choix du pays", nations['country'])

        if country_option:  # Vérifie qu'un pays a été sélectionné
            requete = f"""
        MATCH (c:COMPETITOR)-[r:PLAYED]->(g:GAME)-[:HAPPENED_IN]->(s:SEASON)
        MATCH (n:NATION)
        WHERE n.country_code2 = c.country_code
        AND c.country = '{country_option}'  // Filtre pour le pays sélectionné
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



     





    








