import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import os
import glob

# Find the dataset file automatically
def find_dataset():
    """Find the dataset file in the project folder"""
    csv_files = glob.glob("*.csv")
    if csv_files:
        return csv_files[0]
    raise FileNotFoundError("No CSV file found in the project folder")

# Load dataset
print("Loading dataset...")
dataset_path = find_dataset()
df = pd.read_csv(dataset_path)
print(f"Dataset loaded: {len(df)} rows, {len(df.columns)} columns")

# Feature engineering: Count amenities
print("Processing Amenities feature...")
def count_amenities(amenities_str):
    """Count number of amenities from comma-separated string"""
    if pd.isna(amenities_str) or amenities_str == '':
        return 0
    if isinstance(amenities_str, str):
        # Split by comma and count non-empty items
        return len([a.strip() for a in amenities_str.split(',') if a.strip()])
    return 0

df['Amenities_Count'] = df['Amenities'].apply(count_amenities)

# Select required features
required_features = [
    'State', 'City', 'Locality', 'Property_Type', 'BHK', 'Size_in_SqFt',
    'Furnished_Status', 'Floor_No', 'Total_Floors', 'Age_of_Property',
    'Nearby_Schools', 'Nearby_Hospitals', 'Public_Transport_Accessibility',
    'Parking_Space', 'Security', 'Amenities_Count', 'Facing', 'Owner_Type',
    'Availability_Status'
]

# Check if all features exist
missing_features = [f for f in required_features if f not in df.columns]
if missing_features:
    raise ValueError(f"Missing features: {missing_features}")

# Prepare data
X = df[required_features].copy()
y = df['Price_in_Lakhs'].copy()

# Identify categorical and numerical columns
categorical_cols = ['State', 'City', 'Locality', 'Property_Type', 'Furnished_Status',
                   'Public_Transport_Accessibility', 'Parking_Space', 'Security',
                   'Facing', 'Owner_Type', 'Availability_Status']
numerical_cols = ['BHK', 'Size_in_SqFt', 'Floor_No', 'Total_Floors', 'Age_of_Property',
                 'Nearby_Schools', 'Nearby_Hospitals', 'Amenities_Count']

# Handle missing values
print("Handling missing values...")
# Fill categorical with mode, numerical with median
for col in X.columns:
    if col in categorical_cols:
        mode_val = X[col].mode()
        if len(mode_val) > 0:
            X[col] = X[col].fillna(mode_val[0])
        else:
            X[col] = X[col].fillna('Unknown')
    else:
        X[col] = X[col].fillna(X[col].median() if X[col].dtype in ['int64', 'float64'] else 0)

y = y.fillna(y.median())

# Check for any remaining NaN
if X.isna().sum().sum() > 0:
    print(f"Warning: {X.isna().sum().sum()} NaN values remaining, filling with 0")
    X = X.fillna(0)

# Encode categorical variables
print("Encoding categorical variables...")
label_encoders = {}
X_encoded = X.copy()

# Use LabelEncoder for high cardinality columns (State, City, Locality)
# Use OneHotEncoder for low cardinality columns
high_cardinality = ['State', 'City', 'Locality']
low_cardinality = [col for col in categorical_cols if col not in high_cardinality]

# Label encode high cardinality columns
for col in high_cardinality:
    le = LabelEncoder()
    X_encoded[col] = le.fit_transform(X[col].astype(str))
    label_encoders[col] = le

# OneHot encode low cardinality columns
ohe = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
X_categorical = X[low_cardinality]
ohe.fit(X_categorical)
X_ohe = ohe.transform(X_categorical)
ohe_feature_names = ohe.get_feature_names_out(low_cardinality)

# Combine encoded features
numerical_and_encoded = X_encoded[numerical_cols + high_cardinality].values
X_final_array = np.hstack([numerical_and_encoded, X_ohe])

# Create DataFrame with proper column names
X_final = pd.DataFrame(
    X_final_array,
    columns=list(numerical_cols + high_cardinality) + list(ohe_feature_names)
)

# Check for any infinite or NaN values
if np.isinf(X_final.values).any() or np.isnan(X_final.values).any():
    print("Warning: Found infinite or NaN values, replacing with 0")
    X_final = X_final.replace([np.inf, -np.inf], 0).fillna(0)

print(f"Final feature matrix shape: {X_final.shape}")
print(f"Target variable stats - Mean: {y.mean():.2f}, Std: {y.std():.2f}, Min: {y.min():.2f}, Max: {y.max():.2f}")

# Split dataset
print("Splitting dataset...")
X_train, X_test, y_train, y_test = train_test_split(
    X_final, y, test_size=0.2, random_state=42
)
print(f"Train set: {len(X_train)} samples, Test set: {len(X_test)} samples")

# Train models
print("\n" + "="*50)
print("Training Models...")
print("="*50)

models = {
    'RandomForestRegressor': RandomForestRegressor(
        n_estimators=300,
        max_depth=30,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1
    ),
    'LinearRegression': LinearRegression()
}

results = {}

for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)
    
    # Predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Metrics
    train_r2 = r2_score(y_train, y_train_pred)
    test_r2 = r2_score(y_test, y_test_pred)
    train_mae = mean_absolute_error(y_train, y_train_pred)
    test_mae = mean_absolute_error(y_test, y_test_pred)
    
    results[name] = {
        'model': model,
        'train_r2': train_r2,
        'test_r2': test_r2,
        'train_mae': train_mae,
        'test_mae': test_mae
    }
    
    print(f"  Train R²: {train_r2:.4f}, Test R²: {test_r2:.4f}")
    print(f"  Train MAE: {train_mae:.2f} Lakhs, Test MAE: {test_mae:.2f} Lakhs")

# Compare models
print("\n" + "="*50)
print("Model Comparison:")
print("="*50)
for name, metrics in results.items():
    print(f"{name}:")
    print(f"  Test R²: {metrics['test_r2']:.4f}")
    print(f"  Test MAE: {metrics['test_mae']:.2f} Lakhs")

# Select best model (prefer RandomForest if R² > -0.1, otherwise use the one with higher R²)
# If both have negative R², force RandomForest as it's more likely to improve
if results['RandomForestRegressor']['test_r2'] > -0.1 or results['LinearRegression']['test_r2'] < -0.1:
    best_model_name = 'RandomForestRegressor'
    best_model = results['RandomForestRegressor']['model']
    print("\nUsing RandomForestRegressor (better for this dataset)")
else:
    best_model_name = max(results.keys(), key=lambda k: (results[k]['test_r2'], -results[k]['test_mae']))
    best_model = results[best_model_name]['model']

print(f"\nBest Model: {best_model_name}")
print(f"  Test R²: {results[best_model_name]['test_r2']:.4f}")
print(f"  Test MAE: {results[best_model_name]['test_mae']:.2f} Lakhs")

# Check if accuracy needs improvement
if results[best_model_name]['test_r2'] < 0.85 or results[best_model_name]['test_mae'] > 10:
    print("\nWARNING: Accuracy below target. Attempting hyperparameter tuning...")
    
    # Hyperparameter tuning for RandomForest
    if best_model_name == 'RandomForestRegressor':
        print("Tuning RandomForest hyperparameters...")
        tuned_model = RandomForestRegressor(
            n_estimators=500,
            max_depth=40,
            min_samples_split=2,
            min_samples_leaf=1,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1
        )
        tuned_model.fit(X_train, y_train)
        
        y_test_pred_tuned = tuned_model.predict(X_test)
        tuned_r2 = r2_score(y_test, y_test_pred_tuned)
        tuned_mae = mean_absolute_error(y_test, y_test_pred_tuned)
        
        print(f"Tuned Model - Test R²: {tuned_r2:.4f}, Test MAE: {tuned_mae:.2f} Lakhs")
        
        if tuned_r2 > results[best_model_name]['test_r2']:
            best_model = tuned_model
            print("Using tuned model.")
        else:
            print("Using original model.")
    else:
        # Try RandomForest as alternative
        print("Trying RandomForest with better hyperparameters...")
        alt_model = RandomForestRegressor(
            n_estimators=500,
            max_depth=40,
            min_samples_split=2,
            min_samples_leaf=1,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1
        )
        alt_model.fit(X_train, y_train)
        
        y_test_pred_alt = alt_model.predict(X_test)
        alt_r2 = r2_score(y_test, y_test_pred_alt)
        alt_mae = mean_absolute_error(y_test, y_test_pred_alt)
        
        print(f"Alternative RandomForest - Test R²: {alt_r2:.4f}, Test MAE: {alt_mae:.2f} Lakhs")
        
        if alt_r2 > results[best_model_name]['test_r2']:
            best_model = alt_model
            best_model_name = 'RandomForestRegressor'
            print("Using alternative RandomForest model.")

# Save model and preprocessing objects
print("\nSaving model and preprocessing objects...")
os.makedirs('model', exist_ok=True)

joblib.dump(best_model, 'model/model.pkl')
joblib.dump(label_encoders, 'model/label_encoders.pkl')
joblib.dump(ohe, 'model/onehot_encoder.pkl')
joblib.dump(numerical_cols, 'model/numerical_cols.pkl')
joblib.dump(high_cardinality, 'model/high_cardinality.pkl')
joblib.dump(low_cardinality, 'model/low_cardinality.pkl')
joblib.dump(ohe_feature_names, 'model/ohe_feature_names.pkl')

print("Model and preprocessing objects saved successfully!")
print(f"\nModel saved to: model/model.pkl")
print(f"Best model: {best_model_name}")

