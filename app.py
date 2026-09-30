from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import tempfile

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest


app = Flask(__name__)

# Store courses.json in the same directory as this app.py file.
DATA_FILE = Path(__file__).parent / "courses.json"

# These are the only allowed values for a course status.
ALLOWED_STATUSES = {
    "Not Started",
    "In Progress",
    "Completed",
}

# Every course must contain exactly these fields.
COURSE_FIELDS = {
    "id",
    "name",
    "description",
    "target_date",
    "status",
    "created_at",
}

# These are the fields clients must provide when creating or updating a course.
EDITABLE_FIELDS = {
    "name",
    "description",
    "target_date",
    "status",
}


class DataFileError(Exception):
    """Raised when courses.json is missing, invalid, or cannot be accessed."""


def create_empty_data_file():
    """
    Create courses.json with its initial structure.

    This function is only called when the file does not already exist.
    Existing files are never silently overwritten.
    """
    initial_data = {
        "courses": [],
        "next_id": 1,
    }

    save_data(initial_data)


def validate_stored_data(data):
    """
    Validate the structure and contents loaded from courses.json.

    If the file is malformed or contains unexpected data, a DataFileError
    is raised so the API can return a 500 response.
    """
    if not isinstance(data, dict):
        raise DataFileError("Stored data must be a JSON object.")

    # The storage file should contain exactly these two top-level properties.
    if set(data.keys()) != {"courses", "next_id"}:
        raise DataFileError("Stored data has an invalid structure.")

    courses = data["courses"]
    next_id = data["next_id"]

    if not isinstance(courses, list):
        raise DataFileError("The courses value must be a list.")

    # bool is a subclass of int in Python, so it must be rejected explicitly.
    if isinstance(next_id, bool) or not isinstance(next_id, int) or next_id < 1:
        raise DataFileError("The next_id value must be a positive integer.")

    course_ids = set()

    for course in courses:
        if not isinstance(course, dict):
            raise DataFileError("Each stored course must be a JSON object.")

        # Every stored course must contain exactly the six required fields.
        if set(course.keys()) != COURSE_FIELDS:
            raise DataFileError("A stored course has an invalid structure.")

        course_id = course["id"]

        if (
            isinstance(course_id, bool)
            or not isinstance(course_id, int)
            or course_id < 1
        ):
            raise DataFileError("A stored course has an invalid ID.")

        if course_id in course_ids:
            raise DataFileError("Duplicate course IDs were found.")

        course_ids.add(course_id)

        if not isinstance(course["name"], str):
            raise DataFileError("A stored course has an invalid name.")

        if not isinstance(course["description"], str):
            raise DataFileError("A stored course has an invalid description.")

        if not isinstance(course["target_date"], str):
            raise DataFileError("A stored course has an invalid target date.")

        if not is_valid_date(course["target_date"]):
            raise DataFileError("A stored course has an invalid calendar date.")

        if course["status"] not in ALLOWED_STATUSES:
            raise DataFileError("A stored course has an invalid status.")

        if not isinstance(course["created_at"], str):
            raise DataFileError("A stored course has an invalid creation time.")

    # next_id must always be greater than every existing course ID.
    if course_ids and next_id <= max(course_ids):
        raise DataFileError("The next_id value is not valid.")

    return data


def load_data():
    """
    Read and validate courses.json.

    If the file does not exist, it is created automatically.
    """
    if not DATA_FILE.exists():
        create_empty_data_file()

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        # This handles a rare case where the file is removed between the
        # existence check and the read operation.
        create_empty_data_file()

        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            raise DataFileError("Unable to read the course data file.") from error
    except json.JSONDecodeError as error:
        raise DataFileError("The course data file contains invalid JSON.") from error
    except OSError as error:
        raise DataFileError("Unable to read the course data file.") from error

    return validate_stored_data(data)


def save_data(data):
    """
    Save data to courses.json.

    A temporary file is used first, then moved into place. This helps avoid
    leaving a partially written JSON file if a write operation fails.
    """
    try:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        temporary_path = None

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=DATA_FILE.parent,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

            json.dump(data, temporary_file, indent=2)
            temporary_file.write("\n")

        # Replace the old file only after the temporary file was written.
        os.replace(temporary_path, DATA_FILE)

    except (OSError, TypeError, ValueError) as error:
        # Clean up the temporary file if writing or replacing failed.
        if temporary_path is not None and temporary_path.exists():
            try:
                temporary_path.unlink()
            except OSError:
                pass

        raise DataFileError("Unable to save the course data file.") from error


def is_valid_date(value):
    """
    Return True only when value is exactly YYYY-MM-DD and is a real date.
    """
    if not isinstance(value, str):
        return False

    # This ensures the format is exactly four-two-two digits with hyphens.
    if len(value) != 10 or value[4] != "-" or value[7] != "-":
        return False

    year, month, day = value[:4], value[5:7], value[8:10]

    if not (year.isdigit() and month.isdigit() and day.isdigit()):
        return False

    try:
        parsed_date = date(int(year), int(month), int(day))
    except ValueError:
        # This catches invalid calendar dates such as 2026-02-30.
        return False

    # Confirm that the parsed date formats back to the exact original value.
    return parsed_date.isoformat() == value


def validate_course_payload(payload):
    """
    Validate a POST or PUT request body.

    Returns a dictionary containing the four editable course fields.
    Raises ValueError with a user-friendly message when validation fails.
    """
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")

    # Reject server-managed fields supplied by the client.
    if "id" in payload:
        raise ValueError("The id field is generated by the server.")

    if "created_at" in payload:
        raise ValueError("The created_at field is generated by the server.")

    # Reject any fields that are not part of the editable course data.
    unexpected_fields = set(payload.keys()) - EDITABLE_FIELDS

    if unexpected_fields:
        unexpected_field = sorted(unexpected_fields)[0]
        raise ValueError(f"Unexpected field: {unexpected_field}.")

    # All four editable fields are required for both POST and PUT.
    missing_fields = EDITABLE_FIELDS - set(payload.keys())

    if missing_fields:
        missing_field = sorted(missing_fields)[0]
        raise ValueError(f"Missing required field: {missing_field}.")

    name = payload["name"]
    description = payload["description"]
    target_date = payload["target_date"]
    status = payload["status"]

    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string.")

    if not isinstance(description, str) or not description.strip():
        raise ValueError("description must be a non-empty string.")

    if not is_valid_date(target_date):
        raise ValueError("target_date must be a valid date in YYYY-MM-DD format.")

    if status not in ALLOWED_STATUSES:
        raise ValueError(
            "status must be one of: Not Started, In Progress, Completed."
        )

    # Return only validated, editable fields.
    return {
        "name": name,
        "description": description,
        "target_date": target_date,
        "status": status,
    }


def get_json_request_body():
    """
    Read the request JSON and ensure it is a JSON object.

    This function raises ValueError for invalid request bodies.
    """
    if not request.is_json:
        raise ValueError("Request body must contain valid JSON.")

    try:
        payload = request.get_json()
    except BadRequest as error:
        raise ValueError("Request body must contain valid JSON.") from error

    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")

    return payload


def parse_course_id(course_id_text):
    """
    Convert the URL ID to a positive integer.

    A string route parameter is used so invalid IDs can receive a JSON error
    instead of Flask's default HTML error page.
    """
    try:
        course_id = int(course_id_text)
    except ValueError as error:
        raise ValueError("Course ID must be a positive integer.") from error

    if course_id < 1:
        raise ValueError("Course ID must be a positive integer.")

    return course_id


def find_course(courses, course_id):
    """Find and return a course by ID, or return None."""
    for course in courses:
        if course["id"] == course_id:
            return course

    return None


def utc_timestamp():
    """Return the current UTC time in ISO 8601 format."""
    current_time = datetime.now(timezone.utc).replace(microsecond=0)
    return current_time.isoformat().replace("+00:00", "Z")


@app.route("/api/courses", methods=["POST"])
def create_course():
    """Create a new course."""
    try:
        payload = get_json_request_body()
        validated_fields = validate_course_payload(payload)
        data = load_data()

        new_course = {
            "id": data["next_id"],
            **validated_fields,
            "created_at": utc_timestamp(),
        }

        data["courses"].append(new_course)

        # Increment next_id only after the new course has been constructed.
        data["next_id"] += 1

        save_data(data)

        return jsonify(new_course), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except DataFileError:
        return jsonify({"error": "Unable to access course data."}), 500


@app.route("/api/courses", methods=["GET"])
def get_courses():
    """Return all courses."""
    try:
        data = load_data()
        return jsonify(data["courses"]), 200

    except DataFileError:
        return jsonify({"error": "Unable to access course data."}), 500


@app.route("/api/courses/<course_id_text>", methods=["GET"])
def get_course(course_id_text):
    """Return one course by ID."""
    try:
        course_id = parse_course_id(course_id_text)
        data = load_data()
        course = find_course(data["courses"], course_id)

        if course is None:
            return jsonify(
                {"error": f"Course with ID {course_id} not found."}
            ), 404

        return jsonify(course), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except DataFileError:
        return jsonify({"error": "Unable to access course data."}), 500


@app.route("/api/courses/<course_id_text>", methods=["PUT"])
def update_course(course_id_text):
    """Update the editable fields of an existing course."""
    try:
        course_id = parse_course_id(course_id_text)
        payload = get_json_request_body()
        validated_fields = validate_course_payload(payload)
        data = load_data()

        course = find_course(data["courses"], course_id)

        if course is None:
            return jsonify(
                {"error": f"Course with ID {course_id} not found."}
            ), 404

        # Update only editable fields.
        # The original id and created_at values are preserved.
        course.update(validated_fields)

        save_data(data)

        return jsonify(course), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except DataFileError:
        return jsonify({"error": "Unable to access course data."}), 500


@app.route("/api/courses/<course_id_text>", methods=["DELETE"])
def delete_course(course_id_text):
    """Delete an existing course."""
    try:
        course_id = parse_course_id(course_id_text)
        data = load_data()
        course = find_course(data["courses"], course_id)

        if course is None:
            return jsonify(
                {"error": f"Course with ID {course_id} not found."}
            ), 404

        data["courses"].remove(course)

        # next_id is intentionally not changed.
        # This prevents deleted IDs from being reused.
        save_data(data)

        return jsonify({"message": "Course deleted successfully."}), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except DataFileError:
        return jsonify({"error": "Unable to access course data."}), 500


@app.errorhandler(404)
def handle_not_found(error):
    """Return JSON instead of Flask's default HTML 404 response."""
    return jsonify({"error": "The requested resource was not found."}), 404


@app.errorhandler(405)
def handle_method_not_allowed(error):
    """Return JSON for unsupported HTTP methods."""
    return jsonify({"error": "The HTTP method is not allowed for this endpoint."}), 405


@app.errorhandler(500)
def handle_internal_server_error(error):
    """Return a safe JSON response for unexpected server errors."""
    return jsonify({"error": "An internal server error occurred."}), 500


if __name__ == "__main__":
    # Debug mode is disabled by default for safer behavior.
    app.run(host="127.0.0.1", port=5000)
