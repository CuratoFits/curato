from app.connections.connection import SessionLocal
from app.models.user import UserProfile
from app.models.interactions_events import InteractionEvent

class PostgresHandler:

    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def get_events_from_postgres(self, user_id: int):
        try:
            events = self.db.query(InteractionEvent).filter(InteractionEvent.user_id == user_id).all()
            return events
        except Exception as e:
            print(f"Error at get_events_from_postgres: {e}")
            return []
    
    def get_current_interaction_events(self, user_id: int, limit: int = 20)-> list[InteractionEvent]:
        try:
            events = self.db.query(InteractionEvent).filter(
                InteractionEvent.user_id == user_id
            ).order_by(
                InteractionEvent.timestamp.desc()
            ).limit(limit).all()

            return events

        except Exception as e:
            print(f"Error at get_current_interaction_events: {e}")
            return []
    
    def get_user_profile_from_postgres(self, user_id: int):
        try:
            user_profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            return user_profile
        except Exception as e:
            print(f"Error at get_user_profile_from_postgres: {e}")
            return None

    def search_demographic_users_ids(self, current_user_demographics: dict):
        user_age = current_user_demographics.get("age")
        user_gender = current_user_demographics.get("gender")
        user_city = current_user_demographics.get("city")
        user_state = current_user_demographics.get("state")
        user_country = current_user_demographics.get("country")

        try:
            query = self.db.query(UserProfile.user_id).filter(
                (UserProfile.age == user_age) |
                (UserProfile.gender == user_gender) |
                (UserProfile.city == user_city) |
                (UserProfile.state == user_state) |
                (UserProfile.country == user_country)
            )

            return [user_id for (user_id,) in query.all()]

        except Exception as e:
            print(f"Error at search_demographic_users_ids: {e}")
            return []

    def close(self):
        self.db.close()