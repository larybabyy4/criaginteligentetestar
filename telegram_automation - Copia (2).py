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

async def add_as_admin_then_transfer(client, channel, new_owner):
    try:
        # First add as admin with full permissions
        pause_with_message(f"Adicionando {new_owner} como administrador com todas as permissões...")
        await client.edit_admin(channel, new_owner,
            is_admin=True,
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
        
        # Wait to ensure admin rights are properly set
        pause_with_message("Permissões de administrador concedidas", 10)
        
        # Then transfer ownership
        pause_with_message("Iniciando transferência de propriedade...")
        await client.edit_admin(channel, new_owner,
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
        
        # Wait to ensure the transfer is complete
        pause_with_message(f"Propriedade transferida para {new_owner}", 10)
        
        # Remove admin rights from the original account
        await client.edit_admin(channel, "me",
            is_admin=True,
            change_info=False,
            post_messages=True,
            edit_messages=True,
            delete_messages=True,
            ban_users=False,
            invite_users=True,
            pin_messages=False,
            add_admins=False,
            manage_call=False
        )
        
        return True
    except Exception as e:
        print(f"Erro ao transferir propriedade: {str(e)}")
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
            
            # Add bots
            pause_with_message("Adicionando bots como administradores...")
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
                    pause_with_message(f"Bot {bot} adicionado com sucesso!", 3)
                except Exception as e:
                    print(f"Erro ao adicionar bot {bot}: {str(e)}")
            
            # Add as admin then transfer ownership with extended pause
            if await add_as_admin_then_transfer(client, channel, NEW_OWNER):
                pause_with_message("Processo de transferência concluído com sucesso!", 15)
            else:
                print("Falha na transferência de propriedade. Continuando com o próximo grupo...")
            
            # Enviar a mensagem /add no chat do grupo
            pause_with_message("Enviando mensagem /add no chat do grupo...")
            await client.send_message(channel, '/add')
            pause_with_message("Mensagem /add enviada com sucesso!", 5)
            
            pause_with_message(f"Grupo {group_name} configurado com sucesso!", 10)
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