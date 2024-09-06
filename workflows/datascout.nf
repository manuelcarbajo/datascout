/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT MODULES / SUBWORKFLOWS / FUNCTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
include { NCBI_ORTHODB           } from "${projectDir}/modules/local/ncbi_orthodb.nf"
include { GENOME_ASSEMBLY        } from "${projectDir}/modules/local/genome_assembly.nf"
include { UNIPROT_DATA           } from "${projectDir}/modules/local/uniprot_data.nf"
include { RFAM_ACCESSIONS        } from "${projectDir}/modules/local/rfam_accessions.nf"
include { ENA_RNA_CSV            } from "${projectDir}/modules/local/ena_rna_csv.nf"
include { FILTER_RNA_CSV         } from "${projectDir}/modules/local/filter_rna_csv.nf"
include { DOWNLOAD_FASTQ_FILES   } from "${projectDir}/modules/local/download_fastq_files.nf"
include { SOURMASH_RNA_CSV       } from "${projectDir}/modules/local/sourmash_rna_csv.nf"
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

    GENOME_ASSEMBLY(ch_genomes).set { ch_assembly }
    UNIPROT_DATA(ch_genomes).set { ch_uniprot }
    RFAM_ACCESSIONS(ch_genomes).set { ch_rfam }
    ENA_RNA_CSV(ch_genomes)
    FILTER_RNA_CSV(ENA_RNA_CSV.out.rna_csv)

    ch_rna_filtered_to_storeDir = FILTER_RNA_CSV.out.filtered_rna_csv
                                .splitCsv(elem: 1, header: false, sep: '\t' )
                                .map{row -> tuple(row[1][3], row[1][11])}
                                .unique()
                                .map{fastq_file, md5 -> [fastq_file, md5]}

    DOWNLOAD_FASTQ_FILES(ch_rna_filtered_to_storeDir)

    ch_download_is_finished = DOWNLOAD_FASTQ_FILES.out
                            .collect()
                            .filter{ it.isEmpty() }//empty ch waiting for all fastq files download

    ch_rna_filtered_to_sourmash = FILTER_RNA_CSV.out.filtered_rna_csv
                                .splitCsv(elem: 1, header: false, sep: '\t' )
                                .map{row -> tuple(row[0],row[1][3],row[2])}
                                .groupTuple()
                                .map{genome, fastqs, tax_ranks -> [genome, fastqs, tax_ranks[0]]}

    ch_sourmash = ch_rna_filtered_to_sourmash.join(ch_download_is_finished, remainder:true)
                                       .groupTuple()
                                       .map{row -> tuple(row[0], row[1], row[2])}

    SOURMASH_RNA_CSV(ch_sourmash)
    ch_post_sourmash = SOURMASH_RNA_CSV.out.smashed_rna
                                        .groupTuple()


    ch_joined = ch_genomes.join(ch_rfam, remainder:true).join(ch_uniprot, remainder:true).join(ch_post_sourmash, remainder:true).join(ch_assembly, remainder:true)
    ch_joined.view()


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
