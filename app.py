import sys
import os
import hashlib

lib_path = os.path.join(os.path.dirname(__file__), 'lib')
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_here_change_in_production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='student')
    courses_taught = db.relationship('Course', backref='teacher', lazy=True)

    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode('utf-8')).hexdigest()

    def is_admin(self):
        return self.role == 'admin'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(500))
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    grades = db.relationship('Grade', backref='course', lazy=True)

    def __repr__(self):
        return f"Course('{self.name}', '{self.code}')"

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(10))
    comment = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    student = db.relationship('User', foreign_keys=[student_id], backref=db.backref('grades', lazy=True))

    def __repr__(self):
        return f"Grade('{self.student_id}', '{self.course_id}', '{self.score}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        elif current_user.is_teacher():
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            next_page = request.args.get('next')
            if user.is_admin():
                return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
            elif user.is_teacher():
                return redirect(next_page) if next_page else redirect(url_for('teacher_dashboard'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('student_dashboard'))
        else:
            flash('登录失败，请检查用户名和密码', 'danger')
    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('login'))
    users = User.query.all()
    courses = Course.query.all()
    return render_template('admin_dashboard.html', users=users, courses=courses)

@app.route("/admin/user/add", methods=['GET', 'POST'])
@login_required
def admin_add_user():
    if not current_user.is_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('admin_add_user'))
        if User.query.filter_by(email=request.form['email']).first():
            flash('邮箱已被注册', 'danger')
            return redirect(url_for('admin_add_user'))
        
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            role=request.form['role']
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('用户创建成功', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_add_user.html')

@app.route("/admin/user/edit/<int:user_id>", methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if not current_user.is_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    if user.is_admin() and current_user.id != user.id:
        flash('不能编辑其他管理员', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        if user.username != request.form['username'] and User.query.filter_by(username=request.form['username']).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('admin_edit_user', user_id=user_id))
        if user.email != request.form['email'] and User.query.filter_by(email=request.form['email']).first():
            flash('邮箱已被注册', 'danger')
            return redirect(url_for('admin_edit_user', user_id=user_id))
        
        user.username = request.form['username']
        user.email = request.form['email']
        if not user.is_admin():
            user.role = request.form['role']
        if request.form['password']:
            user.set_password(request.form['password'])
        db.session.commit()
        flash('用户信息更新成功', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_edit_user.html', user=user)

@app.route("/admin/user/delete/<int:user_id>", methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    if user.is_admin():
        flash('不能删除管理员', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    db.session.delete(user)
    db.session.commit()
    flash('用户已删除', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/course/add", methods=['GET', 'POST'])
@login_required
def admin_add_course():
    if not current_user.is_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('login'))
    
    teachers = User.query.filter_by(role='teacher').all()
    
    if request.method == 'POST':
        if Course.query.filter_by(code=request.form['code']).first():
            flash('课程代码已存在', 'danger')
            return redirect(url_for('admin_add_course'))
        
        course = Course(
            name=request.form['name'],
            code=request.form['code'],
            description=request.form.get('description', ''),
            teacher_id=request.form['teacher_id']
        )
        db.session.add(course)
        db.session.commit()
        flash('课程创建成功', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_add_course.html', teachers=teachers)

@app.route("/admin/course/edit/<int:course_id>", methods=['GET', 'POST'])
@login_required
def admin_edit_course(course_id):
    if not current_user.is_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('login'))
    
    course = Course.query.get_or_404(course_id)
    teachers = User.query.filter_by(role='teacher').all()
    
    if request.method == 'POST':
        if course.code != request.form['code'] and Course.query.filter_by(code=request.form['code']).first():
            flash('课程代码已存在', 'danger')
            return redirect(url_for('admin_edit_course', course_id=course_id))
        
        course.name = request.form['name']
        course.code = request.form['code']
        course.description = request.form.get('description', '')
        course.teacher_id = request.form['teacher_id']
        db.session.commit()
        flash('课程信息更新成功', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_edit_course.html', course=course, teachers=teachers)

@app.route("/admin/course/delete/<int:course_id>", methods=['POST'])
@login_required
def admin_delete_course(course_id):
    if not current_user.is_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('login'))
    
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('课程已删除', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route("/teacher/dashboard")
@login_required
def teacher_dashboard():
    if not current_user.is_teacher():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('login'))
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher_dashboard.html', courses=courses)

@app.route("/teacher/course/<int:course_id>/grades", methods=['GET', 'POST'])
@login_required
def teacher_grades(course_id):
    if not current_user.is_teacher():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('login'))
    
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        flash('无权访问此课程', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    students = User.query.filter_by(role='student').all()
    grades = Grade.query.filter_by(course_id=course_id).all()
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        score = float(request.form['score'])
        
        existing_grade = Grade.query.filter_by(student_id=student_id, course_id=course_id).first()
        
        if score >= 90:
            letter_grade = 'A'
        elif score >= 80:
            letter_grade = 'B'
        elif score >= 70:
            letter_grade = 'C'
        elif score >= 60:
            letter_grade = 'D'
        else:
            letter_grade = 'F'
        
        if existing_grade:
            existing_grade.score = score
            existing_grade.grade = letter_grade
            existing_grade.comment = request.form.get('comment', '')
            flash('成绩已更新', 'success')
        else:
            grade = Grade(
                student_id=student_id,
                course_id=course_id,
                score=score,
                grade=letter_grade,
                comment=request.form.get('comment', '')
            )
            db.session.add(grade)
            flash('成绩已添加', 'success')
        
        db.session.commit()
        return redirect(url_for('teacher_grades', course_id=course_id))
    
    return render_template('teacher_grades.html', course=course, students=students, grades=grades)

@app.route("/teacher/grade/delete/<int:grade_id>", methods=['POST'])
@login_required
def teacher_delete_grade(grade_id):
    if not current_user.is_teacher():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('login'))
    
    grade = Grade.query.get_or_404(grade_id)
    course = Course.query.get(grade.course_id)
    
    if course.teacher_id != current_user.id:
        flash('无权删除此成绩', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    db.session.delete(grade)
    db.session.commit()
    flash('成绩已删除', 'success')
    return redirect(url_for('teacher_grades', course_id=course.id))

@app.route("/student/dashboard")
@login_required
def student_dashboard():
    if not current_user.is_student():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('login'))
    
    grades = Grade.query.filter_by(student_id=current_user.id).all()
    return render_template('student_dashboard.html', grades=grades)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
