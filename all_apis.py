from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from datetime import date, datetime
from flask_cors import CORS

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

        username = data["userName"]
        email = data["email"]
        address = data["address"]
        phone_number = data["phone"]
        age = data["age"]
        gender = data["gender"]
        user_type = data["userType"]
        password = data["password"]

        mycursor.execute("SELECT * FROM USERS where username = %s", (username,))
        user_exist = mycursor.fetchall()

        if user_exist:
            print("user exist ==>", user_exist)
            return jsonify("User name exist"), 201
        else:
            mycursor.execute(
                "INSERT INTO users (username,password ,email, address, phone_number, age, gender, user_type) VALUES (%s, %s,%s, %s, %s, %s, %s, %s)",
                (
                    username,
                    password,
                    email,
                    address,
                    phone_number,
                    age,
                    gender,
                    user_type,
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
        mycursor.execute("select * from users")
        user_data = mycursor.fetchall()

        user_list = [
            {mycursor.description[i][0]: value for i, value in enumerate(row)}
            for row in user_data
        ]

        return jsonify(user_list), 200
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
            mess = {"message": "User Exist", "userName": user_data[1]}
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

        print("servide date ==>", service_date)

        if "message" in data:
            message = data["message"]
        else:
            message = None

        if "start_datetime" in data and "end_datetime" in data:
            start_datetime = datetime.strptime(data["start_datetime"], "%Y-%m-%d")
            end_datetime = datetime.strptime(data["end_datetime"], "%Y-%m-%d")
            mycursor.execute(
                "INSERT INTO service (dogname, username, breed, height, weight, age, gender, servicetype, message, start_datetime, end_datetime, service_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
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
                ),
            )
        else:
            mycursor.execute(
                "INSERT INTO service (dogname, username, breed, height, weight, age, gender, servicetype, message, service_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
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
                ),
            )

        conn.commit()

        return jsonify("Data inserted successfully"), 200
    except Exception as e:
        conn.rollback()
        return jsonify(f"Error: {str(e)}"), 500


@app.route("/serviceDetails")
def service_details():

    try:
        userName = request.args.get("userId")

        if userName:
            mycursor.execute("SELECT * FROM service WHERE username = %s ", (userName,))
        else:
            mycursor.execute("SELECT * FROM service")

        user_service_details = [
            {mycursor.description[i][0]: value for i, value in enumerate(row)}
            for row in mycursor.fetchall()
        ]

        return jsonify(user_service_details), 200

    except Exception as e:
        conn.rollback()
        return jsonify(f"Error: {str(e)}"), 500


@app.route("/addDog", methods=["POST"])
def add_dog():

    try:
        data = request.get_json()

        username = data["username"]
        dogname = data["dogname"]
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


if __name__ == "__main__":
    app.run(debug=True)


"""
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    age INT NOT NULL,
    gender ENUM('male', 'female', 'other') NOT NULL,
    user_type ENUM('user','care_taker' ,'admin') NOT NULL
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
    service_date VARCHAR(100) NOT NULL
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
