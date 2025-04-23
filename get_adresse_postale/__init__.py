import azure.functions as func
import logging
import numpy as np
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import re
import json
import urllib.request
import os
from typing import List, Dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

'''def load_ner_model():
    logger.info("Chargement du modèle NER...")
    tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
    model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
    return pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")

nlp = load_ner_model()

class InformationExtractor:
    def __init__(self , nlp_pipeline):
        self.nlp=nlp_pipeline
        logger.info("Modèle NER initialisé avec succès.")      
    def extraire_adresse(self, texte):
        logger.info(f"Extraction de l'adresse à partir du texte : {texte}")
        # Extraction du numéro de rue
        numero_rue = re.search(r'\b\d+\b', texte)
        adr = f"{numero_rue.group()} " if numero_rue else ""
        adr=''
        # Extraction des entités pertinentes
        entities = self.nlp(texte)
        for ent in entities:
            if ent['entity_group'] in {"LOC", "PER"}:
                adr += ent['word'] + ' '
        adr = adr.strip()
        if adr:
            logger.info(f"Adresse extraite : {adr}")
        else:
            logger.warning("Aucune adresse n'a été extraite.")
        return adr

extractor = InformationExtractor(nlp)
'''
class InformationExtractor:
    def __init__(self):
        logger.info("Modèle NER initialisé avec succès.")    
    def get_entities(self , texte):
        data = {"inputs": texte}
        body = str.encode(json.dumps(data))
        url = os.environ["HG_MODEL_ENDPOINT"]
        api_key = os.environ["HG_MODEL_ENDPOINT_KEY"]
        if not api_key:
            raise Exception("A key should be provided to invoke the endpoint")
        headers = {'Content-Type':'application/json', 'Accept': 'application/json', 'Authorization':('Bearer '+ api_key)}
        req = urllib.request.Request(url, body, headers)
        try:
            response = urllib.request.urlopen(req)
            result = response.read()
            decoded_str = result.decode('utf-8')
            ner_list = json.loads(decoded_str)
            logger.info(result)
            logger.info(ner_list)
            return ner_list
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))
            print(error.info())
            print(error.read().decode("utf8", 'ignore'))
            return []
    def extraire_adresse(self, texte):
        logger.info(f"Extraction de l'adresse à partir du texte : {texte}")
        numero_rue = re.search(r'\b\d+\b', texte)
        adr = f"{numero_rue.group()} " if numero_rue else ""
        # Extraction des entités pertinentes
        entities = self.get_entities(texte)
        logger.info(entities)
        entities= self.reconstruct_entities(entities)
        logger.info(entities)
        for ent in entities:
            if ent['entity_group'] in {"LOC", "PER"}:
                adr += ent['word'] + ' '
        adr = adr.strip()
        if adr:
            logger.info(f"Adresse extraite : {adr}")
        else:
            logger.warning("Aucune adresse n'a été extraite.")
        return adr
        
    def reconstruct_entities(self, ner_output):
        entities = []
        current_entity = {
            "entity": None,
            "score": [],
            "start": None,
            "end": None,
            "word": ""
        }
    
        for token in ner_output:
            if current_entity["entity"] != token["entity"]:
                if current_entity["entity"]:
                    entities.append({
                        "entity": current_entity["entity"],
                        "score": sum(current_entity["score"]) / len(current_entity["score"]),
                        "word": current_entity["word"].replace("▁", " ").strip(),
                        "start": current_entity["start"],
                        "end": current_entity["end"]
                    })
                # Start new entity
                current_entity = {
                    "entity": token["entity"],
                    "score": [token["score"]],
                    "start": token["start"],
                    "end": token["end"],
                    "word": token["word"]
                }
            else:
                current_entity["score"].append(token["score"])
                current_entity["end"] = token["end"]
                current_entity["word"] += token["word"]
    
        # Add last entity
        if current_entity["entity"]:
            entities.append({
                "entity": current_entity["entity"],
                "score": sum(current_entity["score"]) / len(current_entity["score"]),
                "word": current_entity["word"].replace("▁", " ").strip(),
                "start": current_entity["start"],
                "end": current_entity["end"]
            })
    
        return entities
        
extractor = InformationExtractor()
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

        result = extractor.extraire_adresse(query)

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
