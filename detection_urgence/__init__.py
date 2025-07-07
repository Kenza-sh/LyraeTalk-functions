import re
import azure.functions as func
import logging
import json
import os

def is_urgence(type_exam_id: str, phrase: str) -> bool:
    if not isinstance(phrase, str) or not phrase.strip():
        return False

    # Normalisation
    phrase = phrase.strip().lower()

    # Dictionnaire des patterns par type d'examen
    patterns_by_exam = {
        "US": [
            r"\bd[eéèêë]fenses?\b",
            r"\bsyndromes? appendiculaires?\b",
            r"\bappendicites?\b",
            r"\bp[yéèêë]lon[eéèêë]phrites?\b",
            r"\bchol[eéèêë]cystites?\b",
            r"\bgeu\b",
            r"\bgrossesses? extra[- ]ut[eéèêë]rines?\b",
            r"\btorsions?\b",
            r"\bsalpingites?\b",
            r"\borchi[- ]?[eéèêë]pididymites?\b",
        ],
        "RX": [
            r"\bfractures?\b",
            r"\bluxations?\b",
            r"\btassements?\b",
            r"\bpneumonies?\b",
            r"\bfoyers? pulmonaires?\b",
            r"\binhalations?\b",
            r"\bcorps? [eéèêë]trangers?\b",
        ],
        "CT": [
            r"\bd[eéèêë]fenses?\b",
            r"\bappendicites?\b",
            r"\bdiverticulites?\b",
            r"\bocclusions?\b",
            r"\bperforations?\b",
            r"\bp[yéèêë]lon[eéèêë]phrites? compliqu[eéèêë]es?\b",
            r"\bcoliques? n[éèêë]phr[eéèêë]tiques? f[éèêë]briles?\b",
            r"\bembolies? pulmonaires?\b",
            r"\bspondylodiscites?\b",
            r"\blombalgies? f[éèêë]briles?\b",
            r"\btassements? vert[eéèêë]braux?\b",
            r"\babc[èeéêë]s?\b",
            r"\bcellulites?\b",
            r"\bamygdalites?\b",
        ],
        "MR": [
            r"\bsyndromes? de la queue de cheval\b",
            r"\banesth[éèêë]sies? en selles?\b",
            r"\btroubles? sphinct[éèêë]riens?\b",
            r"\bparapar[éèêë]sies? progressives?\b",
            r"\bspondylodiscites?\b",
            r"\babc[èeéêë]s?\b",
            r"\bthromboses? veineuses? c[éèêë]r[éèêë]brales?\b",
            r"\bthrombophl[éèêë]bites?\b",
            r"\bm[éèêë]ningites?\b",
        ]
    }

    # Pattern par défaut si type non reconnu
    default_patterns = [
        r"\burgences?\b",
        r"\burgemment\b",
        r"\burgent(?:e|s|es)?\b",

    ]

    # Sélection des bons patterns
    patterns = patterns_by_exam.get(type_exam_id.upper(), []) + default_patterns

    # Compilation et recherche
    master_pattern = re.compile("|".join(patterns), re.IGNORECASE)
    return bool(master_pattern.search(phrase))


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        type_exam_id = req_body.get('type_exam_id')
        query = req_body.get('text')

        if not all([type_exam_id,query]):
            return func.HttpResponse(
                json.dumps({"error": "Missing one or more required fields: type_exam_id, text"}),
                mimetype="application/json",
                status_code=400
            )

        result = is_urgence(type_exam_id  ,query)

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

