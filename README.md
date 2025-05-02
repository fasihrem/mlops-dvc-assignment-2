# MLOps DVC Assignment 2

This project demonstrates a simple MLOps pipeline using *Apache Airflow* and optionally *DVC* for data versioning.

---

## 📦 Setup Instructions (Ubuntu/Linux)

### 1. Clone the Repository

```bash
git clone https://github.com/fasihrem/mlops-dvc-assignment-2.git
cd mlops-dvc-assignment-2
```
---

### 2. Create & Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```
---

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```
```bash
pip install apache-airflow==2.7.0 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.0/constraints-3.8.txt"
```
---

### 4. Set Up Airflow

#### Initialize the database:
```bash
export AIRFLOW_HOME=$(pwd)/airflow
airflow db migrate
```

#### Set the DAGs folder:
```bash
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
```
---

### 5. Create Airflow User (first time only)

```bash
airflow users create \
    --username admin \
    --firstname First \
    --lastname Last \
    --role Admin \
    --email admin@example.com \
    --password admin
```
---

### 6. Start Airflow Services

In Terminal 1:
```bash
airflow api-server --port 8081
```
In Terminal 2:
```bash
airflow scheduler
```
In your browser go to http://localhost:8081 and log in with the credentials above.

---

### 7. Run the DAG

Once the Airflow UI loads:

- You should see train_model_dag in the DAGs list.
- Toggle it "on".
- Click the ▶️ (Play) button to trigger a run manually.

---

## ✅ Done!

Now your Airflow DAG is running locally 🎉
