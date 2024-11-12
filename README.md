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

After downloading the datascout repo define your PROJECT_DIR (path to datascout git repo),

Use a comma separated list of genomes to annotate as input  
(following the template in ""${PROJECT_DIR}/assets/test_data/genomes_test_list.csv"")  

  GENOME_NAME	TAX_ID	ENA_ACCESSION    
  #Example:  
  toxoplasma_gondii_ME49,508771,GCA_000006565.2  
  tripanosoma_cruzi,5693,GCA_003719455.1

Define the configuration of USER/PWD/SERVER/PORT of your mysql ncbi_tax and rfam DBs in ""${PROJECT_DIR}/conf/ncbi_db.conf""
and ""${PROJECT_DIR}/conf/rfam_db.conf"" following the structure in the template in that same folder:
mysql://USER:PWD@mysql-ncbi-SERVER:PORT/ncbi_taxonomy_db

Make sure you have conda installed
Define the right paths in env_setup.sh and run it
