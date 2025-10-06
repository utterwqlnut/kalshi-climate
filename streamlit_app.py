import streamlit as st
import plotly.figure_factory as ff
import numpy as np
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

def get_top_of_page():
    st.markdown("# Kalshi Climate Prediction ☁️")

    backtest = st.checkbox('**Backtest**')

    col1,col2,col3,col4,col5 = st.columns(5)

    location = col1.selectbox(
        'What location?',
        ['NYC', 'Miami', 'Chicago', 'Denver', 'Austin', 'Los Angeles', 'Philadelphia']
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

    kde_factor = col4.slider(
        'KDE Scott Bandwidth Factor',
        0.0,
        2.0,
        1.0,
    )

    min_prob = col5.slider(
        'Minimum probability',
        0.0,
        100.0,
        50.0
    )
    
    return backtest, location, forecast, cl, kde_factor, min_prob/100
    
def render_non_backtest(kde, forecasts, mean, std, ci, entropy, min_prob):
    grid = np.linspace(min(forecasts),max(forecasts),int((max(forecasts)-min(forecasts))/0.01)) # dx is 0.01
    pdf = kde(grid)

    fig1 = px.histogram(forecasts,histnorm='probability density',range_x=[min(forecasts),max(forecasts)],opacity=0.5)
    fig2 = px.line(y=pdf,x=grid)
    
    fig = go.Figure(data = fig1.data+fig2.data)

    st.plotly_chart(fig)

    # Add a streamlit input field for range
    smol = round(min(forecasts))
    big = round(max(forecasts))
    initial_min = smol if smol % 2 == 1 else smol-1
    kr_range = st.selectbox("Enter kalshi range",
                 [str(i)+"-"+str(i+1) for i in range(initial_min, big, 2)]
                )
    
    rangeL = float(kr_range.split('-')[0])-0.5
    rangeR = float(kr_range.split('-')[1])+0.5
    new_grid = np.linspace(rangeL,rangeR,int((rangeR-rangeL)/0.01))

    # dx = 0.01
    cdf = np.trapezoid(kde(new_grid),x=new_grid)

    st.markdown(f"> Confidence Interval: [{ci[0]:.2f}, {ci[1]:.2f}]")
    st.markdown(f"> Mean and Std Forecast: {mean:.2f}, {std:.2f}")
    st.markdown(f"> Entropy: {entropy:.2f}")

    if cdf > min_prob:
        st.markdown(f"### Trade Yes: Predicted Cumalitive Probability: {cdf:.2f}")
    else:
        st.markdown(f"### Trade No: Predicted Cumalitive Probability: {cdf:.2f}")

def render_backtest(num_sucess,num_fail):
    odds = num_sucess/(num_sucess+num_fail)
    num_acted = num_sucess+num_fail

    st.markdown(f"### Odds: {odds*100:.2f}%")
    st.markdown(f"### Your model executed {num_acted} trades during the test. Only undergo a trade with this model if the kalshi odds are lower than {odds*100:.2f}")

def render_error(str):
    st.markdown("### "+str)