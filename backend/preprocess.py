import pandas as pd
import numpy as np
import joblib
import os

def preprocess_input(data_dict):
    """
    Preprocess user input to match training data format using TargetEncoder
    
    Args:
        data_dict: Dictionary with user input features
    
    Returns:
        Preprocessed feature array ready for model prediction
    """
    # Load preprocessing objects
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'model')
    
    target_encoder = joblib.load(os.path.join(model_dir, 'target_encoder.pkl'))
    numerical_cols = joblib.load(os.path.join(model_dir, 'numerical_cols.pkl'))
    categorical_cols = joblib.load(os.path.join(model_dir, 'categorical_cols.pkl'))
    
    # Amenities should already be a count at this point (processed in app.py)
    # If it's still a string, convert it
    if 'Amenities' in data_dict and isinstance(data_dict['Amenities'], str):
        amenities_str = data_dict['Amenities']
        if pd.isna(amenities_str) or amenities_str == '' or amenities_str == 'nan':
            data_dict['Amenities'] = 0
        else:
            data_dict['Amenities'] = len([a.strip() for a in amenities_str.split(',') if a.strip()])
    elif 'Amenities' not in data_dict:
        data_dict['Amenities'] = 0
    
    # Create DataFrame with all required columns
    all_cols = numerical_cols + categorical_cols
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
    for col in categorical_cols:
        if col in df.columns and (pd.isna(df[col].iloc[0]) or df[col].iloc[0] == ''):
            df[col] = 'Unknown'
        elif col not in df.columns:
            df[col] = 'Unknown'
    
    # Convert to proper types
    for col in numerical_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Apply TargetEncoder to categorical columns
    # Note: TargetEncoder was fitted on training data, so we use transform only
    try:
        # Create a dummy target for transform (TargetEncoder expects y during fit, but transform can work without it)
        X_encoded = target_encoder.transform(df)
    except:
        # If transform fails, try with a dummy target
        dummy_y = pd.Series([0])  # Dummy target
        X_encoded = target_encoder.transform(df)
    
    # Ensure we have the same columns as during training
    # The TargetEncoder should handle this automatically
    
    # Check for any NaN or Inf values
    X_encoded = X_encoded.replace([np.inf, -np.inf], 0).fillna(0)
    
    # Convert to numpy array
    X_final = X_encoded.values.astype(float)
    
    # Convert to 2D array if needed and ensure it's the right shape
    if len(X_final.shape) == 1:
        X_final = X_final.reshape(1, -1)
    
    return X_final
