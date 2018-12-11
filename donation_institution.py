from datetime import datetime, timedelta

from pony.orm import commit, db_session, select

from app.db import UserInstitution, DonationUser, DonationInstitution

from app.institution_stock import StockInstitution

class DonationInstitutionController():

    @db_session
    def get_donation_user(self, donation_user):
        result = {
                    "user_id": donation_user.user_id.user_id,
                    "donation_user_id": donation_user.donation_user_id,
                    "name": donation_user.user_id.name,
                    "donation_type_id": donation_user.donation_type_id.donation_type_id,
                    "donation_type_description": donation_user.donation_type_id.description,
                    "donation_type_details_id": donation_user.donation_type_details_id.donation_type_details_id,
                    "donation_type_details_description": donation_user.donation_type_details_id.description,
                    "unit_id": donation_user.unit_id.unit_id,
                    "unit": donation_user.unit_id.description,
                    "date_entry": donation_user.date_entry.strftime("%d/%m/%Y %H:%M"),
                    "amount_entry": donation_user.amount_entry,
                    "date_out": donation_user.date_out.strftime("%d/%m/%Y %H:%M"),
                    "status": donation_user.status
                }
        return result

    @db_session
    def list_user_donation(self, institution_id, days=10, status="APPROVED"):
        users_iter = UserInstitution.select(lambda x: x.institution_id.institution_id == institution_id
                                            and x.status==status)
        donations = []
        date_cut = datetime.now() - timedelta(days=days)
        for user in users_iter:
            donations_iter = select(donation for donation in DonationUser if donation.user_id==user.user_id
                                                 and donation.date_out > datetime.now()
                                                 and donation.date_entry > date_cut).order_by(lambda: donation.date_entry)
            for donation in donations_iter:
                donation_format= self.get_donation_user(donation)
                print(donation_format)
                donations.append(donation_format)
        donations.reverse()
        return donations


    @db_session
    def ativate_donation(self, donation_user_id, institution_id):
        donation_user = DonationUser.get(donation_user_id=donation_user_id)
        if not donation_user is None:
            if donation_user.status == "PENDING":
                donation_user.status = "ATIVE"
                commit()
                result = self.get_donation_user(donation_user)
                #ADD stock
                stock = StockInstitution()
                balance = stock.add_total_stock(donation_user_id=result["donation_user_id"],
                                                institution_id=institution_id)

        return result


    #retirada de doacao
    @db_session
    def withdraw_donation(self, donation_user_id, date_withdraw, institution_id):
        user_donation = DonationUser.get(donation_user_id=donation_user_id)
        if user_donation is None:
            result ={}
        else:
            if user_donation.status == "ATIVE":
                user_donation.status = "WITHDRAW"
                date_withdraw_format = datetime.strptime(date_withdraw, "%d/%m/%Y %H:%M")
                user_donation.date_out = date_withdraw_format
                result = self.get_donation_user(user_donation)
                stock = StockInstitution()
                balance = stock.get_balance(donation_type_id=user_donation.donation_type_id.donation_type_id,
                                            institution_id=institution_id)
                donation_inst = DonationInstitution(institution_id=institution_id,
                                                    donation_user_id=user_donation.donation_user_id,
                                                    institution_balance=balance["institution_balance_id"],
                                                    date_entry=date_withdraw_format
                )
                commit()
                balance_inst = stock.add_avaliable_stock(donation_user_id=result["donation_user_id"],
                                                    donation_institution_id=donation_inst.donation_institution_id)

        return result

