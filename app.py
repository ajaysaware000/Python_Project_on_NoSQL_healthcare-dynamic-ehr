import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Healthcare Dynamic EHR",
    page_icon="🏥",
    layout="wide"
)


# ============================================================
# DATABASE
# ============================================================

DATABASE_NAME = "healthcare_ehr.db"


def get_connection():
    return sqlite3.connect(
        DATABASE_NAME,
        check_same_thread=False
    )


conn = get_connection()
cursor = conn.cursor()


# ============================================================
# CREATE TABLES
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    phone TEXT,
    created_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS vitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    date TEXT,
    heart_rate INTEGER,
    temperature REAL,
    spo2 INTEGER,
    systolic_bp INTEGER,
    diastolic_bp INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS lab_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    test_name TEXT,
    result TEXT,
    unit TEXT,
    reference_range TEXT,
    test_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS clinical_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    note TEXT,
    doctor TEXT,
    created_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS medications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    medicine_name TEXT,
    dosage TEXT,
    frequency TEXT,
    start_date TEXT,
    end_date TEXT,
    status TEXT
)
""")

conn.commit()


# ============================================================
# ADD SAMPLE DATA ONLY IF DATABASE IS EMPTY
# ============================================================

patient_count = cursor.execute(
    "SELECT COUNT(*) FROM patients"
).fetchone()[0]


if patient_count == 0:

    cursor.execute("""
    INSERT INTO patients
    (name, age, gender, phone, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        "Rahul Sharma",
        45,
        "Male",
        "9876543210",
        "2026-10-01"
    ))

    cursor.execute("""
    INSERT INTO patients
    (name, age, gender, phone, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        "Priya Sharma",
        32,
        "Female",
        "9876543211",
        "2026-10-01"
    ))

    conn.commit()

    rahul_id = cursor.execute(
        "SELECT id FROM patients WHERE name = ?",
        ("Rahul Sharma",)
    ).fetchone()[0]


    # --------------------------------------------------------
    # SAMPLE VITALS
    # --------------------------------------------------------

    vitals = [
        (rahul_id, "2026-10-01", 78, 98.4, 98, 120, 80),
        (rahul_id, "2026-10-02", 82, 98.6, 97, 125, 82),
        (rahul_id, "2026-10-03", 88, 99.0, 96, 130, 85),
        (rahul_id, "2026-10-04", 84, 98.7, 97, 128, 83),
        (rahul_id, "2026-10-05", 80, 98.5, 98, 122, 80)
    ]

    cursor.executemany("""
    INSERT INTO vitals
    (
        patient_id,
        date,
        heart_rate,
        temperature,
        spo2,
        systolic_bp,
        diastolic_bp
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, vitals)


    # --------------------------------------------------------
    # SAMPLE LAB REPORTS
    # --------------------------------------------------------

    labs = [
        (
            rahul_id,
            "Hemoglobin",
            "13.5",
            "g/dL",
            "13-17",
            "2026-10-01"
        ),
        (
            rahul_id,
            "Glucose",
            "105",
            "mg/dL",
            "70-110",
            "2026-10-01"
        ),
        (
            rahul_id,
            "Cholesterol",
            "180",
            "mg/dL",
            "125-200",
            "2026-10-01"
        )
    ]

    cursor.executemany("""
    INSERT INTO lab_reports
    (
        patient_id,
        test_name,
        result,
        unit,
        reference_range,
        test_date
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, labs)


    # --------------------------------------------------------
    # SAMPLE CLINICAL NOTES
    # --------------------------------------------------------

    notes = [
        (
            rahul_id,
            "Patient reported mild fever and fatigue.",
            "Dr. Kumar",
            "2026-10-01"
        ),
        (
            rahul_id,
            "Patient condition improved. Continue monitoring.",
            "Dr. Kumar",
            "2026-10-03"
        )
    ]

    cursor.executemany("""
    INSERT INTO clinical_notes
    (
        patient_id,
        note,
        doctor,
        created_at
    )
    VALUES (?, ?, ?, ?)
    """, notes)


    # --------------------------------------------------------
    # SAMPLE MEDICATIONS
    # --------------------------------------------------------

    medications = [
        (
            rahul_id,
            "Paracetamol",
            "500 mg",
            "2 times/day",
            "2026-10-01",
            "2026-10-05",
            "Completed"
        ),
        (
            rahul_id,
            "Vitamin D",
            "1000 IU",
            "1 time/day",
            "2026-10-01",
            "",
            "Active"
        )
    ]

    cursor.executemany("""
    INSERT INTO medications
    (
        patient_id,
        medicine_name,
        dosage,
        frequency,
        start_date,
        end_date,
        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, medications)

    conn.commit()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🏥 Healthcare EHR")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Patients",
        "Add Vitals",
        "Lab Reports",
        "Clinical Notes",
        "Medications",
        "Remove Record",
        "Analytics"
    ]
)


# ============================================================
# LOAD PATIENTS
# ============================================================

patients = pd.read_sql_query(
    "SELECT * FROM patients ORDER BY id",
    conn
)


# ============================================================
# DASHBOARD
# ============================================================

if menu == "Dashboard":

    st.title("🏥 Healthcare Dynamic EHR")

    st.write(
        "Electronic Health Record & Multi-Modal "
        "Clinical Record Manager"
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    total_patients = len(patients)

    total_vitals = pd.read_sql_query(
        "SELECT * FROM vitals",
        conn
    ).shape[0]

    total_labs = pd.read_sql_query(
        "SELECT * FROM lab_reports",
        conn
    ).shape[0]

    total_medications = pd.read_sql_query(
        "SELECT * FROM medications",
        conn
    ).shape[0]

    col1.metric(
        "👤 Patients",
        total_patients
    )

    col2.metric(
        "🩺 Vital Records",
        total_vitals
    )

    col3.metric(
        "🧪 Lab Reports",
        total_labs
    )

    col4.metric(
        "💊 Medications",
        total_medications
    )

    st.divider()

    st.subheader("👥 Registered Patients")

    st.dataframe(
        patients,
        use_container_width=True
    )


# ============================================================
# PATIENTS
# ============================================================

elif menu == "Patients":

    st.title("👤 Patient Management")

    st.subheader("Add New Patient")

    with st.form("patient_form"):

        name = st.text_input(
            "Patient Name"
        )

        age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=25
        )

        gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"]
        )

        phone = st.text_input(
            "Phone Number"
        )

        submitted = st.form_submit_button(
            "Add Patient"
        )

        if submitted:

            if name.strip() == "":

                st.error(
                    "Please enter patient name."
                )

            else:

                cursor.execute("""
                INSERT INTO patients
                (
                    name,
                    age,
                    gender,
                    phone,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """, (
                    name,
                    age,
                    gender,
                    phone,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ))

                conn.commit()

                st.success(
                    "Patient added successfully!"
                )

                st.rerun()

    st.divider()

    st.subheader("Patient List")

    patients = pd.read_sql_query(
        "SELECT * FROM patients ORDER BY id DESC",
        conn
    )

    st.dataframe(
        patients,
        use_container_width=True
    )


# ============================================================
# ADD VITALS
# ============================================================

elif menu == "Add Vitals":

    st.title("🩺 Add Patient Vitals")

    if patients.empty:

        st.warning(
            "Please add a patient first."
        )

    else:

        patient_options = {
            f"{row['id']} - {row['name']}":
            row["id"]
            for _, row in patients.iterrows()
        }

        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_options.keys())
        )

        patient_id = patient_options[
            selected_patient
        ]

        with st.form("vitals_form"):

            date = st.date_input(
                "Date"
            )

            heart_rate = st.number_input(
                "Heart Rate (BPM)",
                min_value=0,
                max_value=250,
                value=80
            )

            temperature = st.number_input(
                "Temperature (°F)",
                min_value=80.0,
                max_value=110.0,
                value=98.6
            )

            spo2 = st.number_input(
                "SpO₂ (%)",
                min_value=0,
                max_value=100,
                value=98
            )

            systolic = st.number_input(
                "Systolic BP",
                min_value=0,
                max_value=250,
                value=120
            )

            diastolic = st.number_input(
                "Diastolic BP",
                min_value=0,
                max_value=200,
                value=80
            )

            submitted = st.form_submit_button(
                "Save Vitals"
            )

            if submitted:

                cursor.execute("""
                INSERT INTO vitals
                (
                    patient_id,
                    date,
                    heart_rate,
                    temperature,
                    spo2,
                    systolic_bp,
                    diastolic_bp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    patient_id,
                    str(date),
                    heart_rate,
                    temperature,
                    spo2,
                    systolic,
                    diastolic
                ))

                conn.commit()

                st.success(
                    "Vitals saved successfully!"
                )

                st.rerun()


# ============================================================
# LAB REPORTS
# ============================================================

elif menu == "Lab Reports":

    st.title("🧪 Laboratory Reports")

    if patients.empty:

        st.warning(
            "Please add a patient first."
        )

    else:

        patient_options = {
            f"{row['id']} - {row['name']}":
            row["id"]
            for _, row in patients.iterrows()
        }

        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_options.keys())
        )

        patient_id = patient_options[
            selected_patient
        ]

        with st.form("lab_form"):

            test_name = st.text_input(
                "Test Name"
            )

            result = st.text_input(
                "Result"
            )

            unit = st.text_input(
                "Unit"
            )

            reference_range = st.text_input(
                "Reference Range"
            )

            test_date = st.date_input(
                "Test Date"
            )

            submitted = st.form_submit_button(
                "Save Lab Report"
            )

            if submitted:

                cursor.execute("""
                INSERT INTO lab_reports
                (
                    patient_id,
                    test_name,
                    result,
                    unit,
                    reference_range,
                    test_date
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    patient_id,
                    test_name,
                    result,
                    unit,
                    reference_range,
                    str(test_date)
                ))

                conn.commit()

                st.success(
                    "Lab report saved!"
                )

                st.rerun()

        st.divider()

        labs = pd.read_sql_query(
            f"""
            SELECT *
            FROM lab_reports
            WHERE patient_id = {patient_id}
            ORDER BY test_date DESC
            """,
            conn
        )

        st.dataframe(
            labs,
            use_container_width=True
        )


# ============================================================
# CLINICAL NOTES
# ============================================================

elif menu == "Clinical Notes":

    st.title("📝 Clinical Notes")

    if patients.empty:

        st.warning(
            "Please add a patient first."
        )

    else:

        patient_options = {
            f"{row['id']} - {row['name']}":
            row["id"]
            for _, row in patients.iterrows()
        }

        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_options.keys())
        )

        patient_id = patient_options[
            selected_patient
        ]

        with st.form("notes_form"):

            doctor = st.text_input(
                "Doctor Name"
            )

            note = st.text_area(
                "Clinical Note"
            )

            submitted = st.form_submit_button(
                "Save Note"
            )

            if submitted:

                cursor.execute("""
                INSERT INTO clinical_notes
                (
                    patient_id,
                    note,
                    doctor,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """, (
                    patient_id,
                    note,
                    doctor,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ))

                conn.commit()

                st.success(
                    "Clinical note saved!"
                )

                st.rerun()

        st.divider()

        notes = pd.read_sql_query(
            f"""
            SELECT *
            FROM clinical_notes
            WHERE patient_id = {patient_id}
            ORDER BY created_at DESC
            """,
            conn
        )

        for _, row in notes.iterrows():

            with st.expander(
                f"{row['doctor']} - {row['created_at']}"
            ):

                st.write(
                    row["note"]
                )


# ============================================================
# MEDICATIONS
# ============================================================

elif menu == "Medications":

    st.title("💊 Medication History")

    if patients.empty:

        st.warning(
            "Please add a patient first."
        )

    else:

        patient_options = {
            f"{row['id']} - {row['name']}":
            row["id"]
            for _, row in patients.iterrows()
        }

        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_options.keys())
        )

        patient_id = patient_options[
            selected_patient
        ]

        with st.form("medication_form"):

            medicine = st.text_input(
                "Medicine Name"
            )

            dosage = st.text_input(
                "Dosage"
            )

            frequency = st.text_input(
                "Frequency"
            )

            start_date = st.date_input(
                "Start Date"
            )

            end_date = st.date_input(
                "End Date"
            )

            status = st.selectbox(
                "Status",
                [
                    "Active",
                    "Completed",
                    "Stopped"
                ]
            )

            submitted = st.form_submit_button(
                "Save Medication"
            )

            if submitted:

                cursor.execute("""
                INSERT INTO medications
                (
                    patient_id,
                    medicine_name,
                    dosage,
                    frequency,
                    start_date,
                    end_date,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    patient_id,
                    medicine,
                    dosage,
                    frequency,
                    str(start_date),
                    str(end_date),
                    status
                ))

                conn.commit()

                st.success(
                    "Medication saved!"
                )

                st.rerun()

        st.divider()

        medications = pd.read_sql_query(
            f"""
            SELECT *
            FROM medications
            WHERE patient_id = {patient_id}
            ORDER BY start_date DESC
            """,
            conn
        )

        st.dataframe(
            medications,
            use_container_width=True
        )


# ============================================================
# REMOVE RECORD
# ============================================================

elif menu == "Remove Record":

    st.title("🗑️ Remove Record")

    st.warning(
        "⚠️ Deleted records cannot be recovered."
    )

    delete_type = st.selectbox(
        "Select Record Type",
        [
            "Patient",
            "Vital Record",
            "Lab Report",
            "Clinical Note",
            "Medication"
        ]
    )


    # ========================================================
    # REMOVE PATIENT
    # ========================================================

    if delete_type == "Patient":

        patients = pd.read_sql_query(
            "SELECT * FROM patients ORDER BY id",
            conn
        )

        if patients.empty:

            st.info(
                "No patients available."
            )

        else:

            patient_options = {
                f"{row['id']} - {row['name']}":
                row["id"]
                for _, row in patients.iterrows()
            }

            selected = st.selectbox(
                "Select Patient to Remove",
                list(patient_options.keys())
            )

            patient_id = patient_options[selected]

            st.error(
                "Removing this patient will also remove "
                "their vitals, lab reports, clinical notes "
                "and medications."
            )

            confirm = st.checkbox(
                "I understand that this will permanently delete the patient and related records."
            )

            if st.button(
                "🗑️ Delete Patient",
                type="primary"
            ):

                if not confirm:

                    st.error(
                        "Please confirm the deletion first."
                    )

                else:

                    cursor.execute(
                        "DELETE FROM vitals WHERE patient_id = ?",
                        (patient_id,)
                    )

                    cursor.execute(
                        "DELETE FROM lab_reports WHERE patient_id = ?",
                        (patient_id,)
                    )

                    cursor.execute(
                        "DELETE FROM clinical_notes WHERE patient_id = ?",
                        (patient_id,)
                    )

                    cursor.execute(
                        "DELETE FROM medications WHERE patient_id = ?",
                        (patient_id,)
                    )

                    cursor.execute(
                        "DELETE FROM patients WHERE id = ?",
                        (patient_id,)
                    )

                    conn.commit()

                    st.success(
                        "Patient and all related records deleted successfully!"
                    )

                    st.rerun()


    # ========================================================
    # REMOVE VITAL RECORD
    # ========================================================

    elif delete_type == "Vital Record":

        vitals = pd.read_sql_query(
            """
            SELECT
                vitals.id,
                patients.name AS patient_name,
                vitals.date,
                vitals.heart_rate,
                vitals.temperature,
                vitals.spo2,
                vitals.systolic_bp,
                vitals.diastolic_bp
            FROM vitals
            JOIN patients
            ON vitals.patient_id = patients.id
            ORDER BY vitals.id DESC
            """,
            conn
        )

        if vitals.empty:

            st.info(
                "No vital records available."
            )

        else:

            st.dataframe(
                vitals,
                use_container_width=True
            )

            vital_options = {
                f"ID {row['id']} - "
                f"{row['patient_name']} - "
                f"{row['date']} - "
                f"HR: {row['heart_rate']}":
                row["id"]
                for _, row in vitals.iterrows()
            }

            selected = st.selectbox(
                "Select Vital Record to Remove",
                list(vital_options.keys())
            )

            vital_id = vital_options[selected]

            confirm = st.checkbox(
                "I understand that this vital record will be permanently deleted."
            )

            if st.button(
                "🗑️ Delete Vital Record",
                type="primary"
            ):

                if not confirm:

                    st.error(
                        "Please confirm the deletion first."
                    )

                else:

                    cursor.execute(
                        "DELETE FROM vitals WHERE id = ?",
                        (vital_id,)
                    )

                    conn.commit()

                    st.success(
                        "Vital record deleted successfully!"
                    )

                    st.rerun()


    # ========================================================
    # REMOVE LAB REPORT
    # ========================================================

    elif delete_type == "Lab Report":

        labs = pd.read_sql_query(
            """
            SELECT
                lab_reports.id,
                patients.name AS patient_name,
                lab_reports.test_name,
                lab_reports.result,
                lab_reports.unit,
                lab_reports.test_date
            FROM lab_reports
            JOIN patients
            ON lab_reports.patient_id = patients.id
            ORDER BY lab_reports.id DESC
            """,
            conn
        )

        if labs.empty:

            st.info(
                "No lab reports available."
            )

        else:

            st.dataframe(
                labs,
                use_container_width=True
            )

            lab_options = {
                f"ID {row['id']} - "
                f"{row['patient_name']} - "
                f"{row['test_name']} - "
                f"{row['test_date']}":
                row["id"]
                for _, row in labs.iterrows()
            }

            selected = st.selectbox(
                "Select Lab Report to Remove",
                list(lab_options.keys())
            )

            lab_id = lab_options[selected]

            confirm = st.checkbox(
                "I understand that this lab report will be permanently deleted."
            )

            if st.button(
                "🗑️ Delete Lab Report",
                type="primary"
            ):

                if not confirm:

                    st.error(
                        "Please confirm the deletion first."
                    )

                else:

                    cursor.execute(
                        "DELETE FROM lab_reports WHERE id = ?",
                        (lab_id,)
                    )

                    conn.commit()

                    st.success(
                        "Lab report deleted successfully!"
                    )

                    st.rerun()


    # ========================================================
    # REMOVE CLINICAL NOTE
    # ========================================================

    elif delete_type == "Clinical Note":

        notes = pd.read_sql_query(
            """
            SELECT
                clinical_notes.id,
                patients.name AS patient_name,
                clinical_notes.doctor,
                clinical_notes.note,
                clinical_notes.created_at
            FROM clinical_notes
            JOIN patients
            ON clinical_notes.patient_id = patients.id
            ORDER BY clinical_notes.id DESC
            """,
            conn
        )

        if notes.empty:

            st.info(
                "No clinical notes available."
            )

        else:

            st.dataframe(
                notes,
                use_container_width=True
            )

            note_options = {
                f"ID {row['id']} - "
                f"{row['patient_name']} - "
                f"{row['doctor']} - "
                f"{row['created_at']}":
                row["id"]
                for _, row in notes.iterrows()
            }

            selected = st.selectbox(
                "Select Clinical Note to Remove",
                list(note_options.keys())
            )

            note_id = note_options[selected]

            confirm = st.checkbox(
                "I understand that this clinical note will be permanently deleted."
            )

            if st.button(
                "🗑️ Delete Clinical Note",
                type="primary"
            ):

                if not confirm:

                    st.error(
                        "Please confirm the deletion first."
                    )

                else:

                    cursor.execute(
                        "DELETE FROM clinical_notes WHERE id = ?",
                        (note_id,)
                    )

                    conn.commit()

                    st.success(
                        "Clinical note deleted successfully!"
                    )

                    st.rerun()


    # ========================================================
    # REMOVE MEDICATION
    # ========================================================

    elif delete_type == "Medication":

        medications = pd.read_sql_query(
            """
            SELECT
                medications.id,
                patients.name AS patient_name,
                medications.medicine_name,
                medications.dosage,
                medications.frequency,
                medications.status
            FROM medications
            JOIN patients
            ON medications.patient_id = patients.id
            ORDER BY medications.id DESC
            """,
            conn
        )

        if medications.empty:

            st.info(
                "No medication records available."
            )

        else:

            st.dataframe(
                medications,
                use_container_width=True
            )

            medication_options = {
                f"ID {row['id']} - "
                f"{row['patient_name']} - "
                f"{row['medicine_name']} - "
                f"{row['status']}":
                row["id"]
                for _, row in medications.iterrows()
            }

            selected = st.selectbox(
                "Select Medication to Remove",
                list(medication_options.keys())
            )

            medication_id = medication_options[
                selected
            ]

            confirm = st.checkbox(
                "I understand that this medication record will be permanently deleted."
            )

            if st.button(
                "🗑️ Delete Medication",
                type="primary"
            ):

                if not confirm:

                    st.error(
                        "Please confirm the deletion first."
                    )

                else:

                    cursor.execute(
                        "DELETE FROM medications WHERE id = ?",
                        (medication_id,)
                    )

                    conn.commit()

                    st.success(
                        "Medication record deleted successfully!"
                    )

                    st.rerun()


# ============================================================
# ANALYTICS
# ============================================================

elif menu == "Analytics":

    st.title("📊 Patient Analytics")

    if patients.empty:

        st.warning(
            "Please add a patient first."
        )

    else:

        patient_options = {
            f"{row['id']} - {row['name']}":
            row["id"]
            for _, row in patients.iterrows()
        }

        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_options.keys())
        )

        patient_id = patient_options[
            selected_patient
        ]

        vitals = pd.read_sql_query(
            f"""
            SELECT *
            FROM vitals
            WHERE patient_id = {patient_id}
            ORDER BY date
            """,
            conn
        )

        if vitals.empty:

            st.info(
                "No vital records available."
            )

        else:

            st.subheader(
                "❤️ Heart Rate Trend"
            )

            fig = px.line(
                vitals,
                x="date",
                y="heart_rate",
                markers=True,
                title="Heart Rate Over Time"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


            st.subheader(
                "🩸 Blood Pressure Trend"
            )

            fig = px.line(
                vitals,
                x="date",
                y=[
                    "systolic_bp",
                    "diastolic_bp"
                ],
                markers=True,
                title="Blood Pressure Over Time"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


            st.subheader(
                "🫁 SpO₂ Trend"
            )

            fig = px.line(
                vitals,
                x="date",
                y="spo2",
                markers=True,
                title="SpO₂ Over Time"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


            st.subheader(
                "🌡️ Temperature Trend"
            )

            fig = px.line(
                vitals,
                x="date",
                y="temperature",
                markers=True,
                title="Temperature Over Time"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.info(
    "Healthcare Dynamic EHR\n\n"
    "Built with Python, SQLite, "
    "Streamlit, Pandas and Plotly."
)
