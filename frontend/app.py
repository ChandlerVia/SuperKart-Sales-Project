
# ==========================================
# SUPERKART STREAMLIT FRONTEND
# ==========================================

import os
import pandas as pd
import requests
import streamlit as st

# Flask backend address on the Docker network
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://backend:7860"
)

# Configure Streamlit page
st.set_page_config(
    page_title="SuperKart Sales Prediction",
    page_icon="🛒",
    layout="centered"
)

st.title("🛒 SuperKart Sales Prediction")

st.write(
    "Predict product-store sales revenue using "
    "the trained Random Forest model."
)

# ==========================================
# SINGLE PREDICTION
# ==========================================

st.header("Single Sales Prediction")

with st.form("prediction_form"):

    st.subheader("Product Information")

    product_weight = st.number_input(
        "Product Weight",
        min_value=0.0,
        value=12.66,
        step=0.01
    )

    sugar_content = st.selectbox(
        "Product Sugar Content",
        ["Low Sugar", "Regular", "No Sugar"]
    )

    allocated_area = st.number_input(
        "Product Allocated Area",
        min_value=0.0,
        max_value=1.0,
        value=0.027,
        format="%.3f"
    )

    product_mrp = st.number_input(
        "Product MRP",
        min_value=0.0,
        value=117.08,
        step=0.01
    )

    product_id_char = st.selectbox(
        "Product ID Category",
        ["FD", "DR", "NC"]
    )

    product_type_category = st.selectbox(
        "Product Type Category",
        ["Perishables", "Non Perishables"]
    )

    st.subheader("Store Information")

    store_size = st.selectbox(
        "Store Size",
        ["Small", "Medium", "High"],
        index=1
    )

    city_type = st.selectbox(
        "Store Location City Type",
        ["Tier 1", "Tier 2", "Tier 3"],
        index=1
    )

    store_type = st.selectbox(
        "Store Type",
        [
            "Supermarket Type1",
            "Supermarket Type2",
            "Departmental Store",
            "Food Mart"
        ],
        index=1
    )

    store_age = st.number_input(
        "Store Age (Years, reference year 2026)",
        min_value=0,
        value=17,
        step=1
    )

    submitted = st.form_submit_button(
        "Predict Sales",
        type="primary"
    )

# Prepare the JSON input for Flask
product_data = {
    "Product_Weight": product_weight,
    "Product_Sugar_Content": sugar_content,
    "Product_Allocated_Area": allocated_area,
    "Product_MRP": product_mrp,
    "Store_Size": store_size,
    "Store_Location_City_Type": city_type,
    "Store_Type": store_type,
    "Product_Id_char": product_id_char,
    "Store_Age_Years": store_age,
    "Product_Type_Category": product_type_category
}

if submitted:

    try:
        response = requests.post(
            f"{BACKEND_URL}/v1/predict",
            json=product_data,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()
        predicted_sales = float(result["Sales"])

        st.success("Prediction completed successfully!")

        st.metric(
            label="Predicted Product-Store Sales Total",
            value=f"{predicted_sales:,.2f}"
        )

    except requests.exceptions.RequestException as error:
        st.error(f"Unable to contact prediction API: {error}")

    except (ValueError, KeyError, TypeError) as error:
        st.error(f"Invalid prediction response: {error}")


# ==========================================
# BATCH PREDICTION
# ==========================================

st.divider()

st.header("Batch Sales Prediction")

st.write(
    "Upload a CSV file containing the ten "
    "required model input features."
)

uploaded_file = st.file_uploader(
    "Upload CSV",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        preview_df = pd.read_csv(uploaded_file)

        st.write("Uploaded Data Preview:")
        st.dataframe(preview_df.head())

        uploaded_file.seek(0)

        if st.button("Predict Batch", type="primary"):

            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file,
                        "text/csv"
                    )
                },
                timeout=60
            )

            response.raise_for_status()

            results = response.json()

            predictions_df = pd.DataFrame({
                "Row": list(results.keys()),
                "Predicted Sales": list(results.values())
            })

            st.success("Batch predictions completed successfully!")

            st.dataframe(
                predictions_df,
                use_container_width=True
            )

            csv_output = predictions_df.to_csv(index=False)

            st.download_button(
                label="Download Predictions",
                data=csv_output,
                file_name="superkart_predictions.csv",
                mime="text/csv"
            )

    except requests.exceptions.RequestException as error:
        st.error(f"Batch prediction API error: {error}")

    except (ValueError, TypeError, pd.errors.ParserError) as error:
        st.error(f"Unable to process CSV or response: {error}")

st.caption(
    "Predictions are estimates and may differ "
    "from actual sales."
)
