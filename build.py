# build.py - VERSÃO CORRIGIDA
import os
import sys
import subprocess
import shutil
import zipfile
from datetime import datetime

def create_release():
    """Cria release da aplicação com PyInstaller"""
    
    print("🚀 Iniciando criação do release v0.0.4...")
    
    # Diretórios
    project_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_dir, "dist")
    release_dir = os.path.join(project_dir, "releases")
    
    # Limpa diretórios anteriores
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    if not os.path.exists(release_dir):
        os.makedirs(release_dir)
    
    print("📦 Executando PyInstaller...")
    
    # **CORREÇÃO: Comando PyInstaller melhorado**
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "ControleEstoque_v0.0.4",
        "--add-data", "*.py;.",
        "--add-data", "*.json;.",
        "--hidden-import", "PyQt5.QtWidgets",
        "--hidden-import", "PyQt5.QtCore", 
        "--hidden-import", "PyQt5.QtGui",
        "--hidden-import", "pandas",
        "--hidden-import", "requests",
        "--clean",
        "--noconfirm",
        "main.py"
    ]
    
    try:
        result = subprocess.run(pyinstaller_cmd, check=True, capture_output=True, text=True)
        print("✅ PyInstaller executado com sucesso!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no PyInstaller: {e}")
        print(f"Output: {e.output}")
        return False
    
    # **CORREÇÃO: Cria arquivo ZIP para distribuição**
    version = "0.0.4"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    zip_filename = f"ControleEstoque_v{version}_{timestamp}.zip"
    zip_path = os.path.join(release_dir, zip_filename)
    
    print(f"📁 Criando arquivo de distribuição: {zip_filename}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Adiciona executável
        exe_path = os.path.join(dist_dir, f"ControleEstoque_v{version}.exe")
        if os.path.exists(exe_path):
            zipf.write(exe_path, f"ControleEstoque_v{version}.exe")
            print(f"✅ Executável adicionado: {exe_path}")
        else:
            print(f"❌ Executável não encontrado: {exe_path}")
            return False
        
        # **CORREÇÃO: README melhorado**
        readme_content = f"""
Sistema de Controle de Caixas v{version}
========================================

🆕 NOVIDADES DESTA VERSÃO:
✅ Fluxo Visual funciona para CDs e Lojas
✅ Sistema de atualizações corrigido 
✅ Fontes maiores e mais legíveis
✅ Suporte High DPI

🔧 BUGS CORRIGIDOS:
❌ Fluxo visual para CDs bloqueado - CORRIGIDO
❌ Atualizações sempre falham - CORRIGIDO  
❌ Texto minúsculo na interface - CORRIGIDO

📥 INSTALAÇÃO:
1. Extraia este arquivo em uma pasta de sua escolha
2. Execute o arquivo ControleEstoque_v{version}.exe
3. Na primeira execução, configure o inventário inicial

💻 REQUISITOS:
- Windows 7 ou superior
- Resolução mínima: 1024x768
- Suporte automático para High DPI

⚡ FUNCIONALIDADES:
- Inventário inicial de lojas
- Controle de movimentos (CDs e Lojas)  
- Fluxo visual dia a dia
- Relatórios exportáveis
- Atualizações automáticas

🔄 ATUALIZAÇÕES:
Sistema de atualizações automáticas via GitHub
Menu: Atualizações > Verificar Atualizações

📞 SUPORTE:
GitHub: https://github.com/esc4n0rx/HBTrackerx
Issues: https://github.com/esc4n0rx/HBTrackerx/issues

Data de Build: {datetime.now().strftime("%d/%m/%Y %H:%M")}
        """
        
        zipf.writestr("README.txt", readme_content)
    
    print(f"✅ Release criado: {zip_path}")
    print(f"📊 Tamanho: {os.path.getsize(zip_path) / 1024 / 1024:.1f} MB")
    
    return True

if __name__ == "__main__":
    print("🔨 Criando release para Sistema de Controle de Caixas v0.0.4")
    
    if create_release():
        print("\n🎉 Release criado com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Teste o executável na pasta 'dist'")
        print("2. Faça upload do ZIP para o GitHub Releases")
        print("3. Crie tag v0.0.4 no repositório")
        print("4. Publique o release no GitHub")
    else:
        print("\n❌ Falha na criação do release")