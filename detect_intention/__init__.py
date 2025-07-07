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
llm_model="gpt-4o-mini"

categories = [
    "renseignements",
    "prise de rendez-vous",
    "modification de rendez-vous",
    "annulation de rendez-vous",
    "consultation de rendez-vous",
    "Autre",
]

def answer_query(text):
        custom_prompt_template = (f"""Vous êtes un assistant pour un centre de radiologie.
Voici la liste des catégories possibles : {', '.join(categories)}.

1. **renseignements** : demande d'information générale ou spécifique sur les examens (ex : tarifs, préparation, durée, modalités, type d’appareil, indications médicales, documents à apporter, etc.).

2. **prise de rendez-vous** : demande explicite pour **obtenir un rendez-vous** pour un ou plusieurs examens d’imagerie.

3. **modification de rendez-vous** : demande de **changement de date, d’heure ou de type d’examen** pour un rendez-vous déjà existant.

4. **annulation de rendez-vous** : demande d’**annuler un rendez-vous** programmé, sans souhait immédiat de le reprogrammer.

5. **consultation de rendez-vous** : demande d’**obtenir les détails d’un rendez-vous existant** (date, heure, lieu, type d’examen, nom du praticien, etc.).

6. **Autre** : tout message **hors sujet radiologique** ou sans lien clair avec la gestion des rendez-vous .

Votre tâche :
- Analysez la phrase suivante : "{text}"
- Classez-la dans la catégorie la plus appropriée de la liste.
- Si la phrase n'est pas liée à la radiologie médicale, répondez uniquement : "Autre".
- Répondez uniquement par le nom de la catégorie, sans ajouter d'explication.
""")
        try:
                completion = client.chat.completions.create(
                    model=llm_model,
                    messages=[
                        {"role": "system", "content": custom_prompt_template},
                        {"role": "user", "content": text}
                    ],
                    temperature =0,
                     max_tokens=10
                )
                return completion.choices[0].message.content
        except Exception as e:
            logging.error(f"Error answering query: {e}")
            return "Une erreur est survenue lors de la réponse."


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

        result = answer_query(query)

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
