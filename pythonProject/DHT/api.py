import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail  # Importer send_mail pour l'envoi d'e-mails
from django.conf import settings  # Importer settings pour les configurations d'e-mail
from .serializers import DHT11serialize
from .models import Dht11
from twilio.rest import Client  # Importer la bibliothèque Twilio


# Fonction pour envoyer un message Telegram
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response


# Fonction pour envoyer un message WhatsApp via Twilio
def send_whatsapp_alert():

    account_sid = '#votre account_sid(chercher le dans twilio)'
    auth_token = '#votre token(chercher le dans twilio) '
    # Remplacez par votre token d'authentification Twilio
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body='Il y a une alerte importante sur votre Capteur : la température dépasse le seuil.',
        to='whatsapp:number'  # Remplacez par votre numéro WhatsApp
    )
    return message


# Vue pour gérer les requêtes GET et POST pour les données Dht11
@api_view(["GET", "POST"])
def Dlist(request):
    if request.method == "GET":
        all_data = Dht11.objects.all()  # Récupérer toutes les données
        data_ser = DHT11serialize(all_data, many=True)  # Sérialisation des données
        return Response(data_ser.data)  # Retourner les données en JSON

    elif request.method == "POST":
        serial = DHT11serialize(data=request.data)  # Sérialisation des données envoyées
        if serial.is_valid():
            new_data = serial.save()  # Enregistrer les nouvelles données

            # Vérifier si la température dépasse un seuil (par exemple 10°C)
            if new_data.temp > 10:  # Remplacez 10 par votre seuil
                # Alerte Telegram

                telegram_token = 'YOUR_TELEGRAM_BOT_TOKEN'
                chat_id = 'YOUR_CHAT_ID'
                telegram_message = 'La température dépasse le seuil de 10°C, veuillez intervenir immédiatement pour vérifier et corriger cette situation.'
                send_telegram_message(telegram_token, chat_id, telegram_message)

                # Alerte WhatsApp
                send_whatsapp_alert()

                # Alerte e-mail
                subject = 'Alerte'
                message = 'La température dépasse le seuil de 10°C, Veuillez intervenir immédiatement pour vérifier et corriger cette situation'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = ['email']  # Remplacez par votre e-mail de destination
                send_mail(subject, message, email_from, recipient_list)

            return Response(serial.data, status=201)  # Réponse avec code 201 et données créées
        return Response(serial.errors, status=400)  # Réponse d'erreur si les données sont invalides
