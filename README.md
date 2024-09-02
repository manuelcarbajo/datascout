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

This project uses nextflow-23.04.1 


### Initialising and running the environment

After downloading the datascout repo define your WORK_DIR (path to datascout git repo), ENSEMBL_ROOT_DIR (path to your other ensembl git repositories) and diamond_path (path to a copy of uniprot_euk.fa.dmnd database)

Place a tab separated list of genomes to annotate in "$WORK_DIR/data/genomes_list.csv"  
(following the template in "$WORK_DIR/data/genomes_list_template.csv")  

  GENOME_NAME	TAX_ID	ENA_ACCESSION  
  Place here a tab separated list of genomes to process.  
  Example:  
  toxoplasma_gondii_ME49	508771	GCA_000006565.2  
  tripanosoma_cruzi	5693	GCA_003719455.1  
