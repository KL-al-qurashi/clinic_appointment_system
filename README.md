# CloudCare Clinic Appointment System

A complete cloud-ready Flask web application for clinic appointment booking.

## Main Features

- Patient registration and login
- Doctor login
- Role-based dashboard
- Patient can view doctors, specialties, rooms, and working hours
- Patient can book an appointment with a doctor
- Doctor can view all patients who booked with them
- Doctor can update appointment status
- SQLite database
- Ready for cloud deployment as a PaaS web application

## Demo Accounts

### Patient
Email: patient@clinic.com  
Password: patient123

### Doctors
Email: ahmed@clinic.com  
Password: doctor123

Email: sara@clinic.com  
Password: doctor123

Email: khalid@clinic.com  
Password: doctor123

Email: noura@clinic.com  
Password: doctor123

Email: faisal@clinic.com  
Password: doctor123

## Run Locally

1. Install requirements:

```bash
pip install -r requirements.txt
```

2. Run the app:

```bash
python app.py
```

3. Open:

```text
http://127.0.0.1:5000
```

## Notes

The database is created automatically when you run the app for the first time.
The file `clinic.db` will be generated after running the application.

## Cloud Deployment

This project can be deployed on Azure App Service, Google App Engine, AWS Elastic Beanstalk, or Render.
It represents a Platform as a Service cloud solution.
