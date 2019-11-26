import psycopg2
from flask import Flask, render_template
from flask import jsonify
import json
app = Flask(__name__)




#{% block content %}{% endblock %}


##@app.route('/')
##def index():
##    return render_template('pie.html')

@app.route('/')
def get_piechart_data():
    try:
        conn=psycopg2.connect("dbname=dbtoy user='postgres' host='localhost' password='test'")
    except:
        print("I am unable to connect to the database.")

    if (conn):
        cursor = conn.cursor()
        # load everything on RAM
        cursor.execute('SELECT COUNT(*) FROM label WHERE sample_type_binary=0')

        data0 = cursor.fetchone()
        cursor.execute('SELECT COUNT(*) FROM label WHERE sample_type_binary=1')
        data1 = cursor.fetchone()
  
        
        data_refa = [{"label": "binary_0", "value": data0}, {"label": "binary_1", "value": data1}]
##        for dat in data:
##            dict_inte = {}
##            dict_inte['sample_type'] = dat[1]
##            dict_inte['sample_type_binary'] = dat[2]
##            data_refa.append(dict_inte)     

        print('check')
        cursor.close()
        conn.close()
##        data_refa = [{"label":"one", "value":20}, {"label":"two", "value":50}, {"label":"three", "value":30}]
        return(render_template('pie.html', data=json.dumps(data_refa)))

if __name__ == "__main__":
    app.run()
