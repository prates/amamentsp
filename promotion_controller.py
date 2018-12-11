from datetime import datetime
import json

from pony.orm import select, commit, db_session

from app.db import Promotion, Institution
from app.institution_controller import CRUDInstitution


class ControllerPromotion():


    @db_session
    def get_promotion(self, promotion_id):
        inst_ctrl = CRUDInstitution()
        promotion = Promotion.get(promotion_id=promotion_id)
        promotion_dict = {"promotion_id": promotion.promotion_id,
                          "title": promotion.title, "description": promotion.description, "link": promotion.link,
                          "date_initial": promotion.date_initial.strftime("%d/%m/%Y"),
                          "date_end": promotion.date_end.strftime("%d/%m/%Y")}
        inst = inst_ctrl.get_institution(institution_id=promotion.institution_id.institution_id, export_json=False)
        promotion_dict.update(inst)
        return promotion_dict

    @db_session
    def list_all_promotion(self, size=10):
        promotions = select(promotion for promotion in Promotion if promotion.date_end > datetime.now())[:size]
        promotions_list = []
        for promotion in promotions:
            promotion_dict = self.get_promotion(promotion_id=promotion.promotion_id)
            promotions_list.append(promotion_dict)
        return promotions_list

    @db_session
    def create_promotion(self, institution_id, **kwargs):
        inst = Institution.get(institution_id=institution_id)
        date_initial = datetime.strptime(kwargs["date_initial"], "%d/%m/%Y")
        date_end = datetime.strptime(kwargs["date_end"], "%d/%m/%Y")
        del kwargs["date_initial"]
        del kwargs["date_end"]
        promotion = Promotion(institution_id=inst, date_initial=date_initial, date_end=date_end, **kwargs)
        promotion.flush()
        promotion_dict = self.get_promotion(promotion_id=promotion.promotion_id)
        commit()
        return promotion_dict

    @db_session
    def alter_promotion(self, promotion_id, **kwargs):
        promotion = Promotion.get(promotion_id=promotion_id)
        status = "OK"
        if promotion is None:
            status = "NOTFOUND"
            return {"result": {"message": "promotion not found"}, "status": status}
        else:
            promotion.set(**kwargs)
            commit()
            promotion_dict = self.get_promotion(promotion_id=promotion_id)
            return {"status": "OK", "result": promotion_dict}

    @db_session
    def delete_promotion(self, promotion_id):
        try:
            promotion = Promotion.get(promotion_id=promotion_id)
            promotion.delete()
            commit()
            return True
        except Exception as ex:
            print(ex)
            return False