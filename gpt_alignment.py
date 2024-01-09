"""
Get chunk alignment from chatGPT
"""
from openai import OpenAI

thePrompt = """You are a machine designed to align chunks from 2 sentences. This means you will be taking each chunk from one sentence and comparing it to every chunk from the other sentence. Choose the chunks with the strongest relation and assign them a score. 

The possible relations are:
	EQUI: both chunks have the same meaning, they are semantically equivalent in this context.
	OPPO: the meanings of the chunks are in opposition to each other, lying in an inherently incompatible binary relationship.
	SPE1: both chunks have similar meanings, but chunk in sentence 1 is more specific.
	SPE2: like SPE1, but it is the chunk in sentence 2 which is more specific.
	SIMI: both chunks have similar meanings, they share similar attributes and there is no EQUI, OPPO, SPE1 or SPE2 relation
	REL: both chunks are not considered similar but they are closely related by some relation not mentioned above (i.e. no EQUI, OPPO, SPE1, SPE2, or SIMI relation).
	NOALI: this chunk has not any corresponding chunk in the other sentence. Therefore, it is left unaligned.

The possible scores are a range from 0 to 5 where 0 means that the chunks are not related and 5 means their meanings are the same in the given context. 

A chunk can be aligned to multiple different chunks. Chunks can also be grouped in a relation. If a chunk has no relation to any other chunk, give it a NOALI relation to a an empty chunk. 

Present the answers in this form:
chunk from first sentence <==>chunk from the second sentence // alignment type // score 
"""

def createGPT() -> OpenAI:
    client = OpenAI(api_key="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")
    return client


def callApi(client:OpenAI, chunks:str):
    response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
            {"role": "user", "content": thePrompt},
            {"role": "user", "content": chunks}
        ]
    )
    return response.choices[0].message.content.strip()
