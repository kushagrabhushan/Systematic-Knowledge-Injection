parag_prompt = """<s> [INST] You are an AI assistant who is provided with a conversation between a user and an agent. User utterances start with "User:" and agent utterances start with "Agent:". Your task is to generate agent’s response to the last user utterance. Enclosed within <passage> tags, you will find various excerpts. These passages may or may not contain the answer. You may or may not use the information in them to generate your response. Present your response within <response> and </response> tokens. 

<passage_0> {document_0} </passage_0> 
<passage_1> {document_1} </passage_1> 
<passage_2> {document_2} </passage_2> 
<passage_3> {document_3} </passage_3> 
<passage_4> {document_4} </passage_4> 

User: {data_identifier} {question} 
[/INST] 
### Answer:
"""

raft_prompt = """<s> [INST] You are an AI assistant who is provided with a conversation between a user and an agent. User utterances start with "User:" and agent utterances start with "Agent:". Your task is to generate agent’s response to the last user utterance. Enclosed within <passage> tags, you will find various excerpts. These passages may or may not contain the answer. You may or may not use the information in them to generate your response. Present your response within <response> and </response> tokens. 

<passage_0> {document_0} </passage_0> 
<passage_1> {document_1} </passage_1> 
<passage_2> {document_2} </passage_2> 
<passage_3> {document_3} </passage_3> 
<passage_4> {document_4} </passage_4> 

User: {question} 
[/INST] 
### Answer:
"""

dsf_prompt = """<s> [INST] You are an AI assistant who is provided with a conversation between a user and an agent. User utterances start with "User:" and agent utterances start with "Agent:". Your task is to generate agent's response to the last user utterance. Present your response within <response> and </response> tokens. User: {question} 
[/INST] 
### Answer:
"""