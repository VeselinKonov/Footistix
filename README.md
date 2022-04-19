# Footstix
# Django - project instalation guide

- Follow the steps

 1. Check your python version:

    If on Windows: 

    ```python -V```

    If on MAC or Linux: 

    ```python3 -V```

  If you don't have python download it.

 2. Install ODBC Driver 17 for SQL Server from [here](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver15)

 3. Install Django and mssql-django 

    If on windows:

    ```pip install django mssql-django```
 
    If on Linux:

    ```python3 -m pip install django mssql-django```


 4. If error occupied on 3rd step and if you're using 64bit architecture and last version of python then download "pyodbc‑4.0.32‑cp310‑cp310‑win_amd64.whl" file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyodbc) and install it:
 
    If on Windows:

    ```pip install pyodbc‑4.0.32‑cp310‑cp310‑win_amd64.whl```
 
 5. Go to Django folder directory and open terminal there. Then run server with this command:
 
    If on windows:

    ```python manage.py runserver```

    If on Mac or linux:
    
    ```python3 manage.py runserver```