from openai import AzureOpenAI
import azure.functions as func
import logging
import json
import os
import re
from unidecode import unidecode

client = AzureOpenAI(
          azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"],
          api_key= os.environ["AZURE_OPENAI_API_KEY"],
          api_version="2024-05-01-preview"
        )
llm_model="gpt-35-turbo"
repeat_slowly_keywords = [r"plus fort", r"plus lentement",r"ça va trop vite pour moi", r"tu parles trop vite", r"peux-tu ralentir",r"parle plus doucement",r"répète plus lentement",
    r"c’est trop rapide",r"j’ai du mal à suivre",r"refaire au ralenti",r"un peu moins vite", r"attends une seconde",r"mot par mot",]
patterns = [re.compile(p, re.IGNORECASE) for p in repeat_slowly_keywords ]
def is_repeat_request(text: str) -> bool:
    text_norm = text.lower()
    return any(p.search(text_norm) for p in patterns)
  
def classify_sentence(sentence):
    prompt = f""" détecte si une phrase de l’utilisateur demande de répéter plus lentement ou plus doucement ce qui a déjà été dit (parler moins vite).
Par exemple : « Pouvez-vous répéter plus lentement ? », « Pardon, vous allez trop vite », « en ralenti ».
Attention : une simple demande de répéter ne suffit pas ; il faut demander de répéter plus lentement ou plus doucement.  
Phrase à classifier : {sentence}
Répondez uniquement par True ou False, sans ponctuation ni autre texte.
"""
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        temperature=0.3,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    classification = (response.choices[0].message.content).strip().lower()
    logging.info(f"le résultat du llm est {classification}")
    return 'true' in classification


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        query = req_body.get('text')

        if not query:
            return func.HttpResponse(
                json.dumps({"error": "No query provided in request body"}),
                mimetype="application/json",
                status_code=400
            )
        if is_repeat_request(query) :
            logging.info("is_repeat_request-->True")
            result = True
        else :
              result = classify_sentence(query)
              
        return func.HttpResponse(
            json.dumps({"response": result}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
