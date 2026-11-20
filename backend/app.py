# Superkart Flask Backend

import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize Flask application
superkart_api = Flask("SuperKart")

# Load trained Random Forest pipeline
model = joblib.load("superkart_model.joblib")

# Expected model input columns
FEATURES = list(model.feature_names_in_)


# Home endpoint
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Prediction API"


# Single prediction endpoint
@superkart_api.post("/v1/predict")
def predict_sales():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    missing = [col for col in FEATURES if col not in data]

    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    try:
        # Prepare data in the expected feature order
        input_data = pd.DataFrame([data])[FEATURES]

        # Generate prediction
        prediction = float(model.predict(input_data)[0])

        return jsonify({"Sales": round(prediction, 2)})

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


# Batch prediction endpoint
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():

    if "file" not in request.files:
        return jsonify({"error": "CSV file is required"}), 400

    try:
        file = request.files["file"]
        input_data = pd.read_csv(file)

        missing = [
            col for col in FEATURES
            if col not in input_data.columns
        ]

        if missing:
            return jsonify({"error": f"Missing features: {missing}"}), 400

        input_data = input_data[FEATURES]

        # Generate batch predictions
        predictions = model.predict(input_data)

        # Return predictions indexed by row
        results = {
            str(i): round(float(pred), 2)
            for i, pred in enumerate(predictions)
        }

        return jsonify(results)

    except (ValueError, TypeError, pd.errors.ParserError) as error:
        return jsonify({"error": str(error)}), 400


# Run Flask application
if __name__ == "__main__":
    superkart_api.run(
        host="0.0.0.0",
        port=7860,
        debug=False
    )
