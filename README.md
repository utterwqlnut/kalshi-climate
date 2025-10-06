# Kalshi Climate
> This project aims to provide a tool to forecast highest temperature trades on kalshi and inform decisions

## Features

### Forecaster
- Uses the OpenMeteo api, to provide ensemble climate predictions with multiple models
- Fits a probability distribution with Gaussian KDE and users
- Using probability distribution users can find probabilities of kalshi ranges and also statistics about the distribution

### Back Testing (Currently having issues as the historical forecasts have lead times <1day)
- Tune the upper limit of entropy for distributions you wish to trade on
- Test on historical forecasts and highs to get odds of your model

### Streamlit
- Built on streamlit this is meant to be any easy to use tool to make profit on kalshi climate markets
To use run:
```
pip install -r requirments.txt
streamlit run main.py
```
<img width="483" height="579" alt="Screenshot 2025-10-06 at 1 50 09 AM" src="https://github.com/user-attachments/assets/1143b3b0-6e9b-4212-a01a-490cc8bc3c35" />
