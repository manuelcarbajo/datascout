#!/usr/bin/env nextflow

include { SOURMASH_SKETCH_FASTQ      } from "../../modules/local/sourmash_sketch_fastq/main.nf"
include { SOURMASH_SKETCH_GENOME     } from "../../modules/local/sourmash_sketch_genome/main.nf"
include { DOWNLOAD_FASTQ_FILES       } from "../../modules/local/download_fastq_files/main.nf"
include { SOURMASH_GATHER            } from "../../modules/local/sourmash_gather/main.nf"
include { GET_CONTAINMENT            } from "../../modules/local/get_containment/main.nf"
include { PUBLISH_RUNS               } from "../../modules/local/publish_runs/main.nf"

workflow SOURMASH {

    take:
    ena_metadata // tuple: meta, metdata_csv
    genome // tuple: meta, genome_path
    start_line // int
    num_lines // int

    main:

    DOWNLOAD_FASTQ_FILES(ena_metadata, start_line, num_lines)

    // make paired end file channel with run id in meta
    fastq_files_ch = DOWNLOAD_FASTQ_FILES.out.fastq_files

    fastq_files_ch.flatMap { meta, fastqs -> 
        filePairs = fastqs.collect { file(it) }
            .groupBy { file -> file.baseName.replaceFirst(/_[12]$/, '') }
            .collect { run_id, files ->
                def forward = files.find { it.name.endsWith('_1.fastq') }
                def reverse = files.find { it.name.endsWith('_2.fastq') }
                def new_meta = meta + [run_id: run_id]
                return tuple(new_meta, forward, reverse)
            }
        return filePairs
    }
    .set { paired_fastq_files }

    SOURMASH_SKETCH_FASTQ(paired_fastq_files)
    SOURMASH_SKETCH_GENOME(genome)


    signatures_ch = SOURMASH_SKETCH_FASTQ.out.sketch
        .map { meta, sketch -> 
            def new_meta = [id: meta.id] 
            tuple(new_meta, sketch)
        }
        .groupTuple() // output list of signatures per input genome

    SOURMASH_GATHER(
        SOURMASH_SKETCH_GENOME.out.sketch,
        signatures_ch
    )

    GET_CONTAINMENT(
        SOURMASH_GATHER.out.gather_csv
    )

    // read run ids from file into a list
    keep_runs_ch = GET_CONTAINMENT.out.keep_runs
    keep_runs_list_ch = keep_runs_ch
        .map { run_data -> 
            def meta = run_data[0]
            def runs = run_data[1]  // txt file
            def run_ids = runs.readLines().collect { it.trim() }.toList()  // store as list
            return [meta, run_ids] 
        }

    // filter runs which are contained within the genome
    filtered_fastq_ch = fastq_files_ch.combine(keep_runs_list_ch)
        .filter { fastq, runs ->
            def new_meta = fastq[0]
            def run_ids = runs[1]  // list of run IDs
            def fastq_files = fastq[1] // list of fastq file paths
            def filtered = fastq_files.findAll { fq_path -> run_ids.any { id -> fq_path.contains(id)}} // keep any files which have a run ID from the list in the path
            return [new_meta, filtered]
        }
    
    PUBLISH_RUNS(filtered_fastq_ch)

    emit:
    sourmash        = SOURMASH_GATHER.out.gather_csv
    fastq_files     = PUBLISH_RUNS.out.fastq_files


}
