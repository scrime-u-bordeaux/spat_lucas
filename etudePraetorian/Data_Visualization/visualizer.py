# main.py

import Utils
import audioRMS
import spat
import sys
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

NUM_INSTRUMENTS = 6

def get_num_instruments():
    return NUM_INSTRUMENTS

def usage(argc, argv):
    if argc < 3 or argv[1] not in ("audio", "spat", "mixing"):
        print("Usage: python visualizer.py <mode> <track_index> [<instrument_index>|all]")
        print("Modes: audio, spat, mixing")
        return False, None, None, None, None
    mode = argv[1]
    track_idx = int(argv[2])
    
    instrument_idx = None
    all_instruments = False
    global_mode = False

    if argc == 3:
        global_mode = True
    elif argc >= 4:
        if argv[3] == "all":
            all_instruments = True
        else:
            instrument_idx = int(argv[3])

    return True, mode, track_idx, instrument_idx, all_instruments, global_mode

def main():
    ok, mode, track_idx, instrument_idx, all_instruments, global_mode = usage(len(sys.argv), sys.argv)
    if not ok:
        return

    dataset = []
    # Détermination des indices d'instruments à traiter
    if global_mode or all_instruments:
        instrument_indices = range(NUM_INSTRUMENTS)
    else:
        instrument_indices = [instrument_idx]

    for idx in instrument_indices:
        entry = {"instrument": idx}
        if mode == "audio":
            entry["audio"] = audioRMS.analyse_audio_rms(track_idx, idx + 1)
        elif mode == "spat":
            entry["spat"] = spat.analyse_spat(track_idx, idx + 1, True, True, False)
        elif mode == "mixing":
            entry["audio"] = audioRMS.analyse_audio_rms(track_idx, idx + 1)
            entry["spat"] = spat.analyse_spat(track_idx, idx + 1, False, True, False)
        dataset.append(entry)

    if global_mode:
        if mode == "audio":
            print("Aucune analyse audio pour le mode global disponible.")
        elif mode == "spat":
            # On pourrait faire un traitement global ici si besoin
            pass
        elif mode == "mixing":
            process_mixing_results(
                [d.get("audio") for d in dataset],
                [d.get("spat") for d in dataset]
            )
        return dataset

    if all_instruments:
        if mode == "mixing":
            process_mixing_results(
                [d.get("audio") for d in dataset],
                [d.get("spat") for d in dataset]
            )
        # if mode in ("mixing"):
        #     plot_3d_spat_audio(dataset)
        return dataset

    # Cas d'un seul instrument
    print(f"Analyse pour le morceau {track_idx}, instrument {instrument_idx}")
    if mode == "audio":
        return dataset[0].get("audio")
    elif mode == "spat":
        return dataset[0].get("spat")
    elif mode == "mixing":
        return process_mixing_results(
            dataset[0].get("audio"),
            dataset[0].get("spat")
        )

import matplotlib.pyplot as plt

def process_mixing_results(result_audio, result_spat, line_height=0.8, line_width=0.9):
    """
    Affiche une grille où chaque ligne correspond à un instrument.
    Les bandes de couleurs indiquent les périodes où l'instrument joue.
    Dans chaque case, on affiche la courbe de vitesse de spatialisation.
    Par-dessus tous les instruments, on affiche les segments de régions audio (régions_csv).
    L'axe des abscisses représente le temps (en secondes).
    line_height : hauteur de chaque ligne (axe y)
    line_width : largeur relative des bandes (axe x, 1.0 = pleine largeur)
    """
    import matplotlib.pyplot as plt

    # Si on traite un seul instrument, on convertit en liste pour uniformiser le traitement
    if not isinstance(result_audio, list):
        result_audio = [result_audio]
        result_spat = [result_spat]

    num_instruments = len(result_audio)
    # Récupération des régions audio (régions_csv) depuis le premier instrument (supposé identique pour tous)
    regions = []
    if result_audio and isinstance(result_audio[0], dict):
        regions = result_audio[0].get("regions", [])

    # Affichage d'une ligne supplémentaire dédiée aux régions audio (comme un "instrument" en plus)
    num_rows = num_instruments + 1
    fig, ax = plt.subplots(num_rows, 1, figsize=(12, line_height * num_rows), sharex=True)
    if num_rows == 1:
        ax = [ax]

    # Ligne des régions audio (tout en bas)
    region_ax = ax[-1]
    region_ax.set_ylabel("Région")
    region_ax.set_yticks([])

    num_regions = len(regions)
    # Palette de couleurs pour différencier les régions
    region_colors = plt.cm.get_cmap('tab20', num_regions)
    for i, region in enumerate(regions):
        t_start = region.get("start", None)
        # t_end est égal au t_start du prochain, ou None si dernier (donc jusqu'à la fin)
        if i < num_regions - 1:
            t_end = regions[i + 1].get("start", None)
        else:
            # Si dernier, on prend le max du temps des données spatiales/audio
            max_time = 0
            for audio, spat in zip(result_audio, result_spat):
                if audio and "joue_periods_filtrees" in audio and audio["joue_periods_filtrees"]:
                    max_time = max(max_time, max(period[1] for period in audio["joue_periods_filtrees"]))
                if spat and "real_times" in spat and spat["real_times"]:
                    max_time = max(max_time, max(spat["real_times"]))
            t_end = max_time if max_time > t_start else t_start + 1  # fallback
        label = region.get("label", "")
        color = region_colors(i)
        if t_start is not None and t_end is not None:
            region_ax.axvspan(
                t_start, t_end,
                color=color, alpha=0.25, ymin=0, ymax=1
            )
            # Afficher les 3 premières lettres du label au centre de la bande
            if label:
                region_ax.text(
                    (t_start + t_end) / 2, 0.5,
                    label[:3], ha='center', va='center', fontsize=9, color='black', alpha=0.85,
                    transform=region_ax.get_xaxis_transform()
                )

    # Adapter la suite du code pour utiliser ax[:-1] pour les instruments
    for idx, (audio, spat) in enumerate(zip(result_audio, result_spat)):
        joue_periods = audio.get('joue_periods_filtrees', [])
        real_times = np.array(spat.get('real_times', []))
        vitesse = np.array(spat.get('vitesse', []))
        instrument_label = Utils.get_instrument_name(idx + 1)

        # Affichage des bandes de couleur pour les périodes où l'instrument joue
        for period in joue_periods:
            t_start, t_end = period
            ax[idx].axvspan(t_start, t_end, color='tab:green', alpha=0.1, ymin=0.1, ymax=0.9)

        # Affichage de la courbe de vitesse (une seule courbe, sans distinction)
        # Correction: on ajuste la longueur de 'vitesse' pour qu'elle corresponde à 'real_times'
        if len(vitesse) == len(real_times) - 1:
            vitesse = np.insert(vitesse, 0, 0)
        if len(real_times) > 1 and len(vitesse) == len(real_times):
            ax[idx].plot(
                real_times,
                vitesse,
                color='tab:blue',
                linewidth=1.0,
            )

        ax[idx].set_ylabel(instrument_label)
        ax[idx].set_yticks([])

    region_ax.set_xlabel("Temps (s)")
    plt.suptitle("Périodes de jeu, vitesse de spatialisation et régions audio")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

    # Sauvegarde de la figure dans un fichier image au lieu d'afficher à l'écran
    output_path = f"mixing_results_{id(result_audio)}.png"
    plt.savefig(output_path)
    print(f"Figure sauvegardée dans {output_path}")
    plt.close(fig)







# import matplotlib.pyplot as plt
# from Utils import get_instrument_name, get_regions_from_csv
# def plot_3d_spat_audio(dataset, save_path=None, show=True):
#     """
#     Affiche un graphique 3D montrant la vitesse de spatialisation de chaque instrument au cours du temps,
#     ainsi que des bandes de couleurs discrètes en arrière-plan indiquant si l'instrument joue ou non.
#     Peut sauvegarder la figure dans un fichier si save_path est fourni.
#     """
#     if save_path is None:
#         save_path = "spat_audio_3d_plot.png"

#     fig = plt.figure(figsize=(12, 8))
#     ax = fig.add_subplot(111, projection='3d')

#     num_instruments = len(dataset)
#     colors = plt.cm.get_cmap('tab10', num_instruments)

#     instrument_names = []
#     max_speed = 0  # Pour ajuster l'échelle verticale

#     # Première passe pour trouver la vitesse max (pour normaliser l'échelle)
#     for idx, data in enumerate(dataset):
#         spat = data.get("spat", {})
#         x_coords = spat.get('x_coords', [])
#         y_coords = spat.get('y_coords', [])
#         real_times = spat.get('real_times', [])
#         if len(x_coords) > 1 and len(y_coords) > 1:
#             x_coords = np.array(x_coords)
#             y_coords = np.array(y_coords)
#             real_times = np.array(real_times)
#             dx = np.diff(x_coords)
#             dy = np.diff(y_coords)
#             dt = np.diff(real_times)
#             speed = np.sqrt(dx**2 + dy**2) / np.where(dt == 0, 1e-6, dt)
#             speed = np.insert(speed, 0, 0)
#             if np.max(speed) > max_speed:
#                 max_speed = np.max(speed)

#     # Facteur pour réduire l'échelle verticale (par exemple, 0.3)
#     scale_factor = 0.3
#     scaled_max_speed = max_speed * scale_factor if max_speed > 0 else 1

#     for idx, data in enumerate(dataset):
#         # Récupération des données
#         audio = data.get("audio", {})
#         spat = data.get("spat", {})

#         instrument_idx = data.get("instrument", idx)
#         instrument_name = get_instrument_name(instrument_idx + 1)
#         instrument_names.append(instrument_name)

#         joue_periods = audio.get('joue_periods_filtrees', [])
#         real_times = spat.get('real_times', [])
#         x_coords = spat.get('x_coords', [])
#         y_coords = spat.get('y_coords', [])

#         # Calcul de la vitesse de spatialisation (différence euclidienne entre positions successives)
#         if len(x_coords) > 1 and len(y_coords) > 1:
#             x_coords = np.array(x_coords)
#             y_coords = np.array(y_coords)
#             real_times = np.array(real_times)
#             dx = np.diff(x_coords)
#             dy = np.diff(y_coords)
#             dt = np.diff(real_times)
#             speed = np.sqrt(dx**2 + dy**2) / np.where(dt == 0, 1e-6, dt)
#             speed = np.insert(speed, 0, 0)
#             # Réduction de l'échelle verticale
#             speed = speed * scale_factor
#         else:
#             speed = np.zeros_like(real_times)

#         # Affichage des bandes de couleur pour les périodes où l'instrument joue (en arrière-plan, z très bas)
#         for period in joue_periods:
#             t_start, t_end = period
#             # On place la bande très bas sur l'axe z pour ne pas gêner la courbe
#             ax.bar3d(
#                 x=t_start,
#                 y=idx-0.4,
#                 z=-scaled_max_speed * 0.15,  # en retrait sous la courbe
#                 dx=t_end-t_start,
#                 dy=0.8,
#                 dz=scaled_max_speed * 0.1,   # bande très fine
#                 color=colors(idx, 0.15),
#                 alpha=0.18,
#                 shade=False
#             )

#         # Tracer la courbe de vitesse de spatialisation
#         ax.plot(real_times, [idx]*len(real_times), speed, label=instrument_name, color=colors(idx), linewidth=2.2)

#     ax.set_xlabel('Temps (s)')
#     ax.set_ylabel('Instrument')
#     ax.set_zlabel('Vitesse de spatialisation')
#     ax.set_yticks(range(num_instruments))
#     ax.set_yticklabels(instrument_names)
#     ax.set_zlim(-scaled_max_speed * 0.2, scaled_max_speed * 1.2)
#     ax.legend()
#     plt.title("Vitesse de spatialisation et périodes de jeu des instruments")
#     plt.tight_layout()

#     if save_path:
#         plt.savefig(save_path)
#         print(f"Figure sauvegardée dans {save_path}")
#     if show:
#         plt.show()
#     plt.close(fig)



if __name__ == "__main__":
    main()
