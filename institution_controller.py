import json

from pony.orm import *
from email.utils import parseaddr
from datetime import datetime
import re

from app.db import Institution, InstitutionType, Phone, InstitutionPhone, UserInstitution
from app.address_controller import Address
import app.user_controller

class CRUDInstitution():

    phone_pattern = None

    def __init__(self):
        self.phone_pattern = re.compile("\(\d\d\) (\d{9}|\d{8})$")

    def validate_email(self, email_str):
        return "@" in parseaddr(email_str)[1]


    def is_phone_valid(self, phone_str):
        return self.phone_pattern.match(phone_str)

    @db_session
    def create_institution(self, **kwargs):
        if self.validate_email(kwargs["email"]):
            phones = kwargs["phone"]
            del kwargs["phone"]
            inst = Institution(create_date=datetime.now(), active=True, last_update=datetime.now(), **kwargs)
            inst.flush()
            for phone in phones:
                if self.phone_pattern.match(phone):
                    self.add_phone(institution_id=inst.institution_id, phone_number=phone)
            commit()
            result = {  "institution_id": inst.institution_id,
                        "name": inst.name,
                        "city_id": inst.city_id.city_id,
                        "state": inst.city_id.state_id.state,
                        "city_name": inst.city_id.city,
                        "type": inst.institution_type_id.description,
                        "type_id": inst.institution_type_id.institution_type_id,
                        "email": inst.email,
                        "site": inst.site, "active": inst.active,
                        "street": inst.street, "number": inst.number,
                        "complement": inst.complement, "district": inst.district,
                        "postal_code": inst.postal_code,
                        "phone": phones,
                        "create_date": inst.create_date.strftime("%d/%m/%Y %H:%M"),
                        "last_update": inst.last_update.strftime("%d/%m/%Y %H:%M")}
            return json.dumps(result)
        else:
            raise ValueError("Email not valid")

    @db_session
    def list_institution(self, query):
        if query:
            institutions = select(inst for inst in Institution if inst.name.lower().startswith(query) and inst.active==True)
        else:
            institutions = select(inst for inst in Institution if inst.active==True)
        results = []
        for institution in institutions:
            institution_data = self.get_institution(institution_id=institution.institution_id, export_json=False)
            results.append(institution_data)
        return json.dumps(results)

    @db_session
    def get_institution(self, institution_id, export_json=True):
        inst = Institution.get(institution_id=institution_id)
        phones_inst = select(inst_phone for inst_phone in InstitutionPhone if inst_phone.institution_id==inst)
        phones = []
        address = Address()
        city_data =  address.get_city(inst.city_id.city_id)
        for phone_inst in phones_inst:
            phone = Phone.get(phone_id=phone_inst.phone_id.phone_id)
            phones.append(phone.number)
        response = {"institution_id": institution_id, "name": inst.name,
                    "city_id": inst.city_id.city_id,
                    "city": inst.city_id.city, "state": city_data["state"].state,
                    "type": inst.institution_type_id.description,
                    "institution_type_id": inst.institution_type_id.institution_type_id,
                    "email": inst.email,
                    "site": inst.site, "active": inst.active, "street": inst.street,
                    "number": inst.number, "complement": inst.complement,
                    "phone": phones,
                    "district": inst.district, "postal_code": inst.postal_code,
                    "create_date": inst.create_date.strftime("%d/%m/%Y %H:%M"),
                    "last_update": inst.last_update.strftime("%d/%m/%Y %H:%M")}
        if export_json:
            response = json.dumps(response)
        return response

    @db_session
    def alter_instution(self, institution_id, **kwargs):
        inst = Institution.get(institution_id=institution_id)
        phones = kwargs["phone"]
        del kwargs["phone"]
        inst.set(**kwargs)
        #for phone in phones:
        #    if self.is_phone_valid(phone_str=phone):
        #        self.update_phone(institution_id=institution_id, phone_number=phone)
        commit()
        return self.get_institution(institution_id=institution_id)

    @db_session
    def delete_institution(self, institution_id):
        try:
            inst = Institution.get(institution_id=institution_id)
            inst.activate = False
            commit()
            return {"message": "institution deleted"}
        except Exception as ex:
            print(ex)
            return {"message": "error to delele institution"}

    @db_session
    def add_institution_type(self, description):
        result = InstitutionType(description=description)
        commit()
        return json.dumps({"id": result.institution_type_id,
                            "description": result.description})

    @db_session
    def list_institution_type(self):
        result = select(inst_type for inst_type in InstitutionType)
        result_json = json.dumps([{"id": i.institution_type_id, "description": i.description} for i in result])
        return result_json

    @db_session
    def update_institution_type(self, id, description):
        result = InstitutionType.get(institution_type_id=id)
        result.description = description
        commit()

    @db_session
    def remove_institution_type(self, id):
        inst_type = InstitutionType.get(institution_type_id=id)
        inst_type.delete()
        commit()

    @db_session
    def get_institutions(self, institution_id):
        inst = Institution.get(institution_id=institution_id)
        return inst

    @db_session
    def list_institution_phones(self, institution_id, size=10):
        inst = Institution.get(user_id=institution_id)
        phones_institutions = select( inst_phone for inst_phone in InstitutionPhone if inst_phone.institution_id == inst)
        phones = []
        for phone_inst in phones_institutions:
            phone = Phone.get(phone_id=phone_inst.phone_id.phone_id)
            phone_json = {"institution_id": institution_id, "phone_id":phone_inst.phone_id.phone_id, "number": phone.number}
            phones.append(phone_json)
        return json.dumps(phones)

    #TODO termoinar phones
    @db_session
    def add_phone(self, institution_id, phone_number):
        if self.is_phone_valid(phone_str=phone_number):
            phone = Phone(number=phone_number)
            phone.flush()
            inst_phone = InstitutionPhone( institution_id=institution_id,
                                phone_id=phone.phone_id
                                )
            inst_phone.flush()
            response =  {"institution_id": institution_id, "phone_id": phone.phone_id, "phone_number": phone_number}
        else:
            response =  {"message": "phone not valide", "type": "ERROR"}
        return json.dumps(response)

    @db_session
    def remove_phone(self, institution_id, phone_id):
        institution = Institution.get(institution_id=institution_id)
        phone = Phone.get(phone_id=phone_id)
        phone_institution = InstitutionPhone.get(institution_id=institution, phone_id=phone)
        phone.delete()
        phone_institution.delete()
        commit()

    @db_session
    def update_phone(self, institution_id, phone_number):
        #TODO conSERTAR UPLOAD DE TELEFONE
        if self.is_phone_valid(phone_str=phone_number):
            institution = Institution.get(institution_id=institution_id)
            phone = Phone.get(number=phone_number)
            phones_inst = select(phone_inst for phone_inst in InstitutionPhone if institution_id==institution)
            for phone_inst in phones_inst:
                phone = Phone.get(phone_id=phone_inst.phone_id.phone_id)
            phone.number = phone_number
            commit()
            return json.dumps({"institution_id": institution_id, "phone_id": phone_id, "phone_number": phone_number})
        return {"message": "phone not valide", "type": "ERROR"}


    @db_session
    def list_linked_users(self, institution_id, type="user"):
        inst_id = Institution.get(institution_id=institution_id)
        if institution_id is None:
            users_inst = select(user for user in UserInstitution if
                                user.user_id.role_id.description == "institution")
        else:
            users_inst = select(user for user in UserInstitution if
                                user.institution_id==inst_id and user.user_id.role_id.description==type)
        user = app.user_controller.UserController()
        users = []
        for user_inst in users_inst:
            user_data = user.get_user(user_inst.user_id.user_id, export_json=False)
            user_data["status"] = user_inst.status
            user_data["institution_id"] = user_inst.institution_id.institution_id
            if user_data["status"] in ["PENDING", "APPROVED"]:
                users.append(user_data)
        return users

    @db_session
    def approve_user(self, institution_id, user_id):
        user = UserInstitution.get(institution_id=institution_id, user_id=user_id)
        resp = {}
        if user.status == "PENDING":
            user.status = "APPROVED"
            user_obj = app.user_controller.UserController()
            resp = user_obj.get_user(id=user.user_id.user_id, export_json=False)
            resp["status"] = "APPROVED"
        else:
            raise
        commit()
        return resp

    @db_session
    def remove_user(self, institution_id, user_id):
        user = UserInstitution.get(user_id=user_id, institution_id=institution_id)
        resp = {}
        user.status = "INTS_REMOV"
        commit()
        user_obj = app.user_controller.UserController()
        resp = user_obj.get_user(id=user.user_id.user_id, export_json=False)
        resp["status"] = "INTS_REMOV"
        return resp