from openai import OpenAI


def rate_similarity(c1:list, c2:list) -> str:
    client = OpenAI(api_key='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')
