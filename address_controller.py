import json

from pony.orm import *

from app.db import City, Country, State

class Address():

    @db_session
    def query_countries(self, query=None):
        if query:
            result = select(country for country in Country if country.country.lower().startswith(query) )
        else:
            result = select(country for country in Country)
        result_json = json.dumps([{"id": i.country_id, "name": i.country} for i in result])
        return result_json

    @db_session
    def query_states(self, country_id, query=None):
        country = Country.get(country_id=country_id)
        if query:
            result = select(state for state in State if state.country_id == country and state.state.lower().startswith(query))
        else:
            result = select(state for state in State if state.country_id == country )
        result_json = json.dumps([{"id": i.state_id, "name": i.state} for i in result])
        return result_json

    @db_session
    def query_cities(self, state_id, query=None):
        state = State.get(state_id=state_id)
        if query:
            result = select(city for city in City if city.state_id == state and city.city.lower().startswith(query))
        else:
            result = select(city for city in City if city.state_id == state)
        result_json = json.dumps([{"id": i.city_id, "name": i.city} for i in result])
        return result_json

    @db_session
    def get_state(self, id):
        return State.get(state_id=id).state

    @db_session
    def get_city(self, id):
        city = City.get(city_id=id)
        return {"state": city.state_id, "city": city}

#TODO fazer testes unitarios
