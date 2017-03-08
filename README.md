# Remap

Project management application for REMAP

Check out the [demo page](https://github.com/ObsidianRock/remap/blob/master/demo/Demo.md)

[Demo Video](https://github.com/ObsidianRock/remap/blob/master/demo/Overview-3.gif)

## Packages Used

* Flask
* SQLAlchemy
* WTForms

* Flask-GoogleMaps
* geopy

* pdfkit (TODO: Find an alternative to this package)

## Getting Started

### Install Packages

```
pip install virtualenv
virtualenv venv
source venv/bin/activate (for windows venv\Scripts\activate)
pip install -r requirements.txt
```

## Running Application

## Create configuration file

Firstly create an enviroment variable called "remap-config" which points to a "config2.cfg"

In the **config.cfg** file add the following setting in the format:

[setting] = [input]

### Setting list:

REMAP_ADMIN2 = [email address for admin]

PROJECT_UPLOAD = [where to store uploaded project photos]

PROJECT_SOLUTION [where to store volunteer photo upload]

GOOGLEMAPS_KEY = [Google Maps API key]

BROWSER_KEY = [Browser key for google API]

SQLALCHEMY_DATABASE_URI = [The database URI that should be used for the connection]

### Initiate Database

```
python manage.py shell
db.create_all()
Role.insert_roles()

user = Volunteer(name="Obsidian", email="obsidian@remap.com", postcode="SW18", password="aaa")

db.session.add(user)
db.session.commit()

```
### Start server

```
python manage.py runserver
```
Open up a web browser and type in the URL bar **localhost:5000**

## TODO

* Lose dependency for pdfkit
* Use AJAX for the forms to reduce page reloads
* Complete unit testing
* Project list filter
