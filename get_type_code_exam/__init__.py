import azure.functions as func
import requests
import json
import logging
import os
from openai import AzureOpenAI
import re
import logging
import unicodedata

client = AzureOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version="2024-05-01-preview"
        )
class ExamenFetcher:
    def __init__(self):
        self.url = "https://sandbox.xplore.fr:20443/XaPriseRvGateway/Application/api/External/GetListeExamensFromTypeExamen"
        self.headers = {'Content-Type': 'application/json'}
        self.ids_base = {'CT', 'US', 'MR', 'MG', 'RX'}
        self.llm_model = "gpt-35-turbo"
        self.replacements = {
                r'acromioclaviculaire': "ACROMIOCLAVICULAIRE (RADIOGRAPHIE DE L'ARTICULATION ACROMIO-CLAVICULAIRE)",
                r'pangonogramme': "PANGONOGRAMME (RADIOGRAPHIE DES DENTS)",
                r'asp': "ASP (RADIOGRAPHIE DE L'ABDOMEN SANS PRÉPARATION)",
                r'urocanner': "UROSCANNER (SCANNER DES REINS)",
                r'arm': "ARM (IRM DES VAISSEAUX SANGUINS)",
                r'bili[- ]?irm': "BILI IRM (IRM DES VOIES BILIAIRES)",
                r'entero[- ]?irm': "ENTERO IRM (IRM DE L'INTESTIN)",
                r'entéro[- ]?irm': "ENTERO IRM (IRM DE L'INTESTIN)",
                r'angio[- ]?irm': "ANGIO IRM (IRM ANGIOGRAPHIQUE DES VAISEAUX SANGUINS)",
                r'uro[- ]?scanner': "UROSCANNER (SCANNER DES VOIES URINAIRES)",
                r'dacryoscanner': "DACRYOSCANNER (SCANNER DES VOIES LACRYMALES)",
                r'coroscanner': "COROSCANNER (SCANNER DES ARTÈRES DU CŒUR)",
                r'entéroscanner': "ENTEROSCANNER (SCANNER DE L'INTESTIN)",
                r'coloscanner': "COLOSCANNER (SCANNER DU COLON)",
                r'arthro[- ]?scanner': "ARTHRO-SCANNER (SCANNER DES ARTICULATIONS)",
                r'arthro[- ]?irm': "ARTHRO-IRM (IRM DES ARTICULATIONS)",
                r'ostéodensitométrie': "OSTÉODENSITOMÉTRIE (RADIOGRAPHIE DES OS)",
                r'cystographie': "CYSTOGRAPHIE (RADIOGRAPHIE DE LA VESSIE)",
                r'discographie': "DISCOGRAPHIE (RADIOGRAPHIE DU DISQUE INTERVERTÉBRAL)",
                r'togd': "TOGD (RADIOGRAPHIE DE L'ŒSOPHAGE ET DE L'ESTOMAC)",
                r'urographie': "UROGRAPHIE (RADIOGRAPHIE DES VOIES URINAIRES)",
                r'hystérographie': "HYSTÉROGRAPHIE (RADIOGRAPHIE DE LA CAVITÉ UTÉRINE)",
                r'hystérosalpingographie': "HYSTÉROSALPINGOGRAPHIE (RADIOGRAPHIE DE LA CAVITÉ UTÉRINE)",
                r'cone[- ]?beam': "CONE BEAM (RADIOGRAPHIE DES DENTS)",
                r'tomographie': "TOMOGRAPHIE (RADIOGRAPHIE DES DENTS)",
                r'doppler': "DOPPLER (ÉCHOGRAPHIE DES VAISSEAUX)",               
                r'ct' :"scanner",
                r'echodoppler': "ECHODOPPLER (ÉCHOGRAPHIE DOPPLER)",
                r'echocardiographie': "ECHOCARDIOGRAPHIE (ÉCHOGRAPHIE DU CŒUR)",
                r'cerebro[- ]?scanner': "CEREBROSCANNER (SCANNER DU CERVEAU)",
                r'echographie[- ]?endor[ée]?ctale': "ÉCHOGRAPHIE ENDORÉCTALE (ÉCHOGRAPHIE DU RECTUM)",
                r'echographie[- ]?endovaginale': "ÉCHOGRAPHIE ENDOVAGINALE (ÉCHOGRAPHIE DU VAGIN ET DE L'UTÉRUS)",
                r'hystérosalpingographie': "HYSTÉROSALPINGOGRAPHIE (RADIOGRAPHIE DE L'APPAREIL GÉNITAL INTERNE DE LA FEMME)",
                r'ostéodensitométrie': "OSTÉODENSITOMÉTRIE (RADIOGRAPHIE DES OS)",
                r'uroscanner': "Uroscanner (scanner de l'appareil urinaire)",
                r'arthroscanner':"Arthroscanner (scanner des articulations)",
                r'etf' :"Échographie transfontanellaire encéphale (ETF)",
                r'tap': "SCANNER THORACO-ABDOMINO-PELVIEN (TAP)",
                r"eos": "Radiographie corps entier en station debout (système EOS)",
                r"tdm": "Tomodensitométrie (scanner)",
                r"tsa": "Scanner thoracique (avec ou sans angioscanner) TSA",
                r"angio[- ]?tsa": "Angio-scanner des troncs supra-aortiques (Angio-TSA)",
                r"télécr[aâ]ne": "Radiographie du crâne à distance (profil/face) télécrane",
                r"angio[- ]?tdm": "Angio-scanner (scanner vasculaire)",
                r"whole[- ]?body[- ]?mri": "IRM corps entier (Whole Body MRI)",
                r"uro[- ]?irm": "IRM des voies urinaires (URO-IRM)",
               r"dépistage" :"détection précoce",
               r"uroirm" :"IRM des voies urinaires (URO-IRM)",
               "uroscan" :"Uroscanner (scanner de l'appareil urinaire)",
               r'dacryoscan': "DACRYOSCANNER (SCANNER DES VOIES LACRYMALES)",
                r'coroscan': "COROSCANNER (SCANNER DES ARTÈRES DU CŒUR)",
                r'entéroscan': "ENTEROSCANNER (SCANNER DE L'INTESTIN)",
                r'coloscan': "COLOSCANNER (SCANNER DU COLON)",
                    
            
        }

        self.keywords = {
            "RADIO": ["radio", "radiographie","téléradiographie","teleradiographie",'radiologie',"radioscopie","radiologique"],
            "SCANNER": ["scanner", "tdm", "tomodensitométrie", "scan","angioscanner","angio-scanner","anteroscanner" ,"enteroscanner"],
            "IRM": ["irm", "imagerie par résonance magnétique",'rmn','mri',"uro-irm","uroirm"],
            "ECHOGRAPHIE": ["echo", "écho", "échographie","échographique","echographique","echographie", "échotomographie",'eco','éco'],
            "MAMMOGRAPHIE": ["mammographie","mammographique", "mammogramme", "mammo", "mamographie","mamo", "sein", "mammaire"],
            'IMAGERIE':['imagerie']
        }
    def process_text(self , texte):
        titre_normalise = texte.lower()
        for pattern, replacement in self.replacements.items():
            titre_normalise = re.sub(pattern, replacement, titre_normalise, flags=re.IGNORECASE)
        logging.warning(f"Texte aprés processing {titre_normalise}")
        return titre_normalise
                
    def normalize_to_compare(self , text):
            if text :
                        text = text.replace("’", "'").replace("‘", "'").replace("‛", "'")
                        text = text.replace("“", '"').replace("”", '"')
                        text = text.lower()
                        text = unicodedata.normalize('NFD', text)
                        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
                        text = re.sub(r"[,:.!?]", "", text)
                        text = re.sub(r"\s+", " ", text).strip()
            return text
                
    def normalize_examen(self , text):
                if not isinstance(text, str):
                        return text
                patterns = { r"\bMammographie\s+(Unilatérale|Dépistage|Bilatérale)\b": "Mammographie",
                    r"\bRadio\s+Poignet\b": "Radiographie du poignet",
                    r"\bRadio\s+Rachis\s+Lombaire\b": "Radiographie du rachis lombaire",
                    r"\bRadio\s+Genou\b": "Radiographie du genou",
                    r"\bRadio\s+Membre\s+Inférieur\b": "Radiographie de la jambe",
                    r"\bRadio\s+Membre\s+Supérieur\b": "Radiographie du bras",
                    r"\bIRM\s+Cheville\b": "IRM de la cheville",
                    r"\bIRM\s+Genou\b": "IRM du genou",
                    r"\bIRM\s+Bras\b": "IRM du Bras",
                    r"\bIRM\s+Bassin\b": "IRM du Bassin",
                    r"\bRadio\b": "Radiographie",
                    
                   }
                normalized = text
                for pat, repl in patterns.items():
                    normalized = re.sub(pat, repl, normalized, flags=re.IGNORECASE)
                return normalized
                
    def get_type_examen(self, texte):
                if not texte or not texte.strip():
                    logging.warning("Texte vide ou invalide fourni à get_type_examen")
                    return "AUTRE"
                texte = texte.lower()
                texte = texte.replace("’", "'")  # Apostrophe typographique
                texte = unicodedata.normalize("NFKD", texte)  # Supprime accents
                texte = ''.join(c for c in texte if not unicodedata.combining(c))
                mots = re.findall(r"\b\w+\b", texte)
                for category, words in self.keywords.items():
                    cleaned_words = [
                        ''.join(c for c in unicodedata.normalize("NFKD", w.lower()) if not unicodedata.combining(c))
                        for w in words
                    ]
                    if any(word in mots for word in cleaned_words):
                        logging.info(f"Type d'examen identifié: {category}")
                        return category
            
                logging.info("Aucun type d'examen trouvé, retour par défaut: AUTRE")
                return "AUTRE"

                
    def fetch_examens(self, ids=None):
        if ids is None:
            ids = self.ids_base
        else:
            ids = {id.upper() for id in ids if id.upper() in self.ids_base}
        data = {}
        with requests.Session() as session:
            session.headers.update(self.headers)
            for id in ids:
                try:
                    payload = json.dumps({"id": id})
                    response = session.post(self.url, data=payload, timeout=10)
                    
                    if response.status_code == 200:
                        actes = response.json().get('data', [])
                        data = {acte['code']: acte['libelle'] for acte in actes}
                        logging.info(f"Données récupérées pour ID {id}: {data}")
                    else:
                        logging.info(f"Erreur {response.status_code} pour l'ID {id}")
                except requests.RequestException as e:
                    logging.info(f"Erreur lors de la requête pour {id}: {e}")
        return data
                
    def get_class(self, text, data):
        custom_prompt_template = (
            f"Voici la liste des examens médicaux proposés par notre centre d'imagerie médicale : {', '.join(data.values())}. \n"
            f"Analyse la phrase suivante exprimée par un patient et identifie l'examen le plus adapté à son besoin. "
            f"Répondez uniquement par le 'nom exact et complet' de l'examen correspondant , tel qu'il figure dans la liste ci-dessus."
            f"Si aucun ne convient répondre par 'None' "
        )
        try:
            completion = client.chat.completions.create(
                model=self.llm_model,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": custom_prompt_template},
                    {"role": "user", "content": text}
                ],
            )
            logging.info(f"Réponse du modèle : {completion.choices[0].message.content}")
            res = (completion.choices[0].message.content)
            if res :
                 res = (re.sub(r"[,:.!?]", "", res)).strip()
            return res
        except Exception as e:
            logging.error(f"Error answering query: {e}")
            return ''
    def equiv(self, a, b):
         return self.normalize_to_compare(a) == self.normalize_to_compare(b)
                
    def lyae_talk_exam(self, texte):
      exam_types = {
          "RADIO": "RX",
          "SCANNER": "CT",
          "IRM": "MR",
          "ECHOGRAPHIE": "US",
          "MAMMOGRAPHIE": "MG",
          'AUTRE' :None
      }
      texte=self.process_text(texte)
      type_exam = self.get_type_examen(texte)
      id = exam_types.get(type_exam)
      if not id:
          logging.warning("Aucun ID correspondant trouvé")
          return None, None , None , None
      
      actes = self.fetch_examens([id])
      code_exam = self.get_class(texte, actes)
      code_exam_id = next((k for k, v in actes.items() if self.equiv(v, code_exam )), None)
      if code_exam=='None':
         code_exam= None
      else :
          code_exam = self.normalize_examen(str(code_exam))
      if id=="MG" and code_exam_id is None :
                  code_exam ="Mammographie Bilatérale"
                  code_exam_id = "N01MGBIL"
      logging.info(f"Résultat final: Type {type_exam}, ID {id}, Code Examen {code_exam}, Exam Code {code_exam_id}")
      return type_exam,id, code_exam , code_exam_id

fetcher = ExamenFetcher()

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
        type_examen ,type_examen_id, code_examen , code_examen_id = fetcher.lyae_talk_exam(query)
        return func.HttpResponse(
            json.dumps({"type_examen": type_examen , "type_examen_id":type_examen_id , "code_examen":code_examen , "code_examen_id": code_examen_id}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
