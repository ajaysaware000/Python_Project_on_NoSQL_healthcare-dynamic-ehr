# Healthcare Dynamic EHR System

A dynamic **Electronic Health Record (EHR)** system built using **Neo4j**, a NoSQL graph database, and **Streamlit**.  
This project stores and manages connected healthcare data such as patients, vital records, lab reports, and medications using a graph-based approach.

---

# 🌐 Streamlit Application Link

You can access the Healthcare Dynamic EHR System using the link below:


> Note: Replace `YOUR_STREAMLIT_APP_LINK` with your actual deployed Streamlit application URL.

Example:

[Click Here to Open the Streamlit App](https://pythonprojectonnosqlhealthcare-dynamic-ehr-7extvaklsbez5hzdhzm.streamlit.app/)

---

# 📌 Project Overview

Healthcare data is highly interconnected. A patient may have multiple vital records, lab reports, and prescribed medications. Traditional relational databases require multiple joins to retrieve this connected information.

This project uses **Neo4j**, a graph database, to represent healthcare data as **nodes** and **relationships**. A **Streamlit** web application is used to search patient records and display their complete medical history in an interactive way.

---

# 🚀 Features

- Store healthcare data in a NoSQL graph database
- Manage patient details, vital records, lab reports, and medications
- Create relationships between patients and their medical records
- Search patients using Patient ID or Name
- View complete patient medical history
- Display vital signs, lab reports, and medications
- Visualize patient-related healthcare data as a graph
- Interactive and easy-to-use Streamlit interface

---

# 🛠️ Tools and Technologies Used

| Tool / Technology | Purpose |
|---|---|
| **Neo4j** | NoSQL graph database for storing healthcare data |
| **Cypher Query Language** | Used to query and manage graph data |
| **Streamlit** | Used to build the web application |
| **Python** | Main programming language |
| **Neo4j Python Driver** | Connects Streamlit application with Neo4j |
| **Pandas** | Used for data cleaning and processing |
| **CSV Datasets** | Used to store healthcare data |

---

# 📂 Datasets Used

The project uses the following datasets:

## 1. Patients Dataset

Contains patient details such as:

- Patient ID  
- Name  
- Age  
- Gender  
- Blood Group  
- Contact Number  
- Address  

## 2. Vital Records Dataset

Contains patient health measurements such as:

- Vital Record ID  
- Patient ID  
- Blood Pressure  
- Heart Rate  
- Temperature  
- Oxygen Level  
- Respiratory Rate  
- Recorded Date  

## 3. Lab Reports Dataset

Contains laboratory test details such as:

- Lab Report ID  
- Patient ID  
- Test Name  
- Result Value  
- Normal Range  
- Test Date  

## 4. Medications Dataset

Contains prescribed medicine details such as:

- Medication ID  
- Patient ID  
- Medicine Name  
- Dosage  
- Frequency  
- Start Date  
- End Date  

---

# 🧠 Graph Data Model

The healthcare data is stored in Neo4j using the following graph structure:

```text
(Patient)-[:HAS_VITAL_RECORD]->(VitalRecord)

(Patient)-[:HAS_LAB_REPORT]->(LabReport)

(Patient)-[:TAKES_MEDICATION]->(Medication)
```

## Nodes

- `Patient`
- `VitalRecord`
- `LabReport`
- `Medication`

## Relationships

- `HAS_VITAL_RECORD`
- `HAS_LAB_REPORT`
- `TAKES_MEDICATION`

---

# ⚙️ Installation

## 1. Install Required Python Libraries

```bash
pip install streamlit pandas neo4j
```

## 2. Install and Set Up Neo4j

- Download and install Neo4j Desktop from the official website.
- Create a new database.
- Set the database password.
- Start the Neo4j database.

---

# 🔐 Database Configuration

Create a file named `config.py` or add your Neo4j credentials in the main application file:

```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your_password"
```

---

# 🗄️ Create Graph Nodes and Relationships

Example Cypher queries used in the project:

## Create Patient Node

```cypher
CREATE (p:Patient {
    patient_id: "P101",
    name: "John Doe",
    age: 30,
    gender: "Male",
    blood_group: "O+"
})
```

## Create Vital Record Node

```cypher
CREATE (v:VitalRecord {
    vital_id: "V101",
    blood_pressure: "120/80",
    heart_rate: 78,
    temperature: 98.6,
    oxygen_level: 98
})
```

## Create Relationship

```cypher
MATCH (p:Patient {patient_id: "P101"}),
      (v:VitalRecord {vital_id: "V101"})
CREATE (p)-[:HAS_VITAL_RECORD]->(v)
```

## Retrieve Patient Lab Reports

```cypher
MATCH (p:Patient {patient_id: "P101"})-[:HAS_LAB_REPORT]->(l:LabReport)
RETURN p, l
```

---

# ▶️ Run the Project

After setting up Neo4j and installing the required libraries, run the Streamlit application using:

```bash
streamlit run app.py
```

Then open the generated local URL in your browser:

```text
http://localhost:8501
```

---

# 🖥️ Application Workflow

```text
Healthcare Datasets
        ↓
   Data Cleaning
        ↓
   Neo4j Database
        ↓
   Graph Modeling
        ↓
    Data Import
        ↓
Relationship Creation
        ↓
   Streamlit App
        ↓
    User Search
        ↓
    Cypher Query
        ↓
Patient EHR Display
        ↓
 Graph Visualization
```

---

# 📊 Application Modules

## 1. Patient Search

Users can search for a patient using Patient ID or Name.

## 2. Patient Details

Displays basic patient information such as name, age, gender, and blood group.

## 3. Vital Records

Displays blood pressure, heart rate, temperature, oxygen level, and other health measurements.

## 4. Lab Reports

Displays lab test names, results, normal ranges, and test dates.

## 5. Medications

Displays prescribed medicines, dosage, frequency, and duration.

## 6. Graph Visualization

Displays the relationship between a patient and their healthcare records.

---

# ✅ Advantages

- Provides a complete view of patient medical history
- Uses graph database for connected healthcare data
- Reduces complex SQL joins
- Makes relationship-based queries easier
- Helps doctors quickly access patient information
- Provides interactive data visualization
- Easy to extend with new healthcare datasets
- Useful for hospitals, clinics, and healthcare analytics

---

# 🔮 Future Scope

- Add doctor and appointment management
- Include diagnosis and treatment history
- Add allergy and drug-interaction alerts
- Use AI/ML for health risk prediction
- Add role-based login for doctors, nurses, and admins
- Integrate real-time patient monitoring using IoT devices
- Develop a mobile application
- Deploy the system on cloud platforms
- Integrate with HL7/FHIR healthcare standards

---

# 🧪 Testing

The system was tested using sample healthcare datasets.

Test cases included:

- Searching a patient by ID
- Searching a patient by name
- Displaying vital records
- Displaying lab reports
- Displaying medications
- Verifying graph relationships
- Checking Cypher query results
- Testing Streamlit application performance

---

# 📌 Conclusion

This project successfully demonstrates how a **NoSQL graph database** can be used to build a dynamic Electronic Health Record system. Neo4j helps store connected healthcare data efficiently, while Streamlit provides an interactive interface for viewing patient information.

The system improves access to patient history by connecting patients with their vital records, lab reports, and medications in a single graph-based application.

---

# 👨‍💻 Developed By

**Ajay Saware**  
---
