import os
from flask import Flask, request, jsonify
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import joblib
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Load the trained model and scaler
model = load_model("maternal_health_model.h5")
scaler = joblib.load("scaler.pkl")  # Ensure this scaler was saved during training

# Initialize Flask app
app = Flask(__name__)

# Define endpoint for prediction
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data from the request
        data = request.json
        email = data.get('email')  # User email

        # Validate email in Firestore 'users' collection
        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Query Firestore to find the user by email in the 'users' collection
        user_ref = db.collection("users").where("email", "==", email)
        user_docs = user_ref.stream()

        # Check if any user documents exist
        user_doc = None
        for doc in user_docs:
            user_doc = doc
            break  # Only take the first matching document

        if not user_doc:
            return jsonify({"error": f"Email {email} not found in 'users' collection"}), 404

        # Get input data
        umur = float(data.get('Umur (Tahun)', 0))
        tekanan_sistolik = float(data.get('Tekanan Sistolik (mmHg)', 0))
        tekanan_diastolik = float(data.get('Tekanan Diastolik (mmHg)', 0))
        gula_darah = float(data.get('Gula darah', 0))
        temperatur_tubuh = float(data.get('Temperatur tubuh (F)', 0))
        detak_jantung = float(data.get('Detak Jantung', 0))

        # Prepare the input array
        user_input = np.array([[umur, tekanan_sistolik, tekanan_diastolik, gula_darah, temperatur_tubuh, detak_jantung]])

        # Normalize the input using the trained scaler
        user_input_scaled = scaler.transform(user_input)

        # Reshape for LSTM input (samples, time_steps=1, features)
        user_input_scaled = user_input_scaled.reshape((user_input_scaled.shape[0], 1, user_input_scaled.shape[1]))

        # Make predictions
        prediction = model.predict(user_input_scaled)

        # Convert prediction from probabilities to class labels
        predicted_class = np.argmax(prediction, axis=1)[0]

        # Mapping categories
        risk_mapping = {0: 'Low Risk', 1: 'Mid Risk', 2: 'High Risk'}
        predicted_risk = risk_mapping[predicted_class]

        # Save input and prediction separately
        input_ref = db.collection("users_inputs").document(email)
        input_ref.set({
            "Umur (Tahun)": umur,
            "Tekanan Sistolik (mmHg)": tekanan_sistolik,
            "Tekanan Diastolik (mmHg)": tekanan_diastolik,
            "Gula darah": gula_darah,
            "Temperatur tubuh (F)": temperatur_tubuh,
            "Detak Jantung": detak_jantung
        }, merge=True)

        prediction_ref = db.collection("users_predictions").document(email)
        prediction_ref.set({
            "predicted_risk": predicted_risk
        }, merge=True)

        # Respond with prediction
        return jsonify({
            "email": email,
            "predicted_risk": predicted_risk
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # Use the port specified in Cloud Run or default to 8080
    app.run(debug=True, host='0.0.0.0', port=port)
