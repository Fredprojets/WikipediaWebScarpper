import re
import requests
import networkx as nx
import matplotlib.pyplot as plt
import textdistance
from bs4 import BeautifulSoup

def main():
    nbVisite = 0
    # La node de départ
    mot = input("Choisissez un mot en anglais à chercher sur wikipedia: ")
    # contient les tuples (mot, motLié)
    adj = list(dict.fromkeys(rechercheWikiMotEng(mot)))
    # initialise un graph dirigé avec seulement le mot initial
    G = nx.DiGraph()
    G.add_node(mot)
    
    niveau = int(input("Choisissez le nombre de niveaux désirés: "))
    noeudsParNiveau = int(input("Choisissez le nombre de noeuds par niveau désiré: "))

    # trouve le site
    r = requests.get("https://en.wikipedia.org/wiki/"+mot)
    
    # organise le resultat de la recherche
    motInitial = BeautifulSoup(r.content, 'html.parser')
    #garde le texte seulement
    motInitial =  motInitial.get_text()

    for _ in range(niveau):
        tempDist = [] # contient la distance entre le texte du mot initial et de chaque lien
        tempMots = [] # contient les tuples (mot, motLié)


        # Pour chaque lien, n est la position du mot courant dans la list adj
        for n in range(len(adj)):            
            # trouve le site
            r = requests.get("https://en.wikipedia.org/wiki/"+adj[n][1])
            #organise le resultat de la recherche
            motCourant = BeautifulSoup(r.content, 'html.parser')
            # trouve la distance avec le texte du mot initial
            distMot = textdistance.sorensen(motInitial, motCourant.get_text())
            nbVisite +=1
            # si on a pas encore le maximum de noeud on garde dist et le mot
            if len(tempDist)< noeudsParNiveau:
                tempDist.append(distMot)
                tempMots.append(adj[n])
            else:
                # si on a max de noeud on verifie si la distance est plus petite
                for k in range(len(tempDist)):
                    if distMot<tempDist[k]:
                        tempDist[k] = distMot
                        tempMots[k] = adj[n]
                        break
        # a tous les candidats pour le niveau dans tempMots avec la boucle précédente
        print(tempDist)
        print(tempMots)
        temp = []
        for n in tempMots:
            # store les liens des mots qu'on va ajouter
            temp.extend(rechercheWikiMotEng(n[1]))
        #elimine doublon
        temp = list(dict.fromkeys(temp))
        # pour chaque element on l'ajoute
        for k in tempMots:
            G.add_edge(k[0],k[1])
            #si le noeud destination est présent on retire le noeud de la recherche pour éviter des cycles
            if k[1] in G and k in temp:
                temp.remove(k)
        # met à jour les liens à explorer
        adj = temp
    nx.draw_planar(G, with_labels=True)
    plt.savefig(mot+"planar.png")
    nx.draw_circular(G, with_labels=True)
    plt.savefig(mot+"circular.png")
    nx.draw_shell(G, with_labels=True)
    plt.savefig(mot+"shell.png")
    nx.draw_spring(G, with_labels=True)
    plt.savefig(mot+"spring.png")
    plt.show()
    print(nbVisite)
# fait une recherche du mot dans wikipedia en anglais
# retourne un liste de liens wikipedia
def rechercheWikiMotEng(mot):
    # trouve le site
    r = requests.get("https://en.wikipedia.org/wiki/"+mot)
    #organise le resultat de la recherche
    motCourant = BeautifulSoup(r.content, 'html.parser')

    adj = []
    #trouve tous les liens vers un autre article
    #garde le titre de l'article seulement dans une liste
    for link in motCourant.find_all('a'):
        liens = str(link.get('href'))
        if re.search("^/wiki/", liens) is not None: 
            if re.search("disambiguation+",liens) is None:
                if re.search("Main_Page+",liens) is None:
                    if re.search(":+",liens) is None:
                        adj.append((mot , liens[6:]))
    return adj
    
if __name__ == "__main__":
    main()
