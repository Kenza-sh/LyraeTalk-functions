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
    'comment', 'quand', 'où', 'pourquoi', 'qui', 'que', 'combien',
    'quel', 'quelle', 'quels', 'quelles','lequel', 'laquelle', 'lesquels',
    'lesquelles','est-ce que', 'est ce que',
    'à quelle heure', 'à quel moment', 'à combien',
    'en quoi', 'de quelle façon', 'de quelle manière',
    'à quel point', 'depuis quand', 'jusqu\'à quand',
    'à qui', 'avec qui', "à quel tarif","par où", "vers où","à quelle distance",
  "en quoi", "à quel point","pour quelle raison", "dans quel but",
"sous quelle condition", "dans quel contexte","jusqu'à quand",
"depuis combien de temps","pendant combien de temps", "en quelle année",
"où est-ce que", "quand est-ce que", "pourquoi est-ce que", "qui est-ce que",
 'à qui', 'avec qui', 'pour qui', 'chez qui', 'contre qui', 
'à quoi', 'avec quoi', 'sans quoi', 'dans quoi', 
    
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
    prompt = f"""Tu es un classifieur intelligent.
Je vais te donner une phrase en français.
Ta tâche est de déterminer si cette phrase est :
- une "question globale" : question vague, générale, générique, sans détail spécifique.
  Exemples : 
    - "Puis-je avoir des informations ?"
    - "Je voudrais me renseigner."
    - "Pouvez-vous me donner des renseignements ?"
    - "je veux obtenir des infos"

- ou une "question précise" : question spécifique avec un sujet, un détail ou une demande claire.
  Exemples :
    - "Je voudrais savoir le cout d'une cosultation"
    - "Je veux savoir les horaires d'ouverture de votre cabinet ?"
    - "Pouvez vous me dire les tarifs des examen d'echo"
    - "je veux obtenir des infos sur les différents sites du centre de radiologie"
Phrase : {sentence}
Réponds uniquement par "globale" ou "précise", sans ajouter aucun autre texte.
"""
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        temperature=0.5,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    classification = (response.choices[0].message.content).strip().lower()
    return 'globale' not in classification


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
