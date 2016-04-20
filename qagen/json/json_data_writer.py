import json

from qagen.knowledge.entities import BaseEntity, EntityRelation

ENTITY_JSON_PROPERTIES = 'properties'
ENTITY_JSON_RELATIONS = 'relations'
ENTITY_JSON_RELATION_REF_ENTITY_TYPE = 'ref_entity_type'
ENTITY_JSON_RELATION_REF_ENTITY_ID = 'ref_entity_id'
ENTITY_JSON_RELATION_REF_ENTITY_IDS = 'ref_entity_ids'


class EntityJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, BaseEntity):
            return json.JSONEncoder.encode(self, self.__to_json_dict(obj))
        else:
            return json.JSONEncoder.encode(self, obj)

    @staticmethod
    def __to_json_dict(entity_instance):
        json_dict = dict()

        # property values are already in form of a dictionary
        json_dict[ENTITY_JSON_PROPERTIES] = dict(entity_instance.property_value_map)

        # collect relation references
        relation_ref_map = {}
        for relation_name, relation_def in entity_instance.__class__.relation_def_map:
            related_entity_class = relation_def.related_entity_class
            relation_value = entity_instance.relation_value_map[relation_name]

            if not relation_value:
                continue

            if relation_def.relation_type == EntityRelation.ONE_TO_ONE:
                # relation_value is a single entity instance
                relation_ref = {
                    ENTITY_JSON_RELATION_REF_ENTITY_TYPE: related_entity_class.__name__,
                    ENTITY_JSON_RELATION_REF_ENTITY_ID: relation_value.get_entity_id()
                }
            else:
                # relation_value is a list of related entity instances
                relation_ref = {
                    ENTITY_JSON_RELATION_REF_ENTITY_TYPE: related_entity_class.__name__,
                    ENTITY_JSON_RELATION_REF_ENTITY_IDS:
                        [single_instance.get_entity_id() for single_instance in relation_value]
                }

            relation_ref_map[relation_name] = relation_ref

        # put it under a different section of the json data
        json_dict[ENTITY_JSON_RELATIONS] = relation_ref_map

        return json_dict

