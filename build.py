# build.py
import os
import sys
import subprocess
import shutil
import zipfile
from datetime import datetime
from version import Version

def create_release():
    """Cria release da aplicação com PyInstaller"""
    
    print("🚀 Iniciando criação do release...")
    
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
    
    # Comando PyInstaller
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", f"ControleEstoque_v{Version.CURRENT_VERSION}",
        "--add-data", "*.py;.",
        "--icon", "icon.ico",  # Se você tiver um ícone
        "--clean",
        "main.py"
    ]
    
    try:
        result = subprocess.run(pyinstaller_cmd, check=True, capture_output=True, text=True)
        print("✅ PyInstaller executado com sucesso!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no PyInstaller: {e}")
        print(f"Output: {e.output}")
        return False
    
    # Cria arquivo ZIP para distribuição
    version = Version.CURRENT_VERSION
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    zip_filename = f"ControleEstoque_v{version}_{timestamp}.zip"
    zip_path = os.path.join(release_dir, zip_filename)
    
    print(f"📁 Criando arquivo de distribuição: {zip_filename}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Adiciona executável
        exe_path = os.path.join(dist_dir, f"ControleEstoque_v{version}.exe")
        if os.path.exists(exe_path):
            zipf.write(exe_path, f"ControleEstoque_v{version}.exe")
        
        # Adiciona README
        readme_content = f"""
Sistema de Controle de Caixas v{version}
========================================

INSTALAÇÃO:
1. Extraia este arquivo em uma pasta de sua escolha
2. Execute o arquivo ControleEstoque_v{version}.exe
3. Na primeira execução, configure o inventário inicial

REQUISITOS:
- Windows 7 ou superior
- Nenhuma instalação adicional necessária

NOVIDADES DESTA VERSÃO:
- Sistema de inventário inicial
- Fluxo visual melhorado
- Cálculos corrigidos de estoque
- Sistema de atualizações automáticas

SUPORTE:
Em caso de problemas, entre em contato através do sistema de atualizações.

Data de Build: {datetime.now().strftime("%d/%m/%Y %H:%M")}
        """
        
        zipf.writestr("README.txt", readme_content)
    
    print(f"✅ Release criado: {zip_path}")
    print(f"📊 Tamanho: {os.path.getsize(zip_path) / 1024 / 1024:.1f} MB")
    
    return True

def create_version_json():
    """Cria arquivo version.json para servidor"""
    version_info = {
        "version": Version.CURRENT_VERSION,
        "release_date": datetime.now().strftime("%d/%m/%Y"),
        "download_url": f"https://github.com/esc4n0rx/HBTrackerx/releases/download/v{Version.CURRENT_VERSION}/ControleEstoque_v{Version.CURRENT_VERSION}.zip",
        "changelog": """
        <b>Versão 0.0.1 - Lançamento Inicial</b><br><br>
        
        <b>🆕 Novidades:</b><br>
        • Sistema de inventário inicial<br>
        • Cálculo preciso de estoque por ativo<br>
        • Fluxo visual interativo<br>
        • Sistema de atualizações automáticas<br>
        • Interface melhorada com ícones<br><br>
        
        <b>🔧 Correções:</b><br>
        • Normalização de nomes de ativos<br>
        • Matching inteligente entre inventário e movimentos<br>
        • Cálculos cumulativos corretos<br><br>
        
        <b>⚡ Melhorias:</b><br>
        • Performance otimizada<br>
        • Validação de dados aprimorada<br>
        • Exportação de relatórios completos
        """,
        "required_version": "0.0.0",
        "file_size": "25.5 MB",
        "checksum": "sha256:abc123..."
    }
    
    import json
    with open("version.json", "w", encoding="utf-8") as f:
        json.dump(version_info, f, indent=2, ensure_ascii=False)
    
    print("✅ Arquivo version.json criado")

if __name__ == "__main__":
    print(f"🔨 Criando release para {Version.APP_NAME} v{Version.CURRENT_VERSION}")
    
    if create_release():
        create_version_json()
        print("\n🎉 Release criado com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Teste o executável na pasta 'dist'")
        print("2. Faça upload do ZIP para o GitHub Releases")
        print("3. Atualize a URL no version.json")
        print("4. Faça commit do version.json no repositório")
    else:
        print("\n❌ Falha na criação do release")