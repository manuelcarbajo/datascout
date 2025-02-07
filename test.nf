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
samplesheet.multiMap {sample_id, genome, tax_name, taxid, orthodb_tax, uniprot_tax, rfam_tax, ena_tax, uniprot_evidence ->
    meta = [ id: sample_id ]
    genome_meta = [id: genome, ena_tax: ena_tax]
    genome: [ genome_meta, genome ]
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
include { PUBLISH_RUNS               } from "./modules/local/publish_runs/main.nf"
include { SOURMASH                   } from "./subworkflows/local/sourmash_filtering.nf"
/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RUN MAIN WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/


workflow DATASCOUT{

    // get taxonomy lineage 
    TAX_LINEAGE(input.taxid, params.ncbi_db, params.taxdump)
    taxa_ch = TAX_LINEAGE.out.tax_ranks

    // query databases for supporting proteins and rnas
    NCBI_ORTHODB(taxa_ch, input.orthodb_tax)
    UNIPROT_DATA(taxa_ch, input.uniprot_tax, input.uniprot_evidence)
    RFAM_ACCESSIONS(taxa_ch, input.rfam_tax, params.rfam_db)


    // fetch ENA metadata
    ENA_RNA_CSV(taxa_ch, input.ena_tax)

    // download genome fasta 
    GENOME_ASSEMBLY(input.genome)

       // read run ids from file into a list
    keep_runs_ch = GET_CONTAINMENT.out.keep_runs
    keep_runs_list_ch = keep_runs_ch
        .map { run_data -> 
            def meta = run_data[0]
            def runs = run_data[1]  // txt file
            def run_ids = runs.readLines().collect { it.trim() }.toList()  // store as list
            return [meta, run_ids] 
        }


    // Group sample IDs with the same genome and ena max taxonomic rank. - Avoids multiple downloads of the same set of fastq files.
    ena_metadata_ch = ENA_RNA_CSV.out.rna_csv
        .map { metadata ->
            def ena_file = metadata[1] // csv file
            return [genome_meta, ena_file] // make id genome - further steps will be grouped by genome + ena rank instead of sample ID

        }

    if ( params.sourmash ) {

        SOURMASH(
            ena_metadata_ch,
            GENOME_ASSEMBLY.out.assembly_fa,
            1,
            params.max_runs
        )
    }

    else {

        DOWNLOAD_FASTQ_FILES(
            ena_metadata_ch,
            params.max_runs
        )

        PUBLISH_RUNS(DOWNLOAD_FASTQ_FILES.out.fastq_files)
    }
    
}

// /*
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//     THE END
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// */
