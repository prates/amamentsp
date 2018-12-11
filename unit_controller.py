import json
from pony.orm import *

from app.db import Unit

class UnitController():

    @db_session
    def create_unit(self, **kwargs):
        unit = Unit(kwargs)
        unit.flush()
        commit()
        return {"unit_id": unit.unit_id, "description": unit.description}

    @db_session
    def list_units(self):
        units = select(unit for unit in Unit)
        result = []
        for unit in units:
            result.append({"unit_id": unit.unit_id, "description": unit.description})
        return result
