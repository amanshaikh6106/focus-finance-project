
import os
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db_connection
from eligibility import calculate_eligibility, save_eligibility
from apply import save_application, get_user_applications
from contact import save_contact_message
from admin import get_all_users, get_all_eligibility, get_all_applications, get_all_contacts, update_application_status
from auth_extra import change_user_password, verify_identity_for_reset, reset_password_by_user_id
from emi import calculate_emi

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "change-this-local-development-key")



def login_required(f):
    """Redirects to the login page if there is no active user session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Only allows access if the logged-in user is an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            flash("You do not have permission to access the admin panel.", "error")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/health')
def health():
    return {'status': 'ok'}, 200


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Basic validation
        if not all([full_name, username, email, mobile, password, confirm_password]):
            flash("All fields are required.", "error")
            return render_template('signup.html')

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('signup.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template('signup.html')

        connection = get_db_connection()
        if connection is None:
            flash("Database connection error. Please try again later.", "error")
            return render_template('signup.html')

        cursor = connection.cursor(dictionary=True)

        # Check for duplicate username/email
        cursor.execute(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username or email already exists. Please choose another.", "error")
            cursor.close()
            connection.close()
            return render_template('signup.html')

        hashed_password = generate_password_hash(password)

        try:
            cursor.execute(
                """INSERT INTO users (full_name, username, email, mobile, password)
                   VALUES (%s, %s, %s, %s, %s)""",
                (full_name, username, email, mobile, hashed_password)
            )
            connection.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            print(f"[SIGNUP ERROR] {e}")
            flash("Something went wrong while creating your account.", "error")
            return render_template('signup.html')
        finally:
            cursor.close()
            connection.close()

    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        if not identifier or not password:
            flash("Please enter both username/email and password.", "error")
            return render_template('login.html')

        connection = get_db_connection()
        if connection is None:
            flash("Database connection error. Please try again later.", "error")
            return render_template('login.html')

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE username = %s OR email = %s",
            (identifier, identifier)
        )
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['is_admin'] = bool(user.get('is_admin'))

            # Update last_login timestamp
            cursor.execute(
                "UPDATE users SET last_login = NOW() WHERE id = %s",
                (user['id'],)
            )
            connection.commit()
            cursor.close()
            connection.close()

            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(url_for('index'))
        else:
            cursor.close()
            connection.close()
            flash("Invalid username/email or password.", "error")
            return render_template('login.html')

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('login'))



@app.route('/index')
def index():
    return render_template('index.html')



@app.route('/eligibility', methods=['GET', 'POST'])
@login_required
def eligibility():
    result = None
    reasons = []
    submitted_data = None

    if request.method == 'POST':
        data = {
            'full_name': request.form.get('full_name', '').strip(),
            'age': request.form.get('age', '').strip(),
            'gender': request.form.get('gender', '').strip(),
            'mobile': request.form.get('mobile', '').strip(),
            'email': request.form.get('email', '').strip(),
            'employment_type': request.form.get('employment_type', '').strip(),
            'monthly_income': request.form.get('monthly_income', '').strip(),
            'monthly_expenses': request.form.get('monthly_expenses', '').strip(),
            'monthly_savings': request.form.get('monthly_savings', '').strip(),
            'existing_emi': request.form.get('existing_emi', '').strip(),
            'credit_score': request.form.get('credit_score', '').strip(),
            'loan_type': request.form.get('loan_type', '').strip(),
            'loan_amount': request.form.get('loan_amount', '').strip(),
            'loan_tenure': request.form.get('loan_tenure', '').strip(),
        }

        try:
            result, reasons = calculate_eligibility(data)
            save_eligibility(data, result, user_id=session.get('user_id'))
            submitted_data = data
        except (ValueError, KeyError):
            flash("Please enter valid numeric values in all required fields.", "error")
            return render_template('eligibility.html')

    return render_template(
        'eligibility.html',
        result=result,
        reasons=reasons,
        submitted_data=submitted_data
    )



@app.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    submitted = False
    emi_details = None

    if request.method == 'POST':
        data = {
            'full_name': request.form.get('full_name', '').strip(),
            'age': request.form.get('age', '').strip(),
            'email': request.form.get('email', '').strip(),
            'mobile': request.form.get('mobile', '').strip(),
            'address': request.form.get('address', '').strip(),
            'city': request.form.get('city', '').strip(),
            'state': request.form.get('state', '').strip(),
            'occupation': request.form.get('occupation', '').strip(),
            'monthly_income': request.form.get('monthly_income', '').strip(),
            'loan_type': request.form.get('loan_type', '').strip(),
            'loan_amount': request.form.get('loan_amount', '').strip(),
            'loan_tenure': request.form.get('loan_tenure', '').strip(),
        }

        success = save_application(data, user_id=session.get('user_id'))

        if success:
            submitted = True
            try:
                emi_details = calculate_emi(
                    data['loan_amount'],
                    data['loan_tenure'],
                    data['loan_type']
                )
            except (ValueError, TypeError):
                emi_details = None
            flash("Loan Application Submitted Successfully.", "success")
        else:
            flash("Something went wrong while submitting your application. Please try again.", "error")

    return render_template('apply.html', submitted=submitted, emi_details=emi_details)



@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        data = {
            'name': request.form.get('c_name', '').strip(),
            'email': request.form.get('c_email', '').strip(),
            'subject': request.form.get('c_subject', '').strip(),
            'message': request.form.get('c_message', '').strip(),
        }

        success = save_contact_message(data, user_id=session.get('user_id'))

        if success:
            flash("Thank you for reaching out! Our team will get back to you soon.", "success")
        else:
            flash("Something went wrong while sending your message. Please try again.", "error")

        return redirect(url_for('contact'))

    return render_template('contact.html')



@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    connection = get_db_connection()
    if connection is None:
        flash("Database connection error. Please try again later.", "error")
        return redirect(url_for('index'))

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()

        if not all([full_name, email, mobile]):
            flash("All fields are required.", "error")
            cursor.close()
            connection.close()
            return render_template('profile.html', user=user)

        # Check if the new email is already used by a different account
        cursor.execute(
            "SELECT id FROM users WHERE email = %s AND id != %s",
            (email, session['user_id'])
        )
        existing = cursor.fetchone()

        if existing:
            flash("That email is already in use by another account.", "error")
            cursor.close()
            connection.close()
            return render_template('profile.html', user=user)

        try:
            cursor.execute(
                "UPDATE users SET full_name = %s, email = %s, mobile = %s WHERE id = %s",
                (full_name, email, mobile, session['user_id'])
            )
            connection.commit()

            # Keep session data in sync with the updated profile
            session['full_name'] = full_name

            flash("Profile updated successfully!", "success")
            cursor.close()
            connection.close()
            return redirect(url_for('profile'))
        except Exception as e:
            print(f"[DB ERROR] Could not update profile: {e}")
            flash("Something went wrong while updating your profile.", "error")
            cursor.close()
            connection.close()
            return render_template('profile.html', user=user)

    cursor.close()
    connection.close()
    return render_template('profile.html', user=user)



@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not all([current_password, new_password, confirm_password]):
            flash("All fields are required.", "error")
            return redirect(url_for('profile'))

        if new_password != confirm_password:
            flash("New passwords do not match.", "error")
            return redirect(url_for('profile'))

        if len(new_password) < 6:
            flash("New password must be at least 6 characters long.", "error")
            return redirect(url_for('profile'))

        connection = get_db_connection()
        if connection is None:
            flash("Database connection error. Please try again later.", "error")
            return redirect(url_for('profile'))

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT password FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if not user or not check_password_hash(user['password'], current_password):
            flash("Your current password is incorrect.", "error")
            return redirect(url_for('profile'))

        hashed_new_password = generate_password_hash(new_password)
        success = change_user_password(session['user_id'], hashed_new_password)

        if success:
            flash("Password changed successfully!", "success")
        else:
            flash("Something went wrong. Please try again.", "error")

        return redirect(url_for('profile'))

    return redirect(url_for('profile'))



@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not all([username, email, mobile, new_password, confirm_password]):
            flash("All fields are required.", "error")
            return render_template('forgot_password.html')

        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('forgot_password.html')

        if len(new_password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template('forgot_password.html')

        user_id = verify_identity_for_reset(username, email, mobile)

        if user_id is None:
            flash("We could not verify your identity. Please check your details and try again.", "error")
            return render_template('forgot_password.html')

        success = reset_password_by_user_id(user_id, new_password)

        if success:
            flash("Password reset successfully! Please log in with your new password.", "success")
            return redirect(url_for('login'))
        else:
            flash("Something went wrong. Please try again.", "error")

    return render_template('forgot_password.html')


@app.route('/my-loan-status')
@login_required
def my_loan_status():
    applications = get_user_applications(session.get('user_id'))
    return render_template('my_loan_status.html', applications=applications)


@app.route('/admin')
@admin_required
def admin_dashboard():
    users = get_all_users()
    eligibility_records = get_all_eligibility()
    applications = get_all_applications()
    contacts = get_all_contacts()

    return render_template(
        'admin.html',
        users=users,
        eligibility_records=eligibility_records,
        applications=applications,
        contacts=contacts
    )



@app.route('/admin/update-status/<int:application_id>', methods=['POST'])
@admin_required
def admin_update_status(application_id):
    new_status = request.form.get('status')

    if new_status not in ('Approved', 'Rejected', 'Pending'):
        flash("Invalid status update.", "error")
        return redirect(url_for('admin_dashboard'))

    success = update_application_status(application_id, new_status)

    if success:
        flash(f"Application #{application_id} marked as {new_status}.", "success")
    else:
        flash("Something went wrong while updating the status.", "error")

    return redirect(url_for('admin_dashboard'))



if __name__ == '__main__':
    app.run(debug=True)
