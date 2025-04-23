import argparse
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os
import json
from tqdm import tqdm
from collections import deque
import pandas as pd
from IPython.core.debugger import Pdb

"""


python py_scripts/retrieve_passages_for_synthetic_data.py --qa_dir qa_data/redp5736/base_data --output_dir ./qa_data/redp5736/base_data/with_retrieved_passages --top_k 20
# --cache_dir qa_data/redp5736/base_data/with_retrieved_passages
"""

def parse_arguments(arg_string = None):
    parser = argparse.ArgumentParser(description='retrieval using a saved vector db')
    parser.add_argument('--db_path', type=str, default="./corpus/RedBook/all_index/chroma_db",
                        help='Path to the input database.')
    parser.add_argument('--model_name', type=str, default="BAAI/bge-large-en-v1.5",
                        help='Model name for embedding.')
    parser.add_argument("--top_k",type=int, default = 20)
    parser.add_argument("--force",type=int, default = 0)
    parser.add_argument('--qa_dir', type=str, 
                        help='path containing the train/test/val jsonl files')
    parser.add_argument('--output_dir', type=str, help='path where train/test/val files with retrieved passages is written')
    parser.add_argument('--cache_dir', type=str, default=None)
 
    if arg_string is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(arg_string.split())

    return args 

def populate_cache(args):
    if args.cache_dir is None:
        return {}
    else:
        cache = {}
        for split in ['val','test','train']:
            fname = os.path.join(args.cache_dir, f'retrieved_{split}.jsonl')
            #this_dat = json.load(open(fname))
            print("Reading ", fname)
            if os.path.exists(fname):
                this_tab = pd.read_json(fname, lines=True)

                for ind, ex in this_tab.iterrows():
                    cache[ex['question']] = (ex['retrieved_ids'], 
                                             ex['retrieved_passages']
                    )
        print("Loaded cache of size: ", len(cache))
        return cache

def main():

    args = parse_arguments()

    k = args.top_k
    
    #input_files = os.listdir(args.qa_dir)
    #input_files = [x for x in input_files if os.path.isfile(os.path.join(args.qa_dir,x))]
    #input_files = [x for x in input_files if x.endswith(('.jsonl','.json'))]
    #print(input_files)

    os.makedirs(args.output_dir, exist_ok = True)
    input_files = ['test.jsonl','train.jsonl','val.jsonl']
    #input_files = ['train.jsonl','val.jsonl']
    cache = populate_cache(args)
    model_loaded = None
    for this_input_file in tqdm(input_files):
        if not os.path.exists(os.path.join(args.qa_dir, this_input_file)):
            print('SKIP processing.. file does not exists', os.path.join(args.qa_dir, this_input_file))
            continue

        print('Start processing', os.path.join(args.qa_dir, this_input_file))
        this_output_file  = os.path.join(args.output_dir, f'retrieved_{this_input_file}')
        if os.path.exists(this_output_file) and (not args.force):
            print("output file already exists and force is set to 0. Skipping ....\n",this_output_file )
            continue

        this_data = pd.read_json(os.path.join(args.qa_dir, this_input_file), lines=this_input_file.endswith('.jsonl'))

        retrieved_id_list = []
        retrieved_passages = []
        for ind, row in tqdm(this_data.iterrows(), total=this_data.shape[0]): 
            if row['question'] not in cache.keys():
                #print("Retrieve: for: ", row['question'])
                #print("Retrieved: ", [id_map[this_node.node_id] for this_node in cache[row['question']]])
                #print(row['question'])
                #Pdb().set_trace()
                if model_loaded is None:
                    model_loaded = True
                    db_path = args.db_path
                    model_name = args.model_name
                    embed_model = HuggingFaceEmbedding(model_name=model_name)
                    #, cache_folder="/dccstor/yatinccc/projects/HF_HOME")

                    Settings.embed_model = embed_model

                    # rebuild storage context
                    print("Start rebuild storage context")
                    storage_context = StorageContext.from_defaults(persist_dir=db_path)
                    print("Finish rebuild storage context")

                    # load index
                    print("Start Load index")
                    index = load_index_from_storage(storage_context)
                    print("Finish Load index")

                    retriever = index.as_retriever(similarity_top_k=k)


                retrieved_nodes_based_on_query = retriever.retrieve(row['question'])
                rids = [int(this_sim_node.node_id) for this_sim_node in retrieved_nodes_based_on_query]
                rips = [this_sim_node.text for this_sim_node in retrieved_nodes_based_on_query]
                cache[row['question']] = (rids, rips) 
            
            retrieved_id_list.append(cache[row['question']][0])
            retrieved_passages.append(cache[row['question']][1])
        #
        this_data['retrieved_ids'] = retrieved_id_list
        this_data['retrieved_passages'] = retrieved_passages
        this_data.to_json(this_output_file, orient='records', lines=True)




if __name__ == "__main__":
    main()
