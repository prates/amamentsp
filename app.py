import json
import logging
import os
import sys

import flask
from flask import Flask
from flask import request

from app.address_controller import Address
from app.auth import Auth
from app.controller_donation_user import DonationControllerUSer
from app.donation_institution import DonationInstitutionController
from app.donation_type_controller import DonationTypeController
from app.donation_type_details_controller import DonationTypeDetailsController
from app.institution_controller import CRUDInstitution
from app.promotion_controller import ControllerPromotion
from app.user_controller import UserController
from app.unit_controller import UnitController
from app.institution_stock import StockInstitution

application = Flask(__name__)
gunicorn_logger = logging.getLogger("gunicorn.error")
application.logger.handlers = gunicorn_logger.handlers
application.logger.setLevel(gunicorn_logger.level)


@application.route('/')
def index():
    print('Hit on /')
    return 'Hello World! 1234'

@application.route("/cities/", methods=["GET"])
def list_cities():
    if request.method == "GET":
        query = request.args.get("query", type=str)
        state_id = request.args.get("state_id", type=str)
        application.logger.info("/cities/ method: %s" % (request.method))
        application.logger.info("headers")
        application.logger.info(request.headers)
        application.logger.info("params %s" % request.args)
        addr = Address()
        result = addr.query_cities(state_id=state_id, query=query)
        resp = flask.Response(result)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        if len(result) < 4:
            return resp, 204

        return resp

@application.route("/states/", methods=["GET"])
def list_states():
    if request.method == "GET":
        country_id = request.args.get("country_id", default=1, type=int)
        query = request.args.get("query", type=str)
        addr = Address()
        result = addr.query_states(country_id=country_id, query=query)
        resp = flask.Response(result)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        if len(result) < 4:
            return resp, 204
        return resp

@application.route("/countries/", methods=["GET"])
def list_countries():
    if request.method == "GET":
        query = request.args.get("query", type=str)
        addr = Address()
        result = addr.query_countries(query=query)
        resp = flask.Response(result)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        if len(result) < 4:
            return resp, 204
        return resp

@application.route("/users/", methods=["POST", "GET", "PUT", "DELETE"])
def process_users():
    usercontroller = UserController()
    if request.method == "POST":
        content = request.json
        print(content)
        #try:
        user = usercontroller.create_user(city_id=content["city_id"],
                            email=content["email"],
                            password=content["password"],
                            name=content["name"],
                            birth_date=content["birth_date"],
                            phone = content["phone"],
                            role_id=content["role_id"],
                            nickname=content["nickname"],
                            gender=content["gender"],
                            street=content["street"],
                            number=content["number"],
                            complement=content["complement"],
                            district=content["district"],
                            postal_code=content["postal_code"])

        print("usuario criado")
        resp = flask.Response(user)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers.add("Access-Control-Allow-Headers", "*")
        resp.headers.add("Access-Control-Allow-Methods", "*")
        response = json.loads(user)
        if response.get("message"):
            return resp, 200
        else:
            return resp, 201
        #except Exception as ex:
        #    return "", 400
    elif request.method == "GET":
        email_query = request.args.get("email-query", type=str)
        application.logger.info("method %s args = %s" % (request.method, request.args))
        result = usercontroller.list_users(email_query)
        application.logger.info("result : %s" % (result))
        resp = flask.Response(result)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    elif request.method == "DELETE":
        content = request.json
        result = usercontroller.delete_user(user_id=content["user_id"])
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200
    elif request.method == "PUT":
        content = request.json
        print(content)
        result = usercontroller.update_user(**content)
        resp = flask.Response(json.dumps(result["result"]))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        if result["erro"] == "OK":
            return resp , 200
        elif result["erro"] == "NOFOUND":
            resp = flask.Response(json.dumps({"message": "user not found"}))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 205

@application.route("/roles/", methods=["GET"])
def list_roles():
    if request.method == "GET":
        usercontroller = UserController()
        result = usercontroller.list_user_types()
        resp = flask.Response(result)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

@application.route("/phones/", methods=["POST", "PUT", "DELETE", "GET"])
def process_phone():
    usercontroller = UserController()
    content = request.json
    if request.method == "POST":
        try:
            response = usercontroller.add_phone(user_id=content["user-id"],
                                    phone_number=content["phone-number"])
            return response, 201
        except Exception as ex:
            return ex, 400
    elif request.method == "PUT":
        #try:
        usercontroller.update_phone(user_id=content["user-id"],
                                        phone_id=content["phone-id"],
                                        phone_number=content["phone-number"])
        return "", 200
        #except Exception as ex:
        #    return "", 400
    elif request.method == "GET":
        try:
            result = usercontroller.list_user_phones(user_id=request.args.get("user-id", type=int))
            return result
        except Exception as ex:
            print(ex, file=sys.stderr)
            return "", 400
    elif request.method == "DELETE":
        try:
            usercontroller.remove_phone(user_id=content["user-id"],
                                        phone_id=content["phone-id"])
            return "", 200
        except Exception as ex:
            return "", 400

@application.route("/login/", methods=["POST"])
def login():
    content = request.json
    auth  = Auth()
    result = auth.autenticate(email=content["email"], password=content["password"])
    if result is None:
        result = json.dumps({"message": "email ou password invalid"})
    resp = flask.Response(result)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp, 200

@application.route("/logout/", methods=["GET"])
def logout():
    auth = Auth()
    token = request.headers.get("token")
    token = auth.logout(token=token)
    result = json.dumps({"token": token, "message": "logout"})
    resp = flask.Response(result)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@application.route("/institutions/", methods=["POST", "GET", "PUT", "DELETE"])
def institutions():
    inst = CRUDInstitution()
    if request.method == "POST":
        content = request.json
        #try:
        result = inst.create_institution(city_id=content["city-id"],
                                    institution_type_id=content["institution-type"],
                                    name=content["name"],
                                    email=content["email"],
                                    site=content["site"],
                                    street=content["street"],
                                    number=content["number"],
                                    complement=content["complement"],
                                    district=content["district"],
                                    phone=content["phone"],
                                    postal_code=content["postal-code"]
                                    )
        #except KeyError as ex:
        #    return json.dumps({"message": "Field not found %s" % (str(ex))}), 401
        resp = flask.Response(result)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 201
    elif request.method == "GET":
        result = inst.list_institution(query=request.args.get("query", type=str))
        resp = flask.Response(result)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200
    elif request.method == "PUT":
        content = request.json
        result = inst.alter_instution(**content)
        resp = flask.Response(result)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200
    elif request.method == "DELETE":
        content = request.json
        try:
            result = inst.delete_institution(institution_id=content["institution-id"])
            resp = flask.Response(json.dumps(result))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp, 200
        except Exception as ex:
            return "", 400

@application.route("/institution-types/", methods=["POST", "GET", "PUT", "DELETE"])
def institution_type():
    inst = CRUDInstitution()
    if request.method == "POST":
        content = request.json
        result = inst.add_institution_type(content["description"])
        resp = flask.Response(result)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 201
    elif request.method == "GET":
        result = inst.list_institution_type()
        resp = flask.Response(result)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200
    elif request.method == "PUT":
        content = request.json
        result = inst.update_institution_type(id=content["id"],
                                            description=content["description"])

        return "", 200
    elif request.method == "DELETE":
        content = request.json
        inst.remove_institution_type(content["id"])
        return "", 200

@application.route("/link-user-institutions/", methods=["GET", "POST", "DELETE"])
def linked_users():
    users = UserController()
    if request.method == "POST":
        content = request.json
        result = users.link_institution(user_id=content["user_id"],
                                        institution_id=content["institution_id"])
        return json.dumps(result), 200
    elif request.method == "GET":
        application.logger.info("/link-user-institutions/ - %s" % (request.method))
        user_id = request.headers.get("user_id", type=int)
        if user_id is None:
            user_id = request.args.get("user_id", type=int)
            application.logger.info("/link-user-institutions/ - args: %s" % (request.args))
        application.logger.info("/link-user-institutions/ - headers: %s" % (request.headers))
        application.logger.info("/link-user-institutions/ - user_id: %s" % (user_id) )
        result = users.list_linked_institution(user_id)
        result_json = json.dumps(result)
        application.logger.info("/link-user-institutions/ - json_response %s " % (result_json))
        resp = flask.Response(result_json)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200

@application.route("/link-user-institutions/delete/", methods=["POST"])
def delete_linked_users():
    users = UserController()
    if request.method == "POST":
        content = request.json
        result = users.unlink_institution(user_id=content["user_id"],
                                          institution_id=content["institution_id"])
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp, 200

@application.route("/link-institution-users/", methods=["GET", "POST", "DELETE"])
def linked_users_institution():
    inst = CRUDInstitution()
    if request.method == "GET":
        inst_id = request.args.get("institution_id", type=int)
        type = request.args.get("type", type=str)
        application.logger.info("/link-institution-users/ method: %s" % (request.method))
        application.logger.info("params: %s" % (request.args))
        application.logger.info("headers")
        application.logger.info(request.headers)
        if type is None:
            users = inst.list_linked_users(institution_id=inst_id)
        else:
            users = inst.list_linked_users(institution_id=inst_id, type=type)
        application.logger.info("result: %s" % (users))
        users_json  = json.dumps(users)
        resp = flask.Response(users_json)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        #if len(users) > 0 :
        return resp, 200
        #else:
        #    return resp, 204
    elif request.method == "POST":
        content = request.json
        user_id = content["user_id"]
        institution_id = content["institution_id"]
        application.logger.info("/link-institution-users/ method - %s" %(request.method))
        application.logger.info("content %s" %(content))
        result = inst.approve_user(institution_id=institution_id, user_id=user_id)
        application.logger.info("result %s" % (result))
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200

@application.route("/link-institution-users/delete/", methods=["POST"])
def delete_linked_users_institution():
    inst = CRUDInstitution()
    if request.method == "POST":
        content = request.json
        application.logger.info("/link-institution-users/ method - %s" %(request.method))
        application.logger.info("HEADERS ------ %s" % (request.headers))
        application.logger.info("body %s" %(request.json))
        result = inst.remove_user(institution_id=content["institution_id"], user_id=content["user_id"])
        application.logger.info("result %s" % (result))
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200

@application.route("/status/", methods=["GET"])
def list_status():
    if request.method == "GET":
        status = ["PENDING", "APROVED", "DELETED", "MASTER", "MEMBER_PENDING", "MEMBER"]
        resp = flask.Response(json.dumps(status))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200

@application.route("/promotion/", methods=["GET", "PUT", "DELETE", "POST"])
def process_promotion():
    promotion_ctrl = ControllerPromotion()
    if request.method == "GET":
        size = request.args.get("size", type=int)
        promotion_result = promotion_ctrl.list_all_promotion(size)
        resp = flask.Response(json.dumps(promotion_result))
        if len(promotion_result) > 0:
            return resp, 200
        else:
            return resp, 204
    elif request.method == "POST":
        content = request.json
        institution_id = content["institution_id"]
        del content["institution_id"]
        data = promotion_ctrl.create_promotion(institution_id=institution_id, **content)
        resp = flask.Response(json.dumps(data))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200
    elif request.method == "PUT":
        content = request.json
        promotion_id = content["promotion_id"]
        del content["promotion_id"]
        result = promotion_ctrl.alter_promotion(promotion_id=promotion_id, **content)
        resp = flask.Response(json.dumps(result["result"]))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        if result["status"] == "OK":
            return resp, 200
        else:
            return resp, 404
    elif request.method == "DELETE":
        promotion_id = request.headers.get("promotion_id", type=int)
        result = promotion_ctrl.delete_promotion(promotion_id=promotion_id)
        if result:
            msg = {"message": "promotion deleted"}
        else:
            msg = {"message": "promotion not deleted"}
        resp = flask.Response(json.dumps(msg))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200

@application.route("/donations-types/", methods=["GET", "PUT", "DELETE", "POST"])
def process_donation_types():
    donation = DonationTypeController()
    if request.method == "GET":
        result = donation.list_donation_types()
        resp = flask.Response(result)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200
    elif request.method == "POST":
        content = request.json
        result = donation.create_donation_types(**content)
        resp = flask.Response(result)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200
    elif request.method == "PUT":
        content = request.json
        donation_type_id = content["donation_type_id"]
        del content["donation_type_id"]
        result = donation.alter_donation_types(donation_type_id=donation_type_id, **content)
        if result:
            resp = json.dumps(content)
        else:
            resp = json.dumps({"message": "donation type not altered"})
        resp_result = flask.Response(resp)
        resp_result.headers['Access-Control-Allow-Origin'] = '*'
        return resp_result, 200

    elif request.method == "DELETE":
        donation_type_id = request.headers.get("donation_type_id")
        result = donation.delete_donation_types(donation_type_id=donation_type_id)
        if result:
            result_resp = json.dumps({"message": "donation type deleted"})
        else:
            result_resp = json.dumps({"message": "donation type not deleted"})
        resp = flask.Response(result_resp)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200

@application.route("/donations-user/", methods=["GET", "DELETE", "POST"])
def process_donation_user():
    donation = DonationControllerUSer()
    if request.method == "GET":
        user_id = request.args.get("user_id")
        result = donation.list_donations(user_id)
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200
    elif request.method == "POST":
        application.logger.info("/donations-user/ %s" % (request.method))
        content = request.json
        application.logger.info(" request body - %s" % (content))
        user_id = content["user_id"]
        del content["user_id"]
        result = donation.create_donation(user_id=user_id, **content)
        application.logger.info("result %s" % (result))
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200

    elif request.method == "DELETE":
        application.logger.info("/donations-user/ %s" % (request.method))
        donation_user_id = request.args.get("doantion_user_id", type=int)
        result = donation.remove_donation(donation_user_id=donation_user_id)
        response = {}
        if result:
            response["message"]= "Doacao removida com sucesso."
        else:
            response["maessage"]= "Erro ao remover a doacao"
        resp = flask.request(json.dumps(response))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200

@application.route("/donations-institution/", methods=["GET", "POST"])
def process_donation_institution():
    donation_insitution = DonationInstitutionController()
    if request.method == "GET":
        application.logger.info("/donations-institution/ %s" % (request.method))
        institution_id = request.args.get("institution_id", type=int)
        application.logger.info("result params %s" % (institution_id))
        result = donation_insitution.list_user_donation(institution_id=institution_id)
        application.logger.info("result %s" % (result))
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200
    elif request.method == "POST":
        application.logger.info("/donations-institution/ %s" % (request.method))
        content = request.json
        application.logger.info("result params %s" % (content))
        result = donation_insitution.ativate_donation(donation_user_id=content["donation_user_id"],
                                                      institution_id=content["institution_id"])
        application.logger.info("result %s" % (result))
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200


@application.route("/donations-institution/withdraw/", methods=["POST"])
def withdraw_donation():
    donation_institution = DonationInstitutionController()
    if request.method == "POST":
        application.logger.info("/donations-institution/withdraw/ %s" % (request.method))
        content = request.json
        application.logger.info("result content %s" % (content))
        result = donation_institution.withdraw_donation(institution_id=content["institution_id"],
                                                        donation_user_id=content["donation_user_id"],
                                                        date_withdraw=content["date_withdraw"])
        application.logger.info("result %s" % (result))
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200

@application.route("/stock/", methods=["GET", "POST"])
def process_stock():
    stock = StockInstitution()
    if request.method == "GET":
        application.logger.info("/stock/ %s" % (request.method))
        institution_id = request.args.get("institution_id", type=int)
        donation_type_id = request.args.get("donation_type_id")
        result = stock.get_balance(donation_type_id=donation_type_id, institution_id=institution_id)
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200
    elif request.method == "POST":
        application.logger.info("/stock/ %s" % (request.method))
        content = request.json
        result = stock.withdraw_stock(institution_balance_id=content["institution_balance_id"],
                                      date_out=content["date_out"], amount_out=content["amount_out"])
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200


@application.route("/unit/", methods=["GET"])
def process_unit():
    unit = UnitController()
    if request.method == "GET":
        application.logger.info("/unit/ - %s" % (request.method))
        result = unit.list_units()
        application.logger.info("result - %s" % (result))
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200

@application.route("/donation-type/", methods=["GET"])
def process_donation_type():
    donation_type = DonationTypeController()
    if request.method == "GET":
        application.logger.info("/donation-type/ - %s" % (request.method))
        result = donation_type.list_donation_types()
        application.logger.info("result - %s" % (result) )
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200

@application.route("/donation-type-details/", methods=["GET"])
def process_donation_type_details():
    donation_type_details = DonationTypeDetailsController()
    if request.method == "GET":
        application.logger.info("/donation-type-details/ - %s" % (request.method))
        result = donation_type_details.list_donation_type_details()
        application.logger.info("result %s" % (result))
        resp = flask.Response(json.dumps(result))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200


if __name__ == '__main__':
    application.debug = True
    application.run(host=os.getenv("HOST_ADDRESS"), port=os.getenv("HOST_PORT"))
