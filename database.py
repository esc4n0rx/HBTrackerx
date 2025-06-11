# database.py - Versão corrigida com cálculos adequados
import sqlite3
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_name="estoque.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Tabela de movimentos existente
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, guia TEXT, transacao TEXT,
            local_origem TEXT, local_destino TEXT, tipo_movimento TEXT,
            rti TEXT, nota_fiscal TEXT, quantidade INTEGER, data_movimento DATE
        )
        """)
        
        # Nova tabela para inventário inicial - ARMAZENA NOMES SIMPLES
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_inicial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loja_nome_simples TEXT,
            ativo TEXT,
            quantidade INTEGER,
            data_inventario DATE,
            UNIQUE(loja_nome_simples, ativo)
        )
        """)
        self.conn.commit()

    def insert_inventory_data(self, df: pd.DataFrame, inventory_date='2025-06-08'):
        """Insere dados do inventário inicial DIRETAMENTE (sem mapeamento)"""
        print("=== INSERINDO INVENTÁRIO DIRETAMENTE ===")
        print(f"DataFrame recebido: {len(df)} linhas")
        
        # Limpa inventário anterior
        self.cursor.execute("DELETE FROM inventario_inicial")
        print("Inventário anterior limpo")
        
        successful_inserts = 0
        failed_inserts = []
        
        for index, row in df.iterrows():
            try:
                loja_nome_simples = str(row['loja_nome']).strip().upper()
                ativo = str(row['ativo']).strip().upper()
                quantidade = int(float(row['quantidade']))
                
                print(f"Inserindo: {loja_nome_simples} | {ativo} | {quantidade}")
                
                self.cursor.execute("""
                INSERT OR REPLACE INTO inventario_inicial 
                (loja_nome_simples, ativo, quantidade, data_inventario)
                VALUES (?, ?, ?, ?)
                """, (loja_nome_simples, ativo, quantidade, inventory_date))
                
                successful_inserts += 1
                
            except Exception as e:
                failed_inserts.append({
                    'linha': index + 1,
                    'loja_original': row.get('loja_nome', 'N/A'),
                    'motivo': f'Erro: {str(e)}'
                })
                print(f"❌ Erro na linha {index + 1}: {e}")
        
        self.conn.commit()
        print(f"✅ {successful_inserts} registros inseridos com sucesso")
        
        # Verifica o que foi inserido
        verification_query = "SELECT loja_nome_simples, ativo, quantidade FROM inventario_inicial ORDER BY loja_nome_simples"
        inserted_data = self._execute_query(verification_query)
        print(f"Dados no banco: {len(inserted_data)} registros")
        
        return successful_inserts, failed_inserts

    def levenshtein_distance(self, s1, s2):
        """Calcula distância de Levenshtein entre duas strings"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    def extract_simple_name(self, loja_completa):
        """Extrai nome simples da loja completa"""
        # Exemplo: "LOJA F036 - Recreio A5" -> "RECREIO A5"
        if ' - ' in loja_completa:
            return loja_completa.split(' - ')[1].strip().upper()
        elif loja_completa.startswith('LOJA '):
            # Remove "LOJA " e possíveis códigos
            resto = loja_completa.replace('LOJA ', '').strip()
            # Remove padrões como "F036 - " 
            import re
            resto = re.sub(r'^[A-Z]\d+\s*-?\s*', '', resto).strip().upper()
            return resto
        return loja_completa.upper()

    def find_best_inventory_match(self, loja_completa):
        """Encontra melhor match entre loja completa e inventário usando Levenshtein"""
        loja_simples_extraida = self.extract_simple_name(loja_completa)
        
        # Busca todas as lojas do inventário
        inventory_lojas = self._execute_query("SELECT DISTINCT loja_nome_simples FROM inventario_inicial")
        
        if not inventory_lojas:
            return None
        
        best_match = None
        best_distance = float('inf')
        
        print(f"Buscando match para '{loja_completa}' -> '{loja_simples_extraida}'")
        
        for row in inventory_lojas:
            loja_inventario = row['loja_nome_simples']
            distance = self.levenshtein_distance(loja_simples_extraida, loja_inventario)
            
            print(f"  Comparando com '{loja_inventario}': distância = {distance}")
            
            # Considera match se distância for baixa (ajuste conforme necessário)
            if distance < best_distance and distance <= 3:  # Máximo 3 caracteres diferentes
                best_distance = distance
                best_match = loja_inventario
        
        print(f"  Melhor match: '{best_match}' (distância: {best_distance})")
        return best_match

    def calculate_stock_by_asset_with_inventory(self):
        """Calcula estoque com inventário inicial e matching inteligente"""
        estoque = defaultdict(lambda: defaultdict(int))
        
        print("=== CALCULANDO ESTOQUE COM INVENTÁRIO ===")
        
        # 1. Carrega inventário inicial e mapeia para lojas dos movimentos
        inventory_query = "SELECT loja_nome_simples, ativo, quantidade FROM inventario_inicial"
        inventory_data = self._execute_query(inventory_query)
        
        # Cria mapeamento de lojas completas para inventário
        loja_complete_to_inventory = {}
        
        # Busca todas as lojas dos movimentos
        lojas_movimentos = self.get_all_locations('loja')
        
        for loja_completa in lojas_movimentos:
            best_match = self.find_best_inventory_match(loja_completa)
            if best_match:
                loja_complete_to_inventory[loja_completa] = best_match
                print(f"Mapeamento: '{loja_completa}' -> '{best_match}'")
        
        # Carrega inventário inicial usando o mapeamento
        for inv in inventory_data:
            loja_simples = inv['loja_nome_simples']
            ativo = inv['ativo'] if inv['ativo'] else 'N/A'
            qtde = inv['quantidade']
            
            # Encontra loja completa correspondente
            for loja_completa, loja_inventario in loja_complete_to_inventory.items():
                if loja_inventario == loja_simples:
                    estoque[loja_completa][ativo] = qtde
                    print(f"Inventário inicial: {loja_completa} -> {ativo}: {qtde}")

        # 2. Processa movimentos
        query = """
        SELECT local_origem, local_destino, tipo_movimento, rti, quantidade, data_movimento 
        FROM movimentos 
        ORDER BY data_movimento ASC, id ASC
        """
        movimentos = self._execute_query(query)

        inventory_date = datetime.strptime('2025-06-08', '%Y-%m-%d').date()
        
        for mov in movimentos:
            qtde = mov['quantidade']
            rti = mov['rti'] if mov['rti'] else 'N/A'
            origem = mov['local_origem']
            destino = mov['local_destino']
            tipo = mov['tipo_movimento']
            data_mov = mov['data_movimento']
            
            # Converte data se necessário
            if isinstance(data_mov, str):
                try:
                    data_mov = datetime.strptime(data_mov, '%Y-%m-%d').date()
                except:
                    continue

            # Lógica para CDs (mantém original)
            if not (origem and origem.startswith('LOJA')) and not (destino and destino.startswith('LOJA')):
                if tipo in ('Regresso', 'Entrega', 'Transferencia'):
                    estoque[destino][rti] += qtde
                if tipo in ('Remessa', 'Retorno', 'Transferencia', 'Devolução de Entrega'):
                    estoque[origem][rti] -= qtde
            else:
                # Lógica para lojas com inventário
                # Só processa movimentos após a data do inventário
                if data_mov >= inventory_date:
                    if destino and destino.startswith('LOJA') and tipo == 'Remessa':
                        estoque[destino][rti] += qtde
                        print(f"Movimento: +{qtde} {rti} para {destino}")
                    
                    if origem and origem.startswith('LOJA') and tipo == 'Regresso':
                        estoque[origem][rti] -= qtde
                        print(f"Movimento: -{qtde} {rti} de {origem}")

        return estoque

    def get_daily_stock_evolution(self, location_name):
        """CORRIGIDO: Retorna evolução diária considerando inventário e matching com normalização de ativos"""
        if not location_name.startswith('LOJA'):
            return []

        print(f"=== EVOLUÇÃO DIÁRIA PARA {location_name} ===")
        
        # Encontra match no inventário
        inventory_match = self.find_best_inventory_match(location_name)
        if not inventory_match:
            print(f"Nenhum inventário encontrado para {location_name}")
            return []

        # **FUNÇÃO AUXILIAR: Normaliza nomes de ativos**
        def normalize_asset_name(asset_name):
            """Remove espaços extras e padroniza formato"""
            if not asset_name:
                return 'N/A'
            
            # Remove espaços extras e converte para maiúscula
            normalized = str(asset_name).strip().upper()
            
            # Remove espaços internos (HB 618 -> HB618)
            normalized = normalized.replace(' ', '')
            
            return normalized

        # Busca inventário inicial e normaliza nomes
        inventory_query = "SELECT ativo, quantidade FROM inventario_inicial WHERE loja_nome_simples = ?"
        initial_stock = {}
        for row in self._execute_query(inventory_query, (inventory_match,)):
            normalized_asset = normalize_asset_name(row['ativo'])
            initial_stock[normalized_asset] = row['quantidade']
        
        print(f"Inventário inicial normalizado: {initial_stock}")

        # Busca movimentos ordenados por data
        movements_query = """
        SELECT data_movimento, tipo_movimento, rti, quantidade, local_origem, local_destino
        FROM movimentos 
        WHERE (local_origem = ? OR local_destino = ?) AND data_movimento >= '2025-06-08'
        ORDER BY data_movimento ASC, id ASC
        """
        movements = self._execute_query(movements_query, (location_name, location_name))

        # **CORREÇÃO PRINCIPAL: Calcula evolução dia a dia CUMULATIVA com normalização**
        daily_evolution = []
        current_stock = initial_stock.copy()  # Começa com inventário inicial
        
        # Agrupa movimentos por data
        from collections import defaultdict
        movements_by_date = defaultdict(list)
        for mov in movements:
            movements_by_date[mov['data_movimento']].append(mov)

        print(f"Datas com movimentos: {sorted(movements_by_date.keys())}")

        # Processa cada data em ordem
        for date in sorted(movements_by_date.keys()):
            day_movements = movements_by_date[date]
            
            print(f"\n--- Processando data: {date} ---")
            print(f"Estoque no início do dia: {current_stock}")
            
            # **CRÍTICO: Aplica todos os movimentos do dia NO ESTOQUE ATUAL**
            for mov in day_movements:
                raw_rti = mov['rti'] if mov['rti'] else 'N/A'
                # **NORMALIZAÇÃO: Remove espaços e padroniza**
                rti = normalize_asset_name(raw_rti)
                qtde = mov['quantidade']
                tipo = mov['tipo_movimento']
                
                print(f"Movimento original: {tipo} {qtde} '{raw_rti}' -> normalizado: '{rti}'")
                
                # Garante que o ativo existe no estoque
                if rti not in current_stock:
                    current_stock[rti] = 0
                    print(f"Criando novo ativo {rti} com quantidade 0")
                
                # **CORREÇÃO: Aplica movimento CUMULATIVO no estoque atual**
                old_qty = current_stock[rti]
                
                if mov['local_destino'] == location_name and tipo == 'Remessa':
                    current_stock[rti] += qtde
                    print(f"  ✅ Remessa: {rti} {old_qty} + {qtde} = {current_stock[rti]}")
                elif mov['local_origem'] == location_name and tipo == 'Regresso':
                    current_stock[rti] -= qtde
                    print(f"  ❌ Regresso: {rti} {old_qty} - {qtde} = {current_stock[rti]}")
                else:
                    print(f"  ⚠️ Movimento ignorado: {tipo} (origem: {mov['local_origem']}, destino: {mov['local_destino']})")

            print(f"Estoque final do dia {date}: {current_stock}")

            # **CRÍTICO: Salva estado do dia com CÓPIA do estoque final calculado**
            daily_evolution.append({
                'date': date,
                'stock': current_stock.copy(),  # **IMPORTANTE: Fazer cópia do estado final**
                'movements': day_movements.copy()
            })

        print(f"\nEvolução final calculada:")
        for i, day in enumerate(daily_evolution):
            print(f"Dia {i+1} ({day['date']}): {day['stock']}")

        return daily_evolution

    def insert_inventory_data(self, df: pd.DataFrame, inventory_date='2025-06-08'):
        """Insere dados do inventário inicial com normalização de ativos"""
        print("=== INSERINDO INVENTÁRIO COM NORMALIZAÇÃO ===")
        print(f"DataFrame recebido: {len(df)} linhas")
        
        # **FUNÇÃO AUXILIAR: Normaliza nomes de ativos**
        def normalize_asset_name(asset_name):
            """Remove espaços extras e padroniza formato"""
            if not asset_name:
                return 'N/A'
            
            # Remove espaços extras e converte para maiúscula
            normalized = str(asset_name).strip().upper()
            
            # Remove espaços internos (HB 618 -> HB618)
            normalized = normalized.replace(' ', '')
            
            return normalized
        
        # Limpa inventário anterior
        self.cursor.execute("DELETE FROM inventario_inicial")
        print("Inventário anterior limpo")
        
        successful_inserts = 0
        failed_inserts = []
        
        for index, row in df.iterrows():
            try:
                loja_nome_simples = str(row['loja_nome']).strip().upper()
                
                # **NORMALIZAÇÃO: Aplica normalização nos ativos**
                raw_ativo = str(row['ativo']).strip()
                ativo_normalizado = normalize_asset_name(raw_ativo)
                
                quantidade = int(float(row['quantidade']))
                
                print(f"Inserindo: {loja_nome_simples} | '{raw_ativo}' -> '{ativo_normalizado}' | {quantidade}")
                
                self.cursor.execute("""
                INSERT OR REPLACE INTO inventario_inicial 
                (loja_nome_simples, ativo, quantidade, data_inventario)
                VALUES (?, ?, ?, ?)
                """, (loja_nome_simples, ativo_normalizado, quantidade, inventory_date))
                
                successful_inserts += 1
                
            except Exception as e:
                failed_inserts.append({
                    'linha': index + 1,
                    'loja_original': row.get('loja_nome', 'N/A'),
                    'motivo': f'Erro: {str(e)}'
                })
                print(f"❌ Erro na linha {index + 1}: {e}")
        
        self.conn.commit()
        print(f"✅ {successful_inserts} registros inseridos com sucesso")
        
        # Verifica o que foi inserido
        verification_query = "SELECT loja_nome_simples, ativo, quantidade FROM inventario_inicial ORDER BY loja_nome_simples"
        inserted_data = self._execute_query(verification_query)
        print(f"Dados no banco após normalização: {len(inserted_data)} registros")
        for row in inserted_data:
            print(f"  {row['loja_nome_simples']} | {row['ativo']} | {row['quantidade']}")
        
        return successful_inserts, failed_inserts

    # Resto dos métodos permanecem iguais...
    def _execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_flow_data(self, location_name):
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
        query = """
        SELECT data_movimento, tipo_movimento, rti, local_origem, local_destino, quantidade 
        FROM movimentos 
        WHERE local_origem = ? OR local_destino = ? 
        ORDER BY data_movimento DESC
        """
        return self._execute_query(query, (location_name, location_name))

    def clear_inventory_data(self):
        """Limpa apenas dados de inventário"""
        self.cursor.execute("DELETE FROM inventario_inicial")
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

    def clear_all_data(self):
        from PyQt5.QtWidgets import QMessageBox
        if QMessageBox.warning(None, "Confirmação", 
                             "Você tem certeza que deseja apagar TODOS os dados da base?\nEsta ação não pode ser desfeita.",
                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self._execute_query("DELETE FROM movimentos")
            self._execute_query("DELETE FROM inventario_inicial")
            self.conn.commit()
            QMessageBox.information(None, "Sucesso", "Todos os dados foram apagados.")
            return True
        return False
        
    def close(self):
        self.conn.close()