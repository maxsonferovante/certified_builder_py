from events_api.events_api import EventsAPI

from certified_builder.certified_builder import CertifiedBuilder


certified_builder = CertifiedBuilder(EventsAPI())

certified_builder.build_certificates()