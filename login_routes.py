from flask import Blueprint,render_template,redirect,url_for,session,request,flash
from datetime import date
from curd_web import getLoginDetails


login_bp=Blueprint('login',__name__, url_prefix='/login')
@login_bp.route('/', methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form.get('uname')
        password=request.form.get('pwd')
        result=getLoginDetails(username,password)
        if result:
            session['username']=result[0]
            #flash("Login Successfull",'success') 
            return  redirect(url_for('dashboard.dashboard'))  
        else:
            return redirect(url_for('home_page'))  
    return 'login'

logout_bp=Blueprint('logout',__name__, url_prefix='/logout')
@logout_bp.route('/')
def logout():
    session.clear()
    #flash("You have loggedout","info")
    return redirect(url_for('home_page'))  
    