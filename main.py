# main.py
import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QAction, QFileDialog, 
                             QMessageBox, QGroupBox, QComboBox, QTableView, QHeaderView, QPushButton, QHBoxLayout, QTabWidget)
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem
from database import Database
from settings_dialog import SettingsDialog
from flow_dialog import FlowDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database("estoque.db")
        self.setWindowTitle("Sistema de Controle de Caixas v2.0")
        self.setGeometry(100, 100, 1200, 800)
        
        self.cd_map = {
            'CD RJ': 'CD HORTIFRUTI - Rio de Janeiro (RJ)',
            'CD SP': 'CD HORTIFRUTI - São Paulo (SP)',
            'CD ES': 'CD HORTIFRUTI - Viana (ES)'
        }
        self.asset_types = ['HB 618', 'HB 623'] # Principais ativos a serem exibidos

        self.init_ui()
        self.create_menu()
        self.update_all_views()

    def create_menu(self):
        menu_bar = self.menuBar()
        # Menu Arquivo
        file_menu = menu_bar.addMenu("Arquivo")
        upload_action = QAction("Novo Upload (.csv/.xlsx)", self)
        upload_action.triggered.connect(self.handle_upload)
        file_menu.addAction(upload_action)
        file_menu.addSeparator()
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Ferramentas
        tools_menu = menu_bar.addMenu("Ferramentas")
        settings_action = QAction("Configurações", self)
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Abas para cada tipo de ativo
        self.tabs = QTabWidget()
        self.stock_widgets = {} # Armazena os widgets de cada aba para atualização
        
        # Cria aba de Total
        self.create_stock_tab("Total")
        # Cria abas para cada ativo
        for asset in self.asset_types:
            self.create_stock_tab(asset)

        main_layout.addWidget(self.tabs)

        # Seção de Análise Detalhada
        details_group = QGroupBox("Análise Detalhada por Local")
        details_layout = QVBoxLayout(details_group)
        
        # Layout de Filtro e Ações
        filter_action_layout = QHBoxLayout()
        self.location_combo = QComboBox()
        self.location_combo.currentIndexChanged.connect(self.update_location_details)
        filter_action_layout.addWidget(QLabel("Selecionar Local:"), 1)
        filter_action_layout.addWidget(self.location_combo, 4)
        
        self.view_flow_button = QPushButton("Ver Fluxo Visual")
        self.view_flow_button.clicked.connect(self.show_flow_dialog)
        filter_action_layout.addWidget(self.view_flow_button, 2)
        
        self.export_button = QPushButton("Exportar Histórico")
        self.export_button.clicked.connect(self.export_history)
        filter_action_layout.addWidget(self.export_button, 2)
        
        # Tabela de Histórico
        self.history_table = QTableView()
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setEditTriggers(QTableView.NoEditTriggers)
        self.history_model = QStandardItemModel()
        self.history_table.setModel(self.history_model)
        
        details_layout.addLayout(filter_action_layout)
        details_layout.addWidget(self.history_table)
        main_layout.addWidget(details_group)

    def create_stock_tab(self, asset_name):
        """Cria uma aba de visualização de estoque para um ativo específico ou total."""
        tab_widget = QWidget()
        layout = QGridLayout(tab_widget)
        
        widgets = {}
        
        # Cabeçalho
        headers = ["Local", "Estoque Atual"]
        for i, header in enumerate(headers):
            label = QLabel(f"<b>{header}</b>")
            layout.addWidget(label, 0, i)
        
        # Linhas de CDs
        row = 1
        for cd_key, cd_name in self.cd_map.items():
            layout.addWidget(QLabel(cd_name), row, 0)
            widgets[cd_key] = QLabel("0")
            layout.addWidget(widgets[cd_key], row, 1)
            row += 1
            
        # Linha de Total Lojas
        layout.addWidget(QLabel("<b>TOTAL ESTOQUE LOJAS</b>"), row, 0)
        widgets['total_lojas'] = QLabel("0")
        layout.addWidget(widgets['total_lojas'], row, 1)
        
        self.tabs.addTab(tab_widget, asset_name)
        self.stock_widgets[asset_name] = widgets

    def update_all_views(self):
        """Função central que atualiza dinamicamente toda a interface."""
        # 1. Calcula os estoques
        stock_data = self.db.calculate_stock_by_asset()
        
        # 2. Atualiza as abas de estoque
        for asset_tab_name, widgets in self.stock_widgets.items():
            # Total de lojas para esta aba
            total_lojas_asset = 0
            
            # Atualiza estoque dos CDs
            for cd_key, cd_full_name in self.cd_map.items():
                cd_stock = 0
                if asset_tab_name == "Total":
                    cd_stock = sum(stock_data.get(cd_full_name, {}).values())
                else:
                    cd_stock = stock_data.get(cd_full_name, {}).get(asset_tab_name, 0)
                widgets[cd_key].setText(f"{cd_stock:,}".replace(",", "."))
            
            # Calcula e atualiza estoque total das lojas
            for location, assets in stock_data.items():
                if location.startswith("LOJA"):
                    if asset_tab_name == "Total":
                        total_lojas_asset += sum(assets.values())
                    else:
                        total_lojas_asset += assets.get(asset_tab_name, 0)
            widgets['total_lojas'].setText(f"{total_lojas_asset:,}".replace(",", "."))

        # 3. Atualiza o ComboBox de locais
        self.location_combo.blockSignals(True)
        current_selection = self.location_combo.currentText()
        self.location_combo.clear()
        self.location_combo.addItem("Selecione um local...")
        all_locations = sorted(self.db.get_all_locations('cd') + self.db.get_all_locations('loja'))
        self.location_combo.addItems(all_locations)
        
        # Tenta restaurar a seleção anterior
        index = self.location_combo.findText(current_selection)
        if index != -1:
            self.location_combo.setCurrentIndex(index)
        
        self.location_combo.blockSignals(False)
        
        # 4. Atualiza os detalhes do local selecionado
        self.update_location_details()

    def update_location_details(self):
        """Atualiza a tabela de histórico para o local selecionado."""
        self.history_model.clear()
        self.history_model.setHorizontalHeaderLabels(['Data', 'Movimento', 'Ativo (RTI)', 'Origem', 'Destino', 'Quantidade'])
        
        location_name = self.location_combo.currentText()
        if not location_name or location_name == "Selecione um local...":
            self.view_flow_button.setEnabled(False)
            self.export_button.setEnabled(False)
            return

        self.view_flow_button.setEnabled(True)
        self.export_button.setEnabled(True)
        
        history = self.db.get_location_history(location_name)
        for row_data in history:
            row = [QStandardItem(str(item) if item is not None else "") for item in row_data]
            self.history_model.appendRow(row)
        
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)

    def handle_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo", "", "Arquivos de Dados (*.csv *.xlsx)")
        if file_path:
            try:
                df = pd.read_csv(file_path, sep=';') if file_path.endswith('.csv') else pd.read_excel(file_path)
                if 'Data' not in df.columns or 'Quant.' not in df.columns or 'RTI' not in df.columns:
                    raise ValueError("O arquivo deve conter as colunas 'Data', 'Quant.' e 'RTI'.")
                
                self.db.insert_data(df)
                QMessageBox.information(self, "Sucesso", f"{len(df)} registros importados.")
                self.update_all_views() # Atualização dinâmica!
            except Exception as e:
                QMessageBox.critical(self, "Erro no Upload", f"Falha ao processar arquivo:\n{e}")

    def open_settings(self):
        dialog = SettingsDialog(self.db, self)
        # Conecta o sinal da dialog à função de atualização
        dialog.database_cleared.connect(self.update_all_views)
        dialog.exec_()
        
    def show_flow_dialog(self):
        location_name = self.location_combo.currentText()
        if location_name and location_name != "Selecione um local...":
            flow_data = self.db.get_flow_data(location_name)
            dialog = FlowDialog(location_name, flow_data, self)
            dialog.exec_()
    
    def export_history(self):
        location_name = self.location_combo.currentText()
        if not location_name or self.history_model.rowCount() == 0:
            QMessageBox.warning(self, "Aviso", "Não há dados para exportar.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Histórico", f"historico_{location_name}.csv", "CSV (*.csv)")
        if file_path:
            data = []
            headers = [self.history_model.horizontalHeaderItem(i).text() for i in range(self.history_model.columnCount())]
            for row in range(self.history_model.rowCount()):
                row_data = [self.history_model.item(row, col).text() for col in range(self.history_model.columnCount())]
                data.append(row_data)
            
            df = pd.DataFrame(data, columns=headers)
            df.to_csv(file_path, index=False, sep=';')
            QMessageBox.information(self, "Sucesso", f"Histórico exportado para:\n{file_path}")

    def closeEvent(self, event):
        self.db.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())