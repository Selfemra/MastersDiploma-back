from flask import Flask, render_template, jsonify, request, send_from_directory
import os
from werkzeug.utils import secure_filename

from db_controller import DBController
from face_comparator import FaceComparator

import face_recognition


app = Flask(__name__)

db = DBController()
#db.populate_test_data()

UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/img/<filename>')
def get_image(filename):
    return send_from_directory('img', filename)

@app.route('/admin')
def index():
    return render_template('admin.html')

@app.route('/admin/regions')
def regions():
    response = {'regions': db.get_all_regions()}
    return jsonify(response)

@app.route('/admin/people/<region>/<city>/<street>/<vault>')
def get_people(region, city, street, vault):
    people = db.get_people_by_vault(region, city, street, vault)
    return jsonify({'people': people})


@app.route('/admin/people/add', methods=['POST'])
def add_person():
    try:
        # Get data from the request
        data = request.form  # Assuming form data is used for file upload
        region = data.get('region')
        city = data.get('city')
        street = data.get('street')
        vault = data.get('vault')
        name = data.get('name')

        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'})

        file = request.files['file']

        # Check if the file is allowed
        if file and allowed_file(file.filename):
            # Securely save the file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(filepath)
            # Add the person to the specified vault with the uploaded photo
            db.add_person_to_vault_with_photo(region, city, street, vault, name, filepath)

            return jsonify({'status': 'success', 'message': 'Person added successfully'})

        return jsonify({'status': 'error', 'message': 'File not allowed'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/admin/cities/<region_name>')
def get_cities(region_name):
    cities = db.get_cities_by_region(region_name)
    response = {'cities': cities}
    return jsonify(response)

@app.route('/admin/streets/<region_name>/<city_name>')
def get_streets(region_name, city_name):
    streets = db.get_streets_by_city(region_name, city_name)
    response = {'streets': streets}
    return jsonify(response)

@app.route('/admin/vaults/<region_name>/<city_name>/<street_name>')
def get_vaults(region_name, city_name, street_name):
    vaults = db.get_vaults_by_street(region_name, city_name, street_name)
    response = {'vaults': vaults}
    return jsonify(response)

@app.route('/remove_people', methods=['POST'])
def remove_people():
    try:
        # Get data from the request
        data = request.form  # Assuming form data is used for file upload
        region = data.get('region')
        city = data.get('city')
        street = data.get('street')
        vault = data.get('vault')

        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'})

        file = request.files['file']

        # Check if the file is allowed
        if file and allowed_file(file.filename):
            # Securely save the file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Load the image from the uploaded file
            img_to_remove = face_recognition.load_image_file(filepath)

            # Compare with each person in the specified address from the database
            for person in db.get_people_by_address(region, city, street, vault):
                img_in_db = face_recognition.load_image_file(f'{person["photo_url"]}')
                is_same, accuracy = FaceComparator.compare(img_to_remove, img_in_db)

                # If a similar face is found, remove the person from the database
                if is_same:
                    db.remove_person_by_id(person["id"])
                    os.remove(filepath)  # Remove the uploaded file
                    return jsonify({'status': 'success', 'message': 'Person removed successfully'})

            os.remove(filepath)  # Remove the uploaded file
            return jsonify({'status': 'error', 'message': 'No matching face found'})

        return jsonify({'status': 'error', 'message': 'File not allowed'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    

if __name__ == '__main__':
    app.run(debug=True)
