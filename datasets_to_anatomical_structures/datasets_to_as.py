import csv
import requests
import time
import json



def main():
    TOKEN = ""
    # base_url = "https://entity.api.hubmapconsortium.org/entities/"
    ccf_api_url = "https://ccf-api.hubmapconsortium.org/v1/hubmap/rui_locations.jsonld"
    entity_api_url = "https://entity.api.hubmapconsortium.org/entities/"
    headers = {"Authorization": "Bearer " + TOKEN}

    # get #datasets per source and unique UUIDs
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

    # get ccf_annotations for HuBMAP datasets
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
                        dict_id_annotation[id] = {'tissue_block': 'self',
                                                  'ccf_annotations': sample['rui_location']['ccf_annotations']}
                    for dataset in sample['datasets']:
                        if id in dataset['@id']:
                            dict_id_annotation[id] = {'tissue_block':sample['@id'].split('/')[-1], 'ccf_annotations': sample['rui_location']['ccf_annotations']}

    f.close()
    for key in dict_id_annotation:
        print(f'{key}: {dict_id_annotation[key]}')

#     save as csv
    f = open('ccf_annotations.csv', 'w', newline='')
    writer = csv.writer(f,delimiter=',')
    writer.writerow(['dataset_id', 'tissue_block_id','ccf_annotations','hubmap_id'])

    for key in dict_id_annotation:
        row = [key, dict_id_annotation[key]['tissue_block'], dict_id_annotation[key]['ccf_annotations']]
        writer.writerow(row)

    # close the file
    f.close()


#     get ccf_annotations for Blue Lake kidney and Soumya skin (with HuBMAP IDs)
    with open('Combined Provenance (HuBMAP and non-HuBMAP) - Sheet1.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        dict_organ_hubmap_ids = {"soumya": [], "blue_lake": []}

        for row in csv_reader:
            if row[1][0:3] == "HBM":
                for person in list(dict_organ_hubmap_ids.keys()):
                    if person in row[2].lower():
                        tissue_block = { "hubmap_id": row[1][:-4],"uuid": "",'parent':'', "ccf_annotations":""}
                        dict_organ_hubmap_ids[person].append(tissue_block)

        for key in dict_organ_hubmap_ids:
            for tissue_block in dict_organ_hubmap_ids[key]:
                response = requests.get(entity_api_url + tissue_block["hubmap_id"]).json()
                try:
                    tissue_block['uuid'] = response['uuid']
                except:
                    tissue_block['uuid'] = f'tissue block {tissue_block["hubmap_id"]} not found on Entity API'
                    continue

                try:
                    tissue_block['ccf_annotations'] = response['rui_location']['ccf_annotations']
                    tissue_block['parent'] = tissue_block['uuid']
                except:
                    one_up_response = requests.get(entity_api_url + response['direct_ancestors'][0]['hubmap_id']).json()
                    tissue_block['ccf_annotations'] = one_up_response['direct_ancestor']['rui_location']['ccf_annotations']
                    tissue_block['parent'] = one_up_response['uuid']

        print(dict_organ_hubmap_ids)

        #     save as csv
        f = open('ccf_annotations.csv', 'a', newline='')
        writer = csv.writer(f, delimiter=',')

        for person in dict_organ_hubmap_ids:
            for tissue_block in dict_organ_hubmap_ids[person]:
                row = [tissue_block['uuid'], tissue_block['parent'], tissue_block['ccf_annotations'], tissue_block['hubmap_id']+'.csv']
                writer.writerow(row)

        # close the file
        f.close()

if __name__ == "__main__":
    main()
