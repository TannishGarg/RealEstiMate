import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import os

def check_model_performance():
    """Check the current model's performance"""
    print("Loading model and data...")
    
    # Load the pipeline
    model_path = os.path.join('model', 'pipeline.pkl')
    
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        print("Please train the model first by running: python train_improved.py")
        return
    
    pipeline = joblib.load(model_path)
    print("✓ Model loaded successfully")
    
    # Load and prepare data
    print("\nLoading data...")
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
    df = df.drop_duplicates()
    df = df[(df['Price_in_Lakhs'] >= 10) & (df['Price_in_Lakhs'] <= 10000)]
    
    # Feature engineering
    if 'Bathroom' not in df.columns:
        df['Bathroom'] = df['BHK'] * 1.5
    
    df['Amenities_Count'] = df['Amenities'].apply(
        lambda x: len(str(x).split(',')) if pd.notna(x) else 0
    )
    
    # Select features
    feature_columns = [
        'State', 'City', 'Locality', 'Property_Type', 'BHK', 'Size_in_SqFt',
        'Furnished_Status', 'Floor_No', 'Total_Floors', 'Age_of_Property',
        'Nearby_Schools', 'Nearby_Hospitals', 'Public_Transport_Accessibility',
        'Parking_Space', 'Security', 'Amenities_Count', 'Facing', 'Owner_Type',
        'Availability_Status'
    ]
    
    X = df[feature_columns].copy()
    y = df['Price_in_Lakhs'].copy()
    
    # Handle missing values
    for col in X.columns:
        if X[col].dtype == 'object':
            X[col] = X[col].fillna('Unknown')
        else:
            X[col] = X[col].fillna(X[col].median())
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print("✓ Data prepared successfully")
    print(f"  Training samples: {len(X_train)}")
    print(f"  Testing samples: {len(X_test)}")
    
    # Make predictions
    print("\nMaking predictions...")
    train_pred = pipeline.predict(X_train)
    test_pred = pipeline.predict(X_test)
    
    # Calculate metrics
    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)
    train_mae = mean_absolute_error(y_train, train_pred)
    test_mae = mean_absolute_error(y_test, test_pred)
    
    # Display results
    print("\n" + "="*60)
    print("MODEL PERFORMANCE METRICS")
    print("="*60)
    print(f"\n📊 R² Score (Coefficient of Determination):")
    print(f"   Training Set:  {train_r2:.4f} ({train_r2*100:.2f}%)")
    print(f"   Testing Set:   {test_r2:.4f} ({test_r2*100:.2f}%)")
    
    print(f"\n📉 MAE (Mean Absolute Error):")
    print(f"   Training Set:  ₹{train_mae:.2f} Lakhs")
    print(f"   Testing Set:   ₹{test_mae:.2f} Lakhs")
    
    print(f"\n💡 Interpretation:")
    if test_r2 > 0.9:
        print(f"   ✓ Excellent model! Explains {test_r2*100:.1f}% of price variance")
    elif test_r2 > 0.8:
        print(f"   ✓ Good model! Explains {test_r2*100:.1f}% of price variance")
    elif test_r2 > 0.7:
        print(f"   ⚠ Decent model. Explains {test_r2*100:.1f}% of price variance")
    else:
        print(f"   ⚠ Model needs improvement. Only explains {test_r2*100:.1f}% of variance")
    
    print(f"   Average prediction error: ±₹{test_mae:.2f} Lakhs")
    
    # Check for overfitting
    r2_diff = train_r2 - test_r2
    mae_diff = test_mae - train_mae
    
    print(f"\n🔍 Overfitting Check:")
    if r2_diff > 0.1:
        print(f"   ⚠ Possible overfitting detected (R² difference: {r2_diff:.4f})")
    else:
        print(f"   ✓ Model generalizes well (R² difference: {r2_diff:.4f})")
    
    print("="*60)
    
    # Sample predictions
    print("\n📝 Sample Predictions (first 5 test samples):")
    print("-"*60)
    print(f"{'Actual Price':<15} {'Predicted Price':<18} {'Error':<15}")
    print("-"*60)
    for i in range(min(5, len(y_test))):
        actual = y_test.iloc[i]
        predicted = test_pred[i]
        error = abs(actual - predicted)
        print(f"₹{actual:<14.2f} ₹{predicted:<17.2f} ±₹{error:.2f}")
    print("-"*60)

if __name__ == "__main__":
    check_model_performance()
