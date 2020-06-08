from flask import Flask, render_template, request, jsonify
import sqlite3 as sql
app = Flask(__name__)

DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"

BUGGY_RACE_SERVER_URL = "http://rhul.buggyrace.net"


#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
   return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
  if request.method == 'GET':

     con = sql.connect(DATABASE_FILE)
     con.row_factory = sql.Row
     cur = con.cursor()
     cur.execute("SELECT * FROM buggies")
     record = cur.fetchone();

     return render_template("buggy-form.html", buggy = record)
  elif request.method == 'POST':
    msg=""

    qty_wheels = request.form['qty_wheels']
    power_units = request.form['power_units']
    power_type = request.form['power_type']

    p_type=["petrol", "fusion", "steam", "bio", "electric", "rocket", "hamster", "thermo", "solar", "wind"]
    prices = {"petrol":4, "fusion":400, "steam":3, "bio":5, "electric":20, "rocket":16, "hamster":3, "thermo":300, "solar":40, "wind":20}
  
    
    if qty_wheels.isdigit() == True:
      if power_units.isdigit() == True:
        if int(qty_wheels) >= 4 and int(qty_wheels) % 2 == 0:
          
          with sql.connect(DATABASE_FILE) as con:
            cur = con.cursor()
            cur.execute("UPDATE buggies set qty_wheels=? WHERE id=?", (qty_wheels, DEFAULT_BUGGY_ID))
            cur.execute("UPDATE buggies set power_units=? WHERE id=?", (power_units, DEFAULT_BUGGY_ID))
            cur.execute("UPDATE buggies set power_type=? WHERE id=?", (power_type, DEFAULT_BUGGY_ID))
           
            buggy_cost = prices.get(power_type)*int(power_units)
            cur.execute("UPDATE buggies set buggy_cost=? WHERE id=?", (buggy_cost, DEFAULT_BUGGY_ID))
            
            con.commit()
            msg = "Record successfully saved"

          con.close()
          return render_template("updated.html", msg = msg)
          
  
        else:
          msg = "Number of wheels has to be even and above or equal to 4"
          return render_template("updated.html", msg = msg)

      else:
        msg = "Number of power units has to be an integer"
        return render_template("updated.html", msg = msg)

    else:
        msg = "Number of wheels has to be an integer"
        return render_template("updated.html", msg = msg)
  


#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
  con = sql.connect(DATABASE_FILE)
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM buggies")
  record = cur.fetchone(); 
  return render_template("buggy.html", buggy = record)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/new')
def edit_buggy():
  return render_template("buggy-form.html")


#------------------------------------------------------------
# get JSON from current record
#   this is still probably right, but we won't be
#   using it because we'll be dipping diectly into the
#   database
#------------------------------------------------------------
@app.route('/json')
def summary():
  con = sql.connect(DATABASE_FILE)
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))
  return jsonify(
      {k: v for k, v in dict(zip(
        [column[0] for column in cur.description], cur.fetchone())).items()
        if (v != "" and v is not None)
      }
    )

#------------------------------------------------------------
# delete the buggy
#   don't want DELETE here, because we're anticipating
#   there always being a record to update (because the
#   student needs to change that!)
#------------------------------------------------------------
@app.route('/delete', methods = ['POST'])
def delete_buggy():
  try:
    msg = "deleting buggy"
    with sql.connect(DATABASE_FILE) as con:
      cur = con.cursor()
      cur.execute("DELETE FROM buggies")
      con.commit()
      msg = "Buggy deleted"
  except:
    con.rollback()
    msg = "error in delete operation"
  finally:
    con.close()
    return render_template("updated.html", msg = msg)


if __name__ == '__main__':
   app.run(debug = True, host="0.0.0.0")
