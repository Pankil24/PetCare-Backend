from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from datetime import date, datetime
from flask_cors import CORS
import math
import json


app = Flask(__name__)
CORS(app)

conn = mysql.connector.connect(
    host="localhost", user="root", password="Pankil@1234", database="mydatabase"
)
mycursor = conn.cursor()


@app.route("/register", methods=["POST"])
def register():
    try:

        data = request.get_json()
        today = datetime.today()

        username = data["userName"]
        email = data["email"]
        address = data["address"]
        phone_number = data["phone"]
        age = data["age"]
        gender = data["gender"]
        user_type = data["userType"]
        password = data["password"]
        service_date = today.strftime("%Y-%m-%d %I:%M:%S %p")

        mycursor.execute("SELECT * FROM USERS where username = %s", (username,))
        user_exist = mycursor.fetchall()

        if user_exist:
            print("user exist ==>", user_exist)
            return jsonify("User name exist"), 201
        else:
            if "startTime" in data and "endTime" in data:
                startTime = data["startTime"]
                endTime = data["endTime"]
                mycursor.execute(
                    "INSERT INTO users (username,password ,email, address, phone_number, age, gender, user_type,service_date,start_time,end_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                    username,
                    password,
                    email,
                    address,
                    phone_number,
                    age,
                    gender,
                    user_type,
                    service_date,
                    startTime,
                    endTime,
                ),
            )
            else:
                mycursor.execute(
                    "INSERT INTO users (username,password ,email, address, phone_number, age, gender, user_type,service_date) VALUES (%s, %s,%s, %s, %s, %s, %s, %s,%s)",
                    (
                        username,
                        password,
                        email,
                        address,
                        phone_number,
                        age,
                        gender,
                        user_type,
                        service_date,
                    ),
                )
                conn.commit()
            return jsonify("Data Inserted succussfully"), 200

    except Exception as e:
        conn.rollback()
        return jsonify(f"Error: {str(e)}"), 500


@app.route("/users", methods=["GET"])
def users():
    try:
        # Get pagination parameters from query string
        page = int(request.args.get("pageIndex", 1))  # Default to page 1 if not provided
        page_size = int(
            request.args.get("pageSize", 10)
        )  # Default page size to 10 if not provided

        # Calculate offset for pagination
        offset = (page - 1) * page_size

        mycursor.execute("SELECT COUNT(*) FROM users")
        total_records = mycursor.fetchone()[0]
        total_pages = (total_records + page_size - 1) // page_size

        mycursor.execute("SELECT * FROM users LIMIT %s OFFSET %s", (page_size, offset))
        user_data = mycursor.fetchall()

        user_list = [
            {mycursor.description[i][0]: value for i, value in enumerate(row)}
            for row in user_data
        ]

        response = {
            "totalPages": total_pages,
            "currentPage": page,
            "pageSize": page_size,
            "totalRecords": total_records,
            "data": user_list,
        }

        return jsonify(response), 200
    except Exception as e:
        conn.rollback()
        return jsonify(f"Error: {str(e)}"), 500


@app.route("/login", methods=["POST"])
def login():
    try:
        mess = ""
        data = request.get_json()

        username = data["userName"]
        password = data["password"]

        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        mycursor.execute(query, (username, password))

        user_data = mycursor.fetchone()
        if user_data:
            mess = {"message": "User Exist", "userName": user_data[1],"userType":user_data[8]}
        else:
            mess = "User not Exist"

        return jsonify(mess), 200
    except Exception as e:
        conn.rollback()
        return jsonify(f"Error: {str(e)}"), 500


@app.route("/userService", methods=["POST"])
def service():
    try:
        data = request.get_json()
        today = datetime.today()
        dogname = data["dogname"]
        username = data["username"]
        breed = data["breed"]
        height = float(data["height"])
        weight = float(data["weight"])
        age = int(data["age"])
        gender = data["gender"]
        servicetype = data["servicetype"]
        service_date = today.strftime("%Y-%m-%d %I:%M:%S %p")
        service_price = 100

        if "message" in data:
            message = data["message"]
        else:
            message = None

        if "start_datetime" in data and "end_datetime" in data:
            start_datetime = datetime.strptime(data["start_datetime"], "%Y-%m-%d")
            end_datetime = datetime.strptime(data["end_datetime"], "%Y-%m-%d")
            mycursor.execute(
                "INSERT INTO service (dogname, username, breed, height, weight, age, gender, servicetype, message, start_datetime, end_datetime, service_date,service_price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
                (
                    dogname,
                    username,
                    breed,
                    height,
                    weight,
                    age,
                    gender,
                    servicetype,
                    message,
                    start_datetime,
                    end_datetime,
                    service_date,
                    service_price,
                ),
            )
        else:
            mycursor.execute(
                "INSERT INTO service (dogname, username, breed, height, weight, age, gender, servicetype, message, service_date,service_price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
                (
                    dogname,
                    username,
                    breed,
                    height,
                    weight,
                    age,
                    gender,
                    servicetype,
                    message,
                    service_date,
                    service_price,
                ),
            )

        conn.commit()

        return jsonify("Data inserted successfully"), 200
    except Exception as e:
        conn.rollback()
        return jsonify(f"Error: {str(e)}"), 500


@app.route("/serviceDetails", methods=["GET"])
def service_details():
    try:
        # Get pagination parameters from query string
        page = int(
            request.args.get("pageIndex", 1)
        )  # Default to page 1 if not provided
        page_size = int(
            request.args.get("pageSize", 10)
        )  # Default page size to 10 if not provided
        userName = request.args.get("userId")

        # Calculate offset for pagination
        offset = (page - 1) * page_size

        if userName:
            mycursor.execute(
                "SELECT COUNT(*) FROM service WHERE username = %s ", (userName,)
            )
            total_records = mycursor.fetchone()[0]
            total_pages = math.ceil(total_records / page_size)

            mycursor.execute(
                "SELECT * FROM service WHERE username = %s LIMIT %s OFFSET %s",
                (userName, page_size, offset),
            )
        else:
            mycursor.execute("SELECT COUNT(*) FROM service")
            total_records = mycursor.fetchone()[0]
            total_pages = math.ceil(total_records / page_size)

            mycursor.execute(
                "SELECT * FROM service LIMIT %s OFFSET %s", (page_size, offset)
            )

        user_service_details = [
            {mycursor.description[i][0]: value for i, value in enumerate(row)}
            for row in mycursor.fetchall()
        ]

        response = {
            "totalPages": total_pages,
            "currentPage": page,
            "pageSize": page_size,
            "totalRecords": total_records,
            "data": user_service_details,
        }

        return jsonify(response), 200

    except Exception as e:
        conn.rollback()
        return jsonify(f"Error: {str(e)}"), 500


@app.route("/addDog", methods=["POST"])
def add_dog():

    try:
        data = request.get_json()

        username = data["userName"]
        dogname = data["dogName"]
        breed = data["breed"]
        height = data["height"]
        weight = data["weight"]
        age = data["age"]
        gender = data["gender"]
        mycursor.execute(
            "INSERT INTO dogs (username,dogname ,breed, height, weight, age, gender) VALUES (%s, %s,%s, %s, %s, %s, %s)",
            (username, dogname, breed, height, weight, age, gender),
        )
        conn.commit()
        return jsonify("Dog added succusfully"), 200

    except Exception as e:
        conn.rollback()
        return jsonify(f"Error: {str(e)}"), 500

@app.route("/updateDog/<int:dog_id>", methods=["PUT"])
def update_dog(dog_id):
    try:
        data = request.get_json()

        username = data["userName"]
        dogname = data["dogName"]
        breed = data["breed"]
        height = data["height"]
        weight = data["weight"]
        age = data["age"]
        gender = data["gender"]

        # Update the dog entry with the provided dog_id
        mycursor.execute(
            "UPDATE dogs SET username=%s, dogname=%s, breed=%s, height=%s, weight=%s, age=%s, gender=%s WHERE id=%s",
            (username, dogname, breed, height, weight, age, gender, dog_id),
        )
        conn.commit()
        return jsonify("Dog updated successfully"), 200

    except Exception as e:
        conn.rollback()
        return jsonify(f"Error: {str(e)}"), 500


@app.route("/dogData", methods=["GET"])
def get_dog_data():
    try:
        userName = request.args.get("username")

        mycursor.execute("select * from dogs where username = %s", (userName,))
        user_data = mycursor.fetchall()

        user_list = [
            {mycursor.description[i][0]: value for i, value in enumerate(row)}
            for row in user_data
        ]

        return jsonify(user_list), 200
    except Exception as e:
        conn.rollback()
        return jsonify(f"Error: {str(e)}"), 500


@app.route("/getUserCount", methods=["GET"])
def get_user_count():
    try:
        mycursor.execute("SELECT * FROM users")
        users_data = mycursor.fetchall()
        new_data = []
        for i in range(1, 13):
            if len("0" + str(i)) == 3:
                count = len(
                    [
                        data
                        for data in users_data
                        if data[9][5:7] == ("0" + str(i)).lstrip("0")
                    ]
                )
            else:
                count = len(
                    [data for data in users_data if data[9][5:7] == ("0" + str(i))]
                )
            new_data.append(count)

        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        # Create a dictionary with month names as keys and counts as values
        result = [
            {"month": month, "user": count} for month, count in zip(months, new_data)
        ]

        # Returning all columns' data for the filtered records
        return jsonify(result), 200
    except Exception as e:
        conn.rollback()
        return jsonify(f"Error: {str(e)}"), 500
@app.route("/serviceStats", methods=["GET"])
def service_stats():
    try:
        mycursor.execute("SELECT * FROM service")
        service_data = mycursor.fetchall()
        
        prices_by_month = {
            "01": [],
            "02": [],
            "03": [],
            "04": [],
            "05": [],
            "06": [],
            "07": [],
            "08": [],
            "09": [],
            "10": [],
            "11": [],
            "12": [],
        }
        
        for data in service_data:
            month = data[12][5:7]  # Extract month from the date
            price = data[13]  # Extract the price
            prices_by_month[month].append(price)  # Append the price to the corresponding month's list in the dictionary
        
        user_profit = {}  # Initialize a dictionary to store total price for each month
        for month, prices in prices_by_month.items():
            total_price = sum(prices)  # Calculate total price for the month
            user_profit[month] = total_price  # Store total price for the month in user_profit dictionary
        
        new_data = []
        for i in range(1, 13):  
            if len("0" + str(i)) == 3:
                count = len(
                    [
                        data
                        for data in service_data
                        if data[12][5:7] == ("0" + str(i)).lstrip("0")
                    ]
                )
            else:
                count = len(
                    [data for data in service_data if data[12][5:7] == ("0" + str(i))]
                )

            new_data.append(count) 
        
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        
        result = [
            {"month": month, "service": count, "profit": user_profit.get(str(i).zfill(2), 0)} for i, (month, count) in enumerate(zip(months, new_data), start=1)
        ]
        return jsonify(result), 200
    except Exception as e:
        conn.rollback()
        return jsonify(f"Error: {str(e)}"), 500

if __name__ == "__main__":
    app.run(debug=True)


"""

all import pip command 

pip install Flask
pip install mysql-connector-python
pip install flask_cors

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    age INT NOT NULL,
    gender ENUM('male', 'female', 'other') NOT NULL,
    user_type ENUM('user','care_taker' ,'admin') NOT NULL,
    service_date VARCHAR(100) NOT NULL,
    start_time VARCHAR(50),
    end_time VARCHAR(50)
);

CREATE TABLE service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    dogname VARCHAR(50) NOT NULL,
    breed ENUM('indian_spitz', 'indian_pariah_dog', 'labrador', 'dachshund', 'golden_retriever', 'pug', 'boxer', 'dalmatian', 'pomeranian') NOT NULL,
    height FLOAT NOT NULL,
    weight FLOAT NOT NULL,
    age INT NOT NULL,
    gender ENUM('male', 'female') NOT NULL,
    servicetype VARCHAR(255) NOT NULL,
    message VARCHAR(255),
    start_datetime DATETIME ,
    end_datetime DATETIME ,
    service_date VARCHAR(100) NOT NULL,
    service_price INT NOT NULL
);

CREATE TABLE dogs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    dogname VARCHAR(50) NOT NULL,
    breed ENUM('indian_spitz', 'indian_pariah_dog', 'labrador', 'dachshund', 'golden_retriever', 'pug', 'boxer', 'dalmatian', 'pomeranian') NOT NULL,
    height FLOAT NOT NULL,
    weight FLOAT NOT NULL,
    age INT NOT NULL,
    gender ENUM('male', 'female') NOT NULL
);

"""
