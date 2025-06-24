from config import engine,users,employeeList,labReports,vitalResults,lipid_profile_results,glucose_results
from sqlalchemy import select, and_ , func , case, or_
from math import ceil
from flask import request 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import io
import base64

def getDashboardData(page,PER_PAGE,last_year,search_query):
     #page = request.args.get('page', 1, type=int)
     offset = (page - 1) * PER_PAGE

     filters = []

     if search_query:
      filters.append(or_(
        employeeList.c.employee_name.ilike(f"%{search_query}%"),
        employeeList.c.employee_number.ilike(f"%{search_query}%")
    ))

     with engine.connect() as conn:
        # 1. Get total count for pagination
        count_stmt = select(func.count()).select_from(employeeList)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total_count = conn.execute(count_stmt).scalar()
        total_pages = ceil(total_count / PER_PAGE)
        stmt = ( select(
            employeeList.c.ohc_id,
            employeeList.c.employee_number,
            employeeList.c.employee_name,
            employeeList.c.gender,
            employeeList.c.date_of_birth,
            employeeList.c.blood_group,

            func.max(
                case((labReports.c.reportname == 'Lipid Profile', 1), else_=0)
            ).label('lipid_profile'),

            func.max(
                case((labReports.c.reportname == 'glucose fasting  postprandial', 1), else_=0)
            ).label('glucose'),

            func.max(
                case((labReports.c.reportname == 'Stool Routine', 1), else_=0)
            ).label('urine'),

            func.max(
                case((labReports.c.reportname == 'Urine Routine', 1), else_=0)
            ).label('stool')
        ).select_from(
            employeeList.outerjoin(
                labReports,
                and_(
                    employeeList.c.ohc_id == labReports.c.registration_id,
                    func.year(labReports.c.report_date) == last_year
                )
            )
        ).group_by(
            employeeList.c.ohc_id,
            employeeList.c.employee_number,
            employeeList.c.employee_name,
            employeeList.c.gender,
            employeeList.c.date_of_birth,
            employeeList.c.blood_group
        )
        .limit(PER_PAGE)
        .offset(offset)
       
        )   
        if filters:
            stmt = stmt.where(*filters)
        result = conn.execute(stmt)
        #rows = result.fetchall()
        employeeDet = [dict(r._mapping) for r in result.fetchall()]
        return employeeDet,page,total_pages
     
def getVitalTrenddata(registrationId):
    
    
    with engine.connect() as conn:
        # 1. Get total count for pagination
        
        stmt = select(
            labReports.c.registration_id,
            labReports.c.report_date,
            vitalResults.c.bp,
            vitalResults.c.pulse,
            vitalResults.c.temperature,
            vitalResults.c.height,
            vitalResults.c.weight,
            vitalResults.c.spo2,
            vitalResults.c.bmi,
            vitalResults.c.type,
            vitalResults.c.glucose_random,
            vitalResults.c.glucose_fasting,
            vitalResults.c.total_cholesterol
            ).select_from(
                vitalResults.outerjoin(labReports, vitalResults.c.report_id == labReports.c.id)
            ).where(
                labReports.c.registration_id == registrationId
            )
        result = conn.execute(stmt)
        #rows = result.fetchall()
        vitalDdata = [dict(r._mapping) for r in result.fetchall()]
        return vitalDdata
    
def getLipidTrenddata(registrationId):
    
    
    with engine.connect() as conn:
        # 1. Get total count for pagination
        
        stmt = select(
            labReports.c.registration_id,
            labReports.c.report_date,
            lipid_profile_results.c.triglycerides,
            lipid_profile_results.c.total_cholesterol,
            lipid_profile_results.c.ldl_cholesterol,
            lipid_profile_results.c.hdl_cholesterol,
            lipid_profile_results.c.vldl
            
            ).select_from(
                lipid_profile_results.outerjoin(labReports, lipid_profile_results.c.report_id == labReports.c.id)
            ).where(
                labReports.c.registration_id == registrationId
            )
        result = conn.execute(stmt)
        #rows = result.fetchall()
        lipiddata = [dict(r._mapping) for r in result.fetchall()]
        return lipiddata    
     
def getglucoseTrenddata(registrationId):
    with engine.connect() as conn:
        # 1. Get total count for pagination
        
        stmt = select(
            labReports.c.registration_id,
            labReports.c.report_date,
            glucose_results.c.fasting_blood_glucose,
            glucose_results.c.post_prandial_blood_glucose,
            glucose_results.c.HbA1c
           
            
            ).select_from(
                glucose_results.outerjoin(labReports, glucose_results.c.report_id == labReports.c.id)
            ).where(
                labReports.c.registration_id == registrationId
            )
        result = conn.execute(stmt)
        #rows = result.fetchall()
        glucosedata = [dict(r._mapping) for r in result.fetchall()]
        return glucosedata  

def getLoginDetails(username,password):
    with engine.connect() as conn:
            stmt=select (users.c.fullname).where((users.c.username==username) &(users.c.password==password))
            result=conn.execute(stmt).fetchone()
            print(result)
    return result  

def getemployeeDetails(ohc_id):
    with engine.connect() as conn:
            stmt=select (employeeList.c.employee_name).where((employeeList.c.ohc_id==ohc_id) )
            result=conn.execute(stmt).fetchone()
            print(result)
    return result  

def convertLipidtoimage(lipiddata):
    df = pd.DataFrame(lipiddata)
    print(df.head())

    # ✅ Convert report_date to datetime safely (supports datetime.date or str)
    df['report_date'] = pd.to_datetime(df['report_date'])

    # ✅ Convert values to float (if needed)
    df['triglycerides'] = df['triglycerides'].astype(float)
    df['total_cholesterol'] = df['total_cholesterol'].astype(float)
    df['hdl_cholesterol'] = df['hdl_cholesterol'].astype(float)
    df['ldl_cholesterol'] = df['ldl_cholesterol'].astype(float)
    df['vldl'] = df['vldl'].astype(float)

    # ✅ Set Seaborn theme
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 4))

    # ✅ Plot trends
    sns.lineplot(x='report_date', y='triglycerides', data=df, marker='o', label='triglycerides')
    sns.lineplot(x='report_date', y='total_cholesterol', data=df, marker='o', label='Total cholesterol')
    sns.lineplot(x='report_date', y='hdl_cholesterol', data=df, marker='o', label='HDL cholesterol')
    sns.lineplot(x='report_date', y='ldl_cholesterol', data=df, marker='o', label='LDL Cholesterol (mg/dl)')

    # ✅ Format X-axis as dd-mm-YYYY
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    ax.set_xticks(df['report_date'])  # show only actual dates
    plt.xticks(rotation=45)

    # ✅ Chart formatting
    plt.title("Lipid Profile")
    plt.xlabel("Report Date")
    plt.ylabel("Values")
    plt.legend()
    plt.tight_layout()

    # ✅ Save image
    #plt.savefig("static/plots/health_trend.png")
    # plt.show()  # Uncomment this if running locally to preview

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()  # Always close after saving

    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')  
    return  image_base64   

def convertGlucosetoimage (glucose_data):
    df = pd.DataFrame(glucose_data)
    print(df.head())

    # ✅ Convert report_date to datetime safely (supports datetime.date or str)
    df['report_date'] = pd.to_datetime(df['report_date'])

    # ✅ Convert values to float (if needed)
    df['fasting_blood_glucose'] = df['fasting_blood_glucose'].astype(float)
    df['post_prandial_blood_glucose'] = df['post_prandial_blood_glucose'].astype(float)
    df['HbA1c'] = df['HbA1c'].astype(float)
    

    # ✅ Set Seaborn theme
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 4))

    # ✅ Plot trends
    sns.lineplot(x='report_date', y='fasting_blood_glucose', data=df, marker='o', label='Fasting Sugar')
    sns.lineplot(x='report_date', y='post_prandial_blood_glucose', data=df, marker='o', label='Post Prandial Sugar')
    sns.lineplot(x='report_date', y='HbA1c', data=df, marker='o', label='HbA1c')
   

    # ✅ Format X-axis as dd-mm-YYYY
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    ax.set_xticks(df['report_date'])  # show only actual dates
    plt.xticks(rotation=45)

    # ✅ Chart formatting
    plt.title("Glucose Trend")
    plt.xlabel("Report Date")
    plt.ylabel("Values")
    plt.legend()
    plt.tight_layout()

    # ✅ Save image
    #plt.savefig("static/plots/health_trend.png")
    # plt.show()  # Uncomment this if running locally to preview

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()  # Always close after saving

    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')  
    return  image_base64  