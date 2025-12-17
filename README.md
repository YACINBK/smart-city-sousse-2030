# How to Run the Smart City Platform

## 1. Start the Backend (Django)
This powers the API and connects to the database.

1.  Open a **Terminal**.
2.  Navigate to the project folder:
    ```powershell
    cd c:\Users\YACIN\Desktop\projet_module_bdd
    ```
3.  Run the server:
    ```powershell
    python manage.py runserver
    ```
    *Keep this terminal open!*

## 2. Start the Frontend (Streamlit)
This launches the dashboard in your browser.

1.  Open a **New Terminal** (Split or new window).
2.  Navigate to the project folder again:
    ```powershell
    cd c:\Users\YACIN\Desktop\projet_module_bdd
    ```
3.  Run the dashboard:
    ```powershell
    streamlit run dashboard.py
    ```

## 3. Access
*   **Dashboard**: [http://localhost:8501](http://localhost:8501)
*   **API Root**: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)
*   **Admin Panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
