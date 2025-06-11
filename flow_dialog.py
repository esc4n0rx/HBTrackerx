# flow_visual_dialog.py - Novo arquivo
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
        self.setGeometry(100, 100, 1400, 800)
        
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
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Filtro por ativo
        header_layout.addWidget(QLabel("Filtrar por ativo:"))
        self.asset_combo = QComboBox()
        self.asset_combo.addItem("Todos")
        self.asset_combo.addItem("HB623")
        self.asset_combo.addItem("HB618")
        self.asset_combo.currentTextChanged.connect(self.on_filter_changed)
        header_layout.addWidget(self.asset_combo)
        
        main_layout.addLayout(header_layout)
        
        # Área de scroll para o fluxo
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.flow_widget = QWidget()
        self.flow_layout = QHBoxLayout(self.flow_widget)
        self.flow_layout.setSpacing(20)
        self.flow_layout.setContentsMargins(20, 20, 20, 20)
        
        self.scroll_area.setWidget(self.flow_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("Exportar Fluxo")
        export_btn.clicked.connect(self.export_flow)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)

    def on_filter_changed(self, asset_name):
        self.asset_filter = asset_name
        self.update_flow_display()

    def update_flow_display(self):
        # Limpa layout atual
        for i in reversed(range(self.flow_layout.count())):
            self.flow_layout.itemAt(i).widget().setParent(None)
        
        if not self.daily_data:
            no_data_label = QLabel("Nenhum dado de inventário encontrado.\nFaça o upload do inventário inicial nas configurações.")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #666; font-size: 14px; padding: 50px;")
            self.flow_layout.addWidget(no_data_label)
            return
        
        # Adiciona inventário inicial
        self.add_inventory_card()
        
        # Adiciona cards para cada dia
        for i, day_data in enumerate(self.daily_data):
            self.add_day_card(day_data, i)
            
            # Adiciona seta entre os cards
            if i < len(self.daily_data) - 1:
                self.add_arrow()
        
        self.flow_layout.addStretch()

    def add_inventory_card(self):
        """Adiciona card do inventário inicial"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setLineWidth(2)
        card.setStyleSheet("""
            QFrame {
                background-color: #e8f5e8;
                border: 2px solid #5cb85c;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        card.setMinimumWidth(280)
        card.setMaximumWidth(280)
        
        layout = QVBoxLayout(card)
        
        # Título
        title = QLabel("📦 INVENTÁRIO INICIAL")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Data
        date_label = QLabel("08/06/2025")
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(date_label)
        
        # Estoque inicial
        inventory_data = self.get_initial_inventory()
        for asset, quantity in inventory_data.items():
            if self.asset_filter == "Todos" or self.asset_filter == asset:
                asset_label = QLabel(f"<b>{asset}:</b> {quantity:,}".replace(",", "."))
                asset_label.setStyleSheet("padding: 3px; font-size: 11px;")
                layout.addWidget(asset_label)
        
        layout.addStretch()
        self.flow_layout.addWidget(card)

    def add_day_card(self, day_data, day_index):
        """Adiciona card de um dia específico"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setLineWidth(2)
        card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #007bff;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        card.setMinimumWidth(300)
        card.setMaximumWidth(300)
        
        layout = QVBoxLayout(card)
        
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
        title_font.setPointSize(11)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Movimentos do dia
        movements = day_data.get('movements', [])
        if movements:
            movements_frame = QFrame()
            movements_frame.setStyleSheet("background-color: #fff3cd; border-radius: 5px; margin: 5px;")
            movements_layout = QVBoxLayout(movements_frame)
            
            movements_title = QLabel("🔄 Movimentos:")
            movements_title.setStyleSheet("font-weight: bold; font-size: 10px; color: #856404;")
            movements_layout.addWidget(movements_title)
            
            for mov in movements:
                rti = mov['rti'] if mov['rti'] else 'N/A'
                if self.asset_filter == "Todos" or self.asset_filter == rti:
                    tipo = mov['tipo_movimento']
                    qtde = mov['quantidade']
                    
                    if tipo == 'Remessa':
                        mov_text = f"📥 +{qtde:,} {rti}".replace(",", ".")
                        color = "#28a745"
                    else:
                        mov_text = f"📤 -{qtde:,} {rti}".replace(",", ".")
                        color = "#dc3545"
                    
                    mov_label = QLabel(mov_text)
                    mov_label.setStyleSheet(f"color: {color}; font-size: 10px; padding: 1px;")
                    movements_layout.addWidget(mov_label)
            
            layout.addWidget(movements_frame)
        
        # Estoque final do dia
        stock_frame = QFrame()
        stock_frame.setStyleSheet("background-color: #d1ecf1; border-radius: 5px; margin: 5px;")
        stock_layout = QVBoxLayout(stock_frame)
        
        stock_title = QLabel("📊 Estoque Final:")
        stock_title.setStyleSheet("font-weight: bold; font-size: 10px; color: #0c5460;")
        stock_layout.addWidget(stock_title)
        
        for asset, quantity in day_data['stock'].items():
            if self.asset_filter == "Todos" or self.asset_filter == asset:
                stock_label = QLabel(f"<b>{asset}:</b> {quantity:,}".replace(",", "."))
                stock_label.setStyleSheet("font-size: 10px; padding: 1px;")
                stock_layout.addWidget(stock_label)
        
        layout.addWidget(stock_frame)
        layout.addStretch()
        
        self.flow_layout.addWidget(card)

    def add_arrow(self):
        """Adiciona seta entre os cards"""
        arrow_widget = QWidget()
        arrow_widget.setMinimumWidth(60)
        arrow_widget.setMaximumWidth(60)
        arrow_widget.setMinimumHeight(100)
        
        def paint_arrow(event):
            painter = QPainter(arrow_widget)
            painter.setRenderHint(QPainter.Antialiasing)
            
            pen = QPen(QColor("#007bff"))
            pen.setWidth(3)
            painter.setPen(pen)
            
            # Desenha seta
            start_x = 10
            end_x = 50
            y = arrow_widget.height() // 2
            
            # Linha principal
            painter.drawLine(start_x, y, end_x - 10, y)
            
            # Ponta da seta
            painter.drawLine(end_x - 10, y, end_x - 20, y - 10)
            painter.drawLine(end_x - 10, y, end_x - 20, y + 10)
        
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
        """Exporta dados do fluxo para CSV"""
        try:
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            import pandas as pd
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Salvar Fluxo", f"fluxo_{self.location_name}.csv", "CSV (*.csv)"
            )
            
            if file_path:
                # Prepara dados para export
                export_data = []
                
                # Inventário inicial
                initial_inventory = self.get_initial_inventory()
                for asset, qty in initial_inventory.items():
                    export_data.append({
                        'Data': '08/06/2025',
                        'Tipo': 'Inventário Inicial',
                        'Ativo': asset,
                        'Movimento': '',
                        'Quantidade_Movimento': '',
                        'Estoque_Final': qty
                    })
                
                # Dados diários
                for day_data in self.daily_data:
                    date = day_data['date']
                    movements = day_data.get('movements', [])
                    stock = day_data['stock']
                    
                    if not movements:
                        # Dia sem movimentos
                        for asset, qty in stock.items():
                            export_data.append({
                                'Data': date,
                                'Tipo': 'Sem Movimento',
                                'Ativo': asset,
                                'Movimento': '',
                                'Quantidade_Movimento': '',
                                'Estoque_Final': qty
                            })
                    else:
                        # Dia com movimentos
                        for mov in movements:
                            rti = mov['rti'] if mov['rti'] else 'N/A'
                            export_data.append({
                                'Data': date,
                                'Tipo': 'Movimento',
                                'Ativo': rti,
                                'Movimento': mov['tipo_movimento'],
                                'Quantidade_Movimento': mov['quantidade'],
                                'Estoque_Final': stock.get(rti, 0)
                            })
                
                df = pd.DataFrame(export_data)
                df.to_csv(file_path, index=False, sep=';')
                QMessageBox.information(self, "Sucesso", f"Fluxo exportado para:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar: {e}")