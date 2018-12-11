import json
from datetime import datetime

from pony.orm import db_session, commit, select

from app.db import Unit, DonationType, DonationTypeDetails, Institution, DonationUser, User


class DonationControllerUSer():

    @db_session
    def create_donation(self, user_id ,**kwargs):
        unit = Unit.get(unit_id=kwargs["unit_id"])
        user = User.get(user_id=user_id)
        donation_detaiils = DonationTypeDetails.get(donation_type_details_id=kwargs["donation_type_details_id"])
        donation_type = DonationType.get(donation_type_id=kwargs["donation_type_id"])
        date_entry = datetime.strptime(kwargs["date_entry"], "%d/%m/%Y %H:%M")
        date_out = datetime.strptime("01/01/9999", "%d/%m/%Y")
        donation = DonationUser(donation_type_details_id=donation_detaiils,
                                donation_type_id=donation_type,
                                unit_id=unit,
                                date_entry=date_entry,
                                date_out=date_out,
                                amount_entry=kwargs["amount_entry"],
                                user_id=user,
                                status="PENDING"
                                )
        donation.flush()
        commit()
        response = {"user_id": donation.user_id.user_id,
                    "unit_id": unit.unit_id,
                    "unit_id_description": unit.description,
                    "donation_user_id": donation.donation_user_id,
                    "donation_type_id": donation_type.donation_type_id,
                    "donation_type_id_description": donation_type.description,
                    "donation_type_details_id": donation.donation_type_details_id.donation_type_details_id,
                    "donation_type_details_id_description": donation.donation_type_details_id.description,
                    "amount_entry": donation.amount_entry,
                    "date_entry": kwargs["date_entry"],
                    "date_out": "01/01/9999",
                    "status": donation.status
                    }
        return response

    @db_session
    def remove_donation(self, donation_user_id):
        result = False
        try:
            donation = DonationUser(donation_user_id=donation_user_id)
            donation.delete()
            commit()
            result = True
        except:
            print("erro")
        return result

    @db_session
    def alter_donation(self, donation_user_id, **kwargs):
        result = False
        try:
            donation = DonationUser(donation_user_id=donation_user_id)
            donation.set(**kwargs)
            commit()
            result = True
        except:
            print("erro")
        return result

    @db_session
    def list_donations(self, user_id, status=None):
        result_donations = []
        if status is None:
            donations = select(donation for donation in DonationUser if donation.user_id.user_id==user_id)\
                                .order_by(lambda: donation.date_entry)
        else:
            donations = select(donation for donation in DonationUser if donation.user_id.user_id == user_id
                                        and donation.status == status)\
                                        .order_by(lambda: donation.date_entry)

        for donation in donations:
            result = {
                "donation_user_id": donation.donation_user_id,
                "donation_type_id": donation.donation_type_id.donation_type_id,
                "donation_type_id_description": donation.donation_type_id.description,
                "donation_type_details_id": donation.donation_type_details_id.donation_type_details_id,
                "donation_type_details_id_description": donation.donation_type_details_id.description,
                "unit_id": donation.unit_id.unit_id,
                "unit_id_description": donation.unit_id.description,
                "date_entry": donation.date_entry.strftime("%d/%m/%Y %H:%M"),
                "date_out": donation.date_out.strftime("%d/%m/%Y %H:%M"),
                "amount_entry":donation.amount_entry,
                "status": donation.status
            }
            result_donations.append(result)

        result_donations.reverse()
        return result_donations
