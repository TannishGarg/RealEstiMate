import pandas as pd
import numpy as np
import joblib
import os

def preprocess_input(data_dict, model_dir=None):
    """
    Preprocess input data for prediction using the trained pipeline
    
    Args:
        data_dict: Dictionary containing input features
        model_dir: Path to directory containing model files (default: project_root/model)
        
    Returns:
        Preprocessed features ready for prediction
    """
    try:
        # Set default model directory if not provided
        if model_dir is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_dir = os.path.join(project_root, 'model')
            
        # Load the entire pipeline
        pipeline_path = os.path.join(model_dir, 'pipeline.pkl')
        if not os.path.exists(pipeline_path):
            raise FileNotFoundError(f"Pipeline not found at {pipeline_path}")
            
        print(f"Loading pipeline from: {pipeline_path}")
            
        # Convert input to DataFrame
        input_df = pd.DataFrame([data_dict])
        
        # Calculate derived features
        # 1. Bathroom - Calculate from BHK if not provided
        bhk = int(input_df.get('BHK', 2))
        if 'Bathroom' not in input_df.columns or pd.isna(input_df['Bathroom'].iloc[0]):
            input_df['Bathroom'] = bhk * 1.5
            
        # 2. Amenities_Count - Count number of amenities
        if 'Amenities' in input_df.columns:
            input_df['Amenities_Count'] = input_df['Amenities'].apply(
                lambda x: len(str(x).split(',')) if pd.notna(x) and str(x).strip() else 0
            )
        else:
            input_df['Amenities_Count'] = 0
        
        # Ensure all required columns exist
        required_columns = [
            'State', 'City', 'Locality', 'Property_Type', 'BHK', 'Size_in_SqFt',
            'Furnished_Status', 'Floor_No', 'Total_Floors', 'Age_of_Property',
            'Nearby_Schools', 'Nearby_Hospitals', 'Public_Transport_Accessibility',
            'Parking_Space', 'Security', 'Amenities_Count', 'Facing', 'Owner_Type',
            'Availability_Status'
        ]
        
        # Fill missing columns with appropriate defaults
        for col in required_columns:
            if col not in input_df.columns:
                if col == 'Amenities_Count':
                    input_df[col] = 0
                elif input_df.dtypes.get(col) == 'object':
                    input_df[col] = 'Unknown'
                else:
                    input_df[col] = 0
        
        # Load the pipeline
        pipeline = joblib.load(pipeline_path)
        
        # Get preprocessor to transform the input
        preprocessor = pipeline.named_steps['preprocessor']
        
        # Transform the input
        try:
            # Fill missing values before transformation
            numeric_cols = input_df.select_dtypes(include=['int64', 'float64']).columns
            input_df[numeric_cols] = input_df[numeric_cols].fillna(input_df[numeric_cols].median())
            
            # For categorical columns, fill with mode (most frequent)
            cat_cols = input_df.select_dtypes(include=['object']).columns
            for col in cat_cols:
                if input_df[col].isna().any():
                    input_df[col] = input_df[col].fillna(input_df[col].mode()[0])
            
            # Transform the data
            preprocessed_data = preprocessor.transform(input_df)
            
            # Apply polynomial features if present in the pipeline
            if 'poly' in pipeline.named_steps:
                preprocessed_data = pipeline.named_steps['poly'].transform(preprocessed_data)
                
            return preprocessed_data
            
        except Exception as e:
            print(f"Error during preprocessing: {str(e)}")
            raise
            
    except Exception as e:
        print(f"Error in preprocess_input: {str(e)}")
        raise

def get_locations():
    """
    Get unique locations from the dataset
    
    Returns:
        Dictionary containing states, cities, and localities
    """
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(project_root, 'data.csv')
        
        # Load the dataset
        df = pd.read_csv(data_path)
        
        # Get unique states, cities, and localities
        states = sorted(df['State'].dropna().unique().tolist())
        
        # Get cities for each state
        state_cities = {}
        for state in states:
            cities = df[df['State'] == state]['City'].dropna().unique().tolist()
            state_cities[state] = sorted(cities)
        
        # Get localities for each city
        city_localities = {}
        for city in df['City'].dropna().unique():
            localities = df[df['City'] == city]['Locality'].dropna().unique().tolist()
            city_localities[city] = sorted(localities)
        
        return {
            'states': states,
            'state_cities': state_cities,
            'city_localities': city_localities
        }
        
    except Exception as e:
        print(f"Error in get_locations: {str(e)}")
        return {
            'states': [],
            'state_cities': {},
            'city_localities': {}
        }

def predict_price(data_dict, model_dir='../model'):
    """
    Make a prediction using the trained model
    
    Args:
        data_dict: Dictionary containing input features
        model_dir: Path to directory containing model files
        
    Returns:
        Predicted price in lakhs
    """
    try:
        # Load the pipeline
        pipeline_path = os.path.join(model_dir, 'pipeline.pkl')
        pipeline = joblib.load(pipeline_path)
        
        # Preprocess the input
        X = preprocess_input(data_dict, model_dir)
        
        # Make prediction
        prediction = pipeline.predict(X)
        
        return float(prediction[0])
        
    except Exception as e:
        print(f"Error in predict_price: {str(e)}")
        raise
