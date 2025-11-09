import pandas as pd
import numpy as np
import joblib
import os

def count_amenities(amenities_str):
    """Count number of amenities from comma-separated string"""
    if pd.isna(amenities_str) or amenities_str == '':
        return 0
    if isinstance(amenities_str, str):
        return len([a.strip() for a in amenities_str.split(',') if a.strip()])
    return 0

def preprocess_input(data_dict):
    """
    Preprocess user input to match training data format
    
    Args:
        data_dict: Dictionary with user input features
    
    Returns:
        Preprocessed feature array ready for model prediction
    """
    # Load preprocessing objects
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'model')
    
    label_encoders = joblib.load(os.path.join(model_dir, 'label_encoders.pkl'))
    ohe = joblib.load(os.path.join(model_dir, 'onehot_encoder.pkl'))
    numerical_cols = joblib.load(os.path.join(model_dir, 'numerical_cols.pkl'))
    high_cardinality = joblib.load(os.path.join(model_dir, 'high_cardinality.pkl'))
    low_cardinality = joblib.load(os.path.join(model_dir, 'low_cardinality.pkl'))
    
    # Process Amenities
    if 'Amenities' in data_dict:
        data_dict['Amenities_Count'] = count_amenities(data_dict['Amenities'])
    elif 'Amenities_Count' not in data_dict:
        data_dict['Amenities_Count'] = 0
    
    # Create DataFrame with all required columns
    all_cols = numerical_cols + high_cardinality + low_cardinality
    df = pd.DataFrame([data_dict])
    
    # Ensure all columns exist
    for col in all_cols:
        if col not in df.columns:
            if col in numerical_cols:
                df[col] = 0
            else:
                df[col] = 'Unknown'
    
    # Handle missing values (fill with defaults)
    for col in numerical_cols:
        if col in df.columns and (pd.isna(df[col].iloc[0]) or df[col].iloc[0] == ''):
            df[col] = 0
        elif col not in df.columns:
            df[col] = 0
    
    # Fill missing categorical values
    for col in high_cardinality + low_cardinality:
        if col in df.columns and (pd.isna(df[col].iloc[0]) or df[col].iloc[0] == ''):
            df[col] = 'Unknown'
        elif col not in df.columns:
            df[col] = 'Unknown'
    
    # Convert to proper types
    for col in numerical_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Label encode high cardinality columns
    X_encoded = df.copy()
    for col in high_cardinality:
        if col in df.columns:
            value = str(df[col].iloc[0])
            if value in label_encoders[col].classes_:
                X_encoded[col] = label_encoders[col].transform([value])[0]
            else:
                # Handle unknown values - use first class (index 0)
                X_encoded[col] = 0
    
    # OneHot encode low cardinality columns
    X_categorical = df[low_cardinality].fillna('Unknown')
    X_ohe = ohe.transform(X_categorical)
    
    # Combine features in the same order as training
    numerical_values = X_encoded[numerical_cols + high_cardinality].values.astype(float)
    X_final = np.hstack([numerical_values, X_ohe])
    
    # Check for any NaN or Inf values
    X_final = np.nan_to_num(X_final, nan=0.0, posinf=0.0, neginf=0.0)
    
    # Convert to 2D array if needed and ensure it's the right shape
    if len(X_final.shape) == 1:
        X_final = X_final.reshape(1, -1)
    
    return X_final

