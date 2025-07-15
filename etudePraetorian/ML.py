DATASET_FILE_PATH = "resampled_results/dataset_all_value.csv"
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

def main():
    # Chargement des données
    df = pd.read_csv(DATASET_FILE_PATH)  # Mets ici ton nom de fichier

    # Prétraitement : encoder 'region' (ex: "Start", "Middle", etc.)
    label_encoder = LabelEncoder()
    df['region_encoded'] = label_encoder.fit_transform(df['region'])

    # Sélection des features (X) et cibles (y)
    features = ['time', 'rms', 'region_encoded']
    X = df[features]
    y = df[['x', 'y']]

    # Séparation en train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Normalisation des features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Modèle de régression linéaire multivariée
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)

    # Prédictions
    y_pred = model.predict(X_test_scaled)

    # Évaluation
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("Erreur quadratique moyenne (MSE) :", mse)
    print("Score R² :", r2)

    # Optionnel : afficher les 5 premières prédictions
    print("\nExemples de prédictions vs réels :")
    for i in range(min(5, len(y_test))):
        print(f"Réel: {y_test.iloc[i].values}, Prédit: {y_pred[i]}")
    


if __name__ == "__main__":
    main()