import re
import azure.functions as func
import logging
import json

# motifs de négation à exclure avant tout diagnostic positif
NEGATION_TERMS_LIST = [
    r"pas\s+de",
    r"sans",
    r"aucun(?:e)?s?",
    r"absence\s+d['e]",
    r"nul(?:le)?s?",
    r"hors\s+de",
    r"n[eéèêë]gatif(?:s|ves)?\s+pour",
    r"aucune\s+anomalie\s+d[eéèêë]tect[éeé]"
]
# compile motifs négation en une seule regex
NEGATION = re.compile(r"\b(?:%s)\b" % "|".join(NEGATION_TERMS_LIST), re.IGNORECASE)

# taille fixe du contexte à vérifier avant le terme (nombre de caractères)
CONTEXT_WIDTH = 30

# codes d'examens CT catégorisés :
IMMEDIATE_POSITIVE = {
    'CT': {
        'always_true': [
            'N01CT072', 'N01CT026', 'N01CT028', 'N01CT043'
        ],
        'patterns': {
            # abdomen/pelvis/uroscanner
            ('N01CTABD', 'N01CT030', 'N01CT031', 'N01CT039', 'N01CT036'): [
                r"\b[aàáâä]pp[eéèêë]ndicites?\b",
                r"\bdiverticulites?\b",
                r"\bsigmo[iîïíì]dites?\b",
                r"\bocclusions?\b",
                r"\bpancr[eéèêë]atites?\b",
                r"\bdouleurs? abdominales?\b",
                r"\bconstipations?\b",
                r"\bh[eéèêë]maturies?\b",
                r"\bkystes? r[eéèêë]naux?\b",
                r"\bnodules? r[eéèêë]naux?\b",
                r"\blipas[eéèêë]mies?\b",
                r"\bmasses? r[eéèêë]nales?\b",
                r"\brectorragies?\b",
                r"\bexplorations? surr[eéèêë]naliennes?\b",
            ],
            # thorax
            ('N01CT023', 'N01CTCER'): [
                r"\b[aà]bc[eéèêë]s?\b",
                r"\b[aà]t[eéèêë]l[eéèêë]ct[aà]s[iîïíì][eéèêë]s?\b",
                r"\bbilans?\s+d[’']?[eéèêë]xt[eéèêë]nsions?\b",
                r"\bbrachy(?:œ|oe)s?phag[eéèë]s?\b",
                r"\bdysphagies?\b",
                r"\b[eéèêë]largissements?\s+m[eéèêë]diastinals?\b",
                r"\bembolies?\s+pulmonaires?\b",
                r"\bh[eéèêë]moptysies?\b",
                r"\bherni[eéèêë]s?\s+hiatales?\b",
                r"\bparalysies?\s+phr[eéèêë]niques?\b",
                r"\bpleur[eéèêë]sies?\b",
                r"\bclaude-bernard-horners?\b",
            ],
            # crâne
            ('N01CT004',): [
                r"\balt[eéèêë]rations?\b",
                r"\ban[eéèêë]vrismes?\b",
                r"\btrijumeaux?\b",
                r"\bc[eéèêë]phal[eéèêë]es?\b",
                r"\bch[eéèêë]mosiss?\b",
                r"\bconvulsions?\b",
                r"\b[eéèêë]pilepsies?\b",
                r"\bd[eéèêë]ficits?\s+h[eéèêë]micorporels?\b",
                r"\bavcs?\b",
                r"\baits?\b",
                r"\baphasies?\b",
                r"\bparesth[eéèêë]sies?\b",
                r"\bparalysies?\b",
                r"\bmalaises?\b",
                r"\bm[eéèêë]lanomes?\b",
                r"\bmigraines?\b",
                r"\bnaus[eéèêë]es?\b",
                r"\borbites?\b",
                r"\bost[eéèêë]ites?\b",
                r"\bn[eéèêë]oplasies?\b",
                r"\b(?:œ|oe)d[eéèêë]mes?\s+papillaires?\b",
                r"\bhyperpressions?\b",
                r"\btumeurs?\b",
                r"\bcancers?\b",
                r"\bvertiges?\b",
            ],
            # rachis
            ('N01CT049', 'N01CT051', 'N01CT050', 'N01CT047'): [
                r"\bspondylodiscites?\b",
                r"\babc[eéèêë]s?\b",
                r"\binfections?\b",
                r"\bcollections?\b",
                r"\bfistules?\b",
                r"\bmalformations?\s+vasculaires?\b",
                r"\b[eéèêë]pidurites?\b",
            ],
            # sinus
            ('N01CT008',): [
                r"\bcellulites?\b",
                r"\babc[eéèêë]s?\b",
                r"\bost[eéèêë]ites?\b",
                r"\bthrombophl[eéèêë]bites?\b",
                r"\bmass(es?)?\b",
                r"\b[eéèêë]pistaxis\b",
            ],
        }
    }
}

def contains_suspicious_terms(text: str) -> bool:
    pattern = r"\b(injection|tumeu?r(?:e|es)?|masse?s?|kystes?|néoplasies?|adénopathies?|ganglions?|produits?\s+de\s+contraste|tuméfactions?)\b"
    return re.search(pattern, text, re.IGNORECASE | re.UNICODE) is not None
    
def is_injection(type_exam_id: str, code_exam_id: str, phrase: str) -> bool:
    if type_exam_id != 'CT':
        return False
    if contains_suspicious_terms(phrase) :
         return True
    if code_exam_id in IMMEDIATE_POSITIVE['CT']['always_true']:
        return True

    for code_group, pats in IMMEDIATE_POSITIVE['CT']['patterns'].items():
        if code_exam_id in code_group:
            combined = re.compile(r"|".join(pats), re.IGNORECASE)
            for m in combined.finditer(phrase):
                start = max(0, m.start() - CONTEXT_WIDTH)
                pre_context = phrase[start:m.start()]
                if not NEGATION.search(pre_context):
                    return True
            return False

    return False


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        req_body = req.get_json()
        type_exam_id = req_body.get('type_exam_id')
        code_exam_id = req_body.get('code_exam_id')
        text = req_body.get('text')

        if not all([type_exam_id, code_exam_id, text]):
            return func.HttpResponse(
                json.dumps({"error": "Missing one or more required fields: type_exam_id, code_exam_id, text"}),
                mimetype="application/json",
                status_code=400
            )

        result = is_injection ( type_exam_id , code_exam_id , text)
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

