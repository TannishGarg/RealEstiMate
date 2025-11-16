# RealEstiMate - Real Estate Price Prediction Platform

A sophisticated web application for predicting house prices using advanced machine learning. Built with Flask backend and modern frontend technologies, featuring Firebase authentication and XGBoost model for accurate price predictions.

## Overview

RealEstiMate leverages machine learning to provide accurate house price predictions across India. The platform analyzes multiple factors including location, property specifications, amenities, and nearby facilities to deliver reliable price estimates.

## Features

### Core Functionality
- **Advanced Price Prediction**: XGBoost-powered ML model with 91.86% accuracy
- **Comprehensive Location Support**: Multi-level location selection (State → City → Locality)
- **Multiple Property Types**: Support for Apartments, Independent Houses, and Villas
- **Real-time Form Validation**: Instant feedback and error handling
- **Responsive Design**: Optimized for desktop and mobile devices

### Authentication System
- **Firebase Integration**: Secure and scalable user authentication
- **Protected Routes**: Prediction features require user authentication
- **Session Management**: Automatic login state handling
- **User Registration**: Complete signup and login workflow

### Enhanced User Interface

#### Multi-Select Amenities Dropdown
- **Modern Dropdown Interface**: Replaced basic text input with interactive multi-select component
- **Available Amenities**: Gym, Playground, Club House, Pool, Garden
- **Visual Feedback**: Tag-based selection with gradient styling
- **Interactive Features**: One-click removal, smooth animations, hover effects
- **Smart Behavior**: Click-outside-to-close, keyboard navigation support

#### Intelligent Property Handling
- **Smart Floor Logic**: Context-aware floor number input
  - Independent Houses/Villas: Automatically set to ground floor
  - Apartments: User-selectable floor numbers
- **Dynamic Form Fields**: Adaptive validation based on property type

## Project Architecture

```
RealEstiMate/
├── backend/
│   └── app.py                 # Flask REST API server
├── frontend/
│   ├── index.html            # Landing page with hero section
│   ├── prediction.html       # Main prediction interface
│   ├── login.html           # User authentication page
│   ├── signup.html          # User registration form
│   ├── about.html           # Project information
│   ├── contact.html         # Contact and support
│   ├── styles.css           # Component-specific styling
│   ├── shared.css           # Common design system
│   ├── script.js            # Frontend application logic
│   ├── auth.js              # Firebase authentication
│   ├── firebase.js          # Firebase configuration
│   └── contact.js           # Contact form handling
├── model/
│   ├── model.pkl            # Trained XGBoost model
│   ├── categorical_cols.pkl # Categorical feature mappings
│   ├── numerical_cols.pkl   # Numerical feature scalers
│   ├── feature_order.pkl    # Feature ordering reference
│   └── target_encoder.pkl   # Target encoding mappings
├── data.csv                 # Training dataset (225K samples)
├── train.py                 # Model training pipeline
├── test_model.py            # Model validation and testing
├── verify_setup.py          # Environment verification
└── requirements.txt         # Python dependency specifications
```

## Technology Stack

### Backend Technologies
- **Flask**: Lightweight and powerful web framework
- **XGBoost**: Gradient boosting framework for ML predictions
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: Machine learning utilities and preprocessing
- **Joblib**: Model serialization and persistence

### Frontend Technologies
- **HTML5**: Semantic markup and modern web standards
- **CSS3**: Advanced styling with animations and transitions
- **JavaScript ES6+**: Modern JavaScript with async/await
- **Firebase**: Google's authentication and backend services

### Design System
- **Modern UI/UX**: Gradient backgrounds, smooth transitions, micro-interactions
- **Responsive Design**: Mobile-first approach with breakpoints
- **Accessibility**: WCAG compliance with semantic HTML and ARIA labels
- **Typography**: Inter font family for optimal readability

## Model Performance Metrics

The XGBoost regression model demonstrates exceptional predictive performance:

- **Accuracy**: R² Score of 0.9186 (91.86%)
- **Error Margin**: Mean Absolute Error of 20.28 Lakhs
- **Training Dataset**: 225,000 samples with 20 features
- **Price Range**: Covers properties from 39.39 to 603.55 Lakhs
- **Feature Engineering**: Advanced encoding for categorical variables

### Model Features
The prediction algorithm analyzes:
- **Geographic Data**: State, City, Locality with target encoding
- **Property Specifications**: Type, BHK configuration, Total area
- **Building Details**: Floor number, Total floors, Property age
- **Amenities**: Gym, Pool, Garden, Playground, Club House
- **Infrastructure**: Nearby schools, hospitals, transport accessibility
- **Additional Features**: Furnishing status, parking, security, facing direction

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Firebase project with Authentication enabled
- Git for version control

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/TannishGarg/RealEstiMate.git
   cd RealEstiMate
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Firebase Configuration**
   - Create a new Firebase project at https://console.firebase.google.com
   - Enable Authentication (Email/Password method)
   - Copy your Firebase configuration
   - Update `frontend/firebase.js` with your credentials

5. **Verify Setup**
   ```bash
   python verify_setup.py
   ```

6. **Launch Application**
   ```bash
   python backend/app.py
   ```

7. **Access the Platform**
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - Register a new account or login to access predictions

## API Documentation

### Authentication Endpoints
- `POST /api/register` - Create new user account
- `POST /api/login` - Authenticate existing user
- `POST /api/logout` - Terminate user session

### Location Data Endpoints
- `GET /api/locations` - Retrieve all available states
- `GET /api/locations?state=<state>` - Get cities within specified state
- `GET /api/locations?city=<city>` - Get localities within specified city

### Prediction Endpoint
- `POST /api/predict` - Generate price prediction based on property details

### Request Format
```json
{
  "State": "Punjab",
  "City": "Amritsar",
  "Locality": "Ranjit Avenue",
  "Property_Type": "Apartment",
  "BHK": 3,
  "Size_in_SqFt": 1500,
  "Amenities": "Gym, Pool, Garden",
  "Furnished_Status": "Semi-Furnished",
  "Floor_No": 5,
  "Total_Floors": 10,
  "Age_of_Property": 2,
  "Nearby_Schools": 3,
  "Nearby_Hospitals": 2,
  "Public_Transport_Accessibility": "High",
  "Parking_Space": "Yes",
  "Security": "Yes",
  "Facing": "North",
  "Owner_Type": "Builder",
  "Availability_Status": "Ready To Move"
}
```

## Usage Guide

### Getting Started
1. **Account Creation**: Register with your email and create a secure password
2. **Authentication**: Login to access the prediction features
3. **Property Input**: Navigate to the Predict page and enter property details
4. **Location Selection**: Choose State → City → Locality in sequence
5. **Property Configuration**: Specify type, size, rooms, and other features
6. **Amenities Selection**: Use the multi-select dropdown to choose available amenities
7. **Generate Prediction**: Click "Predict Price" for instant results

### Tips for Accurate Predictions
- Provide precise location information for better accuracy
- Include all relevant amenities to improve price estimates
- Ensure property specifications are accurate and complete
- Consider the age and condition of the property

## Testing and Validation

### Model Testing
Run comprehensive model tests:
```bash
python test_model.py
```

### Test Coverage
- Model loading and validation
- Sample prediction testing
- Performance metric calculation
- Feature processing verification
- Accuracy benchmarking

### Expected Test Results
- R² Score: ~0.92
- MAE: ~20 Lakhs
- Successful feature processing
- Consistent prediction ranges

## Development and Customization

### Adding New Amenities
1. Update `frontend/prediction.html`:
   ```html
   <div class="amenity-option">
       <input type="checkbox" id="amenity_new" value="New Amenity">
       <label for="amenity_new">New Amenity</label>
   </div>
   ```

2. Styles are automatically applied through existing CSS classes

### Model Feature Updates
- Modify feature processing in `backend/app.py`
- Update model training pipeline in `train.py`
- Retrain model with new features if necessary

### UI Customization
- Modify color schemes in `frontend/styles.css`
- Update animations and transitions
- Adjust responsive breakpoints

## Deployment

### Production Deployment
1. **Environment Setup**: Configure production environment variables
2. **Database Setup**: Configure production database if needed
3. **Firebase Production**: Use production Firebase project
4. **Model Optimization**: Optimize model for production inference
5. **Web Server**: Use production WSGI server (Gunicorn/uWSGI)

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "backend/app.py"]
```

## Contributing Guidelines

### Contribution Process
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Implement changes with proper testing
4. Commit changes: `git commit -m 'Add new feature'`
5. Push to branch: `git push origin feature/new-feature`
6. Submit Pull Request with detailed description

### Code Standards
- Follow PEP 8 for Python code
- Use semantic HTML5 markup
- Implement responsive CSS with mobile-first approach
- Write clean, documented JavaScript
- Include tests for new features

## Performance Optimization

### Model Optimization
- Feature selection and engineering
- Hyperparameter tuning
- Cross-validation for robustness
- Regular model retraining with new data

### Frontend Optimization
- Lazy loading for images
- Code splitting for JavaScript
- CSS optimization and minification
- Caching strategies for static assets

## Security Considerations

### Authentication Security
- Firebase authentication best practices
- Session management and timeout
- Secure password policies
- Protection against common attacks

### API Security
- Input validation and sanitization
- Rate limiting for API endpoints
- CORS configuration
- Error handling without information leakage

## License and Acknowledgments

### License
This project is licensed under the MIT License. See LICENSE file for complete details.

### Acknowledgments
- XGBoost team for the powerful machine learning framework
- Firebase for providing authentication infrastructure
- Flask community for the web framework
- Scikit-learn for machine learning utilities
- Open source community for various tools and libraries

## Contact and Support

For questions, support, or contributions:
- GitHub Issues: Report bugs or request features
- Project Repository: https://github.com/TannishGarg/RealEstiMate
- Documentation: Complete API and usage guides available

---

RealEstiMate - Transforming real estate price prediction through machine learning and modern web technologies.