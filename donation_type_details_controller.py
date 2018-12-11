import json
from pony.orm import *


from app.db import DonationTypeDetails


class DonationTypeDetailsController():

    @db_session
    def list_donation_type_details(self):
        donations_types = select(donation_type for donation_type in DonationTypeDetails)
        result = []
        for donation_type in donations_types:
            donation = {"donation_type_details_id": donation_type.donation_type_details_id,
                        "description": donation_type.description,
                        "donation_type_id": donation_type.donation_type_id.donation_type_id}
            result.append(donation)
        return result
