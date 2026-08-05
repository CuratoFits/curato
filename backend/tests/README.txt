Copy the contents of this tests folder into backend/tests/.

Activate the project environment:
.\.venv\Scripts\Activate.ps1

Verify:
python -c "import sys; print(sys.executable)"

Run:
python -m pytest -v

test_database.py is a live Supabase integration test and requires DATABASE_URL in .env.
The repository, service, and route tests use mocks/fakes and do not write to Supabase.
