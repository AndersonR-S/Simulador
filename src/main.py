import sys
import pygame
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow,QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QStackedWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter, QFont, QFontDatabase



class PygameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Inicializa Pygame
        pygame.init()
        self.screen = None  # Será configurado dinamicamente
        self.charges = []  # Lista para armazenar as cargas

        # Coordenadas de interação
        self.mouse_pos = (0, 0)
        self.points = []

        # Timer para atualizar o Pygame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pygame)
        self.timer.start(20)  # Aproximadamente 60 FPS

        # Label para exibir o conteúdo do Pygame
        self.label = QLabel(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

    def resizeEvent(self, event):
        """Redimensiona a superfície Pygame ao redimensionar o widget."""
        width = self.width()
        height = self.height()
        self.screen = pygame.Surface((width, height))
        super().resizeEvent(event)

    def update_pygame(self):
        if not self.screen:
            return

        # Desenha o plano cartesiano
        self.screen.fill((255, 255, 255))  # Fundo branco
        width, height = self.screen.get_size()
        mid_x, mid_y = width // 2, height // 2

        spacing = 20

        # Desenha a grade alinhada
        for x in range(mid_x % spacing, width, spacing):  # Linhas verticais
            pygame.draw.line(self.screen, (200, 200, 200), (x, 0), (x, height))
        for y in range(mid_y % spacing, height, spacing):  # Linhas horizontais
            pygame.draw.line(self.screen, (200, 200, 200), (0, y), (width, y))

        pygame.draw.line(self.screen, (0, 0, 0), (0, mid_y), (width, mid_y), 2)  # Eixo X
        pygame.draw.line(self.screen, (0, 0, 0), (mid_x, 0), (mid_x, height), 2)  # Eixo Y


        # Desenha as cargas
        for charge in self.charges:
            x, y = charge["pos"]
            x *=20
            y *=20
            charge_x = mid_x + x
            charge_y = mid_y - y  # Inverter Y para coordenadas cartesianas
            pygame.draw.circle(self.screen, (0, 255, 0), (charge_x, charge_y), 12)  # Desenhar a carga
            font = pygame.font.SysFont(None, 24)
            charge_number_text = font.render(charge['name'], True, (0, 0, 0))

            pos_x = charge_x
            pos_y = charge_y
            self.screen.blit(charge_number_text, (pos_x - charge_number_text.get_width() // 2, pos_y - charge_number_text.get_height() // 2))

        # Converte a tela do Pygame para QPixmap e exibe no QLabel
        image_data = pygame.image.tostring(self.screen, "RGB")
        qimage = QImage(image_data, width, height, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qimage))

    def atualizarName(self):
        for i in range(len(self.charges)):
            self.charges[i]['name'] = f"q{i + 1}"

    def addCharge(self, charge_value, position):
        """Adiciona uma nova carga ao sistema."""
        try:
            charge_value = float(charge_value)
            position = tuple(map(int, position.strip("()").split(",")))  # Parsing seguro para posição
            if len(position) == 2:
                new_charge = {"charge": charge_value, "pos": position, "name":f"q{len(self.charges) + 1}"}
                self.charges.append(new_charge)
                print(f"Carga adicionada: {new_charge}")
            else:
                raise ValueError("A posição deve ser uma tupla (x, y).")
        except Exception as e:
            print(f"Erro ao adicionar carga: {e}")

    def removeCharge(self, charge_number):
        print(f'Removendo {charge_number}')
        try:
            for charge in self.charges:
                if charge["name"] == charge_number:
                    self.charges.remove(charge)
                    print(f"Carga removida: {charge}")
                    self.atualizarName()

                    break
            else:
                print(f"Carga não encontrada: Q{charge_number}")
        except Exception as e:
            print(f"Erro ao remover carga: {e}")

    def alterarCharge(self, charge_data):
        #print(f'Alterando {charge_data}')
        try:
            for charge in self.charges:
                if charge["name"] == charge_data['name']:
                    charge["charge"] = charge_data['charge']
                    charge["pos"] = tuple(map(int, charge_data['pos'].strip("()").split(",")))
                    break
            else:
                print(f"Carga não encontrada: {charge_data['name']}")
        except Exception as e:
            print(f"Erro ao alterar carga: {e}")



    def buscarCharge(self, charge_number):
        print(f'Buscando {charge_number}')
        try:
            for charge in self.charges:
                if charge["name"] == charge_number:
                    print(f"Carga encontrada: {charge}")
                    return charge
            else:
                print(f"Carga não encontrada: Q{charge_number}")
                return None
        except Exception as e:
            print(f"Erro ao buscar carga: {e}")               
            return None


class Interface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pagina_inicial = True
        self.layout_app()

        self.interface_intro()
        QTimer.singleShot(1000, self.atualizar_interface)  # 5000 milissegundos = 5 segundos

    def layout_app(self):
        self.setWindowTitle("Simulador de Campo de Futebol")
        screen = QApplication.primaryScreen()
        screen_geometry =screen.availableGeometry()  

        self.width = int(screen_geometry.width() * 0.8)
        self.height = int(screen_geometry.height() * 0.8)
        self.resize(self.width, self.height)

        self.move(
            (screen_geometry.width() - self.width) // 2,
            (screen_geometry.height() - self.height) // 2
        )

        available_fonts = QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(""))
        if "Roboto" in available_fonts:
            self.font = QFont("Roboto")
        elif "Liberation Sans" in available_fonts:
            self.fonte = QFont("Liberation Sans")
        else:
            self.fonte = QFont("Arial") 

    def interface_intro(self):

        layout_principal = QVBoxLayout()

        # Texto do título
        title_open = QLabel("Simulador da Lei de Coulomb")
        title_open.setAlignment(Qt.AlignCenter)  # Centraliza o texto
        title_open.setStyleSheet("font-family: fonte; font-size: 55px; font-weight: bold;")

        layout_principal.addWidget(title_open)  # Adiciona ao layout principal

        # Define o layout na janela principal
        container_open = QWidget()
        container_open.setLayout(layout_principal)
        #container_open.setStyleSheet("background-color: #f0f0f0;")

        self.setCentralWidget(container_open)


    def atualizar_interface(self):
        if self.pagina_inicial:
            self.pagina_inicial = False
            self.interface_introduction()
        else:
            self.interface_play()


    def interface_introduction(self):
        self.setCentralWidget(None)  # Remove o layout atual

        layout_principal = QVBoxLayout()

        # Widgets principais
        # Widgets principais
        widget_superior = QWidget()
        widget_inferior = QWidget()

        # Widgets para divisão inferior
        widget_inferior_esquerdo = QWidget()
        widget_inferior_direito = QWidget()
        #texto_introduction = QLabel("A Lei de Coulomb é uma lei da física que descreve a interação eletrostática")
        # Texto de introdução
        #texto_introducao = QLabel("A Lei de Coulomb é uma lei da física que descreve a interação eletrost")
        title_open = QLabel("Lei de Coulomb")
        #title_open.setAlignment(Qt.AlignCenter)  # Centraliza o texto
        title_open.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold;")
        layout_principal.addWidget(title_open, alignment=Qt.AlignLeft)


        # Botão "Pular"
        button_pular = QPushButton("Pular")
        button_pular.clicked.connect(self.interface_play)  
        button_pular.setFixedSize(100, 50)
        button_pular.setStyleSheet("font-family: fonte; font-size: 25px; color: black; border: none;")
        layout_principal.addWidget(button_pular, alignment=Qt.AlignRight)

        container_open = QWidget()
        container_open.setLayout(layout_principal)
        self.setCentralWidget(container_open)
        

    def interface_play(self):
        self.setCentralWidget(None)  

        layout_principal = QVBoxLayout()
        self.pygame_widget = PygameWidget(self)



        largura_janela = self.size().width()
        altura_janela = self.size().height()

        self.aviso = QLabel()
        self.aviso.setStyleSheet("font-family: fonte; font-size: 18px; color: red; border: none; margin-top: 30px")


        # Superior
        # Menu superior
        widget_superior = QWidget()
        widget_superior.setFixedHeight(int(altura_janela * 0.05))  

        widget_superior.setStyleSheet("border-bottom: 2px solid darkgray;")
        
        layout_superior = QHBoxLayout()
        layout_superior.setContentsMargins(10, 0, 10, 0)

        buttons = [
            ("ARQUIVO", self.arquivo),
            ("ADICIONAR", self.adicionar),
            ("REMOVER", self.remover),
            ("ALTERAR", self.alterar),
            ("DADOS DA CARGA", self.dadosCarga),
            ("DISTÂNCIA ENTRE CARGAS", self.distanciaEntreCargas),
        ]

        for text, callback in buttons:
            button = QPushButton(text)
            button.clicked.connect(callback)
            
            button.setStyleSheet("font-family: fonte; font-size: 16px; color: black; border: none; margin-right: 50px;")
            layout_superior.addWidget(button)

        layout_superior.addStretch()
        widget_superior.setLayout(layout_superior)

        # Inferior 
        widget_inferior = QWidget()
        self.layout_inferior = QHBoxLayout()


        # Menu inferior esquerdo
        widget_inferior_esquerdo = QWidget()
        widget_inferior_esquerdo.setMinimumSize(int(largura_janela * 0.3), int(altura_janela * 0.95))
        widget_inferior_esquerdo.setStyleSheet(" border-right: 2px solid darkgray;")

        self.layout_menu_esquerdo = QVBoxLayout()
        #self.layout_menu_esquerdo.setContentsMargins(10, 0, 10, 0)
        
        self.arquivo()

        widget_inferior_esquerdo.setLayout(self.layout_menu_esquerdo)
        self.layout_inferior.addWidget(widget_inferior_esquerdo)

        # Plano inferior direito
        widget_inferior_direito = QWidget()
        widget_inferior_direito.setMinimumSize(int(largura_janela * 0.7), int(altura_janela * 0.95))  


        layout_direito = QVBoxLayout()
        layout_direito.addWidget(self.pygame_widget)
        widget_inferior_direito.setLayout(layout_direito)

        self.layout_inferior.addWidget(widget_inferior_direito)



        # Colocando as duas colunas no layout inferior
        widget_inferior.setLayout(self.layout_inferior)

        # Adiciona widgets principais ao layout principal
        layout_principal.addWidget(widget_superior)
        layout_principal.addWidget(widget_inferior)

        layout_principal.addStretch()

        # Container principal
        container_play = QWidget()
        container_play.setLayout(layout_principal)
        self.setCentralWidget(container_play)


    def limpar_menu_esquerdo(self):
        """Limpar os widgets do menu esquerdo e garantir que o layout seja completamente reiniciado"""
        # Remover todos os widgets do layout antigo
        for i in reversed(range(self.layout_menu_esquerdo.count())):
            widget = self.layout_menu_esquerdo.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        self.layout_menu_esquerdo.setAlignment(Qt.AlignTop)


        



    def vazio(self):
        pass

    def arquivo(self):
        # Limpar o menu esquerdo
        self.limpar_menu_esquerdo()

        # Título da seção
        title_adicionar = QLabel("ARQUIVO")
        title_adicionar.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold; border: none; margin-bottom: 20px;")
        self.layout_menu_esquerdo.addWidget(title_adicionar)

        # Lista de botões e suas ações
        buttons = [
            ("Reiniciar", self.interface_intro),
            ("Importar", self.vazio),
            ("Salvar", self.vazio),
            ("Visualizar forças separadas", self.vazio),
            ("Visualizar cargas no sistema", self.vazio),
        ]

        # Adicionando os botões ao layout
        for text, callback in buttons:
            button = QPushButton(text)
            button.clicked.connect(callback)
            button.setStyleSheet("""
                font-family: fonte;
                font-size: 18px;
                color: black;
                border: none;
                margin-bottom: 10px;
                text-align: left;
                padding-left: 10px;
            """)
            self.layout_menu_esquerdo.addWidget(button)

    def adicionar(self):
        self.limpar_menu_esquerdo()

        title_adicionar = QLabel("ADICIONAR")
        title_adicionar.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold; border: none; margin-bottom: 20px;")

        q_adicionar = QLabel("O valor da carga:")
        q_adicionar.setStyleSheet("font-family: fonte; font-size: 18px; border: none;")
        q_campo_texto = QLineEdit()
        q_campo_texto.setPlaceholderText("Digite a carga")
        q_campo_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")
        pos_adicionar = QLabel("Posição da carga:")
        pos_adicionar.setStyleSheet("font-family: fonte; font-size: 18px; border: none; margin-top: 20px;")
        pos_texto = QLineEdit()
        pos_texto.setPlaceholderText("x,y")
        pos_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

        add_button = QPushButton("Adicionar")
        add_button.clicked.connect(lambda: self.pygame_widget.addCharge(q_campo_texto.text().strip(), pos_texto.text().strip()))
        add_button.setStyleSheet("font-family: fonte; font-size: 16px; padding: 10px;  color: black; margin-top: 20px;")

        self.layout_menu_esquerdo.addWidget(title_adicionar)
        self.layout_menu_esquerdo.addWidget(q_adicionar)
        self.layout_menu_esquerdo.addWidget(q_campo_texto)
        self.layout_menu_esquerdo.addWidget(pos_adicionar)
        self.layout_menu_esquerdo.addWidget(pos_texto)
        self.layout_menu_esquerdo.addWidget(add_button)


    def remover(self):
        self.limpar_menu_esquerdo()

        title_adicionar = QLabel("REMOVER")
        title_adicionar.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold; border: none; margin-bottom: 20px;")

        r_remover = QLabel("O nome da carga ou a posição:")
        r_remover.setStyleSheet("font-family: fonte; font-size: 18px; border: none;")
        r_campo_texto = QLineEdit()
        r_campo_texto.setPlaceholderText("Digite o nome ou posição x,y da carga")
        r_campo_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

        sub_button = QPushButton("Remover")
        sub_button.clicked.connect(lambda: self.pygame_widget.removeCharge(r_campo_texto.text().strip()))

        sub_button.setStyleSheet("font-family: fonte; font-size: 16px; padding: 10px;  color: black; margin-top: 20px;")

        self.layout_menu_esquerdo.addWidget(title_adicionar)
        self.layout_menu_esquerdo.addWidget(r_remover)
        self.layout_menu_esquerdo.addWidget(r_campo_texto)
        self.layout_menu_esquerdo.addWidget(sub_button) 

    def alterar(self):
        self.limpar_menu_esquerdo()

        title_adicionar = QLabel("Alterar")
        title_adicionar.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold; border: none; margin-bottom: 20px;")

        b_buscar = QLabel("O nome da carga ou a posição:")
        b_buscar.setStyleSheet("font-family: fonte; font-size: 18px; border: none;")
        b_campo_texto = QLineEdit()
        b_campo_texto.setPlaceholderText("Digite o nome ou posição x,y da carga")
        b_campo_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

        buscar_button = QPushButton("Buscar")
        buscar_button.clicked.connect(lambda: self.displayAlteraCharge(b_campo_texto.text().strip()))

        buscar_button.setStyleSheet("font-family: fonte; font-size: 16px; padding: 10px;  color: black; margin-top: 20px;")

        self.layout_menu_esquerdo.addWidget(title_adicionar)
        self.layout_menu_esquerdo.addWidget(b_buscar)
        self.layout_menu_esquerdo.addWidget(b_campo_texto)
        self.layout_menu_esquerdo.addWidget(buscar_button)
    
    def displayAlteraCharge(self, charge_number):
        charges = self.pygame_widget.buscarCharge(charge_number)
        if charges is not None:
            self.alterar()

            q_adicionar = QLabel("O valor da carga:")
            q_adicionar.setStyleSheet("font-family: fonte; font-size: 18px; border: none;")
            q_campo_texto = QLineEdit()
            q_campo_texto.setPlaceholderText("Digite a carga")
            q_campo_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")
           
            pos_adicionar = QLabel("Posição da carga:")
            pos_adicionar.setStyleSheet("font-family: fonte; font-size: 18px; border: none; margin-top: 20px;")
            pos_texto = QLineEdit()
            pos_texto.setPlaceholderText("x,y")
            pos_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

            add_button = QPushButton("Alterar")
            add_button.clicked.connect(lambda: self.pygame_widget.alterarCharge({'charge': q_campo_texto.text().strip(), 'pos': pos_texto.text().strip(), 'name': charge_number}))
            add_button.setStyleSheet("font-family: fonte; font-size: 16px; padding: 10px;  color: black; margin-top: 20px;")

            self.layout_menu_esquerdo.addWidget(QLabel(f"Nome: {charges['name']}"))
            self.layout_menu_esquerdo.addWidget(QLabel(f"Carga: {charges['charge']}"))
            self.layout_menu_esquerdo.addWidget(QLabel(f"Posição: {charges['pos']}"))

            self.layout_menu_esquerdo.addWidget(q_adicionar)
            self.layout_menu_esquerdo.addWidget(q_campo_texto)
            self.layout_menu_esquerdo.addWidget(pos_adicionar)
            self.layout_menu_esquerdo.addWidget(pos_texto)
            self.layout_menu_esquerdo.addWidget(add_button)
            



    def dadosCarga(self):
        self.limpar_menu_esquerdo()

        title_adicionar = QLabel("Dados da Carga")
        title_adicionar.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold; border: none; margin-bottom: 20px;")

        b_buscar = QLabel("O nome da carga ou a posição:")
        b_buscar.setStyleSheet("font-family: fonte; font-size: 18px; border: none;")
        b_campo_texto = QLineEdit()
        b_campo_texto.setPlaceholderText("Digite o nome ou posição x,y da carga")
        b_campo_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

        buscar_button = QPushButton("Buscar")
        buscar_button.clicked.connect(lambda: self.display_charge_data(b_campo_texto.text().strip()))
        buscar_button.setStyleSheet("font-family: fonte; font-size: 16px; padding: 10px;  color: black; margin-top: 20px;")

        self.layout_menu_esquerdo.addWidget(title_adicionar)
        self.layout_menu_esquerdo.addWidget(b_buscar)
        self.layout_menu_esquerdo.addWidget(b_campo_texto)
        self.layout_menu_esquerdo.addWidget(buscar_button)

    def display_charge_data(self, charge_number):
            charge = self.pygame_widget.buscarCharge(charge_number)
            if charge is not None:
                self.dadosCarga()
                self.layout_menu_esquerdo.addWidget(QLabel(f"Nome: {charge['name']}"))
                self.layout_menu_esquerdo.addWidget(QLabel(f"Carga: {charge['charge']}"))
                self.layout_menu_esquerdo.addWidget(QLabel(f"Posição: {charge['pos']}"))


    def distanciaEntreCargas(self):
        self.limpar_menu_esquerdo()

        title_adicionar = QLabel("Distância entre Cargas")
        title_adicionar.setStyleSheet("font-family: fonte; font-size: 25px; font-weight: bold; border: none; margin-bottom: 20px;")

        q1_distancia = QLabel("O nome da carga ou a posição da caraga 1:")
        q1_distancia .setStyleSheet("font-family: fonte; font-size: 18px; border: none;")
        q1_campo_texto = QLineEdit()
        q1_campo_texto.setPlaceholderText("Digite o nome ou posição x,y da carga")
        q1_campo_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

        q2_distancia = QLabel("O nome da carga ou a posição da caraga 2:")
        q2_distancia.setStyleSheet("font-family: fonte; font-size: 18px; border: none; margin-top: 20px;")
        q2_campo_texto = QLineEdit()
        q2_campo_texto.setPlaceholderText("Digite o nome ou posição x,y da carga")
        q2_campo_texto.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid gray;")

        buscar_button = QPushButton("Calcular Distância")
        buscar_button.clicked.connect(self.vazio) 
        buscar_button.setStyleSheet("font-family: fonte; font-size: 16px; padding: 10px;  color: black; margin-top: 20px;")

        self.layout_menu_esquerdo.addWidget(title_adicionar)
        self.layout_menu_esquerdo.addWidget(q1_distancia)
        self.layout_menu_esquerdo.addWidget(q1_campo_texto)
        self.layout_menu_esquerdo.addWidget(q2_distancia)
        self.layout_menu_esquerdo.addWidget(q2_campo_texto)
        self.layout_menu_esquerdo.addWidget(buscar_button)   


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Interface()
    window.show()
    sys.exit(app.exec_())