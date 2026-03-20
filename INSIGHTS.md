# Telegram Bot Modular – Lembretes e Automatizações

Bot para Telegram que começa simples (lembretes de prazos via CSV) e pode crescer bastante com módulos novos criados por IA.

A grande sacada está no arquivo **PROMPT.md**: ele serve de molde para a IA gerar módulos novos que respeitam a arquitetura do projeto, sem quebrar o que já existe.

## Instalação e uso básico (PT-BR)

- Instale Python 3.11 ou superior (de preferência 3.13)
- Tenha Telegram instalado (app ou web)

1. Crie seu bot  
   Procure **@BotFather** no Telegram → /start → siga os passos para criar o bot → salve o **TOKEN** com segurança (só você deve ter acesso)

2. Pegue seu ID de usuário  
   Procure exatamente **@userinfobot** (cuidado com bots parecidos) → /start → ele te mostra seu ID numérico

3. (Opcional) ID de grupo  
   Crie um grupo → adicione **@getidsbot** → ele te passa o ID do grupo (vai ser um número negativo)

4. Configure o projeto  
   Rode o `setup.bat` (ele instala as dependências e cria o .env)  
   Abra o arquivo **.env** e coloque:  
   - Seu TOKEN do bot  
   - Seu ID de usuário (para receber mensagens privadas)

5. Teste o módulo de deadlines  
   Rode o bot  
   Envie o comando `/deadline` para ele  
   Ele lê o arquivo .csv de prazos e mostra quanto tempo falta para cada vencimento

### Exemplo de deadlines.csv (salve com separador ; )

Copie o conteúdo abaixo e salve como `deadlines.csv`:

    DATE;DESCRIPTION
    31/03/2026;Pagamento da parcela de março/2026 - financiamento veículo
    07/04/2026;Vencimento da fatura do cartão de crédito (ciclo fechamento 25/03)
    15/04/2026;Declaração pré-preenchida IRPF 2026 disponível (estimado)
    30/04/2026;Prazo final DIRF 2026 (informações de 2025)
    10/05/2026;Vencimento IPTU 2026 - 1ª parcela Colatina/ES (estimado)
    20/06/2026;Pagamento IPVA 2026 - placa final 5 - 1ª cota única ou 1ª parcela
    05/07/2026;DARF mensal IRPJ/CSLL - estimativa junho/2026

No .env, configure assim:
(tire o "#" da frente das linhas que quer usar):

DEADLINES_FILE_PATH=deadlines.csv
DEADLINES_DATE_COLUMN=DATE
DEADLINES_DESCRIPTION_COLUMN=DESCRIPTION
DEADLINES_CSV_SEPARATOR=;
DEADLINES_CSV_ENCODING=utf-8-sig
DEADLINES_ALERT_DAYS=30
DEADLINES_ALERT_TIME=09:10

textLembre: o caminho do arquivo é sem aspas e o "#" comenta a linha — se deixar comentado, não funciona.

### Por que vale a pena continuar esse projeto

O módulo de deadlines é simples, mas já mostra o potencial.  
Com o tempo dá pra fazer coisas bem legais, tipo:

- Monitorar logins suspeitos em redes/email e alertar na hora
- Ler arquivos ou fotos que outras pessoas mandam no grupo
- Pegar dados de sensores (nível de tanque, medidor de litros, etc.) e mandar no Telegram
- Alertas de preço de insumos, dólar, combustível
- Qualquer coisa que você imaginar e conseguir descrever bem no PROMPT.md

O projeto foi feito exatamente pra crescer assim: módulo por módulo, com risco baixo de quebrar tudo.

---

# EN – Installation & Quick Start

- Install Python 3.11+ (best: 3.13)
- Use Telegram (app or web)

1. Create your bot  
   Talk to **@BotFather** → /start → create new bot → save the **TOKEN** safely

2. Get your User ID  
   Message **@userinfobot** → /start → copy your numeric ID

3. (Optional) Group ID  
   Add **@getidsbot** to a group → it gives you the group Chat ID

4. Setup  
   Run `setup.bat` → it installs dependencies and creates .env  
   Edit **.env** with:  
   - Your bot TOKEN  
   - Your user ID

5. Test  
   Start the bot  
   Send `/deadline` → it reads deadlines.csv and shows time left for each entry

### deadlines.csv example (save with ; separator)

Copy the content below and save as `deadlines.csv`:

    DATE;DESCRIPTION
    31/03/2026;Vehicle financing installment - March 2026
    07/04/2026;Credit card bill due (closing cycle 25/03)
    15/04/2026;Pre-filled IRPF 2026 available (estimated)
    30/04/2026;Final deadline DIRF 2026 (2025 info)
    10/05/2026;IPTU 2026 due - 1st installment Colatina/ES (estimated)
    20/06/2026;IPVA 2026 payment - plate ending 5 - 1st single quota or 1st installment
    05/07/2026;Monthly DARF IRPJ/CSLL - June 2026 estimate

Set in .env (remove # from lines you want):
DEADLINES_FILE_PATH=deadlines.csv
DEADLINES_DATE_COLUMN=DATE
DEADLINES_DESCRIPTION_COLUMN=DESCRIPTION
DEADLINES_CSV_SEPARATOR=;
text### Why keep building this

The deadline module is just the beginning.  
Future ideas: suspicious login alerts, file/photo parsing from group, IoT sensor data, price tracking, etc.

The real power is **PROMPT.md** — it lets AI create new modules that fit perfectly into the existing structure, so the bot can grow safely and creatively.
