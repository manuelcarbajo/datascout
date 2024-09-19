# downloadRNASeqFastqs.py

import os
import subprocess
import argparse
import sys

class DownloadRNASeqFastqs:
    def __init__(self, params):
        # Default parameters
        self.params = {
            'decompress': 0,
            'create_faidx': 0,
        }
        # Update with provided parameters
        self.params.update(params)

    def write_output(self):
        ftp_base_url = self.param_required('ftp_base_url')
        fastq = self.param_required('iid')
        path = self.param_required('input_dir')

        if os.path.exists(os.path.join(path, fastq)):
            if self.param('decompress'):
                fastq = self.decompress(path, fastq)

            if self.param('create_faidx'):
                self.create_faidx(path, fastq)

            self.complete_early('Input file already exists, will not download')
            return

        if '_' in fastq:
            srr = fastq.split('_')[0]
        else:
            srr = fastq.split('.')[0]

        first = srr[:6]
        second_a = '00' + srr[-1]
        second_b = '0' + srr[-2:]

        exit_code = 0
        wget_cmd_list = [
            ['wget', '-c', '-qq', f"{ftp_base_url}/{first}/{second_a}/{srr}/{fastq}", '-P', path],
            ['wget', '-c', '-qq', f"{ftp_base_url}/{first}/{second_b}/{srr}/{fastq}", '-P', path],
            ['wget', '-c', '-qq', f"{ftp_base_url}/{first}/{srr}/{fastq}", '-P', path]
        ]
        for wget_cmd in wget_cmd_list:
            exit_code = self.exit_code_test(wget_cmd)
            if exit_code:
                break

        if not exit_code:
            if os.path.exists(os.path.join(path, fastq)):
                self.run_system_command(['rm', os.path.join(path, fastq)])
            self.throw(f"Failed to download {fastq}")

        if not os.path.exists(os.path.join(path, fastq)):
            self.throw(f"Did not find the fastq file on the expected path. Path:\n{os.path.join(path, fastq)}")

        if self.param('decompress'):
            fastq = self.decompress(path, fastq)

        if self.param('create_faidx'):
            self.create_faidx(path, fastq)

    def decompress(self, path, fastq):
        cmd = ['gunzip', os.path.join(path, fastq)]

        if fastq.endswith('.gz'):
            fastq_new = fastq[:-3]  # Remove '.gz'
            gunzip_res = subprocess.call(cmd)
            if gunzip_res:
                self.throw(f"Failed to decompress file. Command:\n{' '.join(cmd)}")
            fastq = fastq_new
        else:
            self.warning("You selected decompress, but the file did not have a .gz extension, so will not try and decompress")

        # Update these in case the extension was removed
        self.params['iid'] = fastq
        self.params['fastq_file'] = fastq

        return fastq

    def create_faidx(self, path, fastq):
        if os.path.exists(os.path.join(path, fastq + '.fai')):
            self.warning("You selected faidx, but the faidx exists, so will not try and create")
            return

        samtools_path = self.param_required('samtools_path')
        cmd = [samtools_path, 'faidx', os.path.join(path, fastq)]
        faidx_res = subprocess.call(cmd)
        if faidx_res:
            self.throw(f"Failed to index file. Command:\n{' '.join(cmd)}")

    def exit_code_test(self, wget_cmd):
        res = self.run_system_command(wget_cmd)
        if res != 0:
            res >>= 8  # Bit-shift right by 8 bits, similar to Perl's behavior
            self.warning(f"wget died with error code {res}")
            return 0
        else:
            return 1

    def run_system_command(self, cmd):
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode
        except Exception as e:
            self.throw(f"Error running command {' '.join(cmd)}: {str(e)}")

    def param(self, key):
        return self.params.get(key)

    def param_required(self, key):
        if key in self.params:
            return self.params[key]
        else:
            self.throw(f"Required parameter '{key}' not found.")

    def warning(self, msg):
        print(f"WARNING: {msg}", file=sys.stderr)

    def throw(self, msg):
        raise Exception(msg)

    def complete_early(self, msg):
        print(f"INFO: {msg}")
        # Exiting the method early
        return

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Download RNASeq FASTQ files.')
    parser.add_argument('-ftp_base_url', required=True, help='FTP base URL')
    parser.add_argument('-input_dir', required=True, help='Input directory to save the files')
    parser.add_argument('-iid', required=True, help='Input identifier (FASTQ file name)')
    parser.add_argument('-decompress', action='store_true', help='Decompress the downloaded file')
    parser.add_argument('-create_faidx', action='store_true', help='Create faidx index of the file')
    parser.add_argument('-samtools_path', default='samtools', help='Path to samtools executable')

    args = parser.parse_args()

    # Prepare parameters
    params = {
        'ftp_base_url': args.ftp_base_url,
        'input_dir': args.input_dir,
        'iid': args.iid,
        'decompress': int(args.decompress),
        'create_faidx': int(args.create_faidx),
        'samtools_path': args.samtools_path,
    }

    # Instantiate and run the downloader
    downloader = DownloadRNASeqFastqs(params)
    try:
        downloader.write_output()
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
