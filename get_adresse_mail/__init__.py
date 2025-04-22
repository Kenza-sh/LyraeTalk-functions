import azure.functions as func
import logging
import re
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class InformationExtractor:
    def __init__(self ):
        logger.info("Initialisation")
    def extraire_adresse_mail(self, texte):
        logger.info(f"Extraction de l'adresse email à partir du texte : {texte}")
        substitutions = [
        (r'\s*(arobase|at)\s*', '@'),        # Gestion des variantes de @
        (r'\s*(underscore|under\s*score)\s*', '_'),        # Gestion des underscores
        (r'\s*(dot|point)\s*', '.'),         # Gestion des points
        (r'\s*(hyphen|minus|moins|tiret)\s*', '-'),       # Gestion des traits d'union
        (r'\s*@\s*', '@'),                   # Suppression des espaces autour de @
        (r'\s*\.\s*', '.'),                  # Suppression des espaces autour des points
        (r'\s*-\s*', '-'),                   # Suppression des espaces autour des -
        (r'\s*_\s*', '_')                    # Suppression des espaces autour des _
    ]

        for pattern, replacement in substitutions:
                          texte = re.sub(pattern, replacement, texte, flags=re.IGNORECASE)
        adresse_mail = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", texte)
        if adresse_mail:
            logger.info(f"Adresse email extraite : {adresse_mail[0].strip()}")
            return adresse_mail[0].strip()
        else:
            logger.warning("Aucune adresse email valide n'a été extraite.")
        return None
      
extractor =  InformationExtractor()

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

        result = extractor.extraire_adresse_mail(query)

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
