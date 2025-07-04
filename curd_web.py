from config import engine,users,metadata,employeeList,labReports,vitalResults,lipid_profile_results,glucose_results
from sqlalchemy import select, and_ , func , case, or_ ,insert
from sqlalchemy.exc import SQLAlchemyError
from math import ceil
from datetime import date
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
def saveNewEmployee(form_data):
    try:
        # Convert date_of_birth if provided
        if form_data['date_of_birth']:
            form_data['date_of_birth'] = date.fromisoformat(form_data['date_of_birth'])
        else:
            form_data['date_of_birth'] = None

        # Set ohc_id
        form_data['ohc_id'] = form_data['employee_number']

        # Convert last_visit_date if provided
        if form_data['last_visit_date']:
            form_data['last_visit_date'] = date.fromisoformat(form_data['last_visit_date'])
        else:
            form_data['last_visit_date'] = None

        # Prepare and execute insert
        stmt = insert(employeeList).values(form_data)
        with engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
            return result.rowcount  # return inside function

    except SQLAlchemyError as e:
        error_type = type(e).__name__ 
        return error_type  # return 0 or False to indicate failure

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

def save_lab_reports_values(reportvalues,labreportsdata):
    registration_id=labreportsdata.get('empid')
    report_date=labreportsdata.get('report_date')
    report_name=labreportsdata.get('report_name')    
    report_table=metadata.tables[labreportsdata.get('table_name')]
    
    try:
        with engine.begin() as conn:        
            chk_stmt=check_data_exists(registration_id,report_date,report_name)
            result_chk=conn.execute(chk_stmt).fetchone()
            print(result_chk)
            if not result_chk :
                    report_stmt = insert(labReports).values(
                    reportname=report_name,
                    registration_id=registration_id,  
                    file_path=labreportsdata.get('file_path'),                  
                    report_date=date.fromisoformat(report_date)
                    )
                    result = conn.execute(report_stmt)
                
                    insert_report_id = result.inserted_primary_key[0]
                    print(insert_report_id)
                    reportvalues['report_id']=insert_report_id
                    stmt2 = insert(report_table).values(reportvalues)        
                    result = conn.execute(stmt2)  

                    return "Data Saved"
            else:
                return "Data Already Exists for the selected Date"
    except Exception as e:
       return "Error occurred:"
              
    return 'dd'

def check_data_exists(patientID,report_date,report_name):
    
    stmt=select(labReports).where((labReports.c.report_date==report_date) &(labReports.c.registration_id==patientID)
                                   &(labReports.c.reportname==report_name))
    return stmt