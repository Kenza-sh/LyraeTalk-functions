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
repeat_keywords = [
    r"je ne comprends pas (du tout|très bien|clairement)",
    r"rien (capté|pigé|compris|entendu|saisi|suivi|zappé)[?!]?",  # Très familier
    r"pas (capté|pigé|compris|entendu|saisi|suivi|zappé)[?!]?",  # Très familier
    r"pas bien (capté|pigé|compris|entendu|saisi|suivi|zappé)[?!]?",  # Très familier
    r"pas tout (capté|pigé|compris|entendu|saisi|suivi[zappé])[?!]?",  # Très familier
    r"\b(capte|entends|comprends|suis|pige) pas\b",
    r"\b(capte|entends|comprends|suis|pige) rien\b",
    r"qu'est[- ]ce que tu as dit\?",
    r"qu'est[- ]ce que vous avez dit\?",
    r"rappelle(?: moi)? ce que tu as dit",
    r"rappelle(?:z moi)? ce que vous avez dit",
    r"\b(j'ai )?perdu(?: le fil)?\b",
    r"\bje suis perdu(?:e)?\b",
    r"\bje (?:ne )?captive? plus\b",
    r"je ne suis pas sûr(e) de suivre",
    r"je n'arrive pas à suivre", 
    r"c'est pas clair pour moi", 
    r"j'ai du mal à comprendre",
    r"j’ai du mal à saisir",
    r"je me perds dans ce que tu dis", 
    r"(?i)\\bje suis à côté de la plaque\\b",
    r"(?i)\\bje suis à la traîne\\b",
    r"(?i)\\bje ne suis plus dans le coup\\b",
    r"tu peux dire ça à nouveau ?",
    r"c'était quoi déjà",
    r"tu disais quoi",r"dit quoi","refaire la phrase",
    r"entendre deux fois",r"refaire au ralenti",
    r"pas concentré","remets ça, j’étais en mode pause.",
    r"j’étais ailleurs",r"balance encore une fois",r"décrocher" ,r"décroche",r"décroché",
    r"je ne (vois|saisis) pas du tout",r"comprends rien",r"vois rien",
    r"répète", r"répéter", r"redire",r'redis',r"redit", r"réitère", r"réitérer",r"reformule", r"reformuler", r"reformule à nouveau",
    r"reprends", r"reprendre",r"plus fort", r"plus lentement", r"plus clairement", r"mot par mot",
    r"une dernière fois", r"encore une fois",r"depuis le début",r"à la ramasse",r"loupé",r"louper",r"confus","reprends",
    r"ça m’est passé au-dessus",r"ça m’a échappé",r"ça m’est sorti de l’esprit",r"attends, j’ai décroché un instant",r"je suis revenu mais j’ai loupé un morceau",
    r"mot par mot",r"dire ça encore une fois",r"je ne suis plus dans le coup",r"ça va trop vite pour moi",r"c’est trop dense",r"c'est incompréhensible",r"dit quoi",
]
patterns = [re.compile(p, re.IGNORECASE) for p in repeat_keywords]
def is_repeat_request(text: str) -> bool:
    text_norm = text.lower()
    return any(p.search(text_norm) for p in patterns)
  
def classify_sentence(sentence):
    prompt = f"""
Vous êtes un assistant dont la mission est de déterminer si une phrase utilisateur exprime une demande de répétition de ce qui a déjà été dit.
Par exemple : « Pouvez-vous répéter ? », « Pardon, je n’ai pas bien entendu », « Vous avez dit quoi? ».
Phrase à classifier : {sentence}
Répondez uniquement par `True` ou `False`, sans ponctuation ni texte additionnel.
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
    return 'True' in classification


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
