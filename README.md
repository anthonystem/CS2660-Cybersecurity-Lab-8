# Lab Assignment 8.0 (Final Project) - PyMart Intranet System

## Description
Final project for CS2660 Cybersecurity Principles at the University of Vermont. A Python Flask implementation of
my PyMart Intranet System in Lab 1.0.

**Author:** Anthony Stem

**Class:** CS 2660 - Cybersecurity Principles

**Assignment:** Lab Assignment 8.0.

## Details
### System Applications
+ **Time Report** - The clock-in/time management panel. 
+ **Inventory** - The department inventory panel.
+ **Job Application Manager** - The application management panel where admins/department managers can manage incoming job applications.
+ **Admin Panel** - The administrator panel.

### Access Levels
There are three primary access levels **STANDARD**, **DEPARTMENT_MANAGER**, **ADMINISTRATOR**.

1. **Standard** - Lowest-level employee such as a cashier.
   + **Can Access:**
     + Time Report
   + **Cannot Access:**
     + Inventory
     + Job Application Manager
     + Admin Panel
2. **Department Manager** - A manager that oversees a specific department. Has the second highest access level.
   + **Can Access:**
     + Time Report
     + Inventory
     + Job Application Manager
   + **Cannot Access:**
     + Admin Panel
3. **Administrator** - An administrator such as a general manager who oversees all departments at PyMart.
   + **Can Access:**
     + Time Report
     + Inventory
     + Job Application Manager
     + Admin Panel
   + **Cannot Access:**
     + User Has Access to *ALL* applications in the system.

## Files
### Templates & Web Pages
+ **layout.html** - Contains the HTML head and metadata. Other files will extend this template.
+ **index.html** - The landing page. The first page the user sees when not logged in.
+ **login.html** - The login page.
+ **register.html** - The registration page.
+ **dashboard.html** - The user dashboard. Has links to all four of the intranet system applications.
+ **macros.html** - A macro/component to that displays whether or not a user has access to a system application.
+ **time-report.html** - The template for the time report application.
+ **inventory.html** - The template for the inventory application.
+ **job-application-manager.html** - The template for the job application manager application.
+ **admin.html** - The template for the admin panel application.

### Python Scripts (.py Files)
+ **app.py** - The main Python script for the PyMart Intranet System. Used to run the Flask application.
+ **authentication.py** - Contains important functions that are used in app.py. These include functions used for authentication, input validation, password generation, and some database operations such as blocking users. This file is imported in app.py.
+ **config.py** - Contains the database file path and the secret key. Only included in the repository for grading purposes.
+ **database_manager.py** - An auxillary file used for setting up and/or deleting the database file for testing purposes.

### Static Files (Styling)
For this project, I used SCSS, so I included the compilled styles.css and .map files alongside the styles.scss.
+ **styles.scss** - The SCSS file used to create the styling for the application.
+ **styles.css** - The compilled CSS.

Also, in the *media* directory, I included PyMart's custom logo svg.
+ **media/pymart_logo.svg** - PyMart's logo.

### Database File
The database file used for this project is **pymart_database.db**.


## How to Test
### Get Required Modules/Packages
Before starting the application, make sure to have the required modules used for this project. The required modules/packages are inside the `requirements.txt` file.

To get the required modules/packages, run the following command in command line (while in the project directory):

```
pip install -r requirements.txt
```

You can also manually install each module listed in the requirements file if needed.

### Database Setup
I provide the database file for you, which is `pymart_database.db`. However, if you need to re-create it, simply execute the `database_manager.py` which will create a fresh database file with three testing users for you (unless you set test_mode=False in the setup call, in which case it will only create an empty Users table).

The database sqlite3 schema is as follows:

```sql
CREATE TABLE IF NOT EXISTS Users (
    user_id integer PRIMARY KEY,
    username text NOT NULL,
    password text NOT NULL,
    access_level text NOT NULL DEFAULT 'STANDARD',
    blocked integer NOT NULL DEFAULT 0
);
```

### Running the Flask Application
While inside the project directory, execute the following command to run the Flask application:

```
python app/app.py
```

If you encounter errors connecting to the database, you may have tried running the application while inside the `app` folder. If so, either modify the `DATABASE_FILE` variable in `config.py` and set the database file path relative to your current working directory or type `cd ..` in the terminal to return to the root project folder.

When you run the `app.py` script, it will provide the host the application is running on in the terminal. Either click the host where it says "Running on http://..." or type the host into the browser of your choice.

When you access the application in your browser, you will see PyMarts landing page where you will be prompted to log in or register.

### Testing Login System
When in the login part of the application, type in the username and password for a user and press the "Log In" button to log in as that user. If the username doesn't exist or is incorrect, or the password provided is incorrect, an alert will show saying "Incorrect username or password". If you successfully log in, a session will be created with the user_id, username, and access level, and you will be brought to the user dashboard page.

If you enter in a correct username but incorrectly enter the password, it display an alert saying "Incorrect password." It will also show how many attempts you have left.

#### Blocked Users
If you incorrectly enter the password for a valid username, it will be logged in a Flask session variable. If you make a mistake three consecutive times, the account is permanently blocked. Users that are blocked will have a '1' in the 'blocked' field in the database. Non-blocked users have a '0'.

#### Demo Users
I provided three different testing users with different access levels for testing purposes. Their credentials are shown below:

   <div align="center" style="display: flex; justify-content: center">

   | Username | Password | Access Level |
   | -------- | -------- | ------------ |
   | test_standard     | Password123! | Standard |
   | test_dm   | Ilikepie1% | Department Manager |
   | test_admin   | I'mADM1N!# | Administrator |
   
   </div>

If you need to reset the database, you can execute database_manager.py and it will recreate the entire file with the demo users (if you call the setup() function in demo mode).

### Testing Registration System
On the registration page, you will be prompted to enter in a new username, a new password, and you will be asked to confirm your password. The password policy requirements are shown on the registration form so you can easily create a new password.

Usernames must be between 3 and 16 characters (inclusive) and passwords must abide by the password policy outlined in the project requirements. When the input username, password, and confirmation are valid per the JavaScript client-sided validation, you will be able to submit/POST the data. When the input data is posted, Flask will perform back-end validation to ensure the requirements are all met. If it encounters any invalid inputs, it will re-render the registration page show the corresponding error(s) to the user, and prompt them to try again. 

#### Register With Strong Password Generation
If a user wishes, they can click the checkbox for "Generate Strong Password" which will generate an 8 character long strong password that abides by the password policy. In this case, the user only needs to enter a username (and click the checkbox) to POST the form. If successful, the password will be temporarily added to the session, and the user will be rerouted to the login page and where new password will be shown and they can log in with it (and their username).

### Testing Access Levels
When successfully logged in as a user, you will be brought to the dashboard. All four system application links will be displayed on the dashboard alongside the user's access level. If a user clicks on an application link, they will be brought to the corresponding page. If they have sufficient access permissions, it will display "You have successfully accessed the [application] application." If they have insufficient permissions, it will say "You are not authorized to access this page." In either case, a button will also be provided to let the user return back to the dashboard.
