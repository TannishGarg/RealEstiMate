# Troubleshooting Guide - Indian House Price Prediction

## Quick Diagnostics

Run the verification script to check system health:
```bash
python verify_setup.py
```

This will check:
- ✓ Dataset presence
- ✓ Model files
- ✓ Backend files
- ✓ Preprocessing functionality
- ✓ Prediction capability

---

## Common Issues and Solutions

### 1. Internal Error / Unknown Error

**Symptoms**: Generic error message with error ID

**Possible Causes**:
- Model not trained yet
- Missing model files
- Incorrect file paths
- Python environment issues

**Solutions**:

#### Step 1: Verify Setup
```bash
python verify_setup.py
```

#### Step 2: Retrain Model (if needed)
```bash
python train.py
```

#### Step 3: Test Model
```bash
python test_model.py
```

#### Step 4: Restart Backend
```bash
cd backend
python app.py
```

---

### 2. KeyError: 'Price_per_SqFt' or 'ID' or 'Year_Built'

**Cause**: Old code referencing removed columns

**Solution**: These columns have been removed. Ensure you're using the updated files:
- `train.py` (new version)
- `backend/app.py` (updated)
- `backend/preprocess.py` (updated)
- `test_model.py` (updated)

**Verify**: Run `python verify_setup.py`

---

### 3. Shape Mismatch Error

**Symptoms**: 
```
ValueError: X has n features, but model was trained with m features
```

**Cause**: Feature order mismatch or incorrect preprocessing

**Solution**:
1. Ensure features are in exact order:
   ```python
   ['State', 'City', 'Locality', 'Property_Type', 'BHK', 'Size_in_SqFt',
    'Furnished_Status', 'Floor_No', 'Total_Floors', 'Age_of_Property',
    'Nearby_Schools', 'Nearby_Hospitals', 'Public_Transport_Accessibility',
    'Parking_Space', 'Security', 'Amenities', 'Facing', 'Owner_Type',
    'Availability_Status']
   ```

2. Retrain model:
   ```bash
   python train.py
   ```

---

### 4. Text Formatting Issues

**Symptoms**: Predictions fail or return unexpected values

**Cause**: Inconsistent text formatting (e.g., "Ready To Move" vs "Ready_to_Move")

**Solution**: The system now auto-normalizes text. Ensure you're using updated files:

**Normalized Formats**:
- `Ready To Move` → `Ready_to_Move`
- `Semi-Furnished` → `Semi_Furnished`
- `yes/no` → `Yes/No`

---

### 5. Amenities Processing Error

**Symptoms**: Error when processing Amenities field

**Cause**: Amenities should be a count (integer), not a string

**Solution**: The system automatically converts:
- Input: `"Gym, Pool, Garden"` (string)
- Processed: `3` (count)

This is handled automatically in `backend/app.py` and `backend/preprocess.py`

---

### 6. Model Loading Error

**Symptoms**:
```
FileNotFoundError: model/model.pkl not found
```

**Cause**: Model not trained or wrong directory

**Solution**:
```bash
# Train the model
python train.py

# Verify model exists
ls model/model.pkl  # Linux/Mac
dir model\model.pkl  # Windows
```

---

### 7. Backend Won't Start

**Symptoms**: Flask server fails to start

**Possible Causes**:
- Port 5000 already in use
- Missing dependencies
- Model files not found

**Solutions**:

#### Check if port is in use:
```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

#### Kill existing process (Windows):
```bash
taskkill /PID <process_id> /F
```

#### Install dependencies:
```bash
pip install -r requirements.txt
```

#### Verify model files:
```bash
python verify_setup.py
```

---

### 8. Prediction Returns Same Value

**Symptoms**: All predictions return identical values

**Cause**: Model not properly trained or preprocessing issue

**Solution**:
1. Retrain model:
   ```bash
   python train.py
   ```

2. Test with different inputs:
   ```bash
   python test_model.py
   ```

3. Check test output - predictions should vary

---

### 9. Unknown Categories Warning

**Symptoms**:
```
UserWarning: Found unknown categories in columns during transform
```

**Cause**: Input contains values not seen during training

**Impact**: Usually harmless - OneHotEncoder handles with `handle_unknown='ignore'`

**Solution**: 
- If critical, retrain model with more diverse data
- Otherwise, ignore - the encoder will handle it

---

### 10. Import Errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'flask'
```

**Solution**:
```bash
pip install -r requirements.txt
```

**Required packages**:
- pandas
- numpy
- scikit-learn
- joblib
- flask
- flask-cors

---

## Verification Checklist

Before reporting an issue, verify:

- [ ] Dataset exists: `data.csv` (30+ MB)
- [ ] Model trained: `model/model.pkl` exists (1.6+ GB)
- [ ] All model files present (8 files in `model/` directory)
- [ ] Backend files updated: `app.py`, `preprocess.py`
- [ ] Training script: `train.py` exists
- [ ] Test script: `test_model.py` exists
- [ ] Python version: 3.8+ recommended
- [ ] Dependencies installed: `pip install -r requirements.txt`

**Quick Check**:
```bash
python verify_setup.py
```

---

## Performance Issues

### Slow Predictions

**Cause**: Large model (300 trees, 1.6 GB)

**Solutions**:
1. **Reduce model size** (retrain with fewer trees):
   ```python
   # In train.py, change:
   n_estimators=100  # instead of 300
   ```

2. **Use model compression**:
   ```python
   import joblib
   joblib.dump(model, 'model/model.pkl', compress=3)
   ```

### High Memory Usage

**Cause**: Large RandomForest model

**Solutions**:
1. Use a lighter model (LinearRegression, Ridge)
2. Reduce `n_estimators` in RandomForest
3. Increase system RAM

---

## Data Issues

### Missing Values in Dataset

**Solution**: The training script handles missing values automatically:
- Categorical: Filled with mode
- Numerical: Filled with median

### Inconsistent Text Formatting

**Solution**: Training script normalizes all text:
```python
# Automatic normalization in train.py
- Trims whitespaces
- Standardizes "Ready To Move" → "Ready_to_Move"
- Standardizes "Semi-Furnished" → "Semi_Furnished"
- Standardizes yes/no → Yes/No
```

---

## Getting Help

### Step 1: Run Diagnostics
```bash
python verify_setup.py
```

### Step 2: Check Logs
- Backend logs: Check terminal where `python backend/app.py` is running
- Look for error messages and stack traces

### Step 3: Test Components Individually

**Test Model**:
```bash
python test_model.py
```

**Test Preprocessing**:
```python
from backend.preprocess import preprocess_input
test_data = {...}  # Your test data
X = preprocess_input(test_data)
print(X.shape)  # Should be (1, 25)
```

**Test Prediction**:
```python
import joblib
model = joblib.load('model/model.pkl')
prediction = model.predict(X)
print(prediction)
```

---

## Reset Everything

If all else fails, retrain from scratch:

```bash
# 1. Clean old model files
rm -rf model/*  # Linux/Mac
rmdir /s model  # Windows (then recreate directory)

# 2. Retrain model
python train.py

# 3. Test model
python test_model.py

# 4. Verify setup
python verify_setup.py

# 5. Start backend
cd backend
python app.py
```

---

## System Requirements

**Minimum**:
- Python 3.8+
- 4 GB RAM
- 2 GB free disk space

**Recommended**:
- Python 3.10+
- 8 GB RAM
- 5 GB free disk space
- Multi-core CPU for faster training

---

## Contact & Support

For persistent issues:
1. Check `CHANGES_SUMMARY.md` for recent changes
2. Review error logs in terminal
3. Run `python verify_setup.py` and share output
4. Include Python version: `python --version`
5. Include OS: Windows/Linux/Mac

---

**Last Updated**: November 11, 2025
