import logging
import azure.functions as func
import re
import json
import os
import string
from openai import AzureOpenAI


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


client = AzureOpenAI(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version="2024-05-01-preview"
)

class AnalyseurConversation:
    def __init__(self):
        self.exemples = {
            "négative": [
                 "Non, merci.", "Je ne suis pas d'accord.", "Non, ce n'est pas pour moi.",
                "Je préfère ne pas.", "Non, ce n'est pas possible.", "Non, je ne veux pas.",
                "Je ne suis pas intéressé.", "Non, je ne le ferai pas.", "Ce n'est pas ce que je veux.",
                "Non, je ne crois pas.", "Non, je ne pense pas.", "Non, c'est non.", "Je m'abstiens.",
                "Non, pas question.", "Ce n'est pas acceptable pour moi.", "Non, je refuse catégoriquement.",
                "Je ne consens pas", "Je ne veux pas", "Pas du tout", "C'est non", "Je ne peux pas", "Je refuse",
                "Hors de question", "Impossible pour moi", "Ça ne me correspond pas", "Je décline l'offre",
                "Je m'y oppose", "Pas cette fois", "Non merci, c'est tout", "Je suis contre", "Niet !",
                "Refus net et définitif", "Aucune chance", "Nan", "Ça ne m'emballe pas", "Je botte en touche",
                "Je ne marche pas", "Pas maintenant", "C'est mort", "Je ne suis pas convaincu", 
                "Ça ne me tente pas", "Je ne suis pas partant", "Je passe mon tour", "Non merci, sans moi",
                "Absolument pas", "En aucun cas", "Je m'y refuse", "Pas question", "Je ne suis pas chaud",
                "Je ne valide pas", "Ça ne me branche pas", "Je dis stop", "Pas envisageable", 
                "Je ne cautionne pas", "Je bloque là-dessus", "Je ne suis pas en phase", "je n'accepte pas"
                "Ça ne me convient pas", "Je ne signe pas", "Je recule", "Pas moyen", "C'est exclu",
                "Je ne suis pas ok", "Je ne donne pas mon accord", "Je ferme la porte à ça","no","impossible","nope",'non','refus',
                "ce n'est pas ça","ce n'est pas cela","c'est pas ça","c'est pas cela","non c'est pas ça","non c'est pas cela","pas ça",
                "pas cela","non ce n'est pas ça","non ce n'est pas cela"],
            "indéterminée": [
                "Oui mais " , "Je ne suis pas sûr.", "Je ne sais pas.", "Peut-être, je ne sais pas vraiment.",
                "Je ne suis pas convaincu.", "C'est compliqué.", "Je doute.", "Ça m'embête.",
                "Je ne suis pas certain.", "C'est flou.", "Je crois que non.", 
                "Je ne suis pas certain de ma réponse.", "Je ne sais pas quoi répondre.",
                "Je suis hésitant.", "C'est ambigu.", "Je ne suis pas clair sur ma réponse.",
                "Je n'ai pas d'avis.", "Je ne sais pas trop.", "Je suis indécis.",
                "C'est un peu flou pour moi.", "Je suis partagé.", "J'ai des doutes.",
                "Je n'ai pas de réponse précise.", "Je ne peux pas me prononcer.", "C'est incertain."
            ],
            "positive": [
                "Oui, bien sûr.","bien sûr", "C'est ca","yes", "je suis ok", "D'accord, je suis partant.", 
                "Oui, je le fais volontiers.", "C'est une excellente idée.", 
                "Oui, sans hésiter.", "Oui, je confirme.", "Bien sûr, je suis d'accord.",
                "Oui, c'est tout à fait correct.", "Je suis pour.", "Oui, je suis avec vous.",
                "Sans problème, c'est oui.", "Oui, pourquoi pas.", "D'accord, je le ferai.",
                "Oui, c'est une bonne solution.", "Absolument","exactement" ,"Avec plaisir", "Ça me va",
                "Bien entendu", "Pas de souci", "Ok, c'est bon", "C'est bon pour moi","Go", "C'est parti", "On y va",
                "On fonce", "Allons-y","Très bien", "Ça roule","D'acc","Mais bien sûr", "Bien volontiers","Carrément, je suis d'accord.", 
                "Ouais, c'est tout bon pour moi.", "Sans doute, je suis partant.", "Tout à fait, c'est validé.", "Je suis en phase avec ça.",
                "C'est un grand oui.", "Je valide complètement.", "Tout à fait, c'est super.", "Bien sûr, il n'y a pas de souci.", "Je suis chaud pour ça.", 
                "C'est bon, on y va.", "Ça marche pour moi.", "Je suis partant à 100%.", "Tu peux compter sur moi.", "Je suis on board.", 
                "Je suis dispo, allons-y.", "Je le fais sans problème.", "Avec grand plaisir.", "C'est tout bon, allons-y.", "Volontiers !", 
                "Entièrement d'accord", "Je souscris à cette idée", "C'est noté", "Je m'engage à le faire", "Je ne dis pas non", "Tout à fait d'accord",
                "Je suis ravi de participer", "C'est validé de mon côté", "Je signe des deux mains", "Je marche à 100%", "C'est entendu",
                "Aucune objection", "Je plussoie", "C'est nickel", "Je valide à 200%","C'est bien ca","pas de problème",
                'sans hésitation','sans souci', 'sans problème',"sans aucun souci","sans aucun problème",'nickel','top',"je valide",
                "Je m'y attelle avec joie", "C'est top", "Je m'implique totalement", "Je ne peux qu'approuver", "C'est du tout bon","oui",'ok',"j'accepte",
                "C'est ça", "C'est cela",
            ],
            
        }

        self.phrase_to_category = {}
        self.preprocess_phrases()
        self.compile_regex()

    def preprocess_phrase(self, text):
        translator = str.maketrans('', '', string.punctuation)
        processed = text.translate(translator).lower().strip()
        return ' '.join(processed.split())

    def preprocess_phrases(self):
        for categorie, phrases in self.exemples.items():
            for phrase in phrases:
                processed = self.preprocess_phrase(phrase)
                if processed in self.phrase_to_category:
                    logger.warning(f"Phrase dupliquée détectée: '{processed}'")
                self.phrase_to_category[processed] = categorie

    def compile_regex(self):
        if not self.phrase_to_category:
            self.regex = None
            return

        patterns = [re.escape(p) for p in self.phrase_to_category.keys()]
        pattern = r'^(' + '|'.join(patterns) + r')$'
        self.regex = re.compile(pattern)

    def detecter_type_reponse(self, texte):
        if self.regex is None:
            return False
            
        texte_preprocessed = self.preprocess_phrase(texte)
        match = self.regex.match(texte_preprocessed)
        return self.phrase_to_category.get(match.group(1), False) if match else False

    def get_class(self, text):
        prompt_template = (
            "Classifiez cette réponse comme 'positive', 'négative' ou 'indéterminée'. "
            "Répondez uniquement par un seul mot en minuscules.\n"
            f"Réponse: {text}"
        )

        try:
            completion = client.chat.completions.create(
                model="gpt-35-turbo",
                messages=[
                    {"role": "system", "content": prompt_template},
                    {"role": "user", "content": text}
                ],
                temperature=0.0,
                max_tokens=10
            )
            
            result = completion.choices[0].message.content.strip().lower()
            if result in {'positive', 'négative', 'indéterminée'}:
                return result
            return 'indéterminée'
        except Exception as e:
            logger.error(f"Erreur OpenAI: {e}")
            return 'indéterminée'

    def get_response(self, texte):
        # Détection rapide avec regex
        detection = self.detecter_type_reponse(texte)
        if detection:
            return detection
        # Fallback sur le modèle si aucune détection
        return self.get_class(texte)


analyzer=AnalyseurConversation()

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
        
        result = analyzer.get_response(query)

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
           
