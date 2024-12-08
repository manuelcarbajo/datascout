# datascout
This repo queries and gather data from different resources which can then be used to run bulk automatised annotation of microbial genomes.
The different types of data are: 
  - OrthoDB and UniProt orthology data;
  - Rfam (non coding Rna data);
  - Transcriptomic data from ENA


### Getting this repo

```
git clone git@github.com:manuelcarbajo/datascout
```

### Configuration

#### Refresing environment

This project uses nextflow-24.04.3

### Initialising and running the environment

After downloading the datascout repo define a PROJECT_DIR variable (path to datascout git repo).
```
export PROJECTDIR="/path/to/your/Ensembl-datascout"
cd ${PROJECTDIR}
```

Define the configuration of USER/PWD/SERVER/PORT of your mysql ncbi_tax and rfam DBs in ""${PROJECT_DIR}/conf/ncbi_db.conf""
and ""${PROJECT_DIR}/conf/rfam_db.conf"" following the structure in the template in that same folder:
mysql://USER:PWD@mysql-ncbi-SERVER:PORT/ncbi_taxonomy_db.

Test the configuration with:
```
nextflow run main.nf -profile slurm,test,singularity
```
Use a comma separated list of genomes to annotate as input  
(following the template in ""${PROJECT_DIR}/assets/test_data/genomes_test_list.csv"")  

  GENOME_NAME	TAX_ID	ENA_ACCESSION    
  #Example:  
  toxoplasma_gondii_ME49,508771,GCA_000006565.2  
  tripanosoma_cruzi,5693,GCA_003719455.1

Define and export the following variables:

export INPUT_CSV="/path/to/your/input-file-dir/your_genomes_list.csv"
export OUTPUT_PATH="/path/to/your/output-dir/genome_annotations"

export ORTHODB_FOLDER="/path/to/your/static-storage-dir/orthodb_dir"
export ASSEMBLIES_DIR="/path/to/your/static-storage-dir/assemblies_dir"
export ENA_CSV_DIR="/path/to/your/static-storage-dir/ena_csv_dir"
export FASTQ_DIR="/path/to/your/static-storage-dir/rna_fastq_dir"
export UNIPROT_DIR="/path/to/your/static-storage-dir/uniprot_dir"

To run the pipeline execute:
```
nextflow run main.nf --csv_file $INPUT_CSV --outdir $OUTPUT_PATH --orthodb_dir $ORTHODB_FOLDER --assemblies_dir $ASSEMBLIES_DIR --rna_fastq_dir $FASTQ_DIR --uniprot_dir $UNIPROT_DIR  --ena_csv_dir $ENA_CSV_DIR -profile slurm
```