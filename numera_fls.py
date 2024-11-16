import os

from flask import Flask, render_template, request, redirect, send_from_directory, url_for
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import letter 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text, column
from sqlalchemy.ext.declarative import declarative_base
#--------------------
app = Flask(__name__)
Upload_Path ="Uploads" #Folder path for the files to get uploaded 
app.config["UPLOAD_FOLDER"] = Upload_Path
#--------------------
# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy()
# change string to the name of your database; add path if necessary
db_name = 'numerador.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)

class Usuarios(db.Model):
    __tablename__='usuarios'

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rubrica = db.Column(db.String(50))

    def __init__(self, rubrica):
        self.rubrica = rubrica

#with app.app_context():
#    db.create_all()
#--------------------
EXTENSIONS = set(['.pdf']) #Extensões aceitas

def check_extension(arq):
    name, ext=os.path.splitext(arq)
    if ext.lower() in EXTENSIONS:
        return True
    else:
        return False
#--------------------    
@app.route('/')
@app.route('/usuario')
def usuario_page() -> 'html':
    #usuarios = db.session.execute(db.select(Usuarios).order_by(Usuarios.rubrica)).scalars()
    sql = text('select rubrica from usuarios order by rubrica')
    usuarios = db.session.execute(sql)
    rubricas = [row[0] for row in usuarios]
    return render_template('usuarios.html',
                           the_title='Seleciona o usuário',
                           lista_usuarios=rubricas)
#--------------------
@app.route('/menu', methods=['GET', 'POST'])
def menu_page() -> 'html':
    return render_template('menu.html',
                           the_title='Menu: tipo de documento a ser numerado',
                           rubrica=request.form.get('rubrica'))
#--------------------
@app.route('/ff')
def ff_page() -> 'html':
    return render_template('ffinclusao.html',
                           the_title='Inclusão de arquivos e a numeração das folhas das Fichas Finais',
                           tipo_doc="ff",
                           arquivo='<input class="form-control" type="file" id="arquivo_ff" name="arquivo_ff" onchange="this.form.submit();" style="width: 315px; margin-top: 10px; margin-bottom: 20px;">',
                           bt_concluir='')
#--------------------
@app.route('/fisico')
def fis_page() -> 'html':
    return render_template('ffinclusao.html',
                           the_title='Inclusão de arquivos e a numeração das folhas das Fichas Finais',
                           tipo_doc="fis",
                           arquivo='<input class="form-control" type="file" id="arquivo1" name="arquivo1" onchange="this.form.submit();" style="width: 315px; margin-top: 10px; margin-bottom: 20px;">',
                           bt_concluir='')
#--------------------
@app.route('/digital')
def dig_page() -> 'html':
    return render_template('ffinclusao.html',
                           the_title='Inclusão de arquivos e a numeração das folhas das Fichas Finais',
                           tipo_doc="dig",
                           arquivo='<input class="form-control" type="file" id="arquivo_dig" name="arquivo_dig" onchange="this.form.submit();" style="width: 315px; margin-top: 10px; margin-bottom: 20px;">',
                           bt_concluir='')
#--------------------
@app.route('/upload', methods=['POST'])
def upload_file():
    if "arquivo_ff" not in request.files and "arquivo_dig" not in request.files:       
        return render_template("ffinclusao.html", error="no file")
    elif "arquivo_ff" in request.files:
        input = request.files["arquivo_ff"]
    else:
        input = request.files["arquivo_dig"]

    if input.filename == "":
        return render_template("ffinclusao.html", error="empty file")
    
    if input and check_extension(input.filename):
        filename = secure_filename(input.filename)
        input.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        #stat=os.stat(os.path.join(app.config["UPLOAD_FOLDER"],filename))   

        arquivoInput = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        pdf = PdfReader(arquivoInput)
        totalPaginas = len(pdf.pages)
        return render_template('ffinclusao.html',
                           the_title='Inclusão de arquivos e a numeração das folhas das Fichas Finais',
                           arquivo=filename, 
                           pgs_pdf=totalPaginas,
                           bt_concluir='<input type="submit" class="btn btn-success" value="Concluído" style="margin-top: 10px; width: 280px;"/>')
    else:
        return render_template("ffinclusao.html", error="invalid extension")
#--------------------
@app.route('/numerar/<arquivo>', methods=['POST'])
def numerar_pgs(arquivo):
    reader1 = PdfReader(os.path.join(app.config["UPLOAD_FOLDER"], arquivo)) 
    num_pgs = request.form.getlist('cont1_fl')
    
    for page in range(len(reader1.pages)): 
        c = canvas.Canvas(arquivo, pagesize=letter) 
        c.drawString(476, 743, num_pgs[page]) 
        c.save() 
        reader2 = PdfReader(arquivo)
        # Merge the overlay page onto the template page
        reader1.pages[page].merge_page(reader2.pages[0])
    # Write the result to a new PDF file
    writer = PdfWriter() 
    for page in reader1.pages: 
        writer.add_page(page) 
    with open(os.path.join(app.config["UPLOAD_FOLDER"], arquivo), "wb") as f_out: 
        writer.write(f_out)
    os.remove(arquivo) 
    return redirect(url_for("listar_arquivos"))
#--------------------
@app.route('/listar')
def listar_arquivos():
    list_arq=[]
    for filename in os.listdir(Upload_Path):
        path=os.path.join(Upload_Path, filename)
        if os.path.isfile(path):
            list_arq.append(filename)  
    ult_arq=list_arq[len(list_arq)-1] if len(list_arq)!=0 else ""
    return render_template('download.html',
                           the_title='Download dos arquivos numerados',
                           list=list_arq,
                           ult_arq=ult_arq)   
#--------------------
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename,as_attachment=True)
#--------------------
@app.route("/delete/<filename>")
def delete_files(filename):
    os.remove(Upload_Path +"/" + filename)
    return redirect(url_for("listar_arquivos"))
#--------------------
if __name__ == '__main__':
    app.run(debug=True)