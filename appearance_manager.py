# appearance_manager.py - Gerenciador de Aparência
import json
import os
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

class AppearanceManager:
    """Gerencia configurações de aparência da aplicação"""
    
    CONFIG_FILE = "appearance_config.json"
    
    DEFAULT_SETTINGS = {
        'font_size': 10,
        'font_family': 'Arial',
        'primary_color': '#007bff',
        'background_color': '#ffffff',
        'text_color': '#000000',
        'high_contrast': False,
        'theme': 'Claro'
    }
    
    @classmethod
    def load_settings(cls):
        """Carrega configurações do arquivo"""
        try:
            if os.path.exists(cls.CONFIG_FILE):
                with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # Valida se todas as chaves existem
                for key in cls.DEFAULT_SETTINGS:
                    if key not in settings:
                        settings[key] = cls.DEFAULT_SETTINGS[key]
                
                return settings
            else:
                return cls.DEFAULT_SETTINGS.copy()
                
        except Exception as e:
            print(f"❌ Erro ao carregar configurações: {e}")
            return cls.DEFAULT_SETTINGS.copy()
    
    @classmethod
    def save_settings(cls, settings):
        """Salva configurações no arquivo"""
        try:
            with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar configurações: {e}")
            return False
    
    @classmethod
    def apply_to_application(cls, settings, main_window=None):
        """Aplica configurações na aplicação"""
        try:
            app = QApplication.instance()
            
            # Aplica fonte global
            font = QFont(settings['font_family'], settings['font_size'])
            app.setFont(font)
            
            if main_window:
                # Aplica tema
                if settings['theme'] == 'Escuro':
                    dark_style = cls.get_dark_theme_style(settings)
                    main_window.setStyleSheet(dark_style)
                elif settings['theme'] == 'Claro':
                    light_style = cls.get_light_theme_style(settings)
                    main_window.setStyleSheet(light_style)
                
                # Alto contraste
                if settings['high_contrast']:
                    contrast_style = cls.get_high_contrast_style(settings)
                    main_window.setStyleSheet(main_window.styleSheet() + contrast_style)
                
                main_window.update()
                main_window.repaint()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao aplicar configurações: {e}")
            return False
    
    @classmethod
    def get_dark_theme_style(cls, settings):
        """Retorna stylesheet para tema escuro"""
        return f"""
        QMainWindow {{
            background-color: #2b2b2b;
            color: #ffffff;
        }}
        
        QWidget {{
            background-color: #2b2b2b;
            color: #ffffff;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {settings['primary_color']};
            background-color: #404040;
        }}
        
        QTabBar::tab {{
            background: #505050;
            color: #ffffff;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }}
        
        QTabBar::tab:selected {{
            background: {settings['primary_color']};
            color: white;
        }}
        
        QGroupBox {{
            color: #ffffff;
            border: 2px solid {settings['primary_color']};
            border-radius: 5px;
            margin-top: 1ex;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            background-color: #2b2b2b;
        }}
        
        QLabel {{
            color: #ffffff;
        }}
        
        QTableView {{
            background-color: #404040;
            color: #ffffff;
            gridline-color: #606060;
        }}
        
        QTableView::item {{
            background-color: #404040;
            color: #ffffff;
        }}
        
        QTableView::item:selected {{
            background-color: {settings['primary_color']};
        }}
        
        QHeaderView::section {{
            background-color: #505050;
            color: #ffffff;
            padding: 8px;
            border: 1px solid #606060;
            font-weight: bold;
        }}
        
        QPushButton {{
            background-color: #505050;
            color: #ffffff;
            border: 1px solid #606060;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        
        QPushButton:hover {{
            background-color: #606060;
        }}
        
        QPushButton:pressed {{
            background-color: {settings['primary_color']};
        }}
        
        QComboBox {{
            background-color: #505050;
            color: #ffffff;
            border: 1px solid #606060;
            padding: 8px;
            border-radius: 4px;
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #ffffff;
        }}
        
        QFrame {{
            background-color: #404040;
            border: 1px solid #606060;
        }}
        """
    
    @classmethod
    def get_light_theme_style(cls, settings):
        """Retorna stylesheet para tema claro"""
        return f"""
        QMainWindow {{
            background-color: {settings['background_color']};
            color: {settings['text_color']};
        }}
        
        QWidget {{
            background-color: {settings['background_color']};
            color: {settings['text_color']};
        }}
        
        QTabWidget::pane {{
            border: 1px solid #c0c0c0;
            border-radius: 5px;
        }}
        
        QTabBar::tab {{
            background: #f0f0f0;
            color: {settings['text_color']};
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }}
        
        QTabBar::tab:selected {{
            background: {settings['primary_color']};
            color: white;
        }}
        
        QGroupBox {{
            color: {settings['text_color']};
            border: 2px solid {settings['primary_color']};
            border-radius: 5px;
            margin-top: 1ex;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            background-color: {settings['background_color']};
        }}
        
        QPushButton {{
            background-color: #f8f9fa;
            color: {settings['text_color']};
            border: 1px solid #dee2e6;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        
        QPushButton:hover {{
            background-color: #e9ecef;
        }}
        
        QPushButton:pressed {{
            background-color: {settings['primary_color']};
            color: white;
        }}
        """
    
    @classmethod
    def get_high_contrast_style(cls, settings):
        """Retorna stylesheet para alto contraste"""
        return """
        QWidget {
            font-weight: bold;
        }
        
        QLabel {
            color: #000000;
            background-color: #ffffff;
        }
        
        QPushButton {
            color: #000000;
            background-color: #ffff00;
            border: 2px solid #000000;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #000000;
            color: #ffffff;
        }
        
        QTabBar::tab {
            color: #000000;
            background-color: #ffffff;
            border: 2px solid #000000;
        }
        
        QTabBar::tab:selected {
            background-color: #000000;
            color: #ffffff;
        }
        """