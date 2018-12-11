from datetime import datetime

from pony.orm import commit, db_session

from app.db import InstitutionBalance, DonationInstitution, Institution, DonationUser, DonationType, DonationInstitutionOut




class StockInstitution():

    @db_session
    def get_balance(self, donation_type_id, institution_id, instance=False):
        balance = InstitutionBalance.get(institution_id=institution_id, donation_type_id=donation_type_id)
        if balance is None:
            result = {}
        else:
            if instance:
                return balance
            else:
                result = {
                    "institution_balance_id": balance.institution_balance,
                    "institution_id": institution_id,
                    "donation_type_id": donation_type_id,
                    "donation_type_description": balance.donation_type_id.description,
                    "unit_id": balance.unit_id.unit_id,
                    "unit_description": balance.unit_id.description,
                    "amount_total": balance.amount_total,
                    "amount_available": balance.amount_available
                }
        return result

    @db_session
    def add_total_stock(self, institution_id, donation_user_id):
        donation_user = DonationUser.get(donation_user_id=donation_user_id)
        balance = InstitutionBalance.get(institution_id=institution_id,
                                         donation_type_id=donation_user.donation_type_id)
        amount = donation_user.amount_entry
        if balance is None:
            balance = InstitutionBalance(
                donation_type_id = donation_user.donation_type_id,
                unit_id = donation_user.unit_id,
                amount_total = amount,
                amount_available = 0,
                institution_id = institution_id
            )
            commit()
        else:
            if donation_user.unit_id.unit_id == balance.unit_id.unit_id:
                balance.amount_total += amount
                commit()
            else:
                raise
        return self.get_balance(balance.donation_type_id.donation_type_id, balance.institution_id.institution_id)

    @db_session
    def add_avaliable_stock(self, donation_institution_id, donation_user_id):
        donation_institution = DonationInstitution.get(donation_institution_id=donation_institution_id)
        donation_user = DonationUser.get(donation_user_id=donation_user_id)
        balance = donation_institution.institution_balance
        amount = donation_user.amount_entry
        if donation_user.unit_id.unit_id == balance.unit_id.unit_id:
            balance.amount_total -= amount
            balance.amount_available += amount
            commit()
        else:
            raise
        return self.get_balance(balance.donation_type_id.donation_type_id, balance.institution_id.institution_id)

    @db_session
    def withdraw_stock(self, institution_balance_id, date_out, amount_out):
        date_out_format = datetime.strptime(date_out, "%d/%m/%Y %H:%M")
        balance = InstitutionBalance.get(institution_balance=institution_balance_id)
        saldo = balance.amount_available - amount_out
        result = {}
        if saldo > 0:
            balance.amount_available = saldo
            balance_out = DonationInstitutionOut(institution_balance_id=balance.institution_balance,
                                                 unit_id=balance.unit_id.unit_id,
                                                 date_out=date_out_format,
                                                 amount_out=amount_out)
            commit()
            result = {
                    "institution_balance_id": balance.institution_balance,
                    "institution_id": balance.institution_id.institution_id,
                    "donation_type_id": balance.donation_type_id.donation_type_id,
                    "donation_type_description": balance.donation_type_id.description,
                    "unit_id": balance.unit_id.unit_id,
                    "unit_description": balance.unit_id.description,
                    "amount_total": balance.amount_total,
                    "amount_available": balance.amount_available
            }
        return result