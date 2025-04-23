
import os
import pandas as pd
from collections import OrderedDict, defaultdict
import os
import argparse
import pandas as pd
import json
import re
import tqdm
from collections import Counter
from rouge_score import rouge_scorer


def parse_arguments(arg_string=None):
    parser = argparse.ArgumentParser(description='assigning gold passage ids')
    parser.add_argument('--chunks_file', type=str, default='./corpus/RedBook/all_index/single_nodes.jsonl')
    parser.add_argument('--subdocs_file_list', type=str, nargs='*', 
                        default=["corpus/RedBook/redp5736/subdocs_for_synthetic_qa.jsonl",
                                 "corpus/RedBook/redp5711/subdocs_for_synthetic_qa.jsonl"]
    )

    if arg_string is None:
        return parser.parse_args()
    else:
        return parser.parse_args(arg_string.split())



def main():
    args = parse_arguments()

    chunks = pd.read_json(args.chunks_file, lines=True)

    chunks['normalized_text']  = chunks['text'].apply(lambda x: '\n'.join(x.split('\n')[1:]).strip())

    scorer = rouge_scorer.RougeScorer(rouge_types = ['rougeL'], use_stemmer=False)

    all_scores = {}
    for subdoc_file in args.subdocs_file_list:
        subdocs = pd.read_json(subdoc_file, lines=True)
        all_scores[subdoc_file] = {}
        for this_doc_ind, this_doc in tqdm.tqdm(subdocs.iterrows(),total=subdocs.shape[0]):
            subdoc_text_normalized = '\n'.join(this_doc['document'].split('\n')[1:]).strip()
            this_chunks = chunks[chunks['book_id'] == this_doc['book_id']]
            scores = []
            for _, this_chunk in this_chunks.iterrows():
                normalized_text = this_chunk['normalized_text']
                this_scores = scorer.score(normalized_text,subdoc_text_normalized)
                scores.append(this_scores)
            #
            all_scores[subdoc_file][this_doc_ind] = scores


    """
    all_boundary_scores = {}
    boundaries = []
    for fid, subdoc2scores in all_scores.items():
        all_boundary_scores[fid] = {}
        indices = subdoc2scores.keys()
        for ind in indices:
            this_scores_dict = subdoc2scores[ind]
            this_scores = [(local_ind,x['rougeL'].recall) for local_ind, x in enumerate(this_scores_dict) if x['rougeL'].recall >=0.99]
            first_ind = this_scores[0][0] - 1
            last_ind = this_scores[-1][0] + 1
            boundary_scores= []

            if first_ind >= 0:
                boundary_scores.append(round(this_scores_dict[first_ind]['rougeL'].recall,2))
                boundaries.append(round(this_scores_dict[first_ind]['rougeL'].recall,2))
            #
            if (last_ind < len(this_scores_dict)):
                boundary_scores.append(round(this_scores_dict[last_ind]['rougeL'].recall,2))
                boundaries.append(round(this_scores_dict[last_ind]['rougeL'].recall,2))
            #
            all_boundary_scores[fid][ind] = (boundary_scores,len(this_scores))
    """        


    for subdoc_file in args.subdocs_file_list:
        print("Process for: ", subdoc_file)
        subdocs = pd.read_json(subdoc_file, lines=True)
        subdoc2scores = all_scores[subdoc_file]
        out_file = '.'.join(subdoc_file.split('.')[:-1])+'_with_gold_chunk_ids.jsonl'
        gold_ids = []
        for ind, this_doc in subdocs.iterrows():
            this_chunks = chunks[chunks['book_id'] == this_doc['book_id']]
            this_scores_dict = subdoc2scores[ind]
            this_scores = [(local_ind,x['rougeL'].recall) for local_ind, x in enumerate(this_scores_dict) if x['rougeL'].recall >=0.99]
            first_ind = this_scores[0][0] - 1
            last_ind = this_scores[-1][0] + 1
            this_gold_ids = [x[0] for x in this_scores]
            for enum_ind, gold_ind in enumerate(this_gold_ids[:-1]):
                assert (gold_ind+1)==this_gold_ids[enum_ind+1]

            if first_ind >= 0:
                if this_scores_dict[first_ind]['rougeL'].recall >= 0.75:
                    print("Adding a starting boundary at score: ", this_scores_dict[first_ind]['rougeL'].recall, " for subdoc at index: ", ind)
                    this_gold_ids = [first_ind] + this_gold_ids
            #
            if (last_ind < len(this_scores_dict)):
                if this_scores_dict[last_ind]['rougeL'].recall >= 0.75:
                    print("Adding an ending boundary at score: ", this_scores_dict[last_ind]['rougeL'].recall, " for subdoc at index: ", ind)
                    this_gold_ids.append(last_ind)
            #
            gold_ids.append(this_chunks['int_id'].iloc[this_gold_ids].tolist())
        #
        subdocs['int_id_list'] = gold_ids
        subdocs.to_json(out_file, lines=True, orient='records')
        print("Writing to : ", out_file)



if __name__=='__main__':
    main()