from Utils import load_credentials
from Database import Database
import streamlit as st


credentials = load_credentials('.gitignore/credentials.json')

URL = credentials['NEO4J_URI']
USER = credentials['NEO4J_USERNAME']
PASSWORD = credentials['NEO4J_PASSWORD']


st.markdown("# Sources")

st.markdown("""
            [SportRadar API](https://console.sportradar.com/accounts/6740bf5617163e1e30067534)\n
            [Tennis Male Players Sponsors](https://www.scoreandchange.com/tennis-sponsorships-men-singles/)\n
            [Tennis Feamle Players Sponsors](https://www.scoreandchange.com/tennis-sponsorships-women-singles/)\n
            [WTA Coachs](https://www.wtatennis.com/coaches/list)\n
            [ATP Coachs](https://www.atptour.com/en/players/coaches)\n
            [Injuries Data](https://tennisinsight.com/injuries/)\n
            [Licences en Europe](https://www.tenniseurope.org/file/822778/?dl=1)\n
            [Nombre d'heures d'EPS](https://patrickbayeux.com/actualites/ecole-elementaire-la-france-sur-le-podium-du-nombre-heures-en-eps/)\n
            [Weather API Data](https://www.visualcrossing.com)


            
            
            
            
            """)




