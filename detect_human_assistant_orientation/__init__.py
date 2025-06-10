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
    r"\b(je\s+ne\s+veux\s+pas|j'en\s+ai\s+marre\s+de)\s+(parler|discuter|echanger)\s+(a|avec)\s+(un|ce|votre)\s+(robot|chatbot|ia|machine|automate|assistant\s+automatise)\b",
    r"\b(stop|arretez|arreter|terminer|quitter|finir)\s+(le|ce)?\s*(robot|chatbot|chat)\b",
    r"\b(je\s+refuse)\s+l'assistance\s+automatisee\b",
    r"\bce\s+(robot|chatbot)\s+ne\s+me\s+convient\s+pas\b",
    r"\b(pas|non)\s+(a|avec)\s+(un|une)\s+(robot|machine|ia|chatbot)\b",
    r"\b(passer|transferer|rediriger|me\s+mettre\s+en\s+relation\s+avec|me\s+passer)\s+(a|au|vers|le|la)\s+(un|une)?\s*(secretariat|secretaire|assistante|accueil|standard|collaborateur|collaboratrice)\b",
    r"\b(joindre|contacter|avoir)\s+(le|la|un|une)\s+(secretariat|secretaire|assistante)\b",
    r"\b(?:pas|sans)\s+(?:un\s+robot|chatbot|IA|automatisation|machine)\b",
    r"\b(?:refuser|rejeter)\s+l['’]assistance\s+automatique\b",
    r"\b(?:transf[éeè]rer|passer|rediriger|mettre\s+en\s+relation)\s+(?:moi\s+)?(?:vers|à)\s+(?:une\s+)?(?:secr[éeé]taire|assistant[e]?|collaborateur|collaboratrice)\b",
    r"\b(?:joindre|contacter|voir)\s+(?:le\s+)?(?:secr[éeé]tariat|(?:un|une)\s+(?:r[éeé]f[éeé]rent[e]?|agent)\s+humain)\b",
    r"\b(?:est-ce\s+que|est-il\s+possible|comment|o[ùu])\s+[\w\s]*?\b(?:joindre|contacter|parler)\s+[àa]\s+une\s+personne\b",
    r"\bpuis-je\s+(?:être\s+mis\s+en\s+relation|parler)\s+avec\s+un\s+humain\s?\?",
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
Répondez uniquement par `True` ou `False`, sans commentaire ni ponctuation supplémentaire.

Exemples de requêtes pertinentes (doivent retourner True) :
- « Puis-je parler à une personne réelle ? »
- « Je souhaite être mis en contact avec le secrétariat »
- « Est-il possible d'avoir un assistant en direct ? »
- "Je ne veux pas parler à un robot."
- "Puis-je joindre quelqu’un en direct ?"

Exemples de requêtes non pertinentes (doivent retourner False) :
- "Quelle est l'heure d'ouverture ?"
- "Prenez-vous des rendez-vous ?"
- "Quel est votre adresse ?"

Phrase à analyser : {sentence}
"""
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        temperature=0.2,
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
