import json
from pony.orm import *


from app.db import DonationType


class DonationTypeController():

    @db_session
    def create_donation_types(self, **kwargs):
        donation_type = DonationType(kwargs)
        commit()
        result = {"doantion_type_id": donation_type.donation_type_id,
                "description": donation_type.description}
        return json.dumps(result)

    @db_session
    def list_donation_types(self):
        donation_types = select(donation_type for donation_type in DonationType)
        result = []
        for donation_type in donation_types:
            result.append({"donation_type_id": donation_type.donation_type_id,
                            "description": donation_type.description})
        return result

    @db_session
    def alter_donation_types(self, donation_type_id, **kwargs):
        try:
            donation_type = DonationType.get(donation_type_id=donation_type_id)
            donation_type.set(kwargs)
            commit()
            return True
        except Exception as ex:
            print(ex)
            return False

    @db_session
    def delete_donation_types(self, donation_type_id):
        try:
            donation_type = DonationType(donation_type_id=donation_type_id)
            donation_type.delete()
            commit()
            return True
        except Exception as ex:
            print(ex)
            return False