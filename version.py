# version.py - VERSÃO CORRIGIDA PARA SISTEMA DE ATUALIZAÇÕES
import os
import json
import requests
import subprocess
import sys
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QProgressDialog
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import zipfile
import tempfile
import shutil

class Version:
    """Classe para gerenciar versões da aplicação"""
    
    CURRENT_VERSION = "0.0.4"
    APP_NAME = "Sistema de Controle de Caixas"
    
    # **CORREÇÃO: URLs corretas do GitHub**
    UPDATE_SERVER = "https://api.github.com/repos/esc4n0rx/HBTrackerx"
    VERSION_CHECK_URL = f"{UPDATE_SERVER}/releases/latest"
    
    @staticmethod
    def get_current_version():
        """Retorna a versão atual da aplicação"""
        return Version.CURRENT_VERSION
    
    @staticmethod
    def get_app_info():
        """Retorna informações da aplicação"""
        return {
            "name": Version.APP_NAME,
            "version": Version.CURRENT_VERSION,
            "build_date": "2025-06-12 13:10:07",
            "description": "Sistema completo de controle de caixas com inventário inicial, fluxo visual para CDs e Lojas, e atualizações automáticas",
            "author": "Desenvolvedor Python",
            "license": "Proprietário",
            "website": "https://github.com/esc4n0rx/HBTrackerx",
            "support_email": "suporte@exemplo.com"
        }

class UpdateChecker(QThread):
    """Thread para verificar atualizações em background - VERSÃO CORRIGIDA"""
    
    update_available = pyqtSignal(dict)
    update_error = pyqtSignal(str)
    no_updates = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
    def run(self):
        """Verifica se há atualizações disponíveis - VERSÃO CORRIGIDA"""
        try:
            print(f"🔍 Verificando atualizações no GitHub...")
            print(f"🔗 URL: {Version.VERSION_CHECK_URL}")
            
            # **CORREÇÃO CRÍTICA: Headers corretos para GitHub API**
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'HBTracker-UpdateChecker/1.0',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # **CORREÇÃO: Timeout maior e retry logic**
            session = requests.Session()
            session.headers.update(headers)
            
            for attempt in range(3):  # Até 3 tentativas
                try:
                    print(f"🔄 Tentativa {attempt + 1}/3...")
                    response = session.get(Version.VERSION_CHECK_URL, timeout=30)
                    print(f"📊 Status da resposta: {response.status_code}")
                    
                    if response.status_code == 403:
                        print("⚠️ Erro 403 - tentando contornar rate limit...")
                        import time
                        time.sleep(2)  # Espera 2 segundos
                        continue
                    
                    if response.status_code == 404:
                        self.update_error.emit("Repositório não encontrado ou não há releases disponíveis")
                        return
                    
                    response.raise_for_status()
                    break  # Sucesso, sai do loop
                    
                except requests.exceptions.Timeout:
                    if attempt == 2:  # Última tentativa
                        raise
                    print(f"⏱️ Timeout na tentativa {attempt + 1}, tentando novamente...")
                    continue
                except requests.exceptions.RequestException as e:
                    if attempt == 2:  # Última tentativa
                        raise
                    print(f"❌ Erro na tentativa {attempt + 1}: {e}")
                    continue
            
            release_info = response.json()
            print(f"📦 Release encontrado: {release_info.get('tag_name', 'N/A')}")
            
            # **CORREÇÃO: Extrai versão do tag_name**
            server_version = release_info.get('tag_name', '').replace('v', '')
            # version.py - CONTINUAÇÃO DA CORREÇÃO
            current_version = Version.get_current_version()
            
            print(f"📊 Versão atual: {current_version}")
            print(f"📊 Versão servidor: {server_version}")
            
            if self.is_newer_version(server_version, current_version):
                print("✅ Nova versão disponível!")
                
                # **CORREÇÃO: Monta informações da atualização**
                update_info = {
                    "version": server_version,
                    "release_date": release_info.get('published_at', '').split('T')[0],
                    "changelog": release_info.get('body', 'Sem informações de changelog'),
                    "download_url": None,
                    "file_size": "N/A"
                }
                
                # **CORREÇÃO CRÍTICA: Busca arquivo de download correto**
                assets = release_info.get('assets', [])
                print(f"📦 Assets encontrados: {len(assets)}")
                
                for asset in assets:
                    asset_name = asset.get('name', '')
                    print(f"  - {asset_name}")
                    
                    # **CORREÇÃO: Aceita diferentes formatos**
                    if (asset_name.endswith('.zip') or asset_name.endswith('.exe')) and \
                       ('ControleEstoque' in asset_name or 'HBTracker' in asset_name):
                        update_info["download_url"] = asset.get('browser_download_url')
                        update_info["file_size"] = f"{asset.get('size', 0) / 1024 / 1024:.1f} MB"
                        print(f"✅ Arquivo de download encontrado: {asset_name}")
                        break
                
                if not update_info["download_url"]:
                    # **CORREÇÃO: Fallback para qualquer arquivo .zip/.exe**
                    for asset in assets:
                        asset_name = asset.get('name', '')
                        if asset_name.endswith('.zip') or asset_name.endswith('.exe'):
                            update_info["download_url"] = asset.get('browser_download_url')
                            update_info["file_size"] = f"{asset.get('size', 0) / 1024 / 1024:.1f} MB"
                            print(f"⚠️ Usando arquivo alternativo: {asset_name}")
                            break
                
                if not update_info["download_url"]:
                    self.update_error.emit("Nenhum arquivo de atualização encontrado no release")
                    return
                
                self.update_available.emit(update_info)
            else:
                print("✅ Aplicação está atualizada")
                self.no_updates.emit()
                
        except requests.exceptions.Timeout:
            error_msg = "Timeout na conexão com GitHub. Verifique sua internet."
            print(f"❌ {error_msg}")
            self.update_error.emit(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "Erro de conexão com GitHub. Verifique sua internet."
            print(f"❌ {error_msg}")
            self.update_error.emit(error_msg)
        except requests.exceptions.HTTPError as e:
            if "403" in str(e):
                error_msg = "GitHub rate limit atingido. Tente novamente em alguns minutos."
            else:
                error_msg = f"Erro HTTP: {str(e)}"
            print(f"❌ {error_msg}")
            self.update_error.emit(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição: {str(e)}"
            print(f"❌ {error_msg}")
            self.update_error.emit(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Erro ao processar resposta do GitHub: {str(e)}"
            print(f"❌ {error_msg}")
            self.update_error.emit(error_msg)
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            print(f"❌ {error_msg}")
            self.update_error.emit(error_msg)
    
    def is_newer_version(self, server_version, current_version):
        """CORREÇÃO: Compara versões corretamente"""
        try:
            # Remove 'v' se presente e normaliza
            server_clean = server_version.replace('v', '').strip()
            current_clean = current_version.replace('v', '').strip()
            
            print(f"🔍 Comparando versões: '{current_clean}' vs '{server_clean}'")
            
            # Divide em partes numéricas
            server_parts = [int(x) for x in server_clean.split('.')]
            current_parts = [int(x) for x in current_clean.split('.')]
            
            # Normaliza o tamanho das listas
            max_len = max(len(server_parts), len(current_parts))
            server_parts.extend([0] * (max_len - len(server_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            print(f"🔍 Partes servidor: {server_parts}")
            print(f"🔍 Partes atual: {current_parts}")
            
            is_newer = server_parts > current_parts
            print(f"🔍 É mais nova? {is_newer}")
            
            return is_newer
        except ValueError as e:
            print(f"❌ Erro na comparação de versões: {e}")
            return False

class UpdateDownloader(QThread):
    """Thread para baixar e instalar atualizações - VERSÃO CORRIGIDA"""
    
    download_progress = pyqtSignal(int)
    download_finished = pyqtSignal()
    download_error = pyqtSignal(str)
    installation_progress = pyqtSignal(str)
    installation_finished = pyqtSignal()
    
    def __init__(self, update_info):
        super().__init__()
        self.update_info = update_info
        
    def run(self):
        """Baixa e instala a atualização - VERSÃO CORRIGIDA"""
        try:
            self.installation_progress.emit("🔄 Iniciando download...")
            
            # URL do arquivo de atualização
            download_url = self.update_info.get("download_url")
            if not download_url:
                raise Exception("URL de download não encontrada")
            
            print(f"📥 Baixando de: {download_url}")
            
            # Cria diretório temporário
            temp_dir = tempfile.mkdtemp()
            file_extension = ".zip" if download_url.endswith('.zip') else ".exe"
            update_file = os.path.join(temp_dir, f"update{file_extension}")
            
            self.installation_progress.emit("📥 Baixando atualização...")
            
            # **CORREÇÃO CRÍTICA: Headers e configuração melhorada**
            headers = {
                'User-Agent': 'HBTracker-Updater/1.0',
                'Accept': 'application/octet-stream, */*',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache'
            }
            
            # **CORREÇÃO: Session com retry logic**
            session = requests.Session()
            session.headers.update(headers)
            
            for attempt in range(3):
                try:
                    print(f"🔄 Tentativa de download {attempt + 1}/3...")
                    
                    # **CORREÇÃO: Configurações de timeout e stream**
                    response = session.get(
                        download_url, 
                        stream=True, 
                        timeout=(30, 300),  # Connect timeout: 30s, Read timeout: 5min
                        allow_redirects=True
                    )
                    
                    if response.status_code == 403:
                        print("⚠️ Erro 403 no download - tentando novamente...")
                        import time
                        time.sleep(5)  # Espera mais tempo
                        continue
                    
                    response.raise_for_status()
                    break  # Sucesso
                    
                except requests.exceptions.RequestException as e:
                    if attempt == 2:  # Última tentativa
                        raise
                    print(f"❌ Erro na tentativa {attempt + 1}: {e}")
                    import time
                    time.sleep(3)
                    continue
            
            # **CORREÇÃO: Download com progress melhorado**
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            print(f"📊 Tamanho total: {total_size} bytes")
            
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.download_progress.emit(progress)
                        
                        # **CORREÇÃO: Feedback visual durante download**
                        if downloaded % (1024 * 1024) == 0:  # A cada MB
                            mb_downloaded = downloaded / (1024 * 1024)
                            mb_total = total_size / (1024 * 1024) if total_size > 0 else 0
                            self.installation_progress.emit(f"📥 Baixando: {mb_downloaded:.1f}MB/{mb_total:.1f}MB")
            
            print(f"✅ Download concluído: {downloaded} bytes")
            self.download_finished.emit()
            
            # **CORREÇÃO: Verifica integridade do arquivo**
            if not os.path.exists(update_file) or os.path.getsize(update_file) == 0:
                raise Exception("Arquivo de atualização não foi baixado corretamente")
            
            file_size = os.path.getsize(update_file)
            print(f"📊 Arquivo baixado: {file_size} bytes")
            
            if file_size < 1024:  # Arquivo muito pequeno
                raise Exception("Arquivo de atualização parece estar corrompido (muito pequeno)")
            
            # **CORREÇÃO: Tratamento diferente para .zip e .exe**
            if file_extension == ".zip":
                self.installation_progress.emit("📦 Extraindo atualização...")
                
                # Extrai atualização
                extract_dir = os.path.join(temp_dir, "extracted")
                
                try:
                    with zipfile.ZipFile(update_file, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                except zipfile.BadZipFile:
                    raise Exception("Arquivo ZIP está corrompido")
                
                print(f"📦 Arquivos extraídos em: {extract_dir}")
                
                self.installation_progress.emit("🔄 Aplicando atualização...")
                
                # Aplica atualização
                self.apply_update(extract_dir)
                
            else:  # .exe
                self.installation_progress.emit("🔄 Executando instalador...")
                
                # **CORREÇÃO: Para .exe, simplesmente executa**
                try:
                    import subprocess
                    subprocess.run([update_file], check=True)
                except subprocess.CalledProcessError as e:
                    raise Exception(f"Falha ao executar instalador: {e}")
            
            self.installation_progress.emit("✅ Atualização concluída!")
            self.installation_finished.emit()
            
        except Exception as e:
            error_msg = f"Erro na atualização: {str(e)}"
            print(f"❌ {error_msg}")
            self.download_error.emit(error_msg)
        finally:
            # Limpa arquivos temporários
            try:
                if 'temp_dir' in locals():
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    print("🧹 Arquivos temporários limpos")
            except:
                pass
    
    def apply_update(self, source_dir):
        """Aplica a atualização substituindo arquivos - VERSÃO MELHORADA"""
        try:
            # **CORREÇÃO: Detecta se é executável compilado ou script Python**
            if getattr(sys, 'frozen', False):
                # Aplicação compilada
                current_dir = os.path.dirname(sys.executable)
                current_executable = sys.executable
            else:
                # Script Python
                current_dir = os.path.dirname(os.path.abspath(__file__))
                current_executable = None
            
            print(f"📁 Diretório atual: {current_dir}")
            print(f"📁 Diretório fonte: {source_dir}")
            
            # **CORREÇÃO: Lista arquivos para atualizar de forma mais inteligente**
            files_to_update = []
            
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    source_path = os.path.join(root, file)
                    rel_path = os.path.relpath(source_path, source_dir)
                    dest_path = os.path.join(current_dir, rel_path)
                    
                    # **CORREÇÃO: Filtros mais específicos**
                    if (file.endswith(('.exe', '.py', '.dll', '.pyd')) or 
                        file in ['version.json', 'config.ini'] or
                        not '.' in file):  # Arquivos sem extensão podem ser executáveis Unix
                        files_to_update.append((source_path, dest_path))
            
            print(f"📋 Arquivos para atualizar: {len(files_to_update)}")
            
            if not files_to_update:
                # **CORREÇÃO: Se não encontrou nada, tenta copiar tudo**
                print("⚠️ Nenhum arquivo específico encontrado, copiando tudo...")
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        source_path = os.path.join(root, file)
                        rel_path = os.path.relpath(source_path, source_dir)
                        dest_path = os.path.join(current_dir, rel_path)
                        files_to_update.append((source_path, dest_path))
            
            if not files_to_update:
                raise Exception("Nenhum arquivo encontrado para atualização")
            
            # **CORREÇÃO: Cria backup melhor**
            backup_dir = os.path.join(current_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(backup_dir, exist_ok=True)
            print(f"📋 Pasta de backup: {backup_dir}")
            
            # **CORREÇÃO: Atualiza arquivos com melhor tratamento de erros**
            updated_count = 0
            for source_path, dest_path in files_to_update:
                try:
                    # **CORREÇÃO: Não sobrescreve executável em uso**
                    if current_executable and os.path.samefile(dest_path, current_executable):
                        print(f"⚠️ Pulando executável em uso: {dest_path}")
                        continue
                    
                    # Backup do arquivo original se existir
                    if os.path.exists(dest_path):
                        backup_path = os.path.join(backup_dir, os.path.relpath(dest_path, current_dir))
                        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                        shutil.copy2(dest_path, backup_path)
                        print(f"📋 Backup: {os.path.basename(dest_path)}")
                    
                    # Copia novo arquivo
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(source_path, dest_path)
                    print(f"✅ Atualizado: {os.path.basename(dest_path)}")
                    updated_count += 1
                    
                except Exception as e:
                    print(f"⚠️ Erro ao atualizar {os.path.basename(dest_path)}: {e}")
                    # Continua com outros arquivos
            
            print(f"✅ {updated_count} arquivos atualizados com sucesso")
            
            if updated_count == 0:
                raise Exception("Nenhum arquivo foi atualizado")
                    
        except Exception as e:
            print(f"❌ Erro na aplicação da atualização: {e}")
            raise