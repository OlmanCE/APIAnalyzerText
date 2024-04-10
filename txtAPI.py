from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
from google.cloud import language_v2
import json
import re

def sample_classify_text(input_data):
    """
    Classifying Content in a String or JSON

    Args:
      input_data: A dictionary with the structure {"description": "text to analyze"}.
    """

    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    # Initialize the Google Cloud client
    client = language_v2.LanguageServiceClient()
    # Extract text_content from input_data
    text_content = input_data.get("description", "")
    print(text_content)
    # Define document type and language
    type_ = language_v2.Document.Type.PLAIN_TEXT
    document = {"content": text_content, "type": type_}
    # Specify model version for content categorization

    response = client.classify_text(request={'document': document})

    # Process and return the response categories
    # Get the name of the category representing the document.
    # See the predefined taxonomy of categories model 2:
    # https://cloud.google.com/natural-language/docs/categories
    categories = [{"name": category.name, "confidence": category.confidence} for category in response.categories]
    return categories


def txt_to_json_messages_only(filepath, lang='auto'):
    """
    Modifica el archivo de texto de WhatsApp o JSON preprocesado en una estructura JSON que contiene solo los mensajes.
    
    Args:
    - filepath: Ruta del archivo a convertir.
    - lang: Idioma del chat ('auto', 'en', 'es'). 'auto' intentará detectar el idioma automáticamente.
    
    Returns:
    - Una cadena JSON representando el contenido de los mensajes en el formato {"description": "texto completo"}.
    """
    messages = []
    
    if lang == 'auto':
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                if "end-to-end encrypted" in line:
                    lang = 'en'
                    break
                elif "cifrado de extremo a extremo" in line:
                    lang = 'es'
                    break
    
    # Actualizado para capturar ambos formatos de fecha: 'dd/mm/yy' y 'm/dd/yy'
    pattern = {
        'en': r'(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}\s[ap]m) - (.*?): (.*)',
        'es': r'(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}\s[a|p]\.m\.) - (.*?): (.*)'
    }[lang if lang in ['en', 'es'] else 'en']
    
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(pattern, line)
            if match:
                _, _, _, message = match.groups()
                if "end-to-end encrypted" not in message and "cifrado de extremo a extremo" not in message and "<Media omitted>" not in message:
                    messages.append(message.replace("<This message was edited>", "").strip())
    
    # Concatenar todos los mensajes en un único string
    conversation = ' '.join(messages)
    # Devolver el contenido en el formato esperado
    return json.dumps({"description": conversation}, ensure_ascii=False, indent=2)
# Llamada a la función txt_to_json_messages_only
# txt_to_json_messages_only('ruta_del_archivo.txt')
app = Flask(__name__)

@app.route('/analyze_chat', methods=['POST'])
def analyze_chat():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        if file.filename.endswith('.txt'):
            # Procesa archivo .txt y lo convierte en un diccionario Python
            processed_content = json.loads(txt_to_json_messages_only(tmp.name))
        elif file.filename.endswith('.json'):
            # Lee el contenido JSON directamente
            with open(tmp.name, 'r', encoding='utf-8') as f:
                processed_content = json.load(f)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

    # Realiza la clasificación del texto
    categories = sample_classify_text(processed_content)

    # Limpia el archivo temporal
    os.unlink(tmp.name)

    return jsonify({'categories': categories})

if __name__ == '__main__':
    app.run(debug=True)