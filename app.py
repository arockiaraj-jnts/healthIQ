from flask import Flask,render_template,session,redirect,url_for,request,flash,jsonify,json,send_from_directory, abort
import secrets,os
from sqlalchemy import select, and_ , func , case
from dashboard_routes import dashboard_bp,emp_dashboard_bp
from login_routes import login_bp,logout_bp
from datetime import date
from file_process import process_pdf
from curd_web import getLipidTrenddata,getThyroidTrenddata,convertLipidtoimage,getglucoseTrenddata,convertGlucosetoimage,saveNewEmployee,getemployeeDetails,save_lab_reports_values,getUploadedPdffiles,convertThyroidtoimage

app=Flask(__name__)
app.secret_key=secrets.token_hex(32)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = 'uploads'
PDF_FOLDER = os.path.join(os.getcwd(), 'uploads')

@app.route('/')
def home_page():
    return render_template('index.html')  

app.register_blueprint(dashboard_bp)
app.register_blueprint(login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(emp_dashboard_bp)
@app.route('/add_new_employee', methods=['GET', 'POST'])
def add_new_employee():
    if 'username' not in session:
        return redirect(url_for('home_page')) 
    if request.method == 'POST':
        # Handle form submission
        form_data = request.form.to_dict()
        result=saveNewEmployee(form_data)
        if(result==1):
            employee_name=form_data['employee_name']
            print("Form submitted:", form_data)
            flash(f'Employee {employee_name} added successfully!', 'success')
        else:
              flash(f'Error Occured-{result}', 'danger')   
        return redirect(url_for('add_new_employee')) 
    return render_template('add_employee.html', request=request)

@app.route('/get_employee/<id>')
def get_employee(id):
    ohc_id=session['ohc_id']
    if(id=='lipid'):
        lipid_trend_data = getLipidTrenddata(ohc_id)
        image_base644=convertLipidtoimage(lipid_trend_data)
        return render_template('partial/employee_modal_content.html', chart=image_base644,title='Lipid')

    elif(id=='thy'):
        thyroid_trend_data = getThyroidTrenddata(ohc_id)
        image_base644=convertThyroidtoimage(thyroid_trend_data)
        return render_template('partial/employee_modal_content.html', chart=image_base644,title='Thyroid')
    
    elif(id=='glucose'):
        glucose_trend_data = getglucoseTrenddata(ohc_id)
        image_base645=convertGlucosetoimage(glucose_trend_data)
        return render_template('partial/employee_modal_content.html', chart=image_base645,title='Glucose')

@app.route('/get_employee_pdfreport/<report_name>')
def get_employee_pdfreport(report_name):    
    filename='070725125030.pdf'
    filename2='070725125035.pdf'
    #print(ohc_id2)
    allPdfs=getUploadedPdffiles(session['ohc_id'],report_name)
    #print(allPdfs)
    """pdf_files = []
    pdf_files.append(f'/view-pdf/{filename}')
    pdf_files.append(f'/view-pdf/{filename2}')
    print(pdf_files)
    #pdf_files.append('/uploads/070725125030.pdf')
    #pdfFiles = ['/static/samples/1652960012_38.pdf']"""
    return jsonify({
        'success': bool(allPdfs),
        'pdfs': allPdfs
    })

@app.route('/view-pdf/<filename>')
def serve_pdf(filename):
    safe_path = os.path.join(PDF_FOLDER)
    full_path = os.path.join(safe_path, filename)
    if os.path.exists(full_path):
        return send_from_directory(safe_path, filename)
    else:
        abort(404)

    

@app.route('/upload_reports')
def upload_reports():
    if 'username' not in session:
        return redirect(url_for('home_page')) 
    return render_template('upload_reports.html',request=request)

@app.route('/verify_employee',methods=["GET","POST"])
def verify_employee():
    data=request.get_json()
    empid=data.get('emp_id')
    empName=getemployeeDetails(empid)[0]
    print(empName)
    if empName:
        return jsonify({'status': 'success', 'employee_name': empName})
    else:
        return jsonify({'status': 'error'}), 404
    
@app.route('/upload_employee_report',methods=["GET","POST"])  
def   upload_employee_report():
     if 'report' not in request.files:
        return jsonify({'error': 'No file part'}), 400

     file = request.files['report']
     empId=request.form['empId']
     report_date=request.form['report_date']
     if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the file
     filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
     file.save(filepath)
     alldata=process_pdf(empId,report_date,filepath,output_folder=app.config['UPLOAD_FOLDER'])
     #alldata2=json.dumps(alldata)
       
     print(alldata)
     return jsonify({'status': 'success','alldata':alldata})

@app.route('/save_reports',methods=['POST'])
def save_reports():
    form_data = request.form.to_dict()
    print(form_data)
    items = list(form_data.items())

    # Split the dictionary
    if form_data.get("report_name")=='Vital Results':
        #print('yes')
        
        height=float(form_data.get("height"))
        weight=float(form_data.get("weight"))
        bmi=int(round((weight*10000)/(height*height),1))
        reportvalues= dict(items[:-4])  # all except last 4
        reportvalues['bmi']=bmi
        labreportsdata = dict(items[-5:])  # last 4
    else:
        reportvalues= dict(items[:-5])  # all except last 4
        labreportsdata = dict(items[-5:])  # last 4   
    print(reportvalues)
    #print(form_data.get("report_name"))
    print("==")     
    message=save_lab_reports_values(reportvalues,labreportsdata)
    
    return jsonify({"status": "success", "message": message, "data": form_data})
    

if(__name__=='__main__'):
    app.run(debug=True,host='0.0.0.0',port=5000)