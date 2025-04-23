base_data_creation_prompt="""<s> [INST] Create question answer pairs from the document given below within <document> tags. Title of the document is given in the first line of the document. Do not use co-referencing and pronouns at all in the questions. Do not refer to the document in the question like \"according to the document ...\" or any similar paraphrasing. When needed,  contextualize the question by using the topic that the question is about. You can use the title of the document as well for contextualizing. There are several figures in the document, while referring to the figure in any question, contextuailize it by mentioning the title of the passage it was present in. Put questions within <question>  and </question> tags and answers within <answer> and </answer> tags. Ensure that the question and answers cover the entire document. When you are done generating QA pairs, generate  </done> token.[/INST]"""

multiple_answers_prompt="""<s> [INST] You are provided with a document within <document> and </document> tags. Followed by the document, you are provided with a question within <question> and </question> tags. Using only the information provided in the document, generate multiple correct, complete and comprehensive answers for the given question, varying the style and format. Each of your answers should be within separate <answer> and </answer> tags so that I can parse and extract them using a code.  Each answer must be complete, correct, comprehensive and only from the provided document. 
Start by first generating <answer> token. Then generate one valid answer following any one style or format. Then generate  </answer> token. Then again generate <answer> token, followed by another valid answer. Then generate </answer> token. Keep on repeating this till you generate as many correct answers as possible. In the end, generate </done> token once you are done generating all the answers in all possible styles and formats. 

Some example styles and format that you must use: 

1. List Answer: Answer can be in the form of a list. 

2. Extractive answer:  Answer with extracted sentences from the document. 

3. Abstractive answer: Abstractive answer that paraphrases the information in the given document.

4. Short answer:  A Terse response that is succinct but contains all relevant information. 

Feel free to generate as many more styles possibles.  

Remember that each answer should be correct, comprehensive and complete.
You don't have to mention the answer style in an answer. Each answer should be within seperate <answer> and </answer> tokens. Generate </done> in the end once you are done generating all answers.[/INST]"""


test_data_filter_prompt="""<s> [INST] You are given a question, and your task is to determine whether the question is complete and makes sense in isolation. A complete question should not contain text like "based on given example" or "mentioned in the chapter" because only question text is there to answer it, not the chapter or examples. Based on this, assign a final score of **Complete** or **Incomplete** for the question. Only assign **Incomplete** if the question uses phrases like these: "based on given example" or "mentioned in the chapter".
**Scoring:** 
- **Complete:** The question contains all necessary details. 
- **Incomplete:** The question uses phrases like "based on given example", "mentioned in the chapter", "mentioned in the passage", "given in the document", or something similar. 
Provide your feedback in the following format: 
'''
Feedback::: 
Evaluation: (Provide your rationale for the scoring in detail) 
Scoring: (State "Complete" or "Incomplete") 
'''
**Important:** You must provide values for both 'Evaluation:' and 'Scoring:' in your answer. 
Now, here is the question: 
**Question:** {question}
Provide your feedback. 
Feedback::: 
Evaluation: [/INST]"""

