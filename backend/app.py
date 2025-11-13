from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import joblib
import os
import pandas as pd
import numpy as np
from preprocess import preprocess_input
from datetime import timedelta

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_path = os.path.join(project_root, 'frontend')

app = Flask(__name__, static_folder=frontend_path)
app.secret_key = 'homeprice_ai_secret_key_2025'  # Change this in production
app.permanent_session_lifetime = timedelta(hours=24)
CORS(app, supports_credentials=True)

# Load model and preprocessing objects
model_dir = os.path.join(project_root, 'model')
print(f"Looking for model in: {model_dir}")

# List files in model directory for debugging
print("Files in model directory:", os.listdir(model_dir))

# Load the model
model_path = os.path.join(model_dir, 'model.pkl')
print(f"Loading model from: {model_path}")

if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}")

try:
    model = joblib.load(model_path)
    print("Successfully loaded the model")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    raise

# Load dataset for location filtering
dataset_path = os.path.join(project_root, 'data.csv')
df = pd.read_csv(dataset_path)

# Cache location relationships
location_cache = {
    'states': sorted(df['State'].unique().tolist()),
    'state_cities': {},
    'city_localities': {}
}

# Build state -> cities mapping
for state in location_cache['states']:
    cities = sorted(df[df['State'] == state]['City'].unique().tolist())
    location_cache['state_cities'][state] = cities

# Build city -> localities mapping
for city in df['City'].unique():
    localities = sorted(df[df['City'] == city]['Locality'].unique().tolist())
    location_cache['city_localities'][city] = localities

print("Model loaded successfully")
print(f"Location cache built: {len(location_cache['states'])} states")

@app.route('/')
def index():
    """Serve the landing page"""
    return send_from_directory(frontend_path, 'index.html')

@app.route('/prediction.html')
def prediction():
    """Serve the prediction page"""
    if not session.get('logged_in'):
        return send_from_directory(frontend_path, 'login.html')
    return send_from_directory(frontend_path, 'prediction.html')

@app.route('/login.html')
def login():
    """Serve the login page"""
    return send_from_directory(frontend_path, 'login.html')

@app.route('/about.html')
def about():
    """Serve the about page"""
    return send_from_directory(frontend_path, 'about.html')

@app.route('/contact.html')
def contact():
    """Serve the contact page"""
    return send_from_directory(frontend_path, 'contact.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, etc.)"""
    return send_from_directory(frontend_path, path)

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle user login"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Simple demo authentication (in production, use proper authentication)
        if email and password:
            # For demo purposes, accept any email/password combination
            session.permanent = True
            session['logged_in'] = True
            session['user_email'] = email
            return jsonify({
                'success': True,
                'message': 'Login successful'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """Check if user is logged in"""
    return jsonify({
        'logged_in': session.get('logged_in', False),
        'user_email': session.get('user_email', '')
    })

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Handle user logout"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Get location data for dropdowns"""
    state = request.args.get('state')
    city = request.args.get('city')
    
    response = {
        'states': location_cache['states']
    }
    
    if state:
        response['cities'] = location_cache['state_cities'].get(state, [])
    
    if city:
        response['localities'] = location_cache['city_localities'].get(city, [])
    
    return jsonify(response)

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict house price"""
    try:
        # Get input data
        data = request.json
        
        # Ensure required fields are present
        required_fields = [
            'State', 'City', 'Locality', 'Property_Type', 'BHK', 'Size_in_SqFt',
            'Furnished_Status', 'Total_Floors', 'Age_of_Property',
            'Nearby_Schools', 'Nearby_Hospitals', 'Public_Transport_Accessibility',
            'Parking_Space', 'Security', 'Amenities', 'Facing', 'Owner_Type',
            'Availability_Status'
        ]
        
        # Floor_No is only required for apartments
        if data.get('Property_Type') not in ['Independent House', 'Villa']:
            required_fields.append('Floor_No')
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {missing_fields}',
                'message': 'Please provide all required fields'
            }), 400
        
        # Auto-set Floor_No to 0 for Independent House and Villa
        if data.get('Property_Type') in ['Independent House', 'Villa']:
            data['Floor_No'] = 0
        
        # Prepare features for prediction
        try:
            # Create a copy of the input data
            input_data = data.copy()
            
            # Normalize text formatting
            # Normalize Availability_Status
            if 'Availability_Status' in input_data:
                input_data['Availability_Status'] = str(input_data['Availability_Status']).strip()
                if input_data['Availability_Status'] in ['Ready To Move', 'Ready to Move', 'ready to move']:
                    input_data['Availability_Status'] = 'Ready_to_Move'
            
            # Normalize Furnished_Status
            if 'Furnished_Status' in input_data:
                input_data['Furnished_Status'] = str(input_data['Furnished_Status']).strip()
                if input_data['Furnished_Status'] in ['Semi-Furnished', 'Semi-furnished', 'semi-furnished', 'semi furnished']:
                    input_data['Furnished_Status'] = 'Semi_Furnished'
            
            # Normalize yes/no values
            for col in ['Parking_Space', 'Security']:
                if col in input_data:
                    val = str(input_data[col]).strip().lower()
                    input_data[col] = 'Yes' if val in ['yes', 'y'] else 'No'
            
            # Calculate Amenities_Count from Amenities string
            amenities = input_data.get('Amenities', '')
            if isinstance(amenities, str) and amenities.strip():
                input_data['Amenities'] = len([a for a in amenities.split(',') if a.strip()])
            else:
                input_data['Amenities'] = 0
            
            # Use preprocess_input function to handle encoding
            X = preprocess_input(input_data)
            
            # Make prediction using the model
            prediction = model.predict(X)[0]
            
            return jsonify({
                'success': True,
                'prediction': float(prediction),
                'message': 'Prediction successful',
                'currency': 'INR',
                'unit': 'lakhs'
            })
            
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Error making prediction',
                'input_data': input_data  # Include input data for debugging
            }), 500
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Server error while processing prediction'
        }), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Starting Flask Server...")
    print("="*50)
    print("Server running at: http://localhost:5000")
    print("Open your browser and navigate to the URL above")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)

