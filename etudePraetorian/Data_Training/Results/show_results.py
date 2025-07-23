import sys
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


# Lecture
df = pd.read_csv("resampled_results/dataset_all_value_Hypnose.csv")

# Générer la colonne temps (en secondes)
time = df.index * 20 / 1000  # conversion ms -> s

# Affichage graphique 3D avec couleur évolutive
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# Utilisation de scatter pour la couleur évolutive
sc = ax.scatter(time, df['x'], df['y'], c=time, cmap='viridis', marker='o', label='Prédictions')

ax.set_xlabel("Temps (s)")
ax.set_ylabel("x_pred")
ax.set_zlabel("y_pred")
ax.set_title("Évolution de x et y en fonction du temps")

# Ajout de la barre de couleur
cbar = plt.colorbar(sc, ax=ax, pad=0.1)
cbar.set_label('Temps (s)')

plt.show()