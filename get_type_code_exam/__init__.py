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
        self.llm_model = "gpt-4o-mini" #"gpt-35-turbo"
        self.radio_interv = [
                r'\bm[íi]cro[- ]?biopsie(s)?\b',
                r'\bbiopsie(s)?\b',
                r'\bdrainage(s)?\b',
                r'\binfiltration(s)?\b',
                r'\bpose(s)?[- ]?de[- ]?cath[éeèe]ter(s)?\b',
                r'\bembolisation(s)?\b',
                r'\bangioplastie(s)?\b',
                r'\bradio[- ]?fr[éeèe]quence(s)?\b',
                r'\bablation(s)?\b',
                r'\bmicro[- ]?ondes\b',
                r'\bcimentoplastie(s)?\b',
                r'\bfiltre(s)?[- ]?cave(s)?\b',
                r'\bthrombectomie(s)?\b',
                r'\bthrombolyse(s)?\b',
                r'\bponction(s)?\b',
                r'\bcyto[- ]?ponction(s)?\b',
                r'\btips\b',
                r'\bgastrostomie(s)?\b',
                r'\bnéphrostomie(s)?\b',
                r'\bcholangiographie(s)?\b',
                r'\bangiographie(s)?\b',
                r'\bfistulographie(s)?\b',
                r'\bdilatation(s)?\b',
                r'\bpose(s)?[- ]?de\b',
                r'\bscl[éeèe]ro[- ]?th[éeèe]rapie(s)?\b',
                r'\bmise(s)?[- ]?en[- ]?place[- ]?de\b',
                r'\breconstruction(s)?\b',
                r'\bcryo[- ]?ablation(s)?\b',
                r'\banesth[éeèe]sie(s)?\b',
                r'\bproc[éeèe]dure(s)?\b',
                r'\basepsie(s)?\b',
                r'\bconsentement(s)?\b',]
        self.patterns_ardio_interv =[re.compile(p, re.IGNORECASE) for p in self.radio_interv ]
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
            "MAMMOGRAPHIE": ["mammographie","mammographique", "mammogramme", "mammo", "mamographie","mamo", "sein", "seins", "mammaire" , "dépistage" ,"depistage"],
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
            return "AUTRE", False, False

        # Normalisation de base
        txt = texte.lower().replace("’", "'")
        is_radio_interv = any(p.search(txt) for p in self.patterns_ardio_interv)

        # Suppression des accents et tokenisation
        normalized = unicodedata.normalize("NFKD", txt)
        cleaned_txt = ''.join(c for c in normalized if not unicodedata.combining(c))
        mots = re.findall(r"\b\w+\b", cleaned_txt)

        # Comptage des occurrences par catégorie
        category_scores = {}
        for category, words in self.keywords.items():
            # Nettoyage et déduplication des mots-clés
            cleaned_words = set(
                ''.join(c for c in unicodedata.normalize("NFKD", w.lower()) if not unicodedata.combining(c))
                for w in words
            )
            # Compter chaque mot-clé dans le texte
            counts = {w: mots.count(w) for w in cleaned_words}
            total_occurrences = sum(counts.values())
            if total_occurrences > 0:
                category_scores[category] = total_occurrences

        # Aucun mot-clé détecté
        if not category_scores:
            logging.info("Aucun type d'examen trouvé, retour par défaut: AUTRE")
            return "AUTRE", False, is_radio_interv

        # Sélection de la catégorie principale (celle avec le plus d'occurrences)
        top_category = max(category_scores.items(), key=lambda x: x[1])[0]
        total_matches = sum(category_scores.values())

        # Correspondance forte si au moins 2 examens détectés (mêmes ou différents types)
        is_strong_match = total_matches >= 2

        return top_category, is_strong_match, is_radio_interv
                
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
            f"Corrige les erreurs de cette phrase issues de la mauvaise transcription vocale (speech-to-text), telles que les confusions phonétiques ou les homophones mal interprétés. "
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
                
    def query_correction(self, text):
        actes = self.fetch_examens()
        custom_prompt_template = (
             f"Voici la liste des examens médicaux proposés par notre centre d'imagerie médicale : {', '.join(actes.values())}. \n"
             f"""Vous êtes un correcteur orthographique spécialisé en imagerie médicale et gestion de rendez-vous.  
• En vous basant sur la phrase du patient, corrigez les erreurs issues de la mauvaise transcription vocale (speech-to-text), telles que les confusions phonétiques ou les homophones mal interprétés.  
• Restez strictement dans le domaine de l’imagerie médicale (radiographie, scanner, angioscanner, coroscanner, IRM, échographie, mammographie, etc.) et de la prise de rendez-vous.  
Vous devez répondre **uniquement** par la phrase corrigée, **sans** ajouter d’explication ni de commentaire.
"""
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
            logging.info(f"Correction de la requete patient : {completion.choices[0].message.content}")
            return (completion.choices[0].message.content).strip()
        except Exception as e:
            logging.error(f"Error answering query: {e}")
            return ''      
                    
    def lyae_talk_exam(self, texte):
      exam_types = {
          "RADIO": "RX",
          "SCANNER": "CT",
          "IRM": "MR",
          "ECHOGRAPHIE": "US",
          "MAMMOGRAPHIE": "MG",
          'AUTRE' : None
      }
      #texte = self.query_correction(texte)
      texte=self.process_text(texte)
      type_exam , multiple_exam , is_radio_interv = self.get_type_examen(texte)
      id = exam_types.get(type_exam)      
      actes = self.fetch_examens([id]) if id else self.fetch_examens()
      code_exam = self.get_class(texte, actes)
      code_exam_id = next((k for k, v in actes.items() if self.equiv(v, code_exam )), None)
      if code_exam=='None':
         code_exam= None
      else :
          code_exam = self.normalize_examen(str(code_exam))
      if id=="MG" and code_exam_id is None :
                  code_exam ="Mammographie Bilatérale"
                  code_exam_id = "N01MGBIL"
      if not id and code_exam:
              type_exam , multiple_exam , is_radio_interv = self.get_type_examen(code_exam)
              id = exam_types.get(type_exam)
      logging.info(f"Résultat final: Type {type_exam}, ID {id}, Code Examen {code_exam}, Exam Code {code_exam_id}")
      return type_exam,id, code_exam , code_exam_id , multiple_exam , is_radio_interv


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
        type_examen ,type_examen_id, code_examen , code_examen_id , multiple_exam , is_radio_interv = fetcher.lyae_talk_exam(query)
        return func.HttpResponse(
            json.dumps({"type_examen": type_examen , "type_examen_id":type_examen_id , "code_examen":code_examen , "code_examen_id": code_examen_id , "multiple_exam": multiple_exam , "radio_interventionnelle" : is_radio_interv}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
