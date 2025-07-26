from config import engine,users,metadata,employeeList,labReports,vitalResults,lipid_profile_results,glucose_results,thyroid_results
from sqlalchemy import select, and_ , func , case, or_ ,insert
from sqlalchemy.exc import SQLAlchemyError,DBAPIError
from math import ceil
from datetime import date
from flask import request 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import io
import base64
import re

def getDashboardData(page,PER_PAGE,last_year_firstdate,today,search_query):
     #page = request.args.get('page', 1, type=int)
     offset = (page - 1) * PER_PAGE

     filters = []

     if search_query:
      filters.append(or_(
        employeeList.c.employee_name.ilike(f"%{search_query}%"),
        employeeList.c.ohc_id.ilike(f"%{search_query}%")
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
            ).label('stool'),

            func.max(
                case((labReports.c.reportname == 'Urine Routine', 1), else_=0)
            ).label('urine')
        ).select_from(
            employeeList.outerjoin(
                labReports,
                and_(
                    employeeList.c.ohc_id == labReports.c.registration_id,
                    labReports.c.report_date.between(last_year_firstdate, today)
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
        print(last_year_firstdate, today)
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

def getThyroidTrenddata(registrationId):
    
    
    with engine.connect() as conn:
        # 1. Get total count for pagination
        
        stmt = select(
            labReports.c.registration_id,
            labReports.c.report_date,
            thyroid_results.c.total_T3_Tri_iodothyronine,
            thyroid_results.c.total_T4_Thyroxine
            
            
            ).select_from(
                thyroid_results.outerjoin(labReports, thyroid_results.c.report_id == labReports.c.id)
            ).where(
                labReports.c.registration_id == registrationId
            )
        result = conn.execute(stmt)
        #rows = result.fetchall()
        thyroiddata = [dict(r._mapping) for r in result.fetchall()]
        return thyroiddata        
     
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
    for x, y in zip(df['report_date'], df['triglycerides']):
        plt.text(x, y, f'{y:.1f}', fontsize=10, ha='center', va='bottom')
    for x, y in zip(df['report_date'], df['total_cholesterol']):
        plt.text(x, y, f'{y:.1f}', fontsize=10, ha='center', va='bottom') 
    for x, y in zip(df['report_date'], df['hdl_cholesterol']):
        plt.text(x, y, f'{y:.1f}', fontsize=10, ha='center', va='bottom') 
    for x, y in zip(df['report_date'], df['ldl_cholesterol']):
        plt.text(x, y, f'{y:.1f}', fontsize=10, ha='center', va='bottom')            
    # ✅ Format X-axis as dd-mm-YYYY
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    ax.set_xticks(df['report_date'])  # show only actual dates
    plt.xticks(rotation=45)

    # ✅ Chart formatting
    plt.title("Lipid Profile")
    plt.xlabel("Report Date")
    plt.ylabel("Values")
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
    return  image_base64  

def convertThyroidtoimage(thyroiddata):
    df = pd.DataFrame(thyroiddata)
    print(df.head())

    # ✅ Convert report_date to datetime safely (supports datetime.date or str)
    df['report_date'] = pd.to_datetime(df['report_date'])

    # ✅ Convert values to float (if needed)
    df['total_T3_Tri_iodothyronine'] = df['total_T3_Tri_iodothyronine'].astype(str).apply(lambda x: re.sub(r'[^\d.]', '', x))
    df['total_T4_Thyroxine'] = df['total_T4_Thyroxine'].astype(str).apply(lambda x: re.sub(r'[^\d.]', '', x))
    df['total_T3_Tri_iodothyronine'] = df['total_T3_Tri_iodothyronine'].astype(float)
    df['total_T4_Thyroxine'] = df['total_T4_Thyroxine'].astype(float)
    

    # ✅ Set Seaborn theme
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 4))

    # ✅ Plot trends
    sns.lineplot(x='report_date', y='total_T3_Tri_iodothyronine', data=df, marker='o', label='Total T3 Tri iodothyronine')
    sns.lineplot(x='report_date', y='total_T4_Thyroxine', data=df, marker='o', label='Total T4 Thyroxine')
    for x, y in zip(df['report_date'], df['total_T3_Tri_iodothyronine']):
        plt.text(x, y, f'{y:.1f}', fontsize=10, ha='center', va='bottom')
    for x, y in zip(df['report_date'], df['total_T4_Thyroxine']):
        plt.text(x, y, f'{y:.1f}', fontsize=10, ha='center', va='bottom')    
    # ✅ Format X-axis as dd-mm-YYYY
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    ax.set_xticks(df['report_date'])  # show only actual dates
    plt.xticks(rotation=45)

    # ✅ Chart formatting
    plt.title("Thyroid Profile")
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
    #df['HbA1c'] = df['HbA1c'].astype(float)
    

    # ✅ Set Seaborn theme
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 4))

    # ✅ Plot trends
    sns.lineplot(x='report_date', y='fasting_blood_glucose', data=df, marker='o', label='Fasting Sugar')
    sns.lineplot(x='report_date', y='post_prandial_blood_glucose', data=df, marker='o', label='Post Prandial Sugar')
    #sns.lineplot(x='report_date', y='HbA1c', data=df, marker='o', label='HbA1c')
    for x, y in zip(df['report_date'], df['fasting_blood_glucose']):
        plt.text(x, y, f'{y:.1f}', fontsize=10, ha='center', va='bottom')
    for x, y in zip(df['report_date'], df['post_prandial_blood_glucose']):
        plt.text(x, y, f'{y:.1f}', fontsize=10, ha='center', va='bottom')    

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
                    #print(stmt2)       
                    result = conn.execute(stmt2)  

                    return "Data Saved"
            else:
                return "Data Already Exists for the selected Date"
    #except Exception as e:
    #   return "Error occurred:"
    except SQLAlchemyError as e:
        error_type = type(e).__name__ 
        error_message = str(e) 
        return f"{error_type}: {error_message}" 
        #return error_type  # return 0 or False to indicate failure
       #return e
              
    #return 'dd'

def check_data_exists(patientID,report_date,report_name):
    
    stmt=select(labReports).where((labReports.c.report_date==report_date) &(labReports.c.registration_id==patientID)
                                   &(labReports.c.reportname==report_name))
    return stmt

def getUploadedPdffiles(empid,report_name):
    print(report_name)
    stmt = select(labReports.c.file_path).where(
    (labReports.c.file_path.isnot(None)) &
    (labReports.c.registration_id == empid) &
    (labReports.c.reportname == report_name)
)

    with engine.connect() as conn:
        result = conn.execute(stmt).fetchall()  
        file_paths = [f'/view-pdf/' + row[0] for row in result]  # extract file_path from each row

        
    return file_paths

   
def saveUrinedata(report_name,parsed_data,test_results,output_save_path,empId,report_date):
      
    lab_reports=metadata.tables["lab_reports"]
    urineReport=metadata.tables["urine_routine_results"]
    try:
     with engine.begin() as conn:       
        
        # Step 1: Insert metadata into lab_reports
            registration_id=empId,
            #report_date=safe_parse_datetime(parsed_data.get("Collection Date/Time")).date()
            chk_stmt=check_data_exists(registration_id,report_date,report_name)
            result_chk=conn.execute(chk_stmt).fetchone() #check duplicate entry
            if not result_chk :
                    report_stmt = insert(lab_reports).values(
                    reportname=report_name,
                    registration_id=registration_id,
                    #registration_datetime=safe_parse_datetime(parsed_data.get("Registration Date/Time")),
                    #patient_name=parsed_data.get("Patient Name"),
                    #collection_datetime=safe_parse_datetime(parsed_data.get("Collection Date/Time")),
                    #reporting_datetime=safe_parse_datetime(parsed_data.get("Reporting Date/Time")),
                    #referred_by=parsed_data.get("Referred By"),
                    #age_sex=parsed_data.get("Age/Sex"),
                    file_path=output_save_path,
                    report_date=report_date
                    )
                    result = conn.execute(report_stmt)
                
                    insert_report_id = result.inserted_primary_key[0]           
                    #conn.commit()
                    print('A',insert_report_id)

                    # Step 2: Insert stool results into stool_routine_results
                    report_stmt = insert(urineReport).values(
                    report_id=insert_report_id,
                    quantity=test_results.get("Quantity"),
                    colour=test_results.get("Colour"),
                    appearance=test_results.get("Appearance"),
                    deposit=test_results.get("Deposit"),
                    pH=test_results.get("pH"),
                    specific_gravity=test_results.get("Specific Gravity"),
                    albumin=test_results.get("Albumin"),
                    sugar=test_results.get("Sugar"),
                    ketone_bodies=test_results.get("Ketone Bodies"),
                    nitrite=test_results.get("Nitrite"),
                    blood=test_results.get("Blood"),
                    bile_pigments=test_results.get("Bile Pigments"),
                    bile_salts=test_results.get("Bile Salts"),
                    urobilinogen=test_results.get("Urobilinogen"),
                    epithelial_cells=test_results.get("Epithelial Cells"),
                    pus_cells=test_results.get("Pus Cells"),
                    red_blood_cells=test_results.get("Red Blood Cells"),
                    casts=test_results.get("Casts"),
                    crystals=test_results.get("Crystals"),
                    amorphous_materials=test_results.get("Amorphous Materials"),
                    bacteria=test_results.get("Bacteria"),
                    yeast_cells=test_results.get("Yeast Cells"),
                    mucus=test_results.get("Mucus")

                    )
                    #result = conn.execute(report_stmt)
            else :
                print("Duplicate Rows")        

            

    except (SQLAlchemyError, DBAPIError) as e:
        print(" Transaction failed and was rolled back:", e)   

def saveStooldata(report_name,parsed_data,test_results,output_save_path,empId,report_date):
      
    lab_reports=metadata.tables["lab_reports"]
    stoolReport=metadata.tables["stool_routine_results"]
    try:
     with engine.begin() as conn:       
        
        # Step 1: Insert metadata into lab_reports
            registration_id=empId,
            
            chk_stmt=check_data_exists(registration_id,report_date,report_name)
            result_chk=conn.execute(chk_stmt).fetchone() #check duplicate entry
            if not result_chk :
                    report_stmt = insert(lab_reports).values(
                    reportname=report_name,
                    registration_id=registration_id,
                    #registration_datetime=safe_parse_datetime(parsed_data.get("Registration Date/Time")),
                    #patient_name=parsed_data.get("Patient Name"),
                    #collection_datetime=safe_parse_datetime(parsed_data.get("Collection Date/Time")),
                    #reporting_datetime=safe_parse_datetime(parsed_data.get("Reporting Date/Time")),
                    #referred_by=parsed_data.get("Referred By"),
                    #age_sex=parsed_data.get("Age/Sex"),
                    file_path=output_save_path,
                    report_date=report_date
                    )
                    result = conn.execute(report_stmt)
                
                    insert_report_id = result.inserted_primary_key[0]           
                    #conn.commit()
                    print('A',insert_report_id)

                    # Step 2: Insert stool results into stool_routine_results
                    report_stmt = insert(stoolReport).values(
                    report_id=insert_report_id,
                    colour=test_results.get("Colour"),
                    consistency=test_results.get("Consistency"),
                    reaction=test_results.get("Reaction"),
                    blood=test_results.get("Blood"),
                    mucus=test_results.get("Mucus"),
                    parasites=test_results.get("Parasites"),
                    occult_blood=test_results.get("Occult Blood"),
                    reducing_substances=test_results.get("Reducing Substances"),
                    red_blood_cells=test_results.get("Red Blood Cells"),
                    epithelial_cells=test_results.get("Epithelial Cells"),
                    pus_cells=test_results.get("Pus Cells"),
                    fungal_organisms=test_results.get("Fungal Organisms"),
                    vegetable_fibres=test_results.get("Vegetable Fibres"),
                    muscle_fibres=test_results.get("Muscle Fibres"),
                    fat_globules=test_results.get("Fat Globules"),
                    starch_granules=test_results.get("Starch Granules"),
                    vegetative_forms=test_results.get("Vegetative forms"),
                    cystic_forms=test_results.get("Cystic forms"),
                    larvae=test_results.get("Larvae"),
                    ova=test_results.get("Ova")

                    )
                    #result = conn.execute(report_stmt)
            else :
                print("Duplicate rows")
                        

            

    except (SQLAlchemyError, DBAPIError) as e:
        print(" Transaction failed and was rolled back:", e)   


def saveCBCdata(report_name,output_save_path,empId,report_date):
      
    lab_reports=metadata.tables["lab_reports"]
    
    try:
     with engine.begin() as conn:       
        
        # Step 1: Insert metadata into lab_reports
            registration_id=empId,
            
            chk_stmt=check_data_exists(registration_id,report_date,report_name)
            result_chk=conn.execute(chk_stmt).fetchone() #check duplicate entry
            if not result_chk :
                    report_stmt = insert(lab_reports).values(
                    reportname=report_name,
                    registration_id=registration_id,
                    #registration_datetime=safe_parse_datetime(parsed_data.get("Registration Date/Time")),
                    #patient_name=parsed_data.get("Patient Name"),
                    #collection_datetime=safe_parse_datetime(parsed_data.get("Collection Date/Time")),
                    #reporting_datetime=safe_parse_datetime(parsed_data.get("Reporting Date/Time")),
                    #referred_by=parsed_data.get("Referred By"),
                    #age_sex=parsed_data.get("Age/Sex"),
                    file_path=output_save_path,
                    report_date=report_date
                    )
                    result = conn.execute(report_stmt)
                
                    insert_report_id = result.inserted_primary_key[0]           
                    #conn.commit()
                    print('A',insert_report_id)

                    
                    #result = conn.execute(report_stmt)
            else :
                print("Duplicate rows")
                        

            

    except (SQLAlchemyError, DBAPIError) as e:
        print(" Transaction failed and was rolled back:", e)               