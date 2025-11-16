import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from category_encoders import TargetEncoder
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import os

print("="*60)
print("Indian House Price Prediction - Model Training")
print("="*60)

# Load dataset
print("\n1. Loading dataset...")
df = pd.read_csv('data.csv')
print(f"Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
print(f"Columns: {df.columns.tolist()}")

# Data Cleaning and Normalization
print("\n2. Normalizing text formatting...")

# Normalize Availability_Status
df['Availability_Status'] = df['Availability_Status'].str.strip()
df['Availability_Status'] = df['Availability_Status'].replace({
    'Ready To Move': 'Ready_To_Move',
    'Ready to Move': 'Ready_To_Move',
    'ready to move': 'Ready_To_Move'
})

# Normalize Furnished_Status
df['Furnished_Status'] = df['Furnished_Status'].str.strip()
df['Furnished_Status'] = df['Furnished_Status'].replace({
    'Semi-Furnished': 'Semi_Furnished',
    'Semi-furnished': 'Semi_Furnished',
    'semi-furnished': 'Semi_Furnished',
    'semi furnished': 'Semi_Furnished'
})

# Normalize yes/no values to Yes/No
for col in ['Parking_Space', 'Security']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.lower()
        df[col] = df[col].replace({'yes': 'Yes', 'no': 'No', 'y': 'Yes', 'n': 'No'})

# Trim whitespaces from all string columns
string_cols = df.select_dtypes(include=['object']).columns
for col in string_cols:
    df[col] = df[col].astype(str).str.strip()

print("Text normalization completed")

# Feature Engineering: Count amenities
print("\n3. Processing Amenities feature...")
def count_amenities(amenities_str):
    """Count number of amenities from comma-separated string"""
    if pd.isna(amenities_str) or amenities_str == '' or amenities_str == 'nan':
        return 0
    if isinstance(amenities_str, str):
        return len([a.strip() for a in amenities_str.split(',') if a.strip()])
    return 0

df['Amenities'] = df['Amenities'].apply(count_amenities)

# Define feature order (EXACT ORDER for training and prediction)
FEATURE_ORDER = [
    'State', 'City', 'Locality', 'Property_Type', 'BHK', 'Size_in_SqFt',
    'Furnished_Status', 'Floor_No', 'Total_Floors', 'Age_of_Property',
    'Nearby_Schools', 'Nearby_Hospitals', 'Public_Transport_Accessibility',
    'Parking_Space', 'Security', 'Amenities', 'Facing', 'Owner_Type',
    'Availability_Status'
]

# Verify all features exist
missing_features = [f for f in FEATURE_ORDER if f not in df.columns]
if missing_features:
    raise ValueError(f"Missing features in dataset: {missing_features}")

print(f"Using {len(FEATURE_ORDER)} features in exact order")

# Prepare data
X = df[FEATURE_ORDER].copy()
y = df['Price_in_Lakhs'].copy()

# Identify categorical and numerical columns
categorical_cols = ['State', 'City', 'Locality', 'Property_Type', 'Furnished_Status',
                   'Public_Transport_Accessibility', 'Parking_Space', 'Security',
                   'Facing', 'Owner_Type', 'Availability_Status']
numerical_cols = ['BHK', 'Size_in_SqFt', 'Floor_No', 'Total_Floors', 'Age_of_Property',
                 'Nearby_Schools', 'Nearby_Hospitals', 'Amenities']

print(f"Categorical features: {len(categorical_cols)}")
print(f"Numerical features: {len(numerical_cols)}")

# Handle missing values
print("\n4. Handling missing values...")
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

# Encode categorical variables using TargetEncoder
print("\n5. Encoding categorical variables with TargetEncoder...")

# Define categorical columns for TargetEncoder
cat_cols = [
    'State', 'City', 'Locality', 'Property_Type', 'Furnished_Status',
    'Public_Transport_Accessibility', 'Parking_Space', 'Security',
    'Facing', 'Owner_Type', 'Availability_Status'
]

# Initialize and fit TargetEncoder
encoder = TargetEncoder(cols=cat_cols, smoothing=0.3)
X_encoded = encoder.fit_transform(X, y)

# TargetEncoder already handles all columns, so X_encoded is our final dataset
X_final = X_encoded.copy()

# Check for any infinite or NaN values
if np.isinf(X_final.values).any() or np.isnan(X_final.values).any():
    print("Warning: Found infinite or NaN values, replacing with 0")
    X_final = X_final.replace([np.inf, -np.inf], 0).fillna(0)

print(f"Final feature matrix shape: {X_final.shape}")
print(f"Target variable stats - Mean: {y.mean():.2f}, Std: {y.std():.2f}, Min: {y.min():.2f}, Max: {y.max():.2f}")

# Split dataset
print("\n6. Splitting dataset...")
X_train, X_test, y_train, y_test = train_test_split(
    X_final, y, test_size=0.2, random_state=42
)
print(f"Train set: {len(X_train)} samples, Test set: {len(X_test)} samples")

# Train model
print("\n7. Training XGBRegressor...")
model = XGBRegressor(
    n_estimators=2000,
    learning_rate=0.015,
    max_depth=12,
    min_child_weight=1,
    subsample=0.85,
    colsample_bytree=0.85,
    gamma=0.2,
    reg_alpha=2,
    reg_lambda=3,
    objective='reg:squarederror',
    tree_method="hist",
    max_bin=256,
    random_state=42
)


model.fit(X_train, y_train)

# Evaluate model
print("\n8. Evaluating model...")
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)
train_mae = mean_absolute_error(y_train, y_train_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)

print(f"\nTraining Results:")
print(f"  Train R²: {train_r2:.4f}")
print(f"  Test R²: {test_r2:.4f}")
print(f"  Train MAE: {train_mae:.2f} Lakhs")
print(f"  Test MAE: {test_mae:.2f} Lakhs")


# -------------------------
# 10. SHAP Analysis
# -------------------------
print("\n10. Running SHAP Analysis...")

import shap
# Only sample 2000 rows if dataset is large (prevents slow computation)
sample_size = min(2000, len(X_train))
X_sample = X_train.sample(sample_size, random_state=42)
# Create SHAP explainer for XGBoost
explainer = shap.TreeExplainer(model)
# Compute SHAP values
shap_values = explainer.shap_values(X_sample)
print("Generating SHAP summary plot...")
# Display SHAP plot
shap.summary_plot(shap_values, X_sample, show=True)
print("SHAP analysis completed.")


# Save model and preprocessing objects
print("\n9. Saving model and preprocessing objects...")
os.makedirs('model', exist_ok=True)

joblib.dump(model, 'model/model.pkl')
joblib.dump(encoder, 'model/target_encoder.pkl')
joblib.dump(numerical_cols, 'model/numerical_cols.pkl')
joblib.dump(cat_cols, 'model/categorical_cols.pkl')

# Save feature order for reference
joblib.dump(FEATURE_ORDER, 'model/feature_order.pkl')

print("\n" + "="*60)
print("Model Training Complete!")
print("="*60)
print(f"Model saved to: model/model.pkl")
print(f"Test R²: {test_r2:.4f}")
print(f"Test MAE: {test_mae:.2f} Lakhs")
print("="*60)
