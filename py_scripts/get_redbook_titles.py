import requests
from bs4 import BeautifulSoup
import os
import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', default='corpus/RedBook/pdfs')
    parser.add_argument('--output_file', default = 'corpus/RedBook/titles.json')
    return parser.parse_args()

def main():
    args = parse_args()
    input_files = os.listdir(args.input_dir)
    pdf2title = {}
    for this_file in input_files:
        path = f"/abstracts/{this_file.replace('pdf','html')}"
        r = requests.get(f"https://www.redbooks.ibm.com/{path}")
        if r.status_code == 200:
            s = BeautifulSoup(r.text, "html.parser")
            pdf2title[this_file] = s.title.text
            #print(f"{this_file} title: {s.title.text}")
        else:
            print("couldn't find ", this_file)
        
    with open(args.output_file,'w') as file:
        json.dump(pdf2title,file)
            
if __name__=='__main__':
    main()
