# paired end processing 

echo sorting PE bam file
samtools sort -o  $1_PE.sort.bam  $1_PE.bam

echo indexing file PE bam file
samtools index  $1_PE.sort.bam

echo adding readgroups PE
picard AddOrReplaceReadGroups I= $1_PE.sort.bam O= $1_PE.sort.RG.bam LB=Veeramah PL=ILLUMINA PU=BGI RGSM=$1  CN=BGI RGID=$1 VALIDATION_STRINGENCY=SILENT

echo sorting bam file with readgroups PE 

samtools sort -o $1_PE.sort.RG.sort.bam $1_PE.sort.RG.bam

echo indexing readgroups PE
samtools index  $1_PE.sort.RG.sort.bam

echo markduplicates
picard MarkDuplicates I=$1_PE.sort.RG.sort.bam O=$1_PE.sort.RG.sort.Mkdup.bam AS=TRUE M=$1_PE_merged.sort.RG.finalmerge.resort.metrics REMOVE_DUPLICATES=FALSE VALIDATION_STRINGENCY=LENIENT

echo indexing readgroups file
samtools index $1_PE.sort.RG.sort.Mkdup.bam

echo flagstat PE
samtools flagstat  $1_PE.sort.RG.sort.Mkdup.bam >  $1_PE.sort.RG.sort.Mkdup.flagstat


# single end reads 

echo sorting ME bam file
samtools sort -o  $1_ME.sort.bam  $1_ME.bam

echo indexing file ME bam file
samtools index  $1_ME.sort.bam

echo adding readgroups ME
picard AddOrReplaceReadGroups I= $1_ME.sort.bam O= $1_ME.sort.RG.bam LB=Veeramah PL=ILLUMINA PU=BGI RGSM=$1  CN=BGI RGID=$1 VALIDATION_STRINGENCY=SILENT

echo sorting bam file with readgroups ME 

samtools sort -o $1_ME.sort.RG.sort.bam $1_ME.sort.RG.bam

echo indexing readgroups ME
samtools index  $1_ME.sort.RG.sort.bam

echo markduplicates
picard MarkDuplicates I=$1_ME.sort.RG.sort.bam O=$1_ME.sort.RG.sort.Mkdup.bam AS=TRUE M=$1_ME_merged.sort.RG.finalmerge.resort.metrics REMOVE_DUPLICATES=FALSE VALIDATION_STRINGENCY=LENIENT

echo indexing readgroups file
samtools index $1_ME.sort.RG.sort.Mkdup.bam

echo flagstat ME
samtools flagstat  $1_ME.sort.RG.sort.Mkdup.bam >  $1_ME.sort.RG.sort.Mkdup.flagstat


# merging bams 
echo merging PE and ME bam files

samtools merge $1.PE_ME.RG.Mkdup.bam $1_ME.sort.RG.sort.Mkdup.bam $1_PE.sort.RG.sort.Mkdup.bam

samtools sort -o $1.PE_ME.RG.Mkdup.sort.bam $1.PE_ME.RG.Mkdup.bam

echo indexing sorted bam file
samtools index  $1.PE_ME.RG.Mkdup.sort.bam


echo flagstat final_merge
samtools flagstat  $1.PE_ME.RG.Mkdup.sort.bam >  $1.PE_ME.RG.Mkdup.sort.flagstat


rm $1_ME.sort.RG.sort.Mkdup.bam*
rm $1_ME.sort.RG.sort.bam*
rm $1_ME.sort.RG.bam*
rm $1_ME.sort.bam*

rm $1_PE.sort.RG.sort.Mkdup.bam*
rm $1_PE.sort.RG.sort.bam*
rm $1_PE.sort.RG.bam*
rm $1_PE.sort.bam*





