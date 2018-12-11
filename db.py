import os
from datetime import datetime, date

from pony.orm import *


db = Database()


class Country(db.Entity):
    country_id = PrimaryKey(int, auto=True)
    country = Required(str)
    states = Set("State")

class State(db.Entity):
    state_id = PrimaryKey(int, auto=True)
    country_id = Required(Country)
    state = Required(str)
    cities = Set("City")

class City(db.Entity):
    state_id = Required(State)
    city = Required(str)
    city_id = PrimaryKey(int, auto=True)
    users = Set("User")
    institutions = Set("Institution")

class Role(db.Entity):
    role_id = PrimaryKey(int, auto=True)
    description = Required(str)
    user_institutions = Set("User")

class User(db.Entity):
    user_id = PrimaryKey(int, auto=True)
    city_id = Required(City)
    email = Required(str)
    password = Required(str)
    name = Required(str)
    birth_date = Required(date)
    nickname = Required(str)
    gender = Required(str)
    active = Required(bool)
    street = Required(str)
    number = Required(str)
    complement = Required(str)
    district = Required(str)
    postal_code = Required(str)
    create_date = Required(datetime)
    last_update = Optional(datetime)
    role_id = Required(Role)
    donations_users = Set("DonationUser")
    users_donations_types = Set("UserDonationType")
    user_phones = Set("UserPhone")
    user_institutions = Set("UserInstitution")

class InstitutionType(db.Entity):
    _table_ = "institution_type"
    institution_type_id = PrimaryKey(int, auto=True)
    description = Required(str)
    institutions = Set("Institution")

class Institution(db.Entity):
    institution_id = PrimaryKey(int, auto=True)
    city_id = Required(City)
    institution_type_id = Required(InstitutionType)
    name = Required(str)
    email = Required(str)
    site = Required(str)
    active = Required(bool)
    street = Required(str)
    number = Required(str)
    complement = Required(str)
    district = Required(str)
    postal_code = Required(str)
    create_date = Required(datetime)
    last_update = Required(datetime)
    promotions = Set("Promotion")
    donations_institution = Set("DonationInstitution")
    user_institutions = Set("UserInstitution")
    institution_phones = Set("InstitutionPhone")
    institution_donation_types = Set("InstitutionDonationType")
    institution_balance = Set("InstitutionBalance")


class Phone(db.Entity):
    phone_id = PrimaryKey(int, auto=True)
    number = Required(str)
    user_phones = Set("UserPhone")
    institution_phone = Set("InstitutionPhone")


class Promotion(db.Entity):
    _table_ = "promotion"
    promotion_id = PrimaryKey(int, auto=True)
    institution_id = Required(Institution)
    title = Required(str)
    description = Required(str)
    link = Required(str)
    date_initial = Required(datetime)
    date_end = Required(datetime)

class DonationType(db.Entity):
    _table_ = "donation_type"
    donation_type_id = PrimaryKey(int, auto=True)
    description = Required(str, unique=True)
    donations_type_details = Set("DonationTypeDetails")
    donations_users = Set("DonationUser")
    institutions_balances = Set("InstitutionBalance")
    users_donations_types = Set("UserDonationType")
    institution_donations_types = Set("InstitutionDonationType")

class Unit(db.Entity):
    unit_id = PrimaryKey(int, auto=True)
    description = Required(str)
    donation_user = Set("DonationUser")
    institutions_balances = Set("InstitutionBalance")
    donations_institutions_out = Set("DonationInstitutionOut")

class DonationTypeDetails(db.Entity):
    _table_ =  "donation_type_details"
    donation_type_details_id = PrimaryKey(int, auto=True)
    description = Required(str)
    donation_type_id = Required(DonationType)
    doantions_users = Set("DonationUser")

class DonationUser(db.Entity):
    _table_ = "donation_user"
    donation_user_id = PrimaryKey(int, auto=True)
    user_id = Required(User)
    donation_type_id = Required(DonationType)
    donation_type_details_id = Required(DonationTypeDetails)
    unit_id = Required(Unit)
    date_entry = Required(datetime)
    date_out = Required(datetime)
    amount_entry = Required(int)
    status = Required(str)
    donations_institution = Set("DonationInstitution")

class InstitutionBalance(db.Entity):
    _table_ = "institution_balance"
    institution_balance = PrimaryKey(int, auto=True)
    donation_type_id = Required(DonationType)
    unit_id = Required(Unit)
    amount_total = Required(int)
    amount_available = Required(int)
    institution_id = Required(Institution)
    donation_institution = Set("DonationInstitution")
    donations_institutions_out = Set("DonationInstitutionOut")

class DonationInstitution(db.Entity):
    _table_ = "donation_institution"
    donation_institution_id = PrimaryKey(int, auto=True)
    institution_id = Required(Institution)
    donation_user_id = Required(DonationUser)
    institution_balance = Required(InstitutionBalance)
    date_entry = Required(datetime)

class UserDonationType(db.Entity):
    _table_ = "user_donation_type"
    user_id = Required(User)
    donation_type_id = Required(DonationType)
    PrimaryKey(user_id, donation_type_id)

class InstitutionDonationType(db.Entity):
    _table_ = "institution_donation_type"
    institution_id = Required(Institution)
    donation_type_id = Required(DonationType)
    PrimaryKey(institution_id, donation_type_id)

class DonationInstitutionOut(db.Entity):
    _table_ = "donation_institution_out"
    donation_institution_out_id = PrimaryKey(int, auto=True)
    institution_balance_id = Required(InstitutionBalance)
    unit_id = Required(Unit)
    date_out = Required(datetime)
    amount_out = Required(int)

class UserPhone(db.Entity):
    _table_ = "user_phone"
    phone_id = Required(Phone)
    user_id = Required(User)
    PrimaryKey(phone_id, user_id)

class InstitutionPhone(db.Entity):
    _table_ = "institution_phone"
    phone_id = Required(Phone)
    institution_id = Required(Institution)
    PrimaryKey(phone_id, institution_id)

class UserInstitution(db.Entity):
    _table_ = "user_institution"
    user_id = Required(User)
    institution_id = Required(Institution)
    status = Required(str)
    event_date = Required(date)
    PrimaryKey(user_id, institution_id)

#db.bind(provider="mysql", host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"), passwd=os.getenv("DB_PASSWD"), db=os.getenv("DB_NAME"))

db.bind(provider="mysql", host="amamenta-sp.ctmmvnhmrbqo.us-east-2.rds.amazonaws.com", user="pgp2018", passwd="asdf1234", db="amamentasp")
db.generate_mapping(create_tables=False)
