import streamlit_app
from api import OpenMeteoAPI
import numpy as np
from scipy import stats
from backtest import back_test
from scipy.stats import gaussian_kde

def interp_forecasts(forecasts,cl,kde_factor):
    mean = forecasts.mean()
    std = forecasts.std(ddof=1)

    kde = gaussian_kde(forecasts,bw_method=kde_factor)

    confidence_interval = stats.t.interval(cl,
                                    df=len(forecasts)-1,
                                    loc=mean,
                                    scale=std
                                    )
                                    
     
    # Bins based on bin width
    num_bins = int(np.ceil((max(forecasts) - min(forecasts))/(0.05)))
    pdf,bins = np.histogram(forecasts,bins=num_bins)
    entropy = stats.entropy(pdf+1e-9)

    return kde, forecasts.mean(), forecasts.std(ddof=1), confidence_interval, entropy


def main():
    # Get inputs
    api = OpenMeteoAPI()
    backtest, location, forecast, cl, kde_factor, min_prob, models = streamlit_app.get_top_of_page(api.get_models())

    if backtest:
        try:
            back_df = api.pull_backtest(forecast,location,models)
            num_success, num_fail = back_test(back_df,min_prob,kde_factor)
            streamlit_app.render_backtest(num_success,num_fail)
        except Exception as e:
            streamlit_app.render_error(str(e))
    else:
        forecasts = api.pull_forecast(forecast,location,models)
        kde, mean, std, ci, entropy = interp_forecasts(forecasts, cl/100, kde_factor)
        streamlit_app.render_non_backtest(kde,forecasts, mean, std, ci, entropy, min_prob)

    
if __name__ == '__main__':
    main()
