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

    # Rahul's ID
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
        "Electronic Health Record & Multi-Modal Clinical "
        "Record Manager"
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

            # ------------------------------------------------
            # HEART RATE
            # ------------------------------------------------

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

            # ------------------------------------------------
            # BLOOD PRESSURE
            # ------------------------------------------------

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

            # ------------------------------------------------
            # SPO2
            # ------------------------------------------------

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

            # ------------------------------------------------
            # TEMPERATURE
            # ------------------------------------------------

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
