import copy
import numpy as np
import collections
import matplotlib.pyplot as plt
from random import randint
from tqdm import tqdm
import time

def printl (l) :
        for i in l :
            print("     ", *i)

def update_plateau (plateau, places_occupées, voitures, sorties) :
    next_plateau  = []
    for i in range (longueur) :
        next_plateau.append([])
        for j in range (largeur) :
            next_plateau[i].append('.')

    for i in range (largeur) :
        for j in range (longueur) :
            if [i, j] in voitures :
                next_plateau[i][j] = "v"
    for sortie in sorties :
        if sortie not in voitures :
            next_plateau[sortie[0]][sortie[1]] = "s"
    for i in places :
        if i not in voitures :
            next_plateau[i[0]][i[1]] = "M"
    return next_plateau

def voisins (plateau, voiture) :
    [largeur, longueur] = dim
    [i, j] = voiture
    voisins_provisoire = [[i-1, j], [i+1, j], [i, j-1], [i, j+1]]
    voisins_final = []
    for k in voisins_provisoire :
        passe = True
        if k[0] < 0 or k[1] < 0 or k[0] >= largeur or k[1] >= longueur:
            passe = False
        if passe :
            voisins_final.append(k)
    return voisins_final

def pathfinding (voiture, sortie, plateau, turvoi): #algo de Bellman Ford

    if voiture == sortie : # cas où la voiture est sur la sortie
        return "bye bye", 0
    #on crée le graphe et la liste des distances
    S = [] # sommets du graphe
    d = [] # distance de la source à chaque point. On met ";" si la distance n'existe pas
    predecesseurs = []
    for i in range (len(plateau)) :
        d.append([])
        predecesseurs.append([])
        for j in range (len(plateau[i])) :
            if ([i,j] not in turvoi and [i, j] not in places) or [i,j] == sortie:
                S.append([i, j])
                d[i].append(np.inf)
                predecesseurs[i].append(None)
            else :
                d[i].append(";")
                predecesseurs[i].append(";")
    d[voiture[0]][voiture[1]] = 0

    #algo en question
    checkable = collections.deque(([voiture]))
    vu = []
    while len(checkable) > 0 :
        u = checkable.popleft()
        for v in voisins(plateau, u) :
            if type(d[u[0]][u[1]]) != str and type(d[v[0]][v[1]]) != str: # on vérifie si la distance existe sinon, d = ";"
                if d[u[0]][u[1]] + 1 < d[v[0]][v[1]] :
                    d[v[0]][v[1]] = d[u[0]][u[1]] + 1
                    predecesseurs[v[0]][v[1]] = u
                if v not in vu and v not in checkable:
                    checkable.append(v)
        vu.append(u)

    #remonter le chemin :
    if d[sortie[0]][sortie[1]] == np.inf :
        return voiture, 1000
    else :
        chemin = [sortie]
        while voiture not in chemin :
            place_int = chemin[0]
            chemin = [predecesseurs[place_int[0]][place_int[1]]] + chemin
        return chemin[1], len(chemin)



def AUTOMATE (dimension, voitures, places) :

    plateau  = [] #ensemble du plateau cad là où ça se passe.
    for i in range (longueur) :
        plateau.append([])
        for j in range (largeur) :
            plateau[i].append('.')
    plateaux = [plateau] # liste des plateaux qui ont été vus dans le processus

    places_occupées = copy.deepcopy(places) #ensemble des places occupées
    #ici toutes les places sont considérrées occupées à l'état initial

    sorties = [[0, int(dimension[0]/2)], [dimension[1]-1, int(dimension[0]/2)-1]] #endroit vers lequel les voitures se dirigent


    running = True
    nb_boucle = 0

    #boucle principale

    while running :

        new_voitures = []
        for v in voitures :
            pos = []
            for s in sorties :
                pos.append(pathfinding(v, s, plateau, new_voitures))
            pmin = pos[0]
            if "bye bye" in pos :
                pmin = "bye bye"
            else :
                for p in pos :
                    if p[1] < pmin[1] :
                        pmin = p
            new_pos = pmin[0] # calul des nouvelles position des voitures
            if new_pos == v : # si la voiture ne bouge pas
                new_voitures.append(v)
            elif new_pos != "bye bye" : #si la voiture bouge classiquement
                if new_pos in new_voitures :
                    new_voitures.append(v)
                else :
                    new_voitures.append(new_pos)
            # si la nouvelle position est bye bye, alors la voitures est rétirée de la liste, en l'occurence pas rajoutée dans la nouvelle liste

        #condition d'arrêt de la boucle: il n'y a plus de voitures sur la parking
        if len(voitures) == 0 :
            running = False

        nb_boucle += 1
        new_plateau = update_plateau(plateau, places_occupées, voitures, sorties) # maj du plateau
        voitures = copy.deepcopy(new_voitures)
        plateau = copy.deepcopy(new_plateau)
        plateaux.append(new_plateau)


    return nb_boucle


def generateur (dim, n, places) : #générateur de n voitures distinctes
    doublets = []
    for i in range (n) :
        c_good = False
        while not c_good :
            x = randint(0, dim[0]-1)
            y = randint(0, dim[1]-1)
            v = [x, y]
            if v in doublets or v in places :
                c_good = False
            else :
                c_good = True
        doublets.append(v)
    return doublets



def testing_parking(dim, places, nom, ymax) :
    n = 100 # nb config pour faire la moyenne
    nb_tours = []
    nb_voitures = []
    t1 = time.time()
    if len(places) != 0 :
        nbplaces = len(places)
    else :
        nbplaces = dim[0]*dim[1]-1
    for i in tqdm(range (1, nbplaces)) : #nb de tours moyens nécessaire pour que i voitures sortent du parking
        tour_ = 0 # nb moyen de tour
        for j in range (n) :
            voitures = generateur(dim, i, places) # on génère aléatoirement les voitures
            tour_ += AUTOMATE (dim, voitures, places)
        tour_ = tour_/n
        nb_tours.append(tour_)
        nb_voitures.append(i/nbplaces)

    t2 = time.time()
    print("{}min, {}s".format((t2-t1)//60, (t2-t1)%60))
    plt.xlabel("taux de remplissage")
    plt.ylabel("nombre de tours ")
    ax = plt.gca()
    ax.set_xlim([0, 1])
    ax.set_ylim([0, ymax])
    plt.plot(nb_voitures, nb_tours)
    z = np.polyfit(nb_voitures, nb_tours, 1)
    p = np.poly1d(z)
    plt.plot(nb_voitures, [p(i) for i in nb_voitures])
    plt.savefig('img/' + str(dim[0]) + '-' + str(dim[1]) + '/' + nom)

def fourchette (dim, ymax) :
    places = []
    for i in range(dim[0]) :
        for j in range (dim[1]) :
            if i%3 == 0 and j not in [dim[1]-1, dim[1]] :
                places.append([i, j])
    testing_parking(dim, places, 'fourchette.svg', ymax)

def fourchetteinv (dim, ymax) :
    places = []
    for i in range(dim[0]) :
        for j in range (dim[1]) :
            if j%3 == 0 and i not in [dim[1]-1, dim[1]] :
                places.append([i, j])
    testing_parking(dim, places, 'fourchetteinv.svg', ymax)

def ilots (dim, ymax) :
    places = []
    for i in range(dim[0]) :
        for j in range (dim[1]) :
            if i%10 >= 2 and j%5 >= 2 :
                places.append([i, j])
    testing_parking(dim, places, 'ilots.svg', ymax)

def pilots (dim, ymax) :
    places = []
    for i in range(dim[0]) : #places en fourchette
        for j in range(dim[1]) :
            if i%4 in [1,2] and j%5 >= 2:
                places.append([i, j])
    testing_parking(dim, places, 'pilots.svg', ymax)

def vide (dim, ymax) :
    places  = []
    testing_parking(dim, places, 'vide.svg', ymax)

def affichage(places, dim, voitures) :
    plateau  = [] #ensemble du plateau cad là où ça se passe.
    for i in range (dim[0]) :
        plateau.append([])
        for j in range (dim[1]) :
            plateau[i].append('.')
    sorties = [[0, dim[0]//2+1]]
    printl(update_plateau(plateau, places, voitures, sorties))

##############################################################

largeur, longueur = 12, 12
dim = [largeur, longueur]
places = [] #ensemble des places vides
ymax = 100

#voitures = [[5, 1], [3, 5], [5, 7], [8, 5], [9, 5], [3, 1]] #ensemble des voitures définies par leur position
#voitures = [[9,5]]

print("")


fourchette(dim, ymax)
fourchetteinv(dim, ymax)
ilots(dim, ymax)
pilots(dim, ymax)
vide(dim, ymax)

#AUTOMATE(dim, voitures, places)

places = []
for i in range(dim[0]) : #places en fourchette
    for j in range(dim[1]) :
        if i%4 in [1,2] and j%5 >= 2:
            places.append([i, j])