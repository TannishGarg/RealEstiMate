# Indian House Price Prediction Website

A full-stack machine learning application for predicting house prices in India using various property features.

## Project Structure

```
Price_House/
├── data.csv                    # Dataset (250,000+ records)
├── train_model.py              # ML model training script
├── requirements.txt            # Python dependencies
├── model/                      # Saved model and preprocessing objects
│   ├── model.pkl
│   ├── label_encoders.pkl
│   ├── onehot_encoder.pkl
│   └── ...
├── backend/                    # Flask backend
│   ├── app.py                  # Main Flask application
│   └── preprocess.py           # Data preprocessing module
└── frontend/                   # Frontend files
    ├── index.html
    ├── styles.css
    └── script.js
```

## Features

- **Machine Learning Models**: RandomForest and LinearRegression with automatic model selection
- **Dynamic Dropdowns**: State → City → Locality cascading dropdowns
- **Real-time Prediction**: Instant price predictions based on property features
- **Modern UI**: Beautiful, responsive web interface

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the Model

First, train the machine learning model:

```bash
python train_model.py
```

This will:
- Load the dataset automatically
- Preprocess and encode features
- Train RandomForest and LinearRegression models
- Compare models and save the best one
- Save all preprocessing objects

### 3. Start the Backend Server

```bash
cd backend
python app.py
```

The server will start at `http://localhost:5000`

### 4. Open the Website

Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Fill in all the required form fields:
   - Select State, City, and Locality (dropdowns are dynamically populated)
   - Enter property details (BHK, Size, Floor, etc.)
   - Select property features (Furnished Status, Parking, Security, etc.)
   - Enter amenities (comma-separated, e.g., "Gym, Pool, Garden")

2. Click "Predict Price" button

3. View the predicted price in Lakhs (₹)

## Model Features

The model uses the following input features:

- **Location**: State, City, Locality
- **Property Details**: Property Type, BHK, Size (SqFt), Floor Number, Total Floors, Age
- **Facilities**: Nearby Schools, Nearby Hospitals, Public Transport Accessibility
- **Features**: Parking Space, Security, Amenities Count, Facing
- **Status**: Furnished Status, Owner Type, Availability Status

## API Endpoints

### GET `/api/locations`
Get location data for dropdowns
- Query params: `state` (optional), `city` (optional)
- Returns: JSON with states, cities, and localities

### POST `/api/predict`
Predict house price
- Body: JSON with all required features
- Returns: JSON with predicted price in Lakhs

## Notes

- The model automatically counts amenities from comma-separated strings
- All categorical features are properly encoded using LabelEncoder and OneHotEncoder
- The best model (based on R² and MAE) is automatically selected and saved

## Troubleshooting

- **Model not found**: Make sure you've run `train_model.py` first
- **Port already in use**: Change the port in `backend/app.py` (line with `app.run()`)
- **CORS errors**: The Flask-CORS package should handle this automatically
- **Dropdowns not loading**: Check that the backend is running and accessible

## Technologies Used

- **Backend**: Flask, Flask-CORS
- **ML**: scikit-learn, pandas, numpy, joblib
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

