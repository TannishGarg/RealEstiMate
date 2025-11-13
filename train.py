import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from category_encoders import TargetEncoder
from sklearn.preprocessing import OneHotEncoder
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
    'Ready To Move': 'Ready_to_Move',
    'Ready to Move': 'Ready_to_Move',
    'ready to move': 'Ready_to_Move'
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

# Multi-Hot Encoding for Amenities
print("\n3. Processing Amenities feature with Multi-Hot Encoding...")

# Define all possible amenities
AMENITY_TYPES = ['gym', 'garden', 'pool', 'clubhouse', 'playground']

def create_amenity_dummies(amenities_str):
    """Create multi-hot encoded amenities columns"""
    amenity_dict = {}
    if pd.isna(amenities_str) or amenities_str == '' or amenities_str == 'nan':
        # If no amenities, all columns should be 0
        for amenity in AMENITY_TYPES:
            amenity_dict[f'Amenity_{amenity.capitalize()}'] = 0
        return amenity_dict
    
    if isinstance(amenities_str, str):
        # Parse amenities and create binary columns
        amenities_list = [a.strip().lower() for a in amenities_str.split(',') if a.strip()]
        for amenity in AMENITY_TYPES:
            amenity_dict[f'Amenity_{amenity.capitalize()}'] = 1 if amenity in amenities_list else 0
        return amenity_dict
    
    # Default case
    for amenity in AMENITY_TYPES:
        amenity_dict[f'Amenity_{amenity.capitalize()}'] = 0
    return amenity_dict

# Create amenity columns
amenity_dummies = df['Amenities'].apply(create_amenity_dummies).apply(pd.Series)
df = pd.concat([df.drop('Amenities', axis=1), amenity_dummies], axis=1)

# Define feature order (EXACT ORDER for training and prediction)
FEATURE_ORDER = [
    'State', 'City', 'Locality', 'Property_Type', 'BHK', 'Size_in_SqFt',
    'Furnished_Status', 'Floor_No', 'Total_Floors', 'Age_of_Property',
    'Nearby_Schools', 'Nearby_Hospitals', 'Public_Transport_Accessibility',
    'Parking_Space', 'Security', 'Amenity_Gym', 'Amenity_Garden', 'Amenity_Pool',
    'Amenity_Clubhouse', 'Amenity_Playground', 'Facing', 'Owner_Type',
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
                 'Nearby_Schools', 'Nearby_Hospitals', 'Amenity_Gym', 'Amenity_Garden', 
                 'Amenity_Pool', 'Amenity_Clubhouse', 'Amenity_Playground']

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

# Split dataset BEFORE encoding to avoid data leakage
print("\n5. Splitting dataset...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"Train set: {len(X_train)} samples, Test set: {len(X_test)} samples")

# Mixed Encoding Strategy
print("\n6. Applying Mixed Encoding Strategy...")

# Define encoding groups
one_hot_cols = ['City', 'Property_Type', 'Facing', 'Owner_Type']
target_encode_cols = ['Locality']
other_categorical_cols = ['State', 'Furnished_Status', 'Public_Transport_Accessibility', 
                         'Parking_Space', 'Security', 'Availability_Status']

# Initialize encoders
print("  - Initializing encoders...")
one_hot_encoder = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
target_encoder = TargetEncoder(cols=target_encode_cols, smoothing=0.3)

# Fit encoders on TRAINING DATA ONLY
print("  - Fitting encoders on training data...")

# Fit OneHotEncoder
X_train_one_hot = one_hot_encoder.fit_transform(X_train[one_hot_cols])
one_hot_feature_names = one_hot_encoder.get_feature_names_out(one_hot_cols)

# Fit TargetEncoder
X_train_target_encoded = target_encoder.fit_transform(X_train[target_encode_cols], y_train)

# Transform training data
print("  - Transforming training data...")

# One-hot encoded features
X_train_one_hot_df = pd.DataFrame(X_train_one_hot, columns=one_hot_feature_names, index=X_train.index)

# Target encoded features
X_train_target_df = pd.DataFrame(X_train_target_encoded, columns=target_encode_cols, index=X_train.index)

# Other categorical features (keep as is for now, will be handled later)
X_train_other_cat = X_train[other_categorical_cols].copy()

# Numerical features
X_train_numerical = X_train[numerical_cols].copy()

# Combine all training features
X_train_final = pd.concat([
    X_train_numerical,
    X_train_one_hot_df,
    X_train_target_df,
    X_train_other_cat
], axis=1)

# Transform TEST data using fitted encoders
print("  - Transforming test data...")

# One-hot encode test data
X_test_one_hot = one_hot_encoder.transform(X_test[one_hot_cols])
X_test_one_hot_df = pd.DataFrame(X_test_one_hot, columns=one_hot_feature_names, index=X_test.index)

# Target encode test data
X_test_target_encoded = target_encoder.transform(X_test[target_encode_cols])
X_test_target_df = pd.DataFrame(X_test_target_encoded, columns=target_encode_cols, index=X_test.index)

# Other categorical features
X_test_other_cat = X_test[other_categorical_cols].copy()

# Numerical features
X_test_numerical = X_test[numerical_cols].copy()

# Combine all test features
X_test_final = pd.concat([
    X_test_numerical,
    X_test_one_hot_df,
    X_test_target_df,
    X_test_other_cat
], axis=1)

# Convert remaining categorical columns to dummy variables (simple encoding)
for col in other_categorical_cols:
    if col in X_train_final.columns and X_train_final[col].dtype == 'object':
        # Create dummy variables for training
        train_dummies = pd.get_dummies(X_train_final[col], prefix=col, drop_first=True)
        X_train_final = pd.concat([X_train_final.drop(col, axis=1), train_dummies], axis=1)
        
        # Create dummy variables for test (ensuring same columns as train)
        test_dummies = pd.get_dummies(X_test_final[col], prefix=col, drop_first=True)
        # Align test dummies with train dummies
        for dummy_col in train_dummies.columns:
            if dummy_col not in test_dummies.columns:
                test_dummies[dummy_col] = 0
        test_dummies = test_dummies[train_dummies.columns]  # Ensure same order
        X_test_final = pd.concat([X_test_final.drop(col, axis=1), test_dummies], axis=1)

# Final cleanup
print("  - Final cleanup...")
X_train_final = X_train_final.replace([np.inf, -np.inf], 0).fillna(0)
X_test_final = X_test_final.replace([np.inf, -np.inf], 0).fillna(0)

print(f"Final training feature matrix shape: {X_train_final.shape}")
print(f"Final test feature matrix shape: {X_test_final.shape}")
print(f"Target variable stats - Mean: {y.mean():.2f}, Std: {y.std():.2f}, Min: {y.min():.2f}, Max: {y.max():.2f}")

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


model.fit(X_train_final, y_train)

# Evaluate model
print("\n8. Evaluating model...")
y_train_pred = model.predict(X_train_final)
y_test_pred = model.predict(X_test_final)

train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)
train_mae = mean_absolute_error(y_train, y_train_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)

print(f"\nTraining Results:")
print(f"  Train R²: {train_r2:.4f}")
print(f"  Test R²: {test_r2:.4f}")
print(f"  Train MAE: {train_mae:.2f} Lakhs")
print(f"  Test MAE: {test_mae:.2f} Lakhs")

# Save model and preprocessing objects
print("\n9. Saving model and preprocessing objects...")
os.makedirs('model', exist_ok=True)

joblib.dump(model, 'model/model.pkl')
joblib.dump(one_hot_encoder, 'model/one_hot_encoder.pkl')
joblib.dump(target_encoder, 'model/target_encoder.pkl')
joblib.dump(numerical_cols, 'model/numerical_cols.pkl')
joblib.dump(one_hot_cols, 'model/one_hot_cols.pkl')
joblib.dump(target_encode_cols, 'model/target_encode_cols.pkl')
joblib.dump(other_categorical_cols, 'model/other_categorical_cols.pkl')

# Save feature order and column information for reference
joblib.dump(FEATURE_ORDER, 'model/feature_order.pkl')
joblib.dump(X_train_final.columns.tolist(), 'model/final_feature_columns.pkl')

print("\n" + "="*60)
print("Model Training Complete!")
print("="*60)
print(f"Model saved to: model/model.pkl")
print(f"Test R²: {test_r2:.4f}")
print(f"Test MAE: {test_mae:.2f} Lakhs")
print("="*60)
