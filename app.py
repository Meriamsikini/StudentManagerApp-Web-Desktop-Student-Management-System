from flask import Flask, render_template, request, redirect, url_for,session
import pandas as pd

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'  # pour gérer les sessions

class DataManager:
    def __init__(self, file_path="etudiants.csv"):
        self.file_path = file_path
        self.load_data()
    
    def load_data(self):
        try:
            self.df = pd.read_csv(self.file_path)
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=["ID", "Nom", "Prénom", "Email", "Matière", "Note"])
            self.df.to_csv(self.file_path, index=False)
    
    def save_data(self):
        self.df.to_csv(self.file_path, index=False)
    
    def ajouter_etudiant(self, nom, prenom, email, matiere, note):
        new_id = len(self.df) + 1
        self.df = pd.concat([self.df, pd.DataFrame([{ "ID": new_id, "Nom": nom, "Prénom": prenom, "Email": email, "Matière": matiere, "Note": note }])], ignore_index=True)
        self.save_data()
    
    def supprimer_etudiant(self, id):
        self.df = self.df[self.df["ID"] != id]
        self.df.reset_index(drop=True, inplace=True)
        self.save_data()
    
    def rechercher_etudiant(self, nom):
        return self.df[self.df["Nom"].str.contains(nom, case=False, na=False)].copy()
    
    def modifier_etudiant(self, id, nom, prenom, email, matiere, note):
        self.df.loc[self.df["ID"] == id, ["Nom", "Prénom", "Email", "Matière", "Note"]] = nom, prenom, email, matiere, note
        self.save_data()
    
    def calculer_moyenne(self, matiere):
        notes = self.df[self.df["Matière"] == matiere]["Note"].astype(float)
        return notes.mean() if not notes.empty else 0

# Création d'une instance de DataManager
data_manager = DataManager()

@app.route('/index')
def index():
    
    if 'username' not in session:
        return redirect(url_for('login'))
    students = data_manager.df.to_dict(orient="records")
    return render_template('index.html', students=students)


@app.route('/')
def accueil():
    return redirect(url_for('login'))



@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        matiere = request.form['matiere']
        note = request.form['note']
        data_manager.ajouter_etudiant(nom, prenom, email, matiere, note)
        return redirect(url_for('index'))
    return render_template('add_student.html')

@app.route('/supprimer/<int:id>', methods=['GET', 'POST'])
def supprimer(id):
    data_manager.supprimer_etudiant(id)
    return redirect(url_for('index'))


@app.route('/stats')
def stats():
    df = pd.read_csv("etudiants.csv")
    if df.empty:
        statistiques = []
    else:
        grouped = df.groupby('Matière')['Note'].mean().reset_index()
        statistiques = list(zip(grouped['Matière'], grouped['Note']))
    return render_template('stats.html', statistiques=statistiques)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))  # Redirige si déjà connecté

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users_df = pd.read_csv('user.csv')
        user = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
        if not user.empty:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Identifiants incorrects.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/recherche', methods=['POST'])
def recherche():
    nom = request.form['recherche_nom']
    resultats = data_manager.rechercher_etudiant(nom)
    return render_template('index.html', students=resultats.to_dict(orient="records"))

@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    if request.method == 'POST':
        nom = request.form['Nom']
        prenom = request.form['Prénom']
        email = request.form['Email']
        matiere = request.form['Matière']
        note = request.form['Note']

        data_manager.modifier_etudiant(id, nom, prenom, email, matiere, note)
        return redirect(url_for('index'))
    etudiant = data_manager.df[data_manager.df["ID"] == id].iloc[0]
    return render_template('edit_student.html', student=etudiant)


if __name__ == '__main__':
    app.run(debug=True)

