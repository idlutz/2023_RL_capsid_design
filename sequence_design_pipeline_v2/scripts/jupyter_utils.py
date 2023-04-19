import math
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

