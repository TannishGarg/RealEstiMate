import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import r2_score, mean_absolute_error
from backend.preprocess import preprocess_input

# Load model
model = joblib.load('model/model.pkl')
print(f"Model type: {type(model)}")

# Load test data
df = pd.read_csv('data.csv')
print(f"\nDataset shape: {df.shape}")

# Test with a few different samples
test_samples = [
    {
        'State': 'Maharashtra',
        'City': 'Pune',
        'Locality': 'Locality_490',
        'Property_Type': 'Apartment',
        'BHK': 3,
        'Size_in_SqFt': 2000,
        'Furnished_Status': 'Furnished',
        'Floor_No': 5,
        'Total_Floors': 10,
        'Age_of_Property': 5,
        'Nearby_Schools': 5,
        'Nearby_Hospitals': 3,
        'Public_Transport_Accessibility': 'High',
        'Parking_Space': 'Yes',
        'Security': 'Yes',
        'Amenities': 'Gym, Pool, Garden',
        'Facing': 'North',
        'Owner_Type': 'Owner',
        'Availability_Status': 'Ready_to_Move'
    },
    {
        'State': 'Karnataka',
        'City': 'Bangalore',
        'Locality': 'Locality_462',
        'Property_Type': 'Villa',
        'BHK': 4,
        'Size_in_SqFt': 3500,
        'Furnished_Status': 'Semi_Furnished',
        'Floor_No': 2,
        'Total_Floors': 3,
        'Age_of_Property': 10,
        'Nearby_Schools': 8,
        'Nearby_Hospitals': 5,
        'Public_Transport_Accessibility': 'Medium',
        'Parking_Space': 'Yes',
        'Security': 'Yes',
        'Amenities': 'Gym, Pool, Garden, Clubhouse',
        'Facing': 'East',
        'Owner_Type': 'Builder',
        'Availability_Status': 'Under_Construction',
        'Amenities': 'Gym, Pool, Garden, Clubhouse'
    },
    {
        'State': 'Delhi',
        'City': 'New Delhi',
        'Locality': 'Locality_232',
        'Property_Type': 'Independent House',
        'BHK': 2,
        'Size_in_SqFt': 1500,
        'Furnished_Status': 'Unfurnished',
        'Floor_No': 1,
        'Total_Floors': 2,
        'Age_of_Property': 20,
        'Nearby_Schools': 3,
        'Nearby_Hospitals': 2,
        'Public_Transport_Accessibility': 'Low',
        'Parking_Space': 'No',
        'Security': 'No',
        'Amenities': 'Garden',
        'Facing': 'South',
        'Owner_Type': 'Broker',
        'Availability_Status': 'Ready_to_Move'
    }
]

print("\n" + "="*60)
print("Testing Model Predictions")
print("="*60)

predictions = []
for i, sample in enumerate(test_samples, 1):
    try:
        # Normalize the sample data
        sample_copy = sample.copy()
        
        # Normalize Availability_Status
        if sample_copy['Availability_Status'] in ['Ready To Move', 'Ready to Move']:
            sample_copy['Availability_Status'] = 'Ready_to_Move'
        
        # Normalize Furnished_Status
        if sample_copy['Furnished_Status'] in ['Semi-Furnished', 'Semi-furnished']:
            sample_copy['Furnished_Status'] = 'Semi_Furnished'
        
        # Convert Amenities string to count
        if 'Amenities' in sample_copy and isinstance(sample_copy['Amenities'], str):
            sample_copy['Amenities'] = len([a for a in sample_copy['Amenities'].split(',') if a.strip()])
        
        X = preprocess_input(sample_copy)
        pred = model.predict(X)[0]
        predictions.append(pred)
        print(f"\nSample {i}:")
        print(f"  Location: {sample['State']}, {sample['City']}")
        print(f"  Property: {sample['Property_Type']}, {sample['BHK']} BHK, {sample['Size_in_SqFt']} SqFt")
        print(f"  Predicted Price: Rs {pred:.2f} Lakhs")
        print(f"  Feature array shape: {X.shape}")
        print(f"  Feature array sample (first 10): {X[0][:10]}")
    except Exception as e:
        print(f"\nSample {i} Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("Prediction Analysis")
print("="*60)
if predictions:
    print(f"Number of predictions: {len(predictions)}")
    print(f"Predictions: {[f'Rs {p:.2f}' for p in predictions]}")
    print(f"Min: Rs {min(predictions):.2f} Lakhs")
    print(f"Max: Rs {max(predictions):.2f} Lakhs")
    print(f"Mean: Rs {np.mean(predictions):.2f} Lakhs")
    print(f"Std: Rs {np.std(predictions):.2f} Lakhs")
    
    if len(set([round(p, 2) for p in predictions])) == 1:
        print("\n⚠️  WARNING: All predictions are the same!")
    else:
        print("\nOK: Predictions vary (model is working)")

# Test model accuracy on actual data
print("\n" + "="*60)
print("Testing Model Accuracy on Test Data")
print("="*60)

# Load preprocessing objects
label_encoders = joblib.load('model/label_encoders.pkl')
ohe = joblib.load('model/onehot_encoder.pkl')
numerical_cols = joblib.load('model/numerical_cols.pkl')
high_cardinality = joblib.load('model/high_cardinality.pkl')
low_cardinality = joblib.load('model/low_cardinality.pkl')

# Take a sample from actual data
sample_df = df.sample(min(100, len(df)), random_state=42)
print(f"Testing on {len(sample_df)} samples from dataset...")

actual_prices = []
predicted_prices = []

for idx, row in sample_df.iterrows():
    try:
        # Normalize the data to match training format
        availability = str(row['Availability_Status']).strip()
        if availability in ['Ready To Move', 'Ready to Move', 'ready to move']:
            availability = 'Ready_to_Move'
        
        furnished = str(row['Furnished_Status']).strip()
        if furnished in ['Semi-Furnished', 'Semi-furnished', 'semi-furnished', 'semi furnished']:
            furnished = 'Semi_Furnished'
        
        # Convert Amenities to count
        amenities = row['Amenities']
        if isinstance(amenities, str) and amenities.strip():
            amenities_count = len([a for a in amenities.split(',') if a.strip()])
        else:
            amenities_count = 0
        
        data_dict = {
            'State': row['State'],
            'City': row['City'],
            'Locality': row['Locality'],
            'Property_Type': row['Property_Type'],
            'BHK': row['BHK'],
            'Size_in_SqFt': row['Size_in_SqFt'],
            'Furnished_Status': furnished,
            'Floor_No': row['Floor_No'],
            'Total_Floors': row['Total_Floors'],
            'Age_of_Property': row['Age_of_Property'],
            'Nearby_Schools': row['Nearby_Schools'],
            'Nearby_Hospitals': row['Nearby_Hospitals'],
            'Public_Transport_Accessibility': row['Public_Transport_Accessibility'],
            'Parking_Space': row['Parking_Space'],
            'Security': row['Security'],
            'Amenities': amenities_count,
            'Facing': row['Facing'],
            'Owner_Type': row['Owner_Type'],
            'Availability_Status': availability
        }
        
        X = preprocess_input(data_dict)
        pred = model.predict(X)[0]
        
        actual_prices.append(row['Price_in_Lakhs'])
        predicted_prices.append(pred)
    except Exception as e:
        continue

if actual_prices and predicted_prices:
    r2 = r2_score(actual_prices, predicted_prices)
    mae = mean_absolute_error(actual_prices, predicted_prices)
    
    print(f"\nResults:")
    print(f"  R² Score: {r2:.4f}")
    print(f"  MAE: {mae:.2f} Lakhs")
    print(f"  Actual Price Range: Rs {min(actual_prices):.2f} - Rs {max(actual_prices):.2f} Lakhs")
    print(f"  Predicted Price Range: Rs {min(predicted_prices):.2f} - Rs {max(predicted_prices):.2f} Lakhs")
    
    if r2 < 0.5:
        print("\n⚠️  WARNING: Model accuracy is very low (R² < 0.5)")
    if len(set([round(p, 2) for p in predicted_prices[:10]])) == 1:
        print("\n⚠️  WARNING: Model is predicting the same value for different inputs!")

