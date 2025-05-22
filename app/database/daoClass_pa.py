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



    def create(self, reading):
        # issue with the database freezing after failed attempt to insert record with wrong cost_code
        # connection.rollback() used to rollback the transaction in case of error
        cursor = self.getCursor()
       
        sql = "INSERT INTO elec.unit (year, month, unit, cost_code) VALUES (%s, %s, %s, %s)"
        values = (reading.get("year"), reading.get("month"), reading.get("unit"), reading.get("cost_code"))
        try:
            cursor.execute(sql, values)
            self.connection.commit()
            newid = cursor.lastrowid
            reading["id"] = newid
            return newid
        except Exception as e:
            self.connection.rollback()  
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
        SELECT unit.id, unit.year, unit.month, unit.unit, 
        cost.cost_code, cost.supplier, round(cost.s_charge, 3) as s_charge, round(cost.unit_cost, 3) as unit_cost from unit
        INNER JOIN cost 
        ON cost.cost_code = unit.cost_code
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
        cursor = self.getCursor()  # Get the database cursor   
        sql = "update elec.unit set year=%s, month=%s, unit=%s, cost_code=%s where id=%s"
        values = (reading.get("year"), reading.get("month"), reading.get("unit"), reading.get("cost_code"), id)
        print(f"Debug: SQL={sql}, values={values}")  # Debugging
        try:        
            result = cursor.execute(sql, values)
            self.connection.commit()
            return result
        except Exception as e:
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

