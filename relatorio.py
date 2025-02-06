import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from fpdf import FPDF
import json
import os
from datetime import datetime, timedelta
from ttkbootstrap import Style
import subprocess
import sys
import webbrowser
import pdfplumber
import re 

def install(package):
    """Instala um pacote usando pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    # Lista de pacotes necessários
    packages = [
        "ttkbootstrap",
        "fpdf"
    ]

    for package in packages:
        try:
            __import__(package)  # Tenta importar o pacote
        except ImportError:
            print(f"{package} não está instalado. Instalando...")
            install(package)

# File to store product and client data
DATA_FILE = "cadastros.json"

# Product and Client data storage
products = []
clients = []
reports = []  # To store report data
inventory = []  # To store inventory data


import tkinter as tk
from tkinter import ttk
import json
import os

DATA_FILE = 'cadastros.json'  # Defina o caminho do seu arquivo JSON

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Orçamento - Madeireira")
        self.geometry("800x600")
        self.style = Style(theme="flatly")
        self.inventory = []  # Inicializa a lista de inventário

        # Carregar dados existentes
        self.load_data()

        # Criar um controle de abas
        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(expand=1, fill='both')

        # Criar abas
        self.tab_products = ProductsTab(self)  # Pass self como parent
        self.tab_clients = ClientsTab(self)
        self.tab_notes = NotesTab(self)
        self.tab_reports = ReportsTab(self)  # Nova aba de Relatório
        self.tab_inventory = InventoryTab(self)  # Nova aba de Estoque

        # Adicionar abas ao controle de abas
        self.tab_control.add(self.tab_products, text='Produtos')
        self.tab_control.add(self.tab_clients, text='Clientes')
        self.tab_control.add(self.tab_notes, text='Notas')
        self.tab_control.add(self.tab_reports, text='Relatório')  # Adicionar aba de Relatório
        self.tab_control.add(self.tab_inventory, text='Estoque')  # Adicionar aba de Estoque

        # Iniciar o loop de atualização do inventário
        self.update_inventory()

    def load_data(self):
        """Carregar produtos e clientes do arquivo JSON."""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as file:
                try:
                    data = json.load(file)
                    global products, clients, reports
                    products = data.get("produtos", [])
                    clients = data.get("clientes", [])
                    self.inventory = data.get("estoque", [])  # Carregar dados do estoque
                    reports = data.get("relatorios", [])  # Carregar dados de relatórios

                    # Garantir que todos os itens do inventário tenham o campo 'un_com'
                    for inv in self.inventory:
                        if 'un_com' not in inv:
                            inv['un_com'] = "N/A"  # Valor padrão se 'un_com' estiver faltando
                except json.JSONDecodeError:
                    print("Arquivo JSON está vazio ou malformado. Inicializando dados padrão.")
                    self.initialize_data()  # Chama um método para inicializar dados padrão
        else:
            print("Arquivo JSON não encontrado. Inicializando dados padrão.")
            self.initialize_data()  # Chama um método para inicializar dados padrão

    def initialize_data(self):
        """Inicializa dados padrão."""
        global products, clients, reports
        products = []
        clients = []
        reports = []
        self.inventory = []  # Inicializa a lista de inventário
        self.save_data()  # Salva os dados padrão no arquivo JSON

    def save_data(self):
        """Salvar produtos e clientes no arquivo JSON."""
        data = {
            "produtos": products,
            "clientes": clients,
            "estoque": self.inventory,  # Salvar dados do estoque
            "relatorios": reports  # Salvar dados de relatórios
        }
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)

    def update_inventory(self):
        """Atualizar o inventário a cada segundo."""
        self.save_data()  # Salvar dados periodicamente
        self.after(1000, self.update_inventory)  # Chamar este método novamente após 1 segundo

    def destroy(self):
        """Sobrescrever o método destroy para limpar nota.json antes de fechar."""
        with open('nota.json', 'w') as json_file:
            json.dump({}, json_file)  # Limpar o conteúdo de nota.json
        super().destroy()    

class ProductsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.selected_button = None
        self.create_widgets()

    def create_widgets(self):
        # Menu lateral
        self.sidebar = tk.Frame(self, bg="white", width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.menu_buttons = {
            "Cadastrar Produtos LxE": self.show_register_product,
            "Cadastrar Produtos Dz-Unid": self.show_new_product_registration,
            "Cadastrar Itens": self.show_register_item,  # Novo botão para cadastrar itens
            "Editar Produtos": self.show_edit_product,
            "Excluir Produtos": self.show_delete_product
        }

        self.buttons = {}
        for idx, (label, command) in enumerate(self.menu_buttons.items()):
            btn = tk.Button(
                self.sidebar,
                text=label,
                font=("Arial", 12),
                bg="white",
                fg="black",
                activebackground="gray",
                activeforeground="white",
                command=lambda cmd=command, b=label: self.select_button(b, cmd),
            )
            btn.pack(fill=tk.X, padx=5, pady=(0 if idx == 0 else 5))
            self.buttons[label] = btn

        # Área central
        self.main_frame = tk.Frame(self, bg="white")
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Inicializa com o frame de cadastro de produtos
        self.register_product_frame()
        self.select_button("Cadastrar Produtos LxE", self.show_register_product)

    def select_button(self, button_label, command):
        if self.selected_button:
            self.buttons[self.selected_button].config(bg="white", fg="black")

        self.buttons[button_label].config(bg="gray", fg="white")
        self.selected_button = button_label

        # Chama o comando associado
        command()

    def show_register_product(self):
        """Show the product registration frame."""
        self.clear_main_frame()
        self.register_product_frame()
        self.register_frame.pack(fill=tk.BOTH, expand=True)

    def register_product_frame(self):
        self.register_frame = tk.Frame(self.main_frame, bg="white")
        self.register_frame.pack(fill=tk.BOTH, expand=True)

        self.un_com_var = tk.StringVar(value="UNIDADE")
        ttk.Label(self.register_frame, text="UNIDADE DE COMERCIALIZAÇÃO:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Radiobutton(self.register_frame, text="UNIDADE", variable=self.un_com_var, value="UNIDADE", command=self.toggle_frame).grid(row=0, column=1, sticky=tk.W)

        self.unit_frame = tk.Frame(self.register_frame, bg="white")
        self.create_unit_fields()

        self.unit_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

    def toggle_frame(self):
        if self.un_com_var.get() == "UNIDADE":
            self.unit_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

    def create_unit_fields(self):
        ttk.Label(self.unit_frame, text="DESCRIÇÃO:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_desc = ttk.Entry(self.unit_frame)
        self.prod_desc.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.unit_frame, text="ESPESSURA (cm):").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_thickness = ttk.Entry(self.unit_frame)
        self.prod_thickness.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.unit_frame, text="LARGURA (cm):").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_width = ttk.Entry(self.unit_frame)
        self.prod_width.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        # Novo campo para Tipo de Madeira
        ttk.Label(self.unit_frame, text="TIPO DE MADEIRA:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_wood_type = ttk.Entry(self.unit_frame)
        self.prod_wood_type.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.unit_frame, text="PREÇO POR M³:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_cost_per_m3 = ttk.Entry(self.unit_frame)
        self.prod_cost_per_m3.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.unit_frame, text="PREÇO DE VENDA POR M LINEAR:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_sale_price_per_m = ttk.Entry(self.unit_frame)
        self.prod_sale_price_per_m.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)

        # Lucro e Botão de Adicionar
        self.lucro_label = ttk.Label(self.unit_frame, text="Lucro: R$ 0.00")
        self.lucro_label.grid(row=6, column=0, columnspan=2, pady=5)

        self.lucro_percentage_label = ttk.Label(self.unit_frame, text="Porcentagem de Lucro: 0.00%")
        self.lucro_percentage_label.grid(row=7, column=0, columnspan=2, pady=5)

        ttk.Button(self.unit_frame, text="Adicionar", command=self.register_product_unit).grid(row=8, column=0, columnspan=2, pady=10)

        # Bind the entry fields to calculate profit in real-time
        self.prod_cost_per_m3.bind("<KeyRelease>", self.calculate_profit)
        self.prod_width.bind("<KeyRelease>", self.calculate_profit)
        self.prod_thickness.bind("<KeyRelease>", self.calculate_profit)
        self.prod_sale_price_per_m.bind("<KeyRelease>", self.calculate_profit)

    def calculate_profit(self, event=None):
        try:
            cost_per_m3 = float(self.prod_cost_per_m3.get().replace(',', '.'))
            width = float(self.prod_width.get()) / 100  # Convert to meters
            thickness = float(self.prod_thickness.get()) / 100  # Convert to meters
            sale_price_per_m = float(self.prod_sale_price_per_m.get().replace(',', '.'))

            # Calculate volume per linear meter
            volume_per_m = width * thickness  # Volume for 1 meter linear

            # Calculate cost and profit
            cost_per_meter = volume_per_m * cost_per_m3
            profit = sale_price_per_m - cost_per_meter
            profit_percentage = (profit / cost_per_meter * 100) if cost_per_meter > 0 else 0  # Calculate profit percentage

            self.lucro_label.config(text=f"Lucro: R$ {profit:.2f}".rstrip('0').rstrip('.'))
            self.lucro_percentage_label.config(text=f"Porcentagem de Lucro: {profit_percentage:.2f}%")
        except ValueError:
            self.lucro_label.config(text="Lucro: R$ 0.00")
            self.lucro_percentage_label.config(text="Porcentagem de Lucro: 0.00%")        

    def register_product_unit(self):
        try:
            # Retrieve input values for UNIDADE
            product_name = self.prod_desc.get()
            width = int(float(self.prod_width.get()))  # Convert to integer
            thickness = int(float(self.prod_thickness.get()))  # Convert to integer
            wood_type = self.prod_wood_type.get()
            cost_per_m3 = float(self.prod_cost_per_m3.get().replace(',', '.'))
            sale_price_per_m = float(self.prod_sale_price_per_m.get().replace(',', '.'))

            # Validate required fields
            if not product_name or not wood_type:
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
                return

            # Create a new product dictionary
            new_product = {
                "descricao": product_name,
                "largura": width,
                "espessura": thickness,
                "madeira": wood_type,
                "un_com": "UNIDADE",
                "vl_m": cost_per_m3,
                "valor_venda": sale_price_per_m,
                "tipo": "LxE"  # Adicionando o tipo do produto
            }

            # Calculate and store profit percentage
            width_m = width / 100  # Convert to meters
            thickness_m = thickness / 100  # Convert to meters
            volume_per_m = width_m * thickness_m  # Volume for 1 meter linear
            cost_per_meter = volume_per_m * cost_per_m3
            profit = sale_price_per_m - cost_per_meter
            profit_percentage = (profit / cost_per_meter * 100) if cost_per_meter > 0 else 0
            new_product["porcentagem_lucro"] = profit_percentage  # Store profit percentage

            # Add the product to the global list
            products.append(new_product)

            # Notify the user
            messagebox.showinfo("Sucesso", f"Produto '{product_name}' cadastrado com sucesso!")

            # Clear input fields
            self.prod_desc.delete(0, tk.END)
            self.prod_width.delete(0, tk.END)
            self.prod_thickness.delete(0, tk.END)
            self.prod_wood_type.delete(0, tk.END)
            self.prod_cost_per_m3.delete(0, tk.END)
            self.prod_sale_price_per_m.delete(0, tk.END)
            self.lucro_label.config(text="Lucro: R$ 0.00")
            self.lucro_percentage_label.config(text="Porcentagem de Lucro: 0.00%")

            # Save the data persistently
            self.parent.save_data()

        except ValueError:
            messagebox.showerror("Erro", "Certifique-se de que os campos numéricos estão preenchidos corretamente.")

    def show_register_item(self):
        self.clear_main_frame()
        self.register_item_frame()
        self.register_frame.pack(fill=tk.BOTH, expand=True)

    def register_item_frame(self):
        self.register_frame = tk.Frame(self.main_frame, bg="white")
        self.register_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.register_frame, text="DESCRIÇÃO:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.item_desc = ttk.Entry(self.register_frame)
        self.item_desc.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.register_frame, text="PREÇO DE VENDA:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.item_sale_price = ttk.Entry(self.register_frame)
        self.item_sale_price.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.register_frame, text="PREÇO DE COMPRA:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.item_purchase_price = ttk.Entry(self.register_frame)
        self.item_purchase_price.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Button(self.register_frame, text="Adicionar Item", command=self.register_item).grid(row=4, columnspan=2, pady=10)

    def calculate_item_profit(self, event=None):
        try:
            sale_price = float(self.item_sale_price.get().replace(',', '.'))
            purchase_price = float(self.item_purchase_price.get().replace(',', '.'))

            # Calculate profit
            profit = sale_price - purchase_price
            profit_percentage = (profit / purchase_price * 100) if purchase_price > 0 else 0  # Calculate profit percentage

            self.lucro_label.config(text=f"Lucro: R$ {profit:.2f}".rstrip('0').rstrip('.'))
            self.lucro_percentage_label.config(text=f"Porcentagem de Lucro: {profit_percentage:.2f}%")
        except ValueError:
            self.lucro_label.config(text="Lucro: R$ 0.00")
            self.lucro_percentage_label.config(text="Porcentagem de Lucro: 0.00%")

    def register_item(self):
        try:
            item_name = self.item_desc.get()
            sale_price = float(self.item_sale_price.get().replace(',', '.'))
            purchase_price = float(self.item_purchase_price.get().replace(',', '.'))

            if not item_name:
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
                return

            new_item = {
                "descricao": item_name,
                "valor_venda": sale_price,
                "preco_compra": purchase_price,
                "un_com": "UNIDADE",  # Assuming UNIDADE for this example
                "tipo": "Item"  # Adicionando o tipo do produto
            }

            products.append(new_item)  # Add to global products list

            messagebox.showinfo("Sucesso", f"Item '{item_name}' cadastrado com sucesso!")

            self.clear_item_fields()  # Clear fields after registration
            self.parent.save_data()  # Save data persistently

        except ValueError:
            messagebox.showerror("Erro", "Certifique-se de que os campos numéricos estão preenchidos corretamente.")

    def clear_item_fields(self):
        self.item_desc.delete(0, tk.END)
        self.item_sale_price.delete(0, tk.END)
        self.item_purchase_price.delete(0, tk.END)

    def show_edit_product(self):
        self.clear_main_frame()
        self.edit_frame = tk.Frame(self.main_frame, bg="white")
        self.edit_frame.pack(fill=tk.BOTH, expand=True)

        for product in products:  # Use the global products list
            product_frame = tk.Frame(self.edit_frame, bg="white", relief=tk.RAISED, bd=1)
            product_frame.pack(fill=tk.X, padx=5, pady=2)

            # Display the product based on its type
            if "tamanho" in product:  # Produto do tipo Dz-Unid
                product_display = f"{product.get('descricao', 'N/A')} - {product.get('madeira', 'N/A')} - {product.get('tamanho', 'N/A')}"
            elif "espessura" in product:  # Produto do tipo LxE
                product_display = f"{product.get('descricao', 'N/A')} - {product.get('espessura', 'N/A')} X {product.get('largura', 'N/A')} - {product.get('madeira', 'N/A')}"
            else:  # Produto do tipo Item
                product_display = f"{product.get('descricao', 'N/A')}"

            lbl_name = tk.Label(product_frame, text=product_display, font=("Arial", 12), bg="white", anchor=tk.W)
            lbl_name.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

            btn_expand = tk.Button(
                product_frame,
                text="▼",
                font=("Arial", 10),
                bg="white",
                command=lambda p=product, f=product_frame: self.toggle_edit_details(p, f),
            )
            btn_expand.pack(side=tk.RIGHT)

    def toggle_edit_details(self, product, frame):
        if hasattr(frame, "edit_details_frame") and frame.edit_details_frame.winfo_ismapped():
            frame.edit_details_frame.pack_forget()
        else:
            if not hasattr(frame, "edit_details_frame"):
                frame.edit_details_frame = tk.Frame(frame, bg="white")

                # Edit fields based on product type
                if "tamanho" in product:  # Produto do tipo Dz-Unid
                    ttk.Label(frame.edit_details_frame, text="Nome:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
                    edit_name = ttk.Entry(frame.edit_details_frame)
                    edit_name.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
                    edit_name.insert(0, product.get("descricao", ""))

                    ttk.Label(frame.edit_details_frame, text="Tipo de Madeira:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
                    edit_wood_type = ttk.Entry(frame.edit_details_frame)
                    edit_wood_type.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
                    edit_wood_type.insert(0, product.get("madeira", ""))

                    ttk.Label(frame.edit_details_frame, text="Tamanho:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
                    edit_size = ttk.Entry(frame.edit_details_frame)
                    edit_size.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
                    edit_size.insert(0, product.get("tamanho", ""))

                    save_button = tk.Button(
                        frame.edit_details_frame,
                        text="SALVAR",
                        font=("Arial", 10, "bold"),
                        bg="green",
                        fg="white",
                        command=lambda p=product: self.save_edit_details_item(p, edit_name, edit_wood_type, edit_size),
                    )
                    save_button.grid(row=3, columnspan=2, pady=10)

                elif "espessura" in product:  # Produto do tipo LxE
                    ttk.Label(frame.edit_details_frame, text="Nome:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
                    edit_name = ttk.Entry(frame.edit_details_frame)
                    edit_name.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
                    edit_name.insert(0, product.get("descricao", ""))

                    ttk.Label(frame.edit_details_frame, text="Espessura:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
                    edit_thickness = ttk.Entry(frame.edit_details_frame)
                    edit_thickness.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
                    edit_thickness.insert(0, product.get("espessura", ""))

                    ttk.Label(frame.edit_details_frame, text="Largura:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
                    edit_width = ttk.Entry(frame.edit_details_frame)
                    edit_width.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
                    edit_width.insert(0, product.get("largura", ""))

                    ttk.Label(frame.edit_details_frame, text="Tipo de Madeira:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
                    edit_wood_type = ttk.Entry(frame.edit_details_frame)
                    edit_wood_type.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
                    edit_wood_type.insert(0, product.get("madeira", ""))

                    ttk.Label(frame.edit_details_frame, text="Preço por m³:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
                    edit_price_per_m3 = ttk.Entry(frame.edit_details_frame)
                    edit_price_per_m3.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
                    edit_price_per_m3.insert(0, product.get("vl_m", ""))

                    ttk.Label(frame.edit_details_frame, text="Preço de Venda:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
                    edit_sale_price = ttk.Entry(frame.edit_details_frame)
                    edit_sale_price.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)
                    edit_sale_price.insert(0, product.get("valor_venda", ""))

                    save_button = tk.Button(
                        frame.edit_details_frame,
                        text="SALVAR",
                        font=("Arial", 10, "bold"),
                        bg="green",
                        fg="white",
                        command=lambda p=product: self.save_edit_details(p, edit_name, edit_thickness, edit_width, edit_wood_type, edit_price_per_m3, edit_sale_price),
                    )
                    save_button.grid(row=6, columnspan=2, pady=10)

                else:  # Produto do tipo Item
                    ttk.Label(frame.edit_details_frame, text="Nome:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
                    edit_name = ttk.Entry(frame.edit_details_frame)
                    edit_name.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
                    edit_name.insert(0, product.get("descricao", ""))

                    ttk.Label(frame.edit_details_frame, text="Preço de Venda:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
                    edit_sale_price = ttk.Entry(frame.edit_details_frame)
                    edit_sale_price.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
                    edit_sale_price.insert(0, product.get("valor_venda", ""))

                    ttk.Label(frame.edit_details_frame, text="Preço de Compra:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
                    edit_purchase_price = ttk.Entry(frame.edit_details_frame)
                    edit_purchase_price.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
                    edit_purchase_price.insert(0, product.get("preco_compra", ""))

                    save_button = tk.Button(
                        frame.edit_details_frame,
                        text="SALVAR",
                        font=("Arial", 10, "bold"),
                        bg="green",
                        fg="white",
                        command=lambda p=product: self.save_edit_details_item(p, edit_name, edit_sale_price, edit_purchase_price),
                    )
                    save_button.grid(row=3, columnspan=2, pady=10)

            frame.edit_details_frame.pack(fill=tk.X)

    def save_edit_details_item(self, product, desc_entry, sale_price_entry, purchase_price_entry):
        product["descricao"] = desc_entry.get()
        product["valor_venda"] = float(sale_price_entry.get())
        product["preco_compra"] = float(purchase_price_entry.get())

        messagebox.showinfo("Sucesso", "Detalhes do item atualizados com sucesso!")
        self.parent.save_data()  # Save data after editing

    def save_edit_details(self, product, desc_entry, thickness_entry, width_entry, wood_type_entry, price_entry, sale_price_entry):
        product["descricao"] = desc_entry.get()
        product["madeira"] = wood_type_entry.get()
        product["valor_venda"] = float(sale_price_entry.get())

        # Update specific fields based on the product type
        product["largura"] = float(width_entry.get())
        product["espessura"] = float(thickness_entry.get())
        product["vl_m"] = float(price_entry.get())

        # Recalculate and store profit percentage
        width = product["largura"] / 100  # Convert to meters
        thickness = product["espessura"] / 100  # Convert to meters
        volume_per_m = width * thickness  # Volume for 1 meter linear
        cost_per_meter = volume_per_m * product["vl_m"]
        profit = product["valor_venda"] - cost_per_meter
        profit_percentage = (profit / cost_per_meter * 100) if cost_per_meter > 0 else 0
        product["porcentagem_lucro"] = profit_percentage  # Store profit percentage

        messagebox.showinfo("Sucesso", "Detalhes do produto atualizados com sucesso!")
        self.parent.save_data()  # Save data after editing

    def show_delete_product(self):
        self.clear_main_frame()
        self.delete_frame = tk.Frame(self.main_frame, bg="white")
        self.delete_frame.pack(fill=tk.BOTH, expand=True)

        for product in products:  # Use the global products list
            product_frame = tk.Frame(self.delete_frame, bg="white", relief=tk.RAISED, bd=1)
            product_frame.pack(fill=tk.X, padx=5, pady=2)

            # Display the product based on its type
            if "tamanho" in product:  # Produto do tipo Dz-Unid
                product_display = f"{product.get('descricao', 'N/A')} - {product.get('madeira', 'N/A')} - {product.get('tamanho', 'N/A')}"
            elif "espessura" in product:  # Produto do tipo LxE
                product_display = f"{product.get('descricao', 'N/A')} - {product.get('espessura', 'N/A')} X {product.get('largura', 'N/A')} - {product.get('madeira', 'N/A')}"
            else:  # Produto do tipo Item
                product_display = f"{product.get('descricao', 'N/A')}"

            lbl_name = tk.Label(product_frame, text=product_display, font=("Arial", 12), bg="white", anchor=tk.W)
            lbl_name.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

            btn_delete = tk.Button(
                product_frame,
                text="🗑",
                font=("Arial", 12),
                bg="red",
                fg="white",
                activebackground="darkred",
                activeforeground="white",
                command=lambda p=product: self.delete_product(p),
            )
            btn_delete.pack(side=tk.RIGHT, padx=5)

    def delete_product(self, product):
        confirm = messagebox.askyesno("Confirmar", f"Deseja excluir o produto {product['descricao']}?")
        if confirm:
            products.remove(product)
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
            self.parent.save_data()  # Save data after deleting
            self.show_delete_product()  # Refresh the delete product view

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_new_product_registration(self):
        self.clear_main_frame()
        self.new_product_frame = tk.Frame(self.main_frame, bg="white")
        self.new_product_frame.pack(fill=tk.BOTH, expand=True)

        # Create fields for new product registration
        ttk.Label(self.new_product_frame, text="Descrição:").grid(row=0, column=0, padx=10, pady=5)
        self.new_product_desc = ttk.Entry(self.new_product_frame)
        self.new_product_desc.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self.new_product_frame, text="Tipo de Madeira:").grid(row=1, column=0, padx=10, pady=5)
        self.new_product_wood_type = ttk.Entry(self.new_product_frame)
        self.new_product_wood_type.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self.new_product_frame, text="Tamanho (M):").grid(row=2, column=0, padx=10, pady=5)
        self.new_product_size = ttk.Entry(self.new_product_frame)
        self.new_product_size.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self.new_product_frame, text="Preço de Compra:").grid(row=3, column=0, padx=10, pady=5)
        self.new_product_purchase_price = ttk.Entry(self.new_product_frame)
        self.new_product_purchase_price.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(self.new_product_frame, text="Preço de Venda:").grid(row=4, column=0, padx=10, pady=5)
        self.new_product_sale_price = ttk.Entry(self.new_product_frame)
        self.new_product_sale_price.grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(self.new_product_frame, text="UN COM:").grid(row=5, column=0, padx=10, pady=5)
        self.new_product_unit_type = ttk.Entry(self.new_product_frame)
        self.new_product_unit_type.grid(row=5, column=1, padx=10, pady=5)

        # Button to register the new product
        ttk.Button(self.new_product_frame, text="Registrar Produto", command=self.register_new_product).grid(row=6, columnspan=2, pady=10)

    def register_new_product(self):
        """Register the new product with the provided details."""
        try:
            new_product = {
                "descricao": self.new_product_desc.get(),
                "madeira": self.new_product_wood_type.get(),
                "tamanho": float(self.new_product_size.get()),
                "vl_m": float(self.new_product_purchase_price.get()),
                "valor_venda": float(self.new_product_sale_price.get()),
                "un_com": self.new_product_unit_type.get(),
                "tipo": "Dz/Unid"  # Adicionando o tipo do produto
            }

            # Add the new product to the global products list
            products.append(new_product)

            messagebox.showinfo("Sucesso", f"Produto '{new_product['descricao']}' cadastrado com sucesso!")
            self.clear_new_product_fields()  # Clear fields after registration
        except ValueError:
            messagebox.showerror("Erro", "Certifique-se de que todos os campos estão preenchidos corretamente.")

    def clear_new_product_fields(self):
        """Clear the fields in the new product registration frame."""
        self.new_product_desc.delete(0, tk.END)
        self.new_product_wood_type.delete(0, tk.END)
        self.new_product_size.delete(0, tk.END)
        self.new_product_purchase_price.delete(0, tk.END)
        self.new_product_sale_price.delete(0, tk.END)
        self.new_product_unit_type.delete(0, tk.END)

class ClientsTab(ttk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_button = None
        self.parent = parent  # Store the object that manages data persistence (if any)
        self.create_widgets()

    def create_widgets(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg="white", width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.menu_buttons = {
            "Cadastrar Clientes": self.show_register_client,
            "Editar Clientes": self.show_edit_client,
            "Excluir Clientes": self.show_delete_client,
        }

        self.buttons = {}
        for idx, (label, command) in enumerate(self.menu_buttons.items()):
            btn = tk.Button(
                self.sidebar,
                text=label,
                font=("Arial", 12),
                bg="white",
                fg="black",
                activebackground="gray",
                activeforeground="white",
                command=lambda cmd=command, b=label: self.select_button(b, cmd),
            )
            btn.pack(fill=tk.X, padx=5, pady=(0 if idx == 0 else 5))
            self.buttons[label] = btn

        # Main area
        self.main_frame = tk.Frame(self, bg="white")
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Initialize with the client registration frame
        self.register_client_frame()
        self.select_button("Cadastrar Clientes", self.show_register_client)

    def select_button(self, button_label, command):
        if self.selected_button:
            self.buttons[self.selected_button].config(bg="white", fg="black")

        self.buttons[button_label].config(bg="gray", fg="white")
        self.selected_button = button_label

        # Call the associated command
        command()

    def register_client_frame(self):
        # Create the registration frame
        self.register_frame = tk.Frame(self.main_frame, bg="white")

        ttk.Label(self.register_frame, text="NOME DO CLIENTE:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.client_name = ttk.Entry(self.register_frame)
        self.client_name.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.register_frame, text="TELEFONE DO CLIENTE:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.client_phone = ttk.Entry(self.register_frame)
        self.client_phone.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.register_frame, text="CPF DO CLIENTE:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.client_cpf = ttk.Entry(self.register_frame)
        self.client_cpf.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.register_frame, text="ENDEREÇO DO CLIENTE:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.client_address = ttk.Entry(self.register_frame)
        self.client_address.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        add_button = tk.Button(
            self.register_frame,
            text="+ ADICIONAR",
            font=("Arial", 12, "bold"),
            bg="green",
            fg="white",
            activebackground="darkgreen",
            activeforeground="white",
            command=self.register_client,
        )
        add_button.grid(row=4, columnspan=2, pady=10)

    def show_register_client(self):
        self.clear_main_frame()
        self.register_client_frame()
        self.register_frame.pack(fill=tk.BOTH, expand=True)

    def show_edit_client(self):
        self.clear_main_frame()
        self.edit_frame = tk.Frame(self.main_frame, bg="white")
        self.edit_frame.pack(fill=tk.BOTH, expand=True)

        for client in clients:  # Use the global clients list
            client_frame = tk.Frame(self.edit_frame, bg="white", relief=tk.RAISED, bd=1)
            client_frame.pack(fill=tk.X, padx=5, pady=2)

            lbl_name = tk.Label(client_frame, text=client.get("name", "N/A"), font=("Arial", 12), bg="white", anchor=tk.W)
            lbl_name.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

            btn_expand = tk.Button(
                client_frame,
                text="▼",
                font=("Arial", 10),
                bg="white",
                command=lambda c=client, f=client_frame: self.toggle_edit_details(c, f),
            )
            btn_expand.pack(side=tk.RIGHT)

    def toggle_edit_details(self, client, frame):
        if hasattr(frame, "edit_details_frame") and frame.edit_details_frame.winfo_ismapped():
            frame.edit_details_frame.pack_forget()
        else:
            if not hasattr(frame, "edit_details_frame"):
                frame.edit_details_frame = tk.Frame(frame, bg="white")

                ttk.Label(frame.edit_details_frame, text="Nome:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
                edit_name = ttk.Entry(frame.edit_details_frame)
                edit_name.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
                edit_name.insert(0, client.get("name", ""))

                ttk.Label(frame.edit_details_frame, text="CPF:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
                edit_cpf = ttk.Entry(frame.edit_details_frame)
                edit_cpf.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
                edit_cpf.insert(0, client.get("cpf", ""))

                ttk.Label(frame.edit_details_frame, text="Telefone:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
                edit_phone = ttk.Entry(frame.edit_details_frame)
                edit_phone.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
                edit_phone.insert(0, client.get("phone", ""))

                ttk.Label(frame.edit_details_frame, text="Endereço:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
                edit_address = ttk.Entry(frame.edit_details_frame)
                edit_address.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
                edit_address.insert(0, client.get("address", ""))

                save_button = tk.Button(
                    frame.edit_details_frame,
                    text="Salvar",
                    font=("Arial", 10, "bold"),
                    bg="green",
                    fg="white",
                    command=lambda c=client: self.save_edit_details(c, edit_name, edit_cpf, edit_phone, edit_address)
                )
                save_button.grid(row=4, columnspan=2, pady=10)

            frame.edit_details_frame.pack(fill=tk.X)

    def save_edit_details(self, client, edit_name, edit_cpf, edit_phone, edit_address):
        client["name"] = edit_name.get()
        client["cpf"] = edit_cpf.get()
        client["phone"] = edit_phone.get()
        client["address"] = edit_address.get()
        messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
        self.parent.save_data()  # Save data after editing

    def show_delete_client(self):
        self.clear_main_frame()
        self.delete_frame = tk.Frame(self.main_frame, bg="white")
        self.delete_frame.pack(fill=tk.BOTH, expand=True)

        for client in clients:  # Use the global clients list
            client_frame = tk.Frame(self.delete_frame, bg="white", relief=tk.RAISED, bd=1)
            client_frame.pack(fill=tk.X, padx=5, pady=2)

            lbl_name = tk.Label(client_frame, text=client.get("name", "N/A"), font=("Arial", 12), bg="white", anchor=tk.W)
            lbl_name.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

            btn_delete = tk.Button(client_frame, text="Excluir", font=("Arial", 10), bg="red", fg="white", command=lambda c=client: self.delete_client(c))
            btn_delete.pack(side=tk.RIGHT)

    def delete_client(self, client):
        confirm = messagebox.askyesno("Confirmar", f"Deseja excluir o cliente {client['name']}?")
        if confirm:
            clients.remove(client)
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
            self.show_delete_client()  # Refresh the delete client view

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def register_client(self):
        try:
            # Retrieve input values
            client_name = self.client_name.get()
            client_phone = self.client_phone.get()
            client_cpf = self.client_cpf.get()
            client_address = self.client_address.get()

            # Validate required fields
            if not client_name or not client_phone or not client_cpf or not client_address:
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
                return

            # Create a new client
            new_client = {
                "name": client_name,
                "cpf": client_cpf,
                "phone": client_phone,
                "address": client_address,
                "movements": [],
            }

            # Add the client to the global clients list
            clients.append(new_client)

            # Notify the user
            messagebox.showinfo("Sucesso", f"Cliente '{client_name}' cadastrado com sucesso!")

            # Clear input fields
            self.clear_fields()  # Clear fields after registration

            # Update NotesTab with the new client
            self.parent.update_notes_tab_with_new_client(new_client)

            # Save persistent data
            self.parent.save_data()  # Ensure this line is called correctly

        except ValueError:
            messagebox.showerror("Erro", "Certifique-se de que os campos numéricos estão preenchidos corretamente.")

    def clear_fields(self):
        self.client_name.delete(0, tk.END)
        self.client_phone.delete(0, tk.END)
        self.client_cpf.delete(0, tk.END)
        self.client_address.delete(0, tk.END)

class NotesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_button = None
        self.parent = parent
        self.create_widgets()
        self.invoice_items = []  # Store invoice items temporarily
        self.load_invoice_data()  # Load existing invoice data on initialization

    def create_widgets(self):
        # Menu lateral
        self.sidebar = tk.Frame(self, bg="white", width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.menu_buttons = {
            "Criar Nota": self.show_create_note,
            "Duzia": self.show_duzia,
            "Item": self.show_item,
            "Notas": self.show_notas,  # New button for Notas
            "Visualizar PDFs": self.show_pdf_viewer,
        }

        self.buttons = {}
        for idx, (label, command) in enumerate(self.menu_buttons.items()):
            btn = tk.Button(
                self.sidebar,
                text=label,
                font=("Arial", 12),
                bg="white",
                fg="black",
                activebackground="gray",
                activeforeground="white",
                command=lambda cmd=command, b=label: self.select_button(b, cmd),
            )
            btn.pack(fill=tk.X, padx=5, pady=(0 if idx == 0 else 5))
            self.buttons[label] = btn

        # Área central
        self.main_frame = tk.Frame(self, bg="white")
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Inicializa com o frame de criar nota
        self.create_note_frame()
        self.select_button("Criar Nota", self.show_create_note)

    def select_button(self, button_label, command):
        if self.selected_button:
            self.buttons[self.selected_button].config(bg="white", fg="black")

        self.buttons[button_label].config(bg="gray", fg="white")
        self.selected_button = button_label

        # Chama o comando associado
        command()

    def show_create_note(self):
        """Show the create note frame."""
        self.clear_main_frame()
        self.create_note_frame()
        self.create_frame.pack(fill=tk.BOTH, expand=True)

    def show_duzia(self):
        """Show the duzia frame with product selection and pricing."""
        self.clear_main_frame()
        self.duzia_frame = tk.Frame(self.main_frame, bg="white")
        self.duzia_frame.pack(fill=tk.BOTH, expand=True)

        # Product selection
        ttk.Label(self.duzia_frame, text="Selecione o Produto:").grid(row=0, column=0, padx=5, pady=5)
        self.product_entry = ttk.Entry(self.duzia_frame)
        self.product_entry.grid(row=0, column=1, padx=5, pady=5)
        self.product_entry.bind("<Return>", self.confirm_product_duzia)

        self.size_entry = ttk.Entry(self.duzia_frame)
        self.size_entry.insert(0, "2.2")  # Pre-fill size
        self.size_entry.grid(row=0, column=2, padx=5, pady=5)

        # Quantidade input
        ttk.Label(self.duzia_frame, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5)
        self.quantity_entry_duzia = ttk.Entry(self.duzia_frame)
        self.quantity_entry_duzia.grid(row=1, column=1, padx=5, pady=5)

        # Unit type selection
        ttk.Label(self.duzia_frame, text="Tipo de Unidade:").grid(row=2, column=0, padx=5, pady=5)
        self.unit_type_combobox = ttk.Combobox(self.duzia_frame, values=["DUZIA", "UNIDADE"])
        self.unit_type_combobox.current(0)  # Default to DUZIA
        self.unit_type_combobox.grid(row=2, column=1, padx=5, pady=5)

        # Button to add product
        self.btn_add_product = ttk.Button(self.duzia_frame, text="Adicionar Produto", command=self.add_product_to_invoice_duzia)
        self.btn_add_product.grid(row=3, columnspan=2, pady=10)

        # Button to remove product
        self.btn_remove_product = ttk.Button(self.duzia_frame, text="Remover Produto", command=self.remove_product_from_invoice)
        self.btn_remove_product.grid(row=3, column=2, pady=10)

        self.invoice_table = ttk.Treeview(self.duzia_frame, columns=("Produto", "Quantidade", "UN COM.", "Valor por Unidade", "Valor por Duzia", "Valor Total", "Lucro Total"), show='headings')
        self.invoice_table.heading("Produto", text="Produto Descrição")
        self.invoice_table.heading("Quantidade", text="Qtd")
        self.invoice_table.heading("UN COM.", text="UN COM.")
        self.invoice_table.heading("Valor por Unidade", text="Vlr Un")
        self.invoice_table.heading("Valor por Duzia", text="Vlr Dz")
        self.invoice_table.heading("Valor Total", text="Vlr Total")
        self.invoice_table.heading("Lucro Total", text="Lucro Total")
        self.invoice_table.grid(row=4, columnspan=3, sticky='nsew')

        # Configure grid weights for resizing
        self.duzia_frame.grid_rowconfigure(4, weight=1)  # Allow the invoice table to expand
        self.duzia_frame.grid_columnconfigure(1, weight=1)  # Allow the product entry to expand

        # Button to save products in the duzia frame
        self.btn_save_duzia_products = ttk.Button(self.duzia_frame, text="Salvar Produtos", command=self.save_duzia_products_to_json)
        self.btn_save_duzia_products.grid(row=5, columnspan=3, pady=10)

        # Button to generate PDF
        self.btn_generate_pdf = ttk.Button(self.duzia_frame, text="Gerar Nota", command=self.gerar_pdf)
        self.btn_generate_pdf.grid(row=6, columnspan=3, pady=10)

        # Bind double-click event to edit values
        self.invoice_table.bind("<Double-1>", self.on_invoice_duzia_double_click)

    def add_product_to_invoice_duzia(self):
        selected_product = self.product_entry.get()
        size = self.size_entry.get()
        quantity = simpledialog.askinteger("Quantidade", "Digite a quantidade:")

        if not selected_product or not size or quantity is None or quantity <= 0:
            messagebox.showwarning("Erro", "Selecione um produto, informe o tamanho e a quantidade.")
            return

        # Find the product details from the products list
        product_details = next((p for p in products if f"{p['descricao']} - {p['madeira']}" == selected_product), None)
        if product_details:
            unit_type = self.unit_type_combobox.get()
            if unit_type == "DUZIA":
                price_per_dz = product_details["valor_venda"]  # Selling price for a dozen
                price_per_unit = price_per_dz / 12  # Price per unit
                profit_total = (price_per_dz - product_details["vl_m"]) * quantity  # Total profit
                total_value = price_per_dz * quantity  # Total value for the quantity

                # Insert into the invoice table
                self.invoice_table.insert("", "end", values=(f"{selected_product} {size}M", quantity, "DUZIA", f"R$ {price_per_unit:.2f}", f"R$ {price_per_dz:.2f}", f"R$ {total_value:.2f}", f"R$ {profit_total:.2f}"))
            else:  # UNIDADE
                price_per_unit = product_details["valor_venda"]  # Selling price for a unit
                total_value = price_per_unit * quantity  # Total value for the quantity
                profit_total = (price_per_unit - product_details["vl_m"]) * quantity  # Total profit

                # Insert into the invoice table
                self.invoice_table.insert("", "end", values=(f"{selected_product} {size}M", quantity, "UNIDADE", f"R$ {price_per_unit:.2f}", "R$ 0.00", f"R$ {total_value:.2f}", f"R$ {profit_total:.2f}"))
        else:
            messagebox.showwarning("Erro", "Produto não encontrado!")
            
    def show_pdf_viewer(self):
        """Exibe a frame para visualizar PDFs de notas e movimentos dos clientes."""
        self.clear_main_frame()  # Limpa a frame principal

        self.pdf_frame = tk.Frame(self.main_frame, bg="white")
        self.pdf_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.pdf_frame, text="Clientes e Movimentos", font=("Arial", 14)).pack(pady=10)
        
        # Listar todos os clientes
        for client in clients:
            self.create_client_frame(client)

    def create_client_frame(self, client):
        """Cria um retângulo para exibir informações do cliente e seus movimentos."""
        client_frame = tk.Frame(self.pdf_frame, bg="white", relief=tk.RAISED, bd=2)
        client_frame.pack(fill=tk.X, padx=5, pady=5)

        lbl_name = tk.Label(client_frame, text=client.get("name", "N/A"), font=("Arial", 12), bg="white", anchor=tk.W)
        lbl_name.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        btn_toggle = tk.Button(
            client_frame,
            text="▼",
            font=("Arial", 10),
            bg="white",
            command=lambda c=client, cf=client_frame: self.toggle_movements(c, cf),
        )
        btn_toggle.pack(side=tk.RIGHT, padx=5)

        # Cria o frame de movimentos inicialmente oculto
        client_frame.movements_frame = tk.Frame(client_frame, bg="white")
        client_frame.movements_frame.pack(fill=tk.X, padx=10, pady=5)
        client_frame.movements_frame.pack_forget()  # Esconde o frame de movimentos inicialmente

        return client_frame

    def toggle_movements(self, client, client_frame):
        """Exibe ou oculta os movimentos do cliente selecionado."""
        if client_frame.movements_frame.winfo_ismapped():
            client_frame.movements_frame.pack_forget()  # Esconde os movimentos
            client_frame.configure(height=50)  # Reduz o tamanho do retângulo
        else:
            if not hasattr(client_frame, "movements_frame"):
                client_frame.movements_frame = tk.Frame(self.pdf_frame, bg="white")

            # Limpa os movimentos anteriores
            for widget in client_frame.movements_frame.winfo_children():
                widget.destroy()

            # Define o caminho para a pasta de movimentos do cliente
            cliente_nome = client.get("name", "N/A")
            cliente_inicial = cliente_nome[0].upper()  # Primeira letra do nome do cliente em maiúscula
            client_folder = os.path.join("notas", cliente_inicial, cliente_nome.replace(" ", "_"))

            # Verifica se a pasta do cliente existe
            if not os.path.exists(client_folder):
                messagebox.showwarning("Aviso", f"Nenhuma pasta encontrada para o cliente '{cliente_nome}'.")
                return

            # Lista todos os arquivos PDF na pasta do cliente
            pdf_files = [f for f in os.listdir(client_folder) if f.endswith('.pdf')]

            if not pdf_files:
                messagebox.showinfo("Informação", f"Nenhum movimento encontrado para o cliente '{cliente_nome}'.")
                return

            # Adiciona cada movimento como um rótulo, botão e botão de exclusão
            for pdf_file in pdf_files:
                movement_frame = tk.Frame(client_frame.movements_frame, bg="white")
                movement_frame.pack(fill=tk.X, padx=5, pady=2)

                # Extrai o valor total e a data do PDF
                total_value, date = self.extract_value_from_pdf(os.path.join(client_folder, pdf_file))

                # Cria o rótulo com a data e o valor total
                movement_label = tk.Label(movement_frame, text=f"{date} - R$ {total_value:.2f}", font=("Arial", 10), bg="white", anchor=tk.W)
                movement_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

                # Botão para abrir o PDF correspondente
                pdf_button = ttk.Button(movement_frame, text="Abrir PDF", command=lambda p=os.path.join(client_folder, pdf_file): self.open_pdf(p))
                pdf_button.pack(side=tk.RIGHT, padx=5)

                # Botão para excluir o movimento
                delete_button = ttk.Button(movement_frame, text="🗑", command=lambda f=pdf_file: self.delete_movement(cliente_nome, f))
                delete_button.pack(side=tk.RIGHT, padx=5)

            # Empacota o frame de movimentos diretamente abaixo do nome do cliente
            client_frame.movements_frame.pack(fill=tk.X)  # Exibe os movimentos
            client_frame.configure(height=200)  # Ajusta a altura do frame do cliente
            
    def delete_movement(self, cliente_nome, pdf_file):
        """Remove o movimento e atualiza o estoque e relatórios."""
        cliente_inicial = cliente_nome[0].upper()
        client_folder = os.path.join("notas", cliente_inicial, cliente_nome.replace(" ", "_"))

        # Remove o PDF
        pdf_path = os.path.join(client_folder, pdf_file)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            messagebox.showinfo("Sucesso", f"Movimento '{pdf_file}' excluído com sucesso!")
        else:
            messagebox.showwarning("Erro", "Arquivo não encontrado.")
       

    def extract_value_from_pdf(self, pdf_path):
        """Extrai o valor total e a data do PDF."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                first_page = pdf.pages[0]  # Get the first page
                text = first_page.extract_text()  # Extract text from the page

                # Initialize variables to hold extracted data
                total_value = 0.0
                date = "Data não encontrada"

                # Process the text to find the total value and date
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    line = line.strip()  # Remove leading/trailing whitespace

                    # Look for the line containing "Total"
                    if "Total" in line:
                        try:
                            total_value = float(line.split("R$")[-1].strip().replace(",", "."))
                        except ValueError:
                            print(f"Erro ao converter o valor: {line}")  # Debugging output
                            total_value = 0.0  # Reset to 0 if conversion fails

                    # Check for the line that contains "Data Pgto"
                    if "Data Pgto" in line:
                        # The date is usually in the next line
                        if i + 1 < len(lines):
                            # Use regex to find the date in the next line
                            date_match = re.search(r'\d{2}/\d{2}/\d{4}', lines[i + 1])
                            if date_match:
                                date = date_match.group(0)  # Extract the date

                return total_value, date  # Return the extracted date and total value
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível extrair o valor do PDF: {e}")
            return 0.0, "Erro"  # Return 0 and error message if there's an error

    def calculate_total_value_for_client(self, client):
        """Calcula o valor total para o cliente."""
        # Aqui você deve implementar a lógica para calcular o valor total dos movimentos do cliente
        # Por exemplo, somando os valores dos PDFs associados ao cliente
        total = 0.0
        cliente_nome = client.get("name", "N/A")
        cliente_inicial = cliente_nome[0].upper()
        client_folder = os.path.join("notas", cliente_inicial, cliente_nome.replace(" ", "_"))

        if os.path.exists(client_folder):
            pdf_files = [f for f in os.listdir(client_folder) if f.endswith('.pdf')]
            for pdf_file in pdf_files:
                # Aqui você pode implementar a lógica para extrair o valor do PDF
                # Por exemplo, se você tiver um método para ler o PDF e obter o valor
                # total += self.extract_value_from_pdf(os.path.join(client_folder, pdf_file))

                # Para fins de exemplo, vamos adicionar um valor fixo
                total += 100.0  # Substitua isso pela lógica real

        return total




    def open_pdf(self, pdf_file):
        """Abre o PDF selecionado."""
        try:
            webbrowser.open(pdf_file)  # Abre o PDF no navegador padrão
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o PDF: {e}") 

    def show_item(self):
        """Show the item frame with product selection and pricing."""
        self.clear_main_frame()
        self.item_frame = tk.Frame(self.main_frame, bg="white")
        self.item_frame.pack(fill=tk.BOTH, expand=True)

        # Product selection
        ttk.Label(self.item_frame, text="Selecione o Item:").grid(row=0, column=0, padx=5, pady=5)
        self.product_entry = ttk.Entry(self.item_frame)
        self.product_entry.grid(row=0, column=1, padx=5, pady=5)
        self.product_entry.bind("<Return>", self.confirm_product_item)

        # Quantity input
        ttk.Label(self.item_frame, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(self.item_frame)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        # Button to add product
        self.btn_add_product = ttk.Button(self.item_frame, text="Adicionar Produto", command=self.add_product_to_invoice_item)
        self.btn_add_product.grid(row=2, columnspan=2, pady=10)

        # Create the invoice item table
        self.invoice_item_table = ttk.Treeview(self.item_frame, columns=("Produto", "Quantidade", "UN COM.", "Valor por Unidade", "Valor Total", "Lucro Total"), show='headings')
        self.invoice_item_table.heading("Produto", text="Produto Descrição")
        self.invoice_item_table.heading("Quantidade", text="Qtd")
        self.invoice_item_table.heading("UN COM.", text="UN COM.")
        self.invoice_item_table.heading("Valor por Unidade", text="Vlr Un")
        self.invoice_item_table.heading("Valor Total", text="Vlr Total")
        self.invoice_item_table.heading("Lucro Total", text="Lucro Total")
        self.invoice_item_table.grid(row=3, columnspan=3, sticky='nsew')

        # Configure grid weights for resizing
        self.item_frame.grid_rowconfigure(3, weight=1)  # Allow the invoice table to expand
        self.item_frame.grid_columnconfigure(1, weight=1)  # Allow the product entry to expand

        # Button to save products in the item frame
        self.btn_save_item_products = ttk.Button(self.item_frame, text="Salvar Produtos", command=self.save_item_products_to_json)
        self.btn_save_item_products.grid(row=4, columnspan=3, pady=10)

        # Button to generate PDF
        self.btn_generate_pdf = ttk.Button(self.item_frame, text="Gerar Nota", command=self.gerar_pdf)
        self.btn_generate_pdf.grid(row=5, columnspan=3, pady=10)

        # Bind double-click event to edit values
        self.invoice_item_table.bind("<Double-1>", self.on_item_double_click)

    def add_product_to_invoice_item(self):
        selected_product = self.product_entry.get()
        quantity = self.quantity_entry.get()

        if not selected_product or not quantity.isdigit() or int(quantity) <= 0:
            messagebox.showwarning("Erro", "Selecione um produto e informe a quantidade válida.")
            return

        quantity = int(quantity)

        # Buscar diretamente pelo produto selecionado
        product_details = next((p for p in products if p['descricao'].strip() == selected_product.strip()), None)

        if product_details:
            price_per_unit = product_details["valor_venda"]  # Preço de venda por unidade
            purchase_price = product_details["preco_compra"]  # Preço de compra
            total_value = price_per_unit * quantity  # Valor total pela quantidade
            profit_total = (price_per_unit - purchase_price) * quantity  # Lucro total

            # Inserir na tabela de itens da fatura
            self.invoice_item_table.insert("", "end", values=(
                f"{selected_product}", quantity, "UNIDADE", f"R$ {price_per_unit:.2f}", 
                f"R$ {total_value:.2f}", f"R$ {profit_total:.2f}"
            ))
        else:
            messagebox.showwarning("Erro", "Produto não encontrado!")




    def show_notas(self):
        """Exibe a interface de notas com cliente, vendedor e tabelas de faturas."""
        self.clear_main_frame()

        # Criação do Frame principal
        self.notas_frame = tk.Frame(self.main_frame, bg="white")
        self.notas_frame.pack(fill=tk.BOTH, expand=True)

        # Seção: Cliente e Vendedor
        self.client_vendor_frame = ttk.LabelFrame(self.notas_frame, text="Cliente e Vendedor", padding=10)
        self.client_vendor_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        ttk.Label(self.client_vendor_frame, text="Digite o Nome do Cliente:").grid(row=0, column=0, padx=5)
        self.client_entry = ttk.Entry(self.client_vendor_frame)
        self.client_entry.grid(row=0, column=1, padx=5)
        self.client_entry.bind("<Return>", self.confirm_client)  # Bind the Enter key to confirm client

        ttk.Label(self.client_vendor_frame, text="Vendedor:").grid(row=0, column=2, padx=5)
        self.vendor_entry = ttk.Entry(self.client_vendor_frame)
        self.vendor_entry.insert(0, "EVERSON")
        self.vendor_entry.config(state='readonly')
        self.vendor_entry.grid(row=0, column=3, padx=5)

        # Seção: Pagamento
        self.payment_frame = ttk.LabelFrame(self.notas_frame, text="Pagamento", padding=10)
        self.payment_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        ttk.Label(self.payment_frame, text="Forma de Pagamento:").grid(row=0, column=0, padx=5)
        self.payment_method_entry = ttk.Entry(self.payment_frame)
        self.payment_method_entry.insert(0, "DINHEIRO")
        self.payment_method_entry.config(state='readonly')
        self.payment_method_entry.grid(row=0, column=1, padx=5)

        ttk.Label(self.payment_frame, text="Condição de Pagamento:").grid(row=0, column=2, padx=5)
        self.payment_condition_combobox = ttk.Combobox(self.payment_frame, values=["A VISTA", "A PRAZO (30 DIAS)"])
        self.payment_condition_combobox.grid(row=0, column=3, padx=5)

        # Botão: Gerar Nota
        self.btn_generate_pdf = ttk.Button(self.notas_frame, text="Gerar Nota", command=self.gerar_pdf)
        self.btn_generate_pdf.grid(row=2, column=0, columnspan=2, pady=15)

        # Criação das tabelas de faturas
        self.create_invoice_tables()

        # Configurar peso para as linhas e colunas
        self.notas_frame.grid_rowconfigure(3, weight=1)  # Invoice Unidade
        self.notas_frame.grid_rowconfigure(4, weight=1)  # Invoice Duzia
        self.notas_frame.grid_rowconfigure(5, weight=1)  # Invoice Item
        self.notas_frame.grid_rowconfigure(6, weight=0)  # Botão "Remover Produto"
        self.notas_frame.grid_columnconfigure(0, weight=1)

    def confirm_client(self, event):
        """Confirma o cliente digitado na caixa de entrada."""
        client_name = self.client_entry.get().strip()
        matched_clients = [client for client in clients if client_name.lower() in client.get("name", "").lower()]

        if len(matched_clients) == 1:
            self.client_entry.delete(0, tk.END)
            self.client_entry.insert(0, matched_clients[0]["name"])  # Set the selected client name in the entry
        elif len(matched_clients) > 1:
            self.show_selection_window("Selecione o Cliente", matched_clients)
        else:
            messagebox.showwarning("Erro", "Cliente não encontrado!")

    def show_selection_window(self, title, options):
        top = tk.Toplevel(self)
        top.title(title)

        listbox = tk.Listbox(top, height=10, width=50)
        for option in options:
            listbox.insert(tk.END, option["name"])  # Display the client names

        listbox.pack(padx=10, pady=10)
        select_button = tk.Button(top, text="Selecionar", command=lambda: self.select_from_listbox(listbox))
        select_button.pack(pady=5)

    def select_from_listbox(self, listbox):
        selected_index = listbox.curselection()
        if selected_index:
            selected_item = listbox.get(selected_index)
            self.client_entry.delete(0, tk.END)
            self.client_entry.insert(0, selected_item)  # Set the selected client in the entry
        listbox.master.destroy()

    def create_invoice_tables(self):
        """Cria as tabelas de faturas (unidade, dúzia e item)."""

        # Tabela: Invoice Unidade
        self.invoice_unidade_frame = ttk.LabelFrame(self.notas_frame, text="Invoice Unidade", padding=5)
        self.invoice_unidade_frame.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')

        self.invoice_unidade_table = ttk.Treeview(self.invoice_unidade_frame, columns=(
            "Produto", "Quantidade", "UN COM.", "Valor por Metro", "Valor Unitário",
            "Valor Total", "Lucro Total", "Volume Total"), show='headings')

        for col in self.invoice_unidade_table["columns"]:
            self.invoice_unidade_table.heading(col, text=col)
            self.invoice_unidade_table.column(col, anchor="center", width=100)

        self.invoice_unidade_table.pack(fill=tk.BOTH, expand=True)

        # Tabela: Invoice Duzia
        self.invoice_duzia_frame = ttk.LabelFrame(self.notas_frame, text="Invoice Duzia", padding=10)
        self.invoice_duzia_frame.grid(row=4, column=0, padx=10, pady=10, sticky='nsew')

        self.invoice_duzia_table = ttk.Treeview(self.invoice_duzia_frame, columns=(
            "Produto", "Quantidade", "UN COM.", "Valor por Unidade", "Valor por Duzia",
            "Valor Total", "Lucro Total"), show='headings')

        for col in self.invoice_duzia_table["columns"]:
            self.invoice_duzia_table.heading(col, text=col)
            self.invoice_duzia_table.column(col, anchor="center", width=100)

        self.invoice_duzia_table.pack(fill=tk.BOTH, expand=True)

        # Tabela: Invoice Item
        self.invoice_item_frame = ttk.LabelFrame(self.notas_frame, text="Invoice Item", padding=10)
        self.invoice_item_frame.grid(row=5, column=0, padx=10, pady=10, sticky='nsew')

        self.invoice_item_table = ttk.Treeview(self.invoice_item_frame, columns=(
            "Produto", "Quantidade", "UN COM.", "Valor por Unidade", "Valor Total", "Lucro Total"), show='headings')

        for col in self.invoice_item_table["columns"]:
            self.invoice_item_table.heading(col, text=col)
            self.invoice_item_table.column(col, anchor="center", width=100)

        self.invoice_item_table.pack(fill=tk.BOTH, expand=True)

        # Botão: Remover Produto
        self.btn_remove_product = ttk.Button(self.notas_frame, text="Remover Produto", command=self.remove_product_from_invoice)
        self.btn_remove_product.grid(row=6, column=0, pady=10)

        # Carregar dados do JSON
        self.load_invoices_from_json()


    def load_invoices_from_json(self):
        """Load invoices from nota.json and populate the tables."""
        try:
            with open('nota.json', 'r') as json_file:
                data = json.load(json_file)

            # Limpar tabelas antes de carregar novos dados
            for table in [self.invoice_unidade_table, self.invoice_duzia_table, self.invoice_item_table]:
                table.delete(*table.get_children())

            # Load nota_unidade
            for product in data.get("nota_unidade", []):
                self.invoice_unidade_table.insert("", "end", values=(
                    product.get("produto", "N/A"),
                    product.get("quantidade", 0),
                    product.get("un_com", "N/A"),
                    product.get("vl_m", 0.0),
                    product.get("vlr_un", 0.0),
                    product.get("vlr_total", 0.0),
                    product.get("lucro_total", 0.0),
                    product.get("volume_total", 0.0)
                ))

            # Load nota_duzia
            for product in data.get("nota_duzia", []):
                self.invoice_duzia_table.insert("", "end", values=(
                    product.get("produto", "N/A"),
                    product.get("quantidade", 0),
                    product.get("un_com", "N/A"),
                    product.get("vlr_uni", 0.0),
                    product.get("vlr_dz", 0.0),
                    product.get("vlr_total", 0.0),
                    product.get("lucro_total", 0.0)
                ))

            # Load nota_item
            for product in data.get("nota_item", []):
                self.invoice_item_table.insert("", "end", values=(
                    product.get("produto", "N/A"),
                    product.get("quantidade", 0),
                    product.get("un_com", "N/A"),
                    product.get("vlr_uni", 0.0),
                    product.get("vlr_total", 0.0),
                    product.get("lucro_total", 0.0)
                ))

        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showwarning("Aviso", "Nenhum dado encontrado para carregar.")



    

    def add_product_to_invoice_duzia(self):
        selected_product = self.product_entry.get()
        size = self.size_entry.get()
    
        # Obter a quantidade diretamente do campo de entrada
        quantity_str = self.quantity_entry_duzia.get()  # Supondo que você tenha um campo de entrada para quantidade

        # Verificar se a quantidade é um número válido
        try:
            quantity = int(quantity_str)
        except ValueError:
            messagebox.showwarning("Erro", "Por favor, insira uma quantidade válida.")
            return

        if not selected_product or not size or quantity <= 0:
            messagebox.showwarning("Erro", "Selecione um produto, informe o tamanho e a quantidade.")
            return

        # Find the product details from the products list
        product_details = next((p for p in products if 'descricao' in p and 'madeira' in p and 'tipo' in p and p['tipo'] == "Dz/Unid" and f"{p['descricao']} - {p['madeira']}" == selected_product), None)
        if product_details:
            unit_type = self.unit_type_combobox.get()
            if unit_type == "DUZIA":
                price_per_dz = product_details["valor_venda"]  # Selling price for a dozen
                price_per_unit = price_per_dz / 12  # Price per unit
                profit_total = (price_per_dz - product_details["vl_m"]) * quantity  # Total profit
                total_value = price_per_dz * quantity  # Total value for the quantity

                # Insert into the invoice table
                self.invoice_table.insert("", "end", values=(f"{selected_product} {size}M", quantity, "DUZIA", f"R$ {price_per_unit:.2f}", f"R$ {price_per_dz:.2f}", f"R$ {total_value:.2f}", f"R$ {profit_total:.2f}"))
            else:  # UNIDADE
                price_per_unit = product_details["valor_venda"] /12  # Selling price for a unit
                total_value = price_per_unit * quantity  # Total value for the quantity
                profit_total = (price_per_unit - (product_details["vl_m"] / 12)) * quantity  # Total profit

                # Insert into the invoice table
                self.invoice_table.insert("", "end", values=(f"{selected_product} {size}M", quantity, "UNIDADE", f"R$ {price_per_unit:.2f}", "R$ 0.00", f"R$ {total_value:.2f}", f"R$ {profit_total:.2f}"))
        else:
            messagebox.showwarning("Erro", "Produto não encontrado!")

    def remove_product_from_invoice(self):
        selected_item = self.invoice_table.selection()
        if not selected_item:
            messagebox.showwarning("Erro", "Selecione um produto para remover.")
            return

        for item in selected_item:
            self.invoice_table.delete(item)

        messagebox.showinfo("Sucesso", "Produto removido da fatura com sucesso.")

    def add_product_to_invoice_item(self):
        selected_product = self.product_entry.get()
        quantity = self.quantity_entry.get()

        if not selected_product or not quantity.isdigit() or int(quantity) <= 0:
            messagebox.showwarning("Erro", "Selecione um produto e informe a quantidade válida.")
            return

        quantity = int(quantity)

        # Buscar diretamente pelo produto selecionado
        product_details = next((p for p in products if p['descricao'].strip() == selected_product.strip()), None)

        if product_details:
            price_per_unit = product_details["valor_venda"]  # Preço de venda por unidade
            purchase_price = product_details["preco_compra"]  # Preço de compra
            total_value = price_per_unit * quantity  # Valor total pela quantidade
            profit_total = (price_per_unit - purchase_price) * quantity  # Lucro total

            # Inserir na tabela de itens da fatura
            self.invoice_item_table.insert("", "end", values=(
                f"{selected_product}", quantity, "UNIDADE", f"R$ {price_per_unit:.2f}", 
                f"R$ {total_value:.2f}", f"R$ {profit_total:.2f}"
            ))
        else:
            messagebox.showwarning("Erro", "Produto não encontrado!")

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_note_frame(self):
        # Frame para criar nota
        self.create_frame = tk.Frame(self.main_frame, bg="white")
        

        # Product selection
        self.product_details_frame = ttk.LabelFrame(self.create_frame, text="Detalhes do Produto", padding=10)
        self.product_details_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Selecionar Produto
        ttk.Label(self.product_details_frame, text="Selecione o Produto:").grid(row=0, column=0, padx=5, pady=5)
        self.product_entry = ttk.Entry(self.product_details_frame)  # Use Entry instead of Combobox
        self.product_entry.grid(row=0, column=1, padx=5, pady=5)
        self.product_entry.bind("<Return>", self.confirm_product)  # Bind the Enter key to confirm product
        # Tamanho (m)
        ttk.Label(self.product_details_frame, text="Tamanho (m):").grid(row=0, column=2, padx=5, pady=5)
        self.size_entry = ttk.Entry(self.product_details_frame)
        self.size_entry.grid(row=0, column=3, padx=5, pady=5)

        # Quantidade input
        ttk.Label(self.product_details_frame, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(self.product_details_frame)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        # Botão Adicionar Produto
        self.btn_add_product = ttk.Button(self.product_details_frame, text="Adicionar Produto", command=self.add_product_to_invoice)
        self.btn_add_product.grid(row=2, column=2, columnspan=2, pady=10)

        self.btn_remove_product = ttk.Button(self.product_details_frame, text="Remover Produto", command=self.remove_product_from_invoice)
        self.btn_remove_product.grid(row=2, column=3, pady=10)

        # Button to generate invoice
        self.btn_generate_invoice = ttk.Button(self.create_frame, text="Gerar Nota", command=self.gerar_pdf)
        self.btn_generate_invoice.grid(row=7, columnspan=2, pady=10)

        # Button to save products
        self.btn_save_products = ttk.Button(self.create_frame, text="Salvar Produtos", command=self.save_products_to_json)
        self.btn_save_products.grid(row=8, columnspan=2, pady=10)

        # Table to display added products (invoice table)
        self.invoice_table = ttk.Treeview(self.create_frame, columns=("Produto", "Quantidade", "UN COM.", "Valor por Metro", "Valor Unitário", "Valor Total", "Lucro Total", "Volume Total"), show='headings')
        self.invoice_table.heading("Produto", text="Produto Descrição")
        self.invoice_table.heading("Quantidade", text="Qtd")
        self.invoice_table.heading("UN COM.", text="UN COM.")
        self.invoice_table.heading("Valor por Metro", text="Vlr por Metro")
        self.invoice_table.heading("Valor Unitário", text="Vlr Un")
        self.invoice_table.heading("Valor Total", text="Vlr Total")
        self.invoice_table.heading("Lucro Total", text="Lucro Total")
        self.invoice_table.heading("Volume Total", text="Volume (m³)")
        self.invoice_table.grid(row=9, columnspan=2, sticky='nsew')
        
        self.invoice_table.bind("<Double-1>", self.on_invoice_double_click)

        # Configure grid weights for resizing
        self.create_frame.grid_rowconfigure(9, weight=1)  # Allow the invoice table to expand
        
    def on_invoice_double_click(self, event):
        item = self.invoice_table.selection()[0]
        column = self.invoice_table.identify_column(event.x)
        column_index = int(column.replace("#", "")) - 1

        if column_index in [3, 4]:  # Check if the clicked column is "Valor por Metro" or "Valor Unitário"
            current_value = self.invoice_table.item(item)["values"][column_index]
            new_value = simpledialog.askfloat("Editar Valor", f"Novo valor para {self.invoice_table.heading(column)['text']}:",
                                                initialvalue=float(current_value.replace("R$", "").replace(",", ".")))

            if new_value is not None:
                self.invoice_table.item(item, values=self.update_invoice_values(item, column_index, new_value))

    def update_invoice_values(self, item, column_index, new_value):
        values = list(self.invoice_table.item(item)["values"])
        quantity = int(values[1])
        size = float(self.size_entry.get())
        product_description = values[0]

        if column_index == 3:  # Valor por Metro
            old_total_value = float(values[5][3:].replace(",", "."))
            old_profit = float(values[6][3:].replace(",", "."))

            values[3] = f"R$ {new_value:.2f}"

            total_value = new_value * size
            values[4] = f"R$ {total_value:.2f}"  # Update Valor Unitário based on new price per meter
            new_total_value = total_value * quantity
            values[5] = f"R$ {new_total_value:.2f}"

            lucro_total = old_profit + (new_total_value - old_total_value)
            values[6] = f"R$ {lucro_total:.2f}"

        elif column_index == 4:  # Valor Unitário
            old_total_value = float(values[5][3:].replace(",", "."))
            old_profit = float(values[6][3:].replace(",", "."))

            values[4] = f"R$ {new_value:.2f}"  # Keep "R$" for Unitário

            # Update total value based on new price per unit
            total_value = new_value * quantity
            new_total_value = total_value
            lucro_total = old_profit + (new_total_value - old_total_value)
            vlr_un = new_value / size
            values[5] = f"R$ {new_total_value:.2f}"
            values[3] = f"R$ {vlr_un:.2f}"  # Keep "R$" for price per meter
            values[6] = f"R$ {lucro_total:.2f}"

        return values    

    def load_invoice_data(self):
        """Load invoice data from nota.json and populate the tables."""
        try:
            with open('nota.json', 'r') as json_file:
                data = json.load(json_file)

            # Load UNIDADE products
            for product in data.get("nota_unidade", []):
                self.invoice_table.insert("", "end", values=(
                    product.get("produto", "N/A"),
                    product.get("quantidade", 0),
                    product.get("un_com", "N/A"),
                    product.get("vl_m", 0.0),
                    product.get("vlr_un", 0.0),
                    product.get("vlr_total", 0.0),
                    product.get("lucro_total", 0.0),
                    product.get("volume_total", 0.0)
                ))

            # Load nota_duzia
            for product in data.get("nota_duzia", []):
                self.invoice_table.insert("", "end", values=(
                    product.get("produto", "N/A"),
                    product.get("quantidade", 0),
                    product.get("un_com", "N/A"),
                    product.get("vlr_uni", 0.0),
                    product.get("vlr_dz", 0.0),
                    product.get("vlr_total", 0.0),
                    product.get("lucro_total", 0.0)
                ))
                
            # Load nota_item
            for product in data.get("nota_item", []):
                self.invoice_item_table.insert("", "end", values=(
                    product.get("produto", "N/A"),
                    product.get("quantidade", 0),
                    product.get("un_com", "N/A"),
                    product.get("vlr_uni", 0.0),
                    product.get("vlr_total", 0.0),
                    product.get("lucro_total", 0.0)
                ))

        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showwarning("Aviso", "Nenhum dado encontrado para carregar.")

    def save_products_to_json(self):
        # Load existing data
        try:
            with open('nota.json', 'r') as json_file:
                data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"nota_unidade": [], "nota_duzia": []}
            
        if "nota_unidade" not in data:
            data["nota_unidade"] = []    

        products_to_save = []
        for item in self.invoice_table.get_children():
            values = self.invoice_table.item(item)["values"]
            product_data = {
                "produto": values[0],
                "quantidade": values[1],
                "un_com": "UNIDADE",  # Assuming UNIDADE for this example
                "vl_m": float(values[3].replace("R$", "").replace(",", ".")),
                "vlr_un": float(values[4].replace("R$", "").replace(",", ".")),
                "vlr_total": float(values[5].replace("R$", "").replace(",", ".")),
                "lucro_total": float(values[6].replace("R$", "").replace(",", ".")),
                "volume_total": float(values[7]) if len(values) > 7 else 0.0
            }
            products_to_save.append(product_data)

        # Append new products to existing data
        data["nota_unidade"].extend(products_to_save)

        # Save to JSON file
        with open('nota.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        messagebox.showinfo("Sucesso", "Produtos salvos com sucesso em 'nota.json'.")

    def save_duzia_products_to_json(self):
        # Load existing data
        try:
            with open('nota.json', 'r') as json_file:
                data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"nota_unidade": [], "nota_duzia": []}

        products_to_save = []
        for item in self.invoice_table.get_children():
            values = self.invoice_table.item(item)["values"]
            product_data = {
                "produto": values[0],
                "quantidade": values[1],
                "un_com": values[2],  # Assuming DUZIA for this example
                "vlr_uni": float(values[3].replace("R$", "").replace(",", ".")),
                "vlr_dz": float(values[4].replace("R$", "").replace(",", ".")),
                "vlr_total": float(values[5].replace("R$", "").replace(",", ".")),
                "lucro_total": float(values[6].replace("R$", "").replace(",", ".")),
            }
            products_to_save.append(product_data)

        # Append new products to existing data
        if "nota_duzia" not in data:
            data["nota_duzia"] = []  # Ensure the key exists
        data["nota_duzia"].extend(products_to_save)

        # Save to JSON file
        with open('nota.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        messagebox.showinfo("Sucesso", "Produtos da Duzia salvos com sucesso em 'nota.json'.")

    def save_item_products_to_json(self):
        # Carregar dados existentes
        try:
            with open('nota.json', 'r') as json_file:
                data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"nota_unidade": [], "nota_duzia": [], "nota_item": []}

        products_to_save = []
        for item in self.invoice_item_table.get_children():  # Usar a tabela correta para itens
            values = self.invoice_item_table.item(item)["values"]
            if len(values) < 6:  # Garantir que haja valores suficientes
                continue  # Pular se não houver valores suficientes
            product_data = {
                "produto": values[0],
                "quantidade": values[1],
                "un_com": values[2],  # Usar UN COM. aqui
                "vlr_uni": float(values[3].replace("R$", "").replace(",", ".")),
                "vlr_total": float(values[4].replace("R$", "").replace(",", ".")),
                "lucro_total": float(values[5].replace("R$", "").replace(",", ".")),
            }
            products_to_save.append(product_data)

        # Adicionar novos produtos aos dados existentes
        if "nota_item" not in data:
            data["nota_item"] = []  # Garantir que a chave exista
        data["nota_item"].extend(products_to_save)

        # Salvar no arquivo JSON
        with open('nota.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        messagebox.showinfo("Sucesso", "Produtos da Item salvos com sucesso em 'nota.json'.")

    def remove_product_from_invoice(self):
        selected_item = self.invoice_table.selection()
        if not selected_item:
            messagebox.showwarning("Erro", "Selecione um produto para remover.")
            return

        product_details = self.invoice_table.item(selected_item)["values"]
        product_description = product_details[0]
        quantity = int(product_details[1])

        for product in products:
            if product['descricao'] in product_description:
                if 'quantidade' in product:
                    product['quantidade'] += quantity
                else:
                    messagebox.showwarning("Erro", f"A chave 'quantidade' não existe para o produto '{product['descricao']}'.")
                break
        else:
            messagebox.showwarning("Erro", "Produto não encontrado no estoque.")

        self.invoice_table.delete(selected_item)
        messagebox.showinfo("Sucesso", f"Produto '{product_description}' removido do invoice e quantidade restaurada no estoque.")    

    def confirm_product(self, event):
        product_name = self.product_entry.get().replace(" ", "").lower()  # Remove spaces and convert to lowercase
        matched_products = [
            product for product in products 
            if product_name in f"{product.get('descricao', '')}{product.get('espessura', '')}X{product.get('largura', '')}{product.get('madeira', '')}".replace(" ", "").lower()
        ]

        if len(matched_products) == 1:
            self.product_entry.delete(0, tk.END)
            product = matched_products[0]
            if product.get('un_com') == "UNIDADE":
                self.product_entry.insert(0, f"{product['descricao']} - {product.get('espessura', 'N/A')} X {product.get('largura', 'N/A')} - {product.get('madeira', 'N/A')}")
            else:
                self.product_entry.insert(0, f"{product['descricao']} - {product.get('diametro_menor', 'N/A')} X {product.get('diametro_maior', 'N/A')} - {product.get('madeira', 'N/A')} - Tamanho: {product.get('tamanho', 'N/A')}")
                self.size_entry.delete(0, tk.END)
                self.size_entry.insert(0, product.get('tamanho', ''))
        elif len(matched_products) > 1:
            self.show_selection_window("Selecione o Produto", matched_products)
        else:
            messagebox.showwarning("Erro", "Produto não encontrado!")

    def confirm_product_duzia(self, event):
        product_name = self.product_entry.get().replace(" ", "").lower()  # Remove spaces and convert to lowercase
        matched_products = [
            product for product in products 
            if 'descricao' in product and 'madeira' in product and 'tipo' in product and product['tipo'] == "Dz/Unid" and product_name in f"{product['descricao']}{product['madeira']}".replace(" ", "").lower()
        ]

        if len(matched_products) == 1:
            self.product_entry.delete(0, tk.END)
            product = matched_products[0]
            self.product_entry.insert(0, f"{product['descricao']} - {product['madeira']}")
            self.size_entry.delete(0, tk.END)
            self.size_entry.insert(0, product.get('tamanho', ''))
        elif len(matched_products) > 1:
            self.show_selection_window("Selecione o Produto", matched_products, self.set_product_details_duzia)
        else:
            messagebox.showwarning("Erro", "Produto não encontrado!")

    def confirm_product_item(self, event):
        product_name = self.product_entry.get().replace(" ", "").lower()  # Remove spaces and convert to lowercase
        matched_products = [product for product in products if product_name in f"{product['descricao']}".replace(" ", "").lower()]

        if len(matched_products) == 1:
            self.product_entry.delete(0, tk.END)
            product = matched_products[0]
            self.product_entry.insert(0, f"{product['descricao']}")
        elif len(matched_products) > 1:
            self.show_selection_window("Selecione o Produto", matched_products)
        else:
            messagebox.showwarning("Erro", "Produto não encontrado!")           

    def show_selection_window(self, title, options, callback):
        top = tk.Toplevel(self)
        top.title(title)

        listbox = tk.Listbox(top, height=10, width=50)
        for option in options:
            listbox.insert(tk.END, f"{option['descricao']} - {option['espessura']} X {option['largura']} - {option['madeira']}")

        listbox.pack(padx=10, pady=10)
        select_button = tk.Button(top, text="Selecionar", command=lambda: self.select_from_listbox(listbox, callback))
        select_button.pack(pady=5)

    def select_from_listbox(self, listbox, callback):
        selected_index = listbox.curselection()
        if selected_index:
            selected_item = listbox.get(selected_index)
            # Extract the product description from the selected item
            product_description = selected_item.split(" - ")[0]  # Get the description part
            callback(product_description)  # Call the callback with the selected product description
        listbox.master.destroy()
        
    def on_item_double_click(self, event):
        item = self.invoice_item_table.selection()[0]
        column = self.invoice_item_table.identify_column(event.x)
        column_index = int(column.replace("#", "")) - 1

        if column_index == 3:  # Check if the clicked column is "Valor por Unidade"
            current_value = self.invoice_item_table.item(item)["values"][column_index]
            new_value = simpledialog.askfloat("Editar Valor", f"Novo valor para {self.invoice_item_table.heading(column)['text']}:",
                                                initialvalue=float(current_value.replace("R$", "").replace(",", ".")))

            if new_value is not None:
                self.invoice_item_table.item(item, values=self.update_invoice_item_values(item, new_value))

    def update_invoice_item_values(self, item, new_value):
        values = list(self.invoice_item_table.item(item)["values"])
        quantity = int(values[1])  # Get the quantity from the second column
        old_total_value = float(values[4][3:].replace(",", "."))  # Current total value
        old_profit = float(values[5][3:].replace(",", "."))  # Current profit

        # Update the unit price
        values[3] = f"R$ {new_value:.2f}"

        # Calculate new total value and profit
        new_total_value = new_value * quantity
        values[4] = f"R$ {new_total_value:.2f}"  # Update Valor Total
        new_profit = (new_total_value - (old_total_value - old_profit))  # Recalculate profit
        values[5] = f"R$ {new_profit:.2f}"  # Update Lucro Total

        return values    

    def on_invoice_duzia_double_click(self, event):
        item = self.invoice_table.selection()[0]
        column = self.invoice_table.identify_column(event.x)
        column_index = int(column.replace("#", "")) - 1

        if column_index in [3, 4]:  # Check if the clicked column is "Valor por Unidade" or "Valor por Duzia"
            current_value = self.invoice_table.item(item)["values"][column_index]
            new_value = simpledialog.askfloat("Editar Valor", f"Novo valor para {self.invoice_table.heading(column)['text']}:",
                                                initialvalue=float(current_value.replace("R$", "").replace(",", ".")))

            if new_value is not None:
                self.invoice_table.item(item, values=self.update_invoice_duzia_values(item, column_index, new_value))

    def update_invoice_duzia_values(self, item, column_index, new_value):
        values = list(self.invoice_table.item(item)["values"])
        quantity = int(values[1])
        product_description = values[0]

        if column_index == 3:  # Valor por Unidade
            old_total_value = float(values[5][3:].replace(",", "."))
            old_profit = float(values[6][3:].replace(",", "."))

            values[3] = f"R$ {new_value:.2f}"

            total_value = new_value * 12
            values[4] = f"R$ {total_value:.2f}"  # Update Valor por Duzia based on new unit price
            new_total_value = total_value * quantity
            values[5] = f"R$ {new_total_value:.2f}"

            lucro_total = old_profit + (new_total_value - old_total_value)
            lucro_total = max(lucro_total, 0)

            values[6] = f"R$ {lucro_total:.2f}"

        elif column_index == 4:  # Valor por Duzia
            old_total_value = float(values[5][3:].replace(",", "."))
            old_profit = float(values[6][3:].replace(",", "."))

            values[4] = f"{new_value:.2f}"  # No "R$" for DUZIA
            
            # Update total value based on new price per dozen
            vlr_per_unit = new_value / 12
            total_value = new_value * quantity  # Assuming 12 units in a dozen
            new_total_value = total_value
            lucro_total = old_profit + (new_total_value - old_total_value)
            values[5] = f"R$ {total_value:.2f}"
            values[3] = f"R$ {vlr_per_unit:.2f}"  # Keep "R$" for unit price
            values[6] = f"R$ {lucro_total:.2f}"

        return values

    def add_product_to_invoice(self):
        selected_product = self.product_entry.get()
        size = self.size_entry.get()

        # Obter a quantidade diretamente do campo de entrada
        quantity_str = self.quantity_entry.get()

        # Verificar se a quantidade é um número válido
        try:
            quantity = int(quantity_str)
        except ValueError:
            messagebox.showwarning("Erro", "Por favor, insira uma quantidade válida.")
            return

        if not selected_product or not size or quantity <= 0:
            messagebox.showwarning("Erro", "Selecione um produto, informe o tamanho e a quantidade.")
            return

        # Encontrar os detalhes do produto na lista de produtos
        product_details = next(
            (p for p in products if 
             'descricao' in p and 
             'espessura' in p and 
             'largura' in p and 
             'madeira' in p and 
             f"{p['descricao']} - {p['espessura']} X {p['largura']} - {p['madeira']}".strip().lower() == selected_product.strip().lower()), 
            None
        )

        if product_details:
            # Construir a descrição do produto para a invoice
            descricao = f"{product_details['descricao']} - {int(product_details['espessura'])}X{int(product_details['largura'])} - {product_details['madeira']} {size}M"

            # Calcular valores
            cost_per_m3 = product_details.get("vl_m", 0)
            width = int(product_details.get("largura", 0)) / 100  # Convert to meters
            thickness = int(product_details.get("espessura", 0)) / 100  # Convert to meters
            sale_price_per_m = product_details.get("valor_venda", 0)

            area = width * thickness
            volume_per_m = area * float(size) * quantity

            cost_per_meter = area * cost_per_m3
            price_per_unit = sale_price_per_m * float(size)
            total_cost = price_per_unit * quantity

            vlr_un = sale_price_per_m * float(size)

            profit_per_meter = sale_price_per_m - cost_per_meter
            total_profit = profit_per_meter * quantity * float(size)

            # Inserir na tabela de fatura
            self.invoice_table.insert("", "end", values=(descricao, quantity, product_details['un_com'], f"R$ {sale_price_per_m:.2f}", f"R$ {vlr_un:.2f}", f"R$ {total_cost:.2f}", f"R$ {total_profit:.2f}", f"{volume_per_m:.4f}"))

            # Atualizar inventário se for do tipo UNIDADE
            if product_details['un_com'] == "UNIDADE":
                self.update_inventory_on_add(product_details, size, quantity)

        else:
            messagebox.showwarning("Erro", "Produto não encontrado!")

    def update_inventory_on_add(self, product_details, size, quantity):
        for inv in inventory:
            if (inv['descricao'] == product_details['descricao'] and
                inv['espessura'] == int(product_details['espessura']) and  # Ensure espessura is an integer
                inv['largura'] == int(product_details['largura']) and  # Ensure largura is an integer
                inv['madeira'] == product_details['madeira'] and
                inv['tamanho'] == float(size)):
                inv['quantidade'] -= quantity
                messagebox.showinfo("Sucesso", f"Quantidade de {inv['descricao']} ({size}m) atualizada no estoque.")
                self.parent.save_data()
                break

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def gerar_pdf(self):
        try:
            # Coletar dados do cliente
            cliente_nome = self.client_entry.get()
            cliente = next((c for c in clients if c["name"] == cliente_nome), None)

            if cliente is None:
                messagebox.showwarning("Erro", "Selecione um cliente válido!")
                return

            cliente_endereco = cliente.get("address", "N/A")
            cliente_cpf = cliente.get("cpf", "N/A")
            cliente_telefone = cliente.get("phone", "N/A")

            # Criar PDF
            pdf = FPDF(orientation='P', unit='mm', format='A4')  # Página no formato A4
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)  # Margem inferior de 15mm
            pdf.set_font("Arial", size=8)

            # Cabeçalho
            pdf.set_font("Arial", style="B", size=9)
            pdf.cell(0, 7, "TICKET DE VENDA", ln=True, align="C")  # Centralizado
            pdf.set_font("Arial", size=8)
            pdf.cell(0, 6, "TIGELA MADEIRAS E ARTEFATOS LTDA", ln=True, align="C")
            pdf.cell(0, 6, "Telefone: (44) 9754-8463", ln=True, align="C")
            pdf.cell(0, 6, "Endereco: AVENIDA BRASIL, No 1621, DISTRITO CASA BRANCA, XAMBRE - PR", ln=True, align="C")
            pdf.cell(0, 6, "CNPJ: 39.594.567/0001-79    IE: 9086731905", ln=True, align="C")
            pdf.ln(1)

            # Dados do cliente
            pdf.set_font("Arial", style="B", size=8)
            pdf.cell(0, 6, f"Cliente: {cliente_nome}", ln=True, align="L")
            pdf.cell(0, 6, f"Endereco: {cliente_endereco}", ln=True, align="L")
            pdf.cell(0, 6, f"CPF: {cliente_cpf}", ln=True, align="L")
            pdf.cell(0, 6, f"Telefone: {cliente_telefone}", ln=True, align="L")
            pdf.ln(2)

            # Tabela de produtos
            pdf.set_fill_color(200, 200, 200)  # Cor de fundo para o cabeçalho da tabela
            pdf.set_font("Arial", style="B", size=7)
            pdf.cell(65, 5, "PRODUTO", border=1, align="C", fill=True)
            pdf.cell(18, 5, "UN. COM.", border=1, align="C", fill=True)
            pdf.cell(10, 5, "Qtd", border=1, align="C", fill=True)
            pdf.cell(37, 5, "Vlr por M/Vlr por Un", border=1, align="C", fill=True)
            pdf.cell(40, 5, "Vlr UN/Vlr DZ", border=1, align="C", fill=True)
            pdf.cell(30, 5, "Vlr Total", border=1, align="C", fill=True)
            pdf.ln()

            pdf.set_font("Arial", size=8)
            total_final = 0

            # Adicionar produtos da tabela de unidade
            for item in self.invoice_unidade_table.get_children():
                produto = self.invoice_unidade_table.item(item)["values"]
                if len(produto) < 5:
                    continue

                produto_desc = produto[0]
                un_com = "UNID"  # Alterado para UNID
                quantidade = produto[1]
                price_per_m = float(produto[3].replace("R$ ", "").replace(",", "."))
                price_per_unit = float(produto[4].replace("R$ ", "").replace(",", "."))
                total = float(produto[5].replace("R$ ", "").replace(",", "."))

                pdf.cell(65, 5, produto_desc, border=1, align="L")
                pdf.cell(18, 5, un_com, border=1, align="C")
                pdf.cell(10, 5, str(quantidade), border=1, align="C")
                pdf.cell(37, 5, f"R$ {price_per_m:.2f}", border=1, align="C")
                pdf.cell(40, 5, f"R$ {price_per_unit:.2f}", border=1, align="C")
                pdf.cell(30, 5, f"R$ {total:.2f}", border=1, align="C")
                pdf.ln()

                total_final += total

            # Adicionar produtos da tabela de item
            for item in self.invoice_item_table.get_children():
                produto = self.invoice_item_table.item(item)["values"]
                if len(produto) < 5:
                    continue

                produto_desc = produto[0]
                un_com = "UNID"  # Alterado para UNID
                quantidade = produto[1]
                price_per_unit = float(produto[3].replace("R$ ", "").replace(",", "."))
                total = float(produto[4].replace("R$ ", "").replace(",", "."))

                pdf.cell(65, 5, produto_desc, border=1, align="L")
                pdf.cell(18, 5, un_com, border=1, align="C")
                pdf.cell(10, 5, str(quantidade), border=1, align="C")
                pdf.cell(37, 5, "", border=1, align="C")  # Vlr por M vazio
                pdf.cell(40, 5, f"R$ {price_per_unit:.2f}", border=1, align="C")
                pdf.cell(30, 5, f"R$ {total:.2f}", border=1, align="C")
                pdf.ln()

                total_final += total

            # Adicionar produtos da tabela de duzia
            if self.invoice_duzia_table.get_children():
                for item in self.invoice_duzia_table.get_children():
                    produto = self.invoice_duzia_table.item(item)["values"]
                    if len(produto) < 5:
                        continue

                    produto_desc = produto[0]
                    un_com = "UNID" if produto[2] == "UNIDADE" else produto[2]  # Set to UNID if UNIDADE
                    quantidade = produto[1]
                    price_per_unit = float(produto[3].replace("R$ ", "").replace(",", "."))
                    total = float(produto[5].replace("R$ ", "").replace(",", "."))

                    pdf.cell(65, 5, produto_desc, border=1, align="L")
                    pdf.cell(18, 5, un_com, border=1, align="C")
                    pdf.cell(10, 5, str(quantidade), border=1, align="C")
                    pdf.cell(37, 5, f"R$ {price_per_unit:.2f}", border=1, align="C")
                    pdf.cell(40, 5, "", border=1, align="C")  # Show R$ 600.00 for DUZIA
                    pdf.cell(30, 5, f"R$ {total:.2f}", border=1, align="C")
                    pdf.ln()

                    total_final += total

            # Adicionar totais e informações adicionais
            pdf.ln(5)
            pdf.cell(17, 4, txt=f"Vendedor:", border=0, align="L")
            pdf.cell(29, 4, txt="", border=0)  # Espaço vazio
            pdf.cell(30, 4, txt=f"{self.vendor_entry.get()}", border=0, align="L")
            pdf.cell(75, 4, txt="", border=0)  # Espaço vazio
            pdf.cell(30, 4, txt=f"Total:", border=0, align="L")  # Total at the end
            pdf.cell(10, 4, txt=f"R$ {total_final:.2f}", border=0, align="L")  # Total after discount
            pdf.ln()

            pdf.cell(36, 4, txt=f"Forma de Pagamento:", border=0, align="L")
            pdf.cell(10, 4, txt="", border=0)  # Espaço vazio
            pdf.cell(30, 4, txt=f"{self.payment_method_entry.get()}", border=0, align="L")
            pdf.cell(75, 4, txt="", border=0)  # Espaço vazio
            pdf.cell(30, 4, txt=f"Acréscimos:", border=0, align="L")  # Total at the end
            pdf.cell(10, 4, txt=f"R$ 00.00", border=0, align="L")
            pdf.ln()

            pdf.cell(43, 4, txt=f"Limite de Crédito Utilizado:", border=0, align="L")
            pdf.cell(3, 4, txt="", border=0)  # Espaço vazio
            pdf.cell(30, 4, txt=f"R$ 00.00", border=0, align="L")
            pdf.cell(75, 4, txt="", border=0)  # Espaço vazio
            pdf.cell(30, 4, txt=f"Total Líquido:", border=0, align="L")  # Total at the end
            pdf.cell(10, 4, txt=f"R$ {total_final:.2f}", border=0, align="L")
            pdf.ln(5)

            pdf.set_font("Arial", style="B", size=7)
            pdf.cell(40, 5, "Composição Pgto", border=0, align="L")
            pdf.cell(30, 5, "Parcela", border=0, align="L")
            pdf.cell(50, 5, "Numerário", border=0, align="L")
            pdf.cell(30, 5, "", border=0, align="L")
            pdf.cell(30, 5, "Valor", border=0, align="L")
            pdf.cell(30, 5, "Data Pgto", border=0, align="L")
            pdf.ln()

            pdf.set_font("Arial", size=7)
            pdf.cell(40, 5, "", border=0, align="L")  # Espaço vazio para "Composição Pgto"
            pdf.cell(30, 5, "1", border=0, align="L")  # Parcela
            pdf.cell(50, 5, "Dinheiro", border=0, align="L")  # Numerário
            pdf.cell(30, 5, "", border=0, align="L")  # Espaço vazio
            pdf.cell(30, 5, f"R$ {total_final:.2f}", border=0, align="L")  # Valor
            pdf.cell(30, 5, datetime.now().strftime("%d/%m/%Y"), border=0, align="L")

            base_directory = "notas"

            # Certifique-se de que a pasta base "notas" existe
            if not os.path.exists(base_directory):
                os.makedirs(base_directory)

            # Determinar a inicial do cliente
            cliente_inicial = cliente_nome[0].upper()  # Primeira letra do nome do cliente em maiúscula

            # Caminho completo da subpasta baseada na inicial do cliente
            sub_directory = os.path.join(base_directory, cliente_inicial)

            # Certifique-se de que a subpasta exista
            if not os.path.exists(sub_directory):
                os.makedirs(sub_directory)

            # Caminho completo da pasta do cliente
            client_folder = os.path.join(sub_directory, cliente_nome.replace(" ", "_"))

            # Certifique-se de que a pasta do cliente exista
            if not os.path.exists(client_folder):
                os.makedirs(client_folder)

            # Determinar o número da operação com base nos arquivos já existentes na pasta do cliente
            operation_number = len([f for f in os.listdir(client_folder) if f.startswith(cliente_nome.replace(" ", "_") + "_Nota-")]) + 1

            # Nome do arquivo PDF
            nome_pdf = f"{cliente_nome.replace(' ', '_')}_Nota-{operation_number}.pdf"

            # Caminho completo do arquivo PDF
            caminho_pdf = os.path.join(client_folder, nome_pdf)

            # Salvar o arquivo PDF
            pdf.output(caminho_pdf)

            # Abrir o PDF automaticamente
            os.startfile(caminho_pdf)

            # Update inventory and report after generating the invoice
            self.update_inventory_after_invoice()  # Call the new method to update inventory
            self.parent.save_data()
            self.update_report_after_invoice(cliente_nome, total_final)
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o PDF: {str(e)}")

    def update_inventory_after_invoice(self):
        """Update the inventory based on the products in the invoice."""
        # Atualizar o estoque para produtos do tipo UNIDADE
        for item in self.invoice_unidade_table.get_children():
            produto = self.invoice_unidade_table.item(item)["values"]
            produto_desc = produto[0]
            quantidade = produto[1]

            # Print the product description and quantity for debugging
            print(f"Processing product: {produto_desc}, Quantity: {quantidade}")

            # Extracting details from the product description
            parts = produto_desc.split(" - ")
            print(f"Parts after split: {parts}")  # Debugging output

            if len(parts) < 3:
                print("Skipping product due to insufficient parts.")
                continue  # Skip if the format is not as expected

            descricao = parts[0].strip()
            madeira_part = parts[2].strip()

            # Split the wood type and size
            try:
                if " " in madeira_part:
                    madeira, tamanho_str = madeira_part.rsplit(" ", 1)  # Split from the right
                    tamanho = float(tamanho_str.replace("M", "").strip())  # Convert size to float, removing "M"
                else:
                    madeira = madeira_part
                    tamanho = 0.0  # Default value if size is not provided
            except ValueError as e:
                print(f"Error converting size: {e}")
                continue  # Skip this product if there's a conversion error

            try:
                espessura = float(parts[1].split("X")[0].strip())
                largura = float(parts[1].split("X")[1].strip())
            except ValueError as e:
                print(f"Error converting dimensions: {e}")
                print(f"Espessura and largura parts: {parts[1].split('X')}")
                continue  # Skip this product if there's a conversion error

            # Update the inventory for UNIDADE products
            for inv in self.parent.inventory:
                print(f"Checking inventory item: {inv}")  # Print inventory item for debugging
                if (inv['descricao'] == descricao and
                    inv['madeira'] == madeira and
                    inv['espessura'] == espessura and
                    inv['largura'] == largura and
                    inv['tamanho'] == tamanho):
                    inv['quantidade'] -= quantidade  # Decrease the quantity
                    print(f"Updated inventory for {descricao}: New quantity is {inv['quantidade']}")
                    break  # Exit the loop after updating

        # Atualizar o estoque para produtos do tipo ITEM
        for item in self.invoice_item_table.get_children():
            produto = self.invoice_item_table.item(item)["values"]
            produto_desc = produto[0]
            quantidade = produto[1]

            # Print the product description and quantity for debugging
            print(f"Processing item: {produto_desc}, Quantity: {quantidade}")

            # Update the inventory for ITEM products
            for inv in self.parent.inventory:
                print(f"Checking inventory item for ITEM: {inv}")  # Print inventory item for debugging
                if inv['tipo'] == "Item" and inv['descricao'].strip() == produto_desc.strip():  # Usar strip() para remover espaços
                    inv['quantidade'] -= quantidade  # Decrease the quantity
                    print(f"Updated inventory for item {produto_desc}: New quantity is {inv['quantidade']}")
                    break  # Exit the loop after updating

        # Atualizar o estoque para produtos do tipo DUZIA
        for item in self.invoice_duzia_table.get_children():
            produto = self.invoice_duzia_table.item(item)["values"]
            produto_desc = produto[0]
            quantidade = produto[1]

            # Print the product description and quantity for debugging
            print(f"Processing duzia product: {produto_desc}, Quantity: {quantidade}")

            # Extrair detalhes da descrição do produto
            parts = produto_desc.split(" - ")
            print(f"Parts after split: {parts}")  # Debugging output

            if len(parts) < 2:
                print("Skipping product due to insufficient parts.")
                continue  # Skip if the format is not as expected

            descricao = parts[0].strip()  # Nome do produto
            madeira_part = parts[1].strip()  # Parte que contém a madeira e o tamanho

            # Separar a madeira e o tamanho
            try:
                if " " in madeira_part:
                    madeira, tamanho_str = madeira_part.rsplit(" ", 1)  # Divide a partir da direita
                    tamanho = float(tamanho_str.replace("M", "").strip())  # Converte o tamanho para float, removendo "M"
                else:
                    madeira = madeira_part
                    tamanho = 0.0  # Valor padrão se o tamanho não for fornecido
            except ValueError as e:
                print(f"Error converting size: {e}")
                continue  # Pular este produto se houver um erro de conversão

            # Atualizar o estoque para produtos do tipo DUZIA
            for inv in self.parent.inventory:
                print(f"Checking inventory item for DUZIA: {inv}")  # Print inventory item for debugging
                if (inv['tipo'] == "Dz/Unid" and 
                    inv['descricao'].strip() == descricao and 
                    inv['madeira'].strip() == madeira and 
                    inv['tamanho'] == tamanho):  # Verifica todos os atributos

                    # Verifica a unidade de medida e atualiza a quantidade corretamente
                    if produto[2] == "UNIDADE":  # Supondo que a unidade de medida está na terceira posição
                        inv['quantidade'] -= quantidade  # Decrease the quantity directly
                    elif produto[2] == "DUZIA":  # Se for DUZIA
                        inv['quantidade'] -= quantidade * 12

                print(f"Updated inventory for duzia {produto_desc}: New quantity is {inv['quantidade']}")
                break  # Exit the loop after updating

        self.parent.save_data()  # Save data after updating inventory
            
    def update_report_after_invoice(self, cliente_nome, total_final):
        """Atualiza o relatório com a nova venda."""
        # Iterar por todos os itens na tabela de fatura e adicioná-los ao relatório
        for item in self.invoice_unidade_table.get_children():
            produto = self.invoice_unidade_table.item(item)["values"]
            produto_desc = produto[0]
            quantidade = produto[1]
            total_cost = float(produto[5].replace("R$", "").replace(",", "."))
            total_profit = float(produto[6])  # Lucro total para produtos da frame Unidade
            volume_total = produto[7]  # Volume total para produtos da frame Unidade

            # Criar uma nova entrada de relatório para cada produto
            new_report = {
                "produto": produto_desc,
                "quantidade": quantidade,
                "un_com": "UNIDADE",  # Adicionando UN COM.
                "valor_total": total_cost,
                "lucro_total": total_profit,  # Armazenar como float
                "cliente": cliente_nome,
                "data": datetime.now().strftime("%d/%m/%Y"),
                "volume_total": volume_total,  # Mantendo o volume total
            }
            reports.append(new_report)  # Adicionar o novo relatório à lista de relatórios

        for item in self.invoice_duzia_table.get_children():
            produto = self.invoice_duzia_table.item(item)["values"]
            produto_desc = produto[0]
            quantidade = produto[1]
            un_com = produto[2]
            total_cost = float(produto[5].replace("R$", "").replace(",", "."))
            total_profit = float(produto[6])  # Lucro total para produtos da frame Duzia

            # Criar uma nova entrada de relatório para cada produto
            new_report = {
                "produto": produto_desc,
                "quantidade": quantidade,
                "un_com": un_com,  # Adicionando UN COM.
                "valor_total": total_cost,
                "lucro_total": total_profit,  # Armazenar como float
                "cliente": cliente_nome,
                "data": datetime.now().strftime("%d/%m/%Y"),
                "volume_total": "",  # Volume total não aplicável para duzia
            }
            reports.append(new_report)  # Adicionar o novo relatório à lista de relatórios

        for item in self.invoice_item_table.get_children():
            produto = self.invoice_item_table.item(item)["values"]
            produto_desc = produto[0]
            quantidade = produto[1]
            un_com = produto[2]
            total_cost = float(produto[4].replace("R$", "").replace(",", "."))
            total_profit = float(produto[5])  # Lucro total para produtos da frame Item

            # Criar uma nova entrada de relatório para cada produto
            new_report = {
                "produto": produto_desc,
                "quantidade": quantidade,
                "un_com": un_com,  # Adicionando UN COM. para itens
                "valor_total": total_cost,
                "lucro_total": total_profit,  # Armazenar como float
                "cliente": cliente_nome,
                "data": datetime.now().strftime("%d/%m/%Y"),
                "volume_total": "",  # Volume total não aplicável para item
            }
            reports.append(new_report)  # Adicionar o novo relatório à lista de relatórios

        self.parent.save_data()  # Salvar dados após atualizar relatórios    

class ReportsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.refresh_report()  # Atualizar relatório na inicialização

    def create_widgets(self):
        # Frame para filtros
        self.filter_frame = ttk.Frame(self)
        self.filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        # Filtro por data
        ttk.Label(self.filter_frame, text="Filtrar por Data:").grid(row=0, column=0, padx=10)
        self.date_filter_combobox = ttk.Combobox(self.filter_frame, values=["Hoje", "Ontem", "Essa Semana", "Esse Mês", "Esse Ano", "Qualquer"])
        self.date_filter_combobox.current(0)  # Default: "Hoje"
        self.date_filter_combobox.grid(row=0, column=1, padx=10)

        # Pesquisa
        ttk.Label(self.filter_frame, text="Pesquisar:").grid(row=0, column=2, padx=10)
        self.search_entry = ttk.Entry(self.filter_frame)
        self.search_entry.grid(row=0, column=3, padx=10)

        # Botão de atualizar relatório
        self.btn_refresh_report = ttk.Button(self.filter_frame, text="Atualizar Relatório", command=self.refresh_report)
        self.btn_refresh_report.grid(row=0, column=4, padx=10)

        # Botão de gerar PDF
        self.btn_generate_pdf = ttk.Button(self.filter_frame, text="Gerar PDF", command=self.generate_pdf_report)
        self.btn_generate_pdf.grid(row=0, column=5, padx=10)

        # Tabela de relatórios
        self.report_table = ttk.Treeview(self, columns=("Produto", "Quantidade", "UN COM.", "Valor Total", "Lucro Total", "Cliente", "Data", "Volume Total"), show='headings')
        self.report_table.heading("Produto", text="Produto")
        self.report_table.heading("Quantidade", text="Qtd")
        self.report_table.heading("UN COM.", text="UN COM.")  # Adicionando cabeçalho para UN COM.
        self.report_table.heading("Valor Total", text="Valor Total")
        self.report_table.heading("Lucro Total", text="Lucro Total")
        self.report_table.heading("Cliente", text="Cliente")
        self.report_table.heading("Data", text="Data")
        self.report_table.heading("Volume Total", text="Volume Total (m³)")

        # Ajustar tamanho das colunas
        self.report_table.column("Produto", width=150, anchor="center")
        self.report_table.column("Quantidade", width=60, anchor="center")
        self.report_table.column("UN COM.", width=60, anchor="center")  # Ajustando largura da coluna UN COM.
        self.report_table.column("Valor Total", width=100, anchor="center")
        self.report_table.column("Lucro Total", width=100, anchor="center")
        self.report_table.column("Cliente", width=150, anchor="center")
        self.report_table.column("Data", width=100, anchor="center")
        self.report_table.column("Volume Total", width=120, anchor="center")

        self.report_table.grid(row=1, column=0, sticky='nsew')

        # Botão para excluir relatório
        self.btn_delete_report = ttk.Button(self, text="Excluir Relatório", command=self.delete_report)
        self.btn_delete_report.grid(row=2, column=0, pady=10)

        self.btn_send_whatsapp = ttk.Button(self, text="Enviar para WhatsApp", command=self.send_to_whatsapp)
        self.btn_send_whatsapp.grid(row=3, column=0, pady=10)
        
        # Add this line in the create_widgets method
        self.btn_generate_simple_pdf = ttk.Button(self.filter_frame, text="Gerar PDF Simples", command=self.generate_simple_pdf_report)
        self.btn_generate_simple_pdf.grid(row=0, column=6, padx=10)

        # Configurar grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
    def generate_simple_pdf_report(self):
        try:
            # Configurar o PDF
            pdf = FPDF("L", "mm", "A3")  # Tamanho A3
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Criar diretório para relatórios, se não existir
            directory = "relatorios_clientes"
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Título
            pdf.cell(0, 10, "Relatório de Movimentos", ln=True, align="C")
            pdf.ln(10)  # Quebra de linha

            pdf.set_fill_color(0, 0, 0)  # Cor de fundo para o cabeçalho da tabela
            pdf.set_font("Arial", style="B", size=10)
            pdf.cell(35, 10, "", border=0, align="C", fill=True)
            pdf.cell(85, 10, "CLIENTE", border=1, align="C", fill=True)
            pdf.cell(85, 10, "PRODUTO", border=1, align="C", fill=True)
            pdf.cell(25, 10, "QUANTIDADE", border=1, align="C", fill=True)
            pdf.cell(30, 10, "UN COM.", border=1, align="C", fill=True)
            pdf.cell(60, 10, "VALOR TOTAL", border=1, align="C", fill=True)
            pdf.cell(50, 10, "DATA", border=1, align="C", fill=True)
            pdf.ln()

            # Adicionar dados da tabela
            for item in self.report_table.get_children():
                values = self.report_table.item(item)["values"]
                pdf.cell(35, 10, "", border=0, align="C")
                pdf.cell(85, 10, str(values[5]), border=1, align="C")  # Cliente
                pdf.cell(85, 10, str(values[0]), border=1, align="C")  # Produto
                pdf.cell(25, 10, str(values[1]), border=1, align="C")  # Quantidade
                pdf.cell(30, 10, str(values[2]), border=1, align="C")  # UN COM.
                pdf.cell(60, 10, str(values[3]), border=1, align="C")  # Valor Total                
                pdf.cell(50, 10, str(values[6]), border=1, align="C")  # Data
                pdf.ln()

            # Salvar o PDF
            pdf_file_name = os.path.join(
                directory, f"relatorio_vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            pdf.output(pdf_file_name)

            # Verificar se o arquivo foi criado
            if os.path.exists(pdf_file_name):
                os.startfile(pdf_file_name)  # Abrir o PDF
                messagebox.showinfo("Sucesso", f"PDF gerado com sucesso: {pdf_file_name}")
            else:
                raise FileNotFoundError(f"Erro ao criar o arquivo PDF: {pdf_file_name}")

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o PDF: {e}")

    def generate_pdf_report(self):
        # Criar um objeto FPDF para gerar o PDF
        pdf = FPDF("L", "mm", "A3")  # Alterado para tamanho maior (A3)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=14)

        # Título
        pdf.cell(400, 15, txt="Relatório de Vendas", ln=True, align="C")

        # Cabeçalhos
        pdf.ln(10)  # Linha em branco
        pdf.cell(75, 15, "Produto", border=1, align="C")
        pdf.cell(15, 15, "Qtd", border=1, align="C")
        pdf.cell(25, 15, "UN COM.", border=1, align="C")  # Adicionando coluna UN COM.
        pdf.cell(60, 15, "Valor Total", border=1, align="C")
        pdf.cell(50, 15, "Lucro Total", border=1, align="C")
        pdf.cell(80, 15, "Cliente", border=1, align="C")
        pdf.cell(50, 15, "Data", border=1, align="C")
        pdf.cell(60, 15, "Volume Total (m³)", border=1, align="C")
        pdf.ln(15)  # Nova linha para os dados

        # Adicionar dados da tabela no PDF
        for item in self.report_table.get_children():
            values = self.report_table.item(item)["values"]
            pdf.cell(75, 15, values[0], border=1, align="C")  # Produto
            pdf.cell(15, 15, str(values[1]), border=1, align="C")  # Quantidade
            pdf.cell(25, 15, values[2], border=1, align="C")  # UN COM.
            pdf.cell(60, 15, str(values[3]), border=1, align="C")  # Valor Total
            pdf.cell(50, 15, str(values[4]), border=1, align="C")  # Lucro Total
            pdf.cell(80, 15, values[5], border=1, align="C")  # Cliente
            pdf.cell(50, 15, values[6], border=1, align="C")  # Data
            pdf.cell(60, 15, str(values[7]), border=1, align="C")  # Volume Total
            pdf.ln(15)

        # Salvar o PDF
        pdf.output("relatorio.pdf")
        messagebox.showinfo("Sucesso", "Relatório PDF gerado com sucesso!")

    def refresh_report(self):
        # Limpar entradas existentes
        for item in self.report_table.get_children():
            self.report_table.delete(item)

        # Filtro de data e pesquisa
        date_filter = self.date_filter_combobox.get()
        search_query = self.search_entry.get().lower()

        # Adicionar dados ao relatório
        for report in reports:
            # Filtrar por data
            report_date = datetime.strptime(report.get("data", "01/01/1970"), "%d/%m/%Y")
            if date_filter == "Hoje" and report_date.date() != datetime.now().date():
                continue
            elif date_filter == "Ontem" and report_date.date() != (datetime.now() - timedelta(days=1)).date():
                continue
            elif date_filter == "Essa Semana" and report_date < (datetime.now() - timedelta(days=datetime.now().weekday())):
                continue
            elif date_filter == "Esse Mês" and report_date.month != datetime.now().month:
                continue
            elif date_filter == "Esse Ano" and report_date.year != datetime.now().year:
                continue

            # Filtro de pesquisa
            if search_query and not (search_query in report.get("produto", "").lower() or search_query in report.get("cliente", "").lower()):
                continue

            # Certifique-se de que os valores são convertidos corretamente
            self.report_table.insert("", "end", values=(
                report.get("produto", "N/A"),
                report.get("quantidade", 0),
                report.get("un_com", "N/A"),  # Adicionando UN COM. no relatório
                f"R$ {float(report.get('valor_total', 0)):.2f}",  # Converter para float
                f"R$ {float(report.get('lucro_total', 0)):.2f}",  # Converter para float
                report.get("cliente", "N/A"),
                report.get("data", "N/A"),
                f"{float(report.get('volume_total', 0)):.4f}" if report.get('volume_total') else "0.0000"  # Verifica se volume_total é vazio
            ))  


    def delete_report(self):
        selected_item = self.report_table.selection()
        if selected_item:
            report_desc = self.report_table.item(selected_item)["values"][0]  # Descrição do produto
            confirm = messagebox.askyesno("Confirmar", f"Deseja excluir o relatório para o produto {report_desc}?")
            if confirm:
                for item in selected_item:
                    self.report_table.delete(item)
                for report in reports[:]:
                    if report.get("produto") == report_desc:
                        reports.remove(report)
                messagebox.showinfo("Sucesso", "Relatório excluído com sucesso!")
        else:
            messagebox.showwarning("Erro", "Selecione um relatório para excluir.")

            
    def send_to_whatsapp(self):
        from twilio.rest import Client
        from tkinter import messagebox

        # Informações da conta Twilio
        account_sid = 'AC8280b1c474a2067ccffd4129c27b7e4a'  # Replace with your Account SID
        auth_token = '9f59cdb0972f0885ce036aca82176813'  # Replace with your Auth Token

        # Número do WhatsApp do Twilio (sandbox)
        from_whatsapp_number = "whatsapp:+14155238886"  # Twilio sandbox number

        # Número do destinatário
        to_whatsapp_number = "whatsapp:+554498205264"  # Your WhatsApp number

        # Configuração do cliente Twilio
        client = Client(account_sid, auth_token)

        # Obter todos os itens da tabela
        all_items = self.report_table.get_children()
        if not all_items:
            messagebox.showwarning("Aviso", "A tabela está vazia. Nenhum relatório a ser enviado.")
            return

        # Criar o conteúdo do relatório
        report_lines = ["*RELATÓRIO DE VENDAS*"]  # Use asterisks for bold in WhatsApp
        for item in all_items:
            values = self.report_table.item(item)["values"]
            try:
                # Formatar cada linha do relatório com os dados da tabela
                line = f"{values[1]} | {values[0]} | VALOR: R$ {values[2]} | LUCRO: R$ {values[3]} | {values[4]} | {values[5]}"
                report_lines.append(line + "\n")  # Add a newline for spacing
            except IndexError:
                messagebox.showerror("Erro", "Um dos itens na tabela tem valores inválidos.")
                return

        # Concatenar as linhas do relatório em uma única string
        report_content = "\n".join(report_lines)

        # Debug: Print the report content to the console
        print("Conteúdo do relatório a ser enviado:")
        print(report_content)

        # Verificar se o conteúdo do relatório é muito grande e dividir em partes
        max_message_length = 1600  # Limite do WhatsApp para mensagens
        if len(report_content) > max_message_length:
            # Dividir o conteúdo em partes menores
            parts = [report_content[i:i+max_message_length] for i in range(0, len(report_content), max_message_length)]
        else:
            parts = [report_content]

        # Enviar as partes uma por uma
        try:
            for part in parts:
                message = client.messages.create(
                    body=part,  # Parte do relatório
                    from_=from_whatsapp_number,  # Número do Twilio
                    to=to_whatsapp_number  # Número do destinatário
                )
                print(f"Mensagem enviada: {part}")  # Debug: Print the sent message
            messagebox.showinfo("Sucesso", "Relatório enviado com sucesso!")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            messagebox.showerror("Erro", f"Erro ao enviar o relatório: {error_details}")

class InventoryTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        # Sidebar para navegação
        self.sidebar = tk.Frame(self, bg="white", width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.menu_buttons = {
            "Cadastrar Produtos LxE": self.show_register_lxe,
            "Cadastrar Produtos UN/Dz": self.show_register_un_dz,
            "Cadastrar Itens": self.show_register_item,
            "Lista de Estoque": self.show_inventory_list,
        }

        self.buttons = {}
        for label, command in self.menu_buttons.items():
            btn = tk.Button(
                self.sidebar,
                text=label,
                font=("Arial", 12),
                bg="white",
                fg="black",
                activebackground="gray",
                activeforeground="white",
                command=command,
            )
            btn.pack(fill=tk.X, padx=5, pady=5)
            self.buttons[label] = btn

        self.main_frame = tk.Frame(self, bg="white")
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.show_register_lxe()  # Exibe a tela de cadastro de produtos LxE por padrão

    def show_register_lxe(self):
        self.clear_main_frame()
        self.register_frame = tk.Frame(self.main_frame, bg="white")
        self.register_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.register_frame, text="DESCRIÇÃO:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_desc_lxe = ttk.Entry(self.register_frame)
        self.prod_desc_lxe.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.register_frame, text="TIPO DE MADEIRA:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_wood_type_lxe = ttk.Entry(self.register_frame)
        self.prod_wood_type_lxe.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.register_frame, text="ESPESSURA (cm):").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_thickness_lxe = ttk.Entry(self.register_frame)
        self.prod_thickness_lxe.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.register_frame, text="LARGURA (cm):").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_width_lxe = ttk.Entry(self.register_frame)
        self.prod_width_lxe.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.register_frame, text="TAMANHO (M):").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_size_lxe = ttk.Entry(self.register_frame)
        self.prod_size_lxe.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Button(self.register_frame, text="Cadastrar Produto LxE", command=self.register_product_lxe).grid(row=5, columnspan=2, pady=10)

    def register_product_lxe(self):
        try:
            product_name = self.prod_desc_lxe.get()
            wood_type = self.prod_wood_type_lxe.get()
            thickness = float(self.prod_thickness_lxe.get())
            width = float(self.prod_width_lxe.get())
            size = float(self.prod_size_lxe.get())  # Allow decimal size

            if not product_name or not wood_type:
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
                return

            new_product = {
                "descricao": product_name,
                "madeira": wood_type,
                "espessura": int(thickness),  # Convert to int to remove decimal for display
                "largura": int(width),  # Convert to int to remove decimal for display
                "tamanho": size,  # Store as float to allow decimals
                "quantidade": 0,  # Quantidade padrão
                "un_com": "UNIDADE",  # Alterado para "UNIDADE"
                "tipo": "LxE"  # New field added
            }

            self.parent.inventory.append(new_product)
            messagebox.showinfo("Sucesso", f"Produto LxE '{product_name}' cadastrado com sucesso!")

            self.prod_desc_lxe.delete(0, tk.END)
            self.prod_wood_type_lxe.delete(0, tk.END)
            self.prod_thickness_lxe.delete(0, tk.END)
            self.prod_width_lxe.delete(0, tk.END)
            self.prod_size_lxe.delete(0, tk.END)

            self.parent.save_data()  # Salvar dados

        except ValueError:
            messagebox.showerror("Erro", "Certifique-se de que os campos numéricos estão preenchidos corretamente.")

    def show_register_un_dz(self):
        self.clear_main_frame()
        self.register_frame = tk.Frame(self.main_frame, bg="white")
        self.register_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.register_frame, text="DESCRIÇÃO:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_desc_un_dz = ttk.Entry(self.register_frame)
        self.prod_desc_un_dz.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.register_frame, text="TIPO DE MADEIRA:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_wood_type_un_dz = ttk.Entry(self.register_frame)
        self.prod_wood_type_un_dz.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.register_frame, text="TAMANHO (M):").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.prod_size_un_dz = ttk.Entry(self.register_frame)
        self.prod_size_un_dz.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Button(self.register_frame, text="Cadastrar Produto UN/Dz", command=self.register_product_un_dz).grid(row=3, columnspan=2, pady=10)

    def register_product_un_dz(self):
        try:
            product_name = self.prod_desc_un_dz.get()
            wood_type = self.prod_wood_type_un_dz.get()
            size = float(self.prod_size_un_dz.get())  # Allow decimal size

            if not product_name or not wood_type:
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
                return

            new_product = {
                "descricao": product_name,
                "madeira": wood_type,
                "tamanho": size,  # Store as float to allow decimals
                "un_com": "UNIDADE",  # Sempre UNIDADE
                "quantidade": 0,  # Quantidade padrão
                "duzia": 0,  # Novo campo para duzias
                "tipo": "Dz/Unid"  # New field added
            }

            self.parent.inventory.append(new_product)
            messagebox.showinfo("Sucesso", f"Produto UN/Dz '{product_name}' cadastrado com sucesso!")

            self.prod_desc_un_dz.delete(0, tk.END)
            self.prod_wood_type_un_dz.delete(0, tk.END)
            self.prod_size_un_dz.delete(0, tk.END)

            self.parent.save_data()  # Salvar dados

        except ValueError:
            messagebox.showerror("Erro", "Certifique-se de que os campos estão preenchidos corretamente.")

    def show_register_item(self):
        self.clear_main_frame()
        self.register_item_frame()
        self.register_frame.pack(fill=tk.BOTH, expand=True)

    def register_item_frame(self):
        self.register_frame = tk.Frame(self.main_frame, bg="white")
        self.register_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.register_frame, text="DESCRIÇÃO:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.item_desc = ttk.Entry(self.register_frame)
        self.item_desc.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Button(self.register_frame, text="Adicionar Item", command=self.register_item).grid(row=1, columnspan=2, pady=10)

    def register_item(self):
        try:
            item_name = self.item_desc.get()

            if not item_name:
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
                return

            new_item = {
                "descricao": item_name,
                "un_com": "UNIDADE",  # Sempre UNIDADE
                "tipo": "Item"  # New field added
            }

            self.parent.inventory.append(new_item)  # Add to inventory list

            messagebox.showinfo("Sucesso", f"Item '{item_name}' cadastrado com sucesso!")

            self.clear_item_fields()  # Clear fields after registration
            self.parent.save_data()  # Save data persistently

        except ValueError:
            messagebox.showerror("Erro", "Certifique-se de que os campos estão preenchidos corretamente.")

    def clear_item_fields(self):
        self.item_desc.delete(0, tk.END)

    def show_inventory_list(self):
        self.clear_main_frame()
        
        frame_inventory_list = ttk.LabelFrame(self.main_frame, text="Lista de Estoque")
        frame_inventory_list.pack(fill=tk.BOTH, expand=True)

        self.inventory_table = ttk.Treeview(frame_inventory_list, columns=("Descrição", "Quantidade", "Duzia"), show='headings')
        self.inventory_table.heading("Descrição", text="Descrição")
        self.inventory_table.heading("Quantidade", text="Quantidade")
        self.inventory_table.heading("Duzia", text="Duzia")

        self.inventory_table.column("Descrição", width=300)
        self.inventory_table.column("Quantidade", width=80)
        self.inventory_table.column("Duzia", width=80)

        self.inventory_table.pack(fill=tk.BOTH, expand=True)

        # Botão para excluir produto
        ttk.Button(frame_inventory_list, text="Excluir Produto", command=self.delete_product).pack(pady=10)
        
        # Botão para alterar quantidade
        ttk.Button(frame_inventory_list, text="Alterar Quantidade", command=self.change_quantity).pack(pady=10)

        self.update_inventory_table()

    def change_quantity(self):
        selected_item = self.inventory_table.selection()  # Obtém o item selecionado
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um produto para alterar a quantidade.")
            return

        item_values = self.inventory_table.item(selected_item[0], 'values')
        descricao = item_values[0].strip()  # Descrição do produto (remover espaços extras)
        print(f"Descrição do produto selecionado: {descricao}")  # Print para depuração

        # Solicitar nova quantidade
        new_quantity = simpledialog.askinteger("Alterar Quantidade", f"Nova quantidade para '{descricao}':", minvalue=0)
        if new_quantity is None:
            return  # Se o usuário cancelar, sai da função

        found_product = False  # Flag para verificar se o produto foi encontrado
        for inv in self.parent.inventory:
            print(f"Verificando produto no inventário: {inv}")  # Print para depuração

            # Verificando se o produto é do tipo "Item"
            if inv['tipo'] == "Item" and inv['descricao'].strip() == descricao:
                inv['quantidade'] = new_quantity  # Atualiza a quantidade
                inv['duzia'] = new_quantity // 12  # Atualiza a quantidade de duzias
                found_product = True
                print(f"Produto Item atualizado: {inv}")  # Print para depuração
                break

            size_parts = descricao.split(" - ")
            if len(size_parts) < 3:
                continue  # Se a descrição não estiver no formato esperado, pula este item

            produto_descricao = size_parts[0]  # Nome do produto
            madeira = size_parts[1]  # Tipo de madeira
            ultimo_item = size_parts[-1].strip()  # Último item pode ser unidade ou tamanho

            if "/" in ultimo_item:  # Caso "LASCA - EUCALIPTO - 2.2 M / UNIDADE"
                tamanho_str, unidade_comercial = ultimo_item.split(" / ")
                unidade_comercial = unidade_comercial.strip()
            else:
                tamanho_str = ultimo_item
                unidade_comercial = None

            try:
                tamanho = float(tamanho_str.replace(" M", "").strip())  # Remover espaços e converter para float
            except ValueError:
                print(f"Erro ao converter tamanho: {tamanho_str}")
                continue  # Se houver erro na conversão, ignora este item

            # Comparação para tipo "Dz/Unid"
            if inv['tipo'] == "Dz/Unid" and inv['descricao'] == produto_descricao:
                if (inv['madeira'] == madeira and
                    inv['tamanho'] == tamanho and
                    (unidade_comercial is None or inv['un_com'].strip().upper() == unidade_comercial.upper())):

                    inv['quantidade'] = new_quantity  # Atualiza a quantidade
                    inv['duzia'] = new_quantity // 12  # Atualiza a quantidade de duzias
                    found_product = True
                    print(f"Produto Dz/Unid atualizado: {inv}")  # Print para depuração
                    break
                
            # Comparação para tipo "LxE"
            elif inv['tipo'] == "LxE" and inv['descricao'] == produto_descricao:
                if len(size_parts) < 4:
                    continue  # Evita erros de índice

                esp_largura = size_parts[2].split('X')  # Separar "8.0X12.0"
                if len(esp_largura) != 2:
                    continue  # Ignora se o formato não for esperado

                try:
                    espessura = int(float(esp_largura[0].strip()))  # Remove espaços antes de converter para int
                    largura = int(float(esp_largura[1].strip()))  # Remove espaços antes de converter para int
                    tamanho = float(size_parts[3].replace(" M", "").strip())  # Converte tamanho corretamente para float
                except ValueError:
                    continue  # Se não conseguir converter, ignora
                   
                if (inv['madeira'] == madeira and
                    inv['espessura'] == espessura and
                    inv['largura'] == largura and
                    inv['tamanho'] == tamanho):

                    inv['quantidade'] = new_quantity  # Atualiza a quantidade
                    found_product = True
                    print(f"Produto LxE atualizado: {inv}")  # Print para depuração
                    break

        if not found_product:
            messagebox.showwarning("Atenção", "Produto não encontrado no inventário.")
        else:
            messagebox.showinfo("Sucesso", f"Quantidade de '{descricao}' alterada para {new_quantity}.")

        self.update_inventory_table()  # Atualiza a tabela
        self.parent.save_data()  # Salva os dados após a alteração
        
        self.inventory_table.column("Descrição", width=400)  # Increased width for product description
        self.inventory_table.column("Quantidade", width=100)  # Increased width for quantity
        self.inventory_table.column("Duzia", width=100)  # Increased width for duzia

        # Set font size for the Treeview to quadruple the original size
        self.inventory_table.tag_configure('large_font', font=('Arial', 48))  # Set font to Arial, size 48

        # Apply the tag to all rows
        for item in self.inventory_table.get_children():
            self.inventory_table.item(item, tags=('large_font',))

    def update_inventory_table(self):
        for item in self.inventory_table.get_children():
            self.inventory_table.delete(item)

        for inv in self.parent.inventory:  # Use the inventory from the parent
            tipo = inv.get('tipo', 'N/A')  # Get the tipo field

            if tipo == "LxE":
                descricao = f"{inv['descricao']} - {inv['madeira']} - {inv['espessura']}X{inv['largura']} - {inv['tamanho']} M"
            elif tipo == "Dz/Unid":
                descricao = f"{inv['descricao']} - {inv['madeira']} - {inv['tamanho']} M"  # Removed "/ UNIDADE"
            elif tipo == "Item":
                descricao = f"{inv['descricao']}"
            else:
                descricao = "Descrição não disponível"  # Fallback for unknown types

            quantidade = inv.get('quantidade', 0)
            duzia = inv.get('duzia', 0)  # Get the duzia field
            self.inventory_table.insert("", "end", values=(descricao, quantidade, duzia))
            
        
    def delete_product(self):
        selected_item = self.inventory_table.selection()  # Obtém o item selecionado
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um produto para excluir.")
            return

        # Confirmação de exclusão do item selecionado
        confirm = messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir o produto selecionado?")
        if not confirm:
            return  # Cancela a exclusão

        for item in selected_item:
            item_values = self.inventory_table.item(item, 'values')
            descricao = item_values[0].strip()  # Descrição do produto (remover espaços extras)

            # Print para depuração
            print(f"Descrição do produto selecionado para exclusão: '{descricao}'")

            # Verificando se o tipo é "Item" e excluindo pela descrição completa
            if descricao and any(inv['tipo'] == "Item" and inv['descricao'].strip() == descricao for inv in self.parent.inventory):
                print(f"Produto tipo 'Item' encontrado. Tentando excluir: '{descricao}'")

                # Excluir item do tipo "Item"
                self.parent.inventory = [
                    inv for inv in self.parent.inventory
                    if not (inv['tipo'] == "Item" and inv['descricao'].strip() == descricao)
                ]
                print(f"Inventário após exclusão do Item: {self.parent.inventory}")
            else:
                print(f"Produto não é do tipo 'Item', verificando outros tipos.")

                # Separação da descrição conforme o tipo de produto
                parts = descricao.split(" - ")
                produto_descricao = parts[0].strip()  # Nome do produto, sem espaços extras

                if len(parts) >= 3:  
                    madeira = parts[1].strip()  # Tipo de madeira
                    # Para produtos LxE, o tamanho é a última parte
                    tamanho_str = parts[-1].replace(" M", "").strip()  # Tamanho (sem unidade)

                    # Remover "M" e converter para float
                    try:
                        tamanho = float(tamanho_str)
                    except ValueError:
                        print(f"Erro ao converter tamanho: {tamanho_str}")  # Debugging print statement
                        continue  # Se houver erro na conversão, ignora este item

                    # Para Dz/Unid
                    if len(parts) == 3:  
                        print(f"Excluindo produto do tipo 'Dz/Unid': {produto_descricao}, madeira: {madeira}, tamanho: {tamanho}")  # Debugging print statement
                        self.parent.inventory = [
                            inv for inv in self.parent.inventory
                            if not (inv['tipo'] == "Dz/Unid" and 
                                    inv['descricao'].strip() == produto_descricao and 
                                    inv['madeira'].strip() == madeira and 
                                    inv['tamanho'] == tamanho)
                        ]

                    # Para LxE
                    elif len(parts) >= 4:  
                        esp_largura = parts[2].strip()  # A parte do meio contém "espessuraXlargura"
                        espessura, largura = map(float, esp_largura.split('X'))  # Separar e converter espessura e largura

                        print(f"Excluindo produto do tipo 'LxE': {produto_descricao}, madeira: {madeira}, espessura: {espessura}, largura: {largura}, tamanho: {tamanho}")  # Debugging print statement
                        self.parent.inventory = [
                            inv for inv in self.parent.inventory
                            if not (inv['tipo'] == "LxE" and 
                                    inv['descricao'].strip() == produto_descricao and 
                                    inv['madeira'].strip() == madeira and
                                    inv['espessura'] == espessura and 
                                    inv['largura'] == largura and 
                                    inv['tamanho'] == tamanho)
                        ]

        self.update_inventory_table()  # Atualiza a tabela
        self.parent.save_data()  # Salva os dados após a exclusão
        messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            



if __name__ == "__main__":
    try:
        app = MainApp()
        app.mainloop()  # Mantém a interface gráfica aberta
    except Exception as e:
        print(f"Erro: {e}")
        input("Pressione Enter para sair...")