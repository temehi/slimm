#!/usr/bin/env python
import argparse
import glob
import os
import re
import gzip

parser = argparse.ArgumentParser(description =
''' Merge downloaded reference genomes in to one single fasta file.
Contigs will be delimited by a sequence of NNNs
''', formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-i', '--input_dir', type=str, required=True,
                    help = 'The path of directory where fasta files are located')
parser.add_argument('-o', '--output_file', type=str, required=True,
                    help = 'The path of to the merged output file')
parser.add_argument('-t', '--tsv_file', type=str, required=True,
                    help = '''tsv files containing taxas to download and their corresponding FTP path.
                                a result from running select_refs.py''')


args = parser.parse_args()

input_dir = args.input_dir
output_file = args.output_file
tsv_file = args.tsv_file
testing = False


to_merge = {}
missed_count = 0
missing_files = False
inpf = open(tsv_file, 'r')
for line in inpf:
    if line[0] == "#":
        continue
    # if not firstLine:
    l = line.replace("\n", "").split('\t')
    fna_file_name = l[7]
    if (os.path.isfile(input_dir + "/" + fna_file_name) ) :
        to_merge[fna_file_name] = os.path.abspath(input_dir + "/" + fna_file_name)
    else :
        missed_count += 1
        missing_files = True
inpf.close()

if missing_files:
    print str(missed_count) + " are missing!"

outf = open(output_file, 'w')
global_count = 0
test_count = 0
for fna_file_name in to_merge:
    if test_count == 10 and testing:
        break
    test_count += 1
    fasta_file = to_merge[fna_file_name]
    global_count += 1
    inpf = gzip.open(fasta_file, 'rb')
    current_seq = ""
    count = 0
    plasmid_count = 0
    line_len = 0
    is_plasmid = False
    for line in inpf:
        if re.search("\>", line):
            is_plasmid = "plasmid" in line.lower()
            if is_plasmid:
                plasmid_count += 1
                continue
            if count == 0:
                outf.write(line)
            else:
                outf.write((line_len * "N") +"\n")
            current_seq = ""
            count += 1
        elif not is_plasmid :
            outf.write(line)
            if line_len == 0:
                line_len = len(line) -1
    print "added " + fasta_file + "[" + str(global_count) + "/" + str(len(to_merge)) + "]"
    print str(count) + " seqs\t", plasmid_count ,"plasmids\tall seqs writeen delimated by aline of N's. all_plasmids are ignored"
    inpf.close()
outf.close()
print "merged file written to " + output_file
