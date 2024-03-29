from flask import Flask, render_template, redirect, request
import csv
import datetime
#import bz

app = Flask(__name__, static_folder='assets')

start_stop = "Start"
number_of_sessions = 0
working_time = 0
resting_time = 0
start = False
state = 'none'
#today_working_time = 0
#today_resting_time = 0

def today_total():
    today_resting_time = 0
    today_working_time = 0
    with open('data.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if str(datetime.date.today()) == row[0]:
                if row[2] == 'working':
                    today_working_time += int(row[1])
                elif row[2] == 'resting':
                    today_resting_time += int(row[2])
    return today_working_time, today_resting_time

def read_week_data():
    week = []
    week_y_values = [0]*7

    #finds the dates of the last 7 days
    for day in range(6,0,-1):
        week.append(str(datetime.date.today() - datetime.timedelta(days = day)))
    week.append(str(datetime.date.today()))

    #finds the total working time per day for the last 7 days
    with open('data.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] in week:
                for day in week:
                    if row[0] == day:
                        index = week.index(day)
                        if row[2] == 'working':
                            week_y_values[index] += int(row[1])
    return week, week_y_values

def read_month_data():
    month = []
    month_y_values = [0]*30

    #finds the dates of the last 30 days
    for day in range(29,0,-1):
        month.append(str(datetime.date.today() - datetime.timedelta(days = day)))
    month.append(str(datetime.date.today()))

    #finds the total working time per day for the last 7 days
    with open('data.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] in month:
                for day in month:
                    if row[0] == day:
                        index = month.index(day)
                        if row[2] == 'working':
                            month_y_values[index] += int(row[1])
    return month, month_y_values

def compute_streak():
    streak = 0
    with open("data.csv", 'r') as file:
        last_line = file.readlines()[-1].strip().split(",")
        if last_line[0] == str(datetime.date.today()):
            streak = int(last_line[3])
        elif last_line[0] == str(datetime.date.today() - datetime.timedelta(1)):
            streak = int(last_line[3]) + 1
        else: 
            streak = 1
    return streak

def write_csv(time, type):
    streak = compute_streak()
    with open('data.csv', 'a', newline = '') as file:
        writer = csv.writer(file)
        date = str(datetime.date.today())
        writer.writerow([date, time, type, streak])

def award():
    gold = False
    silver = False
    bronze = False
    with open('data.csv', 'r') as file:
        reader = csv.reader(file)
        last_line = file.readlines()[-1].strip().split(",")
        streak = int(last_line[3])
    if streak >= 500:
        gold, silver, bronze = True
    elif streak >= 50:
        silver, bronze = True
    elif streak >= 5:
        bronze = True
    return gold, silver, bronze

@app.route('/')
def slash():
    return redirect('/home')

@app.route('/home')
def home():
    global start
    global working_time
    global resting_time
    global state
    global number_of_sessions
    milliseconds = 0
    milliseconds = int(working_time) * 60 * 1000
    if start == True:
        write_csv(working_time, 'working')
    return render_template('home.html', start_stop = start_stop, start = start, milliseconds = milliseconds)

@app.route('/history')
def history():
    today_working_total, today_resting_total = today_total()
    gold, silver, bronze = award()
    return render_template('history_daily.html', daily = True, chart = False, time_working = today_working_total, 
                           time_resting = today_resting_total, bronze = bronze, silver = silver, gold = gold)

@app.route('/today')
def today():
    return redirect('/history')

@app.route('/week')
def week():
    week, week_y_values = read_week_data()
    gold, silver, bronze = award()
    return render_template('history_daily.html', daily = False, chart = True, labels = week, values = week_y_values, 
                           bronze = bronze, silver = silver, gold = gold)

@app.route('/month')
def month():
    month, month_y_values = read_month_data()
    gold, silver, bronze = award()
    return render_template('history_daily.html', daily = False, chart = True, labels = month, values = month_y_values, 
                           bronze = bronze, silver = silver, gold = gold)

@app.route('/setting', methods = ['POST', 'GET'])
def setting():
    global number_of_sessions
    global working_time
    global resting_time
    if request.method == 'POST':
        number_of_sessions = int(request.form['number_of_sessions'])
        working_time = int(request.form['working_time'])
        resting_time = int(request.form['resting_time'])
        return redirect('/home')
    else:
        return render_template("setting.html")

@app.route('/start_stop_timer', methods = ['POST', 'GET'])
def start_stop_timer():
    global start_stop
    global start
    if request.method == 'GET':
        if start_stop == 'Start':
            start_stop = 'Stop'
            start = True
            return redirect('/home')
        elif start_stop == 'Stop':
            start_stop = 'Start'
            start = False
            return redirect('/home')
    else:
        return redirect('/home')

@app.route('/reset_timer', methods = ['POST', 'GET'])
def reset_timer():
    if request.method == 'GET':
        return redirect('/home')
    else:
        return redirect('/home')

@app.route('/unlock')
def unlock():
    #bz.unlock()
    return redirect('/start_stop_timer')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)