import csv

def main():
    with open('Combined Provenance (HuBMAP and non-HuBMAP) - Sheet1.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        
        source_dict = {}
        for row in csv_reader:
            
            # guarding clause
            if not row[0].isalnum():
                continue
            
            # collect #datasets per source in a dict
            if row[2] in source_dict:
                source_dict[row[2]] = source_dict[row[2]] + 1
            else:
                source_dict[row[2]] = 1
        for key in source_dict:
            print(f'''
                  {key}: {source_dict[key]}
                  ''')
            
if __name__ == "__main__":
   main()
