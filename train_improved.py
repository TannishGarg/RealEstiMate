import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import (
    StandardScaler, OneHotEncoder, PolynomialFeatures, TargetEncoder
)
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor
import joblib
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

def load_and_clean_data():
    """Load and clean the dataset"""
    print("Loading and cleaning data...")
    
    # Load data with specified dtypes for problematic columns
    dtypes = {
        'BHK': 'float64',
        'Size_in_SqFt': 'float64',
        'Floor_No': 'float64',
        'Total_Floors': 'float64',
        'Age_of_Property': 'float64',
        'Nearby_Schools': 'float64',
        'Nearby_Hospitals': 'float64'
    }
    
    df = pd.read_csv('data.csv', dtype=dtypes, low_memory=False)
    
    # Basic cleaning
    df = df.drop_duplicates()
    
    # Ensure price is within reasonable range (adjust based on your data)
    df = df[(df['Price_in_Lakhs'] >= 10) & (df['Price_in_Lakhs'] <= 10000)]
    
    # Feature engineering
    df['Price_per_SqFt'] = df['Price_in_Lakhs'] * 100000 / df['Size_in_SqFt']
    
    # Handle Bathroom column (use BHK * 1.5 if Bathroom is not available)
    if 'Bathroom' not in df.columns:
        df['Bathroom'] = df['BHK'] * 1.5
    df['Bathroom_Ratio'] = df['Bathroom'] / df['BHK']
    
    # Handle amenities
    df['Amenities_Count'] = df['Amenities'].apply(
        lambda x: len(str(x).split(',')) if pd.notna(x) else 0
    )
    
    return df

def prepare_features(df):
    """Prepare features and target variable"""
    # Select features
    features = [
        'State', 'City', 'Locality', 'Property_Type', 'BHK', 'Size_in_SqFt',
        'Furnished_Status', 'Floor_No', 'Total_Floors', 'Age_of_Property',
        'Nearby_Schools', 'Nearby_Hospitals', 'Public_Transport_Accessibility',
        'Parking_Space', 'Security', 'Amenities_Count', 'Facing', 'Owner_Type',
        'Availability_Status', 'Price_per_SqFt', 'Bathroom_Ratio'
    ]
    
    # Ensure all features exist
    features = [f for f in features if f in df.columns]
    
    X = df[features].copy()
    y = df['Price_in_Lakhs'].copy()
    
    return X, y, features

def create_preprocessor():
    """Create preprocessing pipeline"""
    numerical_features = [
        'BHK', 'Size_in_SqFt', 'Floor_No', 'Total_Floors', 'Age_of_Property',
        'Nearby_Schools', 'Nearby_Hospitals', 'Amenities_Count',
        'Price_per_SqFt', 'Bathroom_Ratio'
    ]
    
    categorical_features = [
        'Property_Type', 'Furnished_Status', 'Public_Transport_Accessibility',
        'Parking_Space', 'Security', 'Facing', 'Owner_Type', 'Availability_Status'
    ]
    
    high_cardinality = ['State', 'City', 'Locality']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
            ('target_enc', TargetEncoder(target_type='continuous'), high_cardinality)
        ],
        remainder='drop'
    )
    
    return preprocessor, numerical_features, categorical_features, high_cardinality

def train_model(X, y):
    """Train and evaluate the model"""
    preprocessor, num_cols, cat_cols, high_card_cols = create_preprocessor()
    
    # Create pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('poly', PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)),
        ('regressor', XGBRegressor(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        ))
    ])
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print("Training model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    train_pred = pipeline.predict(X_train)
    test_pred = pipeline.predict(X_test)
    
    print("\nModel Performance:")
    print(f"Train R²: {r2_score(y_train, train_pred):.4f}")
    print(f"Test R²: {r2_score(y_test, test_pred):.4f}")
    print(f"Train MAE: {mean_absolute_error(y_train, train_pred):.2f} Lakhs")
    print(f"Test MAE: {mean_absolute_error(y_test, test_pred):.2f} Lakhs")
    
    # Feature importance (for tree-based models)
    if hasattr(pipeline.named_steps['regressor'], 'feature_importances_'):
        print("\nTop 10 most important features:")
        feature_importances = pipeline.named_steps['regressor'].feature_importances_
        feature_names = pipeline.named_steps['preprocessor'].get_feature_names_out()
        
        # Handle polynomial features
        if hasattr(pipeline.named_steps['poly'], 'get_feature_names_out'):
            feature_names = pipeline.named_steps['poly'].get_feature_names_out(feature_names)
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': feature_importances
        }).sort_values('importance', ascending=False)
        
        print(importance_df.head(10).to_string())
    
    return pipeline, X_test, y_test

def save_model(pipeline, model_dir='model'):
    """Save the trained model and preprocessing objects"""
    os.makedirs(model_dir, exist_ok=True)
    
    # Save the entire pipeline
    joblib.dump(pipeline, os.path.join(model_dir, 'pipeline.pkl'))
    
    # Save individual components for reference
    joblib.dump(pipeline.named_steps['preprocessor'], 
               os.path.join(model_dir, 'preprocessor.pkl'))
    
    print(f"\nModel and preprocessing objects saved to {model_dir}/")

def main():
    # Load and clean data
    df = load_and_clean_data()
    
    # Prepare features
    X, y, feature_names = prepare_features(df)
    print(f"\nTraining on {len(X)} samples with {len(feature_names)} features")
    
    # Train model
    pipeline, X_test, y_test = train_model(X, y)
    
    # Save model
    save_model(pipeline)
    
    # Sample predictions
    print("\nSample predictions:")
    sample = X_test.sample(5, random_state=42)
    predictions = pipeline.predict(sample)
    
    for i, (idx, row) in enumerate(sample.iterrows()):
        print(f"\nPrediction {i+1}:")
        print(f"- Actual Price: {y_test.loc[idx]:.2f} Lakhs")
        print(f"- Predicted Price: {predictions[i]:.2f} Lakhs")
        print(f"- Features: {row[['City', 'Locality', 'BHK', 'Size_in_SqFt']].to_dict()}")

if __name__ == "__main__":
    main()
