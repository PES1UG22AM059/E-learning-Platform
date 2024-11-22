from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from .db import create_connection, close_connection

main = Blueprint('main', __name__)
import datetime


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Insert data into the database
        try:
            conn = create_connection()
            cursor = conn.cursor()

            query = "INSERT INTO contactus (name, email, message) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, message))
            conn.commit()

            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash("An error occurred while sending your message. Please try again.", "danger")
            print(f"Error: {e}")
        finally:
            close_connection(conn)

        # Redirect back to the contact page
        return redirect(url_for('main.contact'))

    # Render the contact form
    return render_template('contact.html')

# Intro route
@main.route('/intro')
def intro():
    return render_template('intro.html')

# About route
@main.route('/about')
def about():
    return render_template('about.html')

# Contact route
'''@main.route('/contact')
def contact():
    return render_template('contact.html')'''

# Register route with username uniqueness check
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        name = request.form.get('name')

        if not username or not password or not email or not name:
            flash("Please fill out all fields.", "error")
            return redirect(url_for('main.register'))

        db_connection = create_connection()
        if db_connection:
            cursor = db_connection.cursor()
            try:
                # Check if username already exists
                cursor.execute("SELECT * FROM User WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash("Username already taken. Please choose a different one.", "error")
                    return redirect(url_for('main.register'))

                # Insert new user
                cursor.execute("INSERT INTO User (username, password, email, name) VALUES (%s, %s, %s, %s)",
                               (username, password, email, name))
                db_connection.commit()
                flash("Registration successful!", "success")
                session['username'] = username  # Log in the user after registration
                return redirect(url_for('main.home'))
            except Exception as e:
                db_connection.rollback()
                flash(f"An error occurred while registering: {str(e)}", "error")
            finally:
                cursor.close()
                close_connection(db_connection)
        else:
            flash("Could not connect to the database.", "error")
            return redirect(url_for('main.register'))
    return render_template('register.html')

# Home route
@main.route('/', methods=['GET'])
def home():
    return render_template('home.html')

# Login route
@main.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return redirect(url_for('main.login_user'))

        db_connection = create_connection()
        if db_connection:
            cursor = db_connection.cursor()
            try:
                cursor.execute("SELECT * FROM User WHERE username = %s", (username,))
                user = cursor.fetchone()

                if user and user[2] == password:
                    session['username'] = user[1]  # Store username in session
                    flash("Login successful!", "success")
                    return redirect(url_for('main.home'))
                else:
                    flash("Invalid credentials.", "error")
            except Exception as e:
                flash(f"An error occurred while logging in: {str(e)}", "error")
            finally:
                cursor.close()
                close_connection(db_connection)

    return render_template('login.html')

# Profile route
@main.route('/profile', methods=['GET', 'POST'])
def profile():
    current_username = session.get('username')
    if not current_username:
        flash("Please log in to access your profile.", "error")
        return redirect(url_for('main.login_user'))

    db_connection = create_connection()
    if db_connection:
        cursor = db_connection.cursor()
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            username = request.form.get('username')
            age = request.form.get('age')
            address = request.form.get('address')
            phone_number = request.form.get('phone_number')
            profession = request.form.get('profession')

            try:
                cursor.execute("""
                    UPDATE User 
                    SET name = %s, email = %s, username = %s, age = %s, address = %s, phone_number = %s, profession = %s 
                    WHERE username = %s
                """, (name, email, username, age, address, phone_number, profession, current_username))
                db_connection.commit()

                # If the username was changed, update session as well
                if username != current_username:
                    session['username'] = username

                flash("Profile updated successfully!", "success")
            except Exception as e:
                db_connection.rollback()
                flash(f"An error occurred while updating your profile: {str(e)}", "error")
            finally:
                cursor.close()
                close_connection(db_connection)
            return redirect(url_for('main.profile'))

        try:
            cursor.execute("SELECT name, email, username, age, address, phone_number, profession FROM User WHERE username = %s", (current_username,))
            user_data = cursor.fetchone()
            if user_data:
                return render_template('profile.html', user_data=user_data)
            else:
                flash("User not found.", "error")
        except Exception as e:
            flash(f"Error fetching user data: {str(e)}", "error")
        finally:
            cursor.close()
            close_connection(db_connection)

    flash("Error fetching user data.", "error")
    return redirect(url_for('main.login_user'))

# Courses route
@main.route('/courses', methods=['GET'])
def courses():
    return render_template('courses.html')

# Enrollment route
@main.route('/enroll', methods=['POST'])
def enroll():
    course_name = request.json.get('course_name')  # Changed to JSON for JS compatibility
    current_username = session.get('username')

    if not course_name or not current_username:
        return jsonify({"success": False, "message": "Course or user information missing."}), 400

    db_connection = create_connection()
    if db_connection:
        cursor = db_connection.cursor()
        try:
            # Check if user is already enrolled in the course
            cursor.execute("SELECT * FROM Enrollment WHERE username = %s AND course_name = %s", (current_username, course_name))
            existing_enrollment = cursor.fetchone()

            if existing_enrollment:
                return jsonify({"success": False, "message": "You have already enrolled in this course."})

            # Insert new enrollment
            cursor.execute("""
                INSERT INTO Enrollment (username, course_name, enrollment_date, completion_status) 
                VALUES (%s, %s, CURDATE(), 'not completed')
            """, (current_username, course_name))
            db_connection.commit()

            return jsonify({"success": True, "message": f"Successfully enrolled in {course_name}!"})
        except Exception as e:
            db_connection.rollback()
            return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500
        finally:
            cursor.close()
            close_connection(db_connection)
    else:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

# Logout route
@main.route('/logout')
def logout_user():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('main.intro'))


'''# Course lesson routes - Direct Course Pages
@main.route('/python_course')
def python_course():
   return render_template('python_course.html')


@main.route('/r_course')
def r_course():
    return render_template('r_course.html')

@main.route('/web_development_course')
def web_development_course():
    return render_template('web_development_course.html')

@main.route('/machine_learning_course')
def machine_learning_course():
    return render_template('machine_learning_course.html')

@main.route('/artificial_intelligence_basics_course')
def artificial_intelligence_basics_course():
    return render_template('artificial_intelligence_basics_course.html')

@main.route('/cloud_computing_course')
def cloud_computing_course():
    return render_template('cloud_computing_course.html')'''

# Add this helper function at the top of your routes.py
def check_enrollment(username, course_name):
    db_connection = create_connection()
    if db_connection:
        cursor = db_connection.cursor()
        try:
            cursor.execute("SELECT * FROM Enrollment WHERE username = %s AND course_name = %s", 
                         (username, course_name))
            enrollment = cursor.fetchone()
            return enrollment is not None
        finally:
            cursor.close()
            close_connection(db_connection)
    return False

# Modified course routes with enrollment check
@main.route('/python_course')
def python_course():
    current_username = session.get('username')
    if not current_username:
        flash("Please log in to access the course.", "error")
        return redirect(url_for('main.intro'))
    
    if check_enrollment(current_username, "Python Programming"):
        return render_template('python_course.html')
    else:
        flash("Please enroll in the Python Programming course first.", "error")
        return redirect(url_for('main.courses'))

@main.route('/r_course')
def r_course():
    current_username = session.get('username')
    if not current_username:
        flash("Please log in to access the course.", "error")
        return redirect(url_for('main.intro'))
    
    if check_enrollment(current_username, "Data Science with R"):
        return render_template('r_course.html')
    else:
        flash("Please enroll in the Data Science with R course first.", "error")
        return redirect(url_for('main.courses'))

@main.route('/web_development_course')
def web_development_course():
    current_username = session.get('username')
    if not current_username:
        flash("Please log in to access the course.", "error")
        return redirect(url_for('main.intro'))
    
    if check_enrollment(current_username, "Web Development"):
        return render_template('web_development_course.html')
    else:
        flash("Please enroll in the Web Development course first.", "error")
        return redirect(url_for('main.courses'))

@main.route('/machine_learning_course')
def machine_learning_course():
    current_username = session.get('username')
    if not current_username:
        flash("Please log in to access the course.", "error")
        return redirect(url_for('main.intro'))
    
    if check_enrollment(current_username, "Machine Learning"):
        return render_template('machine_learning_course.html')
    else:
        flash("Please enroll in the Machine Learning course first.", "error")
        return redirect(url_for('main.courses'))

@main.route('/artificial_intelligence_basics_course')
def artificial_intelligence_basics_course():
    current_username = session.get('username')
    if not current_username:
        flash("Please log in to access the course.", "error")
        return redirect(url_for('main.intro'))
    
    if check_enrollment(current_username, "Artificial Intelligence Basics"):
        return render_template('artificial_intelligence_basics_course.html')
    else:
        flash("Please enroll in the Artificial Intelligence Basics course first.", "error")
        return redirect(url_for('main.courses'))

@main.route('/cloud_computing_course')
def cloud_computing_course():
    current_username = session.get('username')
    if not current_username:
        flash("Please log in to access the course.", "error")
        return redirect(url_for('main.intro'))
    
    if check_enrollment(current_username, "Cloud Computing Essentials"):
        return render_template('cloud_computing_course.html')
    else:
        flash("Please enroll in the Cloud Computing Essentials course first.", "error")
        return redirect(url_for('main.courses'))

@main.route('/python_test')
def python_test():
    return render_template('python_test.html')

@main.route('/ml_test')
def ml_test():
    return render_template('ml_test.html')

@main.route('/web_test')
def web_test():
    return render_template('web_test.html')

@main.route('/ai_test')
def ai_test():
    return render_template('ai_test.html')

@main.route('/cloud_test')
def cloud_test():
    return render_template('cloud_test.html')

@main.route('/r_test')
def r_test():
    return render_template('r_test.html')


@main.route('/submit_assessment/<course_name>', methods=['POST'])
def submit_assessment(course_name):
    # Map course names to match assessment table
    course_mapping = {
        'Python Programming': 'Python Programming',
        'Machine Learning': 'Machine Learning',
        'Web Development': 'Web Development',
        'Artificial Intelligence Basics': 'Artificial Intelligence Basics',
        'Cloud Computing Essentials': 'Cloud Computing Essentials',
        'Data Science with R': 'Data Science with R'
    }
    # mapped_course_name = course_mapping.get(course_name, course_name)
    mapped_course_name = course_mapping.get(course_name)
    print("Mapped course name",mapped_course_name)

    # Retrieve answers from the form
    user_answers = {
        field: request.form.get(field, '').strip().lower() 
        for field in request.form
        } 
    print("User answers",user_answers)
 # Retrieve correct answers from the database
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT question_id, correct_answer FROM assessment WHERE course_name = %s"
    cursor.execute(query, (mapped_course_name,))
    correct_answers = {row['question_id']: row['correct_answer'].strip().lower() for row in cursor.fetchall()}
    print("correct answers from DB",correct_answers)

    marks = 0
    for question_id, correct_answer in correct_answers.items():
        user_answer = user_answers.get(question_id, '').lower()
        print(f"Comparing - Question: {question_id}")
        print(f"User answer: '{user_answer}'")
        print(f"Correct answer: '{correct_answer}'")
        if user_answer == correct_answer:
            marks += 5
            print("Match found! Adding 5 marks")
    
    print("Final marks:", marks)

    total_questions = len(correct_answers)
    total_marks = total_questions * 5

# Store results in database
    username = session.get('username')
    user_id = session.get('user_id')
    
    # Prepare assessment results
    assessment_results = {
        'course_name': mapped_course_name,
        'marks': marks,
        'total_marks': total_marks,
        'percentage': (marks / total_marks) * 100,
        'date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'username':username
    }

    
#     user_id = session.get('user_id')
# ##############
#     if not user_id:
#         flash("User ID not found in session. Please log in again.", "error")
#         return redirect(url_for('main.login_user'))

    
    try:
        insert_query = """
            INSERT INTO certificate (user_id, course_name, marks, username, assessment_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (user_id, mapped_course_name, marks, username, assessment_results['date']))
        connection.commit()
    except Exception as e:
        connection.rollback()
        flash(f"Error storing assessment results: {e}", "error")
    finally:
        cursor.close()
        close_connection(connection)

    # Store results in session for displaying
    session['assessment_results'] = {mapped_course_name: assessment_results}

    return redirect(url_for('main.assessment_result', course_name=mapped_course_name))



@main.route('/assessment_result/<course_name>')
def assessment_result(course_name):
    # Retrieve results from the session
    assessment_results = session.get('assessment_results', {})
    
    # Check if results exist for the specific course
    if course_name not in assessment_results:
        flash("No assessment results found for this course.", "error")
        return redirect(url_for('main.home'))
    
    # Get the specific course results
    results = assessment_results[course_name]
    
    return render_template('assessment_result.html', results=results)

# Simplified route handlers for each course test submission
@main.route('/submit_python', methods=['POST'])
def submit_python():
    return submit_assessment('Python Programming')

@main.route('/submit_ml', methods=['POST'])
def submit_ml():
    return submit_assessment('Machine Learning')

@main.route('/submit_web', methods=['POST'])
def submit_web():
    return submit_assessment('Web Development')

@main.route('/submit_ai', methods=['POST'])
def submit_ai():
    return submit_assessment('Artificial Intelligence Basics')

@main.route('/submit_cloud', methods=['POST'])
def submit_cloud():
    return submit_assessment('Cloud Computing Essentials')

@main.route('/submit_r', methods=['POST'])
def submit_r():
    return submit_assessment('Data Science with R')   

@main.route('/update_completion_status', methods=['POST'])
def update_completion_status():
    if request.method == 'POST':
        data = request.get_json()
        course_name = data.get('course_name')
        username = data.get('username')

        try:
            conn = create_connection()
            cursor = conn.cursor()

            # Update the completion status in the database
            query = """
                UPDATE enrollment
                SET completion_status = 'completed'
                WHERE course_name = %s AND username = %s
            """
            cursor.execute(query, (course_name, username))
            conn.commit()

            return jsonify({"message": "Completion status updated successfully."}), 200
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return jsonify({"error": "Failed to update completion status."}), 500
        finally:
            close_connection(conn)