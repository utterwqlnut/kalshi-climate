import streamlit as st
import plotly.figure_factory as ff

def get_top_of_page():
    st.markdown("# Kalshi Climate Prediction ☁️")

    backtest = st.checkbox('**Backtest**')

    col1,col2,col3,col4 = st.columns(4)

    location = col1.selectbox(
        'What location?',
        ['Nyc', 'Miami', 'Chicago', 'Denver', 'Austin', 'Houston', 'Philadelphia']
    )

    forecast = col2.selectbox(
        "Forecast Length",
        ['Today','Tomorrow']
    )

    cl = col3.slider(
        'Confidence Level',
        0,
        100,
        95,
    )
    entrop_req = col4.slider(
        'Required Entropy',
        0.0,
        6.0,
        3.0,
    )
    
    return backtest, location, forecast, cl, entrop_req
    
def render_non_backtest(confidence_interval, forecasts, mean, std, cl, entrop_req, entropy):
    fig = ff.create_distplot(
        [forecasts], ["Ensemble Forecasts"], bin_size=[0.1], show_curve=True, show_hist=True,show_rug=True
    )
    st.plotly_chart(fig)
    # Perform Rounding done by NWS
    st.markdown(f"> Confidence Interval at **{cl}%**: [{confidence_interval[0]:.2f},{confidence_interval[1]:.2f}]")
    st.markdown(f"> Mean and Std Forecast: {mean:.2f}, {std:.2f}")
    st.markdown(f"> Entropy: {entropy:.2f}")
    
    if  entropy < entrop_req:
        st.markdown(f"#### Entropy Requirment Met, Trade ✅")
        st.markdown(f"#### Trade: {round(mean)}°")
    else:
        st.markdown(f"#### Entropy Requirment Not Met, Trade ❌")

def render_backtest(num_sucess,num_fail):
    odds = num_sucess/(num_sucess+num_fail)
    num_acted = num_sucess+num_fail

    st.markdown(f"### Odds: {odds*100:.2f}%")
    st.markdown(f"### Your model executed {num_acted} trades during the test. Only undergo a trade with this model if the kalshi odds are lower than {odds*100:.2f}")

def render_error(str):
    st.markdown("### "+str)