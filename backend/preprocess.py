import pandas as pd
import numpy as np
import joblib
import os

def preprocess_input(data_dict):
    """
    Preprocess user input to match training data format using mixed encoding strategy
    
    Args:
        data_dict: Dictionary with user input features
    
    Returns:
        Preprocessed feature array ready for model prediction
    """
    # Load preprocessing objects
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'model')
    
    one_hot_encoder = joblib.load(os.path.join(model_dir, 'one_hot_encoder.pkl'))
    target_encoder = joblib.load(os.path.join(model_dir, 'target_encoder.pkl'))
    numerical_cols = joblib.load(os.path.join(model_dir, 'numerical_cols.pkl'))
    one_hot_cols = joblib.load(os.path.join(model_dir, 'one_hot_cols.pkl'))
    target_encode_cols = joblib.load(os.path.join(model_dir, 'target_encode_cols.pkl'))
    other_categorical_cols = joblib.load(os.path.join(model_dir, 'other_categorical_cols.pkl'))
    final_feature_columns = joblib.load(os.path.join(model_dir, 'final_feature_columns.pkl'))
    
    # Process amenities (multi-hot encoding)
    AMENITY_TYPES = ['gym', 'garden', 'pool', 'clubhouse', 'playground']
    
    def create_amenity_dummies(amenities_str):
        """Create multi-hot encoded amenities columns"""
        amenity_dict = {}
        if pd.isna(amenities_str) or amenities_str == '' or amenities_str == 'nan':
            for amenity in AMENITY_TYPES:
                amenity_dict[f'Amenity_{amenity.capitalize()}'] = 0
            return amenity_dict
        
        if isinstance(amenities_str, str):
            amenities_list = [a.strip().lower() for a in amenities_str.split(',') if a.strip()]
            for amenity in AMENITY_TYPES:
                amenity_dict[f'Amenity_{amenity.capitalize()}'] = 1 if amenity in amenities_list else 0
            return amenity_dict
        
        # Default case
        for amenity in AMENITY_TYPES:
            amenity_dict[f'Amenity_{amenity.capitalize()}'] = 0
        return amenity_dict
    
    # Create amenity columns
    amenity_data = create_amenity_dummies(data_dict.get('Amenities', ''))
    
    # Update data_dict with amenity columns
    for key, value in amenity_data.items():
        data_dict[key] = value
    
    # Remove original Amenities key if it exists
    if 'Amenities' in data_dict:
        del data_dict['Amenities']
    
    # Create DataFrame from input data
    input_df = pd.DataFrame([data_dict])
    
    # Ensure all required columns exist
    for col in numerical_cols + one_hot_cols + target_encode_cols + other_categorical_cols:
        if col not in input_df.columns:
            input_df[col] = 0 if col in numerical_cols else 'Unknown'
    
    # Apply encoding transformations
    
    # 1. One-hot encoding
    X_one_hot = one_hot_encoder.transform(input_df[one_hot_cols])
    one_hot_feature_names = one_hot_encoder.get_feature_names_out(one_hot_cols)
    X_one_hot_df = pd.DataFrame(X_one_hot, columns=one_hot_feature_names)
    
    # 2. Target encoding (use dummy target for prediction)
    X_target_encoded = target_encoder.transform(input_df[target_encode_cols])
    X_target_df = pd.DataFrame(X_target_encoded, columns=target_encode_cols)
    
    # 3. Other categorical features (simple dummy encoding)
    X_other_cat = input_df[other_categorical_cols].copy()
    for col in other_categorical_cols:
        if X_other_cat[col].dtype == 'object':
            dummies = pd.get_dummies(X_other_cat[col], prefix=col, drop_first=True)
            X_other_cat = pd.concat([X_other_cat.drop(col, axis=1), dummies], axis=1)
    
    # 4. Numerical features
    X_numerical = input_df[numerical_cols].copy()
    
    # Combine all features
    X_final = pd.concat([
        X_numerical,
        X_one_hot_df,
        X_target_df,
        X_other_cat
    ], axis=1)
    
    # Ensure final columns match training columns
    for col in final_feature_columns:
        if col not in X_final.columns:
            X_final[col] = 0
    
    # Select only the columns that were in training (in correct order)
    X_final = X_final[final_feature_columns]
    
    # Handle any remaining NaN or infinite values
    X_final = X_final.replace([np.inf, -np.inf], 0).fillna(0)
    
    return X_final.values
