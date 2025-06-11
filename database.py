# database.py
import sqlite3
import pandas as pd
from collections import defaultdict

class Database:
    def __init__(self, db_name="estoque.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row # Facilita o acesso por nome da coluna
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # A tabela já inclui a coluna 'rti', que agora será utilizada
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, guia TEXT, transacao TEXT,
            local_origem TEXT, local_destino TEXT, tipo_movimento TEXT,
            rti TEXT, nota_fiscal TEXT, quantidade INTEGER, data_movimento DATE
        )
        """)
        self.conn.commit()

    def insert_data(self, df: pd.DataFrame):
        column_mapping = {
            'Guia': 'guia', 'Transação': 'transacao', 'LOCAL Origem': 'local_origem',
            'LOCAL Destino': 'local_destino', 'Tipo Movimento': 'tipo_movimento',
            'RTI': 'rti', 'Nota Fiscal': 'nota_fiscal', 'Quant.': 'quantidade', 'Data': 'data_movimento'
        }
        df.rename(columns=column_mapping, inplace=True)
        df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').fillna(0).astype(int)
        df['data_movimento'] = pd.to_datetime(df['data_movimento'], dayfirst=True, errors='coerce').dt.date
        df_to_insert = df[[col for col in column_mapping.values() if col in df.columns]]
        df_to_insert.to_sql('movimentos', self.conn, if_exists='append', index=False)
        self.conn.commit()

    def _execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def calculate_stock_by_asset(self):
        """
        Calcula o estoque atual para CDs e Lojas, separado por ativo (RTI).
        Retorna um dicionário aninhado: {local: {rti: saldo}}
        """
        # defaultdict simplifica a criação de dicionários aninhados
        estoque = defaultdict(lambda: defaultdict(int))
        
        query = "SELECT local_origem, local_destino, tipo_movimento, rti, quantidade FROM movimentos"
        movimentos = self._execute_query(query)

        for mov in movimentos:
            qtde = mov['quantidade']
            rti = mov['rti'] if mov['rti'] else 'N/A'
            origem = mov['local_origem']
            destino = mov['local_destino']
            tipo = mov['tipo_movimento']

            # Lógica de entrada/saída
            if tipo in ('Regresso', 'Entrega', 'Transferencia'):
                estoque[destino][rti] += qtde
            if tipo in ('Remessa', 'Retorno', 'Transferencia', 'Devolução de Entrega'):
                estoque[origem][rti] -= qtde

        return estoque

    def get_flow_data(self, location_name):
        """
        Busca e categoriza os dados de fluxo para um local específico.
        """
        query = """
        SELECT tipo_movimento, local_origem, local_destino, rti, SUM(quantidade) as total_qtde
        FROM movimentos
        WHERE local_origem = ? OR local_destino = ?
        GROUP BY tipo_movimento, local_origem, local_destino, rti
        ORDER BY tipo_movimento
        """
        params = (location_name, location_name)
        return self._execute_query(query, params)

    def get_all_locations(self, type='loja'):
        like_pattern = 'LOJA %' if type == 'loja' else 'CD %'
        query = f"""
        SELECT DISTINCT local FROM (
            SELECT local_origem as local FROM movimentos WHERE local_origem LIKE '{like_pattern}'
            UNION
            SELECT local_destino as local FROM movimentos WHERE local_destino LIKE '{like_pattern}'
        ) ORDER BY local
        """
        return [row[0] for row in self._execute_query(query)]
        
    def get_location_history(self, location_name):
        query = "SELECT data_movimento, tipo_movimento, rti, local_origem, local_destino, quantidade FROM movimentos WHERE local_origem = ? OR local_destino = ? ORDER BY data_movimento DESC"
        return self._execute_query(query, (location_name, location_name))

    def clear_all_data(self):
        """Apaga todos os registros da tabela de movimentos."""
        if QMessageBox.warning(None, "Confirmação", 
                             "Você tem certeza que deseja apagar TODOS os dados da base?\nEsta ação não pode ser desfeita.",
                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self._execute_query("DELETE FROM movimentos")
            self.conn.commit()
            QMessageBox.information(None, "Sucesso", "Todos os dados foram apagados.")
            return True
        return False
        
    def close(self):
        self.conn.close()

# Importações necessárias para as caixas de diálogo no método clear_all_data
from PyQt5.QtWidgets import QMessageBox