from optparse import OptionParser
import numpy as np
import sys

import pyrosetta
import pyrosetta.distributed.io as io
import pyrosetta.distributed.packed_pose as packed_pose
import pyrosetta.distributed.tasks.rosetta_scripts as rosetta_scripts
import pyrosetta.distributed.tasks.score as score
pyrosetta.init('-mute all')

##################################################################################
# Option Parser
##################################################################################

parser = OptionParser(usage="usage: %prog [options] FILE", version="0.1")
parser.add_option("--rainity_npz", type="string", dest="npz", metavar="STR", help="Output npz file from rainity")
parser.add_option("--pssmOut", type="string", dest="pssmOut", metavar="STR", help="Output PSSM")
parser.add_option("--chA_dir", type="string", dest="dir", metavar="STR", help="Input chA directory")

(opts, args) = parser.parse_args()
parser.set_defaults()

# main
input_dir = '/home/swang523/Crystal_engineering/interface_redesign_pssm/T32C-13/design/full_cage_design/input' ### change chainA_path
prob = np.load(opts.npz, allow_pickle=True)['pssm'][0]
pdbname = (opts.npz).split('/')[-1].replace('prediction_','')[:-4]+'.pdb'
chainA_path = f'{input_dir}/{pdbname}' 
seq = str(pyrosetta.pose_from_file(chainA_path).chain_sequence(1))
L = len(seq)

seqB = str(pyrosetta.pose_from_file(chainA_path).chain_sequence(2))
LB = len(seqB)
    
prob_cA = prob[:L]
prob_cB = prob[int(L)+1:int(L+LB)+1]

# Data from BLOSUM62 ncbi-blast-2.6.0+-src/c++/src/algo/blast/composition_adjustment/matrix_frequency_data.c
bg_freqs = np.array([7.4216205067993410e-02, 5.1614486141284638e-02, 4.4645808512757915e-02,
 5.3626000838554413e-02, 2.4687457167944848e-02, 3.4259650591416023e-02,
 5.4311925684587502e-02, 7.4146941452644999e-02, 2.6212984805266227e-02,
 6.7917367618953756e-02, 9.8907868497150955e-02, 5.8155682303079680e-02,
 2.4990197579643110e-02, 4.7418459742284751e-02, 3.8538003320306206e-02,
 5.7229029476494421e-02, 5.0891364550287033e-02, 1.3029956129972148e-02,
 3.2281512313758580e-02, 7.2919098205619245e-02])
bg_freqs = bg_freqs / bg_freqs.sum()

pssm_cA = np.log(prob[:L]/bg_freqs)
pssm_cB = np.log(prob[int(L)+1:int(L+LB)+1]/bg_freqs)
    
with open((opts.pssmOut).replace('.pssm','_chA.pssm'), 'w') as f_out:
    f_out.write('\n')
    f_out.write('Last position-specific scoring matrix computed, weighted observed percentages rounded down, information per position, and relative weight of gapless real matches to pseudocounts\n')
    f_out.write('            A   R   N   D   C   Q   E   G   H   I   L   K   M   F   P   S   T   W   Y   V   A   R   N   D   C   Q   E   G   H   I   L   K   M   F   P   S   T   W   Y   V\n')

    for i, odds in enumerate(pssm_cA):
        aa = seq[i]
        pos = str(i+1)
        odds_str = ' '.join([str(x) for x in pssm_cA[i]])
        occ_str = ' '.join([str(x) for x in prob_cA[i]])
        f_out.write(pos+' '+aa+' '+odds_str+' '+occ_str+' 0.00 0.00'+'\n')
    f_out.write('\n\n\n\n')
    
with open((opts.pssmOut).replace('.pssm','_chB.pssm'), 'w') as f_out:
    f_out.write('\n')
    f_out.write('Last position-specific scoring matrix computed, weighted observed percentages rounded down, information per position, and relative weight of gapless real matches to pseudocounts\n')
    f_out.write('            A   R   N   D   C   Q   E   G   H   I   L   K   M   F   P   S   T   W   Y   V   A   R   N   D   C   Q   E   G   H   I   L   K   M   F   P   S   T   W   Y   V\n')

    for i, odds in enumerate(pssm_cB):
        aa = seqB[i]
        pos = str(i+1)
        odds_str = ' '.join([str(x) for x in pssm_cB[i]])
        occ_str = ' '.join([str(x) for x in prob_cB[i]])
        f_out.write(pos+' '+aa+' '+odds_str+' '+occ_str+' 0.00 0.00'+'\n')
    f_out.write('\n\n\n\n')