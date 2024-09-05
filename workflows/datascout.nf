/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT MODULES / SUBWORKFLOWS / FUNCTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
include { NCBI_ORTHODB           } from "${projectDir}/modules/local/ncbi_orthodb.nf"
include { GENOME_ASSEMBLY        } from "${projectDir}/modules/local/genome_assembly.nf"
include { UNIPROT_DATA           } from "${projectDir}/modules/local/uniprot_data.nf"
include { RFAM_ACCESSIONS       } from "${projectDir}/modules/local/rfam_accessions.nf"
include { paramsSummaryMap       } from 'plugin/nf-validation'
include { paramsSummaryMultiqc   } from "${projectDir}/subworkflows/nf-core/utils_nfcore_pipeline"
include { softwareVersionsToYAML } from "${projectDir}/subworkflows/nf-core/utils_nfcore_pipeline"
include { methodsDescriptionText } from "${projectDir}/subworkflows/local/utils_nfcore_datascout_pipeline"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RUN MAIN WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow DATASCOUT {

    take:
    ch_csv_file// channel: csv_file read in from input param --csv_file
    ch_outdir
    ch_orthodb_dir
    main:

    ch_versions = Channel.empty()
    ch_multiqc_files = Channel.empty()

    //
    // MODULE: Run NCI_OrthoDB
    //
    NCBI_ORTHODB (
        ch_csv_file,
        ch_outdir,
        ch_orthodb_dir
    )

    def ch_genomes = NCBI_ORTHODB.out.genomes
        .flatten()
        .map{ tax_ranks_path -> tuple(tax_ranks_path.getParent().getBaseName(), tax_ranks_path) }

    GENOME_ASSEMBLY(ch_genomes)
    UNIPROT_DATA(ch_genomes)
    RFAM_ACCESSIONS(ch_genomes)


    //
    // Collate and save software versions
    //
    softwareVersionsToYAML(ch_versions)
        .collectFile(
            storeDir: "${params.outdir}/pipeline_info",
            name: 'nf_core_pipeline_software_mqc_versions.yml',
            sort: true,
            newLine: true
        ).set { ch_collated_versions }



    emit:
    //multiqc_report = MULTIQC.out.report.toList() // channel: /path/to/multiqc_report.html
    versions       = ch_versions                 // channel: [ path(versions.yml) ]
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    THE END
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
