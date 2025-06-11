import azure.functions as func
import logging
import re
import json
from datetime import datetime, timedelta
import dateparser
import urllib.request
import os
from typing import List, Dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class InformationExtractor:
    def __init__(self ):
        logger.info("Modèle NER initialisé avec succès.")
        self.NUMBER_MAP = { "premier": 1, "un": 1, "1er": 1, "deuxième": 2, "deux": 2, "2e": 2}   
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
    
    def replace_numbers_in_string(self, sentence):
        for word, num in self.NUMBER_MAP.items():
            sentence = re.sub(r'\b' + re.escape(word) + r'\b', str(num), sentence)
        return sentence.lower()

    def is_future_date(self, birth_date):
        today = datetime.today()
        min_date = datetime(1900, 1, 1)
        return birth_date > today or birth_date < min_date
    
                 
    def extraire_date_naissance(self, texte):
        logger.info(f"Extraction de la date de naissance à partir du texte : {texte}")
        texte = self.replace_numbers_in_string(texte)
        # Premier essai avec dateparser
        date_obj = dateparser.parse(texte, settings={'DATE_ORDER': 'DMY'})
        if date_obj:
            if self.is_future_date(date_obj):
                logger.warning(f"Date non valide (date dans le futur) : {texte}")
                return texte
            else:
                formatted_date = date_obj.strftime("%Y-%m-%d")
                return formatted_date
        # Si dateparser ne trouve rien, on tente avec regex
        jour_pattern = r"(\d{1,2})"
        mois_pattern = r"(janvier|février|mars|avril|mai|juin|juillet|août|" \
                       r"septembre|octobre|novembre|décembre|" \
                       r"janv\.?|févr\.?|avr\.?|juil\.?|sept\.?|oct\.?|nov\.?|déc\.?)"
        annee_pattern = r"(\d{4})"
        full_pattern = re.compile(rf"\b{jour_pattern}\s+{mois_pattern}\b.*?{annee_pattern}", re.IGNORECASE)
        match = full_pattern.search(texte)
        if match:
            jour, mois, annee = match.group(1), match.group(2), match.group(3)
            la_date = f"le {jour} {mois} {annee}"
            date_obj = dateparser.parse(la_date, settings={'DATE_ORDER': 'DMY'}, languages=['fr'])
            if date_obj:
                if self.is_future_date(date_obj):
                    logger.warning(f"Date non valide (date dans le futur) : {la_date}")
                    return texte
                else:
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    return formatted_date
        # Si toujours rien, on essaie d'extraire via les entités
        entities = self.get_entities(texte)
        entities = self.reconstruct_entities(entities)
        for ent in entities:
            if ent['entity'] == "I-DATE":
                date_str = ent['word']
                logger.info(f"Entité date détectée : {date_str}")
                date_obj = dateparser.parse(date_str, settings={'DATE_ORDER': 'DMY'}, languages=['fr'])
                if date_obj:
                    if self.is_future_date(date_obj):
                        logger.warning(f"Date non valide (date dans le futur) : {date_str}")
                        return date_str
                    else:
                        formatted_date = date_obj.strftime("%Y-%m-%d")
                        logger.info(f"Date de naissance extraite : {formatted_date}")
                        return formatted_date
                else:
                    logger.warning(f"Date non valide extraite : {date_str}")
                    return date_str
        logger.warning("Aucune date de naissance n'a été extraite.")
        return None
               
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
