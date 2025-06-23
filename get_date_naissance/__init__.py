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
     self.jour_pattern = r"(\d{1,2})"
     self.mois_pattern = r"(janvier|février|mars|avril|mai|juin|juillet|août|" \
                           r"septembre|octobre|novembre|décembre|" \
                           r"janv\.?|févr\.?|avr\.?|juil\.?|sept\.?|oct\.?|nov\.?|déc\.?)"
     self.annee_pattern = r"(\d{2,4})"
     self.date_pattern = re.compile(rf"\b{self.jour_pattern}\b.*?{self.mois_pattern}\b.*?{self.annee_pattern}",re.IGNORECASE)
     self.MIN_DATE = datetime(1900, 1, 1)
     self.NUMBER_MAP = { "premier": 1, "un": 1, "1er": 1}
     self.MONTH_MAP = {
            "janvier": "01", "février": "02", "fevrier": "02", "mars": "03",
            "avril": "04", "mai": "05", "juin": "06", "juillet": "07",
            "août": "08", "aout": "08", "septembre": "09", "octobre": "10",
            "novembre": "11", "décembre": "12", "decembre": "12"
        }


  def normalize_text(self, text) -> str:
      if not isinstance(text, str):
          return ""
      text = text.lower()
      # Remplace les mots français représentant des nombres
      for word, num in self.NUMBER_MAP.items():
          text = re.sub(r'\b' + re.escape(word) + r'\b', str(num), text)
      # Supprime la ponctuation
      text = re.sub(r"[.,;:!?*#@'\"<>\[\](){}]+", " ", text)
      # Supprime les espaces multiples
      text = re.sub(r"\s+", " ", text).strip()
      return text

  def parse_date(self, text):
        dt = dateparser.parse(text, settings={'DATE_ORDER': 'DMY','PREFER_DATES_FROM': 'past','REQUIRE_PARTS': ['day', 'month', 'year']}, languages=['fr'])
        if not dt:
            return None
        if not (self.MIN_DATE <= dt <= datetime.today()):
            logger.warning(f"Date hors intervalle valide: {dt}")
            return None
        return dt

  def normalize_year(self ,year_str) -> str:
          year_str = year_str.zfill(2)
          if len(year_str) == 2:
              current_year = datetime.now().year
              pivot = current_year % 100
              century = current_year - pivot
              y = int(year_str)
              full = (century + y) if y <= pivot else (century - 100 + y)
              logger.debug(f"Normalized two-digit year {year_str} -> {full}")
              return str(full)
          return year_str

  def split_date_by_length(self, digits):
        l = len(digits)
        if l == 8:
            return digits[:2], digits[2:4], digits[4:]
        elif l == 7:
            return '0' + digits[0], digits[1:3], digits[3:]
        elif l == 6:
            return digits[:2], digits[2:4], digits[4:]
        elif l == 5:
            return '0' + digits[0], digits[1:3], digits[3:]
        else:
            return None, None, None  # Trop court ou trop long

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

  def extraire_date_naissance(self, texte):
       texte =self.normalize_text(texte)
       if (pattern_1 := re.search(r'\b(\d{1,2})(?:er)?\s+([a-zéûî\.-]+)\s+(\d{2,4})\b', texte, re.IGNORECASE)):
                jour, mois_str, annee = pattern_1.groups()
                mois = self.MONTH_MAP.get(mois_str.lower())
                if mois:
                    normalized = f"{jour.zfill(2)} {mois} {annee}"
                    logger.info(f"PATTERN_1: {normalized}")
                    dt = self.parse_date(normalized)
                    if dt:
                            return dt.strftime("%Y-%m-%d")
       elif (pattern_2 := re.search(r'\b(\d{1,2})[ /.-](\d{1,2})[ /.-](\d{2,4})\b', texte, re.IGNORECASE)):
                jour, mois, annee = pattern_2.groups()
                normalized = f"{jour.zfill(2)} {mois.zfill(2)} {annee}"
                logger.info(f"PATTERN_2: {normalized}")
                dt = self.parse_date(normalized)
                if dt:
                        return dt.strftime("%Y-%m-%d")

       elif  (pattern_3 := self.date_pattern.search(texte)):
                jour, mois, annee = pattern_3.group(1), pattern_3.group(2), pattern_3.group(3)
                normalized = f"{jour} {mois} {annee}"
                logger.info(f"PATTERN_3: {normalized}")
                dt = self.parse_date(normalized)
                if dt:
                        return dt.strftime("%Y-%m-%d")

       elif (pattern_4 := re.search(r"""\b(?P<mois>[a-zA-Zéèêëàâäîïôöûüç\.-]+)(?:[\s\./,\-]*\w+)*?[\s\./,\-]*(?P<jour>\d{1,2})(?:er)?(?:[\s\./,\-]*\w+)*?[\s\./,\-]*(?P<annee>\d{2,4})\b""", texte, re.IGNORECASE)):
                  jour = pattern_4.group("jour")
                  mois = pattern_4.group("mois")
                  annee = pattern_4.group("annee")
                  normalized=f"{jour}/{mois}/{annee}"
                  logger.info(f"PATTERN_4: {normalized}")
                  dt = self.parse_date(normalized)
                  if dt:
                        return dt.strftime("%Y-%m-%d")

       elif  (matches := re.findall(r'\b[\d ]{5,10}\b', texte)):
            for match in matches:
                digits = re.sub(r'\D', '', match)  # Supprime espaces, tirets, etc.
                if 5 <= len(digits) <= 8:
                    jour, mois, annee = self.split_date_by_length(digits)
                    if not all([jour, mois, annee]):
                        continue
                    jour = jour.zfill(2)
                    mois = mois.zfill(2)
                    annee = str(self.normalize_year(annee))
                    normalized=f"{jour}/{mois}/{annee}"
                    logger.info(f"PATTERN_5: {normalized}")
                    dt = self.parse_date(normalized)
                    if dt:
                        return dt.strftime("%Y-%m-%d")

       elif  (dt := self.parse_date(texte)):
              logger.info(f"PATTERN_6: {dt}")
              return dt.strftime("%Y-%m-%d")

       elif (entities := self.reconstruct_entities(self.get_entities(texte))):
          date_parts = [ent['word'] for ent in entities if ent['entity'] == "I-DATE"]
          if date_parts:
              date_str = " ".join(date_parts)
              logger.info(f"PATTERN_7 : Date détectée à partir des entités : {date_str}")
              dt = self.parse_date(f"{jour}/{mois}/{annee}")
              if dt:
                  return dt.strftime("%Y-%m-%d")

       else :
           logger.info(f"AUCUNE DATE EXTRAITE : {texte}")
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
