Stage de fin d'étude, Master 2 informatique, de Lucas Brouet. L’objectif est de générer une spatialisation multincanale automatiquement à partir d'un audio ou d'une partition.
Le cas d'étude dans le cadre de ce stage sont les musiques du dernier album du groupe de rock : "Praetorian". 

Contexte : Une expérience de spatialisation a été réalisée lors d'un concert du groupe à "l'inconnue" (salle de spectacle dans Bordeaux). Durant le concert, un des membre du SCRIME a conçu un système lui
permettant de déplacement les sources sonore de chaque instruments dans l'espace. Cela a donné lieu à une spatialisation "intuitive", qui constitue donc une donnée d'entrée pour le stage.
L'objectif sera de se servir de ces données afin de :

- Comprendre les mécaniques et paramètres qui incitent à "déclencher" cette spatialisation.
- Etablir des trajectoires spatiales "types"
- Entrainer un modèle afin de reproduire ce mécanisme à partir des données précedentes. 
- Tester et comparer via du contenu visuel et audio

Le code comporte deux grandes parties :

La **visualisation de donnée** (_Data_Visualization_)ainsi que **l'entrainement des données** (_Data_Training_)


**Visualisation de donnée**
Il s'agit ici de produire du contenu visuelle, comme des graphiques 2d et 3d, afin d'observer et comprendre la spatialisation intuitive. On peut ainsi comprendre les paramètre et moments cléfs du processus de spat.

**Entrainement de donnée**
Ici on utilise et formate les données afin de réaliser un entrainement. L'objectif est de produire une serie de coordonnées pour un instrument. Cette dernière pourra ensuite être exploité sur le logiciel MaxMSP


A noter : Lorsque vous souhaitez lancer un fichier python, placez vous au sein de l'un des deux dossier (en fonction de ce que vous souhaitez réaliser).
