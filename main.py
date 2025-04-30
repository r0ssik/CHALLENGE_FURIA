from flask import Flask, request, jsonify, redirect
import requests
import os
import logging
from dotenv import load_dotenv
import unicodedata
import re
import json
from datetime import datetime
from flask_cors import CORS
from db_actions import update_question_metrics,  save_unanswered_question #Função própria
from db import get_connection
from reset import reset_metrics_if_needed
import cohere
from create_if_not_exists import criar_tabelas





app = Flask(__name__, static_folder='front', static_url_path='/front')
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


cohere_api_key = os.getenv("COHERE_API_KEY")
cohere_client = cohere.Client(cohere_api_key)


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
    reset_metrics_if_needed()
    return redirect('/front/index.html')


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            logging.warning("Requisição inválida recebida.")
            return error_response("Requisição inválida. Verifique o formato enviado.", 400)

        user_message = normalize_text(data.get('message', ''))
        original_message = data.get('message', '')
        keywords_presentation = ['oi', 'oii', 'oiii', 'oiiii', 'tudobem', 'tudo bem']
        keywords_team = ['time', 'team', 'furia']
        keywords_players = ['jogador', 'player', 'jogadores', 'players']
        keywords_contacts = ['contatar', 'contato', 'contact', 'redes', 'social', 'rede', 'instagram', 'linkedin', 'X', 'Twitter', 'insta']
        keywords_matches = ['jogo', 'partida', 'match', 'calendario', 'calendar', 'partidas', 'jogos', 'matches']
        keywords_players_espec = get_cleaned_player_names()

        if any(word in user_message for word in keywords_team):
            resposta = get_team_info()
        elif any(word in user_message for word in keywords_presentation):
            resposta = 'Oii, eu sou o FURIOSO, ajudante da FURIA, com o que posso ajudar? pergunte sobre o time, os jogadores, jogadores específicos do time, calendário, contatos da fúria e sobre as partidas, estou aqui para ajudar!.'
        elif any(word in user_message for word in keywords_players_espec):
            resposta = get_players_info(user_message)
        elif any(word in user_message for word in keywords_players):
            resposta = get_players_info(user_message)
        elif any(word in user_message for word in keywords_contacts):
            resposta = get_contacts()
        elif any(word in user_message for word in keywords_matches):
            resposta = get_upcoming_matches()
        else:
            logging.info(f"Mensagem não entendida: {user_message}")
            save_unanswered_question(original_message)
            update_question_metrics("IA_HANDLE")
            resposta_bruta = generate_ai_response(original_message)
            resposta = refine_response_with_ai(original_message, resposta_bruta)
            return success_response(resposta, "Resposta da IA aprimorada.")

        # Se quiser refinar todas as respostas, ative esta linha:
        resposta = refine_response_with_ai(original_message, resposta)

        return success_response(resposta, "Resposta enviada.")

    except Exception as e:
        logging.error(f"Erro no /chat: {e}")
        return error_response("Erro interno no servidor.", 500)


@app.route('/metrics')
def metrics():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT name_question, X_DIA, X_MES, X_ANO, X_GERAL 
            FROM bot_questions
        """)
        data = cursor.fetchall()

        
        return jsonify(data), 200

    except Exception as e:
        logging.error(f"Erro ao buscar métricas: {e}")
        return error_response("Erro ao buscar métricas")
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()



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
        return f"O time {name}, foi criado na região {location}, e atualmente conta com o número de {quantidade_de_player} players."
    
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
        response = requests.get(
            f"https://api.pandascore.co/csgo/matches/upcoming?filter[opponent_id]={ID_FURIA}",
            headers=headers
        )
        response.raise_for_status()
        response_json = response.json()

        if not response_json:
            message = get_last_match()
            return f"Não há partidas futuras agendadas para a FURIA. {message}"

        mensagens = []
        for partida in response_json:
            opponents = partida.get("opponents", [])
            if len(opponents) < 2:
                time1 = opponents[0]["opponent"]["name"] if opponents else "TBD"
                time2 = "TBD"
            else:
                time1 = opponents[0]["opponent"]["name"]
                time2 = opponents[1]["opponent"]["name"]

            data = partida.get("begin_at", "Data não disponível")
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

def generate_ai_response(message):
    try:
        prompt = (
            "Você é um especialista no time FURIA tanto e-sports quanto sports normal e também um torcedor da furia."
            "Responda sempre em português de forma clara, precisa e objetiva. "
            f"Pergunta do usuário: {message}"
        )
        response = cohere_client.chat(message=prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Erro na Cohere: {e}")
        return "Desculpe, tive um problema para pensar em uma resposta agora."

def refine_response_with_ai(pergunta, resposta_gerada):
    try:
        prompt = (
            "Você é um especialista em FURIA tanto e-sports quanto sports normal, você também um torcedor da furia e seu trabalho é melhorar a coerência entre perguntas e respostas. "
            "Recebe uma pergunta e uma resposta preliminar, e deve reescrever a resposta para que faça mais sentido com a pergunta, "
            "mantendo tudo em português e focado no contexto da FURIA. Você deve deixar apenas a respostas sem apontar outras coisas, como se tivesse conversando com um fã\n\n"
            f"Pergunta: {pergunta}\n"
            f"Resposta preliminar: {resposta_gerada}\n\n"
            "Resposta aprimorada:"
        )
        response = cohere_client.chat(message=prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Erro ao refinar resposta com Cohere: {e}")
        return resposta_gerada  



if __name__ == '__main__':
    criar_tabelas()
    app.run()
