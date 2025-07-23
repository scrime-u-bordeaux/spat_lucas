import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from Data_Visualization.getData import process_track
from scipy.io import wavfile
import warnings

def compute_rms(data_instr, rate, window_sec=0.01, alpha=0.2):
    window_size = int(rate * window_sec)
    num_windows = int(len(data_instr) / window_size)
    rms_values = []
    for i in range(num_windows):
        start = i * window_size
        end = start + window_size
        segment = data_instr[start:end]
        if len(segment) == 0:
            continue
        rms = np.sqrt(np.mean(segment.astype(np.float64) ** 2))
        if rms_values:
            rms = alpha * rms + (1 - alpha) * rms_values[-1]
        rms_values.append(rms)
    return np.array(rms_values), window_sec

def normalize_rms(rms_values, scale=10):
    rms_max = np.max(rms_values)
    if rms_max > 0:
        return rms_values / rms_max * scale
    else:
        return rms_values

def detect_periods(rms_values_norm, window_sec, seuil_rms=1, seuil_temps_non_joue=2, seuil_temps_joue=2):
    joue = rms_values_norm > seuil_rms
    non_joue_periods = []
    start_idx = None
    for idx, val in enumerate(joue):
        if not val and start_idx is None:
            start_idx = idx
        elif val and start_idx is not None:
            duration = (idx - start_idx) * window_sec
            if duration >= seuil_temps_non_joue:
                non_joue_periods.append((start_idx * window_sec, idx * window_sec))
            start_idx = None
    if start_idx is not None:
        duration = (len(joue) - start_idx) * window_sec
        if duration >= seuil_temps_non_joue:
            non_joue_periods.append((start_idx * window_sec, len(joue) * window_sec))
    joue_periods = []
    prev_end = 0.0
    for start, end in non_joue_periods:
        if start > prev_end:
            joue_periods.append((prev_end, start))
        prev_end = end
    if prev_end < len(joue) * window_sec:
        joue_periods.append((prev_end, len(joue) * window_sec))
    joue_periods_filtrees = []
    joue_ponctuel = []
    for start, end in joue_periods:
        if (end - start) >= seuil_temps_joue:
            joue_periods_filtrees.append((start, end))
        else:
            joue_ponctuel.append((start, end))
    return joue_periods_filtrees, joue_ponctuel, non_joue_periods

def plot_rms(rms_values_norm, window_sec, joue_periods_filtrees, regions, instrument_name, track_name, output_dir):
    plt.figure(figsize=(10, 4))
    plt.plot(np.arange(len(rms_values_norm)) * window_sec, rms_values_norm, label='RMS Canal 1 (normalisé)')
    for (start, end) in joue_periods_filtrees:
        plt.axvspan(start, end, color='green', alpha=0.2, label='Instrument joue' if 'Instrument joue' not in plt.gca().get_legend_handles_labels()[1] else "")
    for region in regions:
        name = region["name"]
        color = 'purple' if ("Break" in name or "Punch" in name) else 'red'
        plt.axvline(region["start"], color=color, linestyle='--', alpha=0.7)
        plt.text(region["start"], plt.ylim()[1]*0.95, region["name"][0:3], color=color, ha='left', va='top', fontsize=9, rotation=90)
    plt.xlabel('Temps (s)')
    plt.ylabel('RMS (normalisé)')
    plt.title(f"RMS {instrument_name} - \"{track_name}\" ")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"rms_{instrument_name}_{track_name}.png")
    plt.savefig(output_path)
    plt.close()
    return output_path

def usage(track_idx, instrument_idx):
    print(f"Usage: python {sys.argv[0]} <track_index> <instrument_index>")
    print(f"Example: python {sys.argv[0]} {track_idx} {instrument_idx}")
    sys.exit(1)

def analyse_audio_rms(track_idx, instrument_idx):
    if track_idx < 0 or instrument_idx < 0:
        usage(track_idx, instrument_idx)
    result = process_track(
        instrument_idx=instrument_idx,
        selected_num_track=track_idx,
    )
    track_name = result["track_name"]
    instrument_name = result["instrument_name"]
    regions = result["regions"]
    fname = f"Audio/{track_name}.wav"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rate, data = wavfile.read(fname)
    channel_idx = instrument_idx + 1  # L'audio comporte le chan "clic"
    data_instr = data[:, channel_idx]
    rms_values, window_sec = compute_rms(data_instr, rate)
    rms_values_norm = normalize_rms(rms_values)
    joue_periods_filtrees, joue_ponctuel, non_joue_periods = detect_periods(rms_values_norm, window_sec)
    output_dir = os.path.join("Results", "rms", track_name)
    output_path = plot_rms(
        rms_values_norm, window_sec, joue_periods_filtrees, regions, instrument_name, track_name, output_dir
    )
    print(f"figure enregistrée dans : {output_path}")
    return {
        "track_name": track_name,
        "instrument_name": instrument_name,
        "output_path": output_path,
        "rms_values": rms_values,
        "rms_values_norm": rms_values_norm,
        "window_sec": window_sec,
        "joue_periods_filtrees": joue_periods_filtrees,
        "joue_ponctuel": joue_ponctuel,
        "non_joue_periods": non_joue_periods,
        "regions": regions,
        "rate": rate,
    }

if __name__ == "__main__":
    analyse_audio_rms(3, 9)
    