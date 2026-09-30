
from sqlalchemy import Select

from app.agents.demographicFilter import DemographicFilter

class PostgresHandler:
    def __init__(self, db_config):
        self.db_config = db_config
        
    def send_to_postgres(event_json):
        try:
            # Import the function to insert data into PostgreSQL
            from app.postgres import insert_event_to_postgres
            insert_event_to_postgres(event_json)
        except Exception as e:
            print(f"Error at send_to_postgres: {e}")
            
    def get_events_from_postgres(self, user_id):
        try:
            # Import the function to fetch data from PostgreSQL
            from app.postgres import fetch_events_from_postgres
            return fetch_events_from_postgres(user_id)
        except Exception as e:
            print(f"Error at get_events_from_postgres: {e}")
            return []
        
    def get_user_profile_from_postgres(self, user_id):
        try:
            return PostgresHandler.fetch_user_profile_from_postgres(user_id)
        except Exception as e:
            print(f"Error at get_user_profile_from_postgres: {e}")
            return None
        
    def search_demographic_users_ids(self,current_user_demographics):
        similar_users=[]
        user_age = current_user_demographics.get("age")
        user_gender = current_user_demographics.get("gender")
        user_city = current_user_demographics.get("city")
        user_state = current_user_demographics.get("state")
        user_country = current_user_demographics.get("country")
        try:
            query = """
                SELECT user_id
                FROM user_profiles
                WHERE age = %s
                OR gender = %s
                OR city = %s
                OR state = %s
                OR country = %s
                LIMIT 10
                """

            return PostgresHandler.fetch_users_by_demographics(query,(user_age, user_gender, user_city, user_state, user_country))

        except Exception as e:
            print(f"Error at search_demographic_users: {e}")
            return []