import os
import uuid
from datetime import date, datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from neo4j import GraphDatabase

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(page_title="Healthcare Dynamic EHR", page_icon="🏥", layout="wide")

# ============================================================
# 2. NEO4J CONNECTION
# Set these environment variables, or put them in .streamlit/secrets.toml.
# ============================================================
def setting(name, default=None):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)

NEO4J_URI = setting("NEO4J_URI", "neo4j+s://164c09dc.databases.neo4j.io")
NEO4J_USERNAME = setting("NEO4J_USERNAME", "164c09dc")
NEO4J_PASSWORD = setting("NEO4J_PASSWORD", "SWSlww4obSza5Jm90c0ZtvFe4REuE_0cIJmSe9Kkx4E")
NEO4J_DATABASE = setting("NEO4J_DATABASE", "164c09dc")

if not NEO4J_PASSWORD:
    st.error("Neo4j password is missing. Set NEO4J_PASSWORD in environment variables or .streamlit/secrets.toml.")
    st.stop()

@st.cache_resource
def get_driver():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    driver.verify_connectivity()
    return driver

try:
    driver = get_driver()
except Exception as exc:
    st.error("Could not connect to Neo4j. Check that Neo4j is running and your URI, username, password, and database are correct.")
    st.exception(exc)
    st.stop()

def run_query(query, params=None, write=False):
    """Run a Cypher query and return records as dictionaries."""
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(query, params or {})
        records = [record.data() for record in result]
        if write:
            result.consume()
        return records

def read_table(query, params=None):
    return pd.DataFrame(run_query(query, params))

def new_id():
    return str(uuid.uuid4())

def get_patients():
    return read_table("""
        MATCH (p:Patient)
        RETURN p.id AS id, p.name AS name, p.age AS age, p.gender AS gender,
               p.phone AS phone, p.created_at AS created_at
        ORDER BY p.created_at DESC
    """)

def patient_choices():
    patients = get_patients()
    return {f"{row['id'][:8]} — {row['name']}": row['id'] for _, row in patients.iterrows()}

def choose_patient(label="Select Patient"):
    choices = patient_choices()
    if not choices:
        st.warning("Please add a patient first in the Patients section.")
        return None
    selected = st.selectbox(label, list(choices.keys()))
    return choices[selected]

# Create constraints (safe to run each time the app starts).
run_query("CREATE CONSTRAINT patient_id_unique IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE", write=True)
for label in ["Vital", "LabReport", "ClinicalNote", "Medication"]:
    run_query(f"CREATE CONSTRAINT {label.lower()}_id_unique IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE", write=True)

# ============================================================
# 3. OPTIONAL FICTIONAL DEMO DATA
# ============================================================
if not run_query("MATCH (p:Patient) RETURN p.id AS id LIMIT 1"):
    rahul = new_id()
    priya = new_id()
    run_query("CREATE (:Patient {id:$id, name:$name, age:45, gender:'Male', phone:'9000000001', created_at:'2026-10-01'})", {"id": rahul, "name": "Rahul Sharma"}, True)
    run_query("CREATE (:Patient {id:$id, name:$name, age:32, gender:'Female', phone:'9000000002', created_at:'2026-10-01'})", {"id": priya, "name": "Priya Sharma"}, True)
    for d, hr, temp, spo2, sys, dia in [("2026-10-01",78,98.4,98,120,80),("2026-10-02",82,98.6,97,125,82),("2026-10-03",88,99.0,96,130,85),("2026-10-04",84,98.7,97,128,83),("2026-10-05",80,98.5,98,122,80)]:
        run_query("MATCH (p:Patient {id:$pid}) CREATE (v:Vital {id:$id, date:$date, heart_rate:$hr, temperature:$temp, spo2:$spo2, systolic_bp:$sys, diastolic_bp:$dia})-[:BELONGS_TO]->(p)", {"pid":rahul,"id":new_id(),"date":d,"hr":hr,"temp":temp,"spo2":spo2,"sys":sys,"dia":dia}, True)
    for name, result, unit, ref in [("Hemoglobin","13.5","g/dL","13-17"),("Glucose","105","mg/dL","70-110"),("Cholesterol","180","mg/dL","125-200")]:
        run_query("MATCH (p:Patient {id:$pid}) CREATE (l:LabReport {id:$id, test_name:$name, result:$result, unit:$unit, reference_range:$ref, test_date:'2026-10-01'})-[:BELONGS_TO]->(p)", {"pid":rahul,"id":new_id(),"name":name,"result":result,"unit":unit,"ref":ref}, True)
    for note, doctor, created in [("Patient reported mild fever and fatigue.","Dr. Kumar","2026-10-01"),("Patient condition improved. Continue monitoring.","Dr. Kumar","2026-10-03")]:
        run_query("MATCH (p:Patient {id:$pid}) CREATE (n:ClinicalNote {id:$id, note:$note, doctor:$doctor, created_at:$created})-[:BELONGS_TO]->(p)", {"pid":rahul,"id":new_id(),"note":note,"doctor":doctor,"created":created}, True)
    for med, dosage, freq, start, end, status in [("Paracetamol","500 mg","2 times/day","2026-10-01","2026-10-05","Completed"),("Vitamin D","1000 IU","1 time/day","2026-10-01","","Active")]:
        run_query("MATCH (p:Patient {id:$pid}) CREATE (m:Medication {id:$id, medicine_name:$med, dosage:$dosage, frequency:$freq, start_date:$start, end_date:$end, status:$status})-[:BELONGS_TO]->(p)", {"pid":rahul,"id":new_id(),"med":med,"dosage":dosage,"freq":freq,"start":start,"end":end,"status":status}, True)

# ============================================================
# 4. SIDEBAR NAVIGATION
# ============================================================
st.sidebar.title("🏥 Healthcare EHR")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Patients", "Add Vitals", "Lab Reports", "Clinical Notes", "Medications", "Remove Record", "Analytics"])
st.sidebar.divider()
st.sidebar.caption("Database: Neo4j")
st.sidebar.caption(NEO4J_DATABASE)

# ============================================================
# 5. DASHBOARD
# ============================================================
if menu == "Dashboard":
    st.title("🏥 Healthcare Dynamic EHR")
    st.write("Electronic Health Record & Clinical Record Manager")
    st.info("Demo data is fictional. This application is for demonstration, not clinical decision-making.")
    patients = get_patients()
    counts = run_query("""OPTIONAL MATCH (v:Vital) WITH count(v) AS vitals OPTIONAL MATCH (l:LabReport) WITH vitals,count(l) AS labs OPTIONAL MATCH (m:Medication) RETURN vitals,labs,count(m) AS meds""")[0]
    c1,c2,c3,c4=st.columns(4)
    c1.metric("👤 Patients",len(patients))
    c2.metric("🩺 Vital Records",int(counts["vitals"]))
    c3.metric("🧪 Lab Reports",int(counts["labs"]))
    c4.metric("💊 Medications",int(counts["meds"]))
    st.subheader("Registered Patients")
    st.dataframe(patients,use_container_width=True,hide_index=True)

# ============================================================
# 6. PATIENT MANAGEMENT
# ============================================================
elif menu == "Patients":
    st.title("👤 Patient Management")
    with st.form("patient_form",clear_on_submit=True):
        name=st.text_input("Patient Name")
        age=st.number_input("Age",min_value=0,max_value=120,value=25)
        gender=st.selectbox("Gender",["Male","Female","Other"])
        phone=st.text_input("Phone Number")
        submitted=st.form_submit_button("Add Patient")
    if submitted:
        if not name.strip(): st.error("Please enter the patient name.")
        else:
            run_query("CREATE (:Patient {id:$id,name:$name,age:$age,gender:$gender,phone:$phone,created_at:$created})",{"id":new_id(),"name":name.strip(),"age":int(age),"gender":gender,"phone":phone.strip(),"created":datetime.now().strftime("%Y-%m-%d %H:%M:%S")},True)
            st.success("Patient added successfully!"); st.rerun()
    st.subheader("Patient List")
    st.dataframe(get_patients(),use_container_width=True,hide_index=True)

# ============================================================
# 7. ADD VITALS
# ============================================================
elif menu == "Add Vitals":
    st.title("🩺 Add Patient Vitals")
    patient_id=choose_patient()
    if patient_id:
        with st.form("vitals_form",clear_on_submit=True):
            vital_date=st.date_input("Date",value=date.today())
            heart_rate=st.number_input("Heart Rate (BPM)",0,250,80)
            temperature=st.number_input("Temperature (°F)",80.0,110.0,98.6,step=0.1)
            spo2=st.number_input("SpO₂ (%)",0,100,98)
            systolic=st.number_input("Systolic BP",0,250,120)
            diastolic=st.number_input("Diastolic BP",0,200,80)
            submitted=st.form_submit_button("Save Vitals")
        if submitted:
            run_query("MATCH (p:Patient {id:$pid}) CREATE (v:Vital {id:$id,date:$date,heart_rate:$hr,temperature:$temp,spo2:$spo2,systolic_bp:$sys,diastolic_bp:$dia})-[:BELONGS_TO]->(p)",{"pid":patient_id,"id":new_id(),"date":str(vital_date),"hr":heart_rate,"temp":temperature,"spo2":spo2,"sys":systolic,"dia":diastolic},True)
            st.success("Vitals saved successfully!"); st.rerun()
        st.subheader("Vital History")
        vitals=read_table("MATCH (v:Vital)-[:BELONGS_TO]->(p:Patient {id:$pid}) RETURN v.id AS id,v.date AS date,v.heart_rate AS heart_rate,v.temperature AS temperature,v.spo2 AS spo2,v.systolic_bp AS systolic_bp,v.diastolic_bp AS diastolic_bp ORDER BY date DESC",{"pid":patient_id})
        st.dataframe(vitals.drop(columns=["id"],errors="ignore"),use_container_width=True,hide_index=True)

# ============================================================
# 8. LAB REPORTS
# ============================================================
elif menu == "Lab Reports":
    st.title("🧪 Laboratory Reports")
    patient_id=choose_patient()
    if patient_id:
        with st.form("lab_form",clear_on_submit=True):
            test_name=st.text_input("Test Name"); result=st.text_input("Result"); unit=st.text_input("Unit"); reference_range=st.text_input("Reference Range"); test_date=st.date_input("Test Date",value=date.today())
            submitted=st.form_submit_button("Save Lab Report")
        if submitted:
            if not test_name.strip(): st.error("Please enter the test name.")
            else:
                run_query("MATCH (p:Patient {id:$pid}) CREATE (l:LabReport {id:$id,test_name:$name,result:$result,unit:$unit,reference_range:$ref,test_date:$date})-[:BELONGS_TO]->(p)",{"pid":patient_id,"id":new_id(),"name":test_name.strip(),"result":result.strip(),"unit":unit.strip(),"ref":reference_range.strip(),"date":str(test_date)},True)
                st.success("Lab report saved!"); st.rerun()
        st.subheader("Lab Report History")
        labs=read_table("MATCH (l:LabReport)-[:BELONGS_TO]->(p:Patient {id:$pid}) RETURN l.test_name AS test_name,l.result AS result,l.unit AS unit,l.reference_range AS reference_range,l.test_date AS test_date ORDER BY test_date DESC",{"pid":patient_id})
        st.dataframe(labs,use_container_width=True,hide_index=True)

# ============================================================
# 9. CLINICAL NOTES
# ============================================================
elif menu == "Clinical Notes":
    st.title("📝 Clinical Notes")
    patient_id=choose_patient()
    if patient_id:
        with st.form("notes_form",clear_on_submit=True):
            doctor=st.text_input("Doctor Name"); note=st.text_area("Clinical Note")
            submitted=st.form_submit_button("Save Note")
        if submitted:
            if not note.strip(): st.error("Please enter a clinical note.")
            else:
                run_query("MATCH (p:Patient {id:$pid}) CREATE (n:ClinicalNote {id:$id,note:$note,doctor:$doctor,created_at:$created})-[:BELONGS_TO]->(p)",{"pid":patient_id,"id":new_id(),"note":note.strip(),"doctor":doctor.strip(),"created":datetime.now().strftime("%Y-%m-%d %H:%M:%S")},True)
                st.success("Clinical note saved!"); st.rerun()
        notes=run_query("MATCH (n:ClinicalNote)-[:BELONGS_TO]->(p:Patient {id:$pid}) RETURN n.doctor AS doctor,n.note AS note,n.created_at AS created_at ORDER BY created_at DESC",{"pid":patient_id})
        st.subheader("Previous Notes")
        if not notes: st.info("No clinical notes found.")
        else:
            for row in notes:
                with st.expander(f"{row.get('doctor') or 'Doctor'} — {row.get('created_at')}"): st.write(row.get("note",""))

# ============================================================
# 10. MEDICATIONS
# ============================================================
elif menu == "Medications":
    st.title("💊 Medication History")
    patient_id=choose_patient()
    if patient_id:
        with st.form("medication_form",clear_on_submit=True):
            medicine=st.text_input("Medicine Name"); dosage=st.text_input("Dosage"); frequency=st.text_input("Frequency")
            start_date=st.date_input("Start Date",value=date.today()); has_end_date=st.checkbox("Specify an end date")
            end_date=st.date_input("End Date",value=date.today()) if has_end_date else None
            status=st.selectbox("Status",["Active","Completed","Stopped"])
            submitted=st.form_submit_button("Save Medication")
        if submitted:
            if not medicine.strip(): st.error("Please enter the medicine name.")
            else:
                run_query("MATCH (p:Patient {id:$pid}) CREATE (m:Medication {id:$id,medicine_name:$medicine,dosage:$dosage,frequency:$frequency,start_date:$start,end_date:$end,status:$status})-[:BELONGS_TO]->(p)",{"pid":patient_id,"id":new_id(),"medicine":medicine.strip(),"dosage":dosage.strip(),"frequency":frequency.strip(),"start":str(start_date),"end":str(end_date) if end_date else "","status":status},True)
                st.success("Medication saved!"); st.rerun()
        meds=read_table("MATCH (m:Medication)-[:BELONGS_TO]->(p:Patient {id:$pid}) RETURN m.medicine_name AS medicine_name,m.dosage AS dosage,m.frequency AS frequency,m.start_date AS start_date,m.end_date AS end_date,m.status AS status ORDER BY start_date DESC",{"pid":patient_id})
        st.dataframe(meds,use_container_width=True,hide_index=True)

# ============================================================
# 11. REMOVE RECORDS
# ============================================================
elif menu == "Remove Record":
    st.title("🗑️ Remove Record")
    st.warning("Deletion is permanent. Use fictional/demo data while testing.")
    delete_type=st.selectbox("Select Record Type",["Patient","Vital Record","Lab Report","Clinical Note","Medication"])
    labels={"Vital Record":("Vital","HAS_VITAL"),"Lab Report":("LabReport","HAS_LAB_REPORT"),"Clinical Note":("ClinicalNote","HAS_CLINICAL_NOTE"),"Medication":("Medication","HAS_MEDICATION")}
    if delete_type == "Patient":
        records=get_patients()
        if records.empty: st.info("No patients available.")
        else:
            st.dataframe(records.drop(columns=["id"],errors="ignore"),use_container_width=True,hide_index=True)
            options={f"{r['name']} — {r['id'][:8]}":r['id'] for _,r in records.iterrows()}
            selected=st.selectbox("Select Patient to Remove",list(options.keys()))
            confirm=st.checkbox("I understand the patient and related records will be deleted.")
            if st.button("Delete Patient",type="primary"):
                if not confirm: st.error("Please confirm deletion first.")
                else:
                    run_query("MATCH (p:Patient {id:$id}) OPTIONAL MATCH (n)-[:BELONGS_TO]->(p) DETACH DELETE n,p",{"id":options[selected]},True)
                    st.success("Patient and related records deleted."); st.rerun()
    else:
        label=labels[delete_type][0]
        records=read_table(f"MATCH (n:{label})-[:BELONGS_TO]->(p:Patient) RETURN n.id AS id,p.name AS patient_name,p.id AS patient_id,properties(n) AS props ORDER BY n.id")
        if records.empty: st.info(f"No {delete_type.lower()} records available.")
        else:
            def record_label(row):
                props=row["props"] or {}
                detail=props.get("medicine_name") or props.get("test_name") or props.get("date") or props.get("doctor") or props.get("note") or label
                return f"{detail} — {row['patient_name']} — {row['id'][:8]}"
            options={record_label(row):row["id"] for _,row in records.iterrows()}
            st.dataframe(pd.DataFrame([{"patient":r["patient_name"],**(r["props"] or {})} for _,r in records.iterrows()]).drop(columns=["id"],errors="ignore"),use_container_width=True,hide_index=True)
            selected=st.selectbox(f"Select {delete_type} to Remove",list(options.keys()))
            confirm=st.checkbox(f"I understand this {delete_type.lower()} will be permanently deleted.")
            if st.button(f"Delete {delete_type}",type="primary"):
                if not confirm: st.error("Please confirm deletion first.")
                else:
                    run_query(f"MATCH (n:{label} {{id:$id}}) DETACH DELETE n",{"id":options[selected]},True)
                    st.success(f"{delete_type} deleted successfully."); st.rerun()

# ============================================================
# 12. ANALYTICS
# ============================================================
elif menu == "Analytics":
    st.title("📊 Patient Analytics")
    patient_id=choose_patient()
    if patient_id:
        vitals=read_table("MATCH (v:Vital)-[:BELONGS_TO]->(p:Patient {id:$pid}) RETURN v.id AS id,v.date AS date,v.heart_rate AS heart_rate,v.temperature AS temperature,v.spo2 AS spo2,v.systolic_bp AS systolic_bp,v.diastolic_bp AS diastolic_bp ORDER BY date",{"pid":patient_id})
        if vitals.empty: st.info("No vital records available for this patient.")
        else:
            st.subheader("❤️ Heart Rate Trend")
            st.plotly_chart(px.line(vitals,x="date",y="heart_rate",markers=True,title="Heart Rate Over Time"),use_container_width=True)
            st.subheader("🩸 Blood Pressure Trend")
            st.plotly_chart(px.line(vitals,x="date",y=["systolic_bp","diastolic_bp"],markers=True,title="Blood Pressure Over Time"),use_container_width=True)
            st.subheader("🫁 SpO₂ Trend")
            st.plotly_chart(px.line(vitals,x="date",y="spo2",markers=True,title="SpO₂ Over Time"),use_container_width=True)
            st.subheader("🌡️ Temperature Trend")
            st.plotly_chart(px.line(vitals,x="date",y="temperature",markers=True,title="Temperature Over Time"),use_container_width=True)

# ============================================================
# 13. FOOTER
# ============================================================
st.sidebar.divider()
st.sidebar.caption("Healthcare Dynamic EHR")
st.sidebar.caption("Python • Streamlit • Neo4j • Pandas • Plotly")
