from telethon.sync import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, EditPhotoRequest
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights, InputChatPhotoEmpty
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
    os.getenv('BOT_USERNAME_3')
]
GROUP_PHOTO = os.getenv('GROUP_PHOTO')
GROUP_DESCRIPTION = os.getenv('GROUP_DESCRIPTION')

def pause_with_message(message, seconds=3):
    print(message)
    print(f"Aguardando {seconds} segundos...")
    time.sleep(seconds)

async def main():
    print("Iniciando automação do Telegram...")
    
    # Connect to Telegram
    client = TelegramClient('session_name', API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)
    
    # Read group names from file
    with open('groups.txt', 'r', encoding='utf-8') as f:
        group_names = [line.strip() for line in f if line.strip()]
    
    for group_name in group_names:
        try:
            pause_with_message(f"\nCriando grupo: {group_name}")
            
            # Create group
            result = await client(CreateChannelRequest(
                title=group_name,
                about=GROUP_DESCRIPTION,
                megagroup=True
            ))
            channel = result.chats[0]
            
            pause_with_message("Grupo criado com sucesso!")
            
            # Set group photo
            if os.path.exists(GROUP_PHOTO):
                pause_with_message("Configurando foto do grupo...")
                await client.edit_admin(channel, "me", 
                    change_info=True,
                    post_messages=True,
                    edit_messages=True,
                    delete_messages=True,
                    ban_users=True,
                    invite_users=True,
                    pin_messages=True,
                    add_admins=True,
                    manage_call=True
                )
                await client(EditPhotoRequest(
                    channel=channel,
                    photo=await client.upload_file(GROUP_PHOTO)
                ))
            
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
            
            # Add bots
            pause_with_message("Adicionando bots...")
            for bot in BOTS:
                try:
                    await client.edit_admin(channel, bot,
                        is_admin=True,
                        change_info=True,
                        post_messages=True,
                        edit_messages=True,
                        delete_messages=True,
                        ban_users=True,
                        invite_users=True,
                        pin_messages=True,
                        add_admins=False,
                        manage_call=True
                    )
                    pause_with_message(f"Bot {bot} adicionado com sucesso!")
                except Exception as e:
                    print(f"Erro ao adicionar bot {bot}: {str(e)}")
            
            # Transfer ownership
            pause_with_message(f"Transferindo propriedade para {NEW_OWNER}...")
            try:
                await client.edit_admin(channel, NEW_OWNER,
                    is_admin=True,
                    change_info=True,
                    post_messages=True,
                    edit_messages=True,
                    delete_messages=True,
                    ban_users=True,
                    invite_users=True,
                    pin_messages=True,
                    add_admins=True,
                    manage_call=True,
                    is_owner=True
                )
                pause_with_message("Propriedade transferida com sucesso!")
            except Exception as e:
                print(f"Erro ao transferir propriedade: {str(e)}")
            
            pause_with_message(f"Grupo {group_name} configurado com sucesso!", 5)
            
        except Exception as e:
            print(f"Erro ao processar grupo {group_name}: {str(e)}")
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