# Automação Inteligente de Grupos Telegram 🤖

Este script automatiza a criação e configuração de grupos no Telegram de forma **inteligente e progressiva**.

## ✨ Funcionalidades Principais

- 🔄 **Criação Progressiva**: Começa criando 5 grupos no 1º dia, 10 no 2º dia, e vai aumentando até 40 grupos por dia
- 📊 **Sistema de Tracking**: Rastreia automaticamente quantos grupos já foram criados
- 🚪 **Saída Automática**: Após criar os grupos, a conta criadora sai automaticamente (sem apagar os grupos)
- ⏰ **Execução Automática Diária**: Configurável para rodar todos os dias automaticamente
- 📁 **Separação de Configurações**: Credenciais da API em arquivo separado para maior segurança

## 📋 Requisitos

- Python 3.7 ou superior
- Conexão com internet
- Número de telefone registrado no Telegram
- Credenciais da API do Telegram

## 🔧 Configuração

### 1. Instale as dependências:
```bash
pip install -r requirements.txt
```

### 2. Obtenha suas credenciais API:
   - Acesse https://my.telegram.org
   - Faça login com seu número
   - Crie um novo aplicativo
   - Copie o `API_ID` e `API_HASH`

### 3. Configure o arquivo `api_credentials.env`:
   ```env
   API_ID=seu_api_id_aqui
   API_HASH=seu_api_hash_aqui
   PHONE_NUMBER=+5511999999999
   ```
   ⚠️ **IMPORTANTE**: Este arquivo contém informações sensíveis. NÃO compartilhe!

### 4. Configure o arquivo `config.env`:
   - Adicione o username do novo proprietário
   - Configure os usernames dos bots
   - Especifique o caminho da foto do grupo
   - Configure a descrição do grupo

### 5. Adicione os nomes dos grupos em `groups.txt`:
   - Um nome por linha
   - Não use linhas vazias

## 🚀 Uso

### Execução Manual:
```bash
python telegram_automation_intelligent.py
```

**Primeira execução:**
- O script detectará automaticamente que você não está autenticado
- Você precisará digitar o código de verificação recebido no Telegram
- Se tiver verificação em duas etapas, digite a senha quando solicitado
- A sessão será salva automaticamente para próximas execuções

**Próximas execuções:**
- O script usará a sessão salva automaticamente
- Não precisará digitar código novamente (a menos que a sessão expire)

### Configuração de Execução Automática Diária:

**Windows:**
```bash
python schedule_daily.py
```

**Linux/Mac:**
Execute `python schedule_daily.py` e siga as instruções para configurar o crontab.

## 📈 Como Funciona a Progressão

- **1º dia**: Cria 5 grupos
- **2º dia**: Cria 10 grupos (total: 15)
- **3º dia**: Cria 15 grupos (total: 30)
- **4º dia**: Cria 20 grupos (total: 50)
- **...continua aumentando...**
- **Máximo**: 40 grupos por dia

O sistema rastreia automaticamente:
- Quantos dias já passaram
- Quantos grupos foram criados em cada dia
- Total de grupos criados
- Próxima execução

## 📁 Estrutura de Arquivos

- `api_credentials.env` - Credenciais da API (separado para segurança)
- `config.env` - Outras configurações (bots, proprietário, etc.)
- `groups.txt` - Lista de nomes dos grupos a criar
- `creation_progress.json` - Rastreamento automático do progresso (criado automaticamente)
- `telegram_automation_intelligent.py` - Script principal de automação
- `authenticate.py` - Script para autenticação inicial (execute uma vez)
- `schedule_daily.py` - Script para configurar execução automática diária

## 🔒 Segurança

- Credenciais da API em arquivo separado
- Arquivos sensíveis já estão no `.gitignore`
- Sessões salvas em pasta separada
- Progresso rastreado localmente

## ⚠️ Importante

- A conta criadora **sai automaticamente** dos grupos após criá-los
- Os grupos **não são apagados**, apenas você sai deles
- A progressão é automática baseada nos dias corridos
- Execute uma vez ao dia (ou configure execução automática)

## 🆘 Problemas Comuns

**Erro de autenticação**: Execute o script de autenticação primeiro para configurar a sessão.

**Grupos duplicados**: O sistema evita criar grupos duplicados verificando o progresso.

**Limite de grupos**: O Telegram pode impor limites. O script respeita esses limites.