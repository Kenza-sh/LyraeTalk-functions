from openai import AzureOpenAI
import azure.functions as func
import logging
import json
import os
import re
from unidecode import unidecode

client = AzureOpenAI(
          azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"],
          api_key= os.environ["AZURE_OPENAI_API_KEY"],
          api_version="2024-05-01-preview"
        )
llm_model="gpt-35-turbo"
human_assistant_keywords = [
   r"\béquipe secrétariat\b",r"\bservice des assistantes\b",r"\binterlocuteur\b",r"\bcontact physique\b",
  r"\bquelqu'un\b",r"\bcontact humain\b",r"\bcontact direct\b",r"\bprise en charge humaine\b",r"\bsupport administratif\b",
  r"\baide administrative\b",r"\bpersonnel administratif\b",r"\baccompagnement\b",r"\bpoint de contact humain\b",
  r"\béchange direct\b",r"\bcellule d'assistance\b",r"\bpersonne référente\b",r"\blien humain\b",r"\bcoordination humaine\b",
  r"\bservice relationnel\b",r"\bagent administratif\b",r"\brelation humaine directe\b",r"\brelation humaine\b",
  r"\bmembre de l'équipe support\b",r"\brelais humain\b",r"\bsupport opérationnel\b",r"\bpôle administratif\b",
  r"\bparler à une vraie personne\b",r"\bje ne veux pas parler à un robot\b",r"\bquelqu’un au téléphone\b",
  r"\bme transférer à une secrétaire ou à une personne du cabinet\b",r"\bje veux parler à quelqu’un\b",
  r"\brelation avec une personne\b",r"\bparler à quelqu’un de vrai\b",
  r"\bje refuse de continuer cette conversation avec une machine\b",r"\bje refuse l’assistance automatisée\b",
  r"\bje refuse l’assistant automatisé\b",r"\bje souhaite qu’une vraie personne prenne le relais\b",
  r"\bparler à un membre de votre équipe\b",r"\brelation avec un agent humain\b",r"\bavec une personne réelle\b",
  r"\bpas à une machine\b",r"\bpas un échange automatisé\b",r"\bje refuse d’utiliser ce service automatisé\b",
  r"\bavoir un échange téléphonique avec une assistante\b",r"\bmerci de mettre fin à ce chat automatisé\b", r"\bme passer à une collaboratrice\b",
  r"\bstoppez le chatbot\b",r"\bje veux une vraie assistante au bout du fil\b",r"\bce robot ne me convient pas\b",
  r"\barrêtez le chatbot\b",r"\bpas ce chat\b",r"\bpas à un robot\b",r"\bmerci de ne plus utiliser le chatbot\b",
  r"\bmerci de passer au mode humain\b",r"\best-ce que je peux joindre quelqu’un en direct\b",r"\bpas d’IA\b",
    r"\b(parler|discuter|échanger).*?\b(avec|à)\s+une\s+secrétaire\b",
    r"\b(parler|discuter|échanger).*?\b(avec|à)\s+une\s+assistante\b",
    r"\b(parler|discuter|échanger).*?\b(avec|à)\s+une\s+collaboratrice\b",
    r"\b(parler|discuter|échanger).*?\b(avec|à)\s+un\s+collaborateur\b",
    r"\b(transférer|passer|rediriger).*?\b(à|vers)\s+une\s+secrétaire\b",
    r"\b(transférer|passer|rediriger).*?\b(à|vers)\s+une\s+assistante\b",
    r"\b(transférer|passer|rediriger).*?\b(à|vers)\s+une\s+collaboratrice\b",
    r"\b(transférer|passer|rediriger).*?\b(à|vers)\s+un\s+collaborateur\b",
    r"\b(joindre|contacter).*?\b(le|la)\s+(secrétariat|secrétaire|assistante|collaboratrice|collaborateur)\b",
    r"\b(acceder|avoir accès).*?\b(à|au)\s+(secrétariat|à une secrétaire|à une assistante)\b",
    r"\b(je veux|je souhaite).*?\b(parler|joindre|contacter).*?\b(une|un)\s+(secrétaire|assistante|collaborateur|collaboratrice)\b",
    r"\b(parler|discuter|échanger|voir|appeler|contacter|joindre).*?\b(avec|à)\s+(une|la)\s+(secrétaire|assistante|collaboratrice)\b",
    r"\b(parler|discuter|échanger|voir|appeler|contacter|joindre).*?\b(avec|à)\s+(un|le)\s+(collaborateur)\b",
    r"\b(transférer|passer|rediriger|mettre en relation|me passer).*?\b(à|vers)\s+(une|la)\s+(secrétaire|assistante|collaboratrice)\b",
    r"\b(transférer|passer|rediriger|mettre en relation|me passer).*?\b(à|vers)\s+(un|le)\s+(collaborateur)\b",
    r"\b(je veux|je souhaite|j’aimerais|je désire|il me faut|je préfère).*?\b(parler|échanger|joindre|voir|contacter).*?\b(une|un|la|le)\s+(secrétaire|assistante|collaborateur|collaboratrice)\b",
    r"\b(joindre|contacter|appeler|voir).*?\b(le|la)\s+(secrétariat|secrétaire|assistante|collaboratrice|collaborateur)\b",
    r"\b(acceder|avoir accès|être mis en relation|obtenir un contact).*?\b(à|au)\s+(secrétariat|à une secrétaire|à une assistante|à un collaborateur)\b",
    r"\b(est-ce que|est-il possible|puis-je|serait-il possible).*?\b(parler|joindre|échanger).*?\b(avec|à)\s+(une|un)\s+(secrétaire|assistante|collaborateur|collaboratrice)\b",
    r"\b(parler|joindre|échanger).*?\b(une|un)\s+(personne|humain|interlocuteur|agent)\b.*?\b(pas un robot|vraie personne|en direct)\b"
]
patterns = [re.compile(p, re.IGNORECASE) for p in human_assistant_keywords]
def is_human_assistant_request(text: str) -> bool:
    text_norm = text.lower()
    return any(p.search(text_norm) for p in patterns)
  
def classify_sentence(sentence):
    prompt = f"""Votre rôle est d'identifier si la phrase d'un utilisateur demande explicitement à être redirigé vers un humain (assistant médical ou secrétariat) et non vers un agent automatisé (robot). 
Exemples de requêtes pertinentes :  
- « Puis-je parler à une personne réelle ? »  
- « Je souhaite être mis en contact avec le secrétariat »  
- « Est-il possible d'avoir un assistant en direct ? »  
Phrase à analyser : {sentence}  
Répondez uniquement par `True` ou `False`, sans commentaire ni ponctuation supplémentaire.
""" 
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        temperature=0.3,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    classification = (response.choices[0].message.content).strip().lower()
    logging.info(f"le résultat du llm est {classification}")
    return 'true' in classification


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
        if is_human_assistant_request(query) :
            logging.info("is_human_assistant_request-->True")
            result = True
        else :
              result = classify_sentence(query)
              
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
