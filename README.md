
# 🤖 Chatbot FURIOSO — FURIA Esports (CS:GO)

Este é um chatbot interativo criado com Flask para fornecer informações sobre o time profissional de CS:GO **FURIA Esports**. O chatbot responde perguntas sobre jogadores, lineup, calendário de partidas, história da furia, e muito mais, com base em dados da API da [PandaScore](https://developers.pandascore.co/) e utilizando NLP via [Cohere](https://docs.cohere.com/).
- Esta aplicação está online. Acesse(https://challenge-furia.onrender.com)
---

## 📁 Estrutura do Projeto

```
CHALLENGE_FURIA/
├── front/
│   └── styles.css               # Estilos das paginas
│   └── index.html               # Interface do chat com o usuário
│   └── metrics.html             # Interface dos graficos 
│   └── script.js                # Conexão com o back-end, funções visuais e outros
├── logs/
│   └── main.logs                # Armazena os logs da main para entender melhor como o código está funcionando.
│    
├── main.py                      # Código principal Flask do backend
├── db_actions.py                # Funções auxiliares para realizar operações comuns no banco de dados.
├── db.py                        # Controlar as conexões do banco de dados -> MAXIMO 10 SIMULTANEAS
├── create_if_not_exists.py      # Criar as tabelas se não existir
├── reset.py                     # Reset nas métricas para sair da dependencia do cronjob -> verificação da validade das métricas e atualização se necessário.
├── requirements.txt             # Dependências do projeto
├── Procfile                     # Indica como o servidor deve iniciar o projeto
├── .env                         # Váriaveis ambientes -> Modelo segue no (.env-sample)
├── requirements.txt             # Dependências do projeto
└── README.md                    # Documentação do projeto
```

---

## 🚀 Como Executar (LOCALMENTE) -- Garanta que você tenha python instalado.

1. **Clone o repositório:**

```bash
git clone https://github.com/r0ssik/CHALLENGE_FURIA.git
cd CHALLENGE_FURIA
```

2. **Crie um ambiente virtual e ative-o (recomendado):**

```bash
python -m venv venv
source venv/bin/activate #ou venv\Scripts\activate no Windows
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

5. **Crie um banco de dados com qualquer nome**

6. **Configure as variáveis de ambiente:**

Crie um arquivo `.env` com as chaves da API e conexão com o seu banco de dados:
(Para conseguir as chaves de API acesse [PandaScore](https://developers.pandascore.co/) e [Cohere](https://docs.cohere.com/).)

```
token_princ=            #[PandaScore](https://developers.pandascore.co/)
ID_FURIA=124530
COHERE_API_KEY=         #[Cohere](https://docs.cohere.com/

DB_NAME=banco_que_você criou
DB_HOST=localhost
DB_SENHA= 
DB_USER=root
```

7. **Altere o JS:**

- Para executar localmente, peço que troque a linha 19 e 81 do código (front/script.js) para se conectar com o back localhost e não com o do onrender. Caso queira usar a do onrender não tem problema, mas acredito que seu ip pode ser bloqueado. (Eu não troco pois a versão do git é a que fica online no onrender)

```bash
TROQUE const response = await fetch('https://challenge-furia.onrender.com/chat',  POR  const response = await fetch('http://localhost:5000/chat',
E const response = await fetch('https://challenge-furia.onrender.com/metrics'); POR const response = await fetch('http://localhost:5000/metrics',
```

8. **Execute a aplicação:**

```bash
python main.py
```

9. **Abra o projeto:**
- Abra o projeto no localhost ou diretamente no (front/index.html) e explore as funcionalidades.

---

## 💡 Funcionalidades

- 🎮 **Informações sobre a FURIA Esports** (história, títulos, curiosidades)
- 📅 **Calendário e partidas** usando a API do PandaScore
- 🧠 **Respostas com IA** via Cohere para perguntas abertas
- 📝 **Registro de perguntas não respondidas** para análise posterior
- 📱 **desktop e mobile**

---

## ⚙️ Como Funciona a Ferramenta

O sistema segue um fluxo simples porém robusto:

1. **Interface Web (Frontend)**: O usuário interage com o chatbot por meio de uma interface HTML/CSS.
2. **Processamento da Pergunta (Backend)**: A pergunta é enviada ao servidor Flask, que identifica se ela é respondível diretamente pelos caminhos criados já no CHatBOT ou precisa de uma análise mais profunda.
3. **Uso de NLP com Cohere**: Se a pergunta for mais aberta ou contextual, é usada a API da Cohere para interpretar e gerar uma resposta adequada. Caso já aja uma resposta pre-definida pelo bot, o cohere pega esta resposta e deixa mais coerente com a pergunta em si.
4. **Retorno e Exibição**: A resposta é enviada de volta ao navegador e exibida no chat.
5. **Tipo de Pergunta**: O tipo de pergunta é salvo no banco de dados, e essas métricas são mostradas na pagina de métricas(Os tipos de perguntas são as predefinidas pelo bot, no caso de perguntas abertas elas são guardadas como IA_HANDLES).
6. **IA-HANDLES**: As perguntas sem resposta prévia é guardada como I.A - HANDLE e salva no bd(bot_questions_not_answered) para análise de implementações futuras(uma tela de visualização dessas perguntas foi desenvolvida, porém descartada ao longo do processo das ideas de MVP -> No futuro as implementações de BD abrem um leque para melhor entendimento do fã, batendo também um pouco com o challenge #2 do processo seletivo da FURIA).
7. **Métricas**: Sempre que a main é acessada, as métricas são verificadas com base no last-update, optei por essa abordagem pois hospedei no servidor onrender, e no plano gratuido eu não tinha acesso a cronjob, nem a banco de dados, por isto o banco de dados é da hostinger.
   

---
## ✨ Frontend

- HTML + CSS customizado com responsividade
- Interface amigável inspirada em dark mode
- Scroll automático para mensagens
- Ícones, botões e animações leves

---

## 🔧 Backend

- **Flask** para rotas e controle do chat
- API da **PandaScore** para dados em tempo real
- Integração com **Cohere** para compreensão de linguagem natural
- Integração com o banco de dados relacionais **MySQL* para análise de métricas.

---

## 🧪 Exemplos de Uso

> **Usuário**: Quem são os jogadores da FURIA?  
> **Bot**: O lineup principal conta com FalleN, KSCERATO...

---

## 📱 Design

- **Desktop**: altura fixa, sem rolagem do body (`overflow: hidden`)
- **Mobile**: altura flexível com `overflow: auto` e rolagem ativada
- Controle via media queries no CSS (`max-width: 768px`)

---

## 🧩 Tecnologias Usadas

- Flask
- HTML/CSS puro
- Cohere API (NLP)
- PandaScore API (dados de esportes eletrônicos)
- Banco de Dados -> MYSQL

---

## ✅ Próximos Passos (To-Do)

- [ ] Implementar feedback de usuário para respostas ruins.
- [ ] Suporte a múltiplos jogos (Valorant, Kings League, etc.).
- [ ] Adicionar testes unitários e de integração.
- [ ] Aumentar a capacidade do bot em geral.
- [ ] Melhorar o sistema de métricas de perguntas mais feitas.
- [ ] Melhorar o sistema de captação de perguntas que geraram I.A - HANDLE(Encontrar melhor os padrões).

---

## 📄 Licença

- Este projeto foi feito para um processo seletivo da FURIA ESPORTS em Estágio em Engenharia de Software ou Assistente em Desenvolvimento de Software. Este projeto será usado apenas com o propósito de avalição do candidato e nada mais.
- Este projeto é de autoria do dono deste repositória, Gabriel Rodrigues Rossik, e demorou cerca de 11 horas para o desenvolvimento, até agora.
