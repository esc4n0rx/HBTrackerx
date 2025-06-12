# flow_dialog.py - VERSÃO CORRIGIDA COM SUPORTE PARA CDs
import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
                            QWidget, QFrame, QGridLayout, QPushButton, QComboBox,
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtGui import QFont, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect
from datetime import datetime, timedelta
import json

class FlowDialog(QDialog):
    """Diálogo para exibir fluxo clássico de movimentos"""
    def __init__(self, location_name, flow_data, parent=None):
        super().__init__(parent)
        self.location_name = location_name
        self.flow_data = flow_data
        self.setWindowTitle(f"Fluxo de Movimentos - {location_name}")
        self.setGeometry(100, 100, 1000, 600)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel(f"📊 Fluxo de Movimentos - {self.location_name}")
        title_font = QFont()
        title_font.setPointSize(16)  # CORREÇÃO: Fonte maior
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            '📅 Data', '🔄 Movimento', '📦 Ativo (RTI)', 
            '📤 Origem', '📥 Destino', '🔢 Quantidade'
        ])
        
        # CORREÇÃO: Configura fontes maiores para a tabela
        table_font = QFont()
        table_font.setPointSize(12)
        self.table.setFont(table_font)
        
        # Configuração da tabela
        header = self.table.horizontalHeader()
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header.setFont(header_font)
        
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Movimento
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # RTI
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Origem
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # Destino
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Quantidade
        
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        # Botões
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("❌ Fechar")
        close_btn.setFont(QFont("Arial", 12))  # CORREÇÃO: Fonte maior
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
                'Remessa': '📤',
                'Regresso': '📥', 
                'Entrega': '🚚',
                'Devolução de Entrega': '↩️',
                'Transferencia': '🔄',
                'Retorno': '🔙'
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

class FlowVisualDialog(QDialog):
    def __init__(self, location_name, db_instance, parent=None):
        super().__init__(parent)
        self.location_name = location_name
        self.db = db_instance
        self.setWindowTitle(f"Fluxo Visual - {location_name}")
        
        # CORREÇÃO: Tamanho da janela aumentado para melhor visualização
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1200, 700)
        
        # **CORREÇÃO PRINCIPAL: Detecta se é CD ou Loja e ajusta lógica**
        self.is_cd = not location_name.startswith('LOJA')
        
        if self.is_cd:
            # Para CDs: usa evolução baseada apenas em movimentos
            self.daily_data = self.get_cd_daily_evolution(location_name)
        else:
            # Para Lojas: usa evolução com inventário inicial
            self.daily_data = self.db.get_daily_stock_evolution(location_name)
        
        self.asset_filter = "Todos"
        
        self.init_ui()
        self.update_flow_display()

    def get_cd_daily_evolution(self, cd_name):
        """NOVA FUNÇÃO: Calcula evolução diária para CDs (sem inventário inicial)"""
        print(f"=== EVOLUÇÃO CD PARA {cd_name} ===")
        
        # Busca movimentos ordenados por data
        movements_query = """
        SELECT data_movimento, tipo_movimento, rti, quantidade, local_origem, local_destino
        FROM movimentos 
        WHERE (local_origem = ? OR local_destino = ?)
        ORDER BY data_movimento ASC, id ASC
        """
        movements = self.db._execute_query(movements_query, (cd_name, cd_name))

        # Função auxiliar para normalizar ativos
        def normalize_asset_name(asset_name):
            if not asset_name:
                return 'N/A'
            normalized = str(asset_name).strip().upper()
            normalized = normalized.replace(' ', '')
            return normalized

        # Agrupa movimentos por data
        from collections import defaultdict
        movements_by_date = defaultdict(list)
        for mov in movements:
            movements_by_date[mov['data_movimento']].append(mov)

        print(f"Datas com movimentos: {sorted(movements_by_date.keys())}")

        # Calcula evolução dia a dia CUMULATIVA (começando do zero)
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
                
                # **LÓGICA PARA CDs: Diferentes tipos de movimento**
                if destino == cd_name:
                    # Entrada no CD
                    if tipo in ('Regresso', 'Entrega', 'Transferencia', 'Retorno'):
                        current_stock[rti] += qtde
                        print(f"  ✅ Entrada CD: {rti} {old_qty} + {qtde} = {current_stock[rti]}")
                    else:
                        print(f"  ⚠️ Movimento de entrada não processado: {tipo}")
                        
                elif origem == cd_name:
                    # Saída do CD
                    if tipo in ('Remessa', 'Transferencia', 'Devolução de Entrega'):
                        current_stock[rti] -= qtde
                        print(f"  ❌ Saída CD: {rti} {old_qty} - {qtde} = {current_stock[rti]}")
                    else:
                        print(f"  ⚠️ Movimento de saída não processado: {tipo}")
                else:
                    print(f"  ⚠️ Movimento ignorado: {tipo}")

            print(f"Estoque CD final do dia {date}: {dict(current_stock)}")

            # Salva estado do dia
            daily_evolution.append({
                'date': date,
                'stock': current_stock.copy(),
                'movements': day_movements.copy()
            })

        print(f"\nEvolução CD final calculada:")
        for i, day in enumerate(daily_evolution):
            print(f"Dia CD {i+1} ({day['date']}): {day['stock']}")

        return daily_evolution

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # CORREÇÃO: Fonts maiores globalmente
        base_font = QFont()
        base_font.setPointSize(12)
        self.setFont(base_font)
        
        # Cabeçalho com filtros
        header_layout = QHBoxLayout()
        
        title_label = QLabel(f"Evolução do Estoque - {self.location_name}")
        title_font = QFont()
        title_font.setPointSize(18)  # CORREÇÃO: Fonte maior
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Filtro por ativo
        filter_label = QLabel("Filtrar por ativo:")
        filter_label.setFont(QFont("Arial", 12))
        header_layout.addWidget(filter_label)
        
        self.asset_combo = QComboBox()
        self.asset_combo.addItem("Todos")
        self.asset_combo.setFont(QFont("Arial", 12))
        
        # **CORREÇÃO: Detecta ativos para CDs e Lojas**
        if self.daily_data:
            assets_found = set()
            
            if not self.is_cd:
                # Para lojas: pega do inventário inicial
                initial_inventory = self.get_initial_inventory()
                assets_found.update(initial_inventory.keys())
            
            # Para CDs e Lojas: pega dos movimentos
            for day_data in self.daily_data:
                movements = day_data.get('movements', [])
                if isinstance(movements, list):
                    for mov in movements:
                        if hasattr(mov, 'keys'):  # É um Row object
                            rti = mov['rti'] if mov['rti'] else None
                        else:  # É um dicionário
                            rti = mov.get('rti')
                        
                        if rti:
                            # Normaliza ativo
                            normalized_rti = str(rti).strip().upper().replace(' ', '')
                            assets_found.add(normalized_rti)
            
            for asset in sorted(assets_found):
                self.asset_combo.addItem(asset)
        
        self.asset_combo.currentTextChanged.connect(self.on_filter_changed)
        header_layout.addWidget(self.asset_combo)
        
        main_layout.addLayout(header_layout)
        
        # **CORREÇÃO: Área de scroll melhorada**
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget interno do scroll area
        self.flow_widget = QWidget()
        self.flow_layout = QHBoxLayout(self.flow_widget)
        self.flow_layout.setSpacing(20)  # CORREÇÃO: Espaçamento maior
        self.flow_layout.setContentsMargins(15, 15, 15, 15)
        
        self.scroll_area.setWidget(self.flow_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("💾 Exportar Fluxo")
        export_btn.setFont(QFont("Arial", 12))
        export_btn.clicked.connect(self.export_flow)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("❌ Fechar")
        close_btn.setFont(QFont("Arial", 12))
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)

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
            no_data_label.setFont(QFont("Arial", 14))  # CORREÇÃO: Fonte maior
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
        
        # **CORREÇÃO: Para lojas, adiciona inventário inicial. Para CDs, não**
        if not self.is_cd:
            self.add_inventory_card()
            # Adiciona seta após inventário
            if self.daily_data:
                self.add_arrow()
        
        # Adiciona cards para cada dia
        for i, day_data in enumerate(self.daily_data):
            self.add_day_card(day_data, i)
            
            # Adiciona seta entre os cards (exceto no último)
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
        # CORREÇÃO: Cards maiores
        card.setFixedWidth(280)
        card.setMinimumHeight(250)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Título
        title = QLabel("📦 INVENTÁRIO INICIAL")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)  # CORREÇÃO: Fonte maior
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Data
        date_label = QLabel("📅 08/06/2025")
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setFont(QFont("Arial", 10))  # CORREÇÃO: Fonte maior
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
                    asset_label.setFont(QFont("Arial", 11, QFont.Bold))  # CORREÇÃO: Fonte maior
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
        """Adiciona card de um dia específico"""
        
        # Função auxiliar para normalizar ativos
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
        # CORREÇÃO: Cards maiores
        card.setFixedWidth(300)
        card.setMinimumHeight(350)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)
        
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
        title_font.setPointSize(11)  # CORREÇÃO: Fonte maior
        title.setFont(title_font)
        layout.addWidget(title)
        
        # **CORREÇÃO: Saldo inicial do dia**
        if not self.is_cd and day_index == 0:
            # Para lojas: primeiro dia usa inventário inicial
            previous_stock = self.get_initial_inventory()
        elif not self.is_cd and day_index > 0:
            # Para lojas: dias seguintes usam saldo final do dia anterior
            previous_day_data = self.daily_data[day_index - 1]
            previous_stock = previous_day_data['stock']
        else:
            # Para CDs: usa saldo do dia anterior ou zero no primeiro dia
            if day_index == 0:
                previous_stock = {}
            else:
                previous_day_data = self.daily_data[day_index - 1]
                previous_stock = previous_day_data['stock']
        
        # **SEÇÃO: Saldo inicial do dia**
        initial_frame = QFrame()
        initial_frame.setStyleSheet("background-color: #e3f2fd; border-radius: 4px; margin: 2px;")
        initial_layout = QVBoxLayout(initial_frame)
        initial_layout.setContentsMargins(8, 5, 8, 5)
        
        initial_title = QLabel("📊 Saldo Inicial:")
        initial_title.setFont(QFont("Arial", 9, QFont.Bold))  # CORREÇÃO: Fonte maior
        initial_title.setStyleSheet("color: #1565c0;")
        initial_layout.addWidget(initial_title)
        
        if previous_stock:
            for asset, quantity in previous_stock.items():
                if self.asset_filter == "Todos" or self.asset_filter == asset:
                    initial_label = QLabel(f"• {asset}: {quantity:,}".replace(",", "."))
                    initial_label.setFont(QFont("Arial", 9))  # CORREÇÃO: Fonte maior
                    initial_label.setStyleSheet("padding: 2px;")
                    initial_layout.addWidget(initial_label)
        else:
            zero_label = QLabel("• Saldo: 0 (início)")
            zero_label.setFont(QFont("Arial", 9))
            zero_label.setStyleSheet("padding: 2px; color: #666;")
            initial_layout.addWidget(zero_label)
        
        layout.addWidget(initial_frame)
        
        # **SEÇÃO: Movimentos do dia**
        movements = day_data.get('movements', [])
        if movements:
            movements_frame = QFrame()
            movements_frame.setStyleSheet("background-color: #fff3cd; border-radius: 4px; margin: 2px;")
            movements_layout = QVBoxLayout(movements_frame)
            movements_layout.setContentsMargins(8, 5, 8, 5)
            
            movements_title = QLabel("🔄 Movimentos:")
            movements_title.setFont(QFont("Arial", 9, QFont.Bold))  # CORREÇÃO: Fonte maior
            movements_title.setStyleSheet("color: #856404;")
            movements_layout.addWidget(movements_title)
            
            for mov in movements:
                if hasattr(mov, 'keys'):  # É um Row object
                    raw_rti = mov['rti'] if mov['rti'] else 'N/A'
                    rti = normalize_asset_name(raw_rti)
                    tipo = mov['tipo_movimento']
                    qtde = mov['quantidade']
                    origem = mov['local_origem']
                    destino = mov['local_destino']
                else:  # É um dicionário
                    raw_rti = mov.get('rti', 'N/A') or 'N/A'
                    rti = normalize_asset_name(raw_rti)
                    tipo = mov.get('tipo_movimento', '')
                    qtde = mov.get('quantidade', 0)
                    origem = mov.get('local_origem', '')
                    destino = mov.get('local_destino', '')
                
                if self.asset_filter == "Todos" or normalize_asset_name(self.asset_filter) == rti:
                    # **CORREÇÃO: Lógica diferente para CDs vs Lojas**
                    if self.is_cd:
                        # Para CDs: determina se é entrada ou saída
                        if destino == self.location_name:
                            color = "#28a745"
                            icon = "📥"
                            signal = "+"
                        elif origem == self.location_name:
                            color = "#dc3545"
                            icon = "📤"
                            signal = "-"
                        else:
                            color = "#6c757d"
                            icon = "🔄"
                            signal = "="
                    else:
                        # Para Lojas: lógica original
                        if tipo == 'Remessa':
                            color = "#28a745"
                            icon = "📥"
                            signal = "+"
                        else:
                            color = "#dc3545"
                            icon = "📤"
                            signal = "-"
                    
                    mov_label = QLabel(f"{icon} {signal}{qtde:,} {rti}".replace(",", "."))
                    mov_label.setFont(QFont("Arial", 9, QFont.Bold))  # CORREÇÃO: Fonte maior
                    mov_label.setStyleSheet(f"color: {color}; padding: 2px;")
                    movements_layout.addWidget(mov_label)
            
            layout.addWidget(movements_frame)
        else:
            # Dia sem movimentos
            no_mov_frame = QFrame()
            no_mov_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 4px; margin: 2px;")
            no_mov_layout = QVBoxLayout(no_mov_frame)
            no_mov_layout.setContentsMargins(8, 5, 8, 5)
            
            no_mov_label = QLabel("💤 Sem movimentos")
            no_mov_label.setFont(QFont("Arial", 9))  # CORREÇÃO: Fonte maior
            no_mov_label.setStyleSheet("color: #6c757d; font-style: italic;")
            no_mov_layout.addWidget(no_mov_label)
            layout.addWidget(no_mov_frame)
        
        # **SEÇÃO: Estoque final do dia**
        final_frame = QFrame()
        final_frame.setStyleSheet("background-color: #d1ecf1; border-radius: 4px; margin: 2px;")
        final_layout = QVBoxLayout(final_frame)
        final_layout.setContentsMargins(8, 5, 8, 5)
        
        final_title = QLabel("📊 Saldo Final:")
        final_title.setFont(QFont("Arial", 9, QFont.Bold))  # CORREÇÃO: Fonte maior
        final_title.setStyleSheet("color: #0c5460;")
        final_layout.addWidget(final_title)
        
        final_stock = day_data['stock']
        
        if final_stock:
            for asset, quantity in final_stock.items():
                normalized_filter = normalize_asset_name(self.asset_filter) if self.asset_filter != "Todos" else "Todos"
                
                if self.asset_filter == "Todos" or normalized_filter == asset:
                    # Indica se houve mudança
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
                        stock_label.setFont(QFont("Arial", 10, QFont.Bold))
                        stock_label.setStyleSheet(f"padding: 2px; color: {change_color};")
                    else:
                        stock_label = QLabel(f"• {asset}: {quantity:,}".replace(",", "."))
                        stock_label.setFont(QFont("Arial", 9))  # CORREÇÃO: Fonte maior
                        stock_label.setStyleSheet("padding: 2px;")
                    
                    final_layout.addWidget(stock_label)
        else:
            zero_label = QLabel("• Saldo: 0")
            zero_label.setFont(QFont("Arial", 9))
            zero_label.setStyleSheet("padding: 2px; color: #666;")
            final_layout.addWidget(zero_label)
        
        layout.addWidget(final_frame)
        layout.addStretch()
        
        self.flow_layout.addWidget(card)

    def add_arrow(self):
        """Adiciona seta entre os cards"""
        arrow_widget = QWidget()
        # CORREÇÃO: Seta maior
        arrow_widget.setFixedWidth(60)
        arrow_widget.setMinimumHeight(100)
        
        def paint_arrow(event):
            painter = QPainter(arrow_widget)
            painter.setRenderHint(QPainter.Antialiasing)
            
            pen = QPen(QColor("#007bff"))
            pen.setWidth(3)  # CORREÇÃO: Linha mais grossa
            painter.setPen(pen)
            
            # Desenha seta
            start_x = 10
            end_x = 50
            y = arrow_widget.height() // 2
            
            # Linha principal
            painter.drawLine(start_x, y, end_x - 12, y)
            
            # Ponta da seta
            painter.drawLine(end_x - 12, y, end_x - 20, y - 8)
            painter.drawLine(end_x - 12, y, end_x - 20, y + 8)
        
        arrow_widget.paintEvent = paint_arrow
        self.flow_layout.addWidget(arrow_widget)

    def get_initial_inventory(self):
        """Obtém dados do inventário inicial (só para lojas)"""
        if self.is_cd:
            return {}
        
        # Encontra match no inventário
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
                # Prepara dados para export
                export_data = []
                
                # **CORREÇÃO: Export diferente para CDs vs Lojas**
                if not self.is_cd:
                    # Para Lojas: inclui inventário inicial
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
                    # Para CDs: começa com zero
                    previous_stock = {}
                
                # Dados diários
                for day_data in self.daily_data:
                    date = day_data['date']
                    movements = day_data.get('movements', [])
                    final_stock = day_data['stock']
                    
                    if not movements:
                        # Dia sem movimentos
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
                        # Agrupa movimentos por ativo
                        movements_by_asset = {}
                        for mov in movements:
                            if hasattr(mov, 'keys'):  # É um Row object
                                rti = mov['rti'] if mov['rti'] else 'N/A'
                            else:  # É um dicionário
                                rti = mov.get('rti', 'N/A') or 'N/A'
                            
                            # Normaliza ativo
                            rti_normalized = str(rti).strip().upper().replace(' ', '')
                            
                            if rti_normalized not in movements_by_asset:
                                movements_by_asset[rti_normalized] = []
                            movements_by_asset[rti_normalized].append(mov)
                        
                        # Exporta linha por ativo
                        for asset in set(list(previous_stock.keys()) + list(final_stock.keys()) + list(movements_by_asset.keys())):
                            mov_details = []
                            mov_types = []
                            
                            if asset in movements_by_asset:
                                for mov in movements_by_asset[asset]:
                                    if hasattr(mov, 'keys'):  # É um Row object
                                        mov_type = mov['tipo_movimento']
                                        mov_qty = mov['quantidade']
                                        origem = mov['local_origem']
                                        destino = mov['local_destino']
                                    else:  # É um dicionário
                                        mov_type = mov.get('tipo_movimento', '')
                                        mov_qty = mov.get('quantidade', 0)
                                        origem = mov.get('local_origem', '')
                                        destino = mov.get('local_destino', '')
                                    
                                    mov_types.append(mov_type)
                                    
                                    # **CORREÇÃO: Lógica diferente para CDs**
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
                    
                    # Atualiza estoque anterior para próximo dia
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