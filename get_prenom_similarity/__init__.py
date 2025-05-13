import logging
import azure.functions as func
import re
import json
import os
from rapidfuzz import process

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def retrouver_prenom(personnes, texte):
    noms_famille = [nom.lower() for nom, prenom in personnes]
    resultat = process.extractOne(texte.lower(), noms_famille, score_cutoff=80)
    if resultat:
        nom_trouve, score, index = resultat
        prenom_correspondant = personnes[index][1]
        logger.info(f"Nom détecté : {nom_trouve} (score : {score:.2f})")
        logger.info(f"Prénom associé : {prenom_correspondant}")
        return nom_trouve , prenom_correspondant
    else:
        logger.info("Aucune correspondance suffisamment proche trouvée.")
        return None , None
      
 
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        texte = req_body.get('text')
        personnes = req_body.get('patient_list')

        if not texte or not personnes:
            return func.HttpResponse(
                json.dumps({"error": "Both 'text' and 'patient_list' must be provided in the request body"}),
                mimetype="application/json",
                status_code=400
            )
        if not isinstance(personnes, list) or not all(isinstance(p, (list, tuple)) and len(p) == 2 and all(isinstance(x, str) for x in p)  for p in personnes):
             return func.HttpResponse(
                json.dumps({"error": "Le champ 'personnes' doit être une liste de paires (nom, prénom) de chaînes de caractères."}),
                mimetype="application/json",
                status_code=400
            )
                 
        personnes = [tuple(p) for p in personnes]
        nom, prenom = retrouver_prenom(personnes, texte)

        return func.HttpResponse(
            json.dumps({"nom": nom , "prenom": prenom}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
           
