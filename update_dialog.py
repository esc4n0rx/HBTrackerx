# update_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTextEdit, QProgressBar, QGroupBox,
                            QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
from version import Version, UpdateChecker, UpdateDownloader

class UpdateDialog(QDialog):
    """Diálogo para gerenciar atualizações"""
    
    def __init__(self, parent=None, auto_check=False):
        super().__init__(parent)
        self.parent_window = parent
        self.auto_check = auto_check
        self.update_info = None
        
        self.setWindowTitle("Gerenciador de Atualizações")
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        self.init_ui()
        
        # Inicia verificação automaticamente se solicitado
        if auto_check:
            QTimer.singleShot(500, self.check_updates)
    
    def init_ui(self):
        """Inicializa interface do usuário"""
        layout = QVBoxLayout(self)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        # Ícone e título
        title_layout = QVBoxLayout()
        title = QLabel("🔄 Gerenciador de Atualizações")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title_layout.addWidget(title)
        
        subtitle = QLabel("Mantenha sua aplicação sempre atualizada")
        subtitle.setStyleSheet("color: #666; font-size: 12px;")
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Informações da versão atual
        current_info_group = QGroupBox("📊 Versão Atual")
        current_info_layout = QVBoxLayout(current_info_group)
        
        app_info = Version.get_app_info()
        current_info_layout.addWidget(QLabel(f"<b>Aplicação:</b> {app_info['name']}"))
        current_info_layout.addWidget(QLabel(f"<b>Versão:</b> {app_info['version']}"))
        current_info_layout.addWidget(QLabel(f"<b>Data de Build:</b> {app_info['build_date']}"))
        
        layout.addWidget(current_info_group)
        
        # Status de verificação
        self.status_group = QGroupBox("🔍 Status da Verificação")
        self.status_layout = QVBoxLayout(self.status_group)
        
        self.status_label = QLabel("⏳ Pronto para verificar atualizações")
        self.status_label.setWordWrap(True)
        self.status_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(self.status_group)
        
        # Área de detalhes da atualização (inicialmente oculta)
        self.update_details_group = QGroupBox("📝 Detalhes da Atualização")
        self.update_details_layout = QVBoxLayout(self.update_details_group)
        
        self.update_text = QTextEdit()
        self.update_text.setMaximumHeight(150)
        self.update_text.setReadOnly(True)
        self.update_details_layout.addWidget(self.update_text)
        
        self.update_details_group.setVisible(False)
        layout.addWidget(self.update_details_group)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.check_button = QPushButton("🔍 Verificar Atualizações")
        self.check_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.check_button.clicked.connect(self.check_updates)
        button_layout.addWidget(self.check_button)
        
        self.install_button = QPushButton("📥 Instalar Atualização")
        self.install_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.install_button.clicked.connect(self.install_update)
        self.install_button.setVisible(False)
        button_layout.addWidget(self.install_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("❌ Fechar")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def check_updates(self):
        """Inicia verificação de atualizações"""
        self.check_button.setEnabled(False)
        self.status_label.setText("🔄 Verificando atualizações...")
        self.update_details_group.setVisible(False)
        self.install_button.setVisible(False)
        
        # Inicia thread de verificação
        self.update_checker = UpdateChecker()
        self.update_checker.update_available.connect(self.on_update_available)
        self.update_checker.no_updates.connect(self.on_no_updates)
        self.update_checker.update_error.connect(self.on_update_error)
        self.update_checker.start()
    
    def on_update_available(self, update_info):
        """Chamado quando uma atualização está disponível"""
        self.update_info = update_info
        self.check_button.setEnabled(True)
        
        version = update_info.get("version", "Desconhecida")
        release_date = update_info.get("release_date", "Desconhecida")
        
        self.status_label.setText(f"✅ Nova versão disponível: {version}")
        
        # Mostra detalhes da atualização
        details = f"<b>Versão:</b> {version}<br>"
        details += f"<b>Data de Lançamento:</b> {release_date}<br><br>"
        details += f"<b>Novidades:</b><br>"
        details += update_info.get("changelog", "Nenhuma informação disponível.")
        
        self.update_text.setHtml(details)
        self.update_details_group.setVisible(True)
        self.install_button.setVisible(True)
        
        # Se for verificação automática, pergunta se quer instalar
        if self.auto_check:
            reply = QMessageBox.question(
                self, "Atualização Disponível",
                f"Nova versão {version} disponível!\n\nDeseja instalar agora?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.install_update()
    
    def on_no_updates(self):
        """Chamado quando não há atualizações"""
        self.check_button.setEnabled(True)
        self.status_label.setText("✅ Sua aplicação está atualizada!")
        
        if not self.auto_check:
            QMessageBox.information(
                self, "Sem Atualizações",
                "Você já possui a versão mais recente da aplicação."
            )
    
    def on_update_error(self, error_message):
        """Chamado quando há erro na verificação"""
        self.check_button.setEnabled(True)
        self.status_label.setText(f"❌ Erro: {error_message}")
        
        if not self.auto_check:
            QMessageBox.warning(
                self, "Erro na Verificação",
                f"Não foi possível verificar atualizações:\n\n{error_message}"
            )
    
    def install_update(self):
        """Inicia instalação da atualização"""
        if not self.update_info:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar Instalação",
            "A aplicação será fechada para aplicar a atualização.\n\n"
            "Deseja continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.install_button.setEnabled(False)
        self.check_button.setEnabled(False)
        self.status_label.setText("📥 Iniciando download...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Inicia thread de download
        self.downloader = UpdateDownloader(self.update_info)
        self.downloader.download_progress.connect(self.progress_bar.setValue)
        self.downloader.download_finished.connect(self.on_download_finished)
        self.downloader.installation_progress.connect(self.status_label.setText)
        self.downloader.installation_finished.connect(self.on_installation_finished)
        self.downloader.download_error.connect(self.on_download_error)
        self.downloader.start()
    
    def on_download_finished(self):
        """Chamado quando download termina"""
        self.progress_bar.setVisible(False)
    
    def on_installation_finished(self):
        """Chamado quando instalação termina"""
        QMessageBox.information(
            self, "Atualização Concluída",
            "Atualização instalada com sucesso!\n\n"
            "A aplicação será reiniciada."
        )
        
        # Reinicia aplicação
        if self.parent_window:
            self.parent_window.close()
        self.close()
        
        # Aqui você pode adicionar código para reiniciar a aplicação
        import subprocess
        import sys
        subprocess.Popen([sys.executable] + sys.argv)
    
    def on_download_error(self, error_message):
        """Chamado quando há erro no download"""
        self.install_button.setEnabled(True)
        self.check_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"❌ Erro na instalação: {error_message}")
        
        QMessageBox.critical(
            self, "Erro na Instalação",
            f"Falha ao instalar atualização:\n\n{error_message}"
        )