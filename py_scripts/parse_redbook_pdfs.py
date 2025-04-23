import requests
from bs4 import BeautifulSoup
import os
import re
import argparse
import time
import json
from dotenv import load_dotenv
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
import nest_asyncio
import os
import numpy as np
import random


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', default='corpus/RedBook/pdfs')
    parser.add_argument('--output_dir', default = 'corpus/RedBook/raw')
    parser.add_argument('--api_key',
                        type=str
                        )
    return parser.parse_args()

def main():
    args = parse_args()
    load_dotenv()
    nest_asyncio.apply()

    parser = LlamaParse(
    result_type="markdown",api_key=args.api_key
    )
    file_extractor = {".pdf": parser}

    input_dir = args.input_dir
    output_dir = args.output_dir
    input_files = os.listdir(input_dir)
    random.shuffle(input_files)
    input_files = os.listdir(args.input_dir)
    for this_file in input_files:
        if this_file.endswith('.pdf'):
            full_path = os.path.join(input_dir,this_file)
            output_path = os.path.join(output_dir, this_file.replace('.pdf','.txt'))
            print("Input pdf: ", full_path)
            print("Output txt: ", output_path)
            if not os.path.exists(output_path):
                documents = SimpleDirectoryReader(input_files=[full_path], file_extractor=file_extractor).load_data()
                with open(output_path, 'w') as file:
                    file.write(documents[0].text)

            
if __name__=='__main__':
    main()