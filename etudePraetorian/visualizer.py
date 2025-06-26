# main.py

import audioRMS
import sys


def usage(argc, argv):
    print("Usage: python visualizer.py <mode> <track_index> [<instrument_index>]")
    print("Modes: audio, spat")
    if argc < 2 or argv[1] not in ("audio", "spat"):
        return False, None, None, None
    mode = argv[1]
    if argc < 3:
        return False, None, None, None
    track_idx = int(argv[2])
    instrument_idx = None
    if mode == "audio":
        if argc < 4:
            print("For audio mode, provide <track_index> <instrument_index>")
            return False, None, None, None
        instrument_idx = int(argv[3])
    return True, mode, track_idx, instrument_idx

def main():
    ok, mode, track_idx, instrument_idx = usage(len(sys.argv), sys.argv)
    if not ok:
        return
    if mode == "audio":
        result_audio = audioRMS.analyse_audio_rms(track_idx, instrument_idx)
    # elif mode == "spat":
    #     result = spat.analyse_spat(track_idx)
    # Récupère toutes les données audio utiles pour corrélation future avec la spat
    joue_periods = result_audio.get('joue_periods_filtrees')
    joue_ponctuel = result_audio.get('joue_ponctuel')
    track_name = result_audio.get("track_name")
    instrument_name = result_audio.get("instrument_name")

    print(f"Track: {track_name}, Instrument: {instrument_name}")
    print(f"Joue Periods: {joue_periods}")
    print(f"Joue Ponctuel: {joue_ponctuel}")
    # Ajoutez d'autres champs pertinents selon la structure de result_audio

if __name__ == "__main__":
    main()