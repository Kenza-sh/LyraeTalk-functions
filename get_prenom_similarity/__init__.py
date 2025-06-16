import logging
import azure.functions as func
import re
import json
import os
from rapidfuzz import fuzz, process
import jellyfish
import unicodedata

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def normalize_text(text):
    nfkd = unicodedata.normalize('NFKD', text.lower())
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])

from rapidfuzz import fuzz, process
import jellyfish
import logging
import unicodedata

logger = logging.getLogger(__name__)

def normalize_text(text):
    """Normalise le texte pour la comparaison : minuscules et suppression accents"""
    nfkd = unicodedata.normalize('NFKD', text.lower())
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])

class NameMatcher:
    def __init__(self):
        pass  # Plus rien à faire au constructeur
    
    def find_name(self, texte, personnes):
        """
        Recherche un nom dans la liste personnes à partir du texte.
        personnes : liste de tuples (nom, prenom)
        """
        # Normalisation et préparation à chaque appel
        normalized_data = [
            (normalize_text(nom), normalize_text(prenom), nom, prenom) 
            for nom, prenom in personnes
        ]
        normalized_names = [d[0] for d in normalized_data]
        phonetic_names = [jellyfish.metaphone(n) for n in normalized_names]

        texte_norm = normalize_text(texte)
        
        # 1. Recherche exacte
        if texte_norm in normalized_names:
            idx = normalized_names.index(texte_norm)
            _, _, nom_orig, prenom_orig = normalized_data[idx]
            logger.info(f"[Exact] Nom détecté : {nom_orig}")
            return nom_orig, prenom_orig
        
        # 2. Fuzzy matching adapté au français
        result = process.extractOne(
            texte_norm,
            normalized_names,
            scorer=fuzz.QRatio,
            score_cutoff=65
        )
        
        if result:
            nom_trouve, score, idx = result
            _, _, nom_orig, prenom_orig = normalized_data[idx]
            logger.info(f"[Fuzzy] Nom détecté : {nom_orig} (score : {score:.2f})")
            return nom_orig, prenom_orig
        
        # 3. Phonétique amélioré
        phon_texte = jellyfish.metaphone(texte_norm)
        best_score = 0
        best_idx = -1
        
        for idx, phon_nom in enumerate(phonetic_names):
            score = fuzz.partial_ratio(phon_texte, phon_nom)
            if score > best_score:
                best_score = score
                best_idx = idx
        
        if best_score >= 80:
            _, _, nom_orig, prenom_orig = normalized_data[best_idx]
            logger.info(f"[Phonétique] Nom détecté : {nom_orig} (score : {best_score:.2f})")
            return nom_orig, prenom_orig
        
        # 4. Fallback : recherche de sous-chaîne
        for idx, name in enumerate(normalized_names):
            if texte_norm in name or name in texte_norm:
                _, _, nom_orig, prenom_orig = normalized_data[idx]
                logger.info(f"[Substring] Nom détecté : {nom_orig}")
                return nom_orig, prenom_orig
        
        logger.info("Aucune correspondance trouvée.")
        return None, None
            
matcher = NameMatcher()         
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
        nom, prenom = matcher.find_name(texte, personnes)

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
