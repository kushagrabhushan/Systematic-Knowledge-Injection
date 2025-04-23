import os
import argparse
import json
from tqdm import tqdm
import shutil

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', default='corpus/RedBook/raw')
    parser.add_argument('--output_dir', default='corpus/RedBook/raw_with_titles')
    parser.add_argument('--titles_file', default = 'corpus/RedBook/titles.json')
    return parser.parse_args()

def main():
    args = parse_args()
    input_files = os.listdir(args.input_dir)
    pdf2title = json.load(open(args.titles_file))
    os.makedirs(args.output_dir, exist_ok=True)
    skip_files = [f'book{x}.txt' for x in range(1,4,1)]
    for this_file in tqdm(input_files):
        #print(this_file)
        this_path = os.path.join(args.input_dir, this_file)
        out_path = os.path.join(args.output_dir, this_file)
        lines = open(this_path).readlines()
        this_pdf_file = this_file.replace('.txt','.pdf')
        if (
            (this_pdf_file in pdf2title) and 
            (this_file not in skip_files) and 
            (not os.path.islink(this_path))
        ):
            this_title = pdf2title[this_pdf_file]
            lines = [f'{this_title}\n']+lines
            with open(out_path, 'w') as dest:
                dest.writelines(lines)
        else:
            if (this_pdf_file not in pdf2title) : 
                print("Missing title. ", this_file)
            if (not os.path.islink(this_path)):
                shutil.copy(this_path, out_path)

            
if __name__=='__main__':
    main()
