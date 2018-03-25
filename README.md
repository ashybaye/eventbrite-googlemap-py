# eventbrite-googlemap-py

Install steps:

1. $ python3
2. git clone https://github.com/ashybaye/eventbrite-googlemap-py.git
3. cd eventbrite-googlemap-py
4. $ python3 -m venv venv
5. $ virtualenv venv
6. $ source venv/bin/activate
7. (venv) $ pip install flask
8. (venv) $ export FLASK_APP=eventbrite-googlemap.py  
9. (venv) $ pip install flask-wtf requests flask_googlemaps flask_cache
10. (venv) $ flask run