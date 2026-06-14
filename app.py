from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# -------------------------------
# DATABASE CONFIG
# -------------------------------
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tufailihsan20.'
app.config['MYSQL_DB'] = 'campus_collaboration_finder'

mysql = MySQL(app)

# -------------------------------
# HELPER FUNCTION
# -------------------------------
def query_db(query, args=(), fetch=True):
    cur = mysql.connection.cursor()
    cur.execute(query, args)
    if fetch:
        result = cur.fetchall()
        cur.close()
        return result
    else:
        mysql.connection.commit()
        cur.close()
        return True


# -------------------------------
# HOME
# -------------------------------
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Campus Collaboration Finder API is running"})


# -------------------------------
# AUTH APIs
# -------------------------------

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name       = data['name']
    email      = data['email']
    password   = generate_password_hash(data['password'])
    department = data['department']
    semester   = data['semester']
    try:
        query_db("""
            INSERT INTO Students (name, email, password, department, semester)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, password, department, semester), fetch=False)
        return jsonify({"message": "User created"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/login', methods=['POST'])
def login():
    data     = request.json
    email    = data['email']
    password = data['password']
    user     = query_db("SELECT * FROM Students WHERE email=%s", (email,))
    if user and check_password_hash(user[0][5], password):
        return jsonify({"message": "Login success", "student_id": user[0][0]})
    return jsonify({"error": "Invalid credentials"})


# -------------------------------
# STUDENTS APIs
# -------------------------------

@app.route('/students', methods=['GET'])
def get_students():
    rows = query_db("""
        SELECT student_id, name, email, department, semester, created_at
        FROM Students
        ORDER BY student_id
    """)
    return jsonify([
        {"student_id": r[0], "name": r[1], "email": r[2],
         "department": r[3], "semester": r[4],
         "created_at": r[5].isoformat() if r[5] else None}
        for r in rows
    ])

# ── SEARCH students by name / email / department ──────────────────────────────
@app.route('/students/search', methods=['GET'])
def search_students():
    q = request.args.get('q', '').strip()
    like = f"%{q}%"
    rows = query_db("""
        SELECT student_id, name, email, department, semester, created_at
        FROM Students
        WHERE name LIKE %s OR email LIKE %s OR department LIKE %s
        ORDER BY student_id
    """, (like, like, like))
    return jsonify([
        {"student_id": r[0], "name": r[1], "email": r[2],
         "department": r[3], "semester": r[4],
         "created_at": r[5].isoformat() if r[5] else None}
        for r in rows
    ])

@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    rows = query_db("""
        SELECT student_id, name, email, department, semester, created_at
        FROM Students WHERE student_id=%s
    """, (id,))
    if not rows:
        return jsonify({"error": "Student not found"}), 404
    r = rows[0]
    return jsonify({"student_id": r[0], "name": r[1], "email": r[2],
                    "department": r[3], "semester": r[4],
                    "created_at": r[5].isoformat() if r[5] else None})

@app.route('/students', methods=['POST'])
def create_student():
    data = request.json
    try:
        pw = generate_password_hash(data['password'])
        query_db("""
            INSERT INTO Students (name, email, password, department, semester)
            VALUES (%s,%s,%s,%s,%s)
        """, (data['name'], data['email'], pw, data['department'], data['semester']), False)
        return jsonify({"message": "Student created"})
    except Exception as e:
        return jsonify({"error": str(e)})

# ── UPDATE student ────────────────────────────────────────────────────────────
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.json
    try:
        query_db("""
            UPDATE Students
            SET name=%s, email=%s, department=%s, semester=%s
            WHERE student_id=%s
        """, (data['name'], data['email'], data['department'], data['semester'], id), fetch=False)
        return jsonify({"message": "Student updated"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    try:
        query_db("DELETE FROM Students WHERE student_id=%s", (id,), fetch=False)
        return jsonify({"message": "Student deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})


# -------------------------------
# SKILLS APIs
# -------------------------------

@app.route('/skills', methods=['GET'])
def get_skills():
    rows = query_db("SELECT skill_id, skill_name FROM Skills ORDER BY skill_id")
    return jsonify([{"skill_id": r[0], "skill_name": r[1]} for r in rows])

# ── SEARCH skills ─────────────────────────────────────────────────────────────
@app.route('/skills/search', methods=['GET'])
def search_skills():
    q    = request.args.get('q', '').strip()
    like = f"%{q}%"
    rows = query_db("SELECT skill_id, skill_name FROM Skills WHERE skill_name LIKE %s ORDER BY skill_id", (like,))
    return jsonify([{"skill_id": r[0], "skill_name": r[1]} for r in rows])

@app.route('/skills', methods=['POST'])
def add_skill():
    data = request.json
    try:
        query_db("INSERT INTO Skills (skill_name) VALUES (%s)", (data['skill_name'],), False)
        return jsonify({"message": "Skill added"})
    except Exception as e:
        return jsonify({"error": str(e)})

# ── UPDATE skill ──────────────────────────────────────────────────────────────
@app.route('/skills/<int:id>', methods=['PUT'])
def update_skill(id):
    data = request.json
    try:
        query_db("UPDATE Skills SET skill_name=%s WHERE skill_id=%s",
                 (data['skill_name'], id), fetch=False)
        return jsonify({"message": "Skill updated"})
    except Exception as e:
        return jsonify({"error": str(e)})

# ── DELETE skill ──────────────────────────────────────────────────────────────
@app.route('/skills/<int:id>', methods=['DELETE'])
def delete_skill(id):
    try:
        query_db("DELETE FROM Skills WHERE skill_id=%s", (id,), fetch=False)
        return jsonify({"message": "Skill deleted"})
    except Exception as e:
        return jsonify({"error": str(e)})


# -------------------------------
# STUDENT_SKILLS APIs
# -------------------------------

@app.route('/student_skills', methods=['GET'])
def get_student_skills():
    rows = query_db("""
        SELECT ss.student_id, s.name AS student_name,
               ss.skill_id,   sk.skill_name
        FROM Student_Skills ss
        JOIN Students s  ON ss.student_id = s.student_id
        JOIN Skills   sk ON ss.skill_id   = sk.skill_id
        ORDER BY ss.student_id, sk.skill_name
    """)
    return jsonify([
        {"student_id": r[0], "student_name": r[1],
         "skill_id":   r[2], "skill_name":   r[3]}
        for r in rows
    ])

# ── SEARCH student_skills ─────────────────────────────────────────────────────
@app.route('/student_skills/search', methods=['GET'])
def search_student_skills():
    sid  = request.args.get('student_id', '').strip()
    skid = request.args.get('skill_id',   '').strip()
    sql  = """
        SELECT ss.student_id, s.name AS student_name,
               ss.skill_id,   sk.skill_name
        FROM Student_Skills ss
        JOIN Students s  ON ss.student_id = s.student_id
        JOIN Skills   sk ON ss.skill_id   = sk.skill_id
        WHERE 1=1
    """
    params = []
    if sid:
        sql += " AND ss.student_id=%s"; params.append(int(sid))
    if skid:
        sql += " AND ss.skill_id=%s";   params.append(int(skid))
    sql += " ORDER BY ss.student_id, sk.skill_name"
    rows = query_db(sql, params)
    return jsonify([
        {"student_id": r[0], "student_name": r[1],
         "skill_id":   r[2], "skill_name":   r[3]}
        for r in rows
    ])

@app.route('/student_skills', methods=['POST'])
def add_student_skill():
    data = request.json
    try:
        query_db("INSERT INTO Student_Skills (student_id, skill_id) VALUES (%s,%s)",
                 (data['student_id'], data['skill_id']), False)
        return jsonify({"message": "Skill assigned to student"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/student_skills', methods=['DELETE'])
def remove_student_skill():
    data = request.json
    try:
        query_db("DELETE FROM Student_Skills WHERE student_id=%s AND skill_id=%s",
                 (data['student_id'], data['skill_id']), fetch=False)
        return jsonify({"message": "Skill removed from student"})
    except Exception as e:
        return jsonify({"error": str(e)})


# -------------------------------
# PROJECT APIs
# -------------------------------

@app.route('/projects', methods=['GET'])
def get_projects():
    rows = query_db("""
        SELECT p.project_id, p.project_name, p.description, p.date_posted,
               p.owner_id,   s.name AS owner_name
        FROM Projects p
        JOIN Students s ON p.owner_id = s.student_id
        ORDER BY p.project_id
    """)
    return jsonify([
        {"project_id": r[0], "project_name": r[1], "description": r[2],
         "date_posted": str(r[3]) if r[3] else None,
         "owner_id":    r[4], "owner_name": r[5]}
        for r in rows
    ])

# ── SEARCH projects ───────────────────────────────────────────────────────────
@app.route('/projects/search', methods=['GET'])
def search_projects():
    q    = request.args.get('q', '').strip()
    like = f"%{q}%"
    rows = query_db("""
        SELECT p.project_id, p.project_name, p.description, p.date_posted,
               p.owner_id,   s.name AS owner_name
        FROM Projects p
        JOIN Students s ON p.owner_id = s.student_id
        WHERE p.project_name LIKE %s OR p.description LIKE %s OR s.name LIKE %s
        ORDER BY p.project_id
    """, (like, like, like))
    return jsonify([
        {"project_id": r[0], "project_name": r[1], "description": r[2],
         "date_posted": str(r[3]) if r[3] else None,
         "owner_id":    r[4], "owner_name": r[5]}
        for r in rows
    ])

@app.route('/projects/<int:id>', methods=['GET'])
def get_project(id):
    rows = query_db("""
        SELECT p.project_id, p.project_name, p.description, p.date_posted,
               p.owner_id,   s.name
        FROM Projects p
        JOIN Students s ON p.owner_id = s.student_id
        WHERE p.project_id=%s
    """, (id,))
    if not rows:
        return jsonify({"error": "Project not found"}), 404
    r = rows[0]
    return jsonify({"project_id": r[0], "project_name": r[1], "description": r[2],
                    "date_posted": str(r[3]) if r[3] else None,
                    "owner_id": r[4], "owner_name": r[5]})

@app.route('/projects', methods=['POST'])
def create_project():
    data = request.json
    try:
        query_db("""
            INSERT INTO Projects (owner_id, project_name, description)
            VALUES (%s,%s,%s)
        """, (data['owner_id'], data['project_name'], data.get('description', '')), False)
        return jsonify({"message": "Project created"})
    except Exception as e:
        return jsonify({"error": str(e)})

# ── UPDATE project ────────────────────────────────────────────────────────────
@app.route('/projects/<int:id>', methods=['PUT'])
def update_project(id):
    data = request.json
    try:
        query_db("""
            UPDATE Projects SET project_name=%s, description=%s
            WHERE project_id=%s
        """, (data['project_name'], data.get('description', ''), id), fetch=False)
        return jsonify({"message": "Project updated"})
    except Exception as e:
        return jsonify({"error": str(e)})

# ── DELETE project ────────────────────────────────────────────────────────────
@app.route('/projects/<int:id>', methods=['DELETE'])
def delete_project(id):
    try:
        query_db("DELETE FROM Projects WHERE project_id=%s", (id,), fetch=False)
        return jsonify({"message": "Project deleted"})
    except Exception as e:
        return jsonify({"error": str(e)})


# -------------------------------
# PROJECT_SKILLS APIs
# -------------------------------

@app.route('/project_skills', methods=['GET'])
def get_project_skills():
    rows = query_db("""
        SELECT ps.project_id, p.project_name,
               ps.skill_id,   sk.skill_name
        FROM Project_Skills ps
        JOIN Projects p  ON ps.project_id = p.project_id
        JOIN Skills   sk ON ps.skill_id   = sk.skill_id
        ORDER BY ps.project_id, sk.skill_name
    """)
    return jsonify([
        {"project_id": r[0], "project_name": r[1],
         "skill_id":   r[2], "skill_name":   r[3]}
        for r in rows
    ])

# ── SEARCH project_skills ─────────────────────────────────────────────────────
@app.route('/project_skills/search', methods=['GET'])
def search_project_skills():
    pid  = request.args.get('project_id', '').strip()
    skid = request.args.get('skill_id',   '').strip()
    sql  = """
        SELECT ps.project_id, p.project_name,
               ps.skill_id,   sk.skill_name
        FROM Project_Skills ps
        JOIN Projects p  ON ps.project_id = p.project_id
        JOIN Skills   sk ON ps.skill_id   = sk.skill_id
        WHERE 1=1
    """
    params = []
    if pid:
        sql += " AND ps.project_id=%s"; params.append(int(pid))
    if skid:
        sql += " AND ps.skill_id=%s";   params.append(int(skid))
    sql += " ORDER BY ps.project_id, sk.skill_name"
    rows = query_db(sql, params)
    return jsonify([
        {"project_id": r[0], "project_name": r[1],
         "skill_id":   r[2], "skill_name":   r[3]}
        for r in rows
    ])

@app.route('/project_skills', methods=['POST'])
def add_project_skill():
    data = request.json
    try:
        query_db("INSERT INTO Project_Skills (project_id, skill_id) VALUES (%s,%s)",
                 (data['project_id'], data['skill_id']), False)
        return jsonify({"message": "Skill added to project"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/project_skills', methods=['DELETE'])
def remove_project_skill():
    data = request.json
    try:
        query_db("DELETE FROM Project_Skills WHERE project_id=%s AND skill_id=%s",
                 (data['project_id'], data['skill_id']), fetch=False)
        return jsonify({"message": "Skill removed from project"})
    except Exception as e:
        return jsonify({"error": str(e)})


# -------------------------------
# APPLICATION APIs
# -------------------------------

@app.route('/applications', methods=['GET'])
def get_applications():
    rows = query_db("""
        SELECT a.application_id, a.student_id, s.name AS student_name,
               a.project_id,     p.project_name,
               a.status, a.date_applied
        FROM Applications a
        JOIN Students s ON a.student_id = s.student_id
        JOIN Projects p ON a.project_id = p.project_id
        ORDER BY a.application_id
    """)
    return jsonify([
        {"application_id": r[0], "student_id": r[1], "student_name": r[2],
         "project_id": r[3], "project_name": r[4],
         "status": r[5], "date_applied": str(r[6]) if r[6] else None}
        for r in rows
    ])

# ── SEARCH applications ───────────────────────────────────────────────────────
@app.route('/applications/search', methods=['GET'])
def search_applications():
    sid    = request.args.get('student_id', '').strip()
    pid    = request.args.get('project_id', '').strip()
    status = request.args.get('status',     '').strip()
    sql    = """
        SELECT a.application_id, a.student_id, s.name,
               a.project_id,     p.project_name,
               a.status, a.date_applied
        FROM Applications a
        JOIN Students s ON a.student_id = s.student_id
        JOIN Projects p ON a.project_id = p.project_id
        WHERE 1=1
    """
    params = []
    if sid:
        sql += " AND a.student_id=%s"; params.append(int(sid))
    if pid:
        sql += " AND a.project_id=%s"; params.append(int(pid))
    if status:
        sql += " AND a.status=%s";     params.append(status)
    sql += " ORDER BY a.application_id"
    rows = query_db(sql, params)
    return jsonify([
        {"application_id": r[0], "student_id": r[1], "student_name": r[2],
         "project_id": r[3], "project_name": r[4],
         "status": r[5], "date_applied": str(r[6]) if r[6] else None}
        for r in rows
    ])

@app.route('/applications', methods=['POST'])
def apply():
    data = request.json
    try:
        query_db("""
            INSERT INTO Applications (project_id, student_id)
            VALUES (%s,%s)
        """, (data['project_id'], data['student_id']), False)
        return jsonify({"message": "Applied successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})

# ── UPDATE application status ─────────────────────────────────────────────────
@app.route('/applications/<int:id>', methods=['PUT'])
def update_application(id):
    data = request.json
    try:
        query_db("UPDATE Applications SET status=%s WHERE application_id=%s",
                 (data['status'], id), fetch=False)
        return jsonify({"message": "Status updated"})
    except Exception as e:
        return jsonify({"error": str(e)})

# ── DELETE application ────────────────────────────────────────────────────────
@app.route('/applications/<int:id>', methods=['DELETE'])
def delete_application(id):
    try:
        query_db("DELETE FROM Applications WHERE application_id=%s", (id,), fetch=False)
        return jsonify({"message": "Application withdrawn"})
    except Exception as e:
        return jsonify({"error": str(e)})


# -------------------------------
# AI MATCHING (RECOMMENDATION)
# -------------------------------

@app.route('/recommend/<int:student_id>', methods=['GET'])
def recommend(student_id):
    student_skills = query_db("""
        SELECT skill_id FROM Student_Skills WHERE student_id=%s
    """, (student_id,))
    student_skill_ids = {s[0] for s in student_skills}

    projects = query_db("""
        SELECT p.project_id, p.project_name
        FROM Projects p
        WHERE p.owner_id != %s
    """, (student_id,))

    result = []
    for p in projects:
        project_id, project_name = p[0], p[1]
        project_skills = query_db("""
            SELECT skill_id FROM Project_Skills WHERE project_id=%s
        """, (project_id,))
        project_skill_ids = {ps[0] for ps in project_skills}

        matched = len(student_skill_ids & project_skill_ids)
        total   = len(project_skill_ids)
        score   = round((matched / total) * 100, 2) if total > 0 else 0

        result.append({
            "project_id":       project_id,
            "project_name":     project_name,
            "match_percentage": score,
            "matched_skills":   matched,
            "required_skills":  total
        })

    return jsonify(sorted(result, key=lambda x: x['match_percentage'], reverse=True))


# -------------------------------
# RUN SERVER
# -------------------------------

if __name__ == '__main__':
    app.run(debug=True)
