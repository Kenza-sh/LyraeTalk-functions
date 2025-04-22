import azure.functions as func
import logging
import re
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class InformationExtractor:
    def __init__(self ):
        logger.info("Initialisation")
    def extraire_numero_telephone(self, texte):
        logger.info(f"Extraction du numéro de téléphone à partir du texte : {texte}")
        # Normalisation du texte en supprimant les espaces, tirets, et points
        phone_number = texte.replace(" ", "").replace("-", "").replace(".", "")
        # Premier regex : validation des numéros compactés
        phone_regex = r"^(\+?\d{1,3})?(\d{9,10})$"
        numero_telephone = re.search(phone_regex, phone_number)
        if numero_telephone:
            logger.info(f"Numéro de téléphone extrait : {numero_telephone.group()}")
            return numero_telephone.group()
        # Deuxième regex : validation des formats avec séparateurs (espaces, tirets)
        numero_telephone = re.search(r"(\+?\d{1,3}[\s-]?)?(\(?\d{1,4}\)?[\s-]?)?(\d{2}[\s-]?){4}\d{2}", phone_number)
        if numero_telephone:
            logger.info(f"Numéro de téléphone extrait avec séparateurs : {numero_telephone.group()}")
            return numero_telephone.group()
        logger.warning("Aucun numéro de téléphone valide n'a été extrait.")
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

        result = extractor.extraire_numero_telephone(query)

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
