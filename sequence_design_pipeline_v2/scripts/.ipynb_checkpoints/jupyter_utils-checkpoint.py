import math
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import os
import pandas as pd


def make_submit_file(cmds='commands', submitfile='submit.sh', queue='short', group_size=1, logsfolder='logs', mem='4G'):
    n_jobs = sum(1 for line in open(cmds))
    groups = int(np.ceil(float(n_jobs)/group_size))
    os.makedirs(logsfolder, exist_ok=True)
    file = \
    """#!/bin/bash
#SBATCH -p {0}
#SBATCH --mem={5}
#SBATCH -a 1-{1}
#SBATCH -o {4}/out.%a
#SBATCH -e {4}/out.%a

GROUP_SIZE={3}

for I in $(seq 1 $GROUP_SIZE)
do
    J=$(($SLURM_ARRAY_TASK_ID * $GROUP_SIZE + $I - $GROUP_SIZE))
    CMD=$(sed -n "${{J}}p" {2} )
    echo "${{CMD}} > {4}/out.$SLURM_ARRAY_TASK_ID" | bash
done
""".format(queue, groups, cmds, group_size, logsfolder, mem)
    with open(submitfile,'w') as f_out:
        f_out.write(file)

def make_dist_plots(df, relevant_features, hue=None):
    ncols = 3
    nrows = math.ceil(len(relevant_features) / ncols)
    (fig, axs) = plt.subplots(
        ncols=ncols, nrows=nrows, figsize=[15,3*nrows]
    )
    axs = axs.reshape(-1)

    for (i, metric) in enumerate(relevant_features):
        is_int_arr = np.array_equal(df[metric], df[metric].astype(int))
        if False: #is_int_arr:
            c = Counter(df[metric])
            sns.barplot(x=list(c.keys()), y=list(c.values()), ax=axs[i], color='grey')
            axs[i].set_xlabel(metric)
        else:
            if hue is not None:
                labels = set(df[hue])
                for l in labels:
                    dfsub = df[df[hue]==l]
                    sns.distplot(dfsub[metric], ax=axs[i],label=l)
            else:
                sns.distplot(df[metric], ax=axs[i])
    sns.despine()
    plt.legend()
    plt.tight_layout()
    plt.show()

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

