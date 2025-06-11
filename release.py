#!/usr/bin/env python3
# release.py - Script de Release Automático em Python (Versão Windows Corrigida)
import subprocess
import sys
import os
import re
from datetime import datetime

def run_command(cmd, check=True, capture_output=True):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                              capture_output=capture_output, text=True)
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        if check:
            print(f"❌ Erro executando: {cmd}")
            if capture_output and e.stderr:
                print(f"Erro: {e.stderr}")
            sys.exit(1)
        return None

def print_colored(text, color="white"):
    """Simula cores no terminal"""
    colors = {
        "red": "❌", "green": "✅", "yellow": "⚠️",
        "blue": "🔗", "cyan": "🔧", "white": ""
    }
    icon = colors.get(color, "")
    print(f"{icon} {text}")

def check_git():
    """Verifica se Git está disponível"""
    git_commands = ["git", "git.exe"]
    for cmd in git_commands:
        try:
            subprocess.run([cmd, "--version"], check=True, 
                         capture_output=True, text=True)
            return cmd
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return None

def main():
    print("🔧 Sistema de Release Automático HB Tracker")
    print("=" * 44)
    
    # Verificação de dependências
    print_colored("Verificando dependências...", "yellow")
    
    # Python já está funcionando (script está rodando)
    print_colored("Python encontrado e funcionando", "green")
    
    # Verifica Git
    git_cmd = check_git()
    if not git_cmd:
        print_colored("Git não encontrado. Instale o Git primeiro.", "red")
        print("💡 Baixe em: https://git-scm.com/download/win")
        sys.exit(1)
    
    print_colored(f"Git encontrado: {git_cmd}", "green")
    
    # Verifica se estamos em um repositório Git
    if not os.path.exists(".git"):
        print_colored("Este diretório não é um repositório Git.", "red")
        print("💡 Execute: git init ou clone um repositório existente")
        sys.exit(1)
    
    # Detecta automaticamente a branch principal
    print_colored("Detectando branch principal...", "yellow")
    
    main_branch = ""
    try:
        origin_head = run_command(f"{git_cmd} symbolic-ref refs/remotes/origin/HEAD", check=False)
        if origin_head:
            main_branch = origin_head.replace("refs/remotes/origin/", "")
    except:
        pass
    
    if not main_branch:
        # Verifica manualmente
        try:
            run_command(f"{git_cmd} show-ref --verify --quiet refs/heads/master", check=False)
            if run_command(f"{git_cmd} rev-parse --verify master", check=False):
                main_branch = "master"
        except:
            pass
        
        if not main_branch:
            try:
                run_command(f"{git_cmd} show-ref --verify --quiet refs/heads/main", check=False)
                if run_command(f"{git_cmd} rev-parse --verify main", check=False):
                    main_branch = "main"
            except:
                pass
    
    if not main_branch:
        print_colored("Não foi possível detectar a branch principal", "red")
        print("💡 Branches disponíveis:")
        try:
            branches = run_command(f"{git_cmd} branch", check=False)
            print(branches)
        except:
            pass
        
        main_branch = input("Digite o nome da branch principal (master/main): ").strip()
        if not main_branch:
            sys.exit(1)
    
    print_colored(f"Branch principal detectada: {main_branch}", "green")
    
    # Verifica se estamos na branch correta
    try:
        current_branch = run_command(f"{git_cmd} branch --show-current")
    except:
        current_branch = run_command(f"{git_cmd} rev-parse --abbrev-ref HEAD")
    
    if current_branch != main_branch:
        print_colored(f"Você está na branch '{current_branch}', mas a branch principal é '{main_branch}'", "yellow")
        response = input(f"Deseja mudar para {main_branch}? (s/N): ").strip().lower()
        
        if response == 's':
            run_command(f"{git_cmd} checkout {main_branch}")
            print_colored(f"Mudou para a branch {main_branch}", "green")
        else:
            print_colored(f"Operação cancelada. Mude para a branch {main_branch} manualmente.", "red")
            sys.exit(1)
    
    # Verifica se há mudanças não commitadas
    status = run_command(f"{git_cmd} status --porcelain")
    if status:
        print_colored("Há mudanças não commitadas no repositório:", "yellow")
        run_command(f"{git_cmd} status --short", capture_output=False)
        print()
        response = input("Deseja continuar mesmo assim? (s/N): ").strip().lower()
        
        if response != 's':
            print_colored("Commit suas mudanças antes de fazer o release.", "red")
            sys.exit(1)
    
    # Verifica conectividade com remote
    print_colored("Verificando conectividade com repositório remoto...", "yellow")
    try:
        run_command(f"{git_cmd} ls-remote origin", check=False)
        print_colored("Conexão com repositório remoto OK", "green")
    except:
        print_colored("Aviso: Problema de conectividade com repositório remoto", "yellow")
        response = input("Deseja continuar mesmo assim? (s/N): ").strip().lower()
        if response != 's':
            sys.exit(1)
    
    # Puxa as últimas mudanças
    print_colored("Sincronizando com o repositório remoto...", "yellow")
    try:
        run_command(f"{git_cmd} fetch origin")
        run_command(f"{git_cmd} pull origin {main_branch}")
        print_colored("Sincronização concluída", "green")
    except:
        print_colored("Aviso: Não foi possível sincronizar completamente", "yellow")
    
    # Lê versão atual
    if not os.path.exists("version.py"):
        print_colored("Arquivo version.py não encontrado.", "red")
        print("💡 Certifique-se de estar no diretório correto do projeto")
        sys.exit(1)
    
    try:
        # Adiciona o diretório atual ao path
        sys.path.insert(0, os.getcwd())
        
        # Remove o módulo se já estiver carregado
        if 'version' in sys.modules:
            del sys.modules['version']
            
        from version import Version
        current_version = Version.get_app_info()['version']
    except Exception as e:
        print_colored(f"Erro ao ler version.py: {e}", "red")
        current_version = "0.0.1"
        print_colored(f"Usando versão padrão: {current_version}", "yellow")
    
    print(f"📋 Versão atual: {current_version}")
    
    # Calcula nova versão (incrementa patch)
    version_parts = current_version.split('.')
    try:
        major = int(version_parts[0])
        minor = int(version_parts[1]) if len(version_parts) > 1 else 0
        patch = int(version_parts[2]) if len(version_parts) > 2 else 0
    except:
        major, minor, patch = 0, 0, 1
    
    # Incrementa patch
    patch += 1
    new_version = f"{major}.{minor}.{patch}"
    
    print(f"🆕 Nova versão: {new_version}")
    print()
    response = input("Confirma criação do release automático? (s/N): ").strip().lower()
    
    if response != 's':
        print_colored("Release cancelado.", "red")
        sys.exit(1)
    
    print(f"🚀 Criando release automático para v{new_version}")
    
    # Atualiza version.py
    print(f"📝 version.py: {current_version} → {new_version}")
    
    try:
        # Lê o arquivo
        with open('version.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Atualiza versão
        content = re.sub(r'"version": "[^"]+"', f'"version": "{new_version}"', content)
        
        # Atualiza data de build
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = re.sub(r'"build_date": "[^"]+"', f'"build_date": "{current_date}"', content)
        
        # Salva o arquivo
        with open('version.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print_colored("version.py atualizado com sucesso", "green")
        
    except Exception as e:
        print_colored(f"Erro ao atualizar version.py: {e}", "red")
        sys.exit(1)
    
    # Verifica se a atualização funcionou
    try:
        # Remove o módulo se já estiver carregado
        if 'version' in sys.modules:
            del sys.modules['version']
            
        from version import Version
        updated_version = Version.get_app_info()['version']
        
        if updated_version != new_version:
            print_colored("Aviso: Versão pode não ter sido atualizada corretamente", "yellow")
            print(f"Esperado: {new_version}, Encontrado: {updated_version}")
        
    except Exception as e:
        print_colored(f"Aviso: Não foi possível verificar a atualização: {e}", "yellow")
    
    # Commit das mudanças
    print_colored("Fazendo commit das mudanças...", "yellow")
    try:
        run_command(f"{git_cmd} add version.py")
        
        commit_message = f"🔖 Prepare release v{new_version}\n\n- Version bump: {current_version} → {new_version}\n- Updated build timestamp\n- Ready for automated release"
        
        # Escapa as aspas para Windows
        commit_message_escaped = commit_message.replace('"', '\\"')
        run_command(f'{git_cmd} commit -m "{commit_message_escaped}"')
        
        print_colored("Commit realizado com sucesso", "green")
        
    except Exception as e:
        print_colored(f"Erro no commit: {e}", "red")
        sys.exit(1)
    
    # Cria tag
    print_colored("Criando tag...", "yellow")
    try:
        tag_message = f"Release v{new_version}\n\n🚀 Release Automático\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n🔧 Sistema HB Tracker\n\nFuncionalidades:\n- ✅ Controle de inventário inicial\n- ✅ Monitoramento de movimentos\n- ✅ Fluxo visual aprimorado\n- ✅ Relatórios exportáveis\n- ✅ Sistema de atualizações automáticas"
        
        tag_message_escaped = tag_message.replace('"', '\\"')
        run_command(f'{git_cmd} tag -a "v{new_version}" -m "{tag_message_escaped}"')
        
        print_colored(f"Tag v{new_version} criada localmente", "green")
        
    except Exception as e:
        print_colored(f"Erro ao criar tag: {e}", "red")
        sys.exit(1)
    
    # Push com a branch correta
    print_colored("Fazendo push da tag (isso vai disparar o GitHub Action)...", "yellow")
    
    try:
        print("🔄 Pushing branch...")
        run_command(f"{git_cmd} push origin {main_branch}")
        
        print("🔄 Pushing tag...")
        run_command(f'{git_cmd} push origin "v{new_version}"')
        
        print_colored(f"Release v{new_version} enviado com sucesso!", "green")
        print()
        print_colored("SUCESSO! Release automático criado:", "green")
        print(f"   📦 Versão: v{new_version}")
        print(f"   🌿 Branch: {main_branch}")
        print(f"   🏷️  Tag: v{new_version}")
        print()
        print_colored("O GitHub Actions vai processar automaticamente:", "yellow")
        print("   1. ⚙️  Build da aplicação")
        print("   2. 📦 Empacotamento com PyInstaller")
        print("   3. 🚀 Criação do release no GitHub")
        print("   4. 📎 Upload do executável")
        print()
        print_colored("🔗 Acompanhe em: https://github.com/esc4n0rx/HBTrackerx/actions", "blue")
        
    except Exception as e:
        print_colored("Erro no push:", "red")
        print(f"Detalhes: {e}")
        print("Verifique:")
        print("   - Conectividade com o GitHub")
        print("   - Permissões do repositório")
        print(f"   - Se a branch {main_branch} existe no remoto")
        print("   - Se você está autenticado no Git")
        
        # Rollback local
        print_colored("Fazendo rollback das mudanças locais...", "yellow")
        try:
            run_command(f"{git_cmd} reset --hard HEAD~1")
            run_command(f'{git_cmd} tag -d "v{new_version}"')
            print_colored("Rollback concluído", "yellow")
        except:
            print_colored("Erro no rollback - verifique manualmente", "red")
        
        print_colored("Algo deu errado!", "red")
        sys.exit(1)

if __name__ == "__main__":
    main()