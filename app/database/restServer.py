from flask import Flask, url_for, request, redirect, abort, jsonify, render_template
from daoClass import dbDAO
from flask_cors import CORS
from met_api import get_met
app = Flask(__name__, static_url_path='', static_folder='staticpages', template_folder='../templates')

CORS(app)


#@app.route('/')
#def index():   
#    return "Electricity Unit Recording and Database! - Eilis Donohue"

@app.route('/')
def index_page():
   return render_template('index.html')

@app.route('/webviewer')
def webviewer():
    return render_template('webviewer.html')

@app.route('/costcodes')
def costcodes():
    return render_template('cost_codes.html')

@app.route('/webviewer/analysis')
def analysis():
    return render_template('aggregation.html')


# Plot the usage for current year (2025)
@app.route('/chart')
def chart_page():
    results = dbDAO.findbyyear(int(2025))
    labels = []
    dict = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    data = []
    for result in results:
        labels.append(dict.get(result[1]))
        data.append(result[0])
    # Get the met data for the current year
    year = '2025'
    url="https://prodapi.metweb.ie/monthly-data/Athenry"
    met_feature = "mean_temperature"
    data_temp = get_met(url, met_feature, year)
    print(data_temp)
    print(data)
    data_temp1 = list(data_temp.values())
    print(data_temp1)

    return render_template('mixedchart.html', labels=labels, data=data, data2=data_temp1)



# Updates the chart page when the dropdown is changed
@app.route('/chart_data/<int:year>')
def chart_data(year, methods=['GET']):
    results = dbDAO.findbyyear(year)  # Fetch data for the selected year
    labels = []
    data = []
    
    month_dict = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                  7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    print(results)

    for result in results:
        labels.append(month_dict.get(result[1]))
        data.append(result[0])

    return jsonify({'labels': labels, 'data': data})



# Get all entries in the unit table
@app.route('/elec/units', methods=['GET'])
def getall():
    #table = 'unit'
    results = dbDAO.getAll()
    print("flask", results)
    return jsonify(results)

# Gets the data when the webviewer page is loaded
@app.route('/webviewer/showall', methods=['GET'])
def getallAjax():
    #table = 'unit'
    results = dbDAO.getAll()
    print("webviewer", results)
    return jsonify(results)

# Get all entries in the cost code table
@app.route('/elec/cost_codes', methods=['GET'])
def getAllCode():
    #table = 'unit'
    results = dbDAO.getAllCostCode()
    print("flask", results)
    return jsonify(results)

#create a cost code
@app.route('/elec/cost_codes', methods=['POST'])
def createCode():
    # read json from the body
    jsonstring = request.json
    print(jsonstring)
    reading = {}
    #TODO : put in conditions here based on blanks
    reading["cost_code"] = jsonstring["cost_code"]
    reading["s_charge"] = jsonstring["s_charge"]
    reading["unit_cost"] = jsonstring["unit_cost"]
    reading["vat_pc"] = jsonstring["vat_pc"]
    reading["supplier"] = jsonstring["supplier"]
    
    print("server", request.json)
    return jsonify(dbDAO.createCode(reading))


# Get met data to send to the chart page
@app.route('/met', methods=['GET'])
def get_met_flask():
    url = "https://prodapi.metweb.ie/monthly-data/Athenry"
    
    met_feature = request.args.get('feature', type=str)
    year = request.args.get('year', type=str)
    met_results = get_met(url, met_feature, year)
    print("met_results", met_results)
    print(met_feature, year)
    labels = []
    data = []
    # To convert the met months to the label format for chart
    month_dict = {'january':'Jan', 'february':'Feb', 'mar':'Mar', 'apr':'Apr', 'may':'May', 'june':'Jun',
                  'july':'Jul', 'august':'Aug', 'september':'Sep', 'october':'Oct', 'november':'Nov', 'december':'Dec'}
    data = []
    if not met_results:   
        labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        data = [0,0,0,0,0,0,0,0,0,0,0,0] 
    else:
        for month, value in met_results.items():
            print(month, value)
            labels.append(month_dict.get(month))
            data.append(value)
    #    return jsonify({'labels': labels, 'data': data})
    
    return jsonify({'labels': labels,'data':data})

# find an entry based on year and month query parameters
@app.route('/elec/find', methods=['GET'])
def findbyid():
    year = request.args.get('year', type=int)  
    month = request.args.get('month', type=int)  
    print(f"Debug: year={year}, type={type(year)}")
    print(f"Debug: month={month}, type={type(month)}")
    results = dbDAO.findbyid(year, month)
    return results

#create a reading
@app.route('/elec', methods=['POST'])
def create():
    # read json from the body
    jsonstring = request.json
    reading = {}
    #TODO : put in conditions here based on blanks
    reading["year"] = jsonstring["year"]
    reading["month"] = jsonstring["month"]
    reading["unit"] = jsonstring["unit"]
    reading["cost_code"] = jsonstring["cost_code"]
    print("server", request.json)
    return jsonify(dbDAO.create(reading))


# update an entry based on id
@app.route('/elec/<int:id>', methods=['PUT'])
def update_unit(id):
    # read json from the body
    print("jsonstring in flask", request.json)
    jsonstring = request.json
    reading = {}
    print("reading in server", jsonstring)
    # Extract values from the jsonstring to put in correct order
    reading['id'] = id
    reading["year"] = jsonstring["year"]
    reading["month"] = jsonstring["month"]
    reading["unit"] = jsonstring["unit"]
    reading["cost_code"] = jsonstring["cost_code"]
    print("flask", reading)
    return jsonify(dbDAO.update_unit(id, reading)) 

# update an entry based on id
@app.route('/elec/cost_codes/<string:cost_code>', methods=['PUT'])
def update_costCode(cost_code):
    # read json from the body
    print("jsonstring in flask", request.json)
    jsonstring = request.json
    reading = {}
    print("reading in server", jsonstring)
    # Extract values from the jsonstring to put in correct order
    reading['cost_code'] = jsonstring["cost_code"]
    reading["s_charge"] = jsonstring["s_charge"]
    reading["unit_cost"] = jsonstring["unit_cost"]
    reading["vat_pc"] = jsonstring["vat_pc"]
    reading["supplier"] = jsonstring["supplier"]
    print("flask", reading)
    return jsonify(dbDAO.update_costCode(reading)) 



# delete based on id
@app.route('/elec/<int:id>', methods=['DELETE'])
def delete(id):
    
    return jsonify(dbDAO.delete(id))

# delete a cost code based on cost code
@app.route('/elec/cost_codes/<string:cost_code>', methods=['DELETE'])
def deleteCostCode(cost_code):
    
    return jsonify(dbDAO.deleteCostCode(cost_code))

# Calculates the cost of electricity for a given time period
@app.route('/elec/analysis/cost', methods=['POST'])
def calcCost():
    # read json from the body
    jsonstring = request.json
    print("jsonstr", jsonstring)
    reading = {}
    #TODO : put in conditions here based on blanks
    reading["year_start"] = jsonstring["year_start"]
    reading["month_start"] = jsonstring["month_start"]
    reading["year_end"] = jsonstring["year_end"]
    reading["month_end"] = jsonstring["month_end"]
    
    print("server", reading)
    print("jsonstring in flask", request.json)
    result = dbDAO.calcCost(reading)
    # Extract total cost from the returned json 
    for r in result:
        if 'total_cost' in r:
            total_cost = (r['total_cost'])

    return jsonify({'total_cost': total_cost})


if __name__ == '__main__':
    app.run(debug=True)