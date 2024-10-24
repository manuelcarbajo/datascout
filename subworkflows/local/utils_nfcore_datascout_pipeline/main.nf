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
include { fromSamplesheet           } from 'plugin/nf-schema'
include { UTILS_NEXTFLOW_PIPELINE   } from '../../nf-core/utils_nextflow_pipeline'
include { completionEmail           } from '../../nf-core/utils_nfcore_pipeline'
include { completionSummary         } from '../../nf-core/utils_nfcore_pipeline'
include { dashedLine                } from '../../nf-core/utils_nfcore_pipeline'
include { nfCoreLogo                } from '../../nf-core/utils_nfcore_pipeline'
include { imNotification            } from '../../nf-core/utils_nfcore_pipeline'
include { UTILS_NFCORE_PIPELINE     } from '../../nf-core/utils_nfcore_pipeline'
include { workflowCitation          } from '../../nf-core/utils_nfcore_pipeline'
*/
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
    // Print version and exit if required and dump pipeline parameters to JSON file
    //
    // UTILS_NEXTFLOW_PIPELINE (
    //     version,
    //     true,
    //     outdir,
    //     workflow.profile.tokenize(',').intersect(['conda', 'mamba']).size() >= 1
    // )

    // //
    // // Validate parameters and generate parameter summary to stdout
    // //
    // // pre_help_text = nfCoreLogo(monochrome_logs)
    // // post_help_text = '\n' + workflowCitation() + '\n' + dashedLine(monochrome_logs)
    // // def String workflow_command = "nextflow run ${workflow.manifest.name} -profile <docker/singularity/.../institute> --input samplesheet.csv --outdir <OUTDIR>"
    // // UTILS_NFVALIDATION_PLUGIN (
    // //     help,
    // //     workflow_command,
    // //     pre_help_text,
    // //     post_help_text,
    // //     validate_params,
    // //     "nextflow_schema.json"
    // // )

    // //
    // // Check config provided to the pipeline
    // //
    // UTILS_NFCORE_PIPELINE (
    //     nextflow_cli_args
    // )

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


