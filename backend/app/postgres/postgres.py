def send_to_postgres(event_json):
    try:
        # Import the function to insert data into PostgreSQL
        from app.postgres import insert_event_to_postgres
        insert_event_to_postgres(event_json)
    except Exception as e:
        print(f"Error at send_to_postgres: {e}")