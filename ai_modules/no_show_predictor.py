import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'no_show_model.pkl')
DATA_PATH  = os.path.join(os.path.dirname(BASE_DIR), 'data', 'historical_data.csv')

FEATURES = [
    'previous_no_shows', 'days_until_appointment',
    'appointment_hour',  'day_of_week', 'age',
    'gender_encoded',    'reminder_sent', 'distance_km'
]

def train_model():
    print("Training no-show prediction model...")
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Training data not found at {DATA_PATH}. Run data/generate_data.py first.")

    df = pd.read_csv(DATA_PATH)
    X  = df[FEATURES]
    y  = df['no_show']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        class_weight='balanced',
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred   = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    print(classification_report(y_test, y_pred))

    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to: {MODEL_PATH}")
    return model


def predict_no_show(patient_features: dict) -> float:
    if not os.path.exists(MODEL_PATH):
        train_model()
    model = joblib.load(MODEL_PATH)
    df    = pd.DataFrame([patient_features])[FEATURES]
    prob  = model.predict_proba(df)[0][1]
    return round(float(prob), 3)


if __name__ == '__main__':
    train_model()
    test_patient = {
        'previous_no_shows'      : 3,
        'days_until_appointment' : 14,
        'appointment_hour'       : 8,
        'day_of_week'            : 5,
        'age'                    : 28,
        'gender_encoded'         : 1,
        'reminder_sent'          : 0,
        'distance_km'            : 20.0
    }
    prob = predict_no_show(test_patient)
    risk = 'HIGH' if prob >= 0.7 else 'MEDIUM' if prob >= 0.4 else 'LOW'
    print(f"\nTest Prediction => No-Show Probability: {prob} | Risk: {risk}")
