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
        self.MONTH_MAP = {
            "janvier": "01", "février": "02", "fevrier": "02", "mars": "03",
            "avril": "04", "mai": "05", "juin": "06", "juillet": "07",
            "août": "08", "aout": "08", "septembre": "09", "octobre": "10",
            "novembre": "11", "décembre": "12", "decembre": "12"
        }

        
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
    
    def remplacer_mois(self ,text):
        for mois, num in self.MONTH_MAP.items():
            pattern = r'\b' + re.escape(mois) + r'\b'
            text = re.sub(pattern, num, text, flags=re.IGNORECASE)
        return text
        
    def normalize_year(self , annee) :
            if len(annee) == 4:
                return annee
            current_year = datetime.now().year
            pivot = current_year % 100
            century = current_year - pivot
            annee_int = int(annee)
            if annee_int > pivot:
                year_full = century - 100 + annee_int  # siècle précédent
            else:
                year_full = century + annee_int        # siècle actuel
            logger.info(f"Année courte {annee} normalisée en {year_full}")
            return str(year_full)   
        
    def extraire_date_naissance(self, texte):
        logger.info(f"Extraction de la date de naissance à partir du texte : {texte}")
        texte=self.replace_numbers_in_string(texte)
        textual_date_match = re.search(r'\b(\d{1,2})(?:er)?\s+([a-zéûî\.-]+)\s+(\d{2,4})\b', texte, re.IGNORECASE)
        if textual_date_match:
            jour, mois_str, annee = textual_date_match.groups() 
            mois = self.MONTH_MAP.get(mois_str.lower())
            if mois:
                annee = self.normalize_year(annee)
                normalized = f"{jour.zfill(2)} {mois} {annee}"
                logger.info(f"Date textuelle détectée et normalisée 1 : {normalized}")
                texte = texte.replace(textual_date_match.group(0), normalized)
                logger.info(f"Texte après normalization: {texte}")
        else :
            short_date_match = re.search(r'\b(\d{1,2})[ /.-](\d{1,2})[ /.-](\d{2,4})\b', texte)
            logger.info(f"short_date_match : {short_date_match}")
            if short_date_match:
                    jour, mois, annee = short_date_match.groups()
                    annee = self.normalize_year(annee)
                    logger.info(f"annee est est : {annee}")
                    normalized = f"{jour.zfill(2)} {mois.zfill(2)} {annee}"
                    logger.info(f"Date courte détectée et normalisée  {normalized}")
                    texte = texte.replace(short_date_match.group(0), normalized)
                    logger.info(f"Texte après normalization : {texte}")
            else:
                texte_temp =self.remplacer_mois(texte)
                short_date_match_temp = re.search(r'\b(\d{1,2})\D+(\d{1,2})\D+(\d{2,4})\b', texte_temp)
                logger.info(f"short_date_match : {short_date_match_temp}")
                if short_date_match_temp:
                    jour, mois, annee = short_date_match_temp.groups()
                    annee_d = self.normalize_year(annee)
                    logger.info(f"annee est est : {annee_d}")
                    texte = re.sub(r'\b' + re.escape(annee) + r'\b', annee_d, texte)
                    logger.info(f"Date courte détectée et partiellement normalisée : {texte}") 
                else :
                    return texte
                
        entities = self.get_entities(texte)
        entities= self.reconstruct_entities(entities)
        for ent in entities:
            if ent['entity'] == "I-DATE":
                date_str = ent['word']
                logger.info(f"entities a retourné : {date_str}")
                date_obj = dateparser.parse(date_str, settings={'DATE_ORDER': 'DMY'},languages=['fr'])
                if date_obj:
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    logger.info(f"Date de naissance extraite : {formatted_date}")
                    if self.is_future_date(date_obj):
                        logger.warning(f"Date non valide (date dans le futur) : {date_str}")
                        return date_str
                    return formatted_date
                else:
                    logger.warning(f"Date non valide extraites : {date_str}")
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
