
srun --pty -n 10 -t 14-00:00  --mem=10G  $SHELL

[ -n "$SLURM_JOB_ID" ] && echo "You are inside an interactive SLURM shell with job ID: $SLURM_JOB_ID" || echo "You are not inside an interactive SLURM shell"


module load nextflow/23.04.1


export PROJECTDIR="/<path/to/project>/Ensembl-datascout"
cd ${PROJECTDIR}
export BIOPERL_LIB="/<path/to/linuxbrew>/linuxbrew/opt/bioperl-169/libexec"
export PERL5LIB=${PROJECTDIR}/bin:$BIOPERL_LIB
export PYTHONPATH=${PROJECTDIR}/bin:$PYTHONPATH:${PROJECTDIR}/templates
export PATH="${PROJECTDIR}:${PROJECTDIR}/bin:$PATH" 


conda config --add channels conda-forge
conda env create -n datascout -f env_datascout.yml
conda activate datascout

OUTPUT_STATIC_DIR="/<path/to/output/static/dir>"
export ORTHODB_FOLDER="${OUTPUT_STATIC_DIR}/orthodb_dir"
export OUTPUT_PATH="${OUTPUT_STATIC_DIR}/genome_annotations"
export INPUT_CSV="${PROJECTDIR}/assets/test_data/genomes_test_list.csv" #for tests, otherwise: path to your input file
export ASSEMBLIES_DIR="${OUTPUT_STATIC_DIR}/assemblies_dir"
export ENA_CSV_DIR="${OUTPUT_STATIC_DIR}/ena_csv_dir"
export FASTQ_DIR="${OUTPUT_STATIC_DIR}/rna_fastq_dir"
export UNIPROT_DIR="${OUTPUT_STATIC_DIR}/uniprot_dir"


#Test configuration with:
nextflow run main.nf -profile test,singularity
#Otherwise, regular run with:
#nextflow run main.nf  --csv_file $INPUT_CSV --outdir $OUTPUT_PATH --orthodb_dir $ORTHODB_FOLDER --assemblies_dir $ASSEMBLIES_DIR --rna_fastq_dir $FASTQ_DIR --uniprot_dir $UNIPROT_DIR  --ena_csv_dir $ENA_CSV_DIR

