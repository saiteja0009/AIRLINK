from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import random
import string
import os
import sqlite3


app = Flask(__name__)
app.secret_key = "airlink_super_secret_key_2026"


# =====================================
# DATABASE
# =====================================

def get_db():
    conn = sqlite3.connect("airlink.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_admin():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username='admin'")
    admin = cursor.fetchone()

    if admin is None:
        cursor.execute(
            "INSERT INTO users (username,password) VALUES (?,?)",
            ("admin", "air123")
        )
        conn.commit()

    conn.close()


create_admin()


# =====================================
# LOAD ML MODELS
# =====================================

xgb_model = joblib.load("models/xgboost_model.pkl")
preprocessor = joblib.load("models/preprocessor.pkl")
arima_model = joblib.load("models/arima_model.pkl")
lstm_model = load_model("models/lstm_model.h5", compile=False)
scaler = joblib.load("models/lstm_scaler.pkl")


# =====================================
# LOAD DATASET
# =====================================

df_routes = pd.read_csv("data/enhanced_flight_data.csv")


# =====================================
# ROOT
# =====================================

@app.route('/')
def root():

    if "user" in session:
        return redirect(url_for("home"))

    return redirect(url_for("login_page"))


# =====================================
# DOWNLOAD TICKET
# =====================================

@app.route('/download-ticket/<booking_id>')
def download_ticket(booking_id):

    if "user" not in session:
        return redirect(url_for("login_page"))

    # Get booking details from database
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM bookings WHERE booking_id=?",
        (booking_id,)
    )

    booking = cursor.fetchone()

    conn.close()

    # If booking does not exist
    if booking is None:
        return "Booking not found", 404

    # Create tickets folder
    os.makedirs("tickets", exist_ok=True)

    # PDF file path
    file_path = os.path.join(
        "tickets",
        f"AirLink_Ticket_{booking_id}.pdf"
    )

    # Create PDF
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4
    )

    elements = []

    styles = getSampleStyleSheet()

    # PDF title
    elements.append(
        Paragraph(
            "<b>AIRLINK E-TICKET</b>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    # Ticket information
    ticket_data = [
        ["Passenger Name", booking["passenger"]],
        ["Booking ID", booking["booking_id"]],
        ["PNR", booking["pnr"]],
        ["Seat Number", booking["seat"]],
        ["From", booking["source"]],
        ["To", booking["destination"]],
        ["Airline", booking["airline"]],
        ["Travel Date", booking["date"]],
        ["Total Fare", f"₹ {booking['price']}"],
        ["Status", "CONFIRMED"]
    ]

    # Create table
    table = Table(
        ticket_data,
        colWidths=[150, 300]
    )

    table.setStyle(
        TableStyle([
            (
                'GRID',
                (0, 0),
                (-1, -1),
                1,
                colors.grey
            ),
            (
                'FONTSIZE',
                (0, 0),
                (-1, -1),
                12
            ),
            (
                'ROWHEIGHT',
                (0, 0),
                (-1, -1),
                25
            ),
            (
                'BACKGROUND',
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),
            (
                'VALIGN',
                (0, 0),
                (-1, -1),
                'MIDDLE'
            )
        ])
    )

    elements.append(table)

    # Generate PDF
    doc.build(elements)

    # Download PDF
    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"AirLink_Ticket_{booking_id}.pdf"
    )


# =====================================
# HOME
# =====================================

@app.route('/home')
def home():

    if "user" not in session:
        return redirect(url_for("login_page"))

    return render_template("index.html")


# =====================================
# LOADING
# =====================================

@app.route('/loading')
def loading_page():
    return render_template("loading.html")


# =====================================
# RESULT
# =====================================

@app.route('/result')
def result_page():
    return render_template("result.html")


# =====================================
# SUPPORT
# =====================================

@app.route('/support')
def support_page():
    return render_template("support.html")


# =====================================
# LOGIN
# =====================================

@app.route('/login', methods=["GET", "POST"])
def login_page():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Where the user should go after login
        next_page = request.form.get("next", "home")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user"] = username

            # If user came from Admin, go to Admin dashboard
            if next_page == "admin":
                return redirect(url_for("admin_dashboard"))

            # Otherwise go to Home
            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Invalid Credentials",
            next_page=next_page
        )

    # Get destination from URL
    next_page = request.args.get("next", "home")

    return render_template(
        "login.html",
        next_page=next_page
    )

# =====================================
# SIGNUP
# =====================================

@app.route('/signup', methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        cursor = conn.cursor()

        try:

            cursor.execute(
                "INSERT INTO users (username,password) VALUES (?,?)",
                (username, password)
            )

            conn.commit()

        except:

            return "User already exists"

        conn.close()

        return redirect(url_for("login_page"))

    return render_template("signup.html")


# =====================================
# LOGOUT
# =====================================

@app.route('/logout')
def logout():

    session.pop("user", None)

    return redirect(url_for("login_page"))


# =====================================
# BOOKING PAGE
# =====================================

@app.route('/booking')
def booking_page():

    if "user" not in session:
        return redirect(url_for("login_page"))

    source = request.args.get("source", "")
    destination = request.args.get("destination", "")
    airline = request.args.get("airline", "")
    date = request.args.get("date", "")
    price = request.args.get("price", "")

    return render_template(
        "booking.html",
        source=source,
        destination=destination,
        airline=airline,
        date=date,
        price=price
    )


# =====================================
# BOOKING STATUS
# =====================================

@app.route('/booking-status')
def booking_status():

    if "user" not in session:
        return redirect(url_for("login_page"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM bookings ORDER BY id DESC"
    )

    bookings = cursor.fetchall()

    conn.close()

    return render_template(
        "booking_status.html",
        bookings=bookings
    )


# =====================================
# BOOKING HISTORY
# =====================================

@app.route('/history')
def booking_history():

    if "user" not in session:
        return redirect(url_for("login_page"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM bookings ORDER BY id DESC"
    )

    bookings = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        bookings=bookings
    )


# =====================================
# ADMIN
# =====================================

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():

    # If user is not logged in, send them to login
    if "user" not in session:
        return redirect(url_for("login_page", next="admin"))

    conn = get_db()
    cursor = conn.cursor()

    # Total bookings
    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    # Total revenue
    cursor.execute("SELECT SUM(price) FROM bookings")
    total_revenue = cursor.fetchone()[0] or 0

    # Airline booking count
    cursor.execute(
        "SELECT airline, COUNT(*) FROM bookings GROUP BY airline"
    )

    data = cursor.fetchall()

    airline_count = {
        row[0]: row[1]
        for row in data
    }

    conn.close()

    # Find most booked airline
    if airline_count:
        top_airline = max(
            airline_count,
            key=airline_count.get
        )
    else:
        top_airline = "N/A"

    return render_template(
        "admin.html",
        total_bookings=total_bookings,
        total_revenue=round(float(total_revenue), 2),
        top_airline=top_airline,
        airline_data=airline_count
    )

# =====================================
# ANALYTICS
# =====================================

@app.route('/analytics')
def analytics_page():

    if "user" not in session:
        return redirect(url_for("login_page"))

    return render_template("analytics.html")


@app.route('/analytics-data')
def analytics_data():

    df = pd.read_csv(
        "data/enhanced_flight_data.csv"
    )

    airline_avg = df.groupby("Airline")["Price"].mean()

    month_avg = df.groupby("Journey_Month")["Price"].mean()

    df["Route"] = (
        df["Source"] + " → " + df["Destination"]
    )

    routes = df["Route"].value_counts().head(10)

    price_bins = pd.cut(
        df["Price"],
        bins=10
    )

    price_counts = (
        price_bins
        .value_counts()
        .sort_index()
    )

    return jsonify({

        "airlines":
            airline_avg.index.tolist(),

        "airline_prices":
            airline_avg.values.tolist(),

        "months":
            month_avg.index.tolist(),

        "month_prices":
            month_avg.values.tolist(),

        "routes":
            routes.index.tolist(),

        "route_counts":
            routes.values.tolist(),

        "price_bins":
            [str(i) for i in price_counts.index],

        "price_counts":
            price_counts.values.tolist()

    })


# =====================================
# FLIGHT SEARCH
# =====================================

@app.route('/flights')
def flights_page():

    source = request.args.get("source")
    destination = request.args.get("destination")

    if not source or not destination:
        return redirect(url_for("home"))

    flights_df = df_routes[
        (df_routes["Source"] == source) &
        (df_routes["Destination"] == destination)
    ]

    flights = []

    for _, row in flights_df.head(8).iterrows():

        flights.append({

            "airline": row["Airline"],

            "source": row["Source"],

            "destination": row["Destination"],

            "price": int(row["Price"]),

            "time": random.choice([
                "06:30 AM",
                "09:15 AM",
                "12:40 PM",
                "03:20 PM",
                "07:10 PM"
            ])

        })

    if len(flights) == 0:

        return render_template(
            "no_flights.html",
            source=source,
            destination=destination
        )

    return render_template(
        "flights.html",
        flights=flights
    )


# =====================================
# PRICE PREDICTION
# =====================================

@app.route('/predict', methods=['POST'])
def predict():

    try:

        data = request.get_json()

        source = (
            data.get("Source", "")
            .split(" - ")[0]
            .strip()
        )

        destination = (
            data.get("Destination", "")
            .split(" - ")[0]
            .strip()
        )

        data["Source"] = source
        data["Destination"] = destination

        # Check route
        if (
            (df_routes["Source"] == source) &
            (df_routes["Destination"] == destination)
        ).sum() == 0:

            return jsonify({
                "route_exists": False,
                "message": "No direct flights available"
            })

        numeric_fields = [
            "Total_Stops",
            "Duration_Hours",
            "Duration_Minutes",
            "Journey_Month",
            "Journey_Day",
            "Days_Before"
        ]

        for field in numeric_fields:
            data[field] = int(data[field])

        month = data["Journey_Month"]

        data["Festival"] = (
            1 if month in [10, 11] else 0
        )

        data["IPL"] = (
            1 if month in [4, 5] else 0
        )

        date_obj = datetime(
            2019,
            data["Journey_Month"],
            data["Journey_Day"]
        )

        data["Journey_Weekday"] = (
            date_obj.weekday()
        )

        input_df = pd.DataFrame([data])

        processed = preprocessor.transform(
            input_df
        )

        xgb_pred = xgb_model.predict(
            processed
        )[0]

        arima_pred = (
            arima_model
            .forecast(steps=1)
            .iloc[0]
        )

        last_prices = (
            df_routes["Price"]
            .values[-10:]
        )

        lstm_input = scaler.transform(
            last_prices.reshape(-1, 1)
        )

        lstm_input = lstm_input.reshape(
            1,
            10,
            1
        )

        lstm_pred = lstm_model.predict(
            lstm_input
        )

        lstm_pred = (
            scaler
            .inverse_transform(lstm_pred)[0][0]
        )

        final_price = (
            0.5 * xgb_pred +
            0.3 * arima_pred +
            0.2 * lstm_pred
        )

        trend_prices = []

        for _ in range(7):

            fluctuation = np.random.randint(
                -800,
                800
            )

            trend_prices.append(
                round(
                    float(final_price + fluctuation),
                    2
                )
            )

        return jsonify({

            "route_exists": True,

            "final_price":
                round(float(final_price), 2),

            "trend":
                trend_prices

        })

    except Exception as e:

        print(
            "Prediction Error:",
            e
        )

        return jsonify({

            "route_exists": False,

            "message":
                "Prediction failed"

        })


# =====================================
# SAVE BOOKING
# =====================================

@app.route('/save-booking', methods=['POST'])
def save_booking():

    data = request.get_json()

    booking_id = (
        "AIR" +
        str(random.randint(100000, 999999))
    )

    pnr = ''.join(
        random.choices(
            string.ascii_uppercase +
            string.digits,
            k=6
        )
    )

    seat_number = (
        str(random.randint(1, 30)) +
        random.choice([
            "A",
            "B",
            "C",
            "D",
            "E",
            "F"
        ])
    )

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO bookings
    (booking_id, passenger, source, destination, airline, price, seat, pnr, date)
    VALUES (?,?,?,?,?,?,?,?,?)
    """, (

        booking_id,

        data.get("passenger"),

        data.get("source"),

        data.get("destination"),

        data.get("airline"),

        float(data.get("price")),

        seat_number,

        pnr,

        datetime.now().strftime(
            "%Y-%m-%d"
        )

    ))

    conn.commit()

    conn.close()

    return jsonify({

        "status": "success",

        "booking_id":
            booking_id,

        "pnr":
            pnr,

        "seat":
            seat_number

    })


# =====================================
# RUN APPLICATION
# =====================================

if __name__ == "__main__":
    app.run(debug=True)