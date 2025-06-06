import azure.functions as func
import logging
import re
import json
import urllib.request
import os
from typing import List, Dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class InformationExtractor:
    def __init__(self ):
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
            logger.info("The request failed with status code: " + str(error.code))
            logger.info(error.info())
            logger.info(error.read().decode("utf8", 'ignore'))
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
        
    def check_noun(self, msg_2_check):
        logger.debug(f"Vérification du nom : {msg_2_check}")
        def check_str(msg_2_check: str) -> bool:
            return isinstance(msg_2_check, str) and bool(msg_2_check.strip()) and any(ele in msg_2_check for ele in ["a", "e", "i", "o", "u", "y"])
        if not check_str(msg_2_check):
            logger.warning(f"Le message {msg_2_check} n'est pas une chaîne valide.")
            return False
        if not re.match(r"^[A-Za-zÀ-ÿ]+(?:[-'\s][A-Za-zÀ-ÿ]+)*$", msg_2_check):
            logger.warning(f"Le message {msg_2_check} contient des caractères invalides.")
            return False
        return True
        
    def detecter_lettres_uniques1(self , phrase):
        pattern =  r'\b([a-zA-ZÀ-ÿ])\b'
        phrase_sans_ponctuation = re.sub(r"[^\w\s-]", '', phrase)
        lettres = re.findall(pattern, phrase_sans_ponctuation)
        if not lettres :
                return phrase
        return ''.join(lettres)

    def repeat_match(self , m):
        count = int(m.group(1))
        char = m.group(2)
        return char * count
        
    def detecter_lettres_uniques( self , phrase):
        logger.info(f"Phrase initiale : {phrase}")
        phrase =phrase.lower().strip()
        phrase_sans_ponctuation = re.sub(r"[.,;:!?*#@]+", '', phrase)
        phrase_sans_ponctuation = re.sub(r"[\"'<>{}\[\]()]", '', phrase_sans_ponctuation)
        replacements = { r"\btiret\b": "-", r"\bapostrophe\b": "'",r"\bespace\b": "§",}
        for pattern, symbol in replacements.items():
            phrase_sans_ponctuation = re.sub(pattern, symbol, phrase_sans_ponctuation, flags=re.IGNORECASE)
        logger.info(f"Phrase après remplacements spéciaux : {phrase_sans_ponctuation}")
        phrase_sans_ponctuation = re.sub(r'\s*(\d+)\s*([a-zA-Z*#@&/\-_+=.,!?\'"])', self.repeat_match, phrase_sans_ponctuation)
        phrase_sans_ponctuation = re.sub(r'\s+', ' ', phrase_sans_ponctuation).strip()
        logger.info(f"Phrase après traitement des chiffres suivis de lettres : {phrase_sans_ponctuation}")
        phrase_sans_ponctuation = re.sub(r"\s*([\-'§])\s*", r'\1', phrase_sans_ponctuation)
        logger.info(f"Phrase après suppression des espaces autour des séparateurs : {phrase_sans_ponctuation}")
        if '§' in phrase_sans_ponctuation:
                phrase_sans_ponctuation=re.sub(r'§', ' ', phrase_sans_ponctuation)
        logger.info(f"Résultat final : {phrase_sans_ponctuation}")
        return phrase_sans_ponctuation
        
    def extraire_nom(self, texte):
        logger.info(f"Extraction du nom à partir du texte : {texte}")
        nom=self.detecter_lettres_uniques(texte)
        if nom :
            texte = f"Mon nom de famille est {nom} "
        entities = self.get_entities(texte)
        logger.info(entities)
        entities= self.reconstruct_entities(entities)
        for ent in entities:
            if ent['entity'] == "I-PER":
                if self.check_noun(ent['word'].lower()):
                    logger.info(f"Nom extrait : {ent['word'].upper()}")
                    return ent['word'].upper()
        logger.warning("Aucun nom n'a été extrait.")
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

        result = extractor.extraire_nom(query)

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
