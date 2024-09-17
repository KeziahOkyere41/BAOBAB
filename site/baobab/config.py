from invenio_records_resources import ServiceConfig
from .components.pid_component import PIDComponent

class PIDServiceConfig(ServiceConfig):
    components = [
        PIDComponent
    ]