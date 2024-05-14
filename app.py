from flask import Flask, render_template, url_for, request, session, redirect
from flask_mysqldb import MySQL
app = Flask(__name__)

app.config['MYSQL_HOST'] =  'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'Admin.51214'
app.config['MYSQL_DB'] = 'todo'
app.config['MYSQL_PORT'] = 3307
app.secret_key = 'your_secret_key_here'

mysql = MySQL(app)



@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/register', methods = ['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        # Check if the form fields are present in the request
        if 'name' in request.form and 'password' in request.form and 'email' in request.form:
            name = request.form['name']
            password = request.form['password']
            email = request.form['email']

            # Check if the email already exists in the database
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
            existing_user = cursor.fetchone()
            cursor.close()

            if existing_user:
                message = 'Email Already exists!'
            elif not name or not password or not email:
                message = "Please fill out the form!"
            else:
                # Insert new user data into the database
                cursor = mysql.connection.cursor()
                cursor.execute("INSERT INTO user (name, password, email) VALUES (%s, %s, %s)", (name, password, email))
                mysql.connection.commit()
                cursor.close()
                message = 'You have successfully registered!'
        else:
            message = "Please fill out the form!"

    return render_template('register.html', message = message)    


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        # Check if the form fields are present in the request
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']

            # Fetch user data from the database
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()

            if user is None:
                message = 'Please enter correct username/password!'
            elif user[3] != password:  # Assuming password is stored in the third column
                message = 'Please enter correct email / password!'
            else:
                # Set up session for the user
                session['loggedin'] = True
                session['userid'] = user[0]  # Assuming user ID is stored in the first column
                session['email'] = user[2]  # Assuming username is stored in the second column
                message = 'Logged in successfully!'
                return redirect(url_for('dashboard'))

    return render_template('login.html', message=message)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        try:
            # Establish connection to MySQL
            cur = mysql.connection.cursor()
            # Execute query to fetch data from employes table
            cur.execute("SELECT * FROM employes")
            data_employe = cur.fetchall()
            cur.close()
            return render_template('dashboard.html', data=data_employe)
        except Exception as e:
            # Handle any errors that might occur during database access
            print("An error occurred:", e)
            return render_template('error.html', error_message="An error occurred while accessing data.")
    return redirect(url_for('login'))

@app.route('/input', methods=['GET', 'POST'])
def input_data():
    if 'loggedin' in session:
        if request.method == 'POST':
            try:
                # Get form data
                name = request.form['name']
                email = request.form['email']
                telp = request.form['telp']
                address = request.form['address']

                # Establish connection to MySQL
                cur = mysql.connection.cursor()
                # Execute SQL query to insert data into employes table
                cur.execute("INSERT INTO employes (name, email, telp, address) VALUES (%s, %s, %s, %s)", (name, email, telp, address))
                mysql.connection.commit()
                cur.close()
                message = "Data added successfully !"

                return redirect(url_for('dashboard', message = message))
            except Exception as e:
                # Handle any errors that might occur during database access
                print("An error occurred:", e)
                return render_template('error.html', error_message="An error occurred while inserting data.")
    return render_template('input.html')

@app.route('/edit/<int:id>')
def edit_data(id):
    if 'loggedin' in session:
        try:
            # Establish connection to MySQL
            cur = mysql.connection.cursor()

            # Execute SQL query to select data for the specific employee
            cur.execute("SELECT * FROM employes WHERE id = %s", (id,))
            data_employee = cur.fetchone()

            cur.close()

            # Render the edit template with the employee data
            return render_template('edit.html', data=data_employee)
        except Exception as e:
            # Handle any errors that might occur during database access
            print("An error occurred:", e)
            return render_template('error.html', error_message="An error occurred while fetching employee data.")
    else:
        return redirect(url_for('login'))
    
@app.route('/process_edit', methods=['POST'])
def process_edit():
    if 'loggedin' in session:
        try:
            # Get form data
            id = request.form.get('id')
            name = request.form['name']
            email = request.form['email']
            telp = request.form['telp']
            address = request.form['address']

            # Establish connection to MySQL
            cur = mysql.connection.cursor()

            # Execute SQL query to update the data of the employee
            cur.execute("UPDATE employes SET name = %s, email = %s, telp = %s, address = %s WHERE id = %s", (name, email, telp, address, id))
            mysql.connection.commit()
            cur.close()

            # Redirect to dashboard after successful update
            return redirect(url_for('dashboard'))
        except Exception as e:
            # Handle any errors that might occur during database access
            print("An error occurred:", e)
            return render_template('error.html', error_message="An error occurred while updating employee data.")
    else:
        return redirect(url_for('login'))
    
@app.route('/delete/<int:id>')
def delete(id):
    if 'loggedin' in session:
        try:
            # Establish connection to MySQL
            cur = mysql.connection.cursor()

            # Execute SQL query to delete the employee record
            cur.execute("DELETE FROM employes WHERE id = %s", (id,))
            mysql.connection.commit()
            cur.close()

            # Redirect to dashboard after successful deletion
            return redirect(url_for('dashboard'))
        except Exception as e:
            # Handle any errors that might occur during database access
            print("An error occurred:", e)
            return render_template('error.html', error_message="An error occurred while deleting employee data.")
    else:
        return redirect(url_for('login'))


app.run(debug=True)