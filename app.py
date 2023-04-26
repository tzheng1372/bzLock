from flask import Flask, render_template, redirect, request
import csv
import datetime

app = Flask(__name__, static_folder='assets')

start_stop = "Start"
number_of_sessions = 0
working_time = 0
resting_time = 0
today_working_time = 0
today_resting_time = 0

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
    return redirect('/start_stop_timer')

def today_total():
    global today_resting_time
    global today_working_time
    with open('data.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if datetime.date.today() == datetime.datetime.strptime(row[0], '%Y-%m-%d').date():
                if row[2] == 'working':
                    today_working_time += int(row[1])
                elif row[2] == 'resting':
                    today_resting_time += int(row[2])

def read_week_data():
    week = []
    week_y_values = [0]*7

    #finds the dates of the last 7 days
    for day in range(6,0,-1):
        week.append(str(datetime.date.today() - datetime.timedelta(days = day)))
    week.append(str(datetime.today()))

    #finds the total working time per day for the last 7 days
    with open('data.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] in week:
                for day in week:
                    if row[0] == day:
                        index = week.index[day]
                        if row[2] == 'working':
                            week_y_values[index] += int(row[1])
    return week, week_y_values

def read_month_data():
    month = []
    month_y_values = [0]*30

    #finds the dates of the last 30 days
    for day in range(29,0,-1):
        month.append(str(datetime.date.today() - datetime.timedelta(days = day)))
    month.append(str(datetime.today()))

    #finds the total working time per day for the last 7 days
    with open('data.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] in month:
                for day in month:
                    if row[0] == day:
                        index = month.index[day]
                        if row[2] == 'working':
                            month_y_values[index] += int(row[1])
    return month, month_y_values

def writing_csv():
    with open('data.csv', 'w') as file:
        writer = csv.writer(file)
            

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)