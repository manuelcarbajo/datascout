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

    // Assign workflow.projectDir to a variable
    def projectDir = workflow.projectDir


    take:
        version
        help
        validate_params
        monochrome_logs
        nextflow_cli_args
        outdir
        csv_file

    main:

        // Create channels from input parameters
        ch_csv_file      = Channel.of(params.csv_file)
        ch_outdir        = Channel.of(params.outdir)
        ch_orthodb_dir   = Channel.of(params.orthodb_dir)


        // Assign variables to workflow scope
        csv_file          = ch_csv_file
        outdir            = ch_outdir
        orthodb_dir       = ch_orthodb_dir
        ncbi_conf         = file("${projectDir}/conf/ncbi_db.conf")
        versions          = Channel.empty()

    emit:
        csv_file      = ch_csv_file
        outdir        = outdir
        orthodb_dir   = orthodb_dir
        ncbi_conf     = ncbi_conf
        versions      = versions
}