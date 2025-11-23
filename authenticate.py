"""
Script auxiliar para autenticação inicial da conta do Telegram.
Execute este script uma vez antes de usar a automação principal.
"""
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
import os
from dotenv import load_dotenv

# Carrega credenciais
load_dotenv('api_credentials.env')

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

def authenticate():
    """Autentica a conta do Telegram"""
    if not API_ID or not API_HASH or not PHONE_NUMBER:
        print("❌ ERRO: Configure o arquivo api_credentials.env com API_ID, API_HASH e PHONE_NUMBER")
        return
    
    print("=" * 60)
    print("🔐 AUTENTICAÇÃO DO TELEGRAM")
    print("=" * 60)
    print(f"\nNúmero: {PHONE_NUMBER}")
    print(f"API ID: {API_ID}\n")
    
    # Cria diretório de sessões
    os.makedirs('sessions', exist_ok=True)
    
    # Nome da sessão
    session_name = f"sessions/{PHONE_NUMBER.replace('+', '').replace(' ', '').replace('-', '')}"
    
    # Cria cliente
    client = TelegramClient(session_name, int(API_ID), API_HASH)
    
    try:
        print("🔌 Conectando ao Telegram...")
        client.connect()
        
        if not client.is_user_authorized():
            print("\n📱 Enviando código de verificação...")
            client.send_code_request(PHONE_NUMBER)
            
            code = input("📨 Digite o código recebido no Telegram: ")
            
            try:
                client.sign_in(PHONE_NUMBER, code)
                print("✓ Login realizado com sucesso!")
            except SessionPasswordNeededError:
                password = input("🔒 Digite sua senha de verificação em duas etapas: ")
                client.sign_in(password=password)
                print("✓ Login realizado com sucesso!")
        else:
            print("✓ Você já está autenticado!")
            me = client.get_me()
            print(f"✓ Conectado como: {me.first_name} {me.last_name or ''} (@{me.username or 'sem username'})")
    
    except Exception as e:
        print(f"❌ Erro durante autenticação: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.disconnect()
        print("\n✓ Sessão salva! Agora você pode usar a automação principal.")

if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════╗
║         AUTENTICAÇÃO INICIAL - TELEGRAM                   ║
╚═══════════════════════════════════════════════════════════╝

Este script faz a automação inicial da sua conta do Telegram.
Execute apenas uma vez para configurar a sessão.

Certifique-se de ter:
1. Preenchido o arquivo api_credentials.env
2. Acesso ao número de telefone configurado
3. Acesso ao Telegram no dispositivo

Pressione Enter para continuar...
""")
    input()
    
    authenticate()

