import os
import sys
from getData import process_track
import pandas as pd
import Utils

if len(sys.argv) < 2:
    print("Usage: python audioRMS.py <track_name> <instrument_name>")
    sys.exit(1)

track_idx = int(sys.argv[1])

if len(sys.argv) >= 3:
    instrument_idx = int(sys.argv[2])
    all_instruments = False
else:
    instrument_idx = None
    all_instruments = True

result = process_track(
    instrument_idx=instrument_idx,
    selected_num_track=track_idx,
    all_instruments=all_instruments
)



track_name = result["track_name"]
instrument_name = result["instrument_name"]
# output_paths = result["output_paths"]
result_data = result["result"]
result_data_resampled = result["resampled_result"]
total_duration = result["total_duration"]
regions = result["regions"]





## ================== AFFICHAGE SPATIALISATION ================== ##

import numpy as np
import matplotlib.pyplot as plt
import re
import Utils

# Génération du graphique avec couleur dépendant du temps

# On récupère les temps relatifs normalisés (entre 0 et 1) ainsi que les coordonnées x et y
times_norm = [coord[0] for coord in result_data]
x_coords = [coord[1] for coord in result_data]
y_coords = [coord[2] for coord in result_data]

region_names = [m["name"] for m in regions[:-1]]
region_timecodes = [(regions[i]["start"], regions[i+1]["start"]) for i in range(len(regions)-1)]
region_colors = ['red', 'orange', 'green', 'blue', 'purple', 'brown', 'pink', 'cyan', 'olive']

real_times = [coord[0] * total_duration for coord in result_data]

# Préparer le dossier de sortie
output_dir = os.path.join("Results", "spat", track_name, instrument_name)
os.makedirs(output_dir, exist_ok=True)

def print_positions():

    

    
    
    positions_dir = os.path.join(output_dir, "positions")
    os.makedirs(positions_dir, exist_ok=True)

    for i, (region_name, (start_time, end_time)) in enumerate(zip(region_names, region_timecodes)):
        plt.figure(figsize=(5, 5))
        region_indices = [j for j, t in enumerate(real_times) if start_time <= t < end_time]
        region_x = [x_coords[j] for j in region_indices]
        region_y = [y_coords[j] for j in region_indices]
        plt.scatter(region_x, region_y, c=region_colors[i % len(region_colors)], alpha=0.8, edgecolors='k', label=region_name)
        plt.title(f'{instrument_name}\n"{track_name}"\n{region_name}\n{start_time:.2f}s - {end_time:.2f}s')
        plt.xlabel('Coordonnée X')
        plt.ylabel('Coordonnée Y')
        plt.grid(True)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.xlim(-5, 5)
        plt.ylim(-5, 5)
        plt.legend()
        plt.tight_layout()
        # Sanitize region_name for filename
        safe_region_name = re.sub(r'[\\/*?:"<>|]', "_", region_name).strip().replace(" ", "_")
        output_path = os.path.join(positions_dir, f"{instrument_name}_{track_name}_{safe_region_name}.png")
        if not os.path.exists(output_path):
            plt.savefig(output_path)
            print(f"Figure enregistrée dans : {output_path}")
        plt.close()

if not all_instruments:
    print_positions()

## =============== HEATMAP (UN ou TOUS LES INSTRUMENTS) =============== ##


def generate_heatmap(resampled_data, track_name, instrument_name, output_dir="Results/spat"):
    """
    Génère une heatmap des coordonnées x/y issues de resampled_result.
    
    Parameters:
        resampled_data (list of [x, y]): Données resamplées.
        track_name (str): Nom de la piste.
        instrument_name (str): Nom de l'instrument ou "ALL".
        output_dir (str): Répertoire de sortie racine.
    """
    if not resampled_data:
        print("Aucune donnée pour générer la heatmap.")
        return

    # Séparer les coordonnées
    x_coords = [x for x, _ in resampled_data]
    y_coords = [y for _, y in resampled_data]

    # # Sauvegarder les données resamplées dans un fichier texte pour inspection
    # resampled_path = os.path.join(output_dir, f"resampled_{instrument_name}_{track_name}.txt")
    # with open(resampled_path, "w", encoding="utf-8") as f:
    #     for x, y in resampled_data:
    #         f.write(f"{x}\t{y}\n")
    # print(f"Données resamplées enregistrées dans : {resampled_path}")

    # Taille et résolution de la heatmap
    figsize = (6, 6) if instrument_name == "ALL" else (5, 5)
    heatmap_size = 20 if instrument_name == "ALL" else 10

    # Création de la figure
    plt.figure(figsize=figsize)
    heatmap, xedges, yedges = np.histogram2d(
        x_coords, y_coords, bins=heatmap_size, range=[[-5, 5], [-5, 5]]
    )
    plt.imshow(
        heatmap.T, cmap='hot', origin='lower',
        extent=[-5, 5, -5, 5], aspect='auto'
    )
    plt.colorbar(label='Densité')

    # Titre, labels
    titre = f'Heatmap globale {instrument_name}' if instrument_name != "ALL" else 'Heatmap ALL INSTRUMENTS'
    plt.title(f'{titre}\n"{track_name}"')
    plt.xlabel('Coordonnée X')
    plt.ylabel('Coordonnée Y')
    plt.grid(False)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    plt.tight_layout()

    # Dossier de sortie

    heatmap_path = os.path.join(output_dir, f"heatmap_{instrument_name}_{track_name}.png")

    # Sauvegarde avec gestion de doublons (ajout d'un numéro si le fichier existe déjà)
    base, ext = os.path.splitext(heatmap_path)
    save_path = heatmap_path
    count = 1
    while os.path.exists(save_path):
        save_path = f"{base} ({count}){ext}"
        count += 1
    plt.savefig(save_path)
    print(f"Heatmap enregistrée dans : {save_path}")
    plt.close()

generate_heatmap(result_data_resampled, track_name, instrument_name, output_dir)

## =============== FIN HEATMAP (UN ou TOUS LES INSTRUMENTS) =============== ##

## =================== VITESSE SPAT ================== ##

if not all_instruments:
    x_coords_np = np.array(x_coords)
    y_coords_np = np.array(y_coords)
    real_times_np = np.array(real_times)

    dx = np.diff(x_coords_np)
    dy = np.diff(y_coords_np)
    dt = np.diff(real_times_np)
    dt[dt == 0] = 1e-8

    vitesse = np.sqrt(dx**2 + dy**2) / dt
    temps_milieu = (real_times_np[:-1] + real_times_np[1:]) / 2

    output_path = os.path.join(output_dir, f"vitesse_{instrument_name}_{track_name}.png")
    print(f"Enregistrement de la vitesse spatiale dans : {output_path}")

    plt.figure(figsize=(12, 5))
    plt.plot(temps_milieu, vitesse, color='blue', label='Vitesse instantanée')
    plt.xlabel('Temps (s)')
    plt.ylabel('Vitesse (u/s)')
    plt.title(f"Vitesse de déplacement en fonction du temps\n{instrument_name} - \"{track_name}\"")
    plt.grid(True)

    for i, (region_name, (start_time, end_time)) in enumerate(zip(region_names, region_timecodes)):
        plt.axvspan(start_time, end_time, color=region_colors[i % len(region_colors)], alpha=0.08)
        plt.axvline(start_time, color=region_colors[i % len(region_colors)], linestyle='--', alpha=0.7)
        ylim = plt.ylim()
        y_base = ylim[1] * 0.95
        y_offset = (ylim[1] - ylim[0]) * 0.05
        y_text = y_base - (i % 2) * y_offset
        plt.text((start_time + end_time) / 2, y_text, region_name[0:3], color=region_colors[i % len(region_colors)],
                 ha='center', va='top', fontsize=10, alpha=0.8, rotation=0)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

## =================== FIN VITESSE SPAT ================== ##


## ================== FIN AFFICHAGE SPATIALISATION ================== ##