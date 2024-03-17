import numpy as np
import pandas as pd
import streamlit as st 
from sklearn.pipeline import make_pipeline
import pickle
import janitor

from selenium import webdriver
from bs4 import BeautifulSoup

model = pickle.load(open(r'model\xgboost_opt.pkl', 'rb'))
url_data = {}
df = pd.read_csv(r'data\df.csv').drop(columns=["price"]).dropna()
fields = df.columns.to_list()

def is_convertible_to_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def clean_data(dirty_df):
    dirty_df = dirty_df.clean_names()
    convertible_mask = dirty_df['case_diameter'].str[:2].apply(is_convertible_to_int)
    dirty_df = dirty_df[convertible_mask]
    dirty_df['case_diameter'] = dirty_df['case_diameter'].str[:2].astype('int')

    # add column of whether the price is negotiable
    dirty_df.insert(loc=13, column='is_negotiable', value=dirty_df['price'].str.contains('Negotiable', case=False).astype(int))

    # keep only CA$ in the `price` column
    dirty_df['price'] = dirty_df['price'].str.extract('C\$([0-9,]+)')[0].str.replace(',', '')
    dirty_df['price'] = pd.to_numeric(dirty_df['price'], errors='coerce')
    dirty_df['price'].fillna(0, inplace=True)
    dirty_df['price'] = dirty_df['price'].astype(int)

    dirty_df = dirty_df.query('price != 0')

    # add column of whether the year of production is approximated
    dirty_df.insert(loc=8, column='year_is_approximated', value=dirty_df['year_of_production'].str.contains('Approximation', case=False).astype(int))

    # Clean year of production
    dirty_df['year_of_production'] = dirty_df['year_of_production'].apply(lambda x: x[:4] if x != 'Unknown' else x)
    dirty_df['year_of_production'] = dirty_df['year_of_production'].replace('Unknown', np.nan)
    dirty_df['year_of_production'] = pd.to_numeric(dirty_df['year_of_production'], errors='coerce')

    # simplify the location to country only
    dirty_df['country'] = dirty_df['location'].str.split(',').str[0]

    clean_df = dirty_df
    return clean_df

def get_data_from_url(url):
    url_data = {}
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # Pretend to be a non-headless browser
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
    options.add_argument("--lang=en-US")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1280,720")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    # time.sleep(np.random.randint(1,10))
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    try:
            title = soup.find('h1', class_="h3 m-y-0").contents[0].strip()
    except:
        title = ''
    try:
        subtitle = soup.find('p', class_="text-md text-sm-lg").contents[0].strip()
    except:
        subtitle = ''
    try:
        rating = soup.find('span', class_='rating').contents[2].strip()
    except:
        rating = 0
    try:
        reviews = soup.find('button', class_="js-link-merchant-reviews link").contents[0].strip()
    except:
        reviews = 0
    try:
        description = soup.find('span', id='watchNotes').get_text(strip=True)
    except:
        description = ''

    content_table = soup.find('table')

    extracted_info = []
    # Loop through each tbody element to handle sections separately
    for tbody in content_table.find_all('tbody'):
        # Check if the section is 'Functions' by looking for a h3 tag
        section_header = tbody.find('h3')
        if section_header and 'Functions' in section_header.text:
            # Directly add the 'Functions' value
            functions = tbody.find('tr').find_next_sibling('tr').text.strip()
            extracted_info.append(('Functions', functions))
        else:
            # Extract other table data
            for tr in tbody.find_all('tr'):
                th = tr.find('strong')
                if th:
                    key = th.text.strip()
                    # Some values might be in 'a' tags or directly in 'td'
                    value = tr.find('td').find_next_sibling('td').text.strip()
                    extracted_info.append((key, value))
    extracted_info.append(('title', title))
    extracted_info.append(('subtitle', subtitle))
    extracted_info.append(('rating', rating))
    extracted_info.append(('reviews', reviews))
    extracted_info.append(('description', description))
    print(extracted_info)
    url_data[0] = extracted_info
    flattened_data = {key: dict(value) for key, value in url_data.items()}
    result_df = pd.DataFrame.from_dict(flattened_data, orient='index')

    clean_df = clean_data(result_df)

    desired_columns = [
    'model', 'movement', 'case_material', 'bracelet_material',
    'year_of_production', 'year_is_approximated', 'condition', 
    'scope_of_delivery', 'country', 'availability', 'case_diameter', 
    'bezel_material', 'crystal', 'dial', 'bracelet_color', 'clasp', 
    'clasp_material', 'rating', 'reviews', 'price', 'is_negotiable'
    ]

    # Create a dictionary to hold your data
    data_dict = {}

    for column in desired_columns:
        if column in clean_df.columns:
            # If the column exists in clean_df, use its values
            data_dict[column] = clean_df[column]
        else:
            # If the column does not exist, fill it with None
            data_dict[column] = None

    # Construct user_selections_df with the data dictionary
    # This ensures all desired columns are included, with NaNs for missing ones
    user_selections_df = pd.DataFrame(data_dict)
    return user_selections_df

def main():
    st.set_page_config(page_title="Rolex Price Prediction App")
    st.image(r'img/header.png')
    st.header("Rolex Price Predictor")
    st.write("Enter the specification and predict the price of a Rolex watch!")
    # st.sidebar.radio('drops sub-menu', options=['add drops', 'view drops'])
    tab1, tab2 = st.tabs(["Predict from URL", "Manual Input"])

    with tab1:
        # st.subheader("Paste a link below to predict the price!")
        url = st.text_input(
        "Paste a link below to predict the price!",
        label_visibility="visible",
        disabled=False,
        placeholder="https://www.chrono24.ca/rolex/rolex-gmt-master-ii--id24333283.htm",
        )
        if st.button("Predict from URL"):
            st.toast("Fetching data from URL...")
            user_selections_df = get_data_from_url(url)
            prediction = model.predict(user_selections_df)

            st.success(f'This Rolex is estimated to sell for CA${prediction[0]:,.0f}')

    with tab2:


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


        if st.button("Predict from manual inputs"):
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
    