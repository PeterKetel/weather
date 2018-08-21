from flask_table import Table, Col

class LocationTable(Table):
    name = Col('Locatie')

class Locatie(object):
    def __init__(self, name):
        self.name = name
