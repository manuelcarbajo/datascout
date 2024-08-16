# DataScout
This repo queries and gather data from different resources which can then be used to run bulk automatised annotation of microbial genomes.
The different types of data are:
- OrthoDB and UniProt orthology data, 
- Rfam (non coding Rna( data, 
- Transcriptomic data from ENA

## Prerequisites
Pipelines are intended to be run inside the Ensembl production environment.
Please, make sure you have all the proper credential, keys, etc. set up.

### Getting this repo

```
git clone git@github.com:manuelcarbajo/datascout
```

### Configuration

#### Refresing environment

This project uses nextflow-22.10.1 and can be loaded with: 

module load nextflow-22.10.1-gcc-11.2.0-ju5saqw


### Initialising and running the environment
You can recreate a conda environment with microbes_gb.yml

```
conda env create -n microbes_gb -f microbes_gb.yml
conda activate microbes_gb
```

After downloading datascout define your WORK_DIR (path to datascout git repo), ENSEMBL_ROOT_DIR (path to your other ensembl git repositories) and diamond_path (path to a copy of uniprot_euk.fa.dmnd database)

Place a tab separated list of genomes to annotate in "$WORK_DIR/data/genomes_list.csv"  
(following the template in "$WORK_DIR/data/genomes_list_template.csv")  

  GENOME_NAME	TAX_ID	ENA_ACCESSION  
  Place here a tab separated list of genomes to process.  
  Example:  
  toxoplasma_gondii_ME49	508771	GCA_000006565.2  
  tripanosoma_cruzi	5693	GCA_003719455.1  



#### Run the setup.sh script
Execute:
```
source setup.sh
```

#### Run the nextflow pipeline 
Use the command:
```
nextflow run main.nf  --output_path $OUTPUT_PATH --orthodb_dir $ORTHODB_FOLDER --csv_file $INPUT_CSV --assemblies_dir $ASSEMBLIES_DIR --rna_fastq_dir $FASTQ_DIR --uniprot_dir $UNIPROT_DIR  --ena_csv_dir $ENA_CSV_DIR --min_transcriptomic_reads 100 -profile codon_slur
```
