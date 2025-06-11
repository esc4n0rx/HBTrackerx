# flow_visual_dialog.py - Interface corrigida e melhorada
import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
                            QWidget, QFrame, QGridLayout, QPushButton, QComboBox)
from PyQt5.QtGui import QFont, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect
from datetime import datetime, timedelta
import json

class FlowVisualDialog(QDialog):
    def __init__(self, location_name, db_instance, parent=None):
        super().__init__(parent)
        self.location_name = location_name
        self.db = db_instance
        self.setWindowTitle(f"Fluxo Visual - {location_name}")
        
        # **CORREÇÃO: Tamanho da janela ajustado**
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(1000, 600)
        
        # Obtém dados de evolução diária
        self.daily_data = self.db.get_daily_stock_evolution(location_name)
        self.asset_filter = "Todos"
        
        self.init_ui()
        self.update_flow_display()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Cabeçalho com filtros
        header_layout = QHBoxLayout()
        
        title_label = QLabel(f"Evolução do Estoque - {self.location_name}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Filtro por ativo
        header_layout.addWidget(QLabel("Filtrar por ativo:"))
        self.asset_combo = QComboBox()
        self.asset_combo.addItem("Todos")
        
        # **CORREÇÃO: Detecta ativos automaticamente com tratamento correto**
        if self.daily_data:
            assets_found = set()
            # Pega do inventário inicial
            initial_inventory = self.get_initial_inventory()
            assets_found.update(initial_inventory.keys())
            # Pega dos movimentos
            for day_data in self.daily_data:
                movements = day_data.get('movements', [])
                if isinstance(movements, list):
                    for mov in movements:
                        # **CORREÇÃO: Tratamento correto para sqlite3.Row**
                        if hasattr(mov, 'keys'):  # É um Row object
                            rti = mov['rti'] if mov['rti'] else None
                        else:  # É um dicionário
                            rti = mov.get('rti')
                        
                        if rti:
                            assets_found.add(rti)
            
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
        
        # **CRÍTICO: Widget interno do scroll area**
        self.flow_widget = QWidget()
        self.flow_layout = QHBoxLayout(self.flow_widget)
        self.flow_layout.setSpacing(15)  # Reduzido espaçamento
        self.flow_layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll_area.setWidget(self.flow_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("💾 Exportar Fluxo")
        export_btn.clicked.connect(self.export_flow)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("❌ Fechar")
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
            no_data_label = QLabel("❌ Nenhum dado de inventário encontrado.\n\n📦 Faça o upload do inventário inicial nas configurações.")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("""
                QLabel {
                    color: #666; 
                    font-size: 14px; 
                    padding: 50px;
                    background-color: #f8f9fa;
                    border: 2px dashed #dee2e6;
                    border-radius: 10px;
                }
            """)
            self.flow_layout.addWidget(no_data_label)
            return
        
        # Adiciona inventário inicial
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
        """Adiciona card do inventário inicial com layout melhorado"""
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
        # **CORREÇÃO: Tamanho dos cards reduzido**
        card.setFixedWidth(220)
        card.setMinimumHeight(200)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Título
        title = QLabel("📦 INVENTÁRIO INICIAL")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Data
        date_label = QLabel("📅 08/06/2025")
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("color: #666; font-size: 9px;")
        layout.addWidget(date_label)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #5cb85c;")
        layout.addWidget(separator)
        
        # **SEÇÃO: Estoque inicial**
        stock_title = QLabel("📊 Estoque Base:")
        stock_title.setStyleSheet("font-weight: bold; font-size: 9px; color: #2d5a2d;")
        layout.addWidget(stock_title)
        
        inventory_data = self.get_initial_inventory()
        if inventory_data:
            for asset, quantity in inventory_data.items():
                if self.asset_filter == "Todos" or self.asset_filter == asset:
                    asset_label = QLabel(f"• {asset}: {quantity:,}".replace(",", "."))
                    asset_label.setStyleSheet("padding: 2px; font-size: 10px; font-weight: bold;")
                    layout.addWidget(asset_label)
        else:
            no_stock_label = QLabel("⚠️ Sem dados")
            no_stock_label.setStyleSheet("color: #999; font-size: 9px; font-style: italic;")
            layout.addWidget(no_stock_label)
        
        layout.addStretch()
        self.flow_layout.addWidget(card)

    def add_day_card(self, day_data, day_index):
        """Adiciona card de um dia específico com layout melhorado e normalização"""
        
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
        
        # **DEBUG: Verificar dados**
        print(f"\n=== DEBUG: Criando card para dia {day_index} ===")
        print(f"Data: {day_data['date']}")
        print(f"Movimentos: {len(day_data.get('movements', []))}")
        print(f"Estoque final recebido: {day_data['stock']}")
        
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
        card.setFixedWidth(240)
        card.setMinimumHeight(280)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)
        
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
        title_font.setPointSize(9)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # **CORREÇÃO: Saldo inicial do dia (do dia anterior ou inventário)**
        if day_index == 0:
            # Primeiro dia usa inventário inicial
            previous_stock = self.get_initial_inventory()
            print(f"DEBUG: Saldo inicial (inventário): {previous_stock}")
        else:
            # Dias seguintes usam saldo final do dia anterior
            previous_day_data = self.daily_data[day_index - 1]
            previous_stock = previous_day_data['stock']
            print(f"DEBUG: Saldo inicial (dia anterior): {previous_stock}")
        
        # **SEÇÃO: Saldo inicial do dia**
        initial_frame = QFrame()
        initial_frame.setStyleSheet("background-color: #e3f2fd; border-radius: 4px; margin: 2px;")
        initial_layout = QVBoxLayout(initial_frame)
        initial_layout.setContentsMargins(5, 3, 5, 3)
        
        initial_title = QLabel("📊 Saldo Inicial:")
        initial_title.setStyleSheet("font-weight: bold; font-size: 8px; color: #1565c0;")
        initial_layout.addWidget(initial_title)
        
        for asset, quantity in previous_stock.items():
            if self.asset_filter == "Todos" or self.asset_filter == asset:
                initial_label = QLabel(f"• {asset}: {quantity:,}".replace(",", "."))
                initial_label.setStyleSheet("font-size: 8px; padding: 1px;")
                initial_layout.addWidget(initial_label)
        
        layout.addWidget(initial_frame)
        
        # **SEÇÃO: Movimentos do dia**
        movements = day_data.get('movements', [])
        if movements:
            movements_frame = QFrame()
            movements_frame.setStyleSheet("background-color: #fff3cd; border-radius: 4px; margin: 2px;")
            movements_layout = QVBoxLayout(movements_frame)
            movements_layout.setContentsMargins(5, 3, 5, 3)
            
            movements_title = QLabel("🔄 Movimentos:")
            movements_title.setStyleSheet("font-weight: bold; font-size: 8px; color: #856404;")
            movements_layout.addWidget(movements_title)
            
            for mov in movements:
                # **CORREÇÃO: Tratamento correto para sqlite3.Row com normalização**
                if hasattr(mov, 'keys'):  # É um Row object
                    raw_rti = mov['rti'] if mov['rti'] else 'N/A'
                    rti = normalize_asset_name(raw_rti)  # **NORMALIZAÇÃO**
                    tipo = mov['tipo_movimento']
                    qtde = mov['quantidade']
                else:  # É um dicionário
                    raw_rti = mov.get('rti', 'N/A') or 'N/A'
                    rti = normalize_asset_name(raw_rti)  # **NORMALIZAÇÃO**
                    tipo = mov.get('tipo_movimento', '')
                    qtde = mov.get('quantidade', 0)
                
                print(f"DEBUG: Movimento - {tipo} {qtde} '{raw_rti}' -> '{rti}'")
                
                if self.asset_filter == "Todos" or normalize_asset_name(self.asset_filter) == rti:
                    if tipo == 'Remessa':
                        color = "#28a745"
                        icon = "📥"
                        signal = "+"
                    else:
                        color = "#dc3545"
                        icon = "📤"
                        signal = "-"
                    
                    mov_label = QLabel(f"{icon} {signal}{qtde:,} {rti}".replace(",", "."))
                    mov_label.setStyleSheet(f"color: {color}; font-size: 8px; padding: 1px; font-weight: bold;")
                    movements_layout.addWidget(mov_label)
            
            layout.addWidget(movements_frame)
        else:
            # Dia sem movimentos
            no_mov_frame = QFrame()
            no_mov_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 4px; margin: 2px;")
            no_mov_layout = QVBoxLayout(no_mov_frame)
            no_mov_layout.setContentsMargins(5, 3, 5, 3)
            
            no_mov_label = QLabel("💤 Sem movimentos")
            no_mov_label.setStyleSheet("color: #6c757d; font-size: 8px; font-style: italic;")
            no_mov_layout.addWidget(no_mov_label)
            layout.addWidget(no_mov_frame)
        
        # **SEÇÃO: Estoque final do dia**
        final_frame = QFrame()
        final_frame.setStyleSheet("background-color: #d1ecf1; border-radius: 4px; margin: 2px;")
        final_layout = QVBoxLayout(final_frame)
        final_layout.setContentsMargins(5, 3, 5, 3)
        
        final_title = QLabel("📊 Saldo Final:")
        final_title.setStyleSheet("font-weight: bold; font-size: 8px; color: #0c5460;")
        final_layout.addWidget(final_title)
        
        final_stock = day_data['stock']
        print(f"DEBUG: Saldo final a ser exibido: {final_stock}")
        
        for asset, quantity in final_stock.items():
            normalized_filter = normalize_asset_name(self.asset_filter) if self.asset_filter != "Todos" else "Todos"
            
            if self.asset_filter == "Todos" or normalized_filter == asset:
                # **MELHORIA: Indica se houve mudança**
                previous_qty = previous_stock.get(asset, 0)
                print(f"DEBUG: {asset} - Anterior: {previous_qty}, Final: {quantity}")
                
                if quantity != previous_qty:
                    if quantity > previous_qty:
                        change_icon = "📈"
                        change_color = "#28a745"
                    else:
                        change_icon = "📉"
                        change_color = "#dc3545"
                    stock_text = f"• {asset}: {quantity:,} {change_icon}".replace(",", ".")
                    stock_label = QLabel(stock_text)
                    stock_label.setStyleSheet(f"font-size: 9px; padding: 1px; font-weight: bold; color: {change_color};")
                else:
                    stock_label = QLabel(f"• {asset}: {quantity:,}".replace(",", "."))
                    stock_label.setStyleSheet("font-size: 8px; padding: 1px;")
                
                final_layout.addWidget(stock_label)
        
        layout.addWidget(final_frame)
        layout.addStretch()
        
        self.flow_layout.addWidget(card)

    def add_arrow(self):
        """Adiciona seta entre os cards com tamanho reduzido"""
        arrow_widget = QWidget()
        # **CORREÇÃO: Seta mais estreita**
        arrow_widget.setFixedWidth(40)
        arrow_widget.setMinimumHeight(80)
        
        def paint_arrow(event):
            painter = QPainter(arrow_widget)
            painter.setRenderHint(QPainter.Antialiasing)
            
            pen = QPen(QColor("#007bff"))
            pen.setWidth(2)
            painter.setPen(pen)
            
            # Desenha seta
            start_x = 5
            end_x = 35
            y = arrow_widget.height() // 2
            
            # Linha principal
            painter.drawLine(start_x, y, end_x - 8, y)
            
            # Ponta da seta
            painter.drawLine(end_x - 8, y, end_x - 15, y - 6)
            painter.drawLine(end_x - 8, y, end_x - 15, y + 6)
        
        arrow_widget.paintEvent = paint_arrow
        self.flow_layout.addWidget(arrow_widget)

    def get_initial_inventory(self):
        """Obtém dados do inventário inicial usando matching"""
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
                
                # **MELHORIA: Export detalhado**
                # Inventário inicial
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
                
                # Dados diários
                previous_stock = initial_inventory.copy()
                
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
                            # **CORREÇÃO: Tratamento correto para sqlite3.Row**
                            if hasattr(mov, 'keys'):  # É um Row object
                                rti = mov['rti'] if mov['rti'] else 'N/A'
                            else:  # É um dicionário
                                rti = mov.get('rti', 'N/A') or 'N/A'
                            
                            if rti not in movements_by_asset:
                                movements_by_asset[rti] = []
                            movements_by_asset[rti].append(mov)
                        
                        # Exporta linha por ativo
                        for asset in set(list(previous_stock.keys()) + list(final_stock.keys()) + list(movements_by_asset.keys())):
                            mov_details = []
                            mov_types = []
                            
                            if asset in movements_by_asset:
                                for mov in movements_by_asset[asset]:
                                    # **CORREÇÃO: Tratamento correto para sqlite3.Row**
                                    if hasattr(mov, 'keys'):  # É um Row object
                                        mov_type = mov['tipo_movimento']
                                        mov_qty = mov['quantidade']
                                    else:  # É um dicionário
                                        mov_type = mov.get('tipo_movimento', '')
                                        mov_qty = mov.get('quantidade', 0)
                                    
                                    mov_types.append(mov_type)
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
            # Força atualização do widget interno
            self.flow_widget.updateGeometry()