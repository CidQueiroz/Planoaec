# PlanoAeC: RPA & Operations Automation Dashboard

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.20%2B-red.svg)](https://www.streamlit.io/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0%2B-green.svg)](https://www.selenium.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57.svg?style=flat&logo=SQLite&logoColor=white)](https://www.sqlite.org/index.html)

## 1. Project Overview

`PlanoAeC` is not just a plan; it is a **fully functional Streamlit dashboard for process automation (RPA) and operations**, developed to optimize the workflows of the AEC Planning department.

This project is the **living proof of my MLOps/DevOps origin story**. I identified critical operational bottlenecks and built automated solutions from scratch using Python, Selenium, and SQL. It demonstrates the core philosophy of an MLOps Engineer: **if a process is manual, automate it.**

## 2. Key Features (The "Unicorn" Stack)

This application centralizes multiple automation tasks into a single, user-friendly web interface:

* **RPA (Robotic Process Automation):** Deploys a **Selenium** bot (`atribui_tkt.py`) to log into a live **Zendesk** instance and programmatically change agent call routings, saving hours of manual work.
* **Operational Dashboard:** Built with **Streamlit** (`app.py`), it provides a central hub for the entire team to execute tasks.
* **Authentication:** Includes a secure login page (`login_page`) that verifies credentials against a MySQL database.
* **Data Pipeline:** Features a data logging script (`salva_sinalizacao_bd.py`) that writes operational alerts ("sinalizações") to a **SQLite database**, with built-in logic to prevent duplicate entries within a 10-minute window.
* **Task Automation:** Includes modules for downloading operational reports, sending automated email reports (via `win32com`), and simple CI/CD with batch scripts (`sincronizando.bat`).

## 3. Core Technologies Used

* **Core Language:** Python
* **Web Framework:** Streamlit
* **RPA / Web Automation:** Selenium
* **Database:** SQLite, MySQL
* **Data Manipulation:** Pandas
* **Windows Automation:** Win32com (Outlook)

## 4. How to Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/CidQueiroz/Planoaec.git](https://github.com/CidQueiroz/Planoaec.git)
    cd Planoaec
    ```
2.  **Install dependencies** (ideally in a virtual environment):
    ```bash
    pip install -r requirements.txt 
    ```
    *(Note: You will need to create a `requirements.txt` file based on the imports in `app.py` and `atribui_tkt.py`)*

3.  **Run the Streamlit App:**
    ```bash
    streamlit run app.py
    ```

---

### 📬 Contact

**Cidirclay Queiroz**
(AI Solutions Architect | AI Engineering | MLOps Engineering)

* **Portfolio:** [www.cdkteck.com.br](https://www.cdkteck.com.br)
* **LinkedIn:** [linkedin.com/in/ciddy-queiroz/](https://www.linkedin.com/in/ciddy-queiroz/)
