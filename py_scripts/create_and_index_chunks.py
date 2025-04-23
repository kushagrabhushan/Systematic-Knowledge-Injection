import os
import pandas as pd
from collections import OrderedDict, defaultdict
import os
import argparse
import pandas as pd
import json
import re
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter, SemanticSplitterNodeParser
from llama_index.core import VectorStoreIndex, Document
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, load_index_from_storage
from tqdm import tqdm
from IPython.core.debugger import Pdb
from llama_index.core.schema import TextNode


def parse_arguments(arg_string=None):
    parser = argparse.ArgumentParser(description='dataset chunking')
    parser.add_argument('--data_path_dir', type=str, default='corpus/RedBook/raw_with_titles',
                        help = 'path to all md files')
    parser.add_argument('--dataset_save_path', type=str, default="corpus/RedBook/all_index",
                        help='path to save single_nodes.jsonl that contains all the chunks')
    parser.add_argument('--chunk_size', type=int, default=500)
    parser.add_argument('--model_name', type=str, default="BAAI/bge-large-en-v1.5",
                        help='Model name for embedding.')
    parser.add_argument('--db_path', type=str, default="chroma_db",
                        help='subdir where vectorstore is created within dataset_save_path')
    
    parser.add_argument('--should_index', type=int, default=1,help='should create index or just create chunks?')
    
    if arg_string is None:
        return parser.parse_args()
    else:
        return parser.parse_args(arg_string.split())



def get_chapter_text(doc, chapter):
    pattern = re.compile(rf"# Chapter {chapter}\.(.*?)# Chapter {chapter+1}\.", re.DOTALL)
    matches = pattern.findall(doc)
    if len(matches) > 1:
        return f"# Chapter {chapter}. "+ matches[1]
    else:
        pattern = re.compile(rf"# Chapter {chapter}\.", re.DOTALL)
        matches = list(pattern.finditer(doc))
        if len(matches) > 0:
            try:
                second_match_position = matches[1].end()
            except:
                second_match_position = matches[0].end()
            return f"# Chapter {chapter}. "+ doc[second_match_position:]
        else:
            return None
        

def capture_chapter_title(text, chapter_number):
    pattern = re.compile(rf"Chapter {chapter_number}\.\s*(.*)")
    match = pattern.search(text)
    
    if match:
        return match.group(1).strip()
    else:
        return None
    
    
def chunk_by_chapter_heuristic(data_path, node_parser):
    with open(data_path) as file:
        document = file.readlines()
        book_name = document[0].strip()
        document = ''.join(document[1:])
    
    chapters = OrderedDict()
    empty_chapter_counter = 0 
    current_chapter = 1
    end_of_book = False 
    while not end_of_book:
        this_chapter = get_chapter_text(document,current_chapter)
        if this_chapter is None:
            empty_chapter_counter += 1
            print("Current chapter: ", current_chapter, "empty chapter count: ", empty_chapter_counter)
            if empty_chapter_counter == 5:
                end_of_book = True 
        else:
            chapters[current_chapter] = Document(text=this_chapter)
        #
        current_chapter += 1

    all_nodes = []
    for chapter_no, chapter in chapters.items():
        nodes = node_parser.get_nodes_from_documents([chapter])
        print(f"Number of nodes created for book {book_name}, chapter {chapter_no}:   {len(nodes)}")
        all_nodes.extend(nodes)
        print(f"Number of cumulative nodes:   {len(all_nodes)}")
        for i, node in enumerate(nodes):
            passage_no = i+1
            if node.text.startswith("# Chapter "):
                assert passage_no == 1
                pattern = re.compile(r"# Chapter (\d+)\.")
                matches = pattern.findall(node.text)
                if chapter_no != int(matches[0]):
                    print("mismatch b/w recorded chapter number and chapter number extracted from the text: ", chapter_no, matches[0])

                chapter_title = capture_chapter_title(node.text, chapter_no)
                header_str = f"Book name: {book_name}\n\n"
                node.text = header_str + node.text
            else:
                passage_no += 1
                header_str = f"Book name: {book_name}\n\n"
                node.text = header_str + node.text

            node.metadata = {
                                "book_title": book_name,
                                "book_id": os.path.basename('.'.join(data_path.split('.')[:-1]))
                            }
    return all_nodes

def create_chunks(data_path, node_parser):
    with open(data_path) as file:
        document = file.readlines()
        book_name = document[0].strip()
        document = ''.join(document[1:])

    book = Document(text=document)
    all_nodes = node_parser.get_nodes_from_documents([book])
    print(f"Number of nodes created for book {book_name}:   {len(all_nodes)}")
    for i, node in enumerate(all_nodes):
        header_str = f"Book name: {book_name}\n\n"
        node.text = header_str + node.text
        node.metadata = {
                            "book_title": book_name,
                            "book_id": os.path.basename('.'.join(data_path.split('.')[:-1]))
                        }
    return all_nodes





def main():
    args = parse_arguments()
    embed_model = HuggingFaceEmbedding(model_name=args.model_name)
    Settings.embed_model = embed_model
    
    dst_md_dir = args.data_path_dir
    current_files = os.listdir(dst_md_dir)

    os.makedirs(args.dataset_save_path, exist_ok=True)

    out_file = os.path.join(args.dataset_save_path,'single_nodes.jsonl')
    print("Chunks stored in ", out_file)
    if not os.path.exists(out_file):
        node_parser = SentenceSplitter(
                        chunk_size=args.chunk_size, 
                        chunk_overlap=0,
        )
        nodes = OrderedDict()
        total_num_nodes = 0
        for data_path in current_files:
            full_path = os.path.join(dst_md_dir, data_path)
            if data_path == 'redp5736.txt':
                print("create chunks by chapters for ", data_path)
                nodes[data_path] = chunk_by_chapter_heuristic(full_path,node_parser)
            else:
                nodes[data_path] = create_chunks(full_path, node_parser)
            #
            total_num_nodes += len(nodes[data_path])
            print("chunked ", data_path, " total nodes:: ", total_num_nodes)

        all_chunks = {'chunk_id': [], 'int_id': [], 'book_id': [], 'book_title': [],  'text': []}
        for book_id, this_nodes in nodes.items():
            for this_node in this_nodes:
                all_chunks['int_id'].append(len(all_chunks['chunk_id']))
                all_chunks['chunk_id'].append(this_node.node_id)
                all_chunks['text'].append(this_node.text)
                for k,v in this_node.metadata.items():
                    all_chunks[k].append(v)


        chunks_tab =pd.DataFrame(all_chunks)
        chunks_tab.to_json(out_file, lines=True, orient='records')
    else:
        print("chunks file already exists.. creating vectorstore", out_file)
    # index the nodes
    if args.should_index:
        chunks_tab = pd.read_json(out_file, lines=True)
        all_nodes = []
        for _, row in chunks_tab.iterrows():
            node = TextNode(
                text=row['text'],
                id_=str(row['int_id']),  # Ensure ID is a string
                metadata={col: row[col] for col in chunks_tab.columns if col not in ['text', 'int_id']},
            )
            all_nodes.append(node)
        #
        db_path = os.path.join(args.dataset_save_path, args.db_path)
        db = chromadb.PersistentClient(path=db_path)
        chroma_collection = db.get_or_create_collection("quickstart")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex(all_nodes)    
        index.storage_context.persist(persist_dir=db_path)



if __name__=='__main__':
    main()