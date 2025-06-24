def get_report_name(ocr_text):
    known_reports = [
        "Urine Routine", "Complete Blood Count", "CBC", "Liver Function Test",
        "Thyroid Profile", "Blood Sugar", "Lipid Profile", "Kidney Function Test",
        "Urine Culture", "Stool Routine", "Hematology", "Blood Test", "LIPID PROFILE"
    ]

    lines = ocr_text.splitlines()
    clean_lines = [line.strip().lower() for line in lines if line.strip()]  # normalize to lowercase

    # Step 1: Match against known report names
    for line in clean_lines[:20]:
        for report in known_reports:
            if report.lower() in line:
                return report  # return original casing from list

    # Step 2: Heuristic fallback — standalone lines with title case
    for line in lines:
        clean_line = line.strip()
        if (
            clean_line.istitle() and
            1 <= len(clean_line.split()) <= 4 and
            ':' not in clean_line and
            not any(word in clean_line.lower() for word in ['name', 'date', 'patient', 'age'])
        ):
            return clean_line

    return "Unknown Report"

ocr_txt="""OME

APOORVA

DIAGNOSTIC CENTRE
AN ISO 9001 : 2008
CERTIFIED DIAGNOSTIC CENTRE
325, 1st Floor, C.M.H. Road, Indiranagar, Bangalore - 560 038.
Phone : 25257343, 25285652 Fax : 080 - 25286442 E-mail : apoorvadiagnostics@gmail.com

 

Reg. No. L 16641 Bill No. Date: 11/02/2012 Page | of |

Name: Mr. FREDRIC ANTONY Ref. by:
Age: 41 Year(s) Sex: Male Corporate: NON CORPORATE

Report Date 41/02/2012 14:20
Reference Range

C/o SELF

Test Name Result
BIOCHEMISTRY

GLUCOSE FASTING & POSTPRANDIAL

FASTING BLOOD GLUCOSE (Hexokinase) 91 mg/dL Adult : 70 - 110
Children : 60 - 100 mg/dL

Urine sugar NIL
POST PRANDIAL BLOOD GLUCOSE 111 mg/dL 70 - 150 mg/dL
(Hexokinase)
Urine sugar NIL
LIPID PROFILE
ThkIGLYCERIDES (Lipase) 100 mg/dL Normal : < 150
Boderline high : 151 - 199
High : 200 - 499
Very high : > 500 mg/dL
TOTAL CHOLESTEROL (Cholestrol oxidase) 174 mg/dL Recommended (desirable) : < 200
Moderate risk : 200 - 239
High risk: > 240 mg/dL
H.D.1. CHOLESTROL (Phosphotungstate/Mg) 27 mg/dL 37 - 75 mg/dL
L.D.L. CHOLESTEROL 127 mg/dL Optimal: < 100
Near / above optimal : 100 - 129
borderline high: 130 - 159
, high risk: 160 - 189
V.L.D.L 20 mg/dL 10 - 40 mg/dL
LDL/HDL RATIO 4.7 Less than 4.0
TCAIDL RATIO 6.4 Less than 6.0
Note:
SB. BR aK
eo
Dr.B. Shivappa.MD.,DCP
Pathologist
------ End of Report —---

V Weekdays : 7 am to 8 pm Fully Automated Analyzers with Bidirectional Interface
WORKING Hours: Sunday |

} 7 am to 12 noon This report Is not valid for any medicolegal purpose
. Holidays . '"""
r=get_report_name(ocr_txt)
print(r)