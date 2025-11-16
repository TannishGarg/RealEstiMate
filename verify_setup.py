"""
Verification script to check if all components are properly configured
"""
import os
import sys

print("="*60)
print("Indian House Price Prediction - Setup Verification")
print("="*60)

errors = []
warnings = []
success = []

# Check 1: Dataset exists
print("\n1. Checking dataset...")
if os.path.exists('data.csv'):
    size_mb = os.path.getsize('data.csv') / (1024 * 1024)
    success.append(f"✓ Dataset found (data.csv, {size_mb:.2f} MB)")
else:
    errors.append("✗ Dataset not found (data.csv)")

# Check 2: Model directory and files
print("2. Checking model files...")
model_dir = 'model'
required_model_files = [
    'model.pkl',
    'target_encoder.pkl',
    'numerical_cols.pkl',
    'categorical_cols.pkl',
    'feature_order.pkl'
]

if os.path.exists(model_dir):
    for file in required_model_files:
        file_path = os.path.join(model_dir, file)
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if size_mb > 1:
                success.append(f"✓ {file} ({size_mb:.2f} MB)")
            else:
                size_kb = os.path.getsize(file_path) / 1024
                success.append(f"✓ {file} ({size_kb:.2f} KB)")
        else:
            errors.append(f"✗ Missing: {file}")
else:
    errors.append("✗ Model directory not found")

# Check 3: Backend files
print("3. Checking backend files...")
backend_files = ['backend/app.py', 'backend/preprocess.py']
for file in backend_files:
    if os.path.exists(file):
        success.append(f"✓ {file}")
    else:
        errors.append(f"✗ Missing: {file}")

# Check 4: Training script
print("4. Checking training script...")
if os.path.exists('train.py'):
    success.append("✓ train.py")
else:
    errors.append("✗ Missing: train.py")

# Check 5: Test script
print("5. Checking test script...")
if os.path.exists('test_model.py'):
    success.append("✓ test_model.py")
else:
    errors.append("✗ Missing: test_model.py")

# Check 6: Try loading the model
print("6. Testing model loading...")
try:
    import joblib
    model = joblib.load('model/model.pkl')
    success.append(f"✓ Model loaded successfully (type: {type(model).__name__})")
except Exception as e:
    errors.append(f"✗ Failed to load model: {str(e)}")

# Check 7: Verify feature order
print("7. Checking feature configuration...")
try:
    import joblib
    feature_order = joblib.load('model/feature_order.pkl')
    expected_features = [
        'State', 'City', 'Locality', 'Property_Type', 'BHK', 'Size_in_SqFt',
        'Furnished_Status', 'Floor_No', 'Total_Floors', 'Age_of_Property',
        'Nearby_Schools', 'Nearby_Hospitals', 'Public_Transport_Accessibility',
        'Parking_Space', 'Security', 'Amenities', 'Facing', 'Owner_Type',
        'Availability_Status'
    ]
    if feature_order == expected_features:
        success.append(f"✓ Feature order correct ({len(feature_order)} features)")
    else:
        warnings.append(f"⚠ Feature order mismatch")
except Exception as e:
    warnings.append(f"⚠ Could not verify feature order: {str(e)}")

# Check 8: Test preprocessing
print("8. Testing preprocessing function...")
try:
    from backend.preprocess import preprocess_input
    test_data = {
        'State': 'Madhya Pradesh',
        'City': 'Bhopal',
        'Locality': 'MP Nagar',
        'Property_Type': 'Independent House',
        'BHK': 1,
        'Size_in_SqFt': 624,
        'Furnished_Status': 'Unfurnished',
        'Floor_No': 0,
        'Total_Floors': 1,
        'Age_of_Property': 2,
        'Nearby_Schools': 0,
        'Nearby_Hospitals': 5,
        'Public_Transport_Accessibility': 'High',
        'Parking_Space': 'yes',
        'Security': 'yes',
        'Amenities': 'Club House, Gym, Playground, Pool',
        'Facing': 'West',
        'Owner_Type': 'Owner',
        'Availability_Status': 'Ready To Move'
    }
    X = preprocess_input(test_data)
    success.append(f"✓ Preprocessing works (output shape: {X.shape})")
except Exception as e:
    errors.append(f"✗ Preprocessing failed: {str(e)}")

# Check 9: Test prediction
print("9. Testing prediction...")
try:
    from backend.preprocess import preprocess_input
    import joblib
    model = joblib.load('model/model.pkl')
    test_data = {
        'State': 'Madhya Pradesh',
        'City': 'Bhopal',
        'Locality': 'MP Nagar',
        'Property_Type': 'Independent House',
        'BHK': 1,
        'Size_in_SqFt': 624,
        'Furnished_Status': 'Unfurnished',
        'Floor_No': 0,
        'Total_Floors': 1,
        'Age_of_Property': 2,
        'Nearby_Schools': 0,
        'Nearby_Hospitals': 5,
        'Public_Transport_Accessibility': 'High',
        'Parking_Space': 'yes',
        'Security': 'yes',
        'Amenities': 'Club House, Gym, Playground, Pool',
        'Facing': 'West',
        'Owner_Type': 'Owner',
        'Availability_Status': 'Ready To Move'
    }
    X = preprocess_input(test_data)
    prediction = model.predict(X)[0]
    success.append(f"✓ Prediction works (predicted: ₹{prediction:.2f} Lakhs)")
except Exception as e:
    errors.append(f"✗ Prediction failed: {str(e)}")

# Print summary
print("\n" + "="*60)
print("VERIFICATION SUMMARY")
print("="*60)

if success:
    print(f"\n✓ SUCCESS ({len(success)} checks passed):")
    for item in success:
        print(f"  {item}")

if warnings:
    print(f"\n⚠ WARNINGS ({len(warnings)} items):")
    for item in warnings:
        print(f"  {item}")

if errors:
    print(f"\n✗ ERRORS ({len(errors)} items):")
    for item in errors:
        print(f"  {item}")
else:
    print("\n" + "="*60)
    print("🎉 ALL CHECKS PASSED! System is ready to use.")
    print("="*60)
    print("\nNext steps:")
    print("1. Start backend: cd backend && python app.py")
    print("2. Open browser: http://localhost:5000")
    print("3. Test predictions through the web interface")

print("\n" + "="*60)
sys.exit(0 if not errors else 1)
