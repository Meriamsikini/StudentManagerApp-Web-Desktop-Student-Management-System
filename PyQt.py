import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QLineEdit, QHBoxLayout, QDialog, QFormLayout, QDialogButtonBox, QMessageBox,QLabel
from PyQt6.QtGui import QIcon , QPixmap, QAction


class DataManager:
    def __init__(self, file_path="etudiants.csv"):
        self.file_path = file_path
        self.load_data()
    
    def load_data(self):
        try:
            self.df = pd.read_csv(self.file_path)
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=["ID", "Prénom", "Nom", "Email", "Matière", "Note"])
            self.df.to_csv(self.file_path, index=False)
    
    def save_data(self):
        self.df.to_csv(self.file_path, index=False)
    
    def ajouter_etudiant(self, prenom, nom, email, matiere, note):
        new_id = len(self.df) + 1
        self.df = pd.concat([self.df, pd.DataFrame([{ "ID": new_id,"Prénom": prenom , "Nom": nom, "Email": email, "Matière": matiere, "Note": note }])], ignore_index=True)
        self.save_data()
    
    def supprimer_etudiant(self, id):
        self.df = self.df[self.df["ID"] != id]
        self.df.reset_index(drop=True, inplace=True)
        self.save_data()
    
    def rechercher_etudiant(self, nom):
        return self.df[self.df["Nom"].str.contains(nom, case=False, na=False)].copy()
    
    def modifier_etudiant(self, id, prenom, nom, email, matiere, note):
        self.df.loc[self.df["ID"] == id, ["Nom", "Prénom", "Email", "Matière", "Note"]] = nom, prenom, email, matiere, note
        self.save_data()
    
  
    def calculer_moyennes_par_matiere(self):
        return self.df.groupby("Matière")["Note"].mean().to_dict()

class StatsDialog(QDialog):
    def __init__(self, parent, stats):
        super().__init__(parent)
        self.setWindowTitle("Statistiques des Moyennes")
        layout = QVBoxLayout()

        if stats:
            for matiere, moyenne in stats.items():
                layout.addWidget(QLabel(f"{matiere}: {moyenne:.2f}"))
        else:
            layout.addWidget(QLabel("Aucune donnée disponible."))
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setLayout(layout)    

class AddStudentDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un étudiant")
        layout = QFormLayout()
        
        self.prenom_input = QLineEdit()
        self.nom_input = QLineEdit()
        self.email_input = QLineEdit()
        self.matiere_input = QLineEdit()
        self.note_input = QLineEdit()
        
        layout.addRow("Nom:", self.nom_input)
        layout.addRow("Prénom:", self.prenom_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Matière:", self.matiere_input)
        layout.addRow("Note:", self.note_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        return self.nom_input.text(), self.prenom_input.text(), self.email_input.text(), self.matiere_input.text(), self.note_input.text()

class EditStudentDialog(AddStudentDialog):
    def __init__(self, parent, student_data):
        super().__init__(parent)
        self.setWindowTitle("Modifier un étudiant")
        self.nom_input.setText(student_data["Nom"])
        self.prenom_input.setText(student_data["Prénom"])
        self.email_input.setText(student_data["Email"])
        self.matiere_input.setText(student_data["Matière"])
        self.note_input.setText(str(student_data["Note"]))

class StudentManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Gestion des Étudiants")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Email", "Matière", "Note"])
        layout.addWidget(self.table)
        
        search_layout = QHBoxLayout()

        # Création de la barre de recherche avec icône intégrée
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom")
        self.search_input.setFixedWidth(250)

        # Création de l'action pour l'icône de suppression
        clear_action = QAction(QIcon("static/icons8-clear-50.png"), "", self)  # Remplace par le chemin de ton icône
        clear_action.triggered.connect(self.search_input.clear)
        
        # Ajout de l'icône dans la barre de recherche à gauche
        self.search_input.addAction(clear_action, QLineEdit.ActionPosition.TrailingPosition)

        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        #layout.addLayout(matiere_layout)

        self.btn_stats = QPushButton("Afficher les Statistiques")
        self.btn_stats.clicked.connect(self.show_statistics)
        #layout.addWidget(self.btn_stats)

        self.btn_search = QPushButton("Rechercher")
        search_layout.addWidget(self.btn_search)
        
        self.btn_back = QPushButton(QIcon("static/icons8-back-50.png"),"",self)
        self.btn_back.setVisible(False)
        search_layout.addWidget(self.btn_back)
        
        layout.addLayout(search_layout)
       
        self.btn_add = QPushButton("Ajouter")
        layout.addWidget(self.btn_add)
        self.btn_delete = QPushButton("Supprimer")
        layout.addWidget(self.btn_delete)
        self.btn_edit = QPushButton("Modifier")
        layout.addWidget(self.btn_edit)

        layout.addWidget(self.btn_stats)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.load_students()
        self.btn_search.clicked.connect(self.search_student)
        self.btn_back.clicked.connect(self.load_students)
        self.btn_add.clicked.connect(self.open_add_dialog)
        self.btn_delete.clicked.connect(self.delete_student)
        self.btn_edit.clicked.connect(self.open_edit_dialog)
    
    def load_students(self):
        self.table.setRowCount(len(self.data_manager.df))
        for row, (_, student) in enumerate(self.data_manager.df.iterrows()):
            for col, value in enumerate(student):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
    
    def show_statistics(self):
        stats = self.data_manager.calculer_moyennes_par_matiere()
        dialog = StatsDialog(self, stats)
        dialog.exec()



    def search_student(self):
        search_text = self.search_input.text().strip()
        if search_text:
            filtered_df = self.data_manager.rechercher_etudiant(search_text)
            self.table.setRowCount(len(filtered_df))
            for row, (_, student) in enumerate(filtered_df.iterrows()):
                for col, value in enumerate(student):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))
            self.btn_back.setVisible(True)
    
    def open_add_dialog(self):
        dialog = AddStudentDialog(self)
        if dialog.exec():
            self.data_manager.ajouter_etudiant(*dialog.get_data())
            QMessageBox.information(self, "Succès", "Étudiant ajouté avec succès!")
            self.load_students()
    
    def delete_student(self):
       selected_row = self.table.currentRow()
       if selected_row >= 0:
        student_id = int(self.table.item(selected_row, 0).text())
        print(f"Suppression de l'étudiant avec ID: {student_id}")  # Vérification de l'ID
        reply = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment supprimer cet étudiant?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.supprimer_etudiant(student_id)
            self.load_students()

    
    def open_edit_dialog(self):
      selected_row = self.table.currentRow()
      if selected_row >= 0:
        student_id = int(self.table.item(selected_row, 0).text())
        student_data = self.data_manager.df.loc[self.data_manager.df["ID"] == student_id].iloc[0]
        print(f"Modification de l'étudiant avec ID: {student_id}")  # Vérification des données
        dialog = EditStudentDialog(self, student_data)
        if dialog.exec():
            self.data_manager.modifier_etudiant(student_id, *dialog.get_data())
            QMessageBox.information(self, "Succès", "Étudiant modifié avec succès!")
            self.load_students()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentManagementApp()
    window.show()
    sys.exit(app.exec())


