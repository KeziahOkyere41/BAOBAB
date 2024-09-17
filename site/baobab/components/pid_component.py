from invenio_records_resources.services import ServiceComponent
from baobab.pidslink_service.rest_client import PIDsLinkRESTClient
from baobab.pidslink_service.errors import PIDsLinkError, PIDsLinkNoContentError, PIDsLinkServerError
from invenio_rdm_records.services.pids.providers import PIDProvider


class PIDComponent(ServiceComponent)
    def create(self, identity, data, record=None, **kwargs):
        record.pid = self.register_pid(record)

    def update(self, identity, data, record=None, **kwargs)
        record.pid = self.update_pid(record)

    def register_pid(self, record):
        return "ark:/50962/bb67854"