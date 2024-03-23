# Rolex Fair Price Predictor

The Rolex Fair Price Predictor is a XGBoost model aimed at estimating the fair market price of any Rolex watches, given its specification and condition.  
  
This project leverages data scraped from [chrono24.ca](https://www.chrono24.ca/) as of February 22, 2024.  

The Jupyter notebook [Rolex_price_prediction.ipynb](Rolex_price_prediction.ipynb) contains details of the model development and rationales.

## Getting Started

### Online Prediction (Recommended)

For ease of use and quick access, utilize the [Streamlit app](https://rolexpricepredictor.streamlit.app/). Simply input the URL of a Rolex listing from [chrono24.ca](https://www.chrono24.ca/) to receive an instant price prediction.

### Local Setup

Clone this repository and make predictions using `model/xgboost_opt.pkl` locally.

## Contributing

We welcome contributions to the Rolex Fair Price Predictor! For guidelines on how to contribute, please read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## Authors
**Sam Fo** - *Initial Work* - [Github](https://github.com/fohy24)

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments
All data belongs to [chrono24.ca](https://www.chrono24.ca/).