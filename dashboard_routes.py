from flask import Blueprint,render_template,redirect,url_for,session,request
from datetime import date
from curd_web import getDashboardData,getVitalTrenddata,getemployeeDetails
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import io
import base64
import numpy as np
PER_PAGE = 10  # Rows per page
today=date.today()
last_year_firstdate=date(today.year-1,1,1)

dashboard_bp=Blueprint('dashboard',__name__, url_prefix='/dashboard')
@dashboard_bp.route('/')
def dashboard():
    if  'username' not in session:
        return redirect(url_for('home_page')) 
    search_query = request.args.get('q', '').strip()
    # Get current page from query string (default to 1)
    page = request.args.get('page', 1, type=int)
    employeeDet,page,total_pages=getDashboardData(page,PER_PAGE,last_year_firstdate,today,search_query)     
    #if employeeDet:
    return render_template('dashboard.html',username=session['username'],
                               employees=employeeDet,page=page,total_pages=total_pages,per_page=PER_PAGE,request=request)
    
emp_dashboard_bp=Blueprint('emp_dashboard',__name__, url_prefix='/emp_dashboard')
@emp_dashboard_bp.route('/<ohc_id>', )
def emp_dashboard(ohc_id):
    if 'username' not in session:
        return redirect(url_for('home_page'))
    session['ohc_id']=ohc_id
    #vitaldata=getVitalTrenddata('1652960012')
    empResult=getemployeeDetails(ohc_id)
    vitaldata=getVitalTrenddata(ohc_id)
    print(vitaldata)

# Convert to DataFrame
    df = pd.DataFrame(vitaldata)
    print(df.head())

    # ✅ Convert report_date to datetime safely (supports datetime.date or str)
    df['report_date'] = pd.to_datetime(df['report_date'])
    # Replace empty strings with NaN
    df.replace('', np.nan, inplace=True)

    # ✅ Convert values to float (if needed)
    df['weight'] = df['weight'].astype(float)
    df['bmi'] = df['bmi'].astype(float)
    df['glucose_random'] = df['glucose_random'].astype(float)
    df['total_cholesterol'] = df['total_cholesterol'].astype(float)

    # ✅ Set Seaborn theme
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 4))

    # ✅ Plot trends
    sns.lineplot(x='report_date', y='weight', data=df, marker='o', label='Weight (kg)')
    sns.lineplot(x='report_date', y='bmi', data=df, marker='o', label='BMI')
    sns.lineplot(x='report_date', y='glucose_random', data=df, marker='o', label='Glucose (Random)')
    sns.lineplot(x='report_date', y='total_cholesterol', data=df, marker='o', label='Cholesterol (mg/dl)')
    for x, y in zip(df['report_date'], df['weight']):
        plt.text(x, y, f'{y:.1f}', fontsize=10, ha='center', va='bottom')
    for x, y in zip(df['report_date'], df['bmi']):
        plt.text(x, y, f'{y:.1f}', fontsize=10, ha='center', va='bottom')

    for x, y in zip(df['report_date'], df['glucose_random']):
        plt.text(x, y, f'{y:.0f}', fontsize=10, ha='center', va='bottom')

    for x, y in zip(df['report_date'], df['total_cholesterol']):
        plt.text(x, y, f'{y:.0f}', fontsize=10, ha='center', va='bottom')    
    # ✅ Format X-axis as dd-mm-YYYY
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    ax.set_xticks(df['report_date'])  # show only actual dates
    plt.xticks(rotation=45)
    


    # ✅ Chart formatting
    plt.title("Trend of Weight, BMI,  Glucose (Random) and Cholesterol")
    plt.xlabel("Report Date")
    plt.ylabel("Values")
    #plt.legend()
    #plt.tight_layout()

    plt.legend(
    bbox_to_anchor=(1.02, 1),   # x, y in axes fraction (1.02 = just outside right edge)
    loc='upper left',           # anchor legend’s upper‐left corner at that point
    borderaxespad=0 ,            # no extra padding
    fontsize=8,                     # Smaller font
    frameon=False,                  # Optional: remove legend box background
    handlelength=2,                 # Shorter line length
    handletextpad=0.5  
    )
    plt.tight_layout()

    # ✅ Save image
    #plt.savefig("static/plots/health_trend.png")
    # plt.show()  # Uncomment this if running locally to preview

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()  # Always close after saving

    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')

   




    return render_template("emp_dashboard.html",vitaldata=vitaldata, chart=image_base64,emp_name=empResult[0],ohc_id=ohc_id) 

