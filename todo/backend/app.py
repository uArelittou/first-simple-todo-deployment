

from flask import Flask, jsonify
import pymysql

app = Flask(__name__)

# 1. 配置数据库连接信息
db_config = {
    'host': '127.0.0.1',
    'user': 'qqq',
    'password': 'qqq',  # 刚才 SQL 语句里设的密码
    'database': 'todo',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

@app.route('/api/tasks')
def get_tasks():
    try:
        # 2. 建立连接
        conn = pymysql.connect(**db_config)
        
        with conn.cursor() as cursor:
            # 3. 执行 SQL 查询
            cursor.execute("SELECT * FROM tasks")
            # 4. 获取所有结果
            result = cursor.fetchall()
        
        # 5. 关闭连接
        conn.close()
        
        # 6. 返回 JSON 数据
        return jsonify({
            "status": "success",
            "data": result
        })
        
    except Exception as e:
        # 如果连不上，把错误打印出来方便调试
        print(f"数据库连接失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run()
