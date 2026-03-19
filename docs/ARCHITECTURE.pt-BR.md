# Arquitetura do FluxBuddy

## Objetivo

FluxBuddy é um core open source para bots de fluxo de trabalho com:

- roteamento limpo
- carregamento dinâmico de módulos
- event bus interno
- integração inicial com Telegram
- base neutra de domínio

O core não deve conter nenhuma regra específica de posto, combustível, Telnet ou qualquer outro domínio de negócio.

## O que entra no MVP

- Telegram como primeiro canal
- abstração para múltiplos canais no futuro
- router interno para comandos
- event bus para comunicação entre módulos
- scheduler centralizado para jobs recorrentes
- autorização centralizada com papéis `viewer`, `operator` e `admin`
- logging centralizado com limite de tamanho
- healthcheck restrito a admins
- exemplos neutros de módulos

## O que não entra no core

- integrações de domínio específico
- dependências espalhadas em módulos
- acesso direto dos módulos ao `.env`
- registro manual de handlers Telegram por módulo
- import entre módulos

## Estrutura pensada

```text
main.py
core/
transports/
modules/
shared/
docs/
prompt.md
```

## Papel do core

### Router

- registra comandos declarados por módulos
- impede conflito de comando duplicado
- despacha para o módulo responsável
- mede latência e registra sucesso ou erro

### Event bus

- publica eventos internos
- permite listeners assíncronos
- isola falhas de listener

### Scheduler

- recebe jobs declarados por módulos
- executa com proteção contra falha
- registra início, fim e erro

### Registro central de dependências

- concentra logger, settings, clientes e serviços compartilhados
- impede cada módulo de criar sua própria infraestrutura

## Contrato de módulo

Cada módulo poderá declarar:

- comandos
- listeners de evento
- jobs agendados
- hooks de startup e shutdown

Cada módulo não poderá:

- importar outro módulo
- ler `.env` diretamente
- criar logger próprio
- criar scheduler próprio
- registrar handlers Telegram diretamente
- instalar dependências fora do fluxo central do projeto

## Carregamento dinâmico

Cada pasta de módulo deve conter:

- `plugin.json`
- `module.py`

O loader do core deve validar o manifesto, importar o entrypoint e registrar somente módulos válidos.

## Segurança

- allowlist configurável por `.env`
- três níveis de permissão
- healthcheck apenas para admin
- logs sem tokens e sem conteúdo completo de mensagens privadas

## Observabilidade

Registrar em log:

- startup
- shutdown
- comando recebido
- módulo responsável
- latência
- job iniciado e concluído
- falha de handler, listener e job
- ações administrativas

## Módulos exemplo do MVP

- `status`: comando `/status`
- `occurrences`: exemplo neutro de alerta por leitura recorrente
- `deadlines`: exemplo neutro de vencimentos ou lembretes

## Ordem de entrega

1. documento de arquitetura
2. validação
3. scaffold do core
4. adapter Telegram
5. loader dinâmico
6. módulo `status`
7. módulos exemplo

## Critérios de validação

Validar se:

- o core está neutro
- o contrato de módulo está claro
- o carregamento dinâmico é o padrão certo
- o event bus é a base de crescimento desejada
- dependências centralizadas são obrigatórias
