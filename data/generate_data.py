import pandas as pd
import numpy as np
import os

np.random.seed(42)
N = 1200

data = {
    'previous_no_shows'      : np.random.randint(0, 7, N),
    'days_until_appointment' : np.random.randint(1, 31, N),
    'appointment_hour'       : np.random.randint(8, 18, N),
    'day_of_week'            : np.random.randint(0, 7, N),
    'age'                    : np.random.randint(18, 80, N),
    'gender_encoded'         : np.random.randint(0, 2, N),
    'reminder_sent'          : np.random.randint(0, 2, N),
    'distance_km'            : np.round(np.random.uniform(1, 35, N), 1),
}

df = pd.DataFrame(data)

prob = (
    0.15 * df['previous_no_shows'] +
    0.02 * df['days_until_appointment'] +
    0.03 * (df['appointment_hour'] < 9).astype(int) +
    0.05 * df['day_of_week'].isin([5, 6]).astype(int) -
    0.12 * df['reminder_sent'] +
    0.004 * df['distance_km']
)

noise = np.random.normal(0, 0.08, N)
df['no_show'] = ((prob + noise) > 0.30).astype(int)

output_path = os.path.join(os.path.dirname(__file__), 'historical_data.csv')
df.to_csv(output_path, index=False)
print(f"Dataset generated: {N} records")
print(f"No-show rate: {df['no_show'].mean() * 100:.1f}%")
print(f"Saved to: {output_path}")
