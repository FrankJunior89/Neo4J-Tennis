from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import networkx as nx
import json





class Database:

    def __init__(self,url,user,password):
        self.driver = GraphDatabase.driver(url, auth=(user, password))

    def close(self):
        self.driver.close()

    def nodes(self):
        
        with self.driver.session() as session:
            result = session.run("CALL db.labels();")
            
            return [record[0] for record in result]
        
    def number_nodes(self):
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN COUNT(n)as n_nodes;")

            return result.single()['n_nodes']
        
    def number_relationships(self):
        query = "MATCH ()-[r]->() RETURN count(r) AS numberOfRelationships"

        with self.driver.session() as session:
            result = session.run(query)

            return result.single()['numberOfRelationships']
        
    def delete_nodes(self,LabelName):
        query = "MATCH (n:" + LabelName + ")REMOVE n:" + LabelName

        with self.driver.session() as session:
            result = session.run(query)

        print("Nodes deleted successfully")

    def filter_departments(self,DepartmentName):

        query = "MATCH (c:COMMUNES)-[:`SE SITUE DANS`]->(d:DEPARTEMENTS) WHERE d.departement = '" +  DepartmentName + "' RETURN c.nomcom AS commune"
        
        with self.driver.session() as session:
            result = session.run(query)
            
            return result.data()






