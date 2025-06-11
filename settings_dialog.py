# settings_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QGroupBox
from PyQt5.QtCore import pyqtSignal

class SettingsDialog(QDialog):
    # Sinal para notificar a janela principal que os dados foram limpos
    database_cleared = pyqtSignal()

    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db = db_instance
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Grupo de Ações Perigosas
        danger_zone_group = QGroupBox("Zona de Perigo")
        danger_layout = QVBoxLayout()
        
        label = QLabel("Esta ação removerá permanentemente todos os movimentos registrados.")
        label.setWordWrap(True)
        danger_layout.addWidget(label)
        
        self.clear_db_button = QPushButton("Limpar Base de Dados")
        self.clear_db_button.setStyleSheet("background-color: #d9534f; color: white;")
        self.clear_db_button.clicked.connect(self.clear_database)
        danger_layout.addWidget(self.clear_db_button)
        
        danger_zone_group.setLayout(danger_layout)
        layout.addWidget(danger_zone_group)
        
        self.setLayout(layout)

    def clear_database(self):
        if self.db.clear_all_data():
            self.database_cleared.emit() # Emite o sinal
            self.accept() # Fecha a janela de configurações