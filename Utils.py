import json


Departements = ("Pas de Préférences","Paris","Seine-et-Marne","Yvelines","Essonne","Hauts-de-Seine","Seine-Saint-Denis","Val-de-Marne", "Val-d'oise")

def load_credentials(file_path):

    with open(file_path, 'r') as file:
        credentials = json.load(file)

    return credentials



