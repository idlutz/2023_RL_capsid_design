from optparse import OptionParser

parser = OptionParser(usage="usage: %prog [options] FILE", version="0.1")
parser.add_option("--input_pdb1", type="string", dest="pdb1", metavar="STR", help="structure to align to pdb2")
parser.add_option("--input_pdb2", type="string", dest="pdb2", metavar="STR", help="template on which to align pdb1")
parser.add_option("--output_pdb", type="string", dest="output_pdb", metavar="STR")

(opts, args) = parser.parse_args()

pdb1 = opts.pdb1
pdb2 = opts.pdb2

cmd.load(pdb1)
cmd.load(pdb2)

name1 = pdb1.split('/')[-1][:-4]
name2 = pdb2.split('/')[-1][:-4]

cmd.do(f"super {name1}, {name2}")

print(name1)

cmd.save(opts.output_pdb, name1)
