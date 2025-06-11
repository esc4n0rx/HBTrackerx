# flow_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QScrollArea, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from collections import defaultdict

class FlowDialog(QDialog):
    def __init__(self, location_name, flow_data, parent=None):
        super().__init__(parent)
        self.location_name = location_name
        self.flow_data = flow_data
        
        self.setWindowTitle(f"Fluxo de Caixas - {location_name}")
        self.setGeometry(150, 150, 900, 600)

        # Layout principal com Scroll
        main_layout = QVBoxLayout(self)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        
        layout = QHBoxLayout(content_widget)

        # Processa os dados para separar entradas e saídas
        inflows, outflows, devolutions = self.process_data()

        # Coluna de Entradas
        layout.addWidget(self.create_flow_group("ENTRADAS", inflows, devolutions, "#d4edda"))
        
        # Coluna de Saídas
        layout.addWidget(self.create_flow_group("SAÍDAS", outflows, {}, "#f8d7da"))

    def process_data(self):
        inflows = defaultdict(lambda: defaultdict(int))
        outflows = defaultdict(lambda: defaultdict(int))
        devolutions = defaultdict(lambda: defaultdict(int))

        for row in self.flow_data:
            rti = row['rti'] if row['rti'] else 'N/A'
            qtde = row['total_qtde']
            
            if row['local_destino'] == self.location_name:
                # É uma entrada para este local
                if row['tipo_movimento'] == 'Devolução de Entrega':
                     # Tratamento especial para devolução
                     devolutions['Entrega'][rti] -= qtde
                else:
                    inflows[row['tipo_movimento']][rti] += qtde
            elif row['local_origem'] == self.location_name:
                # É uma saída deste local
                if row['tipo_movimento'] == 'Devolução de Entrega':
                     # Devolução na origem é uma saída que anula uma entrada
                     outflows['Entrega'][rti] -= qtde
                else:
                    outflows[row['tipo_movimento']][rti] += qtde
        
        return inflows, outflows, devolutions


    def create_flow_group(self, title, data, devolutions, color):
        group = QGroupBox(title)
        font = QFont()
        font.setBold(True)
        group.setFont(font)
        group.setStyleSheet(f"QGroupBox {{ background-color: {color}; border: 1px solid gray; border-radius: 5px; margin-top: 1ex; }} QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }}")

        layout = QVBoxLayout(group)
        layout.setAlignment(Qt.AlignTop)

        if not data:
            layout.addWidget(QLabel("Nenhum movimento registrado."))
            return group

        for mov_type, rti_data in sorted(data.items()):
            mov_group = QGroupBox(mov_type)
            mov_layout = QVBoxLayout(mov_group)
            
            for rti, total in sorted(rti_data.items()):
                dev_total = devolutions.get(mov_type, {}).get(rti, 0)
                final_total = total + dev_total
                
                text = f"<b>{rti}:</b> {total: ,}".replace(",", ".")
                if dev_total != 0:
                    text += f" <font color='red'>({dev_total:,})</font> = <b>{final_total:,}</b>".replace(",", ".")
                
                mov_layout.addWidget(QLabel(text))
            
            layout.addWidget(mov_group)
            
        return group