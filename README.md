# MaternalCare Prediction AP


This project provides a REST API to predict maternal health risks based on input health metrics. It uses a pre-trained deep learning model and a Flask web server to serve predictions. The API takes user health data (age, blood pressure, blood sugar, body temperature, and heart rate) and provides a risk classification (Low, Mid, or High) for maternal health.

## Features

- **Flask-based API**: Exposes a `/predict` endpoint to make predictions.
- **Model**: The model uses an LSTM neural network trained on maternal health data.
- **Firebase Integration**: Stores user inputs and predictions in Firebase Firestore for persistence.
- **Data Scaling**: Input data is scaled using a pre-trained StandardScaler.

## Requirements

- Python 3.x
- Flask
- TensorFlow (for loading the Keras model)
- scikit-learn (for the scaler)
- firebase-admin (for Firebase integration)
- joblib (for loading the scaler)
- NumPy
