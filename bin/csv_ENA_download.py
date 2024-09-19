import requests
import json
import re
import os
import sys

class DownloadCsvENA:
    def __init__(self, ena_base_url, download_method, read_type, max_long_read_read_count, queries):
        self.ena_base_url = ena_base_url
        self.download_method = download_method
        self.read_type = read_type
        self.max_long_read_read_count = max_long_read_read_count
        self.queries = queries
        self.files_fields = "run_accession,study_accession,experiment_accession,sample_accession,secondary_sample_accession," \
                      "instrument_platform,instrument_model,library_layout,library_strategy,read_count,base_count," \
                      "fastq_ftp,fastq_aspera,fastq_md5,library_source,library_selection,center_name,study_alias," \
                      "experiment_alias,experiment_title,study_title,submitted_ftp"
        self.sample_domain = "domain=sample&result=sample"
        self.sample_fields = "accession,secondary_sample_accession,bio_material,cell_line,cell_type,collected_by,collection_date," \
                              "country,cultivar,culture_collection,description,dev_stage,ecotype,environmental_sample,first_public," \
                              "germline,identified_by,isolate,isolation_source,location,mating_type,serotype,serovar,sex,submitted_sex," \
                              "specimen_voucher,strain,sub_species,sub_strain,tissue_lib,tissue_type,variety,tax_id,scientific_name,sample_alias," \
                              "center_name,protocol_label,project_name,investigation_type,experimental_factor,sample_collection,sequencing_method"
        self.disease_keyword_for_removal = ['immunization', 'disease']

    def query_ena(self):
        csv_data = {}
        run_accessions = {}
        samples = {}
        json_decoder = json.JSONDecoder()

        for query in self.queries:
            url = f"{self.ena_base_url}&query={query}&domain=read&result=read_run&fields={self.files_fields}"
            #print(url)
            ua = requests.Session()
            response = requests.get(url)

            if response.ok:
                content = response.text
                fields_index = self.parse_header(content)

                for line in content.split('\n')[1:]:
                    if self.should_skip_line(line):
                        continue

                    row = line.split('\t')
                    if not self.check_paired_end(row, fields_index):
                        continue
                    row = self.filter_paired_end_fastq_entries(row, fields_index)


                    read_length = self.calculate_read_length(row, fields_index)
                    if read_length < 75:
                        continue

                    run_accession = self.determine_run_accession(row, fields_index)
                    if run_accession not in run_accessions:
                        run_accessions[run_accession] = {}

                    csv_data_row = {
                        'run_accession': row[fields_index['run_accession']],
                        'instrument_model': row[fields_index['instrument_model']],
                        'instrument_platform': row[fields_index['instrument_platform']],
                        'library_layout': row[fields_index['library_layout']],
                        'fastq_file': row[fields_index['fastq_ftp']],
                        'fastq_md5': row[fields_index['fastq_md5']],
                        'study_title': row[fields_index['study_title']],
                        'experiment_title': row[fields_index['experiment_title']],
                        'read_length': read_length,
                        'center_name': row[fields_index['center_name']],
                        'base_count': int(row[fields_index.get('base_count', 0)] or 0),
                    }

                    sample_name = row[fields_index['sample_accession']]

                    # Initialize a dictionary entry for the sample_name in samples
                    samples[sample_name] = {}
                    study_accession = row[fields_index['study_accession']]


                    # Push data (line, which can be a dictionary or processed row) into csv_data
                    if study_accession not in csv_data:
                        csv_data[study_accession] = {}

                    if sample_name not in csv_data[study_accession]:
                        csv_data[study_accession][sample_name] = []

                    csv_data[study_accession][sample_name].append(csv_data_row)

                sample_list = list(samples.keys())
                for sample in sample_list:
                    data = {}
                    success = self._retrieve_biosample_info(ua, json_decoder, sample, data)

                    if success == -1:
                        del samples[sample]
                        print("+++ unsuccessful sample -1: " + sample + "\nRemoved {} from the set as it is from a non-healthy animal".format(sample))
                        continue
                    elif success == 0:
                        self.ua.headers.update({'User-Agent': 'Python requests'})  # Reset to default headers
                        url = f"{self.ena_base_url}?query=\"accession={sample}\"&{self.sample_domain}&fields={self.sample_fields}"
                        print("+++ unsuccessful sample 0: " + sample + "\n  sample url:" + url)

                        response = self.ua.get(url)
                        if response.ok:
                            content = response.text
                            if content:
                                updated_data = self.process_biosample_content(content, data)
                                data = updated_data
                    samples[sample] = data

        if csv_data:
            for project in csv_data.keys():
                dev_stages = {}
                sample_names = {}
                for sample in csv_data[project].keys():

                    if sample not in samples:
                        continue  # Skip to next sample if sample data is not available

                    sample_data = samples[sample]

                    # Process development stages
                    if 'dev_stage' in sample_data and sample_data['dev_stage']:
                        if sample_data['dev_stage'] == 'sexually immature stage':
                            continue  # Skip if dev_stage is 'sexually immature stage
                        dev_stages[sample_data['dev_stage']] = 1  # Add dev_stage to dev_stages dictionary

                    # Determine the sample name
                    sample_name = sample_data.get('cellType') or sample_data.get('organismPart')

                    if not sample_name:
                        try:
                            sample_alias = sample_data.get('sample_alias')
                            description = sample_data.get('description', '')
                            if sample_alias == sample and len(description) > 2:
                                sample_name = description
                            elif description and sample in description:
                                sample_name = sample
                            else:
                                sample_name = sample_alias
                        except Exception as e:
                            print ("Sample_name Error for sample "+ sample + str(e) + "\n will use sample alias instead :" + sample_data.get('sample_alias'))
                            sample_name = sample_data.get('sample_alias')

                    sample_names[sample] = sample_name

                for sample in csv_data[project].keys():
                    if sample not in samples:
                        continue  # Skip if sample data is not available

                    sample_data = samples[sample]
                    name_parts = []

                    # Add 'sex' to name parts if it exists and is not empty
                    if sample_data.get('sex'):
                        name_parts.append(sample_data['sex'])

                    # Add sample_names[sample] to name parts
                    name_parts.append(sample_names[sample])

                    # Check if there are multiple dev_stages and if dev_stage exists
                    if len(dev_stages) > 1 and sample_data.get('dev_stage'):
                        # Remove ' stage' from dev_stage
                        sample_data['dev_stage'] = sample_data['dev_stage'].replace(' stage', '')

                        if sample_data.get('age'):
                            # Remove '.0' from age
                            sample_data['age'] = sample_data['age'].replace('.0', '')

                            if sample_data['dev_stage'] == 'embryo':
                                # Replace ' (\w)\w+' with '\1pf' in age
                                sample_data['age'] = re.sub(r' (\w)\w+', r'\1pf', sample_data['age'])
                                name_parts.append(sample_data['age'])
                            elif sample_data['dev_stage'] == 'neonate':
                                name_parts.append(sample_data['dev_stage'])
                            else:
                                name_parts.extend([sample_data['age'], sample_data['dev_stage']])
                        else:
                            name_parts.append(sample_data['dev_stage'])

                    # Set samples[sample]['sample_name'] to '_'-joined name parts
                    sample_data['sample_name'] = '_'.join(name_parts)
        return csv_data, samples

    def write_inputfile(self,csv_data, samples, outfile, _centre_name=''):
        output_ids = []
        output_lines_dict = {}  # Key: description, Value: list of output_line dictionaries. To order output by description/base_count

        for study_accession in csv_data:
            study = csv_data[study_accession]

            for sample in study:
                if sample not in samples:
                    continue  # Skip if sample data is not available

                for experiment in study[sample]:
                    files = experiment['fastq_file'].split(';')
                    checksums = experiment['fastq_md5'].split(';')
                    index = 0

                    for file in files:
                        filename = os.path.basename(file)
                        sample_name = samples[sample]['sample_name']

                        # Clean up sample_name
                        sample_name = re.sub(r'\s+-\s+\w+:\w+$', '', sample_name)
                        sample_name = re.sub(r'[\s\W]+', '_', sample_name)
                        sample_name = re.sub(r'_{2,}', '_', sample_name)
                        sample_name = sample_name.strip('_')

                        # Build description
                        cell_type_str = ''
                        if samples[sample].get('cell_type'):
                            cell_type_str = ', ' + samples[sample]['cell_type']

                        description = "{}, {}{}".format(
                            experiment['study_title'],
                            experiment['experiment_title'],
                            cell_type_str
                        )

                        for field in samples[sample].values():
                            if field:
                                description += ';' + str(field)

                        # Replace ':' and tab characters with space in description
                        description = description.replace(':', ' ').replace('\t', ' ')

                        line = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}, {}, {}\t{}\t{}\t{}\n".format(
                            sample_name.lower(),
                            experiment['run_accession'],
                            1 if experiment['library_layout'] == 'PAIRED' else 0,
                            filename,
                            -1,
                            experiment['read_length'],
                            0,
                            experiment.get('center_name') or _centre_name,
                            experiment['instrument_platform'],
                            study_accession,
                            sample,
                            description,
                            file,
                            checksums[index],
                            experiment.get('base_count',0)
                        )

                        # Collect the output line and associated data
                        base_count = int(experiment.get('base_count', 0))
                        output_line = {
                            'line': line,
                            'description': description,
                            'base_count': base_count,
                        }

                        # Organize lines by description and calculate max_base_count
                        if description not in output_lines_dict:
                            output_lines_dict[description] = {
                                'lines': [],
                                'max_base_count': base_count
                            }
                        else:
                            # Update max_base_count if current base_count is higher
                            if base_count > output_lines_dict[description]['max_base_count']:
                                output_lines_dict[description]['max_base_count'] = base_count

                        output_lines_dict[description]['lines'].append(output_line)

                        # Collect output IDs
                        output_ids.append({
                            'url': file,
                            'download_method': 'https',
                            'checksum': checksums[index]
                        })
                        index += 1

        # Sort descriptions by their maximum base_count in descending order
        sorted_descriptions = sorted(
            output_lines_dict.items(),
            key=lambda item: -item[1]['max_base_count']
        )


        # Write the sorted lines to the output file
        with open(outfile, 'w') as fh:
            for description, data in sorted_descriptions:
                # Sort lines within each description by descending base_count
                lines = data['lines']
                lines.sort(key=lambda x: -x['base_count'])

                # For debugging: print description and base_counts
                print(f"description: {description}")
                for line_data in lines:
                    print(f"base_count: {line_data['base_count']}")

                # Write each line to the file
                for output_line in lines:
                    fh.write(output_line['line'])

        return output_ids

    def parse_header(self, content):
        header = content.split('\n')[0]
        result = {field: idx for idx, field in enumerate(header.split('\t'))}
        #print("header dict: " + str(result))
        return result

    def should_skip_line(self, line):
        if line == '':
            return True

        # Check for words related to infection or immune challenges, including variations of 'immunize', 'challenge', 'tomize'
        infection_patterns = [
            r'\binfected\b',
            r'[iIu]mmune',
            r'challenge',
            r'tomi[zs]ed',  # Allow for different endings
        ]
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in infection_patterns):
            return True

        # Check for RNA types including variations
        rna_patterns = [
            r'mi\w{0,3}RNA',  # \w{0,3} allows for up to three letters between 'mi' and 'RNA'
            r'lncRNA',
            r'circRNA',
            r'small RNA',
        ]
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in rna_patterns):
            return True

        # If none of the patterns match, the line should not be skipped
        return False

    def check_paired_end(self, row, fields_index):
        layout = row[fields_index['library_layout']]
        fastq_files = row[fields_index['fastq_ftp']].split(';')
        if layout == 'PAIRED' and len(fastq_files) == 2:
            return True

    def filter_paired_end_fastq_entries(self, row, fields_index):
        # Assume 'row' is a dictionary and 'fields_index' maps field names to their indices in 'row'
        files = row[fields_index['fastq_ftp']].split(';')
        checksums = row[fields_index['fastq_md5']].split(';')
        gzs =  row[fields_index['submitted_ftp']].split(';')

        if len(files) > 2:
            # Initialize to rebuild the file and checksum strings only if there are paired-end files
            new_files = []
            new_checksums = []
            new_gzs = []
            file_count = 0
            # Iterate over files and their respective checksums
            for file, checksum, gunzip in zip(files, checksums, gzs):
                # Check if the file name ends with '_1.fastq.gz' or '_2.fastq.gz'
                if '_1.fastq.gz' in file or '_2.fastq.gz' in file:
                    new_files.append(file)
                    new_checksums.append(checksum)
                    new_gzs.append(gunzip)
                    file_count += 1
                # If exactly two paired-end files are found, update the row data
            if file_count == 2:
                row[fields_index['fastq_ftp']] = ';'.join(new_files)
                row[fields_index['fastq_md5']] = ';'.join(new_checksums)
                row[fields_index['submitted_ftp']] = ';'.join(new_gzs)
            else:
                raise ValueError(f"The number of parsed fastq files must be 2 but it is {file_count} for line: {row}")

        return row

    def calculate_read_length(self, row, fields_index):
        base_count = int(row[fields_index['base_count']])
        read_count = int(row[fields_index['read_count']])
        return (base_count / read_count) / 2 #divided by 2 assuming we only have PAIRED library layout

    def determine_run_accession(self, row, fields_index):
        return row[fields_index['run_accession']]

    def _retrieve_biosample_info(self, ua, json_decoder, current_sample, data):
        # Set the request headers
        headers = {'Content-Type': 'application/json'}

        # Make the GET request to retrieve BioSample information
        response = ua.get(f'http://www.ebi.ac.uk/biosamples/samples/{current_sample}', headers=headers)

        if response.status_code == 200:
            content = response.text
            if content:
                json_data = json_decoder.decode(content)

                # Check for disease-related keywords for removal
                for disease in self.disease_keyword_for_removal:
                    if disease in json_data.get('characteristics', {}) and \
                       json_data['characteristics'][disease][0]['text'] not in ['control', 'normal']:
                        print(f"Removed {current_sample} from the set as it has {disease} value: "
                                     f"{json_data['characteristics'][disease][0]['text']}")
                        return -1

                # Check health status at collection
                if 'health status at collection' in json_data.get('characteristics', {}) and \
                   json_data['characteristics']['health status at collection'][0]['text'] != 'normal':
                    print(f"Removed {current_sample} from the set as its health status is: "
                                 f"{json_data['characteristics']['health status at collection'][0]['text']}")
                    return -1

                # Process relationships (recursive retrieval of related samples)
                if 'relationships' in json_data:
                    for item in json_data['relationships']:
                        if current_sample != item['target']:
                            if self._retrieve_biosample_info(ua, json_decoder, item['target'], data) == -1:
                                return -1

                # Process developmental stage
                for dev_stage in ['developmental stage', 'dev stage']:
                    if dev_stage in json_data.get('characteristics', {}):
                        if 'dev_stage' in data and data['dev_stage'] != json_data['characteristics'][dev_stage][0]['text']:
                            print(f"Replacing {data['dev_stage']} with {json_data['characteristics'][dev_stage][0]['text']}")
                        data['dev_stage'] = json_data['characteristics'][dev_stage][0]['text']
                        break

                # Process sex
                for sex in ['sex', 'ArrayExpress-Sex']:
                    if sex in json_data.get('characteristics', {}) and \
                       json_data['characteristics'][sex][0]['text'] not in self.param('bad_text_sex_field', {}):
                        if sex in data and data[sex] != json_data['characteristics'][sex][0]['text']:
                            print(f"Replacing {data[sex]} with {json_data['characteristics'][sex][0]['text']}")
                        data['sex'] = json_data['characteristics'][sex][0]['text']

                # Process age
                for age_string in ['gestational age at sample collection', 'animal age at collection', 'age']:
                    if age_string in json_data.get('characteristics', {}):
                        age_value = f"{json_data['characteristics'][age_string][0]['text']} {json_data['characteristics'][age_string][0]['unit']}"
                        if 'age' in data and data['age'] != age_value:
                            print(f"Replacing {data['age']} with {age_value}")
                        data['age'] = age_value
                        break

                # Process sample alias
                for sample_string in ['sample_name', 'sample description', 'alias', 'synonym', 'title']:
                    if sample_string in json_data.get('characteristics', {}):
                        sample_text = json_data['characteristics'][sample_string][0]['text']
                        if 'sample_alias' in data and data['sample_alias'] != sample_text:
                            print(f"Replacing {data['sample_alias']} with {sample_text}")
                        if len(sample_text) > 50:
                            data['sample_alias'] = "whole_body"
                        else:
                            data['sample_alias'] = sample_text

                # Further validation on sample_alias
                if 'sample_alias' in data and json_data['name'] in data['sample_alias'] and \
                   len(json_data['name']) < len(data['sample_alias']):
                    data.clear()
                    return 0

                # Process organism part (tissue type)
                for tissue in ['cell type', 'organism part', 'ArrayExpress-OrganismPart', 'tissue', 'tissue_type', 'tissue type']:
                    if tissue in json_data.get('characteristics', {}):
                        tissue_text = json_data['characteristics'][tissue][0]['text']
                        if 'organismPart' in data and data['organismPart'] != tissue_text:
                            print(f"Replacing {data['organismPart']} with {tissue_text}")
                        if len(tissue_text) > 30:
                            data['organismPart'] = "whole_body"
                        else:
                            data['organismPart'] = tissue_text
                        break

                # Handle embryo cases
                if 'age' in json_data.get('characteristics', {}) and 'embryo' in data.get('organismPart', ''):
                    data['organismPart'] = f"embryo_{json_data['characteristics']['age'][0]['text']}"
                    data['organismPart'] = data['organismPart'].replace(' ', '_')

                return 1
            else:
                print(f"{current_sample} not found in BioSample")
                return 0
        else:
            print(f"Failed to get {current_sample}, error is {response.status_code}")
            return 0


    def process_biosample_content(self, content, data):
        lines = content.split("\n")
        for line in lines:
            if line[0].islower(): # assumes header
                fields = line.split('\t')
                fields_index = {field: index for index, field in enumerate(fields)}  # Create a dictionary mapping fields to their indices
                header = line  # Store the line as header
            else:
                row = line.strip().split("\t")
                data = {
                    'center_name': row[fields_index['center_name']],
                    'cell_line': row[fields_index['cell_line']],
                    'cellType': row[fields_index['cell_type']],
                    'dev_stage': row[fields_index['dev_stage']],
                    'sex': row[fields_index['sex']],
                    'strain': row[fields_index['strain']],
                    'sub_species': row[fields_index['sub_species']],
                    'sub_strain': row[fields_index['sub_strain']],
                    'tissue_lib': row[fields_index['tissue_lib']],
                    'organismPart': row[fields_index['tissue_type']],
                    'variety': row[fields_index['variety']],
                    'tax_id': row[fields_index['tax_id']],
                    'description': row[fields_index['description']],
                    'sample_collection': row[fields_index['sample_collection']],
                    'sequencing_method': row[fields_index['sequencing_method']],
                    'sample_alias': row[fields_index['sample_alias']],
                }
                invalid_sex_types = ['not determined', 'not collected', 'missing']
                if data['sex'] in invalid_sex_types:
                    data['sex'] = None
        return  data

def main( tax_id, outdir):
    # Example usage
    ena_downloader = DownloadCsvENA(
    ena_base_url="https://www.ebi.ac.uk/ena/portal/api/search?display=report",
    download_method='ftp',
    read_type='short_read',
    max_long_read_read_count=1000000,
    queries=[f"\"tax_tree({tax_id})%20AND%20instrument_platform=ILLUMINA%20AND%20library_source=TRANSCRIPTOMIC%20AND%20library_layout=PAIRED\""]
    )
    csv_data, samples = ena_downloader.query_ena()

    download_files = ena_downloader.write_inputfile(csv_data, samples, outdir)
    if download_files != {}:
        nb_files = len(download_files)
        return "ENA successfully downloaded " + str(nb_files) + "files to " + outdir
    else:
        return "ENA download ERROR"


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("The taxa or the output dir for csv files is/are missing as an argument.")
    else:
        tax_id = sys.argv[1]
        outpath = sys.argv[2]

        main(tax_id, outpath)
