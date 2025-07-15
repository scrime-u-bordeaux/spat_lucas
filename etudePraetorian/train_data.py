import os
import pandas as pd

COLUMN_DATA_NAME = { "REGIONS", "RMS" }
RESULT_DATA_NAME = "SPAT" 

def load_resampled_data():

    RESAMPLE_DIR = os.path.join(os.path.dirname(__file__), "resampled_results")

    if not os.path.exists(RESAMPLE_DIR):
        raise FileNotFoundError(f"Le répertoire {RESAMPLE_DIR} n'existe pas.")

    resampled_files = [f for f in os.listdir(RESAMPLE_DIR) if f.endswith('.txt') and f.startswith("resampled_")]
    resampled_data = {}

    for filename in resampled_files:
        file_path = os.path.join(RESAMPLE_DIR, filename)
        data = pd.read_csv(file_path, header=None)
        resampled_data[filename] = data

    return resampled_data
    

def main():
    return

if __name__ == "__main__":
    main()

