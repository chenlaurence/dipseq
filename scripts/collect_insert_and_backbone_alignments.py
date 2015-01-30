# -*- coding: utf-8 -*-
# <nbformat>2</nbformat>

import argparse
import numpy as np

from sequtils.read_alignment_data import ReadAlignmentData


parser = argparse.ArgumentParser(description='Filter reads.')
parser.add_argument("-i", "--insert_alignments", nargs='+', required=True,
                    help=("Path to pslx files containing alignments to backbone"))
parser.add_argument("-b", "--backbone_alignments", nargs='+', required=True,
                    help=("Path to pslx files containing alignments to insert"))
parser.add_argument("-r", "--read_filenames", nargs='+', required=True,
                    help="Path to FASTA files containing reads.")
parser.add_argument("-o", "--output_csv_filename", required=True,
                    help="Where to write CSV output to.")
args = parser.parse_args()

insert_aligned_fnames = args.insert_alignments
backbone_aligned_fnames = args.backbone_alignments
fasta_fnames = args.read_filenames

"""
# For testing the script with less data
import glob
insert_aligned_fnames = glob.glob('sequtils/test/data/DFS001_2_index6_GCCAAT_L004_R1_001_clipped100k_insert_aligned.pslx')
backbone_aligned_fnames = glob.glob('sequtils/test/data/DFS001_2_index6_GCCAAT_L004_R1_001_clipped100k_backbone_aligned.pslx')
fasta_fnames = glob.glob('sequtils/test/data/DFS001_2_index6_GCCAAT_L004_R1_001_clipped100k.fa')
"""

# Make sure all the filenames are in the same order so we can zip them.
insert_aligned_fnames = sorted(insert_aligned_fnames)
backbone_aligned_fnames = sorted(backbone_aligned_fnames)
fasta_fnames = sorted(fasta_fnames)
assert insert_aligned_fnames
assert backbone_aligned_fnames
assert fasta_fnames
assert len(insert_aligned_fnames) == len(backbone_aligned_fnames)
assert len(fasta_fnames) == len(insert_aligned_fnames)
print 'Insert aligned filenames'
print insert_aligned_fnames
print 'Backbone aligned filenames'
print backbone_aligned_fnames
print 'FASTA fnames'
print fasta_fnames

# Gather all the reads information by read ID.
read_data_by_id = {}
for insert_fname, backbone_fname, fasta_fname in zip(insert_aligned_fnames,
                                                     backbone_aligned_fnames,
                                                     fasta_fnames):
    print 'Analyzing file set'
    print insert_fname
    print backbone_fname
    print fasta_fname
    read_data_by_id.update(ReadAlignmentData.DictFromFiles(insert_fname,
                                                           backbone_fname,
                                                           fasta_fname))

consistent = [r.has_insertion for r in read_data_by_id.itervalues()]
distances = np.array([r.BackboneInsertDistanceInRead() for r in read_data_by_id.itervalues()])

n_total_w_matches = len(read_data_by_id) 
n_consistent = np.sum(consistent)

print 'Total reads with any matches:', n_total_w_matches
print 'Reads with consistent matches to backbone and insert', n_consistent

import csv

print 'Writing insertion matches to', args.output_csv_filename
with open(args.output_csv_filename, 'w') as f:
    w = csv.DictWriter(f, ReadAlignmentData.DICT_FIELDNAMES)
    w.writeheader()
    for rd in read_data_by_id.itervalues():
        if rd.has_insertion:
            w.writerow(rd.AsDict())

"""
positions = []
positions_3p = []
positions_5p = []
linker_lengths = []
for r in read_data_by_id.itervalues():
    # NOTE: reverse insertions are when the insert and backbone matches are on opposite
    # strands of the read. We may want to quantify these later, but we are ignoring them
    # for now.
    r.CalculateInsertion()
    if r.has_insertion:
        ip = r.insertion_site
        if ip < 0:
            print
            print 'negative insertion site', ip
            print r.insert_hsp
            print r.backbone_hsp
            r.PrettyPrint()
        elif ip > 4107:
            print 
            print 'insertion past stop codon', ip
            print r.insert_hsp
            print r.backbone_hsp
            r.PrettyPrint()
        d = r.BackboneInsertDistanceInRead()
        if d > 15:
            print 'long distance between insert & backbone:', d
            print 'insert position', ip
            print r.insert_hsp
            print r.backbone_hsp
        positions.append(ip)
        linker_lengths.append(r.linker_length)
        if r._insert_match_end == '3p':
            positions_3p.append(ip)
        else:
            positions_5p.append(ip)

import pylab
pylab.figure()
pylab.hist(positions_3p, bins=50, color='b', label='3p insertions')
pylab.hist(positions_5p, bins=50, color='g', label='5p insertions')
pylab.xlabel('Insertion Site (nt)')
pylab.xlim((-30, 4140))
pylab.legend()
pylab.savefig('3p_5p_insert_dist_sample_3.png')
pylab.savefig('3p_5p_insert_dist_sample_3.svg')

pylab.figure()
pylab.hist(positions, bins=50, color='b')
pylab.xlabel('Insertion Site (nt)')
pylab.xlim((-30, 4140))
pylab.savefig('insert_dist_sample_3.png')
pylab.savefig('insert_dist_sample_3.svg')

pylab.figure()
pylab.hist(linker_lengths)
pylab.xlabel('Linker Length')
pylab.savefig('linker_length_sample_3.png')
pylab.savefig('linker_length_sample_3.svg')
pylab.show()
"""
