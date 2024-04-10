# APIAnalyzerText
Contiene una API que categoriza una conversación de WhatsApp's
Se agrega el archivo requirements que contiene las bibliotecas necesarias
Se debe tener una cuenta de Google, esto para poder crear una cuenta en Google Cloud https://cloud.google.com/?hl=en y hacer uso del servicio Natural Language 
Con la cuenta de Google Cloud lista, se debe crear un proyecto en Google Cloud y que tenga Habilitado el servicio de Google Cloud y autenticarse desde la maquina local, aqui la guia -> https://cloud.google.com/natural-language/docs/setup
Google Cloud ofrece una guia acerca del proceso a seguir para utilizar su servicio Natural Language con Python -> https://cloud.google.com/python/docs/reference/language/latest 
y para este trabajo se implemento el modelo V2 -> https://cloud.google.com/python/docs/reference/language/latest/google.cloud.language_v2.services.language_service.LanguageServiceClient 
Una vez se ha seguido la guia que ofrece Google Cloud, ya se puede hacer uso del archivo txtAPI.py