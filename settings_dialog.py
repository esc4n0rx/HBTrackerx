# settings_dialog.py - Versão atualizada
import pandas as pd
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLabel, QGroupBox, 
                            QFileDialog, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import pyqtSignal

class SettingsDialog(QDialog):
    database_cleared = pyqtSignal()

    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db = db_instance
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Grupo de Upload de Inventário
        inventory_group = QGroupBox("Inventário Inicial")
        inventory_layout = QVBoxLayout()
        
        inventory_info = QLabel(
            "Upload do inventário inicial das lojas (Data: 08/06/2025)\n"
            "Formato: loja_nome, ativo, quantidade\n"
            "Ativos aceitos: HB623, HB618\n"
            "Exemplo: CABO FRIO, HB623, 100"
        )
        inventory_info.setWordWrap(True)
        inventory_layout.addWidget(inventory_info)
        
        inventory_buttons = QHBoxLayout()
        self.upload_inventory_button = QPushButton("Upload Inventário (.csv/.xlsx)")
        self.upload_inventory_button.setStyleSheet("background-color: #5cb85c; color: white;")
        self.upload_inventory_button.clicked.connect(self.upload_inventory)
        
        self.clear_inventory_button = QPushButton("Limpar Inventário")
        self.clear_inventory_button.setStyleSheet("background-color: #f0ad4e; color: white;")
        self.clear_inventory_button.clicked.connect(self.clear_inventory)
        
        inventory_buttons.addWidget(self.upload_inventory_button)
        inventory_buttons.addWidget(self.clear_inventory_button)
        inventory_layout.addLayout(inventory_buttons)
        
        inventory_group.setLayout(inventory_layout)
        layout.addWidget(inventory_group)
        
        # Grupo de Ações Perigosas
        danger_zone_group = QGroupBox("Zona de Perigo")
        danger_layout = QVBoxLayout()
        
        label = QLabel("Esta ação removerá permanentemente todos os movimentos e inventários registrados.")
        label.setWordWrap(True)
        danger_layout.addWidget(label)
        
        self.clear_db_button = QPushButton("Limpar Toda a Base de Dados")
        self.clear_db_button.setStyleSheet("background-color: #d9534f; color: white;")
        self.clear_db_button.clicked.connect(self.clear_database)
        danger_layout.addWidget(self.clear_db_button)
        
        danger_zone_group.setLayout(danger_layout)
        layout.addWidget(danger_zone_group)

    def upload_inventory(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo de Inventário", "", 
            "Arquivos de Dados (*.csv *.xlsx)"
        )
        
        if file_path:
            try:
                # Carrega arquivo
                if file_path.endswith('.csv'):
                    # Tenta diferentes separadores
                    try:
                        df = pd.read_csv(file_path, sep=';')
                    except:
                        try:
                            df = pd.read_csv(file_path, sep=',')
                        except:
                            df = pd.read_csv(file_path, sep='\t')
                else:
                    df = pd.read_excel(file_path)
                
                print("=== DEBUG: Arquivo carregado ===")
                print(f"Shape: {df.shape}")
                print(f"Colunas: {list(df.columns)}")
                print("Primeiras linhas:")
                print(df.head())
                
                # Validação das colunas (case insensitive)
                df.columns = [col.strip().lower() for col in df.columns]
                required_columns = ['loja_nome', 'ativo', 'quantidade']
                
                # Mapeia possíveis variações de nomes de colunas
                column_mapping = {
                    'loja': 'loja_nome',
                    'loja_nome': 'loja_nome',
                    'nome_loja': 'loja_nome',
                    'local': 'loja_nome',
                    'ativo': 'ativo',
                    'rti': 'ativo',
                    'produto': 'ativo',
                    'quantidade': 'quantidade',
                    'qtd': 'quantidade',
                    'qtde': 'quantidade',
                    'estoque': 'quantidade'
                }
                
                # Renomeia colunas
                for old_name, new_name in column_mapping.items():
                    if old_name in df.columns:
                        df.rename(columns={old_name: new_name}, inplace=True)
                
                print(f"Colunas após mapeamento: {list(df.columns)}")
                
                # Verifica se todas as colunas necessárias existem
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    available_cols = list(df.columns)
                    raise ValueError(
                        f"Colunas faltando: {missing_columns}\n"
                        f"Colunas disponíveis: {available_cols}\n"
                        f"Certifique-se que o arquivo contém: loja_nome, ativo, quantidade"
                    )
                
                # Remove linhas vazias
                df = df.dropna(subset=required_columns)
                
                # Validação dos ativos
                valid_assets = ['HB623', 'HB618']
                df['ativo'] = df['ativo'].astype(str).str.upper().str.strip()
                
                # Mostra ativos únicos encontrados
                unique_assets = df['ativo'].unique()
                print(f"Ativos encontrados: {unique_assets}")
                
                invalid_assets = df[~df['ativo'].isin(valid_assets)]
                
                if not invalid_assets.empty:
                    invalid_list = invalid_assets['ativo'].unique()
                    raise ValueError(
                        f"Ativos inválidos encontrados: {invalid_list}\n"
                        f"Use apenas: {valid_assets}\n"
                        f"Verifique se os nomes dos ativos estão corretos"
                    )
                
                # Validação das quantidades
                df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce')
                invalid_qty = df[df['quantidade'].isna()]
                
                if not invalid_qty.empty:
                    print("Linhas com quantidades inválidas:")
                    print(invalid_qty)
                    raise ValueError("Algumas quantidades não são números válidos.")
                
                df['quantidade'] = df['quantidade'].astype(int)
                
                # Mostra resumo antes da inserção
                print("\n=== RESUMO DO ARQUIVO ===")
                print(f"Total de linhas válidas: {len(df)}")
                print("\nPor ativo:")
                print(df.groupby('ativo')['quantidade'].agg(['count', 'sum']))
                print("\nPrimeiras lojas:")
                print(df['loja_nome'].unique()[:10])
                
                # Insere no banco
                successful_inserts, failed_inserts = self.db.insert_inventory_data(df)
                
                # Monta mensagem de resultado
                message = f"Processo concluído!\n\n"
                message += f"✅ Inserções bem-sucedidas: {successful_inserts}\n"
                message += f"❌ Falhas: {len(failed_inserts)}\n"
                
                if failed_inserts:
                    message += f"\nPrimeiras falhas:\n"
                    for fail in failed_inserts[:5]:
                        message += f"• Linha {fail['linha']}: {fail['loja_original']}\n"
                    if len(failed_inserts) > 5:
                        message += f"... e mais {len(failed_inserts) - 5} falhas\n"
                
                if successful_inserts > 0:
                    QMessageBox.information(self, "Sucesso", message)
                    self.database_cleared.emit()
                else:
                    QMessageBox.warning(self, "Atenção", message)
                    
            except Exception as e:
                QMessageBox.critical(self, "Erro no Upload", f"Falha ao processar arquivo:\n{e}")

    def clear_inventory(self):
        reply = QMessageBox.question(
            self, "Confirmação", 
            "Deseja limpar apenas os dados de inventário inicial?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.clear_inventory_data()
            QMessageBox.information(self, "Sucesso", "Dados de inventário removidos.")
            self.database_cleared.emit()

    def clear_database(self):
        if self.db.clear_all_data():
            self.database_cleared.emit()
            self.accept()