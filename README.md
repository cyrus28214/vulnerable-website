# vulnerable

包含很多漏洞的网站，用于测试和学习。

搜索`VULN`可以找到大部分漏洞（但不是全部）。

灵感来源：[https://github.com/OWASP/Vulnerable-Web-Application](https://github.com/OWASP/Vulnerable-Web-Application)

## 漏洞列表

- SQL注入
- XSS
- CSRF
- 文件覆盖漏洞
- 路径穿越漏洞
- 任意文件写

## 运行

```bash
# 推荐使用虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行
python app.py
```

