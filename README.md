## 📦 Project Setup Instructions

### 1. 📁 Extract the Project Folder

If you received a ZIP folder (e.g., from Google Drive):

1. Download the ZIP file to your machine.  
2. Extract it to your desired location (e.g., `Documents/fitness-booking-api/`).

### 2. 📥 Install Required Dependencies

Make sure you're in the project root directory (where `requirements.txt` is located) and run:

```bash
pip install -r requirements.txt
```

### 3.  Run Program

```terminal
uvicorn app.main:app --reload --port 8001
```

### 📡 API Endpoints

### **GET** /classes

Returns a list of all upcoming fitness classes including:

* Class name
* Date/time (timezone-aware)
* Instructor
* Available slots

Example URL:
http://127.0.0.1:8001/classes

### **POST** /book

Accepts a booking request with the following JSON body:
```json
{
  "class_id": 1,
  "client_name": "John Doe",
  "client_email": "john@example.com"
}
```
Example URL:
http://127.0.0.1:8001/book

### **GET** /bookings

Returns all bookings made by a specific email address.

#### Query parameter:

email (e.g., john@example.com)

#### Example URL:

http://127.0.0.1:8001/bookings?email=john@example.com