import azure.functions as func
import logging
import re
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class InformationExtractor:
    def __init__(self ):
        logger.info("Initialisation")
    def extraire_code_postal(self, texte):
        logger.info(f"Extraction du code postal à partir du texte : {texte}")
        code_postal = re.search(r"\b\d{5}\b", texte)
        if code_postal:
            logger.info(f"Code postal extrait : {code_postal.group()}")
            return code_postal.group()
        else:
            logger.warning("Aucun code postal valide n'a été extrait.")
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

        result = extractor.extraire_code_postal(query)

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
