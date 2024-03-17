import numpy as np
import pandas as pd
import streamlit as st 
from sklearn.pipeline import make_pipeline
import pickle

model = pickle.load(open(r'model\xgboost_opt.pkl', 'rb'))
# print(model)

def main():
    st.set_page_config(page_title="Rolex Price Prediction App")
    st.image(r'img/header.png')
    st.header("Rolex Price Predictor")
    st.write("Enter the specification and predict the price of a Rolex watch!")
    st.sidebar.radio('drops sub-menu', options=['add drops', 'view drops'])
    

    df = pd.read_csv(r'data\df.csv').drop(columns=["price"]).dropna()
    fields = df.columns.to_list()

    # Adjust slider configurations with default single value, not list
    slider_configs = {
        'rating': {'range': (1.0, 5.0), 'step': 0.1, 'default': float(np.median(df['rating'].dropna()))},
        'case_diameter': {'range': (13, 50), 'step': 1, 'default': int(np.median(df['case_diameter'].dropna()))},
        'reviews': {'range': (0, 10000), 'step': 50, 'default': int(np.median(df['reviews'].dropna()))},
    }

    # Binary fields with "Yes"/"No" options and default values
    binary_options = {
        'year_is_approximated': {'options': ['Yes', 'No'], 'default': 'No'},
        'is_negotiable': {'options': ['Yes', 'No'], 'default': 'No'}
    }

    unsorted_fields = ['condition', 'scope_of_delivery', 'country', 'availability']

    # Generate selectbox options with default values where applicable
    selectbox_options = {}
    for field in fields:
        friendly_name = ' '.join(word.capitalize() for word in field.split('_'))
        if field in binary_options:
            options = binary_options[field]['options']
            default = binary_options[field]['default']
            selectbox_options[friendly_name] = (field, options, options.index(default))
        elif field in unsorted_fields:
            options = df[field].unique().tolist()
            selectbox_options[friendly_name] = (field, options, 0)  # Default to the first option
        else:
            options = sorted(df[field].unique().tolist())
            selectbox_options[friendly_name] = (field, options, 0)  # Default to the first option

    user_selections = {}

    # Iterate through the dictionary to create input widgets and store selections
    for category, (original_field_name, options, default_index) in selectbox_options.items():
        if original_field_name in slider_configs:
            config = slider_configs[original_field_name]
            selected_option = st.slider(category, min_value=config['range'][0], max_value=config['range'][1],
                                        value=config['default'], step=config['step'])
        else:
            selected_option = st.selectbox(category, options, index=default_index)
        user_selections[original_field_name] = selected_option


    if st.button("Predict"):
        # Convert user selections to DataFrame for prediction
        user_selections_df = pd.DataFrame([user_selections])

        # Convert back to 1 and 0
        user_selections_df['year_is_approximated'] = user_selections_df['year_is_approximated'].map({'Yes': 1, 'No': 0})
        user_selections_df['is_negotiable'] = user_selections_df['is_negotiable'].map({'Yes': 1, 'No': 0})
        # print(user_selections_df)

        prediction = model.predict(user_selections_df)

        st.success(f'This Rolex is estimated to sell for CA${prediction[0]:,.0f}')

      
if __name__=='__main__': 
    main() 
    