//
// Subworkflow with functionality specific to the Ensembl/datascout pipeline
//

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT FUNCTIONS / MODULES / SUBWORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { paramsSummaryMap          } from 'plugin/nf-schema'

/*
========================================================================================
    SUBWORKFLOW TO INITIALISE PIPELINE
========================================================================================
*/

workflow PIPELINE_INITIALISATION {

    take:
    version           // boolean: Display version and exit
    help              // boolean: Display help text
    validate_params   // boolean: Boolean whether to validate parameters against the schema at runtime
    monochrome_logs   // boolean: Do not use coloured log outputs
    nextflow_cli_args //   array: List of positional nextflow CLI args
    outdir            //  string: The output directory where the results will be saved
    csv_file          //  string: Path to input samplesheet

    main:

    ch_versions = Channel.empty()

    //
    // Create channel from input file provided through params.input
    //
    Channel.of(params.csv_file).set { ch_csv_file }
    Channel.of(params.outdir).set { ch_outdir }
    Channel.of(params.orthodb_dir).set { ch_orthodb_dir }
    //Channel.of("$baseDir/conf/ncbi_db.conf").set { ch_ncbi_conf }

    emit:
    csv_file = ch_csv_file
    outdir = ch_outdir
    orthodb_dir = ch_orthodb_dir
    versions    = ch_versions
}


