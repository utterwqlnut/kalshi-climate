import pandas as pd
import numpy as np
from scipy import stats


def back_test(df: pd.DataFrame, min_prob, kde_factor,bias,multiplier):
    num_successes = 0
    num_fails = 0

    for i in range(len(df)):
        
        truth = round(df.iloc[i,-1])
        ensemble = pd.to_numeric(df.iloc[i,1:-1])
        ensemble *= multiplier
        ensemble += bias
        kde = stats.gaussian_kde(ensemble.to_numpy(),bw_method=kde_factor)
        
        smol = round(min(ensemble))
        big = round(max(ensemble))

        initial_min = smol if smol % 2 == 1 else smol-1
        kr_range = [(i,i+1) for i in range(initial_min, big, 2)]
        
        trueL = truth if truth%2 == 1 else truth-1
        true_range = (trueL,trueL+1)

        max_cdf = 0
        best_range = (0,0)

        for range_ in kr_range:
            rangeL = range_[0]-0.5
            rangeR = range_[1]+0.5

            new_grid = np.linspace(rangeL,rangeR,int((rangeR-rangeL)/0.01))
            # dx = 0.01

            cdf = np.trapezoid(kde(new_grid),x=new_grid)

            if cdf > max_cdf:
                max_cdf = cdf
                best_range = range_

        if max_cdf > min_prob:
            if best_range == true_range:
                num_successes += 1
            else:
                num_fails += 1

    return num_successes, num_fails
        