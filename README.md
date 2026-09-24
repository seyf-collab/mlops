# Olist MLOps Project

## Project Overview

This project is an end-to-end MLOps project based on the Brazilian E-Commerce Public Dataset by Olist.

The project focuses on preparing the data, building a labeled dataset, splitting the data based on time, and preparing the project structure for the machine learning and MLOps workflow.

The project also uses Docker, MySQL, MLflow, DVC, and Google Drive as part of the MLOps setup.

---

## Project Structure

```text
olist-project/
│
├── archive/
│   └── Raw dataset files
│
├── artifacts/
│   └── Generated datasets and artifacts
│
├── notebooks/
│   ├── Notebook 1
│   ├── Notebook 2
│   └── Notebook 3
│
├── config/
│   └── config.yaml
│
├── tests/
│
├── .dvc/
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Dataset

The project uses the Olist e-commerce dataset.

The original CSV files are imported into a local MySQL database named:

```text
olist_db
```

The main tables include:

* Customers
* Orders
* Order Items
* Order Payments
* Order Reviews
* Products
* Sellers
* Geolocation
* Category Translation

The database is used to read and join the required data for the machine learning workflow.

---

## Data Preparation

The data preparation workflow includes:

1. Loading the Olist CSV files.
2. Creating the local MySQL database.
3. Importing the CSV files into the database.
4. Connecting to the database using Python.
5. Reading the required tables.
6. Joining the required tables.
7. Creating the labeled dataset.
8. Saving the labeled dataset as an artifact.

The resulting labeled table contains information such as:

```text
order_id
customer_id
order_status
order_purchase_timestamp
order_approved_at
order_delivered_carrier_date
order_delivered_customer_date
order_estimated_delivery_date
customer_unique_id
customer_zip_code_prefix
customer_city
customer_state
number_of_items
total_price
total_freight
total_payment
max_installments
late_delivery
```

The target variable is:

```text
late_delivery
```

---

## Target Variable

The target indicates whether an order was delivered late.

```text
0 = On-time delivery
1 = Late delivery
```

After labeling the data, the class distribution was:

```text
On-time: 92.13%
Late:     7.87%
```

---

## Train / Validation / Test Split

A time-based split was used for the dataset.

The purchase date range in the data is:

```text
Minimum: 2016-09-04 21:15:19
Maximum: 2018-10-17 17:30:18
```

The data was divided chronologically into:

```text
Train:      69,608 rows
Validation: 14,916 rows
Test:       14,917 rows
```

The time-based split helps preserve the chronological order of the data and avoids using future observations when preparing the training data.

---

## Data Versioning

DVC (Data Version Control) is used to track the project's data and generated artifacts.

The data files are not stored directly in GitHub.

Instead:

* GitHub stores the project code, configuration, notebooks, tests, and DVC metadata.
* DVC tracks the datasets and artifacts.
* Google Drive is used as the DVC remote storage.

The main DVC workflow is:

```bash
dvc pull
```

to retrieve the required data and artifacts, and:

```bash
dvc push
```

to upload tracked data to the remote storage.

---

## Environment Variables

Sensitive configuration is stored using environment variables.

The project uses a `.env` file locally.

The `.env` file should not be committed to GitHub.

A `.env.example` file is provided as a template.

Important configuration includes:

```text
DATABASE_URL
MLFLOW_TRACKING_URI
APP_CONFIG
```

The application configuration file is:

```text
config/config.yaml
```

---

## Docker

Docker is used to provide a reproducible environment for the project.

The project includes:

```text
Dockerfile
docker-compose.yml
```

Docker Compose is used to run the required project services, including:

* MySQL
* API
* MLflow

---

## MLflow

MLflow is included in the project as part of the experiment tracking and machine learning workflow.

The MLflow tracking URI is configured through the environment variable:

```text
MLFLOW_TRACKING_URI
```

---

## Google Drive

Google Drive is used as the remote storage location for DVC.

The Google Drive storage is separate from the Google Cloud account used to create the Google Cloud client.

The DVC remote is used to store the actual datasets and artifacts, while GitHub stores the project files and DVC metadata.

---

## How to Run the Project

### 1. Clone the repository

```bash
git clone <repository-url>
cd olist-project
```

### 2. Configure environment variables

Create a `.env` file based on:

```text
.env.example
```

Add the required local configuration.

### 3. Retrieve the data

Run:

```bash
dvc pull
```

This retrieves the DVC-tracked data and artifacts from the configured remote storage.

### 4. Start the project

Run:

```bash
docker compose up --build
```

This starts the services defined in `docker-compose.yml`.

---

## Technologies

The project uses:

* Python
* Pandas
* MySQL
* SQLAlchemy
* Docker
* Docker Compose
* MLflow
* DVC
* Google Drive
* Git / GitHub

---

## Project Workflow

The overall workflow is:

```text
Olist CSV Dataset
        ↓
     MySQL
        ↓
 Data Extraction
        ↓
 Data Joining
        ↓
 Data Labeling
        ↓
 labeled_table.csv
        ↓
 Time-based Split
        ↓
Train / Validation / Test
        ↓
 Machine Learning Workflow
        ↓
      MLflow
        ↓
       API
```

---

## Repository

The GitHub repository contains the project source code, notebooks, configuration files, tests, Docker configuration, and DVC metadata.

The actual data files are stored through DVC and the configured Google Drive remote rather than directly in GitHub.
