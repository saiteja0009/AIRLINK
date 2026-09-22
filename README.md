# ✈️ AIRLINK – Smart Flight Price Prediction & Booking System

<p align="center">
  <b>AI-Powered Flight Price Prediction and Smart Travel Management Platform</b>
</p>

<p align="center">
  A full-stack Flask web application that combines Machine Learning, flight price prediction,
  booking management, analytics, and electronic ticket generation into a single platform.
</p>

---

## 📌 Overview

**AIRLINK** is an AI-powered flight management web application designed to help users
analyze flight prices, explore available flights, make bookings, and manage their travel
information through a modern and user-friendly interface.

The system combines **Machine Learning models with a Flask-based web application** to
provide flight price predictions and a complete travel workflow.

AIRLINK also provides an **Admin Dashboard** for monitoring bookings, revenue, airline
activity, and analytics.

---

## 🚀 Key Features

### ✈️ Flight Price Prediction

- Predicts flight prices using Machine Learning models.
- Accepts important flight-related inputs such as:
  - Source
  - Destination
  - Travel date
  - Airline
- Provides predicted fare information through a simple web interface.
- Uses multiple Machine Learning approaches for prediction and analysis.

### 🔍 Smart Flight Search

- Search flights based on source and destination.
- Airline selection.
- Travel date selection.
- City/airport autocomplete functionality.
- Displays available flight information in a clean interface.

### 🎫 Flight Booking

- User-friendly flight booking workflow.
- Passenger information management.
- Automatic booking ID generation.
- PNR generation.
- Seat assignment.
- Booking confirmation.
- Booking status tracking.

### 📄 E-Ticket Generation

AIRLINK automatically generates an electronic flight ticket after a successful booking.

The generated ticket contains:

- Passenger name
- Booking ID
- PNR
- Airline
- Source and destination
- Travel date
- Seat number
- Total fare
- Booking status
- Travel information
- Passenger guidelines

The ticket can be generated as a **PDF document** for the passenger.

### 👤 User Authentication

- User registration
- Login system
- Password protection
- Session-based authentication
- Logout functionality

### 🛠️ Admin Dashboard

The application includes an admin dashboard for monitoring the system.

Admin can view:

- Total bookings
- Total revenue
- Top airline
- Airline activity
- Booking information
- System statistics

### 📊 Analytics

AIRLINK provides an analytics section to visualize and understand flight and booking
information.

The analytics functionality helps in understanding:

- Airline activity
- Booking trends
- Revenue information
- Flight-related data

### 📜 Booking History

Users can view their previous bookings and travel information through the booking
history section.

### 📍 Booking Status

Users can check the current status of their flight booking using the booking information.

### 💬 Support

A dedicated support page is included to provide users with travel-related assistance
and application support information.

---

# 🧠 Machine Learning

AIRLINK uses Machine Learning and time-series techniques for flight price prediction.

The project includes multiple trained models:

- **XGBoost**
- **ARIMA**
- **LSTM**

### Models

| Model | Purpose |
|------|---------|
| XGBoost | Flight price prediction using structured flight features |
| ARIMA | Time-series based price analysis/prediction |
| LSTM | Deep learning based sequence/time-series prediction |
| Preprocessor | Data preprocessing and feature transformation |

The trained models are stored inside the `models/` directory.

---

# 🏗️ Technology Stack

## Frontend

- HTML5
- CSS3
- JavaScript
- Responsive UI
- Modern animations and interactive components

## Backend

- Python
- Flask
- Flask-CORS
- SQLite

## Machine Learning

- Scikit-learn
- XGBoost
- TensorFlow
- Keras
- Pandas
- NumPy
- Statsmodels
- Joblib

## PDF Generation

- ReportLab

## Database

- SQLite

---

# 📂 Project Structure

```text
AIRLINK/
│
├── app.py
│
├── airlink.db
│
├── models/
│   ├── arima_model.pkl
│   ├── xgboost_model.pkl
│   ├── preprocessor.pkl
│   └── lstm_model.keras
│
├── data/
│   └── enhanced_flight_data.csv
│
├── templates/
│   ├── admin.html
│   ├── analytics.html
│   ├── booking_status.html
│   ├── booking.html
│   ├── flights.html
│   ├── history.html
│   ├── index.html
│   ├── loading.html
│   ├── login.html
│   ├── no_flights.html
│   ├── result.html
│   ├── signup.html
│   └── support.html
│
├── static/
│   ├── script.js
│   ├── style.css
│   └── qr.png
│
├── analysis/
│
├── tickets/
│
├── venv/
│
└── README.md
