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

    
    fastq_files_ch = DOWNLOAD_FASTQ_FILES.out.fastq_files

    //make paired end file channel with run id in meta
    fastq_files_ch.flatMap { meta, fastqs -> 
        filePairs = fastqs.collect { file(it) }
            .groupBy { file -> file.name.split('_')[0] }
            .collect { run_id, files ->
                def forward = files.find { it.name.endsWith('_1.fastq') }
                def reverse = files.find { it.name.endsWith('_2.fastq') }
                def new_meta = meta + [run_id: run_id]
                return tuple(new_meta, forward, reverse)
            }
    }
    .set { paired_fastq_files }


    SOURMASH_SKETCH_FASTQ(paired_fastq_files)
    SOURMASH_SKETCH_GENOME(genome)

    // output list of signatures per input genome and ena lineage
    signatures_ch = SOURMASH_SKETCH_FASTQ.out.sketch
        .map { meta, sketch -> 
            def new_meta = [id: meta.id, ena_tax: meta.ena_tax] // remove run ID
            tuple(new_meta, sketch)
        }
        .groupTuple() 
        
    SOURMASH_GATHER(
        SOURMASH_SKETCH_GENOME.out.sketch,
        signatures_ch
    )

    GET_CONTAINMENT(
        SOURMASH_GATHER.out.gather_csv
    )

    keep_runs_ch = GET_CONTAINMENT.out.keep_runs

    // read run ids from file into a list
    keep_runs_list_ch = keep_runs_ch
        .map { run_data -> 
            def meta = run_data[0]
            def runs = run_data[1]  // txt file
            def run_ids = runs.readLines().collect { it.trim() }.toList()  // store as list
            return [meta, run_ids] 
    }

    // get run files which include run id
    filtered_fastq_ch = fastq_files_ch.join(keep_runs_list_ch)
    .map { meta, fastq_files, runs ->  

        def filtered_files = fastq_files.findAll { fq_path -> 
            def base_name = fq_path.getFileName().toString().split('_')[0]
            
            runs.any { id -> base_name == id } 
        }

        return tuple(meta, filtered_files)
    }

    PUBLISH_RUNS(filtered_fastq_ch)

    emit:
    sourmash        = SOURMASH_GATHER.out.gather_csv
    fastq_files     = PUBLISH_RUNS.out.fastq_files

}
