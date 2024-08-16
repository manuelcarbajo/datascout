import sys
import os
import errno
from datetime import datetime
import my_process as mp
import gzip
from pathlib import Path

def symlink_force(target, link_name):
    try:
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e


def sourmash_filter(tax_rank, genome_name,fastq_files,rna_fastq_folder):
    os.makedirs("smashed_rna",exist_ok=True)
    log_file = tax_rank['log_dir'] + '/sourmash.log' 
    fastq_list = fastq_files.strip('[]').split(', ')
    for fq in fastq_list:
        fq_local_symlink = "smashed_rna/" + fq
        fq_static_target = os.path.join(rna_fastq_folder, fq)
        symlink_force(fq_static_target, fq_local_symlink)
        #Path(fq_static_target).symlink_to(fq_local_symlink)
        print(fq_local_symlink + " --> " + fq_static_target)
        """ 
         #TODO:  sourmash filtering here 
        """  
if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if len(sys.argv) < 2:
        print("The genome, the fastq_files list, or the tax_ranks path is/are missing as an argument.")
    else:
        genome_name = sys.argv[1]
        fastq_files = sys.argv[2]
        tax_ranks = sys.argv[3]
        rna_fastq_folder = sys.argv[4]
        tr = mp.read_tax_rank(tax_ranks)
        print("*** begin Sourmash for " + genome_name + " at " + str(now) )
        print("genome_name: " + genome_name )
        print("fastq_files: " + fastq_files)
        print("tax_ranks: " + tax_ranks)
        print("rna_fastq_folder: " + rna_fastq_folder)
        sourmash_filter(tr, genome_name,fastq_files,rna_fastq_folder)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("*** end Sourmash for " + genome_name + " at " + str(now) )
