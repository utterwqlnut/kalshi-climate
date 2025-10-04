import pandas as pd
import numpy as np
from scipy import stats

def back_test(df: pd.DataFrame, entrop_req):
    num_successes = 0
    num_fails = 0

    for i in range(len(df)):
        truth = df.iloc[i,-1]
        ensemble = df.iloc[i,1:]

        mean = ensemble.mean()
        try:
            num_bins = int(np.ceil((max(ensemble) - min(ensemble))/(0.05)))
        except:
            continue

        pdf,bins = np.histogram(ensemble,bins=num_bins)
        entropy = stats.entropy(pdf+1e-9)
        
        if entropy < entrop_req:
            # Executing Trade
            lbound = 0
            hbound = 0

            truth = round(truth)
            mean = round(mean)
            if truth % 2 == 0:
                lbound = truth - 1
                hbound = truth
            else:
                lbound = truth
                hbound = truth + 1
            
            if mean >= lbound and mean <= hbound:
                num_successes += 1
            else:
                num_fails += 1

    return num_successes, num_fails
        