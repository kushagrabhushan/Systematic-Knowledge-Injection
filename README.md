# pa-rag
Official Repository for [Systematic Knowledge Injection into Large Language Models via Diverse Augmentation for Domain-Specific RAG](https://arxiv.org/abs/2502.08356)


## Resources

We provide the following resources:

1. **Data**:
   - `corpus/RedBook/raw_with_titles`: Markdown files corresponding to randomly selected 71 Redbook papers (publically available).
     
   - `corpus/all_index/single_nodes.jsonl`: 4798 chunks of size 512 tokens created from the above red books using Llamaindex
     
   - `corpus/RedBook/redp5736/subdocs_for_synthetic_qa.jsonl`: Sub-documents (chunks of size ~4000 to ~8000 tokens) from redbook [redp5711](https://www.redbooks.ibm.com/redpapers/pdfs/redp5711.pdf) (book1 in the paper). These subdocs are used to create synthetic QA.
     
   - `corpus/RedBook/redp5711/subdocs_for_synthetic_qa.jsonl`: Sub-documents (chunks of size ~4000 to ~8000 tokens) from redbook [redp5711](https://www.redbooks.ibm.com/redpapers/pdfs/redp5711.pdf) (book2 in the paper). These subdocs are used to create synthetic QA.
     

3. **Synthetic QA test data**:
   - `qa_data/redp5736/test.jsonl`: Test data for book1.
     
   - `qa_data/redp5736/with_retrieved_passages/retrieved_test.jsonl`: same as above, with top 20 retrieved chunks from `corpus/all_index/single_nodes.jsonl`
     
   - `qa_data/redp5736/with_retrieved_passages_corrupted_0.4/retrieved_test.jsonl`: obtained by running `py_scripts/corrupt_retriever.py` on the file above. We report numbers using this version of the test data.
  
4. **Scripts:**
   - Scripts to download and parse redbook pdfs into markdown files:
       - `py_scripts/download_redbook_pdfs.py`
       - `py_scripts/get_redbook_titles.py`
       - `py_scripts/add_redbook_titles.py`
       - `py_scripts/parse_redbook_pdfs.py`

   -  `py_scripts/create_and_index_chunks.py`  : Script used to split markdown files into chunks that are indexed.

   
   - `py_scripts/assign_gold_passage_ids_to_subdocs.py`: Script to map subdocs (used to create synthetic data) to corresponding indexed chunks
        
     
   - `py_scripts/retrieve_passages_for_synthetic_data.py`: Script to retrieve chunks using questions in synthetic data
        

   - `py_scripts/corrupt_retriever.py`: script to corrupt the retrieved chunks

  5. **Prompts**
     - `llm_judge_prompts.py`: contains the prompts used for LLM as a Judge evaluation.
       
     - `synthetic_data_prompts.py`: prompts used for creating the synthetic data. It contains both the standard prompt used to create the basic QA dataset and another prompt to create multiple answers for each question. It also includes the prompt used to filter the test data.
       
     - `finetuning_prompts.py`: prompts used while finetuning the models.
    


## Tools used to create the resources

All the above resources have been created using publically available tools and datasets. Specifically, we use the following data/tools:

1. **Redbooks:** Downloaded using `py_scripts/download_redbook_pdfs.py` from [https://www.redbooks.ibm.com/](https://www.redbooks.ibm.com/)
   
2. **Parsing tools:** We use llama-index (https://pypi.org/project/llama-index/) for
     - parsing pdfs to markdown (`llama_parse.LlamaParse` and `llama_index.core.SimpleDirectoryReader`)
     - parsing markdown to chunks for setting up the retriever (`llama_index.core.node_parser.SentenceSplitter`  and `node_parser.get_nodes_from_documents`)
     - setting up of the vector store (`chromadb.PersistentClient` and `llama_index.vector_stores.chroma.ChromaVectorStore`)

3. **Foundation models**: The following foundation models are used from hugging face:
     - `BAAI/bge-large-en-v1.5`: for computing the embeddings for vector store in the retriever
       
     - `mistralai/Mixtral-8x22B-Instruct-v0.1`: for generating the synthetic QA data.
       
     - `mistralai/Mixtral-8x22B-Instruct-v0.1` and  `meta-llama/Llama-3.3-70B-Instruct`: for LLM as a Judge
       
     - `mistralai/Mistral-7B-Instruct-v0.2`, `meta-llama/Llama-2-7b-chat-hf` and `meta-llama/Llama-2-13b-chat-hf`: for finetuning

   All the foundation models and tools described above are publically available for research.
   

   




     
  
   
   
