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

categories = [
    "renseignements",
    "prise de rendez-vous",
    "modification de rendez-vous",
    "annulation de rendez-vous",
    "consultation de rendez-vous"
]

def answer_query(text):
        custom_prompt_template = (f"""Voici une liste de catégories : {', '.join(categories)}.
                Classifiez la phrase suivante dans l'une de ces catégories : {text}
                Répondez uniquement par la catégorie la plus appropriée.""")
        try:
                completion = client.chat.completions.create(
                    model=llm_model,
                    messages=[
                        {"role": "system", "content": custom_prompt_template},
                        {"role": "user", "content": text}
                    ],
                    temperature =0.3,
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
