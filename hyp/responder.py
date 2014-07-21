import json

from inflection import pluralize

from hyp.adapters.base import adapter_for


class Responder(object):
    def __init__(self, type, serializer, links={}):
        # TODO Add a way to override the pluralized type
        self.type = type
        self.serializer = serializer
        self.links = links
        self.root = self.pluralized_type()
        self.adapter = adapter_for(self.serializer)(self.serializer)

    def update_links(self, type, responder, href):
        link_dict = dict("responder"=responder, "href"=href)
        new_link = dict(type=link_dict)
        return self.links.update(new_link)

    def build_meta(self, meta):
        return meta

    def build_links(self, links):
        rv = {}

        for link in links:
            properties = self.links[link]
            key = "%s.%s" % (self.pluralized_type(), link)
            value = {
                'type': properties['responder'].pluralized_type(),
            }
            if 'href' in properties:
                value['href'] = properties['href']

            rv[key] = value

        return rv

    def build_linked(self, linked):
        rv = {}

        for key, instances in linked.iteritems():
            responder = self.links[key]['responder']
            rv[key] = responder.build_resources(instances)

        return rv

    def build_resources(self, instances, links=None):
        return [self.build_resource(instance, links) for instance in instances]

    def build_resource(self, instance, links):
        resource = self.adapter(instance)
        if links is not None:
            resource['links'] = self.build_resource_links(instance, links)
        return resource

    def build_resource_links(self, instance, links):
        resource_links = {}

        for link in links:
            # TODO Should be able to pick from where to get the related instances
            related = self.pick(instance, link)
            if isinstance(related, list):
                resource_links[link] = [self.pick(r, 'id') for r in related]
            else:
                resource_links[link] = self.pick(related, 'id')
        return resource_links

    def respond(self, instances, meta=None, links=None, linked=None):
        if not isinstance(instances, list):
            instances = [instances]

        if linked is not None:
            links = linked.keys()

        document = {}

        if meta is not None:
            document['meta'] = self.build_meta(meta)
        if links is not None:
            document['links'] = self.build_links(links)
        if linked is not None:
            document['linked'] = self.build_linked(linked)
        document[self.root] = self.build_resources(instances, links)

        return json.dumps(document)

    def pluralized_type(self):
        return pluralize(self.type)

    def pick(self, instance, key):
        try:
            return getattr(instance, key)
        except AttributeError:
            return instance[key]
