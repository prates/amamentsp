
import json
import re
from datetime import datetime
from email.utils import parseaddr
from werkzeug.security import generate_password_hash, check_password_hash


from pony.orm import *
from app.db import User, Role, UserInstitution, Phone, UserPhone, Institution
from app.institution_controller import CRUDInstitution

class UserController():

    phone_pattern = None

    def __init__(self):
        self.phone_pattern = re.compile("\(\d\d\) (\d{9}|\d{8})$")


    def validate_email(self, email_str):
        return "@" in parseaddr(email_str)[1]

    def is_phone_valid(self, phone_str):
        return self.phone_pattern.match(phone_str)

    @db_session
    def list_users(self, email_query):
        users = select(user for user in User if user.email.startswith(email_query) and user.active == True)
        result = []
        for user in users:
            user_data = self.get_user(id=user.user_id, export_json=False)
            result.append(user_data)
        return json.dumps(result)

    @db_session
    def list_user_types(self):
        roles = select(role for role in Role)
        role_json = [{"id": role.role_id, "description": role.description} for role in roles]
        return json.dumps(role_json)

    @db_session
    def get_user(self, id, export_json=True):
        user = User.get(user_id=id)
        phones_user = select(user_phone for user_phone in UserPhone if user_phone.user_id == user )
        phones = []
        for phone_user in phones_user:
            phone = Phone.get(phone_id=phone_user.phone_id.phone_id)
            phones.append(phone.number)
        response = {"user_id": id, "nickname": user.nickname, "name": user.name,
                    "email": user.email, "gender": user.gender,
                    "role": user.role_id.description,
                    "role_id": user.role_id.role_id,
                    "bith_date": user.birth_date.strftime("%d/%m/%Y"),
                    "city": user.city_id.city,
                    "city_id": user.city_id.city_id,
                    "state": user.city_id.state_id.state,
                    "state_id": user.city_id.state_id.state_id,
                    "phones": phones, "street": user.street,
                    "number": user.number,"complement":user.complement,
                    "district": user.district, "postal_code": user.postal_code,
                    }
        if export_json:
            response =  json.dumps(response)
        return response

    @db_session
    def delete_user(self, user_id):
        try:
            user = User.get(user_id=user_id)
            user.active = False
            commit()
            return {"message": "user deleted"}
        except Exception as ex:
            print(ex)
            return {"message": "erro"}

    @db_session
    def update_user(self, user_id, **kwargs):
        erro = "OK"
        try:
            user = User.get(user_id=user_id)
            if user is None:
                result = {"message": "user not found"}
                erro = "NOFOUND"
            else:
                user.set(**kwargs)
                commit()
                result = self.get_user(user_id, export_json=False)
        except Exception as ex:
            erro = "ERRO"
            result = {"message": "database erro"}
        return {"erro": erro, "result": result}

    @db_session
    def create_user(self, **kwargs):
        if self.validate_email(kwargs["email"]):
            user = User.get(email=kwargs["email"])
            if user is None:
                if kwargs.get("role_id") is None:
                    role = Role.get(description="user")
                else:
                    role = Role.get(role_id=kwargs["role_id"])
                passwd_encode = generate_password_hash(kwargs["password"])
                user = User(city_id=kwargs["city_id"],
                email=kwargs["email"],
                password=passwd_encode,
                name=kwargs["name"],
                nickname=kwargs["nickname"],
                gender=kwargs["gender"],
                active=True,
                birth_date=datetime.strptime(kwargs["birth_date"], "%d/%m/%Y"),
                role_id=role,
                street=kwargs["street"],
                number=kwargs["number"],
                complement=kwargs["complement"],
                district=kwargs["district"],
                postal_code=kwargs["postal_code"],
                create_date=datetime.now())
                user.flush()
                phones = kwargs["phone"]
                self.add_phones_user(phones, user)
                commit()
                response = {"user_id": user.user_id, "nickname":user.nickname,
                        "name": user.name, "email": user.email, "gender": user.gender,
                        "role": role.description, "role_id": role.role_id,
                        "street": user.street, "city": user.city_id.city,
                        "city_id": user.city_id.city_id,
                        "state": user.city_id.state_id.state,
                        "state_id": user.city_id.state_id.state_id,
                        "number": user.number, "complement": user.complement,
                        "district": user.district, "postal_code": user.postal_code,
                        "phones": kwargs["phone"]}
            else:
                response = {"message": "Email exist", "type": "ERROR"}
        else:
            response = {"message": "Email not valide", "type": "ERROR"}
        return json.dumps(response)

    def add_phones_user(self, phones, user):
        for phone in phones:
            if self.is_phone_valid(phone_str=phone):
                self.add_phone(user_id=user.user_id, phone_number=phone)

    @db_session
    def list_user_phones(self, user_id):
        user = User.get(user_id=user_id)
        phones_users = select( user_phone for user_phone in UserPhone if user_phone.user_id == user)
        phones = []
        for phone_user in phones_users:
            phone = Phone.get(phone_id=phone_user.phone_id.phone_id)
            phone_json = {"id": user_id, "phone_id":phone_user.phone_id.phone_id, "number": phone.number}
            phones.append(phone_json)
        return json.dumps(phones)

    @db_session
    def add_phone(self, user_id, phone_number):
        if self.is_phone_valid(phone_str=phone_number):
            phone = Phone(number=phone_number)
            phone.flush()
            user_phone = UserPhone( user_id=user_id,
                                phone_id=phone.phone_id
                                    )
            response =  {"message": "phone add", "type": "OK"}
        else:
            response =  {"message": "phone not valide", "type": "ERROR"}
        return json.dumps(response)

    @db_session
    def remove_phone(self, user_id, phone_id):
        user = User.get(user_id=user_id)
        phone = Phone.get(phone_id=phone_id)
        phone_user = UserPhone.get(user_id=user, phone_id=phone)
        phone.delete()
        phone_user.delete()
        commit()

    @db_session
    def update_phone(self, user_id, phone_id, phone_number):
        if self.is_phone_valid(phone_str=phone_number):
            user = User.get(user_id=user_id)
            phone = Phone.get(phone_id=phone_id)
            phone_user = UserPhone.get(user_id=user, phone_id=phone)
            phone.number = phone_number
            commit()
            return json.dumps({"id": user_id, "phone_id": phone_id, "phone_number": phone_number})
        return {"message": "phone not valide", "type": "ERROR"}


    @db_session
    def limit_institution_number(self, user_id):
        user_insts = select(user for user in UserInstitution if user.user_id.user_id == user_id)
        count = 0
        for user_inst in user_insts:
            if user_inst.status in ["PENDING", "APPROVED"]:
                count +=1
        if count > 0:
            return False
        return True

    @db_session
    def link_institution(self, user_id, institution_id):
        user = User.get(user_id=user_id)
        if self.limit_institution_number(user_id=user_id):
            crud_inst = CRUDInstitution()
            inst = crud_inst.get_institutions(institution_id=institution_id)
            user_inst = UserInstitution.get(user_id=user_id, institution_id=institution_id)
            if not user_inst is None:
                user_inst.status = "PENDING"
            else:
                user_inst = UserInstitution(user_id=user_id,
                                        institution_id=institution_id,
                                        status="PENDING",
                                        event_date=datetime.today()
                                        )
            commit()
            inst_data = crud_inst.get_institution(institution_id=institution_id, export_json=False)
            inst_data["status"] = "PENDING"
            result = inst_data
        else:
            result = {"message": "USUARIO NAO PODE SE VINCULAR EM MAIS DE 1 INSTITUICAO"}
        return result

    @db_session
    def unlink_institution(self, user_id, institution_id):
        user_inst = UserInstitution.get(user_id=user_id, institution_id=institution_id)
        user_inst.status="REMOVED_BY_USER"
        commit()
        crud_inst = CRUDInstitution()
        inst_data = crud_inst.get_institution(institution_id=institution_id, export_json=False)
        inst_data["status"] = "REMOVED_BY_USER"
        return inst_data


    @db_session
    def list_linked_institution(self, user_id, status=["PENDING", "APPROVED"]):
        user_insts = select(user_inst for user_inst in UserInstitution if user_inst.user_id.user_id==user_id and
                                        user_inst.status in status)
        crud_inst = CRUDInstitution()
        result = {}
        for user_inst in user_insts:
            inst_data = crud_inst.get_institution(institution_id=user_inst.institution_id.institution_id, export_json=False)
            if user_inst.status in ["PENDING", "APPROVED"]:
                inst_data["status"] = user_inst.status
                result = inst_data
        return result

if __name__ == "__main__":
    u = UserController()
    '''
    u.create_user(
         city_id=1,
         email="alexandre.b.prates@gmail.com",
         password="password_teste",
         name="name",
         nickname="nickname",
         gender="masculino",
         street="street",
         number="number",
         complement="complement",
         district="district",
         postal_code="08161-240",
    )'''
    print(u.autenticate(email="alexandre.b.prates@gmail.com", passwd="password_teste"))
