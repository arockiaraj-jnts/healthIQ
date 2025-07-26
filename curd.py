from config import engine
from sqlalchemy import MetaData,insert,select
from sqlalchemy.exc import SQLAlchemyError,DBAPIError
import re
from datetime import datetime

metadata = MetaData()
metadata.reflect(bind=engine)

def check_data_exists(patientID,report_date,report_name):
    lab_reports=metadata.tables["lab_reports"]
    stmt=select(lab_reports).where((lab_reports.c.report_date==report_date) &(lab_reports.c.registration_id==patientID)
                                   &(lab_reports.c.reportname==report_name))
    return stmt

def safe_parse_date(date_str, fmt="%d/%m/%Y"):
    try:
        # Try parsing the date
        return datetime.strptime(date_str, fmt).date()
    except ValueError:       
        return None  # Or set a fallback: datetime.today().date()

def safe_parse_datetime(dt_str):
   cleaned = re.sub(r'\s+', ' ', dt_str).strip()
   cleaned = re.sub(r'[^0-9:/\sAPMapm]', '', cleaned).strip()

    # Optional: remove slash before time if needed
   cleaned = cleaned.replace(" / ", " ")

    # Step 2: Extract only the datetime part (dd/mm/yyyy hh:mmAM/PM)
   match = re.search(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}[APMapm]{2}", cleaned)
   if match:
    dt_str2 = match.group(0)  # e.g., "21/01/2015 08:36AM"
    timestamp_obj = datetime.strptime(dt_str2, "%d/%m/%Y %I:%M%p")
   return timestamp_obj
    
def saveStooldata(report_name,parsed_data,test_results):
      
    lab_reports=metadata.tables["lab_reports"]
    stoolReport=metadata.tables["stool_routine_results"]
    try:
     with engine.begin() as conn:       
        
        # Step 1: Insert metadata into lab_reports
            registration_id=parsed_data.get("Registration Id"),
            report_date=safe_parse_datetime(parsed_data.get("Collection Date/Time")).date()
            chk_stmt=check_data_exists(registration_id,report_date,report_name)
            result_chk=conn.execute(chk_stmt).fetchone() #check duplicate entry
            if not result_chk :
                    report_stmt = insert(lab_reports).values(
                    reportname=report_name,
                    registration_id=registration_id,
                    registration_datetime=safe_parse_datetime(parsed_data.get("Registration Date/Time")),
                    patient_name=parsed_data.get("Patient Name"),
                    collection_datetime=safe_parse_datetime(parsed_data.get("Collection Date/Time")),
                    reporting_datetime=safe_parse_datetime(parsed_data.get("Reporting Date/Time")),
                    referred_by=parsed_data.get("Referred By"),
                    age_sex=parsed_data.get("Age/Sex"),
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
                    result = conn.execute(report_stmt)
            else :
                print("Duplicate rows")
                        

            

    except (SQLAlchemyError, DBAPIError) as e:
        print(" Transaction failed and was rolled back:", e) 

def saveUrinedata(report_name,parsed_data,test_results):
      
    lab_reports=metadata.tables["lab_reports"]
    urineReport=metadata.tables["urine_routine_results"]
    try:
     with engine.begin() as conn:       
        
        # Step 1: Insert metadata into lab_reports
            registration_id=parsed_data.get("Registration Id"),
            report_date=safe_parse_datetime(parsed_data.get("Collection Date/Time")).date()
            chk_stmt=check_data_exists(registration_id,report_date,report_name)
            result_chk=conn.execute(chk_stmt).fetchone() #check duplicate entry
            if not result_chk :
                    report_stmt = insert(lab_reports).values(
                    reportname=report_name,
                    registration_id=registration_id,
                    registration_datetime=safe_parse_datetime(parsed_data.get("Registration Date/Time")),
                    patient_name=parsed_data.get("Patient Name"),
                    collection_datetime=safe_parse_datetime(parsed_data.get("Collection Date/Time")),
                    reporting_datetime=safe_parse_datetime(parsed_data.get("Reporting Date/Time")),
                    referred_by=parsed_data.get("Referred By"),
                    age_sex=parsed_data.get("Age/Sex"),
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
                    result = conn.execute(report_stmt)
            else :
                print("Duplicate Rows")        

            

    except (SQLAlchemyError, DBAPIError) as e:
        print(" Transaction failed and was rolled back:", e)  

def saveLipidProfileData(patientdata,parsed_data,report_name,expected_fields):
    lab_reports=metadata.tables["lab_reports"]
    lipidReport=metadata.tables["lipid_profile_results"]
    try:
     with engine.begin() as conn:       
            
        # Step 1: Insert metadata into lab_reports
            registration_id=patientdata.get("Registration Id") or 1652960012
            report_date_chk=safe_parse_date(patientdata.get("Collection Date/Time"))
            report_date=report_date_chk or '2012-02-11'
            chk_stmt=check_data_exists(registration_id,report_date,report_name)
            result_chk=conn.execute(chk_stmt).fetchone() #check duplicate entry
            if not result_chk :
                    report_stmt = insert(lab_reports).values(
                    reportname=report_name,            
                    registration_id=registration_id,
                    #registration_datetime=safe_parse_datetime(patientdata.get("Registration Date/Time")),
                    patient_name=patientdata.get("Patient Name"),
                    #collection_datetime=safe_parse_datetime(patientdata.get("Collection Date/Time")),
                    #reporting_datetime=safe_parse_datetime(patientdata.get("Reporting Date/Time")),
                    referred_by=patientdata.get("Referred By"),
                    age_sex=patientdata.get("Age/Sex"),
                    report_date=report_date
                    )
                    result = conn.execute(report_stmt)
                
                    insert_report_id = result.inserted_primary_key[0]           
                    #conn.commit()
                    print('A',insert_report_id)

                    field_map = {
                    "triglycerides": "Triglycerides",
                    "total_cholesterol": "Total Cholesterol",
                    "hdl_cholesterol": "HDL Cholesterol",
                    "ldl_cholesterol": "LDL Cholesterol",
                    "vldl": "VLDL",
                    "ldl_hdl_ratio": "LDL/HDL Ratio",
                    "tcl_hdl_ratio": "TC/HDL Ratio"
                    }

                    data_to_insert = {
                        key: float(parsed_data.get(field_map[key], 0)) for key in expected_fields
                    }
                    data_to_insert['report_id'] = insert_report_id

                    # Insert into DB
                    
                    stmt = insert(lipidReport).values(data_to_insert)
                    conn.execute(stmt)
                    conn.commit()
                    print(data_to_insert)
            else :
                print("Duplicate Row")        

    except (SQLAlchemyError, DBAPIError) as e:
        print(" Transaction failed and was rolled back:", e) 


def saveGlucoseData(patientdata,parsed_data,report_name,expected_fields):
    lab_reports=metadata.tables["lab_reports"]
    glucoseReport=metadata.tables["glucose_results"]
    try:
     with engine.begin() as conn:       
        
        # Step 1: Insert metadata into lab_reports
            registration_id=patientdata.get("Registration Id") or 1652960012
            report_date_chk=safe_parse_date(patientdata.get("Collection Date/Time"))
            report_date=report_date_chk or '2012-02-11'
            chk_stmt=check_data_exists(registration_id,report_date,report_name)
            result_chk=conn.execute(chk_stmt).fetchone()
            #print(result_chk)
            if not result_chk :
                    report_stmt = insert(lab_reports).values(
                    reportname=report_name,
                    registration_id=registration_id,
                    #registration_datetime=safe_parse_datetime(patientdata.get("Registration Date/Time")),
                    patient_name=patientdata.get("Patient Name"),
                    #collection_datetime=safe_parse_datetime(patientdata.get("Collection Date/Time")),
                    #reporting_datetime=safe_parse_datetime(patientdata.get("Reporting Date/Time")),
                    referred_by=patientdata.get("Referred By"),
                    age_sex=patientdata.get("Age/Sex"),
                    report_date=report_date
                    )
                    result = conn.execute(report_stmt)
                
                    insert_report_id = result.inserted_primary_key[0]           
                    #conn.commit()
                    print('A',insert_report_id)                    

                    data_to_insert = {
                        key: parsed_data.get(key, 0) for key in expected_fields
                    }
                    data_to_insert['report_id'] = insert_report_id

                    # Insert into DB
                    
                    stmt = insert(glucoseReport).values(data_to_insert)
                    conn.execute(stmt)
                    conn.commit()
                    print(data_to_insert)
            else :
                print("duplicate Rows")        

    except (SQLAlchemyError, DBAPIError) as e:
        print(" Transaction failed and was rolled back:", e) 


def saveStooldata(report_name,parsed_data,test_results):
      
    lab_reports=metadata.tables["lab_reports"]
    stoolReport=metadata.tables["stool_routine_results"]
    try:
     with engine.begin() as conn:       
        
        # Step 1: Insert metadata into lab_reports
            registration_id=parsed_data.get("Registration Id"),
            report_date=safe_parse_datetime(parsed_data.get("Collection Date/Time")).date()
            chk_stmt=check_data_exists(registration_id,report_date,report_name)
            result_chk=conn.execute(chk_stmt).fetchone() #check duplicate entry
            if not result_chk :
                    report_stmt = insert(lab_reports).values(
                    reportname=report_name,
                    registration_id=registration_id,
                    registration_datetime=safe_parse_datetime(parsed_data.get("Registration Date/Time")),
                    patient_name=parsed_data.get("Patient Name"),
                    collection_datetime=safe_parse_datetime(parsed_data.get("Collection Date/Time")),
                    reporting_datetime=safe_parse_datetime(parsed_data.get("Reporting Date/Time")),
                    referred_by=parsed_data.get("Referred By"),
                    age_sex=parsed_data.get("Age/Sex"),
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
                    result = conn.execute(report_stmt)
            else :
                print("Duplicate rows")
                        

            

    except (SQLAlchemyError, DBAPIError) as e:
        print(" Transaction failed and was rolled back:", e) 

