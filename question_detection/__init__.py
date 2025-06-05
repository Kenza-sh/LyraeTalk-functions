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

QUESTION_WORDS = [
    # Formes avec "est-ce que"
    "est-ce que", "est ce que", "est-ce qu’il", "est ce qu’il",
    "est-ce qu’on", "est ce qu’on", "est-ce que tu", "est ce que tu",
    "est-ce que vous", "est ce que vous", "est-ce que je", "est ce que je",

    # Questions temporelles
    "à quelle heure", "à quel moment", "depuis quand", "jusqu’à quand",
    "pendant combien de temps", "en quelle année", "à quelle date",

    # Questions de mesure
    "à combien", "combien de temps", "combien de fois", "à quel point", "à quel tarif", "à quelle distance", "combien ça coûte",

    # Questions de manière / but
    "en quoi", "de quelle façon", "de quelle manière", "comment faire pour", "dans quel but", "dans quel contexte", "à quoi ça sert",

    # Questions spatiales
    "par où", "vers où", "où est-ce que", "où se trouve", "où peut-on",

    # Questions causales / explicatives
    "pourquoi est-ce que", "pourquoi", "dans quelle mesure",

    # Questions avec "qui"
    "qui est-ce que", "à qui", "avec qui", "pour qui", "chez qui", "contre qui",
    "de qui", "sans qui", "derrière qui", "devant qui", "par qui", "sur qui",
    "près de qui", "loin de qui", "qui", "c’est qui", "c’est à qui", "c’est de qui",

    # Questions avec "quoi"
    "à quoi", "avec quoi", "sans quoi", "dans quoi", "c’est quoi", "ça veut dire quoi", "ça sert à quoi", "de quoi s’agit-il",

    # Formes interrogatives avec verbe
    "peux-tu", "peux-vous", "pouvez-vous", "as-tu", "avez-vous", "sais-tu", "savez-vous",
    "connais-tu", "connaissez-vous", "veux-tu", "voulez-vous", "vas-tu", "allez-vous",
    "faut-il", "dois-tu", "doit-on", "devrait-on", "voudrais-tu", "voudriez-vous",

    # Questions directes ou indirectes
    "que faire", "que peut-on", "que devons-nous", "que dois-je", "quoi faire", "qu’est-ce qu’on peut faire",
    "savoir si", "je me demande si", "j’aimerais savoir", "je voudrais savoir", "voir si", "vérifier si",

    # Interrogatifs simples
    "comment", "quand", "où", "pourquoi", "combien", "quoi",
    "quel", "quelle", "quels", "quelles", "lequel", "laquelle", "lesquels", "lesquelles"
]


_pattern = re.compile(
    r'\b(?:' + '|'.join(re.escape(w) for w in QUESTION_WORDS) + r')\b',
    flags=re.IGNORECASE
)

def normalize(text: str) -> str:
    return unidecode(text).lower()

def find_question_words(sentence: str) -> list[str]:
    norm = normalize(sentence)
    return _pattern.findall(norm)

def contains_question_word(sentence: str) -> bool:
    return bool(find_question_words(sentence))

def classify_sentence(sentence):
    prompt = f"""
Vous êtes un assistant chargé d’analyser la phrase d’un utilisateur pour déterminer :
1. Si l’utilisateur a **déjà posé** sa question dans cette phrase (cas “posed”),  
2. Ou s’il a **seulement exprimé l’intention** de poser une question sans en donner le contenu (cas “intent_only”).
Phrase à classifier : {sentence}
Répondez uniquement par `posed` ou `intent_only`, en minuscules, sans ponctuation ni texte additionnel.
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
    return 'posed' in classification


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
        if contains_question_word(query) :
            logging.info("contains question words in the sentence")
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
