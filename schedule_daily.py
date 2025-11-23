"""
Script para agendar a execução diária automática da automação.
Execute este script uma vez para configurar a execução automática diária.
"""
import os
import sys
import platform
from pathlib import Path

def setup_windows_scheduler():
    """Configura agendamento no Windows Task Scheduler"""
    script_path = Path(__file__).parent.absolute()
    python_exe = sys.executable
    automation_script = script_path / "telegram_automation_intelligent.py"
    
    # Nome da tarefa
    task_name = "TelegramAutoCreateGroups"
    
    # Comando para criar a tarefa agendada
    command = f'''schtasks /CREATE /TN "{task_name}" /TR "\\"{python_exe}\\" \\"{automation_script}\"" /SC DAILY /ST 09:00 /F'''
    
    print("=" * 60)
    print("Configurando execução automática diária (Windows)")
    print("=" * 60)
    print(f"\nScript Python: {python_exe}")
    print(f"Script de automação: {automation_script}")
    print(f"\nExecutando comando...\n")
    
    result = os.system(command)
    
    if result == 0:
        print("✓ Tarefa agendada criada com sucesso!")
        print(f"\nA automação será executada diariamente às 09:00")
        print(f"\nPara modificar o horário, execute:")
        print(f'  schtasks /CHANGE /TN "{task_name}" /ST HH:MM')
        print(f"\nPara remover a tarefa agendada:")
        print(f'  schtasks /DELETE /TN "{task_name}" /F')
    else:
        print("⚠️  Erro ao criar tarefa agendada.")
        print("   Execute como Administrador ou configure manualmente.")

def setup_linux_cron():
    """Configura agendamento no Linux com cron"""
    script_path = Path(__file__).parent.absolute()
    python_exe = sys.executable
    automation_script = script_path / "telegram_automation_intelligent.py"
    
    cron_entry = f"0 9 * * * cd {script_path} && {python_exe} {automation_script} >> {script_path}/automation.log 2>&1\n"
    
    print("=" * 60)
    print("Configurando execução automática diária (Linux)")
    print("=" * 60)
    print(f"\nAdicione esta linha ao crontab:")
    print(f"\n{cron_entry}")
    print("\nExecute: crontab -e")
    print("E adicione a linha acima.")

def main():
    """Função principal"""
    system = platform.system()
    
    print("\n" + "=" * 60)
    print("CONFIGURAÇÃO DE EXECUÇÃO AUTOMÁTICA DIÁRIA")
    print("=" * 60 + "\n")
    
    if system == "Windows":
        setup_windows_scheduler()
    elif system == "Linux":
        setup_linux_cron()
    else:
        print(f"Sistema operacional {system} não suportado automaticamente.")
        print("Configure manualmente usando o agendador de tarefas do seu sistema.")
    
    print("\n" + "=" * 60)
    print("✓ Configuração concluída!")
    print("=" * 60)

if __name__ == "__main__":
    main()

