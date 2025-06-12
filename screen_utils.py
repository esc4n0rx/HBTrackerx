# screen_utils.py - NOVO ARQUIVO PARA GERENCIAR TAMANHOS RESPONSIVOS
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtCore import QRect

class ScreenManager:
    """Gerencia tamanhos responsivos baseados na resolução da tela"""
    
    @staticmethod
    def get_screen_geometry():
        """Retorna geometria da tela disponível"""
        app = QApplication.instance()
        if app is None:
            # Se não há aplicação, cria uma temporária
            temp_app = QApplication([])
            screen = temp_app.primaryScreen()
            geometry = screen.availableGeometry()
            temp_app.quit()
            return geometry
        else:
            screen = app.primaryScreen()
            return screen.availableGeometry()
    
    @staticmethod
    def get_responsive_size(width_percent=0.8, height_percent=0.8, 
                          min_width=800, min_height=600,
                          max_width=1600, max_height=1000):
        """
        Calcula tamanho responsivo baseado na tela
        
        Args:
            width_percent: Porcentagem da largura da tela (0.0 a 1.0)
            height_percent: Porcentagem da altura da tela (0.0 a 1.0)
            min_width: Largura mínima
            min_height: Altura mínima
            max_width: Largura máxima
            max_height: Altura máxima
        
        Returns:
            tuple: (width, height)
        """
        geometry = ScreenManager.get_screen_geometry()
        
        # Calcula tamanhos baseados na porcentagem
        calculated_width = int(geometry.width() * width_percent)
        calculated_height = int(geometry.height() * height_percent)
        
        # Aplica limites mínimos e máximos
        width = max(min_width, min(max_width, calculated_width))
        height = max(min_height, min(max_height, calculated_height))
        
        return (width, height)
    
    @staticmethod
    def center_window(window):
        """Centraliza janela na tela"""
        geometry = ScreenManager.get_screen_geometry()
        window_rect = window.frameGeometry()
        center_point = geometry.center()
        window_rect.moveCenter(center_point)
        window.move(window_rect.topLeft())
    
    @staticmethod
    def get_dialog_size(dialog_type="default"):
        """
        Retorna tamanhos pré-definidos para diferentes tipos de diálogo
        
        Args:
            dialog_type: Tipo do diálogo
                - "small": Diálogos pequenos (settings)
                - "medium": Diálogos médios (flow)
                - "large": Diálogos grandes (analysis)
                - "fullscreen": Quase tela cheia
        
        Returns:
            tuple: (width, height)
        """
        if dialog_type == "small":
            return ScreenManager.get_responsive_size(0.4, 0.5, 500, 400, 800, 700)
        elif dialog_type == "medium":
            return ScreenManager.get_responsive_size(0.7, 0.7, 900, 600, 1200, 800)
        elif dialog_type == "large":
            return ScreenManager.get_responsive_size(0.85, 0.8, 1000, 700, 1400, 900)
        elif dialog_type == "fullscreen":
            return ScreenManager.get_responsive_size(0.95, 0.9, 1200, 800, 1800, 1000)
        else:  # default
            return ScreenManager.get_responsive_size(0.6, 0.6, 800, 600, 1200, 800)

class ResponsiveDialog:
    """Mixin para tornar diálogos responsivos"""
    
    def make_responsive(self, dialog_type="default", center=True):
        """
        Torna o diálogo responsivo
        
        Args:
            dialog_type: Tipo do diálogo (ver ScreenManager.get_dialog_size)
            center: Se deve centralizar na tela
        """
        width, height = ScreenManager.get_dialog_size(dialog_type)
        
        # Define tamanho responsivo
        self.resize(width, height)
        
        # Define tamanhos mínimos sensatos
        min_width = min(600, width)
        min_height = min(400, height)
        self.setMinimumSize(min_width, min_height)
        
        # Centraliza se solicitado
        if center:
            ScreenManager.center_window(self)
        
        print(f"✅ Diálogo responsivo: {width}x{height} (tipo: {dialog_type})")