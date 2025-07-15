import re
import os
import pandas as pd

indexInstrument = {
    0: "Sample",
    1: "Voc 1",
    2: "Voc 2",
    3: "Guitare",
    4: "Basse",
    5: "BatterieG",
    6: "BatterieD",
}

indexTitre = {
    1: "APOSTAT",
    2: "ECRAN DE FUMEE",
    3: "L'ENNEMI",
    4: "HYPNOSE",
    5: "COMMUNION",
    6: "FACE AUX GEANTS",
    7: "NOUVEAU DIABLE",
    8: "BALLADE ENTRE LES MINES",
    9: "TEMPS MORT",
}

# Fonction pour convertir un timecode en secondes
def timecode_to_seconds(tc):
    tc_str = str(tc)
    # Pattern timecode classique
    match = re.match(r"(\d+):(\d+):(\d+):(\d+)", tc_str)
    if match:
        h, m, s, f = map(int, match.groups())
        fps = 25
        return h * 3600 + m * 60 + s + f / fps
    # Pattern nombre à 3 décimales (ex: 12.345)
    match_decimal = re.match(r"(\d+)\.(\d{3})", tc_str)
    if match_decimal:
        sec = int(match_decimal.group(1))
        ms = int(match_decimal.group(2))
        return sec + ms / 1000
    return 0.0

def get_regions_from_name(track_name_file):
    print(f"Récupération des régions audio pour le fichier : {track_name_file}")
    csv_audio_path = f"Audio/{track_name_file}.csv"
    regions = []
    if os.path.exists(csv_audio_path):
        df_audio_csv = pd.read_csv(csv_audio_path)
        for _, row in df_audio_csv.iterrows():
            start_sec = timecode_to_seconds(row["Start"])
            region = {"name": row["Name"], "start": start_sec}
            regions.append(region)
    else:
        print(f"Fichier CSV non trouvé : {csv_audio_path}")
    return sorted(regions, key=lambda x: x["start"])
        
def get_instrument_name(index):
    try:
        idx = int(index)
    except (ValueError, TypeError):
        return "Inconnu"
    return indexInstrument.get(idx, "Inconnu")


def get_track_name(index):
    try:
        idx = int(index)
    except (ValueError, TypeError):
        return "Inconnu"
    return indexTitre.get(idx, "Inconnu")



