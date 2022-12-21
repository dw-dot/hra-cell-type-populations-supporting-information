import csv
import requests
import time
import json



def main():
    TOKEN = "Agv0nl80boPq8nb8b1NqenG1xNz7Y79XvjvrWW90j633BOaPKYtzC9GDJEVX0PwY8EEv2bgnYKBpM3fOgNGydsw57l"
    # base_url = "https://entity.api.hubmapconsortium.org/entities/"
    ccf_api_url = "https://ccf-api.hubmapconsortium.org/v1/hubmap/rui_locations.jsonld"
    headers = {"Authorization": "Bearer " + TOKEN}
    
    with open('Combined Provenance (HuBMAP and non-HuBMAP) - Sheet1.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        
        source_counts = {}
        uuids = set()
        
        for row in csv_reader:
            
            # guarding clause
            if not row[0].isalnum():
                continue
            
            # collect uuids
            if row[7] != "":
                uuids.add(row[7])

            # collect #datasets per source in a dict
            if row[2] in source_counts:
                source_counts[row[2]] = source_counts[row[2]] + 1
            else:
                source_counts[row[2]] = 1

        for key in source_counts:
            print(f'{key}: {source_counts[key]}')

    # get ccf_annotations
    dict_id_annotation = {}
    response = requests.get(ccf_api_url, headers=headers).json()
    # f = open("ccf_api_response_rui_locations.jsonld")
    f = open("ccf_api_response_rui_locations_TOKEN.jsonld")
    response = json.load(f)
    print(len(response['@graph']))
    for id in uuids:
            for donor in response['@graph']:
                for sample in donor['samples']:
                    if id in sample['@id']:
                        print(id)
                        dict_id_annotation[id] = {'tissue_block': 'self',
                                                  'ccf_annotations': sample['rui_location']['ccf_annotations']}
                    for dataset in sample['datasets']:
                        if id in dataset['@id']:
                            print(id)
                            dict_id_annotation[id] = {'tissue_block':sample['@id'], 'ccf_annotations': sample['rui_location']['ccf_annotations']}

    f.close()
    for key in dict_id_annotation:
        print(f'{key}: {dict_id_annotation[key]}')

#     save as csv
    f = open('ccf_annotations.csv', 'w', newline='')
    writer = csv.writer(f,delimiter=',')
    writer.writerow(['dataset_id', 'tissue_block_id','ccf_annotations'])

    for key in dict_id_annotation:
        row = [key, dict_id_annotation[key]['tissue_block'], dict_id_annotation[key]['ccf_annotations']]
        writer.writerow(row)

    # close the file
    f.close()

if __name__ == "__main__":
    main()
