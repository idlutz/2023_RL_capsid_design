## define make_dist_plots_w_hue   #### should clean it up in a python script

import math
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from collections import Counter

def make_dist_plots_w_hue(df, relevant_features, hue=None):
    ncols = 3
    nrows = math.ceil(len(relevant_features) / ncols)
    (fig, axs) = plt.subplots(
        ncols=ncols, nrows=nrows, figsize=[15,3*nrows]
    )
    axs = axs.reshape(-1)

    for (i, metric) in enumerate(relevant_features):
        is_int_arr = np.array_equal(df[metric], df[metric].astype(int))
        if is_int_arr:
            if hue is not None:
                hues = list(set(df[hue]))
                dfs = []
                for h in hues:
                    dfsub = df[df[hue]==h]
                    c = Counter(dfsub[metric])
                    x = list(c.keys())
                    y = list(c.values())
                    d = {metric: x, 'counts':y, hue: h}
                    dfx = pd.DataFrame.from_dict(d)
                    dfs.append(dfx)
                _ = sns.catplot(data=pd.concat(dfs), x=metric, y='counts', hue=hue, ax=axs[i], kind="bar")
            else:
                c = Counter(df[metric])
                sns.barplot(x=list(c.keys()), y=list(c.values()), ax=axs[i], color='grey')
                #axs[i].set_xlabel(metric)
        else:
            if hue is not None:
                labels = set(df[hue])
                for l in labels:
                    #print(df[df[hue]==l][metric])
                    sns.distplot(df[df[hue]==l][metric].astype(float), ax=axs[i],label=l)
                axs[i].legend()
            else:
                sns.distplot(df[metric], ax=axs[i])

    # This is silly but catplot is for some reason making extra plots
    for n in range(2,len(relevant_features)):
        plt.close(n)

    sns.despine()
    plt.tight_layout()
#     plt.show()

