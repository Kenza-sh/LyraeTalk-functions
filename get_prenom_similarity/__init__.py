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
        # Essayer de parser le JSON
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Le corps de la requête doit être un JSON valide."}),
                mimetype="application/json",
                status_code=400
            )

        texte = req_body.get('text')
        personnes = req_body.get('patient_list')

        # Vérifier la présence des champs
        if not texte or not personnes:
            return func.HttpResponse(
                json.dumps({"error": "Les champs 'text' et 'patient_list' sont obligatoires."}),
                mimetype="application/json",
                status_code=400
            )

        # Vérification de la structure de patient_list
        if not isinstance(personnes, list):
            return func.HttpResponse(
                json.dumps({"error": "'patient_list' doit être une liste."}),
                mimetype="application/json",
                status_code=400
            )

        for p in personnes:
            if not isinstance(p, (list, tuple)) or len(p) != 2 or not all(isinstance(x, str) for x in p):
                return func.HttpResponse(
                    json.dumps({"error": "Chaque élément de 'patient_list' doit être une paire (nom, prénom) de chaînes de caractères."}),
                    mimetype="application/json",
                    status_code=400
                )

        # Conversion explicite en tuples
        personnes = [tuple(p) for p in personnes]

        # Appel de la fonction de traitement
        nom, prenom = retrouver_prenom(personnes, texte)

        return func.HttpResponse(
            json.dumps({"nom": nom , "prenom": prenom}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Erreur lors du traitement de la requête : {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Erreur interne du serveur."}),
            mimetype="application/json",
            status_code=500
        )
