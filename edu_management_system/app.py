from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
from datetime import timedelta
from functools import wraps 
import hashlib

# 初始化Flask应用
app = Flask(__name__)
app.secret_key = 'your_secret_key_123456'
app.config['SECRET_KEY'] = 'edu_system_2026'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# ===================== 权限装饰器（核心：统一控制权限） =====================
def permission_required(allowed_roles):
    """
    权限校验装饰器：限制只有指定角色能访问接口
    :param allowed_roles: 允许访问的角色列表，比如 ['admin'] 或 ['admin', 'teacher']
    :return: 装饰器函数
    """
    def decorator(view_func):
        @wraps(view_func)  # 保留原视图函数的信息，避免flask路由出错
        def wrapper(*args, **kwargs):
            # 1. 未登录直接重定向到登录页（针对页面路由），接口返回无权限
            if 'username' not in session:
                # 判断是页面路由还是接口路由（通过请求头/URL特征）
                if request.path.startswith('/api/'):
                    return jsonify({'success': False, 'message': '请先登录'}), 401
                else:
                    return redirect(url_for('login_page'))
            
            # 2. 从session中获取当前登录用户的角色
            current_user_role = session.get('role')
            
            # 3. 校验权限
            if not current_user_role or current_user_role not in allowed_roles:
                if request.path.startswith('/api/'):
                    return jsonify({'success': False, 'message': '无访问权限，请使用对应角色登录'}), 403
                else:
                    return redirect(url_for('index'))
            
            # 4. 权限通过，执行原接口的逻辑
            return view_func(*args, **kwargs)
        return wrapper
    return decorator

# -------------------------- 数据库连接 --------------------------
def get_db_connection():
    conn = pymysql.connect(
        host='localhost',
        user='root',        
        password='',  # 替换为你的MySQL密码
        database='educational_management_system',
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

# -------------------------- 初始化管理员和视图 --------------------------
def init_system():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. 初始化管理员（默认密码123456，MD5加密）
        cursor.execute("""
            INSERT IGNORE INTO users (username, password, role, related_id) 
            VALUES ('admin', 'e10adc3949ba59abbe56e057f20f883e', 'admin', '000000');
        """)
        
        # 2. 创建所有MySQL视图（如果不存在则创建，存在则替换）
        # 2.1 专业视图（关联院系）
        cursor.execute("""
            CREATE OR REPLACE VIEW v_majors AS
            SELECT m.*, d.dept_name 
            FROM majors m
            LEFT JOIN departments d ON m.dept_id = d.dept_id;
        """)
        
        # 2.2 班级视图（关联专业+院系）
        cursor.execute("""
            CREATE OR REPLACE VIEW v_classes AS
            SELECT c.*, m.major_name, d.dept_name 
            FROM classes c
            LEFT JOIN majors m ON c.major_id = m.major_id
            LEFT JOIN departments d ON m.dept_id = d.dept_id;
        """)
        
        # 2.3 学生视图（关联班级+专业+院系）
        cursor.execute("""
            CREATE OR REPLACE VIEW v_students AS
            SELECT s.*, c.class_name, m.major_name, d.dept_name 
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN majors m ON c.major_id = m.major_id
            LEFT JOIN departments d ON m.dept_id = d.dept_id;
        """)
        
        # 2.4 教师视图（关联院系）
        cursor.execute("""
            CREATE OR REPLACE VIEW v_teachers AS
            SELECT t.*, d.dept_name 
            FROM teachers t
            LEFT JOIN departments d ON t.dept_id = d.dept_id;
        """)
        
        # 2.5 课程安排视图（关联课程+教师+班级，修正为day/period字段）
        cursor.execute("""
            CREATE OR REPLACE VIEW v_course_arrangements AS
            SELECT 
                ca.arrangement_id,
                ca.course_id, c.course_name, c.credit, c.hours, c.type,
                ca.teacher_id, t.teacher_name,
                ca.class_id, cl.class_name, cl.grade,
                ca.semester, ca.week, ca.day, ca.period, ca.classroom
            FROM course_arrangements ca
            LEFT JOIN courses c ON ca.course_id = c.course_id
            LEFT JOIN teachers t ON ca.teacher_id = t.teacher_id
            LEFT JOIN classes cl ON ca.class_id = cl.class_id;
        """)
        
        # 2.6 学生课表视图（专用，修正为day/period字段）
        cursor.execute("""
            CREATE OR REPLACE VIEW v_student_timetable AS
            SELECT 
                ca.arrangement_id,
                ca.course_id, c.course_name, c.credit, c.hours, c.type,
                ca.teacher_id, t.teacher_name,
                s.student_id, s.student_name,
                cl.class_id, cl.class_name,
                ca.semester, ca.week, ca.day, ca.period, ca.classroom
            FROM course_arrangements ca
            LEFT JOIN courses c ON ca.course_id = c.course_id
            LEFT JOIN teachers t ON ca.teacher_id = t.teacher_id
            LEFT JOIN classes cl ON ca.class_id = cl.class_id
            LEFT JOIN students s ON cl.class_id = s.class_id;
        """)
        
        conn.commit()
        print("✅ 系统初始化完成：管理员账号（admin/123456），所有视图创建成功")
    except Exception as e:
        print(f"⚠️ 初始化提示：{e}（视图已存在属于正常情况）")
    finally:
        cursor.close()
        conn.close()

# 执行系统初始化
init_system()

# -------------------------- 核心路由（登录/首页/退出） --------------------------
# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'username' in session:
        return redirect(url_for('index'))
    
    # POST请求处理登录
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 密码MD5加密
        md5_password = hashlib.md5(password.encode()).hexdigest()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username, md5_password)
            )
            user = cursor.fetchone()
            
            if user:
                session['username'] = user['username']
                session['role'] = user['role']
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='用户名或密码错误')
        finally:
            cursor.close()
            conn.close()
    
    # GET请求返回登录页
    return render_template('login.html')

# 登录接口（AJAX调用）
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        md5_password = hashlib.md5(password.encode()).hexdigest()
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, md5_password)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': '用户名或密码错误'})
        
        # 存入session
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['role'] = user['role']
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {'username': user['username'], 'role': user['role']}
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 首页（总入口）
@app.route('/')
def index():
    # 未登录则跳转到登录页
    if 'username' not in session:
        return redirect('/login')
    
    # 获取当前用户信息
    username = session['username']
    role = session['role']
    real_name = ''
    role_cn = ''
    
    # 根据角色查询真实姓名（使用视图）
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if role == 'admin':
            role_cn = '管理员'
            real_name = '系统管理员'  # 管理员默认名称
        elif role == 'teacher':
            role_cn = '教师'
            # 使用视图v_teachers查询教师姓名
            cursor.execute("SELECT teacher_name FROM v_teachers WHERE teacher_id = %s", (username,))
            teacher_data = cursor.fetchone()
            real_name = teacher_data['teacher_name'] if teacher_data else username
        elif role == 'student':
            role_cn = '学生'
            # 使用视图v_students查询学生姓名
            cursor.execute("SELECT student_name FROM v_students WHERE student_id = %s", (username,))
            student_data = cursor.fetchone()
            real_name = student_data['student_name'] if student_data else username
    finally:
        cursor.close()
        conn.close()
    
    # 传递变量到模板
    return render_template('index.html', 
                           username=username, 
                           role=role, 
                           real_name=real_name,
                           role_cn=role_cn)

# ===================== 学生专属：我的课程页面 =====================
@app.route('/my_courses')
@permission_required(['student'])
def my_courses_page():
    # 获取学生信息（使用视图）
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT student_name FROM v_students WHERE student_id = %s", (session['username'],))
        student_data = cursor.fetchone()
        real_name = student_data['student_name'] if student_data else session['username']
    finally:
        cursor.close()
        conn.close()
    
    return render_template('my_courses.html',
                           username=session['username'],
                           real_name=real_name,
                           role='student')
                           
# 退出登录（页面跳转）
@app.route('/logout')
def logout_page():
    session.clear()
    return redirect('/login')

# 退出登录接口（AJAX调用）
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': '退出登录成功'})

# ===================== 1. 院系管理模块 =====================
# 院系管理页面
@app.route('/manage_departments')
@permission_required(['admin'])
def manage_department_page():
    return render_template('manage_department.html')

# 添加院系
@app.route('/api/departments', methods=['POST'])
@permission_required(['admin'])
def add_department():
    data = request.get_json()
    dept_name = data.get('dept_name')
    
    if not dept_name:
        return jsonify({'success': False, 'message': '院系名称为必填项'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO departments (dept_name) VALUES (%s);", (dept_name,))
        conn.commit()
        return jsonify({'success': True, 'message': '院系添加成功！'})
    except pymysql.IntegrityError:
        conn.rollback()
        return jsonify({'success': False, 'message': '该院系名称已存在'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 查询院系（支持筛选）
@app.route('/api/departments', methods=['GET'])
@permission_required(['admin', 'teacher'])
def get_departments():
    dept_name = request.args.get('dept_name', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "SELECT * FROM departments WHERE 1=1"
        params = []
        if dept_name:
            sql += " AND dept_name LIKE %s"
            params.append(f"%{dept_name}%")
        cursor.execute(sql, params)
        depts = cursor.fetchall()
        return jsonify({'success': True, 'data': depts})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 删除院系
@app.route('/api/departments/<dept_id>', methods=['DELETE'])
@permission_required(['admin'])
def delete_department(dept_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT dept_id FROM departments WHERE dept_id = %s", (dept_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '院系不存在'})
        
        cursor.execute("DELETE FROM departments WHERE dept_id = %s", (dept_id,))
        conn.commit()
        return jsonify({'success': True, 'message': '院系删除成功（关联专业已自动清理）！'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# ===================== 2. 专业管理模块 =====================
# 专业管理页面
@app.route('/manage_majors')
@permission_required(['admin'])
def manage_major_page():
    return render_template('manage_major.html')

# 添加专业
@app.route('/api/majors', methods=['POST'])
@permission_required(['admin'])
def add_major():
    data = request.get_json()
    major_name = data.get('major_name')
    dept_id = data.get('dept_id')
    
    if not all([major_name, dept_id]):
        return jsonify({'success': False, 'message': '专业名称、所属院系为必填项'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO majors (major_name, dept_id) VALUES (%s, %s);", (major_name, dept_id))
        conn.commit()
        return jsonify({'success': True, 'message': '专业添加成功！'})
    except pymysql.IntegrityError:
        conn.rollback()
        return jsonify({'success': False, 'message': '专业名称已存在'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 查询专业（使用视图v_majors）
@app.route('/api/majors', methods=['GET'])
@permission_required(['admin', 'teacher'])
def get_majors():
    major_name = request.args.get('major_name', '')
    dept_id = request.args.get('dept_id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 使用视图v_majors
        sql = "SELECT * FROM v_majors WHERE 1=1"
        params = []
        if major_name:
            sql += " AND major_name LIKE %s"
            params.append(f"%{major_name}%")
        if dept_id:
            sql += " AND dept_id = %s"
            params.append(dept_id)
        cursor.execute(sql, params)
        majors = cursor.fetchall()
        return jsonify({'success': True, 'data': majors})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 删除专业
@app.route('/api/majors/<major_id>', methods=['DELETE'])
@permission_required(['admin'])
def delete_major(major_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT major_id FROM majors WHERE major_id = %s", (major_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '专业不存在'})
        
        cursor.execute("DELETE FROM majors WHERE major_id = %s", (major_id,))
        conn.commit()
        return jsonify({'success': True, 'message': '专业删除成功（关联班级已自动清理）！'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# ===================== 3. 班级管理模块 =====================
# 班级管理页面
@app.route('/manage_classes')
@permission_required(['admin'])
def manage_class_page():
    return render_template('manage_class.html')

# 添加班级
@app.route('/api/classes', methods=['POST'])
@permission_required(['admin'])
def add_class():
    data = request.get_json()
    class_name = data.get('class_name')
    major_id = data.get('major_id')
    grade = data.get('grade')

    if not all([class_name, major_id, grade]):
        return jsonify({'success': False, 'message': '班级名称、所属专业、年级为必填项'})

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO classes (class_name, major_id, grade) VALUES (%s, %s, %s);", 
                      (class_name, major_id, grade))
        conn.commit()
        return jsonify({'success': True, 'message': '班级添加成功！'})
    except pymysql.IntegrityError:
        conn.rollback()
        return jsonify({'success': False, 'message': '该年级的该班级名称已存在'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 查询班级（使用视图v_classes）
@app.route('/api/classes', methods=['GET'])
@permission_required(['admin', 'teacher'])
def get_classes():
    class_name = request.args.get('class_name', '')
    major_id = request.args.get('major_id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 使用视图v_classes
        sql = "SELECT * FROM v_classes WHERE 1=1"
        params = []
        if class_name:
            sql += " AND class_name LIKE %s"
            params.append(f"%{class_name}%")
        if major_id:
            sql += " AND major_id = %s"
            params.append(major_id)
        cursor.execute(sql, params)
        classes = cursor.fetchall()
        return jsonify({'success': True, 'data': classes})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 删除班级
@app.route('/api/classes/<class_id>', methods=['DELETE'])
@permission_required(['admin'])
def delete_class(class_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT class_id FROM classes WHERE class_id = %s", (class_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '班级不存在'})
        
        cursor.execute("DELETE FROM classes WHERE class_id = %s", (class_id,))
        conn.commit()
        return jsonify({'success': True, 'message': '班级删除成功（关联学生已自动清理）！'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# ===================== 4. 学生管理模块 =====================
# 学生管理页面
@app.route('/manage_students')
@permission_required(['admin'])
def manage_student_page():
    return render_template('manage_student.html')

# 添加学生
@app.route('/api/students', methods=['POST'])
@permission_required(['admin'])
def add_student():
    data = request.get_json()
    student_id = data.get('student_id')
    student_name = data.get('student_name')
    gender = data.get('gender')
    class_id = data.get('class_id')
    birth_date = data.get('birth_date')
    phone = data.get('phone')
    email = data.get('email')

    if not all([student_id, student_name, gender, class_id]):
        return jsonify({'success': False, 'message': '学号、姓名、性别、班级ID为必填项'})

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 添加学生信息
        cursor.execute("""
            INSERT INTO students (student_id, student_name, gender, birth_date, class_id, phone, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (student_id, student_name, gender, birth_date, class_id, phone, email))
        # 添加用户账号（默认密码123456）
        cursor.execute("""
            INSERT IGNORE INTO users (username, password, role, related_id)
            VALUES (%s, 'e10adc3949ba59abbe56e057f20f883e', 'student', %s);
        """, (student_id, student_id))
        conn.commit()
        return jsonify({'success': True, 'message': '学生添加成功！'})
    except pymysql.IntegrityError:
        conn.rollback()
        return jsonify({'success': False, 'message': '学号已存在'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 查询学生（使用视图v_students）
@app.route('/api/students', methods=['GET'])
@permission_required(['admin', 'teacher'])
def get_students():
    student_id = request.args.get('student_id', '')
    student_name = request.args.get('student_name', '')
    class_id = request.args.get('class_id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 使用视图v_students
        sql = "SELECT * FROM v_students WHERE 1=1"
        params = []
        if student_id:
            sql += " AND student_id LIKE %s"
            params.append(f"%{student_id}%")
        if student_name:
            sql += " AND student_name LIKE %s"
            params.append(f"%{student_name}%")
        if class_id:
            sql += " AND class_id = %s"
            params.append(class_id)
        cursor.execute(sql, params)
        students = cursor.fetchall()
        return jsonify({'success': True, 'data': students})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 删除学生
@app.route('/api/students/<student_id>', methods=['DELETE'])
@permission_required(['admin'])
def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (student_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '学生不存在'})
        
        cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        conn.commit()
        return jsonify({'success': True, 'message': '学生删除成功（关联用户/成绩已自动清理）！'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# ===================== 5. 教师管理模块 =====================
# 教师管理页面
@app.route('/manage_teachers')
@permission_required(['admin'])
def manage_teacher_page():
    return render_template('manage_teacher.html')

# 添加教师
@app.route('/api/teachers', methods=['POST'])
@permission_required(['admin'])
def add_teacher():
    data = request.get_json()
    teacher_id = data.get('teacher_id')
    teacher_name = data.get('teacher_name')
    gender = data.get('gender')
    dept_id = data.get('dept_id')
    title = data.get('title')
    phone = data.get('phone')
    email = data.get('email')

    if not all([teacher_id, teacher_name, gender, dept_id]):
        return jsonify({'success': False, 'message': '教师工号、姓名、性别、所属院系为必填项'})

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 添加教师信息
        cursor.execute("""
            INSERT INTO teachers (teacher_id, teacher_name, gender, dept_id, title, phone, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (teacher_id, teacher_name, gender, dept_id, title, phone, email))
        # 添加用户账号（默认密码123456）
        cursor.execute("""
            INSERT IGNORE INTO users (username, password, role, related_id)
            VALUES (%s, 'e10adc3949ba59abbe56e057f20f883e', 'teacher', %s);
        """, (teacher_id, teacher_id))
        conn.commit()
        return jsonify({'success': True, 'message': '教师添加成功！'})
    except pymysql.IntegrityError:
        conn.rollback()
        return jsonify({'success': False, 'message': '教师工号已存在'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 查询教师（使用视图v_teachers）
@app.route('/api/teachers', methods=['GET'])
@permission_required(['admin', 'teacher'])
def get_teachers():
    teacher_id = request.args.get('teacher_id', '')
    teacher_name = request.args.get('teacher_name', '')
    dept_id = request.args.get('dept_id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 使用视图v_teachers
        sql = "SELECT * FROM v_teachers WHERE 1=1"
        params = []
        if teacher_id:
            sql += " AND teacher_id LIKE %s"
            params.append(f"%{teacher_id}%")
        if teacher_name:
            sql += " AND teacher_name LIKE %s"
            params.append(f"%{teacher_name}%")
        if dept_id:
            sql += " AND dept_id = %s"
            params.append(dept_id)
        cursor.execute(sql, params)
        teachers = cursor.fetchall()
        return jsonify({'success': True, 'data': teachers})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 删除教师
@app.route('/api/teachers/<teacher_id>', methods=['DELETE'])
@permission_required(['admin'])
def delete_teacher(teacher_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT teacher_id FROM teachers WHERE teacher_id = %s", (teacher_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '教师不存在'})
        
        cursor.execute("DELETE FROM teachers WHERE teacher_id = %s", (teacher_id,))
        conn.commit()
        return jsonify({'success': True, 'message': '教师删除成功（关联排课/用户已自动清理）！'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# ===================== 6. 课程管理模块 =====================
# 课程管理页面
@app.route('/manage_courses')
@permission_required(['admin'])
def manage_course_page():
    return render_template('manage_course.html')

# 添加课程
@app.route('/api/courses', methods=['POST'])
@permission_required(['admin'])
def add_course():
    data = request.get_json()
    course_id = data.get('course_id')
    course_name = data.get('course_name')
    credit = data.get('credit')
    hours = data.get('hours')
    type = data.get('type')

    if not all([course_id, course_name, credit, hours, type]):
        return jsonify({'success': False, 'message': '课程编号、名称、学分、课时、类型为必填项'})

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO courses (course_id, course_name, credit, hours, type)
            VALUES (%s, %s, %s, %s, %s);
        """, (course_id, course_name, credit, hours, type))
        conn.commit()
        return jsonify({'success': True, 'message': '课程添加成功！'})
    except pymysql.IntegrityError:
        conn.rollback()
        return jsonify({'success': False, 'message': '课程编号已存在'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 查询课程（支持筛选）
@app.route('/api/courses', methods=['GET'])
@permission_required(['admin', 'teacher', 'student'])
def get_courses():
    course_name = request.args.get('course_name', '')
    type = request.args.get('type', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "SELECT * FROM courses WHERE 1=1"
        params = []
        if course_name:
            sql += " AND course_name LIKE %s"
            params.append(f"%{course_name}%")
        if type:
            sql += " AND type = %s"
            params.append(type)
        cursor.execute(sql, params)
        courses = cursor.fetchall()
        return jsonify({'success': True, 'data': courses})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 删除课程
@app.route('/api/courses/<course_id>', methods=['DELETE'])
@permission_required(['admin'])
def delete_course(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT course_id FROM courses WHERE course_id = %s", (course_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '课程不存在'})
        
        cursor.execute("DELETE FROM courses WHERE course_id = %s", (course_id,))
        conn.commit()
        return jsonify({'success': True, 'message': '课程删除成功！'})
    except pymysql.MySQLError as e:
        conn.rollback()
        if '该课程已有成绩记录，禁止删除' in str(e):
            return jsonify({'success': False, 'message': '该课程已有成绩记录，禁止删除！'})
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# ===================== 7. 课程安排管理模块 =====================
# 课程安排管理页面
@app.route('/manage_course_arrangements')
@permission_required(['admin', 'teacher', 'student'])  # 新增允许student访问
def manage_course_arrangements_page():
    # 新增：获取学生班级ID、真实姓名等变量（给前端模板用）
    student_class_id = None
    real_name = ''
    role_cn = ''
    
    current_role = session.get('role')
    current_username = session.get('username')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if current_role == 'admin':
            role_cn = '管理员'
            real_name = '系统管理员'
        elif current_role == 'teacher':
            role_cn = '教师'
            cursor.execute("SELECT teacher_name FROM v_teachers WHERE teacher_id = %s", (current_username,))
            teacher_data = cursor.fetchone()
            real_name = teacher_data['teacher_name'] if teacher_data else current_username
        elif current_role == 'student':
            role_cn = '学生'
            cursor.execute("SELECT student_name, class_id FROM v_students WHERE student_id = %s", (current_username,))
            student_data = cursor.fetchone()
            real_name = student_data['student_name'] if student_data else current_username
            student_class_id = student_data['class_id'] if student_data else None
    finally:
        cursor.close()
        conn.close()
    
    # 新增：把student_class_id/real_name/role_cn传给前端
    return render_template(
        'manage_course_arrangements.html',
        username=current_username,
        role=current_role,
        role_cn=role_cn,
        real_name=real_name,
        student_class_id=student_class_id
    )

# 添加课程安排（修正为day/period字段）
@app.route('/api/course_arrangements', methods=['POST'])
@permission_required(['admin'])
def add_course_arrangement():
    data = request.get_json()
    course_id = data.get('course_id')
    teacher_id = data.get('teacher_id')
    class_id = data.get('class_id')
    semester = data.get('semester')
    week = data.get('week')
    day = data.get('day')  # 替换原weekday
    period = data.get('period')  # 替换原section
    classroom = data.get('classroom')

    if not all([course_id, teacher_id, class_id, semester, week, day, period]):
        return jsonify({'success': False, 'message': '课程、教师、班级、学期、周次、星期、节次为必填项'})

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 校验教师时间冲突
        cursor.execute("""
            SELECT * FROM course_arrangements 
            WHERE teacher_id = %s AND semester = %s AND week = %s AND day = %s AND period = %s
        """, (teacher_id, semester, week, day, period))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '该教师同一时间已有排课，避免冲突！'})
        
        # 校验班级时间冲突
        cursor.execute("""
            SELECT * FROM course_arrangements 
            WHERE class_id = %s AND semester = %s AND week = %s AND day = %s AND period = %s
        """, (class_id, semester, week, day, period))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '该班级同一时间已有排课，避免冲突！'})
        
        # 插入排课数据（使用day/period字段）
        cursor.execute("""
            INSERT INTO course_arrangements (course_id, teacher_id, class_id, semester, week, day, period, classroom)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (course_id, teacher_id, class_id, semester, week, day, period, classroom))
        conn.commit()
        return jsonify({'success': True, 'message': '课程安排添加成功！'})
    except pymysql.IntegrityError:
        conn.rollback()
        return jsonify({'success': False, 'message': '排课信息重复或关联数据不存在'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 查询课程安排（使用视图v_course_arrangements，按角色权限过滤）
@app.route('/api/course_arrangements', methods=['GET'])
@permission_required(['admin', 'teacher', 'student'])
def get_course_arrangements():
    course_id = request.args.get('course_id', '')
    semester = request.args.get('semester', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 使用视图v_course_arrangements
        sql = "SELECT * FROM v_course_arrangements WHERE 1=1"
        params = []
        
        # 角色权限过滤
        current_role = session.get('role')
        if current_role == 'teacher':
            sql += " AND teacher_id = %s"
            params.append(session['username'])
        elif current_role == 'student':
            # 学生关联自己的班级
            cursor.execute("SELECT class_id FROM v_students WHERE student_id = %s", (session['username'],))
            student_class = cursor.fetchone()
            if not student_class:
                return jsonify({'success': False, 'message': '未查询到你的班级信息'})
            sql += " AND class_id = %s"
            params.append(student_class['class_id'])
        
        # 通用筛选条件
        if course_id:
            sql += " AND course_id LIKE %s"
            params.append(f"%{course_id}%")
        if semester:
            sql += " AND semester LIKE %s"
            params.append(f"%{semester}%")
        
        cursor.execute(sql, params)
        course_arrangements = cursor.fetchall()
        return jsonify({'success': True, 'data': course_arrangements})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 删除课程安排
@app.route('/api/course_arrangements/<arrangement_id>', methods=['DELETE'])
@permission_required(['admin'])
def delete_course_arrangement(arrangement_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT arrangement_id FROM course_arrangements WHERE arrangement_id = %s", (arrangement_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '课程安排不存在'})
        
        cursor.execute("DELETE FROM course_arrangements WHERE arrangement_id = %s", (arrangement_id,))
        conn.commit()
        return jsonify({'success': True, 'message': '课程安排删除成功！'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})
    finally:
        cursor.close()
        conn.close()

# -------------------------- 启动服务 --------------------------
if __name__ == '__main__':
    print("🚀 教学管理系统启动中...")
    print("🔗 访问地址：http://127.0.0.1:5000")

    app.run(debug=True, host='127.0.0.1', port=5000)
