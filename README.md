CodeCraftHub Learning Management System
CodeCraftHub is a beginner-friendly Learning Management System REST API built with Python and Flask.

The application allows users to manage learning courses using standard HTTP methods. Course data is stored locally in a JSON file instead of a database.

This project is designed for learners who are practicing:

Python
Flask
REST API concepts
JSON request and response data
HTTP status codes
File-based data persistence
Features
Create a new course
Retrieve all courses
Retrieve one course by ID
Update an existing course
Delete a course
Store course data in
courses.json
Automatically create
courses.json
if it does not exist
Automatically generate course IDs
Prevent deleted course IDs from being reused
Preserve
id
and
created_at
during updates
Validate required fields
Validate target dates
Validate course status values
Return JSON responses
Return helpful JSON error messages
Handle malformed or invalid stored JSON safely
No database required
No authentication required
Technologies Used
Python 3
Flask
JSON file storage
Flask is the only external Python dependency required by this project.

Project Structure
codecrafthub/
│
├── app.py
├── courses.json
└── README.md
app.py
Contains the complete Flask application, including:

API routes
Input validation
Course creation
Course updates
Course deletion
JSON file reading and writing
Error handling
ID generation
courses.json
Stores course data and the next available course ID.

This file is created automatically if it does not exist.

Example:

{
  "courses": [],
  "next_id": 1
}
README.md
Contains project documentation and instructions.

Installation
1. Install Python
Make sure Python 3 is installed.

Check your Python version:

python --version
On some systems, use:

python3 --version
Python 3.8 or newer is recommended.

2. Create or open the project directory
Create a directory for the project:

mkdir codecrafthub
cd codecrafthub
Place the following files inside the directory:

app.py
README.md
The
courses.json
file does not need to be created manually. The application creates it automatically.

3. Create a virtual environment
A virtual environment keeps this project's dependencies separate from other Python projects.

Windows
python -m venv venv
Activate it:

venv\Scripts\activate
macOS or Linux
python3 -m venv venv
Activate it:

source venv/bin/activate
After activation, the terminal usually displays
(venv)
at the beginning of the command prompt.

4. Install Flask
Install Flask using
pip
:

pip install Flask
On some systems, use:

pip3 install Flask
Verify the installation:

pip show Flask
Running the Application
Start the Flask application from the project directory:

python app.py
On some systems, use:

python3 app.py
You should see output similar to:

* Running on http://127.0.0.1:5000
The API is now available at:

http://127.0.0.1:5000
To stop the application, press:

Ctrl+C
Data Storage
The application stores data in
courses.json
.

If the file does not exist, it is automatically created with:

{
  "courses": [],
  "next_id": 1
}
A course contains exactly these six fields:

id
name
description
target_date
status
created_at
Example:

{
  "id": 1,
  "name": "Python Basics",
  "description": "Learn the fundamentals of Python.",
  "target_date": "2026-12-31",
  "status": "Not Started",
  "created_at": "2026-09-30T12:00:00Z"
}
The
next_id
value is used to make sure deleted IDs are never reused.

For example:

First course receives ID
1
Second course receives ID
2
If course
1
is deleted, the next course still receives ID
3
API Documentation
The API base URL is:

http://127.0.0.1:5000/api/courses
The API returns JSON responses.

Course fields
Field	Description
id
Automatically generated course ID
name
Course name
description
Course description
target_date
Date in
YYYY-MM-DD
format
status
Not Started
,
In Progress
, or
Completed
created_at
Automatically generated UTC timestamp
1. Create a Course
POST /api/courses
Request
curl -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Python Basics\",\"description\":\"Learn the fundamentals of Python.\",\"target_date\":\"2026-12-31\",\"status\":\"Not Started\"}"
Request body
{
  "name": "Python Basics",
  "description": "Learn the fundamentals of Python.",
  "target_date": "2026-12-31",
  "status": "Not Started"
}
The client must not provide:

id
created_at
The server generates those fields automatically.

Successful response
Status:

201 Created
Response:

{
  "id": 1,
  "name": "Python Basics",
  "description": "Learn the fundamentals of Python.",
  "target_date": "2026-12-31",
  "status": "Not Started",
  "created_at": "2026-09-30T12:00:00Z"
}
2. Get All Courses
GET /api/courses
Request
curl http://127.0.0.1:5000/api/courses
Successful response
Status:

200 OK
Response:

[
  {
    "id": 1,
    "name": "Python Basics",
    "description": "Learn the fundamentals of Python.",
    "target_date": "2026-12-31",
    "status": "Not Started",
    "created_at": "2026-09-30T12:00:00Z"
  }
]
If there are no courses, the response is:

[]
3. Get One Course
GET /api/courses/<id>
Example:

GET /api/courses/1
Request
curl http://127.0.0.1:5000/api/courses/1
Successful response
Status:

200 OK
Response:

{
  "id": 1,
  "name": "Python Basics",
  "description": "Learn the fundamentals of Python.",
  "target_date": "2026-12-31",
  "status": "Not Started",
  "created_at": "2026-09-30T12:00:00Z"
}
Course not found
Status:

404 Not Found
Response:

{
  "error": "Course with ID 1 not found."
}
4. Update a Course
PUT /api/courses/<id>
Example:

PUT /api/courses/1
Request
curl -X PUT http://127.0.0.1:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Advanced Python\",\"description\":\"Learn advanced Python programming.\",\"target_date\":\"2027-01-15\",\"status\":\"In Progress\"}"
Request body
{
  "name": "Advanced Python",
  "description": "Learn advanced Python programming.",
  "target_date": "2027-01-15",
  "status": "In Progress"
}
PUT requires all four editable fields:

name
description
target_date
status
The original values of these fields are replaced.

The following fields are preserved automatically:

id
created_at
Successful response
Status:

200 OK
Response:

{
  "id": 1,
  "name": "Advanced Python",
  "description": "Learn advanced Python programming.",
  "target_date": "2027-01-15",
  "status": "In Progress",
  "created_at": "2026-09-30T12:00:00Z"
}
5. Delete a Course
DELETE /api/courses/<id>
Example:

DELETE /api/courses/1
Request
curl -X DELETE http://127.0.0.1:5000/api/courses/1
Successful response
Status:

200 OK
Response:

{
  "message": "Course deleted successfully."
}
Deleting a course does not decrease or reset
next_id
.

Validation Rules
Required fields
POST and PUT requests must include:

name
description
target_date
status
Name
The name must be a non-empty string.

Invalid examples:

{
  "name": ""
}
{
  "name": "   "
}
Description
The description must be a non-empty string.

Target date
The date must:

Use
YYYY-MM-DD
format
Be a real calendar date
Valid:

2026-12-31
Invalid:

31-12-2026
2026/12/31
2026-02-30
Status
The status must be exactly one of:

Not Started
In Progress
Completed
For example, this is invalid:

in progress
Status values are case-sensitive.

Unexpected fields
Unexpected fields are rejected.

For example:

{
  "name": "Python",
  "description": "Learn Python.",
  "target_date": "2026-12-31",
  "status": "Not Started",
  "teacher": "Alex"
}
Response:

{
  "error": "Unexpected field: teacher."
}
Server-managed fields
Clients cannot provide:

id
created_at
These fields are generated and managed by the server.

HTTP Status Codes
Status code	Meaning
200 OK
Request completed successfully
201 Created
A new course was created
400 Bad Request
The request contains invalid data
404 Not Found
The requested course does not exist
405 Method Not Allowed
The HTTP method is not supported
500 Internal Server Error
A server or file-storage problem occurred
Example validation error:

{
  "error": "target_date must be a valid date in YYYY-MM-DD format."
}
Example missing field error:

{
  "error": "Missing required field: status."
}
Testing the API
Option 1: Test with
curl
Make sure the Flask application is running:

python app.py
Then open another terminal window and run:

Create a course
curl -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Flask Basics\",\"description\":\"Learn Flask REST APIs.\",\"target_date\":\"2026-12-31\",\"status\":\"Not Started\"}"
Get all courses
curl http://127.0.0.1:5000/api/courses
Get course ID 1
curl http://127.0.0.1:5000/api/courses/1
Update course ID 1
curl -X PUT http://127.0.0.1:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Flask Advanced\",\"description\":\"Build advanced Flask APIs.\",\"target_date\":\"2027-01-15\",\"status\":\"In Progress\"}"
Delete course ID 1
curl -X DELETE http://127.0.0.1:5000/api/courses/1
Confirm deletion
curl http://127.0.0.1:5000/api/courses/1
The response should have status
404
.

Option 2: Test with Postman
Postman is a graphical application for testing APIs.

For each request:

Start the Flask application.
Open Postman.
Select the HTTP method.
Enter the request URL.
For POST and PUT:
Select the Body tab.
Select raw.
Choose JSON.
Enter the JSON request body.
Click Send.
Review the response body and status code.
Example URL:

http://127.0.0.1:5000/api/courses
Suggested manual test sequence
Use this sequence to test the complete application:

Start the application.
Call
GET /api/courses
.
Confirm the response is an empty list if there are no courses.
Create a course with POST.
Confirm the response status is
201
.
Call GET all courses.
Call GET by the new course ID.
Update the course with PUT.
Confirm the ID did not change.
Confirm
created_at
did not change.
Delete the course.
Confirm GET by ID returns
404
.
Create another course.
Confirm its ID is not the deleted ID.
Troubleshooting
Flask is not installed
Error:

ModuleNotFoundError: No module named 'flask'
Solution:

pip install Flask
If necessary:

pip3 install Flask
If a virtual environment is being used, make sure it is activated before installing Flask.

The
python
command is not recognized
Try:

python3 app.py
On Windows, reinstall Python and select the option to add Python to the system PATH.

The application address is already in use
Another application may already be using port
5000
.

Stop the other Flask process, or change the port in
app.py
:

app.run(host="127.0.0.1", port=5001)
Then use:

http://127.0.0.1:5001
courses.json
was not created
The file is created when the application receives a request.

Start the application:

python app.py
Then make a request:

curl http://127.0.0.1:5000/api/courses
The file should then appear in the same directory as
app.py
.

A request returns
400 Bad Request
Check that:

The request uses the
Content-Type: application/json
header.
The JSON syntax is correct.
All required fields are included.
No unexpected fields are included.
The date uses
YYYY-MM-DD
.
The status is one of the allowed values.
Example valid request body:

{
  "name": "Python Basics",
  "description": "Learn Python programming.",
  "target_date": "2026-12-31",
  "status": "Not Started"
}
A course returns
404 Not Found
Check that:

The course ID is correct.
The course has not already been deleted.
The URL uses the correct format.
Example:

/api/courses/1
The JSON file is reported as invalid
Do not manually replace the file immediately if it contains important data.

First, make a backup copy of
courses.json
.

The file must contain a structure similar to:

{
  "courses": [],
  "next_id": 1
}
If the file was accidentally edited and the data cannot be repaired, stop the application, back up the original file, and create a new valid
courses.json
.

The API returns a server error when saving
Check that:

The project directory is writable.
courses.json
is not locked by another program.
There is enough disk space.
The application has permission to create or modify files.
Important REST API Concepts
Resource
A course is a resource managed by the API.

The course collection is represented by:

/api/courses
A specific course is represented by:

/api/courses/<id>
HTTP methods
Method	Purpose
POST
Create a course
GET
Read courses
PUT
Replace editable course data
DELETE
Delete a course
This project does not implement
PATCH
.

JSON
JSON is used for:

Request bodies
Successful responses
Error responses
Persistent file storage
Status codes
HTTP status codes tell the client what happened:

200
means success
201
means a resource was created
400
means the client sent invalid data
404
means the requested resource was not found
500
means the server encountered a problem
License
This project is intended for educational use as part of the CodeCraftHub Learning Management System project.