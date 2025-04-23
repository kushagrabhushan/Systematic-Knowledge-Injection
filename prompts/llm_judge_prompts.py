mixtral_cot = """[INST] You are given a question, the corresponding ground-truth answer and a prediction from a model. Compare the \"Ground-truth answer\" and the \"Prediction\" to determine whether the prediction correctly answers the question.
There should be no contradicting statements in a good prediction. The prediction may contain extra information. If the prediction states something as a possibility, treat it as a definitive answer.
A good prediction must contain all the important information presented in the ground truths, but doesn't have to fully match it word by word.
To make your decision, first read the question and Ground-truth answer carefully. Then compare the given Prediction with the Ground-truth answer in the light of the question. 
Start with an explanation and reasoning for your evaluation within <explanation> and </explanation> tags.
Then, within <score> and </score> tokens, generate \"1\" if the Prediction is correct in the light of Ground-truth and question. Otherwise generate \"0\" if it is incomplete or incorrect.  

Question: {question}
Ground-truth answer: {gold_response}
Prediction: {predicted_response}
[/INST]
Answer:"""

llama3_70b_cot = """<|start_header_id|>user<|end_header_id|> You are given a question, the corresponding ground-truth answer and a prediction from a model. Compare the \"Ground-truth answer\" and the \"Prediction\" to determine whether the prediction correctly answers the question.
There should be no contradicting statements in a good prediction. The prediction may contain extra information. If the prediction states something as a possibility, treat it as a definitive answer.
A good prediction must contain all the important information presented in the ground truths, but doesn't have to fully match it word by word.
To make your decision, first read the question and Ground-truth answer carefully. Then compare the given Prediction with the Ground-truth answer in the light of the question. 
Start with an explanation and reasoning for your evaluation within <explanation> and </explanation> tags.
Then, within <score> and </score> tokens, generate \"1\" if the Prediction is correct in the light of Ground-truth and question. Otherwise generate \"0\" if it is incomplete or incorrect.  

Question: {question}
Ground-truth answer: {gold_response}
Prediction: {predicted_response}

Answer:<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
