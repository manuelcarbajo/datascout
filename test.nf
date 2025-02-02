/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    PRINT PARAMS SUMMARY
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { paramsSummaryLog } from 'plugin/nf-schema'

log.info paramsSummaryLog(workflow)

/************************** 
* INPUT CHANNELS 
**************************/

include { samplesheetToList } from 'plugin/nf-schema'

samplesheet = Channel.fromList(samplesheetToList(params.samplesheet, "${projectDir}/assets/schema_input.json"))

/* split the inputs */
samplesheet.multiMap {sample_id, tax_name, taxid, orthodb_tax, uniprot_tax, rfam_tax, ena_tax, uniprot_evidence ->
    meta = [ id: sample_id ]
    genome: [ meta, sample_id ]
    tax_name: [ meta, tax_name ]
    taxid: [ meta, taxid ]
    orthodb_tax: [ meta, orthodb_tax ]
    uniprot_tax: [ meta, uniprot_tax ]
    rfam_tax: [ meta, rfam_tax ]
    ena_tax: [ meta, ena_tax ]
    uniprot_evidence: [ meta, uniprot_evidence ]
}.set {
    input
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT MODULES / SUBWORKFLOWS / FUNCTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
include { TAX_LINEAGE                } from "./modules/local/parse_tax_lineage/main.nf"
include { NCBI_ORTHODB               } from "./modules/local/ncbi_orthodb/main.nf"
include { GENOME_ASSEMBLY            } from "./modules/local/genome_assembly/main.nf"
include { UNIPROT_DATA               } from "./modules/local/uniprot_data/main.nf"
include { RFAM_ACCESSIONS            } from "./modules/local/rfam_accessions/main.nf"
include { ENA_RNA_CSV                } from "./modules/local/ena_rna_csv/main.nf"
include { DOWNLOAD_FASTQ_FILES       } from "./modules/local/download_fastq_files/main.nf"
// include { SOURMASH_RNA_CSV       } from "${projectDir}/modules/local/sourmash_rna_csv/main.nf"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RUN MAIN WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow DATASCOUT{

    GENOME_ASSEMBLY(input.genome)

    TAX_LINEAGE(input.taxid, params.ncbi_db, params.taxdump)
    taxa_ch = TAX_LINEAGE.out.tax_ranks
    NCBI_ORTHODB(taxa_ch, input.orthodb_tax)

    UNIPROT_DATA(taxa_ch, input.uniprot_tax, input.uniprot_evidence)
    RFAM_ACCESSIONS(taxa_ch, input.rfam_tax, params.rfam_db)

    ena_ch = ENA_RNA_CSV(taxa_ch, input.ena_tax)

    DOWNLOAD_FASTQ_FILES(ena_ch, 1)
    fastq_ch = DOWNLOAD_FASTQ_FILES.out.fastq_files

    // In progress for sourmash
    // Channel
    // .fromProcess('DOWNLOAD_PAIRED_FASTQ_FILES')
    // .flatMap { meta, dir, fastqs ->
    //     // Collect paired FASTQ files using their naming pattern
    //     filePairs = fastqs.groupBy { file ->
    //         file.baseName.replaceFirst(/_[12]$/, '') // Extract run ID from _1/_2.fastq.gz
    //     }.collect { runId, files ->
    //         def forward = files.find { it.name.endsWith('_1.fastq') }
    //         def reverse = files.find { it.name.endsWith('_2.fastq') }
    //         tuple(meta, forward, reverse)
    //     }
    //     return filePairs
    // }
    // .set { paired_fastq_files }

    // paired_fastq_files.view()
    
}



 
//     ch_rna_filtered_to_storeDir = FILTER_RNA_CSV.out.filtered_rna_csv
//                                 .splitCsv(elem: 1, header: false, sep: '\t' )
//                                 .map{row -> tuple(row[1][3], row[1][11])}
//                                 .unique()
//                                 .map{fastq_file, md5 -> [fastq_file, md5]}

//     DOWNLOAD_FASTQ_FILES(ch_rna_filtered_to_storeDir)

//     ch_download_is_finished = DOWNLOAD_FASTQ_FILES.out
//                             .collect()
//                             .filter{ it.isEmpty() }//empty ch waiting for all fastq files download
//     /*
//     ch_rna_filtered_to_sourmash = FILTER_RNA_CSV.out.filtered_rna_csv
//                                 .splitCsv(elem: 1, header: false, sep: '\t' )
//                                 .map{row -> tuple(row[0],row[1][3],row[2])}
//                                 .groupTuple()
//                                 .map{genome, fastqs, tax_ranks -> [genome, fastqs, tax_ranks[0]]}

//     ch_sourmash = ch_rna_filtered_to_sourmash.join(ch_download_is_finished, remainder:true)
//                                        .groupTuple()
//                                        .map{row -> tuple(row[0], row[1], row[2])}

//     SOURMASH_RNA_CSV(ch_sourmash)
//     ch_post_sourmash = SOURMASH_RNA_CSV.out.smashed_rna
//                                         .groupTuple()


//     ch_joined = ch_genomes.join(ch_rfam, remainder:true).join(ch_uniprot, remainder:true).join(ch_post_sourmash, remainder:true).join(ch_assembly, remainder:true)
//     ch_joined.view()
//     */

// }

// /*
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//     THE END
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// */
