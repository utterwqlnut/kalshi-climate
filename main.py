import streamlit_app
from api import OpenMeteoAPI
import numpy as np
from scipy import stats
from backtest import back_test

def interp_forecasts(forecasts,cl):
    mean = forecasts.mean()
    std = forecasts.std(ddof=1)

    confidence_interval = stats.t.interval(cl,
                                        df=len(forecasts)-1,
                                        loc=mean,
                                        scale=std/np.sqrt(len(forecasts))
                                        )
    # Bins based on bin width
    num_bins = int(np.ceil((max(forecasts) - min(forecasts))/(0.05)))
    pdf,bins = np.histogram(forecasts,bins=num_bins)
    entropy = stats.entropy(pdf+1e-9)

    return confidence_interval, forecasts.mean(), forecasts.std(ddof=1), entropy

def main():
    # Get inputs
    api = OpenMeteoAPI()
    backtest, location, forecast, cl, entrop_req = streamlit_app.get_top_of_page()

    if backtest:
        try:
            back_df = api.pull_backtest(forecast,location)
            num_success, num_fail = back_test(back_df,entrop_req)
            streamlit_app.render_backtest(num_success,num_fail)
        except Exception as e:
            streamlit_app.render_error("Can only backtest on tomorrow trades")
    else:
        forecasts = api.pull_forecast(forecast,location)
        confidence_interval, mean, std, entropy = interp_forecasts(forecasts,cl/100)
        streamlit_app.render_non_backtest(confidence_interval,forecasts, mean, std, cl, entrop_req, entropy)

    
if __name__ == '__main__':
    main()
