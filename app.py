from flask import Flask, render_template, request, jsonify, redirect
import database
from util import generate_token, verify_token
import os

app = Flask(__name__)

# 初始化数据库
database.init_db()

@app.route('/')
def home():
    token = request.cookies.get('token')
    if not token:
        return render_template('index.html')
    
    payload = verify_token(token)
    username = payload['username']
    user_detail = database.get_user_detail(username)
    print(user_detail)
    discussions = database.get_discussions()
    return render_template('index.html', username=username, discussions=discussions, avatar=user_detail['avatar'])

@app.route('/user')
def user():
    token = request.cookies.get('token')
    if not token:
        return redirect('/')
    
    payload = verify_token(token)
    username = payload['username']
    user_detail = database.get_user_detail(username)
    return render_template('user.html', username=username, avatar=user_detail['avatar'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST':
        # VULN: 未对用户输入进行校验
        username = request.form.get('username')
        password = request.form.get('password')

        if database.check_user_exists(username):
            return jsonify({'success': False, 'message': '用户已存在'})
        
        if database.register_user(username, password):
            token = generate_token(username)
            response = jsonify({'success': True, 'message': '登录成功', 'token': token})
            response.set_cookie('token', token)
            return response
        else:
            return jsonify({'success': False, 'message': '注册失败'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if database.verify_login(username, password):
            token = generate_token(username)
            response = jsonify({'success': True, 'message': '登录成功', 'token': token})
            response.set_cookie('token', token)
            return response
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误'})

@app.route('/change-password', methods=['POST'])
def change_password():
    # VULN: CSRF漏洞 - 没有CSRF token保护
    token = request.cookies.get('token')
    if not token:
        return jsonify({'success': False, 'message': '请先登录'})
    
    payload = verify_token(token)
    username = payload['username']
    new_password = request.form.get('new_password')
    database.change_password(username, new_password)
    
    return jsonify({'success': True, 'message': '密码修改成功'})

@app.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'success': True, 'message': '退出成功'})
    response.delete_cookie('token')
    return response

@app.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    token = request.cookies.get('token')
    if not token:
        return jsonify({'success': False, 'message': '请先登录'})
    
    payload = verify_token(token)

    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': '没有上传文件'})
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'})

    # VULN: 没有限制文件后缀
    # VULN: 没有限制文件大小，攻击者可以上传大文件占用服务器资源
    # VULN: 没有对文件名进行sanitize，如果包含`/`、`\`、`..`等字符，可能导致文件路径穿越漏洞
    # VULN: 没有重命名文件，导致文件覆盖漏洞

    file_path = os.path.join('static/avatars', file.filename)
    file.save(file_path)

    database.update_user_avatar(payload['username'], file_path)
    return jsonify({'success': True, 'message': '上传成功'})
    
    
@app.route('/add-discussion', methods=['POST'])
def post_discussion():
    token = request.cookies.get('token')
    if not token:
        return jsonify({'success': False, 'message': '请先登录'})
    
    payload = verify_token(token)
    content = request.form.get('content')
    
    if not content:
        return jsonify({'success': False, 'message': '内容不能为空'})
    
    if database.add_discussion(payload['username'], content):
        return jsonify({'success': True, 'message': '发布成功'})
    return jsonify({'success': False, 'message': '发布失败'})

@app.route('/delete-discussion', methods=['POST'])
def delete_discussion():
    token = request.cookies.get('token')
    if not token:
        return jsonify({'success': False, 'message': '请先登录'})
    
    payload = verify_token(token)
    username = payload['username']
    data = request.get_json()
    discussion_id = data.get('id')
    
    if not discussion_id:
        return jsonify({'success': False, 'message': '参数错误'})
    
    if database.delete_discussion(username, discussion_id):
        return jsonify({'success': True, 'message': '删除成功'})
    return jsonify({'success': False, 'message': '删除失败'})

@app.route('/evil')
def evil():
    return render_template('evil.html')

if __name__ == '__main__':
    app.run(debug=True) # VULN: 在生产环境使用development server + debug模式运行