from optparse import OptionParser

##################################################################################
# Option Parser
##################################################################################

parser = OptionParser(usage="usage: %prog [options] FILE", version="0.1")
parser.add_option("--pdb_in", type="string", dest="pdb_in", metavar="STR", help="")
parser.add_option("--pdb_out", type="string", dest="pdb_out", metavar="STR", help="")
parser.add_option("--only_chainB", type="string", dest="only_chainB", metavar="STR", help="")


(opts, args) = parser.parse_args()
parser.set_defaults()

cmd.load(opts.pdb_in)
if opts.only_chainB == '1':
    cmd.select('test', 'chain B')
else:
    cmd.select('test', 'bychain (chain A around 8) or (chain A)')

cmd.extract('ex', 'test')
cmd.save(opts.pdb_out,'ex')



