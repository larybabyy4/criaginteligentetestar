from telethon.sync import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, EditPhotoRequest, InviteToChannelRequest
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights, InputPeerUser
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Configuration
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
NEW_OWNER = os.getenv('NEW_OWNER_USERNAME')
BOTS = [
    os.getenv('BOT_USERNAME_1'),
    os.getenv('BOT_USERNAME_2'),
    os.getenv('BOT_USERNAME_3'),
    os.getenv('BOT_USERNAME_4'),
    os.getenv('BOT_USERNAME_5'),
    os.getenv('BOT_USERNAME_6'),
    os.getenv('BOT_USERNAME_7'),
    os.getenv('BOT_USERNAME_8'),
    os.getenv('BOT_USERNAME_9'),
    os.getenv('BOT_USERNAME_10'),
    os.getenv('BOT_USERNAME_11'),
    os.getenv('BOT_USERNAME_12'),
    os.getenv('BOT_USERNAME_13'),
    os.getenv('BOT_USERNAME_14'),
    os.getenv('BOT_USERNAME_15'),
    os.getenv('BOT_USERNAME_16'),
    os.getenv('BOT_USERNAME_17'),
    os.getenv('BOT_USERNAME_18'),
    os.getenv('BOT_USERNAME_19'),
    os.getenv('BOT_USERNAME_20'),
]
GROUP_PHOTO = os.getenv('GROUP_PHOTO')
GROUP_DESCRIPTION = os.getenv('GROUP_DESCRIPTION')

def pause_with_message(message, seconds=3):
    print(message)
    print(f"Aguardando {seconds} segundos...")
    time.sleep(seconds)

async def add_as_admin(client, channel, user, rank="Administrador"):
    try:
        # Add as admin with full permissions
        pause_with_message(f"Adicionando {user} como administrador com todas as permissões...")
        await client(EditAdminRequest(
            channel=channel,
            user_id=user,
            admin_rights=ChatAdminRights(
                change_info=True,
                post_messages=True,
                edit_messages=True,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=True,
                add_admins=True,
                manage_call=True
            ),
            rank=rank
        ))
        
        # Wait to ensure admin rights are properly set
        pause_with_message(f"{user} adicionado como administrador com sucesso!", 10)
        
        return True
    except Exception as e:
        print(f"Erro ao adicionar {user} como administrador: {str(e)}")
        return False

async def main():
    print("Iniciando automação do Telegram...")
    
    # Connect to Telegram
    client = TelegramClient('session_name', API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)
    
    # Read group names from file
    with open('groups.txt', 'r', encoding='utf-8') as f:
        group_names = [line.strip() for line in f if line.strip()]
    
    for index, group_name in enumerate(group_names, 1):
        try:
            print(f"\n=== Processando grupo {index}/{len(group_names)}: {group_name} ===")
            pause_with_message(f"Criando grupo: {group_name}")
            
            # Create group
            result = await client(CreateChannelRequest(
                title=group_name,
                about=GROUP_DESCRIPTION,
                megagroup=True
            ))
            channel = result.chats[0]
            
            pause_with_message("Grupo criado com sucesso!", 5)
            
            # Set group photo
            if os.path.exists(GROUP_PHOTO):
                pause_with_message("Configurando foto do grupo...")
                await client(EditPhotoRequest(
                    channel=channel,
                    photo=await client.upload_file(GROUP_PHOTO)
                ))
                pause_with_message("Foto configurada com sucesso!", 5)
            
            # Remove all permissions from regular users
            pause_with_message("Removendo permissões dos usuários...")
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
            pause_with_message("Permissões removidas com sucesso!", 5)
            
            # Add bots as admins
            pause_with_message("Adicionando bots como administradores...")
            for bot in BOTS:
                if await add_as_admin(client, channel, bot, rank="Bot"):
                    pause_with_message(f"Bot {bot} adicionado como administrador com sucesso!", 3)
                else:
                    print(f"Falha ao adicionar bot {bot} como administrador. Continuando...")
            
            # Add new owner as admin
            if await add_as_admin(client, channel, NEW_OWNER, rank="Proprietário"):
                pause_with_message("Novo proprietário adicionado como administrador com sucesso!", 15)
            else:
                print("Falha ao adicionar novo proprietário como administrador. Continuando com o próximo grupo...")
            
            # Enviar a mensagem /add no chat do grupo
            pause_with_message("Enviando mensagem /add no chat do grupo...")
            await client.send_message(channel, '/add')
            pause_with_message("Mensagem /add enviada com sucesso!", 5)
            
            pause_with_message(f"Grupo {group_name} configurado com sucesso!", 50)
            print(f"\n{'='*50}")
            
        except Exception as e:
            print(f"Erro ao processar grupo {group_name}: {str(e)}")
            pause_with_message("Continuando com o próximo grupo...", 5)
            continue

    print("\nAutomação concluída!")
    await client.disconnect()

if __name__ == '__main__':
    print("""
=== Automação de Grupos Telegram ===
    
Antes de começar:
1. Preencha o arquivo config.env com suas informações
2. Adicione os nomes dos grupos em groups.txt
3. Coloque a foto do grupo no caminho especificado em config.env
    
Pressione Enter para começar...""")
    input()
    
    import asyncio
    asyncio.run(main())
