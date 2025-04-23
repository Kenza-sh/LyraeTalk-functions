import re
import logging
import dateparser
from datetime import datetime, timedelta
from babel.dates import format_date
import calendar
import azure.functions as func
import json
import urllib.request
import os
from typing import List, Dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CreneauExtractor:
    def __init__(self):
        self.french_number_mapping = { "premier": "1", "un": "1", "deux": "2", "trois": "3", "quatre": "4", "cinq": "5",
            "six": "6", "sept": "7", "huit": "8", "neuf": "9", "dix": "10", "onze": "11", "douze": "12", "treize": "13", "quatorze": "14",
            "quinze": "15", "seize": "16", "dix-sept": "17", "dix-huit": "18", "dix-neuf": "19", "vingt": "20", "vingt-et-un": "21",
            "vingt-deux": "22", "vingt-trois": "23", "trente": "30", "trente-et-un": "31", 'minuit': '00h', 'midi': '12h',
            'matin': '9h', 'après-midi': '14h', 'soir': '18h', 'soirée': '18h','deux heures': '2h', 'trois heures': '3h', 'quatre heures': '4h',
            'cinq heures': '5h', 'six heures': '6h', 'sept heures': '7h', 'huit heures': '8h',
            'neuf heures': '9h', 'dix heures': '10h', 'onze heures': '11h', 'douze heures': '12h',
            'treize heures': '13h', 'quatorze heures': '14h', 'quinze heures': '15h',
            'seize heures': '16h', 'dix-sept heures': '17h', 'dix-huit heures': '18h',
            'dix-neuf heures': '19h', 'vingt heures': '20h', 'vingt et une heures': '21h',
            'vingt-deux heures': '22h', 'vingt-trois heures': '23h',}
        self.weekdays_mapping = {"lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3, "vendredi": 4, "samedi": 5, "dimanche": 6}
        self.relative_dates = {"aujourd'hui": 0,"après-demain": 2,"après demain": 2 ,"apres demain": 2,"demain": 1,  "dans deux jours": 2, "dans trois jours": 3,
            "dans une semaine": 7, "dans deux semaines": 14, "dans trois semaines": 21, "dans un mois": 30, "dans deux mois": 60, "dans trois mois": 90,
            "dans six mois": 180, "dans un an": 365, "dans deux ans": 730, "dans trois ans": 1095,'semaine prochaine':7,'fin du mois' :'30',"mois prochain": 30,
           }
    
    def get_next_weekday(self, target_weekday):
        """Retourne la date du prochain jour donné (0 = Lundi, 6 = Dimanche)."""
        today = datetime.now()
        days_ahead = (target_weekday - today.weekday()) % 7
        return today + timedelta(days=days_ahead if days_ahead else 7)
    
    def convert_french_numbers_to_digits(self, text):
        """Remplace les nombres français par leurs équivalents numériques et normalise les heures."""
        logger.debug(f'Conversion des nombres français dans le texte: "{text}"')
        pattern = re.compile(r'\b(' + '|'.join(re.escape(word) for word in self.french_number_mapping.keys()) + r')\b', re.IGNORECASE)
        text = pattern.sub(lambda match: self.french_number_mapping[match.group(0).lower()], text)
        text = re.sub(r'(\d{1,2})h(?!\d)', r'\1h00', text)  # Normalisation des heures
        return text
    
    def get_end_of_current_month(self):
        """Retourne la date du dernier jour du mois courant."""
        today = datetime.now()
        # Obtenez le dernier jour du mois actuel
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_of_month = today.replace(day=last_day)
        return end_of_month

    def get_first_day_of_next_month(self):
        """Retourne la date du premier jour du mois suivant."""
        today = datetime.now()
        # Ajoutez un mois et réinitialisez le jour à 1
        next_month = today.replace(month=(today.month % 12) + 1, day=1)
        return next_month

    def update_choix_patient(self, choix_patient):
        now = datetime.now()
        # Gestion spécifique du "1er du mois prochain"
        if "1er du mois prochain" in choix_patient:
            target_date = self.get_first_day_of_next_month()
            formatted_date = format_date(target_date, format="d MMMM yyyy", locale="fr")
            choix_patient = choix_patient.replace("1er du mois prochain", f"le {formatted_date}")

        if "1er du mois" in choix_patient:
            target_date = self.get_first_day_of_next_month()
            formatted_date = format_date(target_date, format="d MMMM yyyy", locale="fr")
            choix_patient = choix_patient.replace("1er du mois", f"le {formatted_date}")
        
        # Gestion spécifique du "fin du mois"
        if "fin du mois" in choix_patient:
            target_date = self.get_end_of_current_month()
            formatted_date = format_date(target_date, format="d MMMM yyyy", locale="fr")
            choix_patient = choix_patient.replace("fin du mois", f"le {formatted_date}")

        for key, days in self.relative_dates.items():
            if key in choix_patient:
                target_date = datetime.now() + timedelta(days=int(days))
                formatted_date = format_date(target_date, format="d MMMM yyyy", locale="fr")
                choix_patient = choix_patient.replace(key, f"le {formatted_date}")
        
        # Gestion des jours de la semaine
        for jour, index in self.weekdays_mapping.items():
            if f"{jour} prochain" in choix_patient:
                target_date = self.get_next_weekday(index)
                formatted_date = format_date(target_date, format="d MMMM yyyy", locale="fr")
                choix_patient = choix_patient.replace(f"{jour} prochain", f"le {formatted_date}")
        return choix_patient

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
        
    def get_creneau(self, choix_patient):
        """Analyse le texte pour extraire une date et une heure."""
        logger.info(f"Traitement de l'entrée: {choix_patient}")
        choix_patient = choix_patient.lower()
        choix_patient=self.convert_french_numbers_to_digits(choix_patient)
        choix_patient = re.sub(r'[^\w\s]', ' ', choix_patient)
        choix_patient = re.sub(r'\s+', ' ', choix_patient)
        choix_patient =self.update_choix_patient(choix_patient)
        entities = self.get_entities(texte)
        logger.info(entities)
        entities= self.reconstruct_entities(entities)
        creneau_parts = [str(ent['word']) for ent in entities if ent['entity'] in ("I-DATE", "I-TIME")]
        if not creneau_parts:
            logger.warning('Aucune entité DATE ou TIME détectée.')
            return None
        
        # Combinaison des informations extraites
        creneau_choisi = ' '.join(creneau_parts)
        if 'prochain' in creneau_choisi or 'prochaine' in creneau_choisi:
            creneau_choisi = creneau_choisi.replace('prochain', '').replace('prochaine', '')
        date_obj = dateparser.parse(creneau_choisi, languages=['fr'])
        if date_obj:
            now = datetime.now()
            if date_obj.year == now.year and date_obj < now:
                date_obj = date_obj.replace(year=now.year + 1)
                if date_obj.hour == 0 and date_obj.minute == 0:
                    date_obj = date_obj.replace(hour=9, minute=0)
            return date_obj.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            logger.warning(f"Échec de l'analyse de la date: {creneau_choisi}")
            return None
            
extractor=CreneauExtractor()

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
        
        result = extractor.get_creneau(query)

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
