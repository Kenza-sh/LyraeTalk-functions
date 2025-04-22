import azure.functions as func
import logging
import numpy as np
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import re
import json
from datetime import datetime, timedelta
import dateparser

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def load_ner_model():
    logger.info("Chargement du modèle NER...")
    tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
    model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
    return pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")

nlp = load_ner_model()

class InformationExtractor:
    def __init__(self , nlp_pipeline):
        self.nlp=nlp_pipeline
        logger.info("Modèle NER initialisé avec succès.")
    def extraire_date_naissance(self, texte):
        logger.info(f"Extraction de la date de naissance à partir du texte : {texte}")
        entities = self.nlp(texte)
        for ent in entities:
            if ent['entity_group'] == "DATE":
                date_str = ent['word']
                date_obj = dateparser.parse(date_str)
                if date_obj:
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    logger.info(f"Date de naissance extraite : {formatted_date}")
                    return formatted_date
                else:
                    logger.warning(f"Date non valide extraites : {date_str}")
                    return date_str
        logger.warning("Aucune date de naissance n'a été extraite.")
        return None
      
extractor = InformationExtractor(nlp)

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

        result = extractor.extraire_date_naissance(query)

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
