# version.py
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
    
    # Versão atual da aplicação
    CURRENT_VERSION = "0.0.2"
    APP_NAME = "Sistema de Controle de Caixas"
    
    # URLs do servidor de atualizações
    UPDATE_SERVER = "https://raw.githubusercontent.com/esc4n0rx/HBTrackerx/master"
    VERSION_CHECK_URL = f"{UPDATE_SERVER}/version.json"
    
    @staticmethod
    def get_current_version():
        """Retorna a versão atual da aplicação"""
        return Version.CURRENT_VERSION
    
    @staticmethod
    def get_app_info():
        """Retorna informações da aplicação - VERSÃO MELHORADA"""
        return {
            "name": Version.APP_NAME,
            "version": Version.CURRENT_VERSION,
            "build_date": "11/06/2025",
            "description": "Sistema completo de controle de caixas com inventário inicial, fluxo visual e atualizações automáticas",
            "author": "Desenvolvedor Python",
            "license": "Proprietário",
            "website": "https://github.com/esc4n0rx/HBTrackerx",
            "support_email": "suporte@exemplo.com"
        }

class UpdateChecker(QThread):
    """Thread para verificar atualizações em background"""
    
    update_available = pyqtSignal(dict)
    update_error = pyqtSignal(str)
    no_updates = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
    def run(self):
        """Verifica se há atualizações disponíveis"""
        try:
            print(f"🔍 Verificando atualizações...")
            
            # Faz requisição para o servidor
            response = requests.get(Version.VERSION_CHECK_URL, timeout=10)
            response.raise_for_status()
            
            server_info = response.json()
            
            current_version = Version.get_current_version()
            server_version = server_info.get("version", "0.0.0")
            
            print(f"📊 Versão atual: {current_version}")
            print(f"📊 Versão servidor: {server_version}")
            
            if self.is_newer_version(server_version, current_version):
                print("✅ Nova versão disponível!")
                self.update_available.emit(server_info)
            else:
                print("✅ Aplicação está atualizada")
                self.no_updates.emit()
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro de conexão: {str(e)}"
            print(f"❌ {error_msg}")
            self.update_error.emit(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Erro ao processar dados: {str(e)}"
            print(f"❌ {error_msg}")
            self.update_error.emit(error_msg)
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            print(f"❌ {error_msg}")
            self.update_error.emit(error_msg)
    
    def is_newer_version(self, server_version, current_version):
        """Compara versões para determinar se server_version é mais nova"""
        try:
            server_parts = [int(x) for x in server_version.split('.')]
            current_parts = [int(x) for x in current_version.split('.')]
            
            # Normaliza o tamanho das listas
            max_len = max(len(server_parts), len(current_parts))
            server_parts.extend([0] * (max_len - len(server_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return server_parts > current_parts
        except ValueError:
            return False

class UpdateDownloader(QThread):
    """Thread para baixar e instalar atualizações"""
    
    download_progress = pyqtSignal(int)
    download_finished = pyqtSignal()
    download_error = pyqtSignal(str)
    installation_progress = pyqtSignal(str)
    installation_finished = pyqtSignal()
    
    def __init__(self, update_info):
        super().__init__()
        self.update_info = update_info
        
    def run(self):
        """Baixa e instala a atualização"""
        try:
            self.installation_progress.emit("🔄 Iniciando download...")
            
            # URL do arquivo de atualização
            download_url = self.update_info.get("download_url")
            if not download_url:
                raise Exception("URL de download não encontrada")
            
            # Cria diretório temporário
            temp_dir = tempfile.mkdtemp()
            update_file = os.path.join(temp_dir, "update.zip")
            
            self.installation_progress.emit("📥 Baixando atualização...")
            
            # Download com progress
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.download_progress.emit(progress)
            
            self.download_finished.emit()
            self.installation_progress.emit("📦 Extraindo atualização...")
            
            # Extrai atualização
            extract_dir = os.path.join(temp_dir, "extracted")
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            self.installation_progress.emit("🔄 Aplicando atualização...")
            
            # Aplica atualização
            self.apply_update(extract_dir)
            
            self.installation_progress.emit("✅ Atualização concluída!")
            self.installation_finished.emit()
            
        except Exception as e:
            error_msg = f"Erro na atualização: {str(e)}"
            print(f"❌ {error_msg}")
            self.download_error.emit(error_msg)
        finally:
            # Limpa arquivos temporários
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
    
    def apply_update(self, source_dir):
        """Aplica a atualização substituindo arquivos"""
        current_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
        
        # Lista de arquivos para atualizar
        files_to_update = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                source_path = os.path.join(root, file)
                rel_path = os.path.relpath(source_path, source_dir)
                dest_path = os.path.join(current_dir, rel_path)
                files_to_update.append((source_path, dest_path))
        
        # Cria backup dos arquivos existentes
        backup_dir = os.path.join(current_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(backup_dir, exist_ok=True)
        
        for source_path, dest_path in files_to_update:
            try:
                # Backup do arquivo original se existir
                if os.path.exists(dest_path):
                    backup_path = os.path.join(backup_dir, os.path.relpath(dest_path, current_dir))
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    shutil.copy2(dest_path, backup_path)
                
                # Copia novo arquivo
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(source_path, dest_path)
                
            except Exception as e:
                print(f"⚠️ Erro ao atualizar {dest_path}: {e}")