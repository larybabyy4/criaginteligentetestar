from telethon.sync import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, EditPhotoRequest
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import os
import time
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv('config.env')

# Configurações
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
NEW_OWNER = os.getenv('NEW_OWNER_USERNAME')
BOTS = [os.getenv(f'BOT_USERNAME_{i}') for i in range(1, 11) if os.getenv(f'BOT_USERNAME_{i}')]
GROUP_PHOTO = os.getenv('GROUP_PHOTO')
GROUP_DESCRIPTION = os.getenv('GROUP_DESCRIPTION')

async def add_admin(client, channel, user, rank="Admin"):
    try:
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
        print(f"{user} adicionado como {rank}")
        return True
    except Exception as e:
        print(f"Erro ao adicionar {user}: {e}")
        return False

async def main():
    print("Iniciando automação...")
    
    async with TelegramClient('session_name', API_ID, API_HASH) as client:
        await client.start(PHONE_NUMBER)
        
        with open('groups.txt', 'r', encoding='utf-8') as f:
            group_names = [line.strip() for line in f if line.strip()]
        
        for index, name in enumerate(group_names, 1):
            try:
                print(f"\nProcessando grupo {index}/{len(group_names)}: {name}")
                
                # Criação do grupo
                result = await client(CreateChannelRequest(
                    title=name,
                    about=GROUP_DESCRIPTION,
                    megagroup=True
                ))
                channel = result.chats[0]
                print("Grupo criado")
                time.sleep(2)
                
                # Foto do grupo (corrigido o parêntese)
                if GROUP_PHOTO and os.path.exists(GROUP_PHOTO):
                    try:
                        await client(EditPhotoRequest(
                            channel=channel,
                            photo=await client.upload_file(GROUP_PHOTO)
                        ))
                        print("Foto definida")
                    except Exception as e:
                        print(f"Erro ao definir foto: {e}")
                time.sleep(2)
                
                # Permissões
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
                print("Permissões configuradas")
                time.sleep(2)
                
                # Adiciona bots
                for bot in BOTS:
                    if bot:
                        await add_admin(client, channel, bot, "Bot")
                        time.sleep(1)
                
                # Adiciona dono
                if NEW_OWNER:
                    await add_admin(client, channel, NEW_OWNER, "Proprietário")
                    time.sleep(3)
                
                # Comando /add
                await client.send_message(channel, '/add')
                print("Comando /add enviado")
                
                print(f"Grupo {name} concluído!")
                time.sleep(5)
                
            except Exception as e:
                print(f"Erro no grupo {name}: {e}")
                continue

    print("\nProcesso concluído!")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
