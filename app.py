import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 설정
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
DATA_FILE    = os.path.join(app.root_path, 'posts.json')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 디렉터리/파일 준비
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        posts_list = json.load(f)
    # 기존 글에도 id 부여 (순서대로)
    for idx, post in enumerate(posts_list, start=1):
        post['id'] = idx
else:
    posts_list = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template('main.html')

@app.route("/report", methods=['GET','POST'])
def report():
    if request.method == 'POST':
        title   = request.form.get('title','').strip()
        content = request.form.get('content','').strip()

        # 이미지 저장
        image_filename = None
        file = request.files.get('image')
        if file and file.filename and allowed_file(file.filename):
            fn_base, fn_ext = os.path.splitext(secure_filename(file.filename))
            # next_id 계산
            next_id = posts_list[-1]['id'] + 1 if posts_list else 1
            image_filename = f"{fn_base}_{next_id}{fn_ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        if title and content:
            # next_id 계산
            next_id = posts_list[-1]['id'] + 1 if posts_list else 1

            post = {
                'id':      next_id,
                'title':   title,
                'content': content,
                'image':   image_filename,
                'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            posts_list.append(post)
            # JSON에 덮어쓰기
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(posts_list, f, ensure_ascii=False, indent=2)

        return redirect(url_for('show_posts'))

    return render_template('report.html')

@app.route("/posts")
def show_posts():
    # id 내림차순(최신 위) 정렬
    ordered = sorted(posts_list, key=lambda p: p['id'], reverse=True)
    return render_template('posts.html', posts=ordered)

@app.route("/posts/<int:post_id>")
def post_detail(post_id):
    # id로 글 찾기
    post = next((p for p in posts_list if p['id']==post_id), None)
    if not post:
        return "존재하지 않는 글입니다.", 404
    return render_template('post_detail.html', post=post)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
