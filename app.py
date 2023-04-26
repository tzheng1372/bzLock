from flask import Flask, render_template, redirect, request

app = Flask(__name__, static_folder='assets')

start_stop = "Start"
number_of_sessions = 0
working_time = 0
resting_time = 0

@app.route('/')
def slash():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('home.html', start_stop = start_stop, hour = 0, minute = working_time, seconds = 0)

@app.route('/history')
def history():
    return render_template('history_daily.html', daily = True, chart = False)

@app.route('/today')
def today():
    return redirect('/history')

@app.route('/week')
def week():
    return render_template('history_daily.html', daily = False, chart = True)

@app.route('/month')
def month():
    return render_template('history_daily.html', daily = False, chart = True)

@app.route('/setting', methods = ['POST', 'GET'])
def setting():
    global number_of_sessions
    global working_time
    global resting_time
    if request.method == 'POST':
        number_of_sessions = request.form['number_of_sessions']
        working_time = request.form['working_time']
        resting_time = request.form['resting_time']
        return redirect('/home')
    else:
        return render_template("setting.html")

@app.route('/start__stop_timer')
def start_stop_timer():
    global start_stop
    if start_stop == 'Start':
        start_stop = 'Stop'
        return render_template('home.html', start_stop = start_stop, hour = 0, minute = working_time, seconds = 0)
    elif start_stop == 'Stop':
        start_stop = 'Start'
        return render_template('home.html', start_stop = start_stop, hour = 0, minute = working_time, seconds = 0)

@app.route('/reset_timer')
def reset_timer():
    return redirect('/home')

@app.route('/unlock')
def unlock():
    #unlock box
    return

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)