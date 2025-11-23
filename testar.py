from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import CreateChannelRequest, EditPhotoRequest
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights
import asyncio
import os

# Diretório para salvar as sessões
SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

# Diretório e arquivo de grupos
GROUPS_FILE = "groups.txt"

# Função para adicionar nova conta ao Telegram
async def add_new_account(api_id, api_hash, phone_number):
    session_file = os.path.join(SESSION_DIR, f"{phone_number}.session")
    client = TelegramClient(session_file, api_id, api_hash)

    try:
        print(f"[INFO] Conectando o número {phone_number}...")
        await client.connect()

        if not await client.is_user_authorized():
            print(f"[ACTION] Número {phone_number} não autorizado. Solicitando código...")
            try:
                code = input(f"Digite o código enviado para {phone_number}: ")
                await client.sign_in(phone_number, code)
            except SessionPasswordNeededError:
                password = input("Digite sua senha de verificação em duas etapas: ")
                await client.sign_in(password=password)

        # Salvar sessão como string (opcional)
        string_session = StringSession.save(client.session)
        with open(os.path.join(SESSION_DIR, f"{phone_number}.session_string"), "w") as f:
            f.write(string_session)
        print(f"[SUCCESS] Sessão salva para {phone_number}.")

    except Exception as e:
        print(f"[ERROR] Erro ao adicionar número {phone_number}: {str(e)}")
    finally:
        await client.disconnect()

# Função para criar grupos
async def create_groups(api_id, api_hash, group_photo, group_description):
    session_files = [f for f in os.listdir(SESSION_DIR) if f.endswith(".session")]
    if not session_files:
        print("[ERROR] Nenhuma sessão encontrada. Adicione contas antes de criar grupos.")
        return

    # Ler nomes de grupos
    if not os.path.exists(GROUPS_FILE):
        print(f"[ERROR] Arquivo {GROUPS_FILE} não encontrado. Certifique-se de adicioná-lo com os nomes dos grupos.")
        return

    with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
        group_names = [line.strip() for line in f if line.strip()]

    if not group_names:
        print("[ERROR] Nenhum nome de grupo encontrado no arquivo.")
        return

    # Processar grupos para cada sessão
    for session_file in session_files:
        phone_number = session_file.replace(".session", "")
        print(f"[INFO] Conectando a conta {phone_number}...")

        client = TelegramClient(os.path.join(SESSION_DIR, session_file), api_id, api_hash)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"[WARNING] Sessão para {phone_number} não autorizada. Pule esta conta.")
                continue

            for index, group_name in enumerate(group_names, 1):
                print(f"[INFO] Criando grupo {index}/{len(group_names)}: {group_name}...")
                result = await client(CreateChannelRequest(
                    title=group_name,
                    about=group_description,
                    megagroup=True
                ))
                channel = result.chats[0]
                print(f"[SUCCESS] Grupo '{group_name}' criado com sucesso!")

                # Configurar foto do grupo
                if os.path.exists(group_photo):
                    print("[INFO] Configurando foto do grupo...")
                    await client(EditPhotoRequest(
                        channel=channel,
                        photo=await client.upload_file(group_photo)
                    ))
                    print("[SUCCESS] Foto configurada com sucesso!")

                # Remover permissões padrão
                print("[INFO] Removendo permissões padrão dos usuários...")
                await client(EditChatDefaultBannedRightsRequest(
                    channel,
                    ChatBannedRights(
                        until_date=None,
                        send_messages=True,
                        send_media=True,
                        send_stickers=True,
                        send_gifs=True,
                        send_games=True,
                        send_inline=True,
                        embed_links=True,
                        send_polls=True,
                        change_info=True,
                        invite_users=True,
                        pin_messages=True
                    )
                ))
                print("[SUCCESS] Permissões padrão removidas.")

            print(f"[INFO] Todos os grupos foram criados para a conta {phone_number}.")

        except Exception as e:
            print(f"[ERROR] Erro ao processar conta {phone_number}: {str(e)}")
        finally:
            await client.disconnect()

# Menu principal
async def main():
    print("""
=== Gerenciador de Contas e Grupos do Telegram ===

1. Adicionar nova conta ao Telegram
2. Iniciar criação dos grupos
3. Sair
    """)

    api_id = int(input("Digite seu API ID: "))
    api_hash = input("Digite seu API Hash: ")

    while True:
        choice = input("\nEscolha uma opção: ")
        if choice == "1":
            phone_number = input("Digite o número de telefone (com código do país): ")
            await add_new_account(api_id, api_hash, phone_number)
        elif choice == "2":
            group_photo = input("Digite o caminho para a foto do grupo (ou pressione Enter para ignorar): ")
            group_description = input("Digite a descrição padrão para os grupos: ")
            await create_groups(api_id, api_hash, group_photo, group_description)
        elif choice == "3":
            print("Saindo. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    asyncio.run(main())
