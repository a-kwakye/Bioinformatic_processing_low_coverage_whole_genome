#!/usr/bin/env python
# -*- coding: ASCII -*-

import multiprocessing as mp
import os
from subprocess import Popen,PIPE
from sys import argv
import numpy as np

ref_v5 = "/gpfs/scratch/akwakye/mapping_to_genome_with_Y/stickleback_v5_assembly.fa"
ref = "/gpfs/scratch/akwakye/OTHERS/ref_gasAcu1-4/gasAcu1-4.fa"

workdir = os.getcwd()
outdir = '/gpfs/scratch/akwakye/Warfle_22_23_24/mapped/'
readfiledir='/gpfs/scratch/akwakye/Warfle_22_23_24/F24A430001458_LIBucnlR/'
bamdir='/gpfs/scratch/akwakye/Warfle_22_23_24/bams/'
reads_file = open ('reads.list', 'r') #arg1 
reads_data=reads_file.read()
reads_data=reads_data.split('\n')
reads_file.close()
if reads_data[-1]=='':
    del(reads_data[-1])

samp_names=[]
for i in reads_data:
    k=i.split('/')
    samp_names.append(k[-2])

Samples= list(np.unique(samp_names))

idx = list(range(1,len(Samples)+1))

TN5_dict = dict(zip(idx, Samples))

TN5_sample_list = list(TN5_dict)  # list of folders to cycle through
nb_process = len(TN5_sample_list)
nbthreads = 96
batches = []
for g in range(0, nb_process, nbthreads):
    batches.append(TN5_sample_list[g:g + nbthreads])
    

def process_TN5(x, TN5_sample_list, output):
    chrom = TN5_sample_list[x]
    #os.chdir(TN5_dict[chrom])
    Popen.wait(Popen('AdapterRemoval --file1 ' + readfiledir+TN5_dict[chrom]+'/' +TN5_dict[chrom]+'_L1_1.fq.gz --file2 '+ readfiledir+TN5_dict[chrom]+'/' +TN5_dict[chrom]+'_L1_2.fq.gz  --basename ' + outdir+TN5_dict[chrom] + ' --trimns --trimqualities --collapse --gzip', shell=True))
    
    Popen.wait(Popen('bwa mem -M -t 1 ' + ref + ' ' + outdir+TN5_dict[chrom] + '.pair1.truncated.gz ' +outdir+TN5_dict[chrom] + '.pair2.truncated.gz | samtools view -Sb - > ' + bamdir+TN5_dict[chrom] + '_PE.bam', shell=True))
    Popen.wait(Popen('bwa mem -M -t 1 ' + ref + ' '+ outdir+TN5_dict[chrom] + '.collapsed.gz | samtools view -Sb - > ' + bamdir+TN5_dict[chrom] + '_ME.bam', shell=True))
    Popen.wait(Popen('bwa mem -M -t 1 ' + ref + ' ' + outdir+TN5_dict[chrom] + '.collapsed.truncated.gz | samtools view -Sb - > ' + bamdir+TN5_dict[chrom] + '_MEt.bam', shell=True))
    
    output.put('finished ' + TN5_dict[chrom])

for g in range(len(batches)):
    nbthreads2 = len(batches[g])
    output = mp.Queue()
    # Setup a list of processes
    processes = [mp.Process(target=process_TN5, args=(x, batches[g], output)) for x in range(nbthreads2)]
    # Run processes
    for p in processes:
        p.start()

    # Exit the completed processes
    for p in processes:
        p.join()

    results = [output.get() for p in processes]

    print(results)
