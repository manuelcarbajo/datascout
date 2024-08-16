import sys
import re

if len(sys.argv) != 3:
    print("Usage: python reheader_orthodb.py input_file output_file")
    sys.exit(1)

input_filename = sys.argv[1]
output_file = sys.argv[2]


ct = 0 

with open(input_filename, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        line = line.strip()
        if line:
            ct += 1
            match_obj = re.search(r'^>[0-9]+_[0-9]:\w+', line)
            if match_obj:
                header = match_obj.group(0)
                outfile.write(f"{header}\n")
                #print("MATCH: " + str(ct) + " " + header)
            elif line.strip():
                outfile.write(line + "\n")
                #print("NO MATCH: " + str(ct) + " " + line )

