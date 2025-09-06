import string
import os
from subprocess import Popen,PIPE
from sys import argv
import gzip
import multiprocessing as mp

file_list=argv[1]#'bamF.list'
indel_file='/gpfs/projects/VeeramahGroup/Stickleback/genome_vcf/stickleback_SNP_indel_Kingman/206_genomes.bootstrapping.INDELs.double_hard_filtered.vcf'
snp_file='/gpfs/projects/VeeramahGroup/Stickleback/genome_vcf/stickleback_SNP_indel_Kingman/206_genomes.bootstrapping.SNPs.double_hard_filtered.vcf'
ref='/gpfs/projects/VeeramahGroup/Stickleback/genome_vcf/gasAcu1-4/gasAcu1-4.fa'
nbthreads=int(argv[2]) 

file=open(file_list,'r')
data=file.read()
data=string.split(data,'\n')
if data[-1]=='':
    del(data[-1])


samps=[]
for g in range(len(data)):
    k=string.split(data[g],'/')
    samp_name=string.split(k[-1],'.')[0]
    stem=string.split(k[-1],'.bam')[0]
    bam=data[g]
    samps.append([samp_name,stem,bam])

nb_process=len(samps)

batches=[]
for g in range(0,nb_process,nbthreads):
    batches.append(samps[g:g+nbthreads])

if nbthreads>nb_process:
    nb_process_excess=nbthreads/nb_process
else:
    nb_process_excess=1

print nb_process_excess

cwd = os.getcwd()


def realign_BQSR_MP(x,splits,ref,indel_file,snp_file,cwd,nb_process_excess,output):
    os.chdir(cwd)

    samp_name=splits[x][0]
    stem=splits[x][1]
    bam=splits[x][2]


    #creating recalibration table
    run_string=''
    run_string=run_string+'java -Xmx20G -jar /gpfs/software/Anaconda2/opt/gatk-3.7/GenomeAnalysisTK.jar -T BaseRecalibrator'
    run_string=run_string+' -R '+ref
    run_string=run_string+' -I '+stem+'.bam' # changed from .realign.bam
    run_string=run_string+' -knownSites '+snp_file
    run_string=run_string+' -o recal_data.'+samp_name+'.iteration1.table'
    run_string=run_string+' -nct '+str(nb_process_excess)

    Popen.wait(Popen(run_string,shell=True))

    #applying recalibration table
    run_string=''
    run_string=run_string+'java -Xmx20G -jar /gpfs/software/Anaconda2/opt/gatk-3.7/GenomeAnalysisTK.jar -T PrintReads'
    run_string=run_string+' -R '+ref
    run_string=run_string+' -I '+stem+'.bam'
    run_string=run_string+' -BQSR recal_data.'+samp_name+'.iteration1.table'
    run_string=run_string+' -o '+stem+'.BQrecal.bam'
    run_string=run_string+' -nct '+str(nb_process_excess)

    Popen.wait(Popen(run_string,shell=True))

    #index recalibrated bam
    Popen.wait(Popen('samtools index '+stem+'.BQrecal.bam',shell=True))

    #creating recalibration table 2nd version
    run_string=''
    run_string=run_string+'java -Xmx20G -jar /gpfs/software/Anaconda2/opt/gatk-3.7/GenomeAnalysisTK.jar -T BaseRecalibrator'
    run_string=run_string+' -R '+ref
    run_string=run_string+' -I '+stem+'.BQrecal.bam'
    run_string=run_string+' -knownSites '+snp_file
    run_string=run_string+' -o recal_data.'+samp_name+'.iteration2.table'
    run_string=run_string+' -nct '+str(nb_process_excess)

    Popen.wait(Popen(run_string,shell=True))

    #generating BQSR report
    run_string=''
    run_string=run_string+'java -Xmx20G -jar /gpfs/software/Anaconda2/opt/gatk-3.7/GenomeAnalysisTK.jar -T AnalyzeCovariates'
    run_string=run_string+' -R '+ref
    run_string=run_string+' -before recal_data.'+samp_name+'.iteration1.table'
    run_string=run_string+' -after recal_data.'+samp_name+'.iteration2.table'
    run_string=run_string+' -l DEBUG'
    run_string=run_string+' -csv my-report.'+samp_name+'.csv'
    run_string=run_string+' -plots '+stem+'.BQrecal.pdf'

    Popen.wait(Popen(run_string,shell=True))

    Popen.wait(Popen('Rscript BQSR.R my-report.'+samp_name+'.csv recal_data.'+samp_name+'.iteration1.table '+stem+'.BQrecal.pdf',shell=True))

    output.put('finished '+samp_name)

for g in range(len(batches)):
    nbthreads2=len(batches[g])

    ###queue for parallelism output
    output = mp.Queue()

    # Setup a list of processes
    processes = [mp.Process(target=realign_BQSR_MP, args=(x,batches[g],ref,indel_file,snp_file,cwd,nb_process_excess,output)) for x in range(nbthreads2)]
    # Run processes
    for p in processes:
        p.start()

    # Exit the completed processes
    for p in processes:
        p.join()

    results = [output.get() for p in processes]
    print(results)

