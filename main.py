from flask import Flask, request, jsonify
import requests
import os
import logging
from dotenv import load_dotenv
import unicodedata
import re
import json
from datetime import datetime
from flask_cors import CORS
from db_actions import update_question_metrics #Função própria




app = Flask(__name__)
CORS(app)

# Configurações gerais
load_dotenv(".env")
url_principal = "https://api.pandascore.co/csgo/teams?filter[name]=FURIA"
TOKEN = os.getenv("token_princ")
ID_FURIA = os.getenv("ID_FURIA")
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

# Configuração de logs
log_folder = 'logs'
os.makedirs(log_folder, exist_ok=True)
log_file_name = os.path.splitext(os.path.basename(__file__))[0] + '.log'
log_path = os.path.join(log_folder, log_file_name)

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



def success_response(data, message="Success"):
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    }), 200

def error_response(message="An error occurred", status_code=400):
    return jsonify({
        "status": "error",
        "message": message,
        "data": None
    }), status_code

@app.route('/')
def home():
    return """
    <h1>Chatbot da FURIA - Bem-vindo! 🔥</h1>
    <p>Você pode perguntar sobre:</p>
    <ul>
      <li>Informações sobre o time</li>
      <li>Lista dos jogadores atuais</li>
      <li>Detalhes específicos de um jogador (depois de listar)</li>
      <li>Próximos jogos e torneios</li>
      <li>Contatos e redes sociais oficiais</li>
    </ul>
    <p>Envie suas mensagens para o endpoint <b>/chat</b> via método POST (Content-Type: application/json).</p>
    """

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            logging.warning("Requisição inválida recebida.")
            return error_response("Requisição inválida. Verifique o formato enviado.", 400)

        user_message = normalize_text(data.get('message', ''))
        keywords_presentation = ['oi', 'oii', 'oiii', 'oiiii', 'tudobem', 'tudo bem']
        keywords_team = ['time', 'team']
        keywords_players = ['jogador', 'player', 'jogadores', 'players']
        keywords_contacts = ['contato', 'contact', 'redes', 'social', 'rede', 'instagram', 'linkedin', 'X', 'Twitter', 'insta']
        keywords_matches = ['jogo', 'partida', 'match', 'calendario', 'calendar']
        keywords_players_espec = get_cleaned_player_names()

        if any(word in user_message for word in keywords_team):
            return success_response(get_team_info(), "Informações do time enviadas.")
        elif any(word in user_message for word in keywords_presentation):
            return success_response('Oii, eu sou o FURIOSO, ajudante da FURIA, com o que posso ajudar? pergunte sobre o time, os jogadores, jogadores especificos do time, calendário, contatos da fúria e sobre as partidas, estou aqui para ajudar!.', "apresentação enviada")
        elif any(word in user_message for word in keywords_players_espec):
            return success_response(get_players_info(user_message), "Informações específicas de jogador enviadas.")
        elif any(word in user_message for word in keywords_players):
            return success_response(get_players_info(user_message), "Lista de jogadores enviada.")
        elif any(word in user_message for word in keywords_contacts):
            return success_response(get_contacts(), "Contatos da FURIA enviados.")
        elif any(word in user_message for word in keywords_matches):
            return success_response(get_upcoming_matches(), "Próximos jogos enviados.")
        else:
            logging.info(f"Mensagem não entendida: {user_message}")
            return success_response("Não entendi, pode repetir?", "Mensagem não reconhecida.")

    except Exception as e:
        logging.error(f"Erro no /chat: {e}")
        return error_response("Erro interno no servidor.", 500)

def get_team_info():
    try:
        response = requests.get(url_principal, headers=headers)
        response.raise_for_status()
        response_json = response.json()

        location = response_json[0]['location']
        name = response_json[0]['name']
        quantidade_de_player = len(response_json[0]['players'])

        logging.info("Informações do time obtidas com sucesso.")
        update_question_metrics("TEAM_INFO")
        return f"O time {name}, foi criado na região {location}, e atualmente conta com o número de players {quantidade_de_player}."
    
    except Exception as e:
        logging.error(f"Erro ao obter informações do time: {e}")
        raise

def get_players_info(user_message):
    try:
        update_question_metrics("PLAYER_INFO")
        response = requests.get(url_principal, headers=headers)
        response.raise_for_status()
        response_json = response.json()

        jogadores = {i['name'].lower(): i for i in response_json[0]['players']}

        for nome_jogador in jogadores.keys():
            if nome_jogador in user_message:
                jogador = jogadores[nome_jogador]
                logging.info(f"Informações do jogador {jogador['name']} obtidas com sucesso.")
                return f"{jogador['name']} é um jogador da FURIA. Ele possui {jogador['age']} anos, nacionalidade {jogador['nationality']}, nome verdadeiro {jogador['first_name']} {jogador['last_name']} e faz aniversário em {jogador['birthday']}."

        lista_nomes = ", ".join([j['name'] for j in response_json[0]['players']])
        
        return f"Os jogadores atuais da FURIA são: {lista_nomes}. Para saber mais sobre um jogador, envie uma mensagem mencionando o nome!"

    except Exception as e:
        logging.error(f"Erro ao obter informações dos jogadores: {e}")
        raise

def get_contacts():
    try:
        update_question_metrics("CONTACTS")
        result = {
            "linkedin": "https://www.linkedin.com/company/furiagg/",
            "instagram": "https://www.instagram.com/furiagg/?hl=pt-br",
            "X": "https://x.com/FURIA",
            "Central": "https://www.furia.gg/Formulario"
        }
        logging.info("Contatos da FURIA obtidos com sucesso.")
        
        return f"Instagram: {result['instagram']}, LinkedIn: {result['linkedin']}, X(Twitter): {result['X']}, Central de atendimento: {result['Central']}."

    except Exception as e:
        logging.error(f"Erro ao obter contatos: {e}")
        raise

def get_upcoming_matches():
    try:
        update_question_metrics("MATCHES")
        response = requests.get(f"https://api.pandascore.co/csgo/matches/upcoming?filter[opponent_id]={ID_FURIA}", headers=headers)
        response.raise_for_status()
        response_json = response.json()

        if not response_json:
            message = get_last_match()
            return f"Não há partidas futuras agendadas para a FURIA. {message}"

        mensagens = []
        for partida in response_json:
            time1 = partida['opponents'][0]['opponent']['name']
            time2 = partida['opponents'][1]['opponent']['name']
            data = partida['begin_at']
            mensagens.append(f"Partida: {time1} vs {time2} em {data}")

        logging.info("Próximas partidas obtidas com sucesso.")
        return "\n".join(mensagens)

    except Exception as e:
        logging.error(f"Erro ao obter próximas partidas: {e}")
        raise

def get_last_match():
    try:
        response = requests.get(f"https://api.pandascore.co/csgo/matches?filter[opponent_id]={ID_FURIA}", headers=headers)
        response.raise_for_status()
        response_json = response.json()

        if not response_json:
            return "Nenhuma partida encontrada."

        last_match = response_json[0]
        resultado = "positivo para o time furioso, #GoFURIA!" if str(last_match["winner_id"]) == str(ID_FURIA) else "negativo para o time furioso, mas continuaremos firmes. #GoFURIA!"

        partida = last_match['opponents']
        time1 = partida[0]["opponent"]["name"]
        time2 = partida[1]["opponent"]["name"]

        return f"A última partida foi entre {time1} X {time2}, e o resultado foi {resultado}."

    except Exception as e:
        logging.error(f"Erro ao obter última partida: {e}")
        raise

def normalize_text(text):
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'[^a-z0-9\\s]', '', text)
    return text

def get_cleaned_player_names():
    try:
        response = requests.get(url_principal, headers=headers)
        response.raise_for_status()
        response_json = response.json()

        player_names = []
        for player in response_json[0]['players']:
            name_cleaned = player['name'].replace(" ", "").lower()
            player_names.append(name_cleaned)

        return player_names

    except Exception as e:
        logging.error(f"Erro ao obter nomes dos jogadores: {e}")
        raise

if __name__ == '__main__':
    app.run(debug=True)
