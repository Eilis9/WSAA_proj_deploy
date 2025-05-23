import mysql.connector
from dbconfig import mysql as config

class dbDAO:
    host = ""
    user = ""
    password = ""
    database = ""
    connection = ""
    cursor = ""


    def __init__(self):
        self.host = config['host']
        self.user = config['user']
        self.password = config['password']
        self.database = config['database']

    def getCursor(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor()
        return self.cursor
    
    def closeAll(self):
        self.cursor.close()
        self.connection.close()

    def check_if_existing(self, year, month):
        results = []
        cursor = self.getCursor()
        sql = "SELECT * FROM elec.unit WHERE year = %s AND month = %s"
     
        try:
            cursor.execute(sql, (year, month))
            results = cursor.fetchall()
            return results
        except:        
            raise Exception("Error in query")
        finally:
            self.closeAll()

    # Function to valid inputted year and month
    def validate_date(self, year, month):
        results = []
        if month.isdigit() is False or int(month) > 12 or int(month)<1:
            results.append("Month invalid")
        
        if year.isdigit() is False or len(year) < 4:
            results.append("Year invalid")
        
        return results

    def create(self, reading):
        # issue with the database freezing after failed attempt to insert record with wrong cost_code
        # connection.rollback() used to rollback the transaction in case of error
        error_check = []
        month_year_check = []

        # Check if the reading being inputted already exists in database
        error_check = self.check_if_existing(reading.get("year"), reading.get("month"))

        # Check if year and month data is valid
        month_year_check = self.validate_date(reading.get("year"), reading.get("month"))
 
        if len(month_year_check) > 0:
            return ({"message": "Enter valid year (YYYY) and month"}), 400

        elif len(error_check) > 0:
            print("Error caught")
            return ({"message": "Reading for that year and month already exists"}), 400      

        else:
            try:
                sql = "INSERT INTO elec.unit (year, month, unit, cost_code) VALUES (%s, %s, %s, %s)"
                values = (reading.get("year"), reading.get("month"), reading.get("unit"), reading.get("cost_code"))
                cursor = self.getCursor()
                cursor.execute(sql, values)
                self.connection.commit()
                newid = cursor.lastrowid
                reading["id"] = newid
                self.closeAll()
                return ({"message": "Reading successfully created", "id": newid}), 200
            except Exception as e:
                self.connection.rollback() 
                self.closeAll() 
                raise e
            finally:
                self.closeAll()


    # gets all units
    def getAll(self):
        cursor = self.getCursor()
        # elec unit table
        # sql_1 = "SELECT * FROM elec.unit ORDER BY year ASC, month ASC"
        # Joins the data from the 2 database tables to get the reading and cost info
        sql_1= """
        SELECT elec.unit.id, elec.unit.year, elec.unit.month, elec.unit.unit, 
        elec.cost.cost_code, elec.cost.supplier, round(elec.cost.s_charge, 3) as s_charge, round(elec.cost.unit_cost, 3) as unit_cost from elec.unit
        INNER JOIN elec.cost 
        ON elec.cost.cost_code = elec.unit.cost_code
        ORDER by year ASC, month ASC;"""
        cursor.execute(sql_1)
        results_1 = cursor.fetchall()
        # Get column names from the cursor description
        column_names = [desc[0] for desc in cursor.description]
        # Convert each row into a dictionary
        json_results = [dict(zip(column_names, row)) for row in results_1]
        # cost table
        #sql_2 = "SELECT * FROM elec.cost"
        #cursor.execute(sql_2)
        #results_2 = cursor.fetchall()
        self.closeAll()
        #return f"unit table {results_1} cost table {results_2}"
        return json_results
    
    # Gets all units



    # gets all cost codes
    def getAllCostCode(self):
        cursor = self.getCursor()
        # elec unit table
        # sql_1 = "SELECT * FROM elec.unit ORDER BY year ASC, month ASC"
        # Joins the data from the 2 database tables to get the reading and cost info
        sql_1= """
        SELECT elec.cost.cost_code, round(elec.cost.s_charge, 3) as s_charge, round(elec.cost.unit_cost, 3) as unit_cost, 
        elec.cost.vat_pc, elec.cost.supplier from elec.cost;"""
        cursor.execute(sql_1)
        results_1 = cursor.fetchall()
        # Get column names from the cursor description
        column_names = [desc[0] for desc in cursor.description]
        # Convert each row into a dictionary
        json_results = [dict(zip(column_names, row)) for row in results_1]
        # cost table
        #sql_2 = "SELECT * FROM elec.cost"
        #cursor.execute(sql_2)
        #results_2 = cursor.fetchall()
        self.closeAll()
        #return f"unit table {results_1} cost table {results_2}"
        return json_results

    # Create a new cost code
    def createCode(self, reading):
        cursor = self.getCursor()
        sql = "INSERT INTO elec.cost (cost_code, s_charge, unit_cost, vat_pc, supplier) VALUES (%s, %s, %s, %s, %s)"
        values = (reading.get("cost_code"), reading.get("s_charge"), reading.get("unit_cost"), reading.get("vat_pc"), reading.get("supplier"))
        print(f"Debug: SQL={sql}, values={values}")  # Debugging
        cursor.execute(sql, values)
        self.connection.commit()
        newid = cursor.lastrowid
        reading["id"] = newid
        self.closeAll()
        return newid



    
    def findbyid(self, year, month):
        cursor = self.getCursor()  
        sql = "SELECT * FROM elec.unit WHERE year = %s AND month = %s"
        cursor.execute(sql, (year, month))
        results = cursor.fetchall()
        self.closeAll()        
        return results
    
    def findbyyear(self, year):
        cursor = self.getCursor()  
        sql = "SELECT unit, month FROM elec.unit WHERE year = %s"
        cursor.execute(sql, (year,))
        results = cursor.fetchall()
        self.closeAll()        
        return results


    def update_unit(self, id, reading):
     
        error_check = []
        month_year_check = []   
        # Check if year and month data is valid
        #month_year_check = self.validate_date(reading.get("year"), reading.get("month"))
        #error_check = self.check_if_existing(reading.get("year"), reading.get("month"))

        #if len(month_year_check) > 0:
        #    return ({"message": "Enter valid year (YYYY) and month"}), 400        
        # check if the unit input is a positive number
        if reading.get("unit").isdigit() is False or int(reading.get("unit")) < 0:
            return ({"message": "Enter valid unit"}), 400
        # Check if the reading already exists in database
        #elif len(error_check) > 0:
        #    return ({"message": "Reading for that year and month already exists"}), 400
        else:
            try:        
                cursor = self.getCursor()  # Get the database cursor   
                sql = "update elec.unit set year=%s, month=%s, unit=%s, cost_code=%s where id=%s"
                values = (reading.get("year"), reading.get("month"), reading.get("unit"), reading.get("cost_code"), id)
                cursor.execute(sql, values)
                self.connection.commit()
                # Check if any rows were updated
                if cursor.rowcount == 0:
                    return ({"message": "No rows updated"}), 400
                else:
                    return ({"message": "Reading successfully updated"}), 200
            except Exception as e:
                # undo the changes made if there's an error
                self.connection.rollback()  
                raise e
            finally:
                self.closeAll()
    

    
    def update_costCode(self, reading):
        
        cursor = self.getCursor()  # Get the database cursor
        
        sql = "update elec.cost set s_charge=%s, unit_cost=%s, vat_pc=%s, supplier=%s where cost_code=%s"
        values = (reading.get("s_charge"), reading.get("unit_cost"), reading.get("vat_pc"), reading.get("supplier"), reading.get("cost_code"))
        print(f"Debug: SQL={sql}, values={values}")  # Debugging
        
        result = cursor.execute(sql, values)
        self.connection.commit()
        self.closeAll()
        return result
    
    # Delete an entry based on id
    def delete(self, id):
        print(f"Debug: delete id={id}")  # Debugging
        cursor = self.getCursor()  
        sql = "DELETE from elec.unit WHERE id = %s"
        values = (id,)
        cursor.execute(sql, values)
        self.connection.commit()
        self.closeAll()        
        return f"deleted entry for {id}"
        
    # Delete a cost code  based on cost code
    def deleteCostCode(self, cost_code):
        print(f"Debug: delete id={cost_code}")  # Debugging
        cursor = self.getCursor()  
        sql = "DELETE from elec.cost WHERE cost_code = %s"
        values = (cost_code,)
        cursor.execute(sql, values)
        self.connection.commit()
        self.closeAll()        
        return f"deleted entry for {cost_code}"
        
    def calcCost(self, reading):
        cursor = self.getCursor()
        sql = """SELECT elec.unit.year, elec.unit.month, elec.unit.unit, 
        elec.cost.cost_code, elec.cost.s_charge, elec.cost.unit_cost, elec.cost.vat_pc from elec.unit
        INNER JOIN elec.cost 
        ON elec.cost.cost_code = elec.unit.cost_code
        WHERE (elec.unit.year>%s OR (elec.unit.year = %s and month>=%s ))
        AND (elec.unit.year<%s OR (elec.unit.year = %s and month<=%s ))"""
        year_start = reading.get("year_start")
        print("in dao", year_start)
        month_start = reading.get("month_start")
        year_end = reading.get("year_end")
        month_end = reading.get("month_end")

        values = (year_start, year_start, month_start, year_end, year_end, month_end)
        cursor.execute(sql, values)
        results = cursor.fetchall()
        # Get column names from the cursor description
        column_names = [desc[0] for desc in cursor.description]
        # Convert each row into a dictionary
        json_results = [dict(zip(column_names, row)) for row in results]
        # Calculate the total cost for each entry
        month_days_dict = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        for entry in json_results:
            entry["cost"] = round((entry["unit"] * entry["unit_cost"] + entry["s_charge"] * month_days_dict[entry["month"]])*(1+entry["vat_pc"]/100), 2)
            
        # Calculate the total cost for all entries
        total_cost = sum(entry["cost"] for entry in json_results)
        # Add the total cost to the result
        json_results.append({"total_cost": total_cost})
        print(json_results)
        self.closeAll()
        return json_results

dbDAO = dbDAO()

