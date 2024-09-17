from invenio_records_resources.services import ServiceComponent

class PIDService(Service)
    def create(self, identity, data):
        self.run_components('create', identity, data)

    def update(self, identity, data):
        self.run_components('update', identity, data)