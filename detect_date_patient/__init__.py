import re
import logging
from openai import AzureOpenAI
from datetime import datetime
import os
import requests
import json
import azure.functions as func

client = AzureOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version="2024-05-01-preview"
        )

class CreneauAnalyzer:
    def __init__(self):
        self.jours_semaine = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        self.mois_fr = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']

    def get_creneaux_string(self, creneaux):
        lignes = []
        for date_str in creneaux:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            jour = self.jours_semaine[dt.weekday()].capitalize()
            mois_nom = self.mois_fr[dt.month - 1]
            formatted = f"{jour} {dt.day:02d} {mois_nom} {dt.year} à {dt.strftime('%Hh%M')}"
            ligne = f"{date_str} --> {formatted}"
            lignes.append(ligne)
        return " \n ".join(lignes)

    def get_creneaux_adaptes(self, demande_patient: str, creneaux_disponibles: list[str]):
        today = datetime.today()
        today_str = today.strftime("%Y-%m-%d")
        jour_nom = self.jours_semaine[today.weekday()]
        interpretation = self.get_creneaux_string(creneaux_disponibles)
        prompt = f"""
Aujourd'hui, nous sommes le {jour_nom} {today_str}.

Un patient souhaite prendre rendez-vous et a formulé la demande suivante : {demande_patient}.

Voici la liste des créneaux disponibles : {creneaux_disponibles}.
Pour t'aider voici une interprétation des créneaux précédents : 

{interpretation}

Note importante : 
- Le week-end correspond au samedi et dimanche. 
- La 'soirée' doit être interprétée comme la fin d'après-midi.
- L'après-midi commence à partir de 14h, tout ce qui est avant est considéré comme matinée.
- Considérer le *début de la semaine* comme étant le lundi et le mardi.
- Considérer la *fin de la semaine* comme étant le jeudi et le vendredi.
- Considérer la fin du mois comme la période allant du 25 jusqu’au dernier jour du mois en cours.
- Considérer le mois prochain comme le mois qui va suivre le mois actuel.
- Si le jour mentionné par le patient est déjà passé dans la semaine en cours, considère qu’il s’agit de ce même jour **dans la semaine suivante**. 
  Sinon, prends en compte ce jour **à la fois dans la semaine en cours** et **dans la semaine suivante**.
- Si le patient utilise des mots exprimant une exclusion ('sauf', 'pas', 'excepté', 'hors', etc.), il faut exclure toutes les dates ou créneaux concernés.

Analyse la demande du patient et identifie les créneaux qui correspondent le mieux à ses préférences (date, heure, disponibilité, etc.). 

Retourne une **liste des créneaux adaptés**, sans aucun commentaire supplémentaire.
Si aucun créneau ne correspond à la demande, retourne simplement : 'None'
"""
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.8,
                max_tokens=2048,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": demande_patient}
                ]
            )
            result = completion.choices[0].message.content.strip()
            if "none" in result.lower():
               return None
            logging.info(f"Réponse de l'IA : {result}")
            return json.loads(result)
        except Exception as e:
            logging.error(f"Erreur lors de l'analyse de la demande : {e}")
            return None

analyzer = CreneauAnalyzer()

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Le corps de la requête doit être un JSON valide."}),
                mimetype="application/json",
                status_code=400
            )

        texte = req_body.get('text')
        creneaux_list = req_body.get('creneaux_list')

        # Vérifier la présence des champs
        if not texte or not creneaux_list:
            return func.HttpResponse(
                json.dumps({"error": "Les champs 'text' et 'creneaux_list' sont obligatoires."}),
                mimetype="application/json",
                status_code=400
            )

        # Vérification de la structure de patient_list
        if not isinstance(creneaux_list, list):
            return func.HttpResponse(
                json.dumps({"error": "'creneaux_list' doit être une liste."}),
                mimetype="application/json",
                status_code=400
            )
        res = analyzer.get_creneaux_adaptes(texte, creneaux_list)
        return func.HttpResponse(
            json.dumps({"response":res}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Erreur lors du traitement de la requête : {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Erreur interne du serveur."}),
            mimetype="application/json",
            status_code=500
        )


