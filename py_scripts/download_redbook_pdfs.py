import requests
from bs4 import BeautifulSoup
import os
import re
import argparse
import time

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_path', default='corpus/RedBook/pdfs')
    parser.add_argument('--num_pdfs', default=100)
    return parser.parse_args()

def main():
    args = parse_args()
    page_no = 1
    os.makedirs(args.save_path, exist_ok=True)
    while len(os.listdir(args.save_path))<args.num_pdfs:
        response = requests.get(f"https://www.redbooks.ibm.com/?page={page_no}&ps=50")
        soup = BeautifulSoup(response.text, "html.parser")
        pdf_links = soup.find_all('a', href=re.compile(r'^\/abstracts\/[^\/]+\.html$', re.I))
        
        for link in pdf_links:
            time.sleep(2)
            pdf_url = link['href']
            pdf_name = pdf_url.split('/')[2].split('.')[0]
            
            if not pdf_name.startswith('redp'):
                continue

            if pdf_name.startswith('redp'):
                pdf_url = f"https://www.redbooks.ibm.com/redpieces/pdfs/{pdf_name}.pdf"
                response = requests.get(pdf_url)
                if response.status_code != 200:
                    pdf_url = f"https://www.redbooks.ibm.com/redpapers/pdfs/{pdf_name}.pdf"
                    response = requests.get(pdf_url)
            elif pdf_name.startswith("sg"):
                pdf_url = f"https://www.redbooks.ibm.com/redbooks/pdfs/{pdf_name}.pdf"
                response = requests.get(pdf_url)
            elif pdf_name.starts_with("tips"):
                pdf_url = f"https://www.redbooks.ibm.com/redbooks/pdfs/{pdf_name}.pdf"
                response = requests.get(pdf_url)

            pdf_path = f"{args.save_path}/{pdf_name}.pdf"
            if not os.path.exists(pdf_path):
                if response.status_code == 200:
                    with open(pdf_path, 'wb') as pdf_file:
                        pdf_file.write(response.content)
                    print(f"Downloaded: {pdf_name}")
                else:
                    print(f"Failed to download {pdf_url}")
            else:
                print(f"Already downloaded {pdf_url}")
            page_no += 1
            
if __name__=='__main__':
    main()
