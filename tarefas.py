#!/usr/bin/env python
# coding: utf-8

# In[46]:


import tkinter as tk
from tkinter import messagebox, simpledialog
from tkcalendar import Calendar
import datetime
import json

class TarefasDoDia:
    def __init__(self, root):
        self.root = root
        self.root.title("tarefas do dia")
        self.root.geometry("300x340")
        self.root.resizable(False, False)
        self.root.configure(bg="white")
        
        self.fonte_padrao = ("Bahnschrift", 10)
        self.data_atual = datetime.date.today()
        self.tarefas = self.carregar_tarefas()
        
        self.frame_topo = tk.Frame(self.root, bg="white")
        self.frame_topo.pack(fill=tk.X, pady=5)
        
        self.label_data = tk.Label(self.frame_topo, text=self.data_atual.strftime("%d/%m/%y"), font=self.fonte_padrao, bg="white")
        self.label_data.pack(side=tk.LEFT, padx=10)
        
        self.botao_calendario = tk.Button(self.frame_topo, text="📅", command=self.abrir_calendario)
        self.botao_calendario.pack(side=tk.RIGHT, padx=10)
        
        self.frame_lista = tk.Frame(self.root, bg="white")
        self.frame_lista.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.checkboxes = []
        self.entradas_tarefas = []
        for _ in range(10):
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(self.frame_lista, variable=var, bg="white")
            checkbox.pack(anchor="w")
            self.checkboxes.append((checkbox, var))
            self.entradas_tarefas.append("")
        
        self.frame_botoes = tk.Frame(self.root, bg="white")
        self.frame_botoes.pack(fill=tk.X, pady=5)
        
        self.botoes = {
            "➕": self.adicionar_tarefa,
            "❌": self.excluir_tarefa,
            "✔": self.concluir_tarefa,
            "➡": self.adiar_tarefa
        }
        
        for simbolo, comando in self.botoes.items():
            btn = tk.Button(self.frame_botoes, text=simbolo, command=comando)
            btn.pack(side=tk.LEFT, expand=True, padx=5)
        
        self.carregar_tarefas_na_interface()

    def abrir_calendario(self):
        top = tk.Toplevel(self.root)
        top.title("selecionar data")
        cal = Calendar(top, date_pattern="dd/mm/yy")
        cal.pack(pady=10)
        
        def selecionar():
            self.data_atual = datetime.datetime.strptime(cal.get_date(), "%d/%m/%y").date()
            self.label_data.config(text=self.data_atual.strftime("%d/%m/%y"))
            self.carregar_tarefas_na_interface()
            top.destroy()
        
        tk.Button(top, text="ok", command=selecionar).pack(pady=5)

    def carregar_tarefas(self):
        try:
            with open("tarefas.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            with open("tarefas.json", "w") as f:
                json.dump({},f)
            return {}

    def salvar_tarefas(self):
        with open("tarefas.json", "w") as f:
            json.dump(self.tarefas, f)

    def carregar_tarefas_na_interface(self):
        tarefas_do_dia = self.tarefas.get(self.data_atual.strftime("%d/%m/%y"), [])
        for i in range(10):
            texto = tarefas_do_dia[i] if i < len(tarefas_do_dia) else ""
            self.checkboxes[i][0].config(text=texto)
            self.entradas_tarefas[i] = texto
                
    def verificar_checkbox_unica(self):
        selecionadas = sum(var.get() for _, var in self.checkboxes)
    
        if selecionadas > 1:
            messagebox.showinfo("erro", "tem que selecionar apenas uma tarefa")
            return False  # Retorna False se mais de uma checkbox estiver selecionada
    
        if selecionadas == 0:
            messagebox.showinfo("erro", "tem que selecionar uma tarefa")
            return False  # Retorna False se nenhuma checkbox estiver selecionada
    
        return True  # Retorna True se apenas uma checkbox estiver selecionada

    def adicionar_tarefa(self):
        if "" not in self.entradas_tarefas:
            messagebox.showinfo("erro", "tem que excluir uma tarefa pra poder adicionar uma nova")
            return
        indice = self.entradas_tarefas.index("")
        nova_tarefa = simpledialog.askstring("nova tarefa", "digite a tarefa:")
        if nova_tarefa:
            self.entradas_tarefas[indice] = nova_tarefa
            self.checkboxes[indice][0].config(text=nova_tarefa, font=("Bahnschrift", 10))
            self.salvar_tarefa()
    
    def excluir_tarefa(self):
        indices_para_excluir = []

        for i, (_, var) in enumerate(self.checkboxes):
            if var.get() and self.entradas_tarefas[i]:  # Se a tarefa está selecionada
                indices_para_excluir.append(i)  # Adicionar o índice da tarefa à lista para exclusão

        if indices_para_excluir:
            for i in indices_para_excluir:
                self.entradas_tarefas[i] = ""
                self.checkboxes[i][0].config(text="", font=("Bahnschrift", 10))  # Limpar o texto da checkbox
                self.checkboxes[i][1].set(False)  # Desmarcar a checkbox
            self.salvar_tarefa()  # Salvar as alterações

        else:
            messagebox.showinfo("erro", "Selecione uma ou mais tarefas para serem excluídas.")
    
    def concluir_tarefa(self):
        encontrou = False

        for i, (_, var) in enumerate(self.checkboxes):
            if var.get() and self.entradas_tarefas[i]:
                current_font = self.checkboxes[i][0].cget("font")

                if "overstrike" in current_font:
                    self.checkboxes[i][0].config(font=("Bahnschrift", 10))
                
                else:
                    self.checkboxes[i][0].config(font=("Bahnschrift", 10, "overstrike"))  # Adicionar o tachado
                
                self.checkboxes[i][0].config(text=self.entradas_tarefas[i])  # Atualizar o texto da checkbox
                encontrou = True  # Marcar que ao menos uma tarefa foi concluída

        if encontrou:
            self.salvar_tarefa()  # Salvar as alterações
        else:
            messagebox.showinfo("erro", "tem que selecionar pelo menos uma tarefa")
                
    def adiar_tarefa(self):
        encontrou = False
        data_amanha = (self.data_atual + datetime.timedelta(days=1)).strftime("%d/%m/%y")

        if data_amanha not in self.tarefas:
            self.tarefas[data_amanha] = []

        indices_para_excluir = []
    
        for i, (_, var) in enumerate(self.checkboxes):
            if var.get() and self.entradas_tarefas[i]:  # Se a tarefa está selecionada
                self.tarefas[data_amanha].append(self.entradas_tarefas[i])  # Transferir a tarefa para o dia seguinte
                indices_para_excluir.append(i)  # Adicionar o índice da tarefa à lista para exclusão
                encontrou = True  # Marcar que ao menos uma tarefa foi transferida

        for i in indices_para_excluir:
            self.entradas_tarefas[i] = ""
            self.checkboxes[i][0].config(text="", font=("Bahnschrift", 10))  # Limpar o texto na checkbox
            self.checkboxes[i][1].set(False)  # Desmarcar a checkbox

        if encontrou:
            self.salvar_tarefa()
        else:
            messagebox.showinfo("erro", "seleciona uma tarefa para ser adiada")
          
        
    def salvar_tarefa(self):
        self.tarefas[self.data_atual.strftime("%d/%m/%y")] = [t for t in self.entradas_tarefas if t]
        self.salvar_tarefas()

if __name__ == "__main__":
    root = tk.Tk()
    app = TarefasDoDia(root)
    root.mainloop()


# In[ ]:




