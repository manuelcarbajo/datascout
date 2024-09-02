import sys
import os

input_file = sys.argv[1]
if len(sys.argv) != 2 or not os.path.exists(input_file):
    print("Usage: python remove_dup_seqs.py input_file\nPerhaps the input_file was missing")
    sys.exit(1)

seq_hash = {}

with open(input_file, 'r') as infile:
    header = None
    sequence = ""

    for line in infile:
        line = line.strip()

        if not line:
            continue  # Skip empty lines

        if line.startswith('>'):
            # If a header line is encountered, store the previous sequence
            if header is not None and sequence:
                seq_hash[sequence] = header

            # Reset header and start a new sequence
            header = line
            sequence = ""
        else:
            sequence += line

    # Process the last sequence in the file
    if header is not None and sequence:
        seq_hash[sequence] = header

# Print unique sequences along with their headers
for sequence, header in seq_hash.items():
    print(header)
    print(sequence)

