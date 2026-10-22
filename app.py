import sqlite3
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Healthcare Dynamic EHR",
    page_icon="🏥",
    layout="wide"
)

# ============================================================
# 2. DATABASE SETUP (FREE SQLITE DATABASE)
# ============================================================

# The database is created in the same folder as this app.py file.
BASE_DIR = Path(__file__).resolve().parent
DATABASE_NAME = BASE_DIR / "healthcare_ehr.db"


def get_connection():
    """Create a database connection with foreign-key support."""
    connection = sqlite3.connect(
        DATABASE_NAME,
        check_same_thread=False,
        timeout=30
    )
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    """Create all required tables if they do not already exist."""
    with get_connection() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                phone TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS vitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                heart_rate INTEGER,
                temperature REAL,
                spo2 INTEGER,
                systolic_bp INTEGER,
                diastolic_bp INTEGER,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS lab_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                test_name TEXT NOT NULL,
                result TEXT,
                unit TEXT,
                reference_range TEXT,
                test_date TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS clinical_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                note TEXT NOT NULL,
                doctor TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                medicine_name TEXT NOT NULL,
                dosage TEXT,
                frequency TEXT,
                start_date TEXT,
                end_date TEXT,
                status TEXT NOT NULL DEFAULT 'Active',
                FOREIGN KEY (patient_id) REFERENCES patients(id)
                    ON DELETE CASCADE
            );
        """)


initialize_database()


def read_table(query, params=()):
    with get_connection() as db:
        return pd.read_sql_query(query, db, params=params)


def execute_query(query, params=()):
    with get_connection() as db:
        cursor = db.execute(query, params)
        db.commit()
        return cursor.lastrowid


def get_patients():
    return read_table("SELECT * FROM patients ORDER BY id DESC")


def patient_choices():
    patients = get_patients()
    return {
        f"{int(row['id'])} - {row['name']}": int(row["id"])
        for _, row in patients.iterrows()
    }


def choose_patient(label="Select Patient"):
    choices = patient_choices()
    if not choices:
        st.warning("Please add a patient first in the Patients section.")
        return None
    selected = st.selectbox(label, list(choices.keys()))
    return choices[selected]


# ============================================================
# 3. OPTIONAL DEMO DATA
#    Add demo data only once, when the patients table is empty.
#    These are fictional sample records.
# ============================================================

with get_connection() as db:
    count = db.execute("SELECT COUNT(*) FROM patients").fetchone()[0]

    if count == 0:
        cur = db.execute(
            """INSERT INTO patients (name, age, gender, phone, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            ("Rahul Sharma", 45, "Male", "9000000001", "2026-10-01")
        )
        rahul_id = cur.lastrowid

        db.execute(
            """INSERT INTO patients (name, age, gender, phone, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            ("Priya Sharma", 32, "Female", "9000000002", "2026-10-01")
        )

        db.executemany(
            """INSERT INTO vitals
               (patient_id, date, heart_rate, temperature, spo2,
                systolic_bp, diastolic_bp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                (rahul_id, "2026-10-01", 78, 98.4, 98, 120, 80),
                (rahul_id, "2026-10-02", 82, 98.6, 97, 125, 82),
                (rahul_id, "2026-10-03", 88, 99.0, 96, 130, 85),
                (rahul_id, "2026-10-04", 84, 98.7, 97, 128, 83),
                (rahul_id, "2026-10-05", 80, 98.5, 98, 122, 80),
            ]
        )

        db.executemany(
            """INSERT INTO lab_reports
               (patient_id, test_name, result, unit, reference_range, test_date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (rahul_id, "Hemoglobin", "13.5", "g/dL", "13-17", "2026-10-01"),
                (rahul_id, "Glucose", "105", "mg/dL", "70-110", "2026-10-01"),
                (rahul_id, "Cholesterol", "180", "mg/dL", "125-200", "2026-10-01"),
            ]
        )

        db.executemany(
            """INSERT INTO clinical_notes (patient_id, note, doctor, created_at)
               VALUES (?, ?, ?, ?)""",
            [
                (rahul_id, "Patient reported mild fever and fatigue.",
                 "Dr. Kumar", "2026-10-01"),
                (rahul_id, "Patient condition improved. Continue monitoring.",
                 "Dr. Kumar", "2026-10-03"),
            ]
        )

        db.executemany(
            """INSERT INTO medications
               (patient_id, medicine_name, dosage, frequency,
                start_date, end_date, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                (rahul_id, "Paracetamol", "500 mg", "2 times/day",
                 "2026-10-01", "2026-10-05", "Completed"),
                (rahul_id, "Vitamin D", "1000 IU", "1 time/day",
                 "2026-10-01", "", "Active"),
            ]
        )

# ============================================================
# 4. SIDEBAR NAVIGATION
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
        "Analytics",
    ]
)

st.sidebar.divider()
st.sidebar.caption("Database: SQLite")
st.sidebar.caption(str(DATABASE_NAME.name))

# ============================================================
# 5. DASHBOARD
# ============================================================

if menu == "Dashboard":
    st.title("🏥 Healthcare Dynamic EHR")
    st.write("Electronic Health Record & Clinical Record Manager")
    st.info("Demo data is fictional. This application is for demonstration, not clinical decision-making.")

    patients = get_patients()
    total_vitals = read_table("SELECT COUNT(*) AS n FROM vitals").iloc[0]["n"]
    total_labs = read_table("SELECT COUNT(*) AS n FROM lab_reports").iloc[0]["n"]
    total_meds = read_table("SELECT COUNT(*) AS n FROM medications").iloc[0]["n"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👤 Patients", int(len(patients)))
    c2.metric("🩺 Vital Records", int(total_vitals))
    c3.metric("🧪 Lab Reports", int(total_labs))
    c4.metric("💊 Medications", int(total_meds))

    st.subheader("Registered Patients")
    st.dataframe(patients, use_container_width=True, hide_index=True)

# ============================================================
# 6. PATIENT MANAGEMENT
# ============================================================

elif menu == "Patients":
    st.title("👤 Patient Management")

    with st.form("patient_form", clear_on_submit=True):
        name = st.text_input("Patient Name")
        age = st.number_input("Age", min_value=0, max_value=120, value=25)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        phone = st.text_input("Phone Number")
        submitted = st.form_submit_button("Add Patient")

    if submitted:
        if not name.strip():
            st.error("Please enter the patient name.")
        else:
            execute_query(
                """INSERT INTO patients (name, age, gender, phone, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    name.strip(), int(age), gender, phone.strip(),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
            st.success("Patient added successfully!")
            st.rerun()

    st.subheader("Patient List")
    st.dataframe(get_patients(), use_container_width=True, hide_index=True)

# ============================================================
# 7. ADD VITALS
# ============================================================

elif menu == "Add Vitals":
    st.title("🩺 Add Patient Vitals")
    patient_id = choose_patient()

    if patient_id is not None:
        with st.form("vitals_form", clear_on_submit=True):
            vital_date = st.date_input("Date", value=date.today())
            heart_rate = st.number_input("Heart Rate (BPM)", 0, 250, 80)
            temperature = st.number_input("Temperature (°F)", 80.0, 110.0, 98.6, step=0.1)
            spo2 = st.number_input("SpO₂ (%)", 0, 100, 98)
            systolic = st.number_input("Systolic BP", 0, 250, 120)
            diastolic = st.number_input("Diastolic BP", 0, 200, 80)
            submitted = st.form_submit_button("Save Vitals")

        if submitted:
            execute_query(
                """INSERT INTO vitals
                   (patient_id, date, heart_rate, temperature, spo2,
                    systolic_bp, diastolic_bp)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (patient_id, str(vital_date), heart_rate, temperature,
                 spo2, systolic, diastolic)
            )
            st.success("Vitals saved successfully!")
            st.rerun()

        st.subheader("Vital History")
        st.dataframe(
            read_table(
                """SELECT id, date, heart_rate, temperature, spo2,
                          systolic_bp, diastolic_bp
                   FROM vitals WHERE patient_id = ? ORDER BY date DESC""",
                (patient_id,)
            ),
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# 8. LAB REPORTS
# ============================================================

elif menu == "Lab Reports":
    st.title("🧪 Laboratory Reports")
    patient_id = choose_patient()

    if patient_id is not None:
        with st.form("lab_form", clear_on_submit=True):
            test_name = st.text_input("Test Name")
            result = st.text_input("Result")
            unit = st.text_input("Unit")
            reference_range = st.text_input("Reference Range")
            test_date = st.date_input("Test Date", value=date.today())
            submitted = st.form_submit_button("Save Lab Report")

        if submitted:
            if not test_name.strip():
                st.error("Please enter the test name.")
            else:
                execute_query(
                    """INSERT INTO lab_reports
                       (patient_id, test_name, result, unit, reference_range, test_date)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (patient_id, test_name.strip(), result.strip(), unit.strip(),
                     reference_range.strip(), str(test_date))
                )
                st.success("Lab report saved!")
                st.rerun()

        st.subheader("Lab Report History")
        st.dataframe(
            read_table(
                """SELECT id, test_name, result, unit, reference_range, test_date
                   FROM lab_reports WHERE patient_id = ? ORDER BY test_date DESC""",
                (patient_id,)
            ),
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# 9. CLINICAL NOTES
# ============================================================

elif menu == "Clinical Notes":
    st.title("📝 Clinical Notes")
    patient_id = choose_patient()

    if patient_id is not None:
        with st.form("notes_form", clear_on_submit=True):
            doctor = st.text_input("Doctor Name")
            note = st.text_area("Clinical Note")
            submitted = st.form_submit_button("Save Note")

        if submitted:
            if not note.strip():
                st.error("Please enter a clinical note.")
            else:
                execute_query(
                    """INSERT INTO clinical_notes (patient_id, note, doctor, created_at)
                       VALUES (?, ?, ?, ?)""",
                    (patient_id, note.strip(), doctor.strip(),
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                st.success("Clinical note saved!")
                st.rerun()

        st.subheader("Previous Notes")
        notes = read_table(
            """SELECT id, doctor, note, created_at
               FROM clinical_notes WHERE patient_id = ? ORDER BY created_at DESC""",
            (patient_id,)
        )
        if notes.empty:
            st.info("No clinical notes found.")
        else:
            for _, row in notes.iterrows():
                with st.expander(f"{row['doctor'] or 'Doctor'} — {row['created_at']}"):
                    st.write(row["note"])

# ============================================================
# 10. MEDICATIONS
# ============================================================

elif menu == "Medications":
    st.title("💊 Medication History")
    patient_id = choose_patient()

    if patient_id is not None:
        with st.form("medication_form", clear_on_submit=True):
            medicine = st.text_input("Medicine Name")
            dosage = st.text_input("Dosage")
            frequency = st.text_input("Frequency")
            start_date = st.date_input("Start Date", value=date.today())
            has_end_date = st.checkbox("Specify an end date")
            end_date = st.date_input("End Date", value=date.today()) if has_end_date else None
            status = st.selectbox("Status", ["Active", "Completed", "Stopped"])
            submitted = st.form_submit_button("Save Medication")

        if submitted:
            if not medicine.strip():
                st.error("Please enter the medicine name.")
            else:
                execute_query(
                    """INSERT INTO medications
                       (patient_id, medicine_name, dosage, frequency,
                        start_date, end_date, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (patient_id, medicine.strip(), dosage.strip(), frequency.strip(),
                     str(start_date), str(end_date) if end_date else "", status)
                )
                st.success("Medication saved!")
                st.rerun()

        st.subheader("Medication History")
        st.dataframe(
            read_table(
                """SELECT id, medicine_name, dosage, frequency,
                          start_date, end_date, status
                   FROM medications WHERE patient_id = ? ORDER BY start_date DESC""",
                (patient_id,)
            ),
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# 11. REMOVE RECORDS
# ============================================================

elif menu == "Remove Record":
    st.title("🗑️ Remove Record")
    st.warning("Deletion is permanent. Use fictional/demo data while testing.")

    delete_type = st.selectbox(
        "Select Record Type",
        ["Patient", "Vital Record", "Lab Report", "Clinical Note", "Medication"]
    )

    if delete_type == "Patient":
        records = read_table("SELECT id, name, age, gender, phone FROM patients ORDER BY id")
        if records.empty:
            st.info("No patients available.")
        else:
            st.dataframe(records, use_container_width=True, hide_index=True)
            options = {f"ID {r.id} — {r.name}": int(r.id) for r in records.itertuples()}
            selected = st.selectbox("Select Patient to Remove", list(options.keys()))
            confirm = st.checkbox("I understand the patient and related records will be deleted.")
            if st.button("Delete Patient", type="primary"):
                if not confirm:
                    st.error("Please confirm deletion first.")
                else:
                    # ON DELETE CASCADE removes all linked records.
                    execute_query("DELETE FROM patients WHERE id = ?", (options[selected],))
                    st.success("Patient and related records deleted.")
                    st.rerun()

    else:
        table_info = {
            "Vital Record": ("vitals", "Vital Record"),
            "Lab Report": ("lab_reports", "Lab Report"),
            "Clinical Note": ("clinical_notes", "Clinical Note"),
            "Medication": ("medications", "Medication"),
        }
        table, label = table_info[delete_type]
        records = read_table(
            f"""SELECT t.id, p.name AS patient_name, t.*
                FROM {table} t
                JOIN patients p ON p.id = t.patient_id
                ORDER BY t.id DESC"""
        )
        if records.empty:
            st.info(f"No {label.lower()} records available.")
        else:
            st.dataframe(records, use_container_width=True, hide_index=True)
            options = {
                f"ID {int(r['id'])} — {r['patient_name']}": int(r["id"])
                for _, r in records.iterrows()
            }
            selected = st.selectbox(f"Select {label} to Remove", list(options.keys()))
            confirm = st.checkbox(f"I understand this {label.lower()} will be permanently deleted.")
            if st.button(f"Delete {label}", type="primary"):
                if not confirm:
                    st.error("Please confirm deletion first.")
                else:
                    execute_query(f"DELETE FROM {table} WHERE id = ?", (options[selected],))
                    st.success(f"{label} deleted successfully.")
                    st.rerun()

# ============================================================
# 12. ANALYTICS
# ============================================================

elif menu == "Analytics":
    st.title("📊 Patient Analytics")
    patient_id = choose_patient()

    if patient_id is not None:
        vitals = read_table(
            "SELECT * FROM vitals WHERE patient_id = ? ORDER BY date",
            (patient_id,)
        )

        if vitals.empty:
            st.info("No vital records available for this patient.")
        else:
            st.subheader("❤️ Heart Rate Trend")
            fig = px.line(vitals, x="date", y="heart_rate", markers=True,
                          title="Heart Rate Over Time")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🩸 Blood Pressure Trend")
            fig = px.line(vitals, x="date", y=["systolic_bp", "diastolic_bp"],
                          markers=True, title="Blood Pressure Over Time")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🫁 SpO₂ Trend")
            fig = px.line(vitals, x="date", y="spo2", markers=True,
                          title="SpO₂ Over Time")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🌡️ Temperature Trend")
            fig = px.line(vitals, x="date", y="temperature", markers=True,
                          title="Temperature Over Time")
            st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 13. FOOTER
# ============================================================

st.sidebar.divider()
st.sidebar.caption("Healthcare Dynamic EHR")
st.sidebar.caption("Python • Streamlit • SQLite • Pandas • Plotly")
