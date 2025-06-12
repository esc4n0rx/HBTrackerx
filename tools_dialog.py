# tools_dialog.py - Tela de Ferramentas com Abas
import pandas as pd
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, 
                            QFileDialog, QMessageBox, QTabWidget, QSpinBox, QComboBox,
                            QColorDialog, QCheckBox, QSlider, QWidget, QFormLayout,
                            QLineEdit, QTextEdit, QScrollArea)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from version import Version
from appearance_manager import AppearanceManager

class ToolsDialog(QDialog):
    """Diálogo de ferramentas com abas organizadas"""
    
    # Sinais para comunicação com a janela principal
    database_cleared = pyqtSignal()
    appearance_changed = pyqtSignal(dict)  # Emite mudanças de aparência
    
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db = db_instance
        self.parent_window = parent
        
        # **MELHORIA: Carrega configurações salvas**
        self.appearance_settings = AppearanceManager.load_settings()
        
        self.setWindowTitle("🔧 Ferramentas do Sistema")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        self.init_ui()
        self.load_current_appearance()

    def init_ui(self):
        """Inicializa interface com abas"""
        layout = QVBoxLayout(self)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        title = QLabel("🔧 Ferramentas do Sistema")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Informação da versão
        version_info = Version.get_app_info()
        version_label = QLabel(f"v{version_info['version']}")
        version_label.setStyleSheet("color: #666; font-size: 12px;")
        header_layout.addWidget(version_label)
        
        layout.addLayout(header_layout)
        
        # Widget de abas
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        
        # Criar abas
        self.create_data_management_tab()
        self.create_appearance_tab()
        self.create_maintenance_tab()
        self.create_about_tab()
        
        layout.addWidget(self.tabs)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        # Aplicar mudanças
        self.apply_button = QPushButton("✅ Aplicar Mudanças")
        self.apply_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
        """)
        self.apply_button.clicked.connect(self.apply_changes)
        button_layout.addWidget(self.apply_button)
        
        button_layout.addStretch()
        
        # Fechar
        close_button = QPushButton("❌ Fechar")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)

    def create_data_management_tab(self):
        """Aba de Gerenciamento de Dados"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grupo de Upload de Inventário
        inventory_group = QGroupBox("📦 Inventário Inicial")
        inventory_layout = QVBoxLayout()
        
        inventory_info = QLabel(
            "Upload do inventário inicial das lojas (Data: 08/06/2025)\n"
            "Formato: loja_nome, ativo, quantidade\n"
            "Ativos aceitos: HB623, HB618\n"
            "Exemplo: CABO FRIO, HB623, 100"
        )
        inventory_info.setWordWrap(True)
        inventory_info.setStyleSheet("background-color: #e8f4fd; padding: 10px; border-radius: 4px;")
        inventory_layout.addWidget(inventory_info)
        
        inventory_buttons = QHBoxLayout()
        
        self.upload_inventory_button = QPushButton("📤 Upload Inventário (.csv/.xlsx)")
        self.upload_inventory_button.setStyleSheet("background-color: #5cb85c; color: white; padding: 8px 16px;")
        self.upload_inventory_button.clicked.connect(self.upload_inventory)
        inventory_buttons.addWidget(self.upload_inventory_button)
        
        self.clear_inventory_button = QPushButton("🗑️ Limpar Inventário")
        self.clear_inventory_button.setStyleSheet("background-color: #f0ad4e; color: white; padding: 8px 16px;")
        self.clear_inventory_button.clicked.connect(self.clear_inventory)
        inventory_buttons.addWidget(self.clear_inventory_button)
        
        inventory_layout.addLayout(inventory_buttons)
        inventory_group.setLayout(inventory_layout)
        layout.addWidget(inventory_group)
        
        # Grupo de Upload de Movimentos
        movements_group = QGroupBox("🔄 Movimentos")
        movements_layout = QVBoxLayout()
        
        movements_info = QLabel(
            "Upload de movimentos entre CDs e Lojas\n"
            "Formato: Data, Guia, Transação, LOCAL Origem, LOCAL Destino, Tipo Movimento, RTI, Nota Fiscal, Quant.\n"
            "Suporta formatos .csv e .xlsx"
        )
        movements_info.setWordWrap(True)
        movements_info.setStyleSheet("background-color: #fff3cd; padding: 10px; border-radius: 4px;")
        movements_layout.addWidget(movements_info)
        
        movements_buttons = QHBoxLayout()
        
        self.upload_movements_button = QPushButton("📤 Upload Movimentos (.csv/.xlsx)")
        self.upload_movements_button.setStyleSheet("background-color: #007bff; color: white; padding: 8px 16px;")
        self.upload_movements_button.clicked.connect(self.upload_movements)
        movements_buttons.addWidget(self.upload_movements_button)
        
        movements_layout.addLayout(movements_buttons)
        movements_group.setLayout(movements_layout)
        layout.addWidget(movements_group)
        
        # Grupo de Exportação
        export_group = QGroupBox("💾 Exportação")
        export_layout = QVBoxLayout()
        
        export_buttons = QHBoxLayout()
        
        self.export_complete_button = QPushButton("📊 Relatório Completo")
        self.export_complete_button.setStyleSheet("background-color: #6c757d; color: white; padding: 8px 16px;")
        self.export_complete_button.clicked.connect(self.export_complete_report)
        export_buttons.addWidget(self.export_complete_button)
        
        self.export_inventory_button = QPushButton("📦 Apenas Inventário")
        self.export_inventory_button.setStyleSheet("background-color: #17a2b8; color: white; padding: 8px 16px;")
        self.export_inventory_button.clicked.connect(self.export_inventory_only)
        export_buttons.addWidget(self.export_inventory_button)
        
        export_layout.addLayout(export_buttons)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "📁 Dados")

    def create_appearance_tab(self):
        """Aba de Configurações de Aparência"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        
        # Área de scroll para muitas opções
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # Grupo de Fontes
        font_group = QGroupBox("🔤 Configurações de Fonte")
        font_layout = QFormLayout()
        
        # Tamanho da fonte
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 24)
        self.font_size_spinbox.setValue(self.appearance_settings['font_size'])
        self.font_size_spinbox.valueChanged.connect(self.preview_changes)
        font_layout.addRow("Tamanho da Fonte:", self.font_size_spinbox)
        
        # Família da fonte
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(['Arial', 'Helvetica', 'Times New Roman', 'Calibri', 'Segoe UI'])
        self.font_family_combo.setCurrentText(self.appearance_settings['font_family'])
        self.font_family_combo.currentTextChanged.connect(self.preview_changes)
        font_layout.addRow("Família da Fonte:", self.font_family_combo)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # Grupo de Cores
        colors_group = QGroupBox("🎨 Configurações de Cores")
        colors_layout = QFormLayout()
        
        # Cor primária
        self.primary_color_button = QPushButton("Cor Primária")
        self.primary_color_button.setStyleSheet(f"background-color: {self.appearance_settings['primary_color']}; color: white; padding: 8px;")
        self.primary_color_button.clicked.connect(lambda: self.choose_color('primary_color'))
        colors_layout.addRow("Cor Primária:", self.primary_color_button)
        
        # Cor de fundo
        self.background_color_button = QPushButton("Cor de Fundo")
        self.background_color_button.setStyleSheet(f"background-color: {self.appearance_settings['background_color']}; color: black; padding: 8px;")
        self.background_color_button.clicked.connect(lambda: self.choose_color('background_color'))
        colors_layout.addRow("Cor de Fundo:", self.background_color_button)
        
        # Cor do texto
        self.text_color_button = QPushButton("Cor do Texto")
        self.text_color_button.setStyleSheet(f"background-color: {self.appearance_settings['text_color']}; color: white; padding: 8px;")
        self.text_color_button.clicked.connect(lambda: self.choose_color('text_color'))
        colors_layout.addRow("Cor do Texto:", self.text_color_button)
        
        colors_group.setLayout(colors_layout)
        layout.addWidget(colors_group)
        
        # Grupo de Temas
        theme_group = QGroupBox("🌙 Tema")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Claro', 'Escuro', 'Automático'])
        self.theme_combo.setCurrentText(self.appearance_settings['theme'])
        self.theme_combo.currentTextChanged.connect(self.preview_changes)
        theme_layout.addRow("Tema:", self.theme_combo)
        
        # Alto contraste
        self.high_contrast_checkbox = QCheckBox("Ativar Alto Contraste")
        self.high_contrast_checkbox.setChecked(self.appearance_settings['high_contrast'])
        self.high_contrast_checkbox.toggled.connect(self.preview_changes)
        theme_layout.addRow("Acessibilidade:", self.high_contrast_checkbox)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Área de preview
        preview_group = QGroupBox("👁️ Visualização")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("Este é um exemplo de como o texto aparecerá\ncom as configurações selecionadas.")
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("padding: 20px; border: 1px solid #ccc; border-radius: 4px;")
        preview_layout.addWidget(self.preview_label)
        
        self.preview_button = QPushButton("Botão de Exemplo")
        self.preview_button.setStyleSheet("padding: 8px 16px;")
        preview_layout.addWidget(self.preview_button)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Botões de reset
        reset_layout = QHBoxLayout()
        
        reset_defaults_button = QPushButton("🔄 Restaurar Padrões")
        reset_defaults_button.clicked.connect(self.reset_to_defaults)
        reset_layout.addWidget(reset_defaults_button)
        
        reset_layout.addStretch()
        
        layout.addLayout(reset_layout)
        layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        self.tabs.addTab(tab, "🎨 Aparência")

    def create_maintenance_tab(self):
        """Aba de Manutenção"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grupo de Limpeza
        cleanup_group = QGroupBox("🧹 Limpeza do Sistema")
        cleanup_layout = QVBoxLayout()
        
        cleanup_info = QLabel(
            "Ferramentas para limpeza e manutenção da base de dados.\n"
            "⚠️ ATENÇÃO: Essas operações são irreversíveis!"
        )
        cleanup_info.setWordWrap(True)
        cleanup_info.setStyleSheet("background-color: #fff3cd; padding: 10px; border-radius: 4px; color: #856404;")
        cleanup_layout.addWidget(cleanup_info)
        
        cleanup_buttons = QVBoxLayout()
        
        self.clear_movements_button = QPushButton("🗑️ Limpar Apenas Movimentos")
        self.clear_movements_button.setStyleSheet("background-color: #f0ad4e; color: white; padding: 8px 16px;")
        self.clear_movements_button.clicked.connect(self.clear_movements_only)
        cleanup_buttons.addWidget(self.clear_movements_button)
        
        self.clear_inventory_only_button = QPushButton("🗑️ Limpar Apenas Inventário")
        self.clear_inventory_only_button.setStyleSheet("background-color: #f0ad4e; color: white; padding: 8px 16px;")
        self.clear_inventory_only_button.clicked.connect(self.clear_inventory)
        cleanup_buttons.addWidget(self.clear_inventory_only_button)
        
        cleanup_layout.addLayout(cleanup_buttons)
        cleanup_group.setLayout(cleanup_layout)
        layout.addWidget(cleanup_group)
        
        # Zona de Perigo
        danger_zone_group = QGroupBox("☢️ Zona de Perigo")
        danger_zone_group.setStyleSheet("QGroupBox { color: #dc3545; font-weight: bold; }")
        danger_layout = QVBoxLayout()
        
        danger_label = QLabel(
            "⚠️ ATENÇÃO: Esta ação removerá permanentemente TODOS os dados!\n"
            "Isso inclui movimentos, inventários e configurações.\n"
            "Esta operação NÃO pode ser desfeita."
        )
        danger_label.setWordWrap(True)
        danger_label.setStyleSheet("background-color: #f8d7da; padding: 15px; border-radius: 4px; color: #721c24; font-weight: bold;")
        danger_layout.addWidget(danger_label)
        
        self.clear_db_button = QPushButton("☢️ LIMPAR TODA A BASE DE DADOS")
        self.clear_db_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.clear_db_button.clicked.connect(self.clear_database)
        danger_layout.addWidget(self.clear_db_button)
        
        danger_zone_group.setLayout(danger_layout)
        layout.addWidget(danger_zone_group)
        
        # Grupo de Backup
        backup_group = QGroupBox("💾 Backup e Restauração")
        backup_layout = QVBoxLayout()
        
        backup_buttons = QHBoxLayout()
        
        self.create_backup_button = QPushButton("💾 Criar Backup")
        self.create_backup_button.setStyleSheet("background-color: #17a2b8; color: white; padding: 8px 16px;")
        self.create_backup_button.clicked.connect(self.create_backup)
        backup_buttons.addWidget(self.create_backup_button)
        
        self.restore_backup_button = QPushButton("📤 Restaurar Backup")
        self.restore_backup_button.setStyleSheet("background-color: #28a745; color: white; padding: 8px 16px;")
        self.restore_backup_button.clicked.connect(self.restore_backup)
        backup_buttons.addWidget(self.restore_backup_button)
        
        backup_layout.addLayout(backup_buttons)
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "🛠️ Manutenção")

    def create_about_tab(self):
        """Aba Sobre"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Área de scroll para informações
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        content_layout = QVBoxLayout(scroll_widget)
        
        # Informações da aplicação
        app_info = Version.get_app_info()
        
        about_text = f"""
        <div style="text-align: center;">
            <h1>🔧 {app_info['name']}</h1>
            <h3 style="color: #007bff;">Versão {app_info['version']}</h3>
        </div>
        
        <hr>
        
        <h3>📊 Informações Técnicas</h3>
        <table border="0" cellpadding="5">
            <tr><td><b>🏷️ Versão:</b></td><td>{app_info['version']}</td></tr>
            <tr><td><b>📅 Data de Build:</b></td><td>{app_info['build_date']}</td></tr>
            <tr><td><b>👨‍💻 Desenvolvedor:</b></td><td>{app_info.get('author', 'Equipe de Desenvolvimento')}</td></tr>
            <tr><td><b>📝 Descrição:</b></td><td>{app_info['description']}</td></tr>
        </table>
        
        <hr>
        
        <h3>⚡ Funcionalidades Principais</h3>
        <ul>
            <li>📦 <b>Inventário Inicial:</b> Carregamento de estoque base para lojas</li>
            <li>📊 <b>Controle de Movimentos:</b> Remessas, regressos e transferências</li>
            <li>🎯 <b>Fluxo Visual:</b> Acompanhe mudanças dia a dia (Lojas e CDs)</li>
            <li>📈 <b>Relatórios Completos:</b> Exportação em Excel/CSV</li>
            <li>🔄 <b>Atualizações Automáticas:</b> Sistema sempre atualizado</li>
            <li>🏪 <b>Multi-Local:</b> CDs e Lojas integrados</li>
            <li>🎨 <b>Interface Personalizável:</b> Ajuste fontes, cores e temas</li>
        </ul>
        
        <hr>
        
        <h3>🔧 Especificações Técnicas</h3>
        <ul>
            <li><b>Framework:</b> PyQt5</li>
            <li><b>Base de Dados:</b> SQLite3</li>
            <li><b>Formatos Suportados:</b> CSV, Excel (XLSX)</li>
            <li><b>Sistema Operacional:</b> Windows 7 ou superior</li>
            <li><b>Resolução Mínima:</b> 1024x768</li>
            <li><b>Suporte High DPI:</b> Sim</li>
        </ul>
        """
        
        about_label = QLabel(about_text)
        about_label.setWordWrap(True)
        about_label.setOpenExternalLinks(True)
        about_label.setStyleSheet("""
            QLabel {
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 8px;
                line-height: 1.4;
            }
        """)
        
        content_layout.addWidget(about_label)
        content_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Botões de ação
        action_layout = QHBoxLayout()
        
        check_updates_button = QPushButton("🔄 Verificar Atualizações")
        check_updates_button.setStyleSheet("background-color: #007bff; color: white; padding: 8px 16px;")
        check_updates_button.clicked.connect(self.check_updates)
        action_layout.addWidget(check_updates_button)
        
        action_layout.addStretch()
        
        visit_github_button = QPushButton("🔗 Visitar GitHub")
        visit_github_button.setStyleSheet("background-color: #6c757d; color: white; padding: 8px 16px;")
        visit_github_button.clicked.connect(self.visit_github)
        action_layout.addWidget(visit_github_button)
        
        layout.addLayout(action_layout)
        
        self.tabs.addTab(tab, "ℹ️ Sobre")

    # Métodos de funcionalidade
    def load_current_appearance(self):
        """Carrega configurações atuais de aparência"""
        # Atualiza controles com valores carregados
        self.font_size_spinbox.setValue(self.appearance_settings['font_size'])
        self.font_family_combo.setCurrentText(self.appearance_settings['font_family'])
        self.theme_combo.setCurrentText(self.appearance_settings['theme'])
        self.high_contrast_checkbox.setChecked(self.appearance_settings['high_contrast'])
        
        # Atualiza botões de cor
        self.primary_color_button.setStyleSheet(f"background-color: {self.appearance_settings['primary_color']}; color: white; padding: 8px;")
        self.background_color_button.setStyleSheet(f"background-color: {self.appearance_settings['background_color']}; color: black; padding: 8px;")
        self.text_color_button.setStyleSheet(f"background-color: {self.appearance_settings['text_color']}; color: white; padding: 8px;")
        
        # Aplica preview
        self.preview_changes()

    # Atualizar método apply_changes:
    def apply_changes(self):
        """Aplica mudanças na aplicação principal"""
        # Salva configurações
        if AppearanceManager.save_settings(self.appearance_settings):
            # Aplica na aplicação
            if AppearanceManager.apply_to_application(self.appearance_settings, self.parent_window):
                # Emite sinal para compatibilidade
                self.appearance_changed.emit(self.appearance_settings.copy())
                QMessageBox.information(self, "✅ Sucesso", "Configurações aplicadas e salvas com sucesso!")
            else:
                QMessageBox.warning(self, "⚠️ Aviso", "Configurações salvas, mas houve problema na aplicação.")
        else:
            QMessageBox.critical(self, "❌ Erro", "Erro ao salvar configurações.")

    def preview_changes(self):
        """Aplica mudanças em tempo real na preview"""
        # Atualiza configurações
        self.appearance_settings['font_size'] = self.font_size_spinbox.value()
        self.appearance_settings['font_family'] = self.font_family_combo.currentText()
        self.appearance_settings['theme'] = self.theme_combo.currentText()
        self.appearance_settings['high_contrast'] = self.high_contrast_checkbox.isChecked()
        
        # Aplica na preview
        font = QFont(self.appearance_settings['font_family'], self.appearance_settings['font_size'])
        self.preview_label.setFont(font)
        self.preview_button.setFont(font)
        
        # Aplica cores
        primary_color = self.appearance_settings['primary_color']
        text_color = self.appearance_settings['text_color']
        background_color = self.appearance_settings['background_color']
        
        if self.appearance_settings['high_contrast']:
            text_color = '#000000' if self.appearance_settings['theme'] == 'Claro' else '#ffffff'
            background_color = '#ffffff' if self.appearance_settings['theme'] == 'Claro' else '#000000'
        
        self.preview_label.setStyleSheet(f"""
            padding: 20px; 
            border: 1px solid #ccc; 
            border-radius: 4px;
            background-color: {background_color};
            color: {text_color};
        """)
        
        self.preview_button.setStyleSheet(f"""
            background-color: {primary_color};
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
        """)

    def choose_color(self, color_type):
        """Abre diálogo de seleção de cor"""
        current_color = QColor(self.appearance_settings[color_type])
        color = QColorDialog.getColor(current_color, self)
        
        if color.isValid():
            color_hex = color.name()
            self.appearance_settings[color_type] = color_hex
            
            # Atualiza botão
            if color_type == 'primary_color':
                self.primary_color_button.setStyleSheet(f"background-color: {color_hex}; color: white; padding: 8px;")
            elif color_type == 'background_color':
                self.background_color_button.setStyleSheet(f"background-color: {color_hex}; color: black; padding: 8px;")
            elif color_type == 'text_color':
                self.text_color_button.setStyleSheet(f"background-color: {color_hex}; color: white; padding: 8px;")
            
            self.preview_changes()

    def reset_to_defaults(self):
        """Restaura configurações padrão"""
        self.appearance_settings = {
            'font_size': 10,
            'font_family': 'Arial',
            'primary_color': '#007bff',
            'background_color': '#ffffff',
            'text_color': '#000000',
            'high_contrast': False,
            'theme': 'Claro'
        }
        
        # Atualiza controles
        self.font_size_spinbox.setValue(10)
        self.font_family_combo.setCurrentText('Arial')
        self.theme_combo.setCurrentText('Claro')
        self.high_contrast_checkbox.setChecked(False)
        
        # Atualiza botões de cor
        self.primary_color_button.setStyleSheet("background-color: #007bff; color: white; padding: 8px;")
        self.background_color_button.setStyleSheet("background-color: #ffffff; color: black; padding: 8px;")
        self.text_color_button.setStyleSheet("background-color: #000000; color: white; padding: 8px;")
        
        self.preview_changes()
        QMessageBox.information(self, "✅ Sucesso", "Configurações restauradas para os valores padrão.")

    def apply_changes(self):
        """Aplica mudanças na aplicação principal"""
        # Emite sinal com as configurações para a janela principal
        self.appearance_changed.emit(self.appearance_settings.copy())
        QMessageBox.information(self, "✅ Sucesso", "Configurações aplicadas com sucesso!")

    # Métodos de upload e limpeza (reutilizados do settings_dialog.py original)
    def upload_inventory(self):
        """Upload de inventário"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo de Inventário", "", 
            "Arquivos de Dados (*.csv *.xlsx)"
        )
        
        if file_path:
            try:
                # Lógica de upload (copiada do settings_dialog.py original)
                if file_path.endswith('.csv'):
                    try:
                        df = pd.read_csv(file_path, sep=';')
                    except:
                        try:
                            df = pd.read_csv(file_path, sep=',')
                        except:
                            df = pd.read_csv(file_path, sep='\t')
                else:
                    df = pd.read_excel(file_path)
                
                # Validação e inserção (código do settings_dialog.py)
                df.columns = [col.strip().lower() for col in df.columns]
                required_columns = ['loja_nome', 'ativo', 'quantidade']
                
                column_mapping = {
                    'loja': 'loja_nome', 'loja_nome': 'loja_nome', 'nome_loja': 'loja_nome', 'local': 'loja_nome',
                    'ativo': 'ativo', 'rti': 'ativo', 'produto': 'ativo',
                    'quantidade': 'quantidade', 'qtd': 'quantidade', 'qtde': 'quantidade', 'estoque': 'quantidade'
                }
                
                for old_name, new_name in column_mapping.items():
                    if old_name in df.columns:
                        df.rename(columns={old_name: new_name}, inplace=True)
                
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    raise ValueError(f"Colunas faltando: {missing_columns}")
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    raise ValueError(f"Colunas faltando: {missing_columns}")
                
                df = df.dropna(subset=required_columns)
                
                # Validação dos ativos
                valid_assets = ['HB623', 'HB618']
                df['ativo'] = df['ativo'].astype(str).str.upper().str.strip()
                
                invalid_assets = df[~df['ativo'].isin(valid_assets)]
                if not invalid_assets.empty:
                    invalid_list = invalid_assets['ativo'].unique()
                    raise ValueError(f"Ativos inválidos: {invalid_list}. Use apenas: {valid_assets}")
                
                df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce')
                df = df.dropna(subset=['quantidade'])
                df['quantidade'] = df['quantidade'].astype(int)
                
                successful_inserts, failed_inserts = self.db.insert_inventory_data(df)
                
                message = f"✅ Upload concluído!\n\nInserções bem-sucedidas: {successful_inserts}\nFalhas: {len(failed_inserts)}"
                
                if successful_inserts > 0:
                    QMessageBox.information(self, "Sucesso", message)
                    self.database_cleared.emit()
                else:
                    QMessageBox.warning(self, "Atenção", message)
                    
            except Exception as e:
                QMessageBox.critical(self, "Erro no Upload", f"Falha ao processar arquivo:\n{e}")

    def upload_movements(self):
        """Upload de movimentos"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo de Movimentos", "", 
            "Arquivos de Dados (*.csv *.xlsx)"
        )
        
        if file_path:
            try:
                df = pd.read_csv(file_path, sep=';') if file_path.endswith('.csv') else pd.read_excel(file_path)
                
                if 'Data' not in df.columns or 'Quant.' not in df.columns or 'RTI' not in df.columns:
                    raise ValueError("O arquivo deve conter as colunas 'Data', 'Quant.' e 'RTI'.")
                
                self.db.insert_data(df)
                QMessageBox.information(self, "Sucesso", f"✅ {len(df)} registros de movimento importados.")
                self.database_cleared.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Erro no Upload", f"Falha ao processar arquivo:\n{e}")

    def clear_inventory(self):
        """Limpa apenas inventário"""
        reply = QMessageBox.question(
            self, "Confirmação", 
            "Deseja limpar apenas os dados de inventário inicial?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.clear_inventory_data()
            QMessageBox.information(self, "Sucesso", "✅ Dados de inventário removidos.")
            self.database_cleared.emit()

    def clear_movements_only(self):
        """Limpa apenas movimentos"""
        reply = QMessageBox.question(
            self, "Confirmação", 
            "Deseja limpar apenas os dados de movimentos?\n\nO inventário inicial será mantido.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.cursor.execute("DELETE FROM movimentos")
            self.db.conn.commit()
            QMessageBox.information(self, "Sucesso", "✅ Dados de movimentos removidos.")
            self.database_cleared.emit()

    def clear_database(self):
        """Limpa toda a base de dados"""
        if self.db.clear_all_data():
            self.database_cleared.emit()

    def export_complete_report(self):
        """Exporta relatório completo"""
        try:
            import datetime
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Salvar Relatório Completo", 
                f"relatorio_completo_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", 
                "Excel (*.xlsx)"
            )
            
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Estoque atual
                    stock_data = self.db.calculate_stock_by_asset_with_inventory()
                    stock_list = []
                    for location, assets in stock_data.items():
                        for asset, qty in assets.items():
                            stock_list.append({
                                'Local': location,
                                'Ativo': asset,
                                'Quantidade': qty,
                                'Tipo': 'CD' if 'CD' in location else 'Loja'
                            })
                    
                    if stock_list:
                        stock_df = pd.DataFrame(stock_list)
                        stock_df.to_excel(writer, sheet_name='Estoque Atual', index=False)
                    
                    # Movimentos
                    movements_query = """
                    SELECT data_movimento, tipo_movimento, local_origem, local_destino, 
                            rti, quantidade, guia, nota_fiscal
                    FROM movimentos ORDER BY data_movimento DESC
                    """
                    movements = self.db._execute_query(movements_query)
                    if movements:
                        movements_df = pd.DataFrame([dict(row) for row in movements])
                        movements_df.to_excel(writer, sheet_name='Movimentos', index=False)
                    
                    # Inventário inicial
                    inventory_query = """
                    SELECT loja_nome_simples, ativo, quantidade, data_inventario
                    FROM inventario_inicial ORDER BY loja_nome_simples
                    """
                    inventory = self.db._execute_query(inventory_query)
                    if inventory:
                        inventory_df = pd.DataFrame([dict(row) for row in inventory])
                        inventory_df.to_excel(writer, sheet_name='Inventario Inicial', index=False)
                
                QMessageBox.information(self, "Sucesso", f"✅ Relatório completo exportado para:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar relatório:\n{e}")

    def export_inventory_only(self):
        """Exporta apenas inventário"""
        try:
            import datetime
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Salvar Inventário", 
                f"inventario_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", 
                "Excel (*.xlsx)"
            )
            
            if file_path:
                inventory_query = """
                SELECT loja_nome_simples as 'Loja', ativo as 'Ativo', 
                        quantidade as 'Quantidade', data_inventario as 'Data Inventário'
                FROM inventario_inicial ORDER BY loja_nome_simples, ativo
                """
                inventory = self.db._execute_query(inventory_query)
                
                if inventory:
                    inventory_df = pd.DataFrame([dict(row) for row in inventory])
                    inventory_df.to_excel(file_path, index=False)
                    QMessageBox.information(self, "Sucesso", f"✅ Inventário exportado para:\n{file_path}")
                else:
                    QMessageBox.warning(self, "Aviso", "❌ Nenhum dado de inventário encontrado.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar inventário:\n{e}")

    def create_backup(self):
        """Cria backup da base de dados"""
        try:
            import shutil
            import datetime
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Salvar Backup", 
                f"backup_estoque_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.db", 
                "Database (*.db)"
            )
            
            if file_path:
                shutil.copy2(self.db.db_name, file_path)
                QMessageBox.information(self, "Sucesso", f"✅ Backup criado com sucesso:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao criar backup:\n{e}")

    def restore_backup(self):
        """Restaura backup da base de dados"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Backup", "", 
            "Database (*.db)"
        )
        
        if file_path:
            reply = QMessageBox.question(
                self, "Confirmação", 
                "⚠️ ATENÇÃO: Esta operação substituirá TODOS os dados atuais!\n\n"
                "Deseja continuar?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    import shutil
                    
                    # Fecha conexão atual
                    self.db.close()
                    
                    # Restaura backup
                    shutil.copy2(file_path, self.db.db_name)
                    
                    # Reabre conexão
                    self.db.__init__(self.db.db_name)
                    
                    QMessageBox.information(self, "Sucesso", "✅ Backup restaurado com sucesso!")
                    self.database_cleared.emit()
                    
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao restaurar backup:\n{e}")

    def check_updates(self):
        """Verifica atualizações"""
        from update_dialog import UpdateDialog
        dialog = UpdateDialog(self, auto_check=False)
        dialog.exec_()

    def visit_github(self):
        """Abre página do GitHub"""
        import webbrowser
        webbrowser.open("https://github.com/esc4n0rx/HBTrackerx")
                