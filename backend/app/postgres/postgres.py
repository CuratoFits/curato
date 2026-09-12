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