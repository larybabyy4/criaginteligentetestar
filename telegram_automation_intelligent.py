from telethon.sync import TelegramClient
from telethon.tl.functions.channels import (
    CreateChannelRequest, 
    EditPhotoRequest, 
    DeleteChannelRequest,
    LeaveChannelRequest
)
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
from telethon.errors import SessionPasswordNeededError
import os
import json
import time
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carrega arquivos de configuração
load_dotenv('api_credentials.env')  # Credenciais da API (opcional)
load_dotenv('config.env')  # Outras configurações

# Credenciais da API serão solicitadas sempre ao usuário
# Valores padrão do arquivo (podem ser sobrescritos)
DEFAULT_API_ID = os.getenv('API_ID')
DEFAULT_API_HASH = os.getenv('API_HASH')
DEFAULT_PHONE_NUMBER = os.getenv('PHONE_NUMBER')

# Variáveis globais que serão definidas na execução
API_ID = None
API_HASH = None
PHONE_NUMBER = None

# Outras configurações (do config.env)
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
# Remove valores vazios
BOTS = [bot for bot in BOTS if bot]

GROUP_PHOTO = os.getenv('GROUP_PHOTO', 'foto.jpg')
GROUP_DESCRIPTION = os.getenv('GROUP_DESCRIPTION', 'Nosso Site Oficial   https://DraLarissa.github.io')

# Arquivo para rastrear progresso
PROGRESS_FILE = 'creation_progress.json'

def load_progress():
    """Carrega o progresso de criação dos grupos"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_progress(progress):
    """Salva o progresso de criação dos grupos"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def calculate_groups_for_today(phone_number):
    """Calcula quantos grupos devem ser criados hoje"""
    progress = load_progress()
    
    # Inicializa o progresso se não existir
    if phone_number not in progress:
        progress[phone_number] = {
            'day': 1,
            'total_created': 0,
            'last_creation_date': None,
            'created_groups': []
        }
    
    phone_progress = progress[phone_number]
    today = datetime.now().date().isoformat()
    last_date = phone_progress.get('last_creation_date')
    
    # Se já criou hoje, retorna 0
    if last_date == today:
        return 0, phone_progress
    
    # Se é um novo dia, incrementa o dia
    if last_date and last_date != today:
        # Verifica se passou mais de 1 dia
        last_datetime = datetime.fromisoformat(last_date).date()
        days_passed = (datetime.now().date() - last_datetime).days
        
        if days_passed > 0:
            # Incrementa o dia para cada dia que passou
            phone_progress['day'] += days_passed
    elif not last_date:
        # Primeira execução
        phone_progress['day'] = 1
    
    # Calcula quantos grupos criar (5 no dia 1, 10 no dia 2, etc., máximo 40)
    day = phone_progress['day']
    groups_to_create = min(5 * day, 40)
    
    # Subtrai os grupos já criados para não ultrapassar o limite diário
    groups_today = 0
    if last_date == today:
        # Se já criou hoje, conta quantos foram criados hoje
        created_today = [g for g in phone_progress['created_groups'] 
                        if g.get('date') == today]
        groups_today = len(created_today)
        groups_to_create = max(0, groups_to_create - groups_today)
    
    save_progress(progress)
    return groups_to_create, phone_progress

def record_group_created(phone_number, group_name, group_id):
    """Registra um grupo criado"""
    progress = load_progress()
    
    if phone_number not in progress:
        progress[phone_number] = {
            'day': 1,
            'total_created': 0,
            'last_creation_date': None,
            'created_groups': []
        }
    
    today = datetime.now().date().isoformat()
    progress[phone_number]['created_groups'].append({
        'name': group_name,
        'id': group_id,
        'date': today
    })
    progress[phone_number]['total_created'] += 1
    progress[phone_number]['last_creation_date'] = today
    
    save_progress(progress)

def update_day(phone_number):
    """Atualiza o dia após concluir a criação"""
    progress = load_progress()
    
    if phone_number in progress:
        # O dia só incrementa no próximo dia natural, não aqui
        # Mas atualizamos a data da última criação
        progress[phone_number]['last_creation_date'] = datetime.now().date().isoformat()
        save_progress(progress)

def get_groups_to_create_list(phone_progress):
    """Obtém a lista de nomes de grupos que ainda não foram criados"""
    with open('groups.txt', 'r', encoding='utf-8') as f:
        all_groups = [line.strip() for line in f if line.strip()]
    
    # Remove grupos já criados
    created_names = {g['name'] for g in phone_progress.get('created_groups', [])}
    remaining_groups = [g for g in all_groups if g not in created_names]
    
    return remaining_groups

def validate_phone_number(phone):
    """Valida formato do número de telefone"""
    # Remove espaços e caracteres especiais
    phone_clean = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Verifica se começa com +
    if not phone_clean.startswith('+'):
        if phone_clean.startswith('55'):
            phone_clean = '+' + phone_clean
        else:
            return False
    
    # Verifica se tem pelo menos 10 dígitos após o +
    digits = phone_clean[1:]
    if not digits.isdigit() or len(digits) < 10:
        return False
    
    return phone_clean

def get_credentials():
    """Solicita credenciais da API ao usuário"""
    global API_ID, API_HASH, PHONE_NUMBER
    
    print("\n" + "=" * 60)
    print("🔐 CONFIGURAÇÃO DE CREDENCIAIS")
    print("=" * 60)
    print("\nPor favor, forneça suas credenciais da API do Telegram:")
    print("(Obtenha em: https://my.telegram.org)\n")
    
    # Solicita API_ID
    api_id_prompt = "📱 API ID"
    if DEFAULT_API_ID:
        # Tenta converter o valor padrão para exibição
        try:
            default_display = str(int(DEFAULT_API_ID)) if DEFAULT_API_ID else ""
            if default_display:
                api_id_prompt += f" (pressione Enter para usar: {default_display})"
        except:
            if DEFAULT_API_ID:
                api_id_prompt += f" (pressione Enter para usar o valor salvo)"
    api_id_prompt += ": "
    
    api_id_input = input(api_id_prompt).strip()
    api_id_value = api_id_input if api_id_input else DEFAULT_API_ID
    
    if not api_id_value:
        print("❌ API ID é obrigatório!")
        return False
    
    try:
        API_ID = int(api_id_value)
        if API_ID <= 0:
            print("❌ API ID deve ser um número positivo!")
            return False
    except ValueError:
        print("❌ API ID deve ser um número!")
        return False
    
    # Solicita API_HASH
    api_hash_prompt = "🔑 API Hash"
    if DEFAULT_API_HASH:
        api_hash_prompt += f" (pressione Enter para usar o valor salvo)"
    api_hash_prompt += ": "
    
    api_hash_input = input(api_hash_prompt).strip()
    API_HASH = api_hash_input if api_hash_input else DEFAULT_API_HASH
    
    if not API_HASH:
        print("❌ API Hash é obrigatório!")
        return False
    
    if len(API_HASH) < 20:
        print("⚠️  API Hash parece estar incorreto (muito curto).")
        confirm = input("Continuar mesmo assim? (s/N): ").strip().lower()
        if confirm != 's':
            return False
    
    # Solicita PHONE_NUMBER
    phone_prompt = "📞 Número de telefone (com código do país, ex: +5511999999999)"
    if DEFAULT_PHONE_NUMBER:
        phone_prompt += f" (pressione Enter para usar: {DEFAULT_PHONE_NUMBER})"
    phone_prompt += ": "
    
    phone_input = input(phone_prompt).strip()
    phone_value = phone_input if phone_input else DEFAULT_PHONE_NUMBER
    
    if not phone_value:
        print("❌ Número de telefone é obrigatório!")
        return False
    
    # Valida e normaliza número de telefone
    validated_phone = validate_phone_number(phone_value)
    if not validated_phone:
        print("⚠️  Formato de telefone inválido. Tentando normalizar...")
        validated_phone = phone_value if phone_value.startswith('+') else '+' + phone_value
    
    PHONE_NUMBER = validated_phone
    
    print("\n✓ Credenciais configuradas com sucesso!")
    print(f"   📱 API ID: {API_ID}")
    print(f"   📞 Telefone: {PHONE_NUMBER}\n")
    return True

def pause_with_message(message, seconds=3):
    """Pausa com mensagem"""
    if message:
        print(message)
    if seconds > 0:
        print(f"Aguardando {seconds} segundos...")
        time.sleep(seconds)

async def add_as_admin(client, channel, user, rank="Admin", full_permissions=True):
    """Adiciona um usuário como administrador
    
    Args:
        client: Cliente Telegram
        channel: Canal/Grupo
        user: Usuário/Bot a adicionar
        rank: Título do cargo
        full_permissions: Se True, todas as permissões incluindo adicionar admins
                         Se False, permissões limitadas (sem adicionar admins)
    """
    try:
        if full_permissions:
            # Permissões completas: todas as permissões incluindo adicionar admins
            admin_rights = ChatAdminRights(
                change_info=True,
                post_messages=True,
                edit_messages=True,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=True,
                add_admins=True,  # Pode adicionar novos admins
                manage_call=True
            )
        else:
            # Permissões limitadas: pode fixar mensagens e convidar via link, mas NÃO pode adicionar admins
            admin_rights = ChatAdminRights(
                change_info=False,      # Não pode alterar informações do grupo
                post_messages=True,      # Pode postar mensagens
                edit_messages=True,      # Pode editar mensagens
                delete_messages=True,    # Pode deletar mensagens
                ban_users=True,          # Pode banir usuários
                invite_users=True,       # Pode convidar via link
                pin_messages=True,       # Pode fixar mensagens
                add_admins=False,        # NÃO pode adicionar novos admins
                manage_call=True         # Pode gerenciar chamadas
            )
        
        await client(EditAdminRequest(
            channel=channel,
            user_id=user,
            admin_rights=admin_rights,
            rank=rank
        ))
        perm_type = "completas" if full_permissions else "limitadas"
        print(f"✓ {user} adicionado como {rank} (permissões {perm_type})")
        return True
    except Exception as e:
        print(f"✗ Erro ao adicionar {user}: {e}")
        return False

async def remove_own_admin(client, channel):
    """Remove a própria conta como admin (mas mantém o grupo ativo)"""
    try:
        # Remove suas próprias permissões de admin, mas mantém o grupo
        # Isso permite que o grupo continue existindo sem você
        me = await client.get_me()
        await client(EditAdminRequest(
            channel=channel,
            user_id=me.id,
            admin_rights=ChatAdminRights(
                change_info=False,
                post_messages=False,
                edit_messages=False,
                delete_messages=False,
                ban_users=False,
                invite_users=False,
                pin_messages=False,
                add_admins=False,
                manage_call=False
            ),
            rank=""
        ))
        print(f"✓ Permissões de admin removidas")
        return True
    except Exception as e:
        # Se não conseguir remover, tenta sair mesmo assim
        print(f"⚠️  Não foi possível remover permissões (pode ser que já não seja admin): {e}")
        return False

async def authenticate_client(client):
    """Autentica o cliente se necessário"""
    if await client.is_user_authorized():
        print("✓ Sessão já autenticada!")
        me = await client.get_me()
        print(f"✓ Conectado como: {me.first_name} {me.last_name or ''} (@{me.username or 'sem username'})\n")
        return True
    
    print("\n" + "=" * 60)
    print("🔐 AUTENTICAÇÃO NECESSÁRIA")
    print("=" * 60)
    print(f"\nNúmero: {PHONE_NUMBER}")
    print("📱 Iniciando processo de autenticação...\n")
    
    try:
        print("📨 Enviando código de verificação para o Telegram...")
        await client.send_code_request(PHONE_NUMBER)
        
        code = input("📨 Digite o código recebido no Telegram: ").strip()
        
        try:
            await client.sign_in(PHONE_NUMBER, code)
            print("✓ Login realizado com sucesso!\n")
            return True
        except SessionPasswordNeededError:
            print("\n🔒 Conta com verificação em duas etapas detectada.")
            password = input("🔒 Digite sua senha de verificação em duas etapas: ").strip()
            await client.sign_in(password=password)
            print("✓ Login realizado com sucesso!\n")
            return True
    except Exception as e:
        print(f"\n❌ Erro durante autenticação: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def leave_group(client, channel):
    """Sai do grupo sem apagá-lo"""
    try:
        # Primeiro, remove suas permissões de admin para garantir que o grupo continue
        # Isso é importante se você for o único dono
        await remove_own_admin(client, channel)
        await asyncio.sleep(2)
        
        # Agora tenta sair do grupo
        await client(LeaveChannelRequest(channel))
        print(f"✓ Saído do grupo {channel.id}")
        return True
    except Exception as e:
        # Alguns grupos podem não permitir sair se você for dono
        # Mas como já removemos as permissões, o grupo deve continuar existindo
        error_msg = str(e).lower()
        if "owner" in error_msg or "creator" in error_msg:
            print(f"⚠️  Não foi possível sair (você é o dono), mas o grupo continua ativo")
        else:
            print(f"⚠️  Erro ao sair do grupo: {e}")
        return False

def validate_files():
    """Valida se os arquivos necessários existem"""
    errors = []
    warnings = []
    
    # Verifica groups.txt
    if not os.path.exists('groups.txt'):
        errors.append("❌ Arquivo 'groups.txt' não encontrado!")
    else:
        try:
            with open('groups.txt', 'r', encoding='utf-8') as f:
                groups = [line.strip() for line in f if line.strip()]
                if not groups:
                    errors.append("❌ Arquivo 'groups.txt' está vazio!")
                else:
                    print(f"✓ {len(groups)} grupos encontrados em groups.txt")
        except Exception as e:
            errors.append(f"❌ Erro ao ler 'groups.txt': {e}")
    
    # Verifica foto do grupo
    if GROUP_PHOTO and not os.path.exists(GROUP_PHOTO):
        warnings.append(f"⚠️  Foto do grupo '{GROUP_PHOTO}' não encontrada. Grupos serão criados sem foto.")
    elif GROUP_PHOTO and os.path.exists(GROUP_PHOTO):
        print(f"✓ Foto do grupo encontrada: {GROUP_PHOTO}")
    
    # Verifica configurações
    if not NEW_OWNER:
        warnings.append("⚠️  NEW_OWNER_USERNAME não configurado. Nenhum proprietário será adicionado.")
    else:
        print(f"✓ Proprietário configurado: {NEW_OWNER}")
    
    if not BOTS:
        warnings.append("⚠️  Nenhum bot configurado. Nenhum bot será adicionado aos grupos.")
    else:
        print(f"✓ {len(BOTS)} bot(s) configurado(s)")
    
    # Mostra avisos
    if warnings:
        print("\n📋 Avisos:")
        for warning in warnings:
            print(f"   {warning}")
    
    # Mostra erros
    if errors:
        print("\n❌ Erros encontrados:")
        for error in errors:
            print(f"   {error}")
        return False
    
    return True

async def main():
    """Função principal da automação inteligente"""
    print("\n" + "=" * 60)
    print("🤖 AUTOMAÇÃO INTELIGENTE DE CRIAÇÃO DE GRUPOS")
    print("=" * 60 + "\n")
    
    # Valida arquivos necessários
    print("📋 Verificando arquivos necessários...")
    if not validate_files():
        print("\n❌ ERRO: Arquivos necessários não encontrados ou inválidos.")
        print("   Por favor, verifique os arquivos e tente novamente.")
        return
    
    print()
    
    # Solicita credenciais sempre
    if not get_credentials():
        print("❌ ERRO: Credenciais não fornecidas corretamente.")
        return
    
    # Valida credenciais
    if not API_ID or not API_HASH or not PHONE_NUMBER:
        print("❌ ERRO: Credenciais inválidas.")
        return
    
    # Calcula quantos grupos criar hoje
    groups_to_create, phone_progress = calculate_groups_for_today(PHONE_NUMBER)
    
    if groups_to_create == 0:
        print(f"✓ Já foram criados todos os grupos permitidos para hoje!")
        print(f"  Total criado: {phone_progress.get('total_created', 0)} grupos")
        return
    
    print(f"📅 Dia {phone_progress['day']} de criação")
    print(f"📊 Grupos a criar hoje: {groups_to_create}")
    print(f"📈 Total já criado: {phone_progress.get('total_created', 0)} grupos")
    print()
    
    # Obtém lista de grupos para criar
    available_groups = get_groups_to_create_list(phone_progress)
    
    if not available_groups:
        print("❌ Todos os grupos do arquivo groups.txt já foram criados!")
        return
    
    # Limita aos grupos que devem ser criados hoje
    groups_to_process = available_groups[:groups_to_create]
    print(f"📝 Processando {len(groups_to_process)} grupos hoje...")
    print()
    
    # Conecta ao Telegram
    session_name = f"sessions/{PHONE_NUMBER.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')}"
    os.makedirs('sessions', exist_ok=True)
    
    client = None
    try:
        print("🔌 Conectando ao Telegram...")
        client = TelegramClient(session_name, int(API_ID), API_HASH)
        await client.connect()
        
        # Verifica conexão
        if not client.is_connected():
            print("❌ Falha ao conectar ao Telegram. Verifique sua conexão com a internet.")
            if client:
                await client.disconnect()
            return
        
        # Autentica automaticamente se necessário
        if not await authenticate_client(client):
            print("❌ Falha na autenticação. Verifique suas credenciais e tente novamente.")
            if client:
                await client.disconnect()
            return
        
        created_groups_list = []  # Para rastrear grupos criados e sair depois
        
        # Cria os grupos
        for index, group_name in enumerate(groups_to_process, 1):
            try:
                print(f"\n{'='*60}")
                print(f"📦 Grupo {index}/{len(groups_to_process)}: {group_name}")
                print(f"{'='*60}")
                
                # Cria o grupo
                pause_with_message("🔄 Criando grupo...", 2)
                result = await client(CreateChannelRequest(
                    title=group_name,
                    about=GROUP_DESCRIPTION,
                    megagroup=True
                ))
                channel = result.chats[0]
                print(f"✓ Grupo '{group_name}' criado! (ID: {channel.id})")
                pause_with_message("", 3)
                
                # Configura foto do grupo
                if GROUP_PHOTO and os.path.exists(GROUP_PHOTO):
                    try:
                        pause_with_message("🖼️  Configurando foto do grupo...", 1)
                        await client(EditPhotoRequest(
                            channel=channel,
                            photo=await client.upload_file(GROUP_PHOTO)
                        ))
                        print("✓ Foto configurada com sucesso!")
                    except Exception as e:
                        print(f"⚠️  Erro ao configurar foto: {e}")
                pause_with_message("", 2)
                
                # Remove permissões padrão
                pause_with_message("🔒 Configurando permissões...", 1)
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
                print("✓ Permissões configuradas!")
                pause_with_message("", 2)
                
                # Adiciona bots como administradores
                if BOTS:
                    pause_with_message("🤖 Adicionando bots como administradores...", 1)
                    bots_added_full = 0
                    bots_added_limited = 0
                    
                    for index, bot in enumerate(BOTS, 1):
                        if bot:
                            # Os 5 primeiros bots têm permissões completas (incluindo adicionar admins)
                            # Os demais têm permissões limitadas (sem adicionar admins)
                            if index <= 5:
                                if await add_as_admin(client, channel, bot, rank="Bot", full_permissions=True):
                                    bots_added_full += 1
                                    print(f"   → {bot} (Bot #{index}) - Permissões COMPLETAS")
                            else:
                                if await add_as_admin(client, channel, bot, rank="Bot", full_permissions=False):
                                    bots_added_limited += 1
                                    print(f"   → {bot} (Bot #{index}) - Permissões LIMITADAS")
                            await asyncio.sleep(1)
                    
                    total_added = bots_added_full + bots_added_limited
                    print(f"\n✓ {total_added}/{len(BOTS)} bot(s) adicionado(s)!")
                    print(f"   • {bots_added_full} bot(s) com permissões completas (podem adicionar admins)")
                    print(f"   • {bots_added_limited} bot(s) com permissões limitadas (não podem adicionar admins)")
                pause_with_message("", 2)
                
                # Adiciona novo proprietário (sempre com permissões completas)
                if NEW_OWNER:
                    pause_with_message(f"👤 Adicionando {NEW_OWNER} como proprietário...", 1)
                    if await add_as_admin(client, channel, NEW_OWNER, rank="Proprietário", full_permissions=True):
                        print(f"   → {NEW_OWNER} - Permissões COMPLETAS (Proprietário)")
                    pause_with_message("", 3)
                
                # Envia comando /add
                try:
                    await asyncio.sleep(2)  # Aguarda um pouco antes de enviar
                    await client.send_message(channel, '/add')
                    print("✓ Comando /add enviado!")
                except Exception as e:
                    print(f"⚠️  Não foi possível enviar comando /add: {e}")
                
                # Registra o grupo criado
                record_group_created(PHONE_NUMBER, group_name, channel.id)
                created_groups_list.append((group_name, channel))
                
                print(f"✅ Grupo '{group_name}' configurado com sucesso!")
                pause_with_message("", 5)
                
            except Exception as e:
                print(f"❌ Erro ao processar grupo {group_name}: {str(e)}")
                pause_with_message("Continuando com o próximo grupo...", 3)
                continue
        
        # SAI DE TODOS OS GRUPOS CRIADOS (sem apagar)
        if created_groups_list:
            print(f"\n{'='*60}")
            print(f"🚪 Saindo dos grupos criados (sem apagar)...")
            print(f"{'='*60}")
            
            for group_name, channel in created_groups_list:
                try:
                    print(f"🚪 Saindo do grupo '{group_name}'...")
                    await leave_group(client, channel)
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"⚠️  Erro ao sair do grupo {group_name}: {e}")
                    continue
            
            print(f"\n✓ Saído de {len(created_groups_list)} grupos com sucesso!")
            print("ℹ️  Os grupos permanecem ativos e não foram apagados.")
        
        # Atualiza o progresso
        update_day(PHONE_NUMBER)
        
        print(f"\n{'='*60}")
        print(f"✅ AUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"{'='*60}")
        print(f"📊 Grupos criados hoje: {len(created_groups_list)}")
        progress = load_progress()
        total = progress.get(PHONE_NUMBER, {}).get('total_created', 0)
        print(f"📈 Total geral: {total} grupos")
        print(f"📅 Próxima execução: Amanhã (serão criados {min(5 * (progress.get(PHONE_NUMBER, {}).get('day', 1) + 1), 40)} grupos)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação interrompida pelo usuário.")
        print("⚠️  Grupos já criados permanecerão ativos.")
        if created_groups_list:
            print(f"📊 {len(created_groups_list)} grupo(s) criado(s) antes da interrupção.")
    except Exception as e:
        print(f"\n❌ Erro geral: {str(e)}")
        print("📋 Detalhes do erro:")
        import traceback
        traceback.print_exc()
    finally:
        if client and client.is_connected():
            try:
                await client.disconnect()
                print("\n✓ Desconectado do Telegram.")
            except:
                pass

if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════╗
║     AUTOMAÇÃO INTELIGENTE DE CRIAÇÃO DE GRUPOS TELEGRAM  ║
╚═══════════════════════════════════════════════════════════╝

📋 Funcionalidades:
   • Criação progressiva: 5 grupos no 1º dia, 10 no 2º, etc.
   • Máximo de 40 grupos por dia
   • Saída automática dos grupos após criação (sem apagar)
   • Execução automática diária (agende no agendador de tarefas)
   • Autenticação automática integrada
   • Validação completa de arquivos e credenciais

⚙️  Requisitos:
   • Arquivo groups.txt com nomes dos grupos
   • API_ID, API_HASH do Telegram (https://my.telegram.org)
   • Número de telefone registrado no Telegram
   • Foto do grupo (opcional, mas recomendado)

ℹ️  Nota: As credenciais serão solicitadas na execução.
   Você pode preencher api_credentials.env para valores padrão.

Pressione Enter para iniciar...
""")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário.")
        exit(0)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrompido pelo usuário.")
        exit(0)

