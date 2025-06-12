# flow_dialog.py - VERSÃO CORRIGIDA COM CARDS RESPONSIVOS E MÉTODO FALTANTE
import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
                            QWidget, QFrame, QGridLayout, QPushButton, QComboBox,
                            QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
                            QGroupBox, QSplitter, QSizePolicy)
from PyQt5.QtGui import QFont, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect
from datetime import datetime, timedelta
from collections import defaultdict
from screen_utils import ScreenManager, ResponsiveDialog
import json

class FlowDialog(QDialog, ResponsiveDialog):
    """Diálogo para exibir fluxo clássico de movimentos - VERSÃO RESPONSIVA"""
    def __init__(self, location_name, flow_data, parent=None):
        super().__init__(parent)
        self.location_name = location_name
        self.flow_data = flow_data
        self.setWindowTitle(f"Fluxo de Movimentos - {location_name}")
        
        # **CORREÇÃO: Usa sistema responsivo**
        self.make_responsive("medium", center=True)
        
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título responsivo
        title = QLabel(f"📊 Fluxo de Movimentos - {self.location_name}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Tabela responsiva
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            '📅 Data', '🔄 Movimento', '📦 Ativo (RTI)', 
            '📤 Origem', '📥 Destino', '🔢 Quantidade'
        ])
        
        # **CORREÇÃO: Fonte ajustada para responsividade**
        table_font = QFont()
        table_font.setPointSize(10)
        self.table.setFont(table_font)
        
        header = self.table.horizontalHeader()
        header_font = QFont()
        header_font.setPointSize(10)
        header_font.setBold(True)
        header.setFont(header_font)
        
        # **CORREÇÃO: Headers responsivos**
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        # Botões responsivos
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("❌ Fechar")
        close_btn.setFont(QFont("Arial", 10))
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)

    def load_data(self):
        """Carrega dados na tabela"""
        if not self.flow_data:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("❌ Nenhum dado encontrado"))
            return
        
        self.table.setRowCount(len(self.flow_data))
        
        for row, data in enumerate(self.flow_data):
            # Data
            if data.get('data_movimento'):
                try:
                    date_obj = datetime.strptime(str(data['data_movimento']), '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%d/%m/%Y')
                    self.table.setItem(row, 0, QTableWidgetItem(formatted_date))
                except:
                    self.table.setItem(row, 0, QTableWidgetItem(str(data['data_movimento'])))
            else:
                self.table.setItem(row, 0, QTableWidgetItem(""))
            
            # Movimento
            movement = data.get('tipo_movimento', '')
            movement_icons = {
                'Remessa': '📤', 'Regresso': '📥', 'Entrega': '🚚',
                'Devolução de Entrega': '↩️', 'Transferencia': '🔄', 'Retorno': '🔙'
            }
            icon = movement_icons.get(movement, '📋')
            self.table.setItem(row, 1, QTableWidgetItem(f"{icon} {movement}"))
            
            # RTI
            self.table.setItem(row, 2, QTableWidgetItem(str(data.get('rti', ''))))
            
            # Origem
            self.table.setItem(row, 3, QTableWidgetItem(str(data.get('local_origem', ''))))
            
            # Destino
            self.table.setItem(row, 4, QTableWidgetItem(str(data.get('local_destino', ''))))
            
            # Quantidade
            self.table.setItem(row, 5, QTableWidgetItem(str(data.get('quantidade', ''))))

class CDFlowAnalysisDialog(QDialog, ResponsiveDialog):
    """Diálogo específico para análise completa de fluxo de CDs - VERSÃO CORRIGIDA"""
    
    def __init__(self, cd_name, db_instance, parent=None):
        super().__init__(parent)
        self.cd_name = cd_name
        self.db = db_instance
        self.setWindowTitle(f"Análise Completa de Fluxo - {cd_name}")
        
        # **CORREÇÃO: Usa sistema responsivo para diálogos grandes**
        self.make_responsive("large", center=True)
        
        self.init_ui()
        self.load_cd_analysis()

    def init_ui(self):
        """Inicializa interface com abas específicas para CDs - VERSÃO RESPONSIVA"""
        main_layout = QVBoxLayout(self)
        
        # Cabeçalho responsivo
        header_layout = QHBoxLayout()
        
        title = QLabel(f"📊 Análise Completa de Fluxo - {self.cd_name}")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Período de análise
        period_label = QLabel("📅 Período: Todos os registros")
        period_label.setFont(QFont("Arial", 10))
        period_label.setStyleSheet("color: #666;")
        header_layout.addWidget(period_label)
        
        main_layout.addLayout(header_layout)
        
        # Widget de abas para diferentes análises
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 9))
        
        # **CORREÇÃO CRÍTICA: Criar aba de resumo ANTES de chamar método**
        self.create_summary_tab()
        
        # Aba 2: Saídas para Lojas (Remessas)
        self.create_outbound_tab()
        
        # Aba 3: Retornos das Lojas (Regressos)
        self.create_inbound_tab()
        
        # Aba 4: Transferências entre CDs
        self.create_transfers_tab()
        
        # Aba 5: Análise Temporal
        self.create_temporal_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Botões de ação responsivos
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("💾 Exportar Análise Completa")
        export_btn.setFont(QFont("Arial", 10))
        export_btn.setStyleSheet("background-color: #28a745; color: white; padding: 6px 12px;")
        export_btn.clicked.connect(self.export_analysis)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("❌ Fechar")
        close_btn.setFont(QFont("Arial", 10))
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)

    def create_summary_tab(self):
        """**MÉTODO FALTANTE CORRIGIDO**: Cria aba de resumo executivo"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grid de cards de resumo
        cards_layout = QGridLayout()
        
        # **CORREÇÃO: Cards de resumo responsivos**
        self.outbound_card = self.create_summary_card(
            "📤 Saídas Totais", "0", "Remessas para lojas", "#dc3545"
        )
        cards_layout.addWidget(self.outbound_card, 0, 0)
        
        self.inbound_card = self.create_summary_card(
            "📥 Retornos Totais", "0", "Regressos das lojas", "#28a745"
        )
        cards_layout.addWidget(self.inbound_card, 0, 1)
        
        self.transfers_card = self.create_summary_card(
            "🔄 Transferências", "0", "Entre CDs", "#007bff"
        )
        cards_layout.addWidget(self.transfers_card, 1, 0)
        
        self.balance_card = self.create_summary_card(
            "⚖️ Saldo Líquido", "0", "Entradas - Saídas", "#6c757d"
        )
        cards_layout.addWidget(self.balance_card, 1, 1)
        
        layout.addLayout(cards_layout)
        
        # Tabela de resumo por ativo
        assets_group = QGroupBox("📦 Resumo por Ativo")
        assets_layout = QVBoxLayout()
        
        self.assets_table = QTableWidget()
        self.assets_table.setColumnCount(5)
        self.assets_table.setHorizontalHeaderLabels([
            '📦 Ativo', '📤 Saídas', '📥 Entradas', '🔄 Transferências', '⚖️ Saldo'
        ])
        
        # Configurar tabela responsiva
        header = self.assets_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        self.assets_table.setAlternatingRowColors(True)
        self.assets_table.setSortingEnabled(True)
        
        assets_layout.addWidget(self.assets_table)
        assets_group.setLayout(assets_layout)
        layout.addWidget(assets_group)
        
        self.tabs.addTab(tab, "📊 Resumo")

    def create_summary_card(self, title, value, subtitle, color):
        """Cria um card de resumo RESPONSIVO E CORRIGIDO"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setLineWidth(2)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 8px;
                margin: 3px;
            }}
        """)
        
        # **CORREÇÃO CRÍTICA: Define política de tamanho responsiva**
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        card.setMinimumHeight(100)  # Altura mínima garantida
        card.setMaximumHeight(150)  # Altura máxima para não ficar muito grande
        
        layout = QVBoxLayout(card)
        layout.setSpacing(4)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Título
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(9)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {color};")
        layout.addWidget(title_label)
        
        # Valor principal
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_font = QFont()
        value_font.setPointSize(16)  # Tamanho adequado
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # Subtítulo
        subtitle_label = QLabel(subtitle)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 8))
        subtitle_label.setStyleSheet("color: #666;")
        layout.addWidget(subtitle_label)
        
        # **CORREÇÃO: Permite redimensionamento dinâmico**
        layout.addStretch(0)  # Remove stretch para garantir layout compacto
        
        # Armazenar referência ao label de valor para atualização
        card.value_label = value_label
        
        return card

    def create_outbound_tab(self):
        """Aba de análise de saídas (Remessas)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Informações gerais
        info_layout = QHBoxLayout()
        
        total_outbound_label = QLabel("📤 Total de Saídas: Calculando...")
        total_outbound_label.setFont(QFont("Arial", 14, QFont.Bold))
        total_outbound_label.setStyleSheet("color: #dc3545; padding: 10px;")
        info_layout.addWidget(total_outbound_label)
        
        info_layout.addStretch()
        
        unique_stores_label = QLabel("🏪 Lojas Atendidas: Calculando...")
        unique_stores_label.setFont(QFont("Arial", 12))
        unique_stores_label.setStyleSheet("color: #666; padding: 10px;")
        info_layout.addWidget(unique_stores_label)
        
        layout.addLayout(info_layout)
        
        # Tabela detalhada de saídas
        outbound_group = QGroupBox("📤 Detalhamento de Remessas por Loja")
        outbound_layout = QVBoxLayout()
        
        self.outbound_table = QTableWidget()
        self.outbound_table.setColumnCount(6)
        self.outbound_table.setHorizontalHeaderLabels([
            '🏪 Loja Destino', '📦 HB618', '📦 HB623', '📦 Total', '📅 Última Remessa', '📈 Frequência'
        ])
        
        # Configurar tabela
        header = self.outbound_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.outbound_table.setAlternatingRowColors(True)
        self.outbound_table.setSortingEnabled(True)
        
        outbound_layout.addWidget(self.outbound_table)
        outbound_group.setLayout(outbound_layout)
        layout.addWidget(outbound_group)
        
        # Armazenar labels para atualização
        self.total_outbound_label = total_outbound_label
        self.unique_stores_label = unique_stores_label
        
        self.tabs.addTab(tab, "📤 Saídas")

    def create_inbound_tab(self):
        """Aba de análise de entradas (Regressos)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Informações gerais
        info_layout = QHBoxLayout()
        
        total_inbound_label = QLabel("📥 Total de Retornos: Calculando...")
        total_inbound_label.setFont(QFont("Arial", 14, QFont.Bold))
        total_inbound_label.setStyleSheet("color: #28a745; padding: 10px;")
        info_layout.addWidget(total_inbound_label)
        
        info_layout.addStretch()
        
        return_rate_label = QLabel("📊 Taxa de Retorno: Calculando...")
        return_rate_label.setFont(QFont("Arial", 12))
        return_rate_label.setStyleSheet("color: #666; padding: 10px;")
        info_layout.addWidget(return_rate_label)
        
        layout.addLayout(info_layout)
        
        # Tabela detalhada de retornos
        inbound_group = QGroupBox("📥 Detalhamento de Regressos por Loja")
        inbound_layout = QVBoxLayout()
        
        self.inbound_table = QTableWidget()
        self.inbound_table.setColumnCount(6)
        self.inbound_table.setHorizontalHeaderLabels([
            '🏪 Loja Origem', '📦 HB618', '📦 HB623', '📦 Total', '📅 Último Regresso', '📈 Frequência'
        ])
        
        # Configurar tabela
        header = self.inbound_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.inbound_table.setAlternatingRowColors(True)
        self.inbound_table.setSortingEnabled(True)
        
        inbound_layout.addWidget(self.inbound_table)
        inbound_group.setLayout(inbound_layout)
        layout.addWidget(inbound_group)
        
        # Armazenar labels para atualização
        self.total_inbound_label = total_inbound_label
        self.return_rate_label = return_rate_label
        
        self.tabs.addTab(tab, "📥 Retornos")

    def create_transfers_tab(self):
        """Aba de análise de transferências entre CDs"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Splitter para entrada e saída
        splitter = QSplitter(Qt.Horizontal)
        
        # Transferências de saída
        outbound_transfers_group = QGroupBox("📤 Transferências de Saída")
        outbound_transfers_layout = QVBoxLayout()
        
        self.transfers_out_table = QTableWidget()
        self.transfers_out_table.setColumnCount(5)
        self.transfers_out_table.setHorizontalHeaderLabels([
            '🏢 CD Destino', '📦 HB618', '📦 HB623', '📦 Total', '📅 Última'
        ])
        
        outbound_transfers_layout.addWidget(self.transfers_out_table)
        outbound_transfers_group.setLayout(outbound_transfers_layout)
        splitter.addWidget(outbound_transfers_group)
        
        # Transferências de entrada
        inbound_transfers_group = QGroupBox("📥 Transferências de Entrada")
        inbound_transfers_layout = QVBoxLayout()
        
        self.transfers_in_table = QTableWidget()
        self.transfers_in_table.setColumnCount(5)
        self.transfers_in_table.setHorizontalHeaderLabels([
            '🏢 CD Origem', '📦 HB618', '📦 HB623', '📦 Total', '📅 Última'
        ])
        
        inbound_transfers_layout.addWidget(self.transfers_in_table)
        inbound_transfers_group.setLayout(inbound_transfers_layout)
        splitter.addWidget(inbound_transfers_group)
        
        layout.addWidget(splitter)
        
        self.tabs.addTab(tab, "🔄 Transferências")

    def create_temporal_tab(self):
        """Aba de análise temporal"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Gráfico temporal (simulado com tabela)
        temporal_group = QGroupBox("📈 Movimentação por Período")
        temporal_layout = QVBoxLayout()
        
        # Filtros de período
        filter_layout = QHBoxLayout()
        
        period_label = QLabel("Agrupar por:")
        filter_layout.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(['Diário', 'Semanal', 'Mensal'])
        self.period_combo.currentTextChanged.connect(self.update_temporal_analysis)
        filter_layout.addWidget(self.period_combo)
        
        filter_layout.addStretch()
        
        temporal_layout.addLayout(filter_layout)
        
        # Tabela temporal
        self.temporal_table = QTableWidget()
        self.temporal_table.setColumnCount(6)
        self.temporal_table.setHorizontalHeaderLabels([
            '📅 Período', '📤 Saídas', '📥 Entradas', '🔄 Transferências', '⚖️ Saldo', '📊 Variação'
        ])
        
        temporal_layout.addWidget(self.temporal_table)
        temporal_group.setLayout(temporal_layout)
        layout.addWidget(temporal_group)
        
        self.tabs.addTab(tab, "📈 Temporal")

    def load_cd_analysis(self):
        """Carrega análise completa do CD"""
        print(f"=== CARREGANDO ANÁLISE COMPLETA PARA {self.cd_name} ===")
        
        # Busca todos os movimentos relacionados ao CD
        movements_query = """
        SELECT data_movimento, tipo_movimento, rti, quantidade, 
                local_origem, local_destino, guia, nota_fiscal
        FROM movimentos 
        WHERE local_origem = ? OR local_destino = ?
        ORDER BY data_movimento DESC, id DESC
        """
        movements = self.db._execute_query(movements_query, (self.cd_name, self.cd_name))
        
        # Processar dados
        self.process_movements_data(movements)
        
        # Atualizar todas as abas
        self.update_summary_tab()
        self.update_outbound_tab()
        self.update_inbound_tab()
        self.update_transfers_tab()
        self.update_temporal_analysis()

    def process_movements_data(self, movements):
        """Processa dados de movimentos para análise"""
        self.outbound_data = defaultdict(lambda: defaultdict(int))  # Por loja
        self.inbound_data = defaultdict(lambda: defaultdict(int))   # Por loja
        self.transfers_out_data = defaultdict(lambda: defaultdict(int))  # Para outros CDs
        self.transfers_in_data = defaultdict(lambda: defaultdict(int))   # De outros CDs
        self.temporal_data = defaultdict(lambda: defaultdict(int))  # Por data
        
        # Contadores totais
        self.total_outbound = defaultdict(int)
        self.total_inbound = defaultdict(int)
        self.total_transfers_out = defaultdict(int)
        self.total_transfers_in = defaultdict(int)
        
        # Últimas datas
        self.last_outbound_dates = {}
        self.last_inbound_dates = {}
        self.last_transfer_dates = {}
        
        def normalize_asset(asset):
            """Normaliza nome do ativo"""
            if not asset:
                return 'N/A'
            return str(asset).strip().upper().replace(' ', '')
        
        for mov in movements:
            rti = normalize_asset(mov['rti'])
            qty = mov['quantidade']
            tipo = mov['tipo_movimento']
            origem = mov['local_origem']
            destino = mov['local_destino']
            data = mov['data_movimento']
            
            # **SAÍDAS DO CD (Remessas para lojas)**
            if origem == self.cd_name and destino and destino.startswith('LOJA'):
                if tipo == 'Remessa':
                    self.outbound_data[destino][rti] += qty
                    self.total_outbound[rti] += qty
                    self.last_outbound_dates[destino] = data
                    
                    # Dados temporais
                    self.temporal_data[data]['saidas'] += qty
            
            # **ENTRADAS NO CD (Regressos de lojas)**
            elif destino == self.cd_name and origem and origem.startswith('LOJA'):
                if tipo == 'Regresso':
                    self.inbound_data[origem][rti] += qty
                    self.total_inbound[rti] += qty
                    self.last_inbound_dates[origem] = data
                    
                    # Dados temporais
                    self.temporal_data[data]['entradas'] += qty
            
            # **TRANSFERÊNCIAS ENTRE CDs**
            elif origem == self.cd_name and destino and 'CD' in destino:
                if tipo in ('Transferencia', 'Remessa'):
                    self.transfers_out_data[destino][rti] += qty
                    self.total_transfers_out[rti] += qty
                    self.last_transfer_dates[destino] = data
                    
                    # Dados temporais
                    self.temporal_data[data]['transferencias_out'] += qty
                    
            elif destino == self.cd_name and origem and 'CD' in origem:
                if tipo in ('Transferencia', 'Entrega', 'Retorno'):
                    self.transfers_in_data[origem][rti] += qty
                    self.total_transfers_in[rti] += qty
                    self.last_transfer_dates[origem] = data
                    
                    # Dados temporais
                    self.temporal_data[data]['transferencias_in'] += qty

    def update_summary_tab(self):
        """Atualiza aba de resumo"""
        # Calcular totais
        total_out = sum(self.total_outbound.values())
        total_in = sum(self.total_inbound.values())
        total_transfers = sum(self.total_transfers_out.values()) + sum(self.total_transfers_in.values())
        saldo_liquido = total_in - total_out
        
        # Atualizar cards
        self.outbound_card.value_label.setText(f"{total_out:,}".replace(",", "."))
        self.inbound_card.value_label.setText(f"{total_in:,}".replace(",", "."))
        self.transfers_card.value_label.setText(f"{total_transfers:,}".replace(",", "."))
        
        # Saldo com cor baseada no valor
        if saldo_liquido > 0:
            color = "#28a745"
            signal = "+"
        elif saldo_liquido < 0:
            color = "#dc3545" 
            signal = ""
        else:
            color = "#6c757d"
            signal = ""
            
        self.balance_card.value_label.setText(f"{signal}{saldo_liquido:,}".replace(",", "."))
        self.balance_card.value_label.setStyleSheet(f"color: {color};")
        
        # Atualizar tabela de ativos
        assets = set(list(self.total_outbound.keys()) + list(self.total_inbound.keys()) + 
                    list(self.total_transfers_out.keys()) + list(self.total_transfers_in.keys()))
        
        self.assets_table.setRowCount(len(assets))
        
        for i, asset in enumerate(sorted(assets)):
            saidas = self.total_outbound.get(asset, 0)
            entradas = self.total_inbound.get(asset, 0)
            transf = self.total_transfers_out.get(asset, 0) + self.total_transfers_in.get(asset, 0)
            saldo = entradas - saidas
            
            self.assets_table.setItem(i, 0, QTableWidgetItem(asset))
            self.assets_table.setItem(i, 1, QTableWidgetItem(f"{saidas:,}".replace(",", ".")))
            self.assets_table.setItem(i, 2, QTableWidgetItem(f"{entradas:,}".replace(",", ".")))
            self.assets_table.setItem(i, 3, QTableWidgetItem(f"{transf:,}".replace(",", ".")))
            
            # Saldo com cor
            saldo_item = QTableWidgetItem(f"{saldo:+,}".replace(",", "."))
            if saldo > 0:
                saldo_item.setBackground(QColor(200, 255, 200))
            elif saldo < 0:
                saldo_item.setBackground(QColor(255, 200, 200))
            
            self.assets_table.setItem(i, 4, saldo_item)

    def update_outbound_tab(self):
        """Atualiza aba de saídas"""
        total_saidas = sum(self.total_outbound.values())
        lojas_atendidas = len(self.outbound_data)
        
        self.total_outbound_label.setText(f"📤 Total de Saídas: {total_saidas:,}".replace(",", "."))
        self.unique_stores_label.setText(f"🏪 Lojas Atendidas: {lojas_atendidas}")
        
        # Preencher tabela
        self.outbound_table.setRowCount(len(self.outbound_data))
        
        for i, (loja, assets) in enumerate(self.outbound_data.items()):
            hb618 = assets.get('HB618', 0)
            hb623 = assets.get('HB623', 0)
            total = hb618 + hb623
            
            # Calcular frequência (número de remessas diferentes)
            freq_query = """
            SELECT COUNT(DISTINCT data_movimento) as freq
            FROM movimentos 
            WHERE local_origem = ? AND local_destino = ? AND tipo_movimento = 'Remessa'
            """
            freq_result = self.db._execute_query(freq_query, (self.cd_name, loja))
            frequencia = freq_result[0]['freq'] if freq_result else 0
            
            self.outbound_table.setItem(i, 0, QTableWidgetItem(loja))
            self.outbound_table.setItem(i, 1, QTableWidgetItem(f"{hb618:,}".replace(",", ".")))
            self.outbound_table.setItem(i, 2, QTableWidgetItem(f"{hb623:,}".replace(",", ".")))
            self.outbound_table.setItem(i, 3, QTableWidgetItem(f"{total:,}".replace(",", ".")))
            self.outbound_table.setItem(i, 4, QTableWidgetItem(self.last_outbound_dates.get(loja, "N/A")))
            self.outbound_table.setItem(i, 5, QTableWidgetItem(f"{frequencia} remessas"))

    def update_inbound_tab(self):
        """Atualiza aba de retornos"""
        total_retornos = sum(self.total_inbound.values())
        total_saidas = sum(self.total_outbound.values())
        
        # Taxa de retorno
        taxa_retorno = (total_retornos / total_saidas * 100) if total_saidas > 0 else 0
        
        self.total_inbound_label.setText(f"📥 Total de Retornos: {total_retornos:,}".replace(",", "."))
        self.return_rate_label.setText(f"📊 Taxa de Retorno: {taxa_retorno:.1f}%")
        
        # Preencher tabela
        self.inbound_table.setRowCount(len(self.inbound_data))
        
        for i, (loja, assets) in enumerate(self.inbound_data.items()):
            hb618 = assets.get('HB618', 0)
            hb623 = assets.get('HB623', 0)
            total = hb618 + hb623
            
            # Calcular frequência
            freq_query = """
            SELECT COUNT(DISTINCT data_movimento) as freq
            FROM movimentos 
            WHERE local_destino = ? AND local_origem = ? AND tipo_movimento = 'Regresso'
            """
            freq_result = self.db._execute_query(freq_query, (self.cd_name, loja))
            frequencia = freq_result[0]['freq'] if freq_result else 0
            
            self.inbound_table.setItem(i, 0, QTableWidgetItem(loja))
            self.inbound_table.setItem(i, 1, QTableWidgetItem(f"{hb618:,}".replace(",", ".")))
            self.inbound_table.setItem(i, 2, QTableWidgetItem(f"{hb623:,}".replace(",", ".")))
            self.inbound_table.setItem(i, 3, QTableWidgetItem(f"{total:,}".replace(",", ".")))
            self.inbound_table.setItem(i, 4, QTableWidgetItem(self.last_inbound_dates.get(loja, "N/A")))
            self.inbound_table.setItem(i, 5, QTableWidgetItem(f"{frequencia} regressos"))

    def update_transfers_tab(self):
        """Atualiza aba de transferências"""
        # Transferências de saída
        self.transfers_out_table.setRowCount(len(self.transfers_out_data))
        
        for i, (cd_destino, assets) in enumerate(self.transfers_out_data.items()):
            hb618 = assets.get('HB618', 0)
            hb623 = assets.get('HB623', 0)
            total = hb618 + hb623
            
            self.transfers_out_table.setItem(i, 0, QTableWidgetItem(cd_destino))
            self.transfers_out_table.setItem(i, 1, QTableWidgetItem(f"{hb618:,}".replace(",", ".")))
            self.transfers_out_table.setItem(i, 2, QTableWidgetItem(f"{hb623:,}".replace(",", ".")))
            self.transfers_out_table.setItem(i, 3, QTableWidgetItem(f"{total:,}".replace(",", ".")))
            self.transfers_out_table.setItem(i, 4, QTableWidgetItem(self.last_transfer_dates.get(cd_destino, "N/A")))
        
        # Transferências de entrada
        self.transfers_in_table.setRowCount(len(self.transfers_in_data))
        
        for i, (cd_origem, assets) in enumerate(self.transfers_in_data.items()):
            hb618 = assets.get('HB618', 0)
            hb623 = assets.get('HB623', 0)
            total = hb618 + hb623
            
            self.transfers_in_table.setItem(i, 0, QTableWidgetItem(cd_origem))
            self.transfers_in_table.setItem(i, 1, QTableWidgetItem(f"{hb618:,}".replace(",", ".")))
            self.transfers_in_table.setItem(i, 2, QTableWidgetItem(f"{hb623:,}".replace(",", ".")))
            self.transfers_in_table.setItem(i, 3, QTableWidgetItem(f"{total:,}".replace(",", ".")))
            self.transfers_in_table.setItem(i, 4, QTableWidgetItem(self.last_transfer_dates.get(cd_origem, "N/A")))

    def update_temporal_analysis(self):
        """Atualiza análise temporal"""
        period_type = self.period_combo.currentText()
        
        # Agrupar dados por período
        grouped_data = defaultdict(lambda: defaultdict(int))
        
        for date_str, movements in self.temporal_data.items():
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                
                if period_type == 'Diário':
                    period_key = date_obj.strftime('%d/%m/%Y')
                elif period_type == 'Semanal':
                    # Início da semana (segunda-feira)
                    start_week = date_obj - timedelta(days=date_obj.weekday())
                    period_key = f"Semana {start_week.strftime('%d/%m/%Y')}"
                else:  # Mensal
                    period_key = date_obj.strftime('%m/%Y')
                
                for mov_type, qty in movements.items():
                    grouped_data[period_key][mov_type] += qty
                    
            except ValueError:
                continue
        
        # Preencher tabela temporal
        self.temporal_table.setRowCount(len(grouped_data))
        
        for i, (period, data) in enumerate(sorted(grouped_data.items(), reverse=True)):
            saidas = data.get('saidas', 0)
            entradas = data.get('entradas', 0)
            transf_out = data.get('transferencias_out', 0)
            transf_in = data.get('transferencias_in', 0)
            transferencias = transf_out + transf_in
            saldo = entradas - saidas
            
            # Calcular variação (simulada)
            variacao = "N/A"
            if i < len(grouped_data) - 1:
                # Comparar com período anterior (lógica simplificada)
                if saldo > 0:
                    variacao = "📈 +X%"
                elif saldo < 0:
                    variacao = "📉 -X%"
                else:
                    variacao = "➡️ 0%"
            
            self.temporal_table.setItem(i, 0, QTableWidgetItem(period))
            self.temporal_table.setItem(i, 1, QTableWidgetItem(f"{saidas:,}".replace(",", ".")))
            self.temporal_table.setItem(i, 2, QTableWidgetItem(f"{entradas:,}".replace(",", ".")))
            self.temporal_table.setItem(i, 3, QTableWidgetItem(f"{transferencias:,}".replace(",", ".")))
            
            # Saldo com cor
            saldo_item = QTableWidgetItem(f"{saldo:+,}".replace(",", "."))
            if saldo > 0:
                saldo_item.setBackground(QColor(200, 255, 200))
            elif saldo < 0:
                saldo_item.setBackground(QColor(255, 200, 200))
            
            self.temporal_table.setItem(i, 4, saldo_item)
            self.temporal_table.setItem(i, 5, QTableWidgetItem(variacao))

    def export_analysis(self):
        """Exporta análise completa"""
        try:
            import pandas as pd
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            import datetime
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Salvar Análise Completa", 
                f"analise_cd_{self.cd_name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", 
                "Excel (*.xlsx)"
            )
            
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Aba 1: Resumo
                    summary_data = []
                    summary_data.append({
                        'Métrica': 'Total de Saídas',
                        'Valor': sum(self.total_outbound.values()),
                        'Descrição': 'Remessas para lojas'
                    })
                    summary_data.append({
                        'Métrica': 'Total de Retornos',
                        'Valor': sum(self.total_inbound.values()),
                        'Descrição': 'Regressos das lojas'
                    })
                    summary_data.append({
                        'Métrica': 'Transferências',
                        'Valor': sum(self.total_transfers_out.values()) + sum(self.total_transfers_in.values()),
                        'Descrição': 'Entre CDs'
                    })
                    
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Resumo', index=False)
                    
                    # Aba 2: Saídas detalhadas
                    outbound_data = []
                    for loja, assets in self.outbound_data.items():
                        outbound_data.append({
                            'Loja': loja,
                            'HB618': assets.get('HB618', 0),
                            'HB623': assets.get('HB623', 0),
                            'Total': sum(assets.values()),
                            'Última_Remessa': self.last_outbound_dates.get(loja, 'N/A')
                        })
                    
                    if outbound_data:
                        outbound_df = pd.DataFrame(outbound_data)
                        outbound_df.to_excel(writer, sheet_name='Saídas_Detalhadas', index=False)
                    
                    # Aba 3: Retornos detalhados
                    inbound_data = []
                    for loja, assets in self.inbound_data.items():
                        inbound_data.append({
                            'Loja': loja,
                            'HB618': assets.get('HB618', 0),
                            'HB623': assets.get('HB623', 0),
                            'Total': sum(assets.values()),
                            'Último_Regresso': self.last_inbound_dates.get(loja, 'N/A')
                        })
                    
                    if inbound_data:
                        inbound_df = pd.DataFrame(inbound_data)
                        inbound_df.to_excel(writer, sheet_name='Retornos_Detalhados', index=False)
                    
                    # Aba 4: Transferências
                    transfers_data = []
                    
                    # Transferências de saída
                    for cd, assets in self.transfers_out_data.items():
                        transfers_data.append({
                            'Tipo': 'Saída',
                            'CD_Relacionado': cd,
                            'HB618': assets.get('HB618', 0),
                            'HB623': assets.get('HB623', 0),
                            'Total': sum(assets.values())
                        })
                    
                    # Transferências de entrada
                    for cd, assets in self.transfers_in_data.items():
                        transfers_data.append({
                            'Tipo': 'Entrada',
                            'CD_Relacionado': cd,
                            'HB618': assets.get('HB618', 0),
                            'HB623': assets.get('HB623', 0),
                            'Total': sum(assets.values())
                        })
                    
                    if transfers_data:
                        transfers_df = pd.DataFrame(transfers_data)
                        transfers_df.to_excel(writer, sheet_name='Transferências', index=False)
                
                QMessageBox.information(self, "✅ Sucesso", f"Análise completa exportada para:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "❌ Erro", f"Erro ao exportar análise:\n{e}")

class FlowVisualDialog(QDialog, ResponsiveDialog):
    """Diálogo de fluxo visual melhorado - VERSÃO CORRIGIDA PARA CARDS RESPONSIVOS"""
    def __init__(self, location_name, db_instance, parent=None):
        super().__init__(parent)
        self.location_name = location_name
        self.db = db_instance
        self.setWindowTitle(f"Fluxo Visual - {location_name}")
        
        # **CORREÇÃO: Usa sistema responsivo**
        self.make_responsive("large", center=True)
        
        # Detecta se é CD e oferece análise completa
        self.is_cd = not location_name.startswith('LOJA')
        
        if self.is_cd:
            self.daily_data = self.get_cd_daily_evolution(location_name)
        else:
            self.daily_data = self.db.get_daily_stock_evolution(location_name)
        
        self.asset_filter = "Todos"
        
        self.init_ui()
        self.update_flow_display()

    def init_ui(self):
        """Interface melhorada e RESPONSIVA"""
        main_layout = QVBoxLayout(self)
        
        # **CORREÇÃO: Fonte base menor**
        base_font = QFont()
        base_font.setPointSize(10)
        self.setFont(base_font)
        
        # Cabeçalho melhorado
        header_layout = QHBoxLayout()
        
        title_label = QLabel(f"Evolução do Estoque - {self.location_name}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botão de análise completa para CDs
        if self.is_cd:
            self.analysis_button = QPushButton("📊 Análise Completa")
            self.analysis_button.setFont(QFont("Arial", 10))
            self.analysis_button.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    padding: 6px 12px;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            self.analysis_button.clicked.connect(self.open_complete_analysis)
            header_layout.addWidget(self.analysis_button)
        
        # Filtro por ativo
        filter_label = QLabel("Filtrar por ativo:")
        filter_label.setFont(QFont("Arial", 10))
        header_layout.addWidget(filter_label)
        
        self.asset_combo = QComboBox()
        self.asset_combo.addItem("Todos")
        self.asset_combo.setFont(QFont("Arial", 10))
        
        # Detecta ativos
        if self.daily_data:
            assets_found = set()
            
            if not self.is_cd:
                initial_inventory = self.get_initial_inventory()
                assets_found.update(initial_inventory.keys())
            
            for day_data in self.daily_data:
                movements = day_data.get('movements', [])
                if isinstance(movements, list):
                    for mov in movements:
                        if hasattr(mov, 'keys'):
                            rti = mov['rti'] if mov['rti'] else None
                        else:
                            rti = mov.get('rti')
                        
                        if rti:
                            normalized_rti = str(rti).strip().upper().replace(' ', '')
                            assets_found.add(normalized_rti)
            
            for asset in sorted(assets_found):
                self.asset_combo.addItem(asset)
        
        self.asset_combo.currentTextChanged.connect(self.on_filter_changed)
        header_layout.addWidget(self.asset_combo)
        
        main_layout.addLayout(header_layout)
        
        # **CORREÇÃO CRÍTICA: Área de scroll com configuração responsiva melhorada**
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # **CORREÇÃO: Widget de flow com configurações responsivas**
        self.flow_widget = QWidget()
        self.flow_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        
        self.flow_layout = QHBoxLayout(self.flow_widget)
        self.flow_layout.setSpacing(10)  # **CORREÇÃO: Espaçamento reduzido**
        self.flow_layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll_area.setWidget(self.flow_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Botões de ação responsivos
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("💾 Exportar Fluxo")
        export_btn.setFont(QFont("Arial", 10))
        export_btn.clicked.connect(self.export_flow)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("❌ Fechar")
        close_btn.setFont(QFont("Arial", 10))
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)

    def open_complete_analysis(self):
        """Abre análise completa para CDs"""
        analysis_dialog = CDFlowAnalysisDialog(self.location_name, self.db, self)
        analysis_dialog.exec_()

    def get_cd_daily_evolution(self, cd_name):
        """Calcula evolução diária para CDs"""
        print(f"=== EVOLUÇÃO CD PARA {cd_name} ===")
        
        movements_query = """
        SELECT data_movimento, tipo_movimento, rti, quantidade, local_origem, local_destino
        FROM movimentos 
        WHERE (local_origem = ? OR local_destino = ?)
        ORDER BY data_movimento ASC, id ASC
        """
        movements = self.db._execute_query(movements_query, (cd_name, cd_name))

        def normalize_asset_name(asset_name):
            if not asset_name:
                return 'N/A'
            normalized = str(asset_name).strip().upper()
            normalized = normalized.replace(' ', '')
            return normalized

        from collections import defaultdict
        movements_by_date = defaultdict(list)
        for mov in movements:
            movements_by_date[mov['data_movimento']].append(mov)

        daily_evolution = []
        current_stock = defaultdict(int)  # Começa com zero para CDs
        
        # Processa cada data em ordem
        for date in sorted(movements_by_date.keys()):
            day_movements = movements_by_date[date]
            
            print(f"\n--- Processando data CD: {date} ---")
            print(f"Estoque CD no início do dia: {dict(current_stock)}")
            
            # Aplica todos os movimentos do dia
            for mov in day_movements:
                raw_rti = mov['rti'] if mov['rti'] else 'N/A'
                rti = normalize_asset_name(raw_rti)
                qtde = mov['quantidade']
                tipo = mov['tipo_movimento']
                origem = mov['local_origem']
                destino = mov['local_destino']
                
                print(f"Movimento CD: {tipo} {qtde} '{raw_rti}' -> '{rti}' (de {origem} para {destino})")
                
                old_qty = current_stock[rti]
                
                # Lógica para CDs
                if destino == cd_name:
                    if tipo in ('Regresso', 'Entrega', 'Transferencia', 'Retorno'):
                        current_stock[rti] += qtde
                        print(f"  ✅ Entrada CD: {rti} {old_qty} + {qtde} = {current_stock[rti]}")
                        
                elif origem == cd_name:
                    if tipo in ('Remessa', 'Transferencia', 'Devolução de Entrega'):
                        current_stock[rti] -= qtde
                        print(f"  ❌ Saída CD: {rti} {old_qty} - {qtde} = {current_stock[rti]}")

            print(f"Estoque CD final do dia {date}: {dict(current_stock)}")

            daily_evolution.append({
                'date': date,
                'stock': current_stock.copy(),
                'movements': day_movements.copy()
            })

        return daily_evolution

    def on_filter_changed(self, asset_name):
        self.asset_filter = asset_name
        self.update_flow_display()

    def update_flow_display(self):
        # Limpa layout atual
        for i in reversed(range(self.flow_layout.count())):
            child = self.flow_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if not self.daily_data:
            no_data_label = QLabel(f"❌ Nenhum dado encontrado para {self.location_name}.\n\n📦 {'Carregue o inventário inicial nas configurações.' if not self.is_cd else 'Verifique se há movimentos para este CD.'}")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setFont(QFont("Arial", 14))
            no_data_label.setStyleSheet("""
                QLabel {
                    color: #666; 
                    font-size: 16px; 
                    padding: 50px;
                    background-color: #f8f9fa;
                    border: 2px dashed #dee2e6;
                    border-radius: 10px;
                }
            """)
            self.flow_layout.addWidget(no_data_label)
            return
        
        # Para lojas, adiciona inventário inicial
        if not self.is_cd:
            self.add_inventory_card()
            if self.daily_data:
                self.add_arrow()
        
        # Adiciona cards para cada dia
        for i, day_data in enumerate(self.daily_data):
            self.add_day_card(day_data, i)
            
            if i < len(self.daily_data) - 1:
                self.add_arrow()
        
        self.flow_layout.addStretch()

    def add_inventory_card(self):
        """Adiciona card do inventário inicial (só para lojas)"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setLineWidth(2)
        card.setStyleSheet("""
            QFrame {
                background-color: #e8f5e8;
                border: 2px solid #5cb85c;
                border-radius: 8px;
                margin: 3px;
            }
        """)
        
        # **CORREÇÃO CRÍTICA: Define tamanho fixo e política de tamanho**
        card.setFixedWidth(280)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        card.setMinimumHeight(250)  # Altura mínima garantida
        card.setMaximumHeight(400)  # Altura máxima para evitar cards gigantes
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Título
        title = QLabel("📦 INVENTÁRIO INICIAL")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Data
        date_label = QLabel("📅 08/06/2025")
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setFont(QFont("Arial", 10))
        date_label.setStyleSheet("color: #666;")
        layout.addWidget(date_label)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #5cb85c;")
        layout.addWidget(separator)
        
        # Estoque inicial
        stock_title = QLabel("📊 Estoque Base:")
        stock_title.setFont(QFont("Arial", 10, QFont.Bold))
        stock_title.setStyleSheet("color: #2d5a2d;")
        layout.addWidget(stock_title)
        
        inventory_data = self.get_initial_inventory()
        if inventory_data:
            for asset, quantity in inventory_data.items():
                if self.asset_filter == "Todos" or self.asset_filter == asset:
                    asset_label = QLabel(f"• {asset}: {quantity:,}".replace(",", "."))
                    asset_label.setFont(QFont("Arial", 11, QFont.Bold))
                    asset_label.setStyleSheet("padding: 3px;")
                    layout.addWidget(asset_label)
        else:
            no_stock_label = QLabel("⚠️ Sem dados")
            no_stock_label.setFont(QFont("Arial", 10))
            no_stock_label.setStyleSheet("color: #999; font-style: italic;")
            layout.addWidget(no_stock_label)
        
        layout.addStretch()
        self.flow_layout.addWidget(card)

    def add_day_card(self, day_data, day_index):
        """**CORREÇÃO CRÍTICA**: Adiciona card de um dia específico com altura corrigida"""
        
        def normalize_asset_name(asset_name):
            if not asset_name:
                return 'N/A'
            normalized = str(asset_name).strip().upper()
            normalized = normalized.replace(' ', '')
            return normalized
        
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setLineWidth(2)
        card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #007bff;
                border-radius: 8px;
                margin: 3px;
            }
        """)
        
        # **CORREÇÃO CRÍTICA: Tamanho fixo responsivo**
        card.setFixedWidth(280)  # Largura fixa para consistência
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        card.setMinimumHeight(300)  # **CORREÇÃO: Altura mínima suficiente**
        card.setMaximumHeight(500)  # **CORREÇÃO: Altura máxima controlada**
        
        layout = QVBoxLayout(card)
        layout.setSpacing(6)  # **CORREÇÃO: Espaçamento adequado**
        layout.setContentsMargins(10, 10, 10, 10)
        # Título com data
        date_str = day_data['date']
        if isinstance(date_str, str):
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d/%m/%Y')
                day_name = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'][date_obj.weekday()]
                title_text = f"📅 {formatted_date} ({day_name})"
            except:
                title_text = f"📅 {date_str}"
        else:
            title_text = f"📅 {date_str}"
            
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)  # **CORREÇÃO: Fonte adequada**
        title.setFont(title_font)
        layout.addWidget(title)
        
        # **CORREÇÃO: Calcula saldo inicial corretamente**
        if not self.is_cd and day_index == 0:
            previous_stock = self.get_initial_inventory()
        elif not self.is_cd and day_index > 0:
            previous_day_data = self.daily_data[day_index - 1]
            previous_stock = previous_day_data['stock']
        else:
            if day_index == 0:
                previous_stock = {}
            else:
                previous_day_data = self.daily_data[day_index - 1]
                previous_stock = previous_day_data['stock']
        
        # **CORREÇÃO: Seção de saldo inicial com altura controlada**
        initial_frame = QFrame()
        initial_frame.setStyleSheet("background-color: #e3f2fd; border-radius: 4px; margin: 2px;")
        initial_frame.setMaximumHeight(80)  # **CORREÇÃO: Altura máxima**
        initial_layout = QVBoxLayout(initial_frame)
        initial_layout.setContentsMargins(8, 5, 8, 5)
        initial_layout.setSpacing(2)  # **CORREÇÃO: Espaçamento menor**
        
        initial_title = QLabel("📊 Saldo Inicial:")
        initial_title.setFont(QFont("Arial", 9, QFont.Bold))
        initial_title.setStyleSheet("color: #1565c0;")
        initial_layout.addWidget(initial_title)
        
        # **CORREÇÃO: Limita número de itens mostrados no saldo inicial**
        shown_items = 0
        max_items = 2  # Máximo 2 itens para economizar espaço
        
        if previous_stock:
            for asset, quantity in list(previous_stock.items())[:max_items]:
                if self.asset_filter == "Todos" or self.asset_filter == asset:
                    initial_label = QLabel(f"• {asset}: {quantity:,}".replace(",", "."))
                    initial_label.setFont(QFont("Arial", 8))  # **CORREÇÃO: Fonte menor**
                    initial_label.setStyleSheet("padding: 1px;")
                    initial_layout.addWidget(initial_label)
                    shown_items += 1
            
            # Se há mais itens, mostra indicador
            if len(previous_stock) > max_items:
                more_label = QLabel(f"... e mais {len(previous_stock) - max_items} itens")
                more_label.setFont(QFont("Arial", 8))
                more_label.setStyleSheet("color: #666; font-style: italic; padding: 1px;")
                initial_layout.addWidget(more_label)
        else:
            zero_label = QLabel("• Saldo: 0")
            zero_label.setFont(QFont("Arial", 8))
            zero_label.setStyleSheet("padding: 1px; color: #666;")
            initial_layout.addWidget(zero_label)
        
        layout.addWidget(initial_frame)
        
        # **CORREÇÃO: Seção de movimentos com altura controlada**
        movements = day_data.get('movements', [])
        if movements:
            movements_frame = QFrame()
            movements_frame.setStyleSheet("background-color: #fff3cd; border-radius: 4px; margin: 2px;")
            movements_frame.setMaximumHeight(100)  # **CORREÇÃO: Altura máxima**
            movements_layout = QVBoxLayout(movements_frame)
            movements_layout.setContentsMargins(8, 5, 8, 5)
            movements_layout.setSpacing(2)
            
            movements_title = QLabel("🔄 Movimentos:")
            movements_title.setFont(QFont("Arial", 9, QFont.Bold))
            movements_title.setStyleSheet("color: #856404;")
            movements_layout.addWidget(movements_title)
            
            # **CORREÇÃO: Agrupa movimentos por ativo para economizar espaço**
            movements_by_asset = defaultdict(list)
            for mov in movements:
                if hasattr(mov, 'keys'):
                    raw_rti = mov['rti'] if mov['rti'] else 'N/A'
                    rti = normalize_asset_name(raw_rti)
                    tipo = mov['tipo_movimento']
                    qtde = mov['quantidade']
                    origem = mov['local_origem']
                    destino = mov['local_destino']
                else:
                    raw_rti = mov.get('rti', 'N/A') or 'N/A'
                    rti = normalize_asset_name(raw_rti)
                    tipo = mov.get('tipo_movimento', '')
                    qtde = mov.get('quantidade', 0)
                    origem = mov.get('local_origem', '')
                    destino = mov.get('local_destino', '')
                
                if self.asset_filter == "Todos" or normalize_asset_name(self.asset_filter) == rti:
                    movements_by_asset[rti].append({
                        'tipo': tipo, 'qtde': qtde, 'origem': origem, 'destino': destino
                    })
            
            # **CORREÇÃO: Mostra movimentos agrupados (máximo 3 linhas)**
            shown_movements = 0
            max_movements = 3
            
            for rti, asset_movements in list(movements_by_asset.items())[:max_movements]:
                total_qtde = sum(m['qtde'] for m in asset_movements)
                
                # Determina direção do movimento
                if self.is_cd:
                    entrada_count = sum(1 for m in asset_movements 
                                     if m['destino'] == self.location_name)
                    if entrada_count > len(asset_movements) / 2:
                        color = "#28a745"
                        icon = "📥"
                        signal = "+"
                    else:
                        color = "#dc3545"
                        icon = "📤"
                        signal = "-"
                else:
                    remessa_count = sum(1 for m in asset_movements if m['tipo'] == 'Remessa')
                    if remessa_count > len(asset_movements) / 2:
                        color = "#28a745"
                        icon = "📥"
                        signal = "+"
                    else:
                        color = "#dc3545"
                        icon = "📤"
                        signal = "-"
                
                mov_label = QLabel(f"{icon} {signal}{total_qtde:,} {rti}".replace(",", "."))
                mov_label.setFont(QFont("Arial", 8, QFont.Bold))  # **CORREÇÃO: Fonte menor**
                mov_label.setStyleSheet(f"color: {color}; padding: 1px;")
                movements_layout.addWidget(mov_label)
                shown_movements += 1
            
            # Se há mais movimentos, mostra indicador
            if len(movements_by_asset) > max_movements:
                more_mov_label = QLabel(f"... e mais {len(movements_by_asset) - max_movements} ativos")
                more_mov_label.setFont(QFont("Arial", 8))
                more_mov_label.setStyleSheet("color: #666; font-style: italic; padding: 1px;")
                movements_layout.addWidget(more_mov_label)
            
            layout.addWidget(movements_frame)
        else:
            # **CORREÇÃO: Frame de "sem movimentos" mais compacto**
            no_mov_frame = QFrame()
            no_mov_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 4px; margin: 2px;")
            no_mov_frame.setMaximumHeight(40)  # **CORREÇÃO: Altura mínima**
            no_mov_layout = QVBoxLayout(no_mov_frame)
            no_mov_layout.setContentsMargins(8, 5, 8, 5)
            
            no_mov_label = QLabel("💤 Sem movimentos")
            no_mov_label.setFont(QFont("Arial", 8))
            no_mov_label.setStyleSheet("color: #6c757d; font-style: italic;")
            no_mov_layout.addWidget(no_mov_label)
            layout.addWidget(no_mov_frame)
        
        # **CORREÇÃO: Seção de estoque final com altura controlada**
        final_frame = QFrame()
        final_frame.setStyleSheet("background-color: #d1ecf1; border-radius: 4px; margin: 2px;")
        final_frame.setMaximumHeight(80)  # **CORREÇÃO: Altura máxima**
        final_layout = QVBoxLayout(final_frame)
        final_layout.setContentsMargins(8, 5, 8, 5)
        final_layout.setSpacing(2)
        
        final_title = QLabel("📊 Saldo Final:")
        final_title.setFont(QFont("Arial", 9, QFont.Bold))
        final_title.setStyleSheet("color: #0c5460;")
        final_layout.addWidget(final_title)
        
        final_stock = day_data['stock']
        
        # **CORREÇÃO: Limita itens mostrados no saldo final**
        if final_stock:
            shown_final = 0
            max_final = 2  # Máximo 2 itens
            
            for asset, quantity in list(final_stock.items())[:max_final]:
                normalized_filter = normalize_asset_name(self.asset_filter) if self.asset_filter != "Todos" else "Todos"
                
                if self.asset_filter == "Todos" or normalized_filter == asset:
                    previous_qty = previous_stock.get(asset, 0) if previous_stock else 0
                    
                    if quantity != previous_qty:
                        if quantity > previous_qty:
                            change_icon = "📈"
                            change_color = "#28a745"
                        else:
                            change_icon = "📉"
                            change_color = "#dc3545"
                        stock_text = f"• {asset}: {quantity:,} {change_icon}".replace(",", ".")
                        stock_label = QLabel(stock_text)
                        stock_label.setFont(QFont("Arial", 8, QFont.Bold))  # **CORREÇÃO: Fonte menor**
                        stock_label.setStyleSheet(f"padding: 1px; color: {change_color};")
                    else:
                        stock_label = QLabel(f"• {asset}: {quantity:,}".replace(",", "."))
                        stock_label.setFont(QFont("Arial", 8))
                        stock_label.setStyleSheet("padding: 1px;")
                    
                    final_layout.addWidget(stock_label)
                    shown_final += 1
            
            # Se há mais itens, mostra indicador
            if len(final_stock) > max_final:
                more_final_label = QLabel(f"... e mais {len(final_stock) - max_final} itens")
                more_final_label.setFont(QFont("Arial", 8))
                more_final_label.setStyleSheet("color: #666; font-style: italic; padding: 1px;")
                final_layout.addWidget(more_final_label)
        else:
            zero_label = QLabel("• Saldo: 0")
            zero_label.setFont(QFont("Arial", 8))
            zero_label.setStyleSheet("padding: 1px; color: #666;")
            final_layout.addWidget(zero_label)
        
        layout.addWidget(final_frame)
        
        # **CORREÇÃO: Remove stretch para manter altura compacta**
        # layout.addStretch()  # REMOVIDO
        
        self.flow_layout.addWidget(card)

    def add_arrow(self):
        """Adiciona seta entre os cards"""
        arrow_widget = QWidget()
        arrow_widget.setFixedWidth(50)  # **CORREÇÃO: Largura menor**
        arrow_widget.setMinimumHeight(100)
        arrow_widget.setMaximumHeight(300)  # **CORREÇÃO: Altura máxima**
        
        def paint_arrow(event):
            painter = QPainter(arrow_widget)
            painter.setRenderHint(QPainter.Antialiasing)
            
            pen = QPen(QColor("#007bff"))
            pen.setWidth(3)
            painter.setPen(pen)
            
            start_x = 5
            end_x = 45
            y = arrow_widget.height() // 2
            
            painter.drawLine(start_x, y, end_x - 12, y)
            painter.drawLine(end_x - 12, y, end_x - 20, y - 8)
            painter.drawLine(end_x - 12, y, end_x - 20, y + 8)
        
        arrow_widget.paintEvent = paint_arrow
        self.flow_layout.addWidget(arrow_widget)

    def get_initial_inventory(self):
        """Obtém dados do inventário inicial (só para lojas)"""
        if self.is_cd:
            return {}
        
        inventory_match = self.db.find_best_inventory_match(self.location_name)
        if not inventory_match:
            return {}
        
        query = "SELECT ativo, quantidade FROM inventario_inicial WHERE loja_nome_simples = ?"
        result = self.db._execute_query(query, (inventory_match,))
        return {row['ativo']: row['quantidade'] for row in result}

    def export_flow(self):
        """Exporta dados do fluxo para CSV melhorado"""
        try:
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            import pandas as pd
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Salvar Fluxo", f"fluxo_{self.location_name.replace(' ', '_')}.csv", "CSV (*.csv)"
            )
            
            if file_path:
                export_data = []
                
                if not self.is_cd:
                    initial_inventory = self.get_initial_inventory()
                    for asset, qty in initial_inventory.items():
                        export_data.append({
                            'Data': '08/06/2025',
                            'Tipo': 'Inventário Inicial',
                            'Ativo': asset,
                            'Saldo_Inicial': qty,
                            'Movimento_Tipo': '',
                            'Movimento_Quantidade': '',
                            'Saldo_Final': qty
                        })
                    previous_stock = initial_inventory.copy()
                else:
                    previous_stock = {}
                
                for day_data in self.daily_data:
                    date = day_data['date']
                    movements = day_data.get('movements', [])
                    final_stock = day_data['stock']
                    
                    if not movements:
                        for asset in set(list(previous_stock.keys()) + list(final_stock.keys())):
                            export_data.append({
                                'Data': date,
                                'Tipo': 'Sem Movimento',
                                'Ativo': asset,
                                'Saldo_Inicial': previous_stock.get(asset, 0),
                                'Movimento_Tipo': '',
                                'Movimento_Quantidade': '',
                                'Saldo_Final': final_stock.get(asset, 0)
                            })
                    else:
                        movements_by_asset = {}
                        for mov in movements:
                            if hasattr(mov, 'keys'):
                                rti = mov['rti'] if mov['rti'] else 'N/A'
                            else:
                                rti = mov.get('rti', 'N/A') or 'N/A'
                            
                            rti_normalized = str(rti).strip().upper().replace(' ', '')
                            
                            if rti_normalized not in movements_by_asset:
                                movements_by_asset[rti_normalized] = []
                            movements_by_asset[rti_normalized].append(mov)
                        
                        for asset in set(list(previous_stock.keys()) + list(final_stock.keys()) + list(movements_by_asset.keys())):
                            mov_details = []
                            mov_types = []
                            
                            if asset in movements_by_asset:
                                for mov in movements_by_asset[asset]:
                                    if hasattr(mov, 'keys'):
                                        mov_type = mov['tipo_movimento']
                                        mov_qty = mov['quantidade']
                                        origem = mov['local_origem']
                                        destino = mov['local_destino']
                                    else:
                                        mov_type = mov.get('tipo_movimento', '')
                                        mov_qty = mov.get('quantidade', 0)
                                        origem = mov.get('local_origem', '')
                                        destino = mov.get('local_destino', '')
                                    
                                    mov_types.append(mov_type)
                                    
                                    if self.is_cd:
                                        if destino == self.location_name:
                                            mov_details.append(f"+{mov_qty}")
                                        elif origem == self.location_name:
                                            mov_details.append(f"-{mov_qty}")
                                        else:
                                            mov_details.append(f"={mov_qty}")
                                    else:
                                        if mov_type == 'Remessa':
                                            mov_details.append(f"+{mov_qty}")
                                        else:
                                            mov_details.append(f"-{mov_qty}")
                            
                            export_data.append({
                                'Data': date,
                                'Tipo': 'Movimento',
                                'Ativo': asset,
                                'Saldo_Inicial': previous_stock.get(asset, 0),
                                'Movimento_Tipo': '; '.join(mov_types),
                                'Movimento_Quantidade': '; '.join(mov_details),
                                'Saldo_Final': final_stock.get(asset, 0)
                            })
                    
                    previous_stock = final_stock.copy()
                
                df = pd.DataFrame(export_data)
                df.to_csv(file_path, index=False, sep=';', encoding='utf-8-sig')
                QMessageBox.information(self, "✅ Sucesso", f"Fluxo exportado para:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "❌ Erro", f"Erro ao exportar: {e}")

    def resizeEvent(self, event):
        """Garante que o scroll funcione corretamente ao redimensionar"""
        super().resizeEvent(event)
        if hasattr(self, 'flow_widget'):
            self.flow_widget.updateGeometry()