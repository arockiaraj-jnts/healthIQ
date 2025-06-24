from flask import Flask,render_template,session
import secrets
from sqlalchemy import select, and_ , func , case
from dashboard_routes import dashboard_bp,emp_dashboard_bp
from login_routes import login_bp,logout_bp
from datetime import date
from curd_web import getLipidTrenddata,convertLipidtoimage,getglucoseTrenddata,convertGlucosetoimage

app=Flask(__name__)
app.secret_key=secrets.token_hex(32)


@app.route('/')
def home_page():
    return render_template('index.html')  

app.register_blueprint(dashboard_bp)
app.register_blueprint(login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(emp_dashboard_bp)

@app.route('/get_employee/<id>')
def get_employee(id):
    ohc_id=session['ohc_id']
    if(id=='lipid'):
        lipid_trend_data = getLipidTrenddata(ohc_id)
        image_base644=convertLipidtoimage(lipid_trend_data)
        return render_template('partial/employee_modal_content.html', chart=image_base644,title='Lipid')

    elif(id=='glucose'):
        glucose_trend_data = getglucoseTrenddata(ohc_id)
        image_base645=convertGlucosetoimage(glucose_trend_data)
        return render_template('partial/employee_modal_content.html', chart=image_base645,title='Glucose')


    

if(__name__=='__main__'):
    app.run(debug=True)