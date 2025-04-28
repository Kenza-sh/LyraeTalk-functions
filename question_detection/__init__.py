from openai import AzureOpenAI
import azure.functions as func
import logging
import json
import os

client = AzureOpenAI(
          azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"],
          api_key= os.environ["AZURE_OPENAI_API_KEY"],
          api_version="2024-05-01-preview"
        )
llm_model="gpt-35-turbo"

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
    - "Quels sont vos horaires d'ouverture ?"
    - "Combien coûte un examen de radiologie "
    - "À quelle heure êtes-vous disponibles pour un rendez-vous ?"
Phrase : {sentence}
Réponds uniquement par "globale" ou "précise", sans ajouter aucun autre texte.
"""
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        temperature=0,
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
