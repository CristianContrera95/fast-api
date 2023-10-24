MONGO_SERVER=mongodb://40.87.50.238:27017/ \
SQL_DRIVER='{ODBC Driver 17 for SQL Server}' \
SQL_SERVER=folpix-eus-sdb01.database.windows.net \
SQL_DATABASE=folpix-eus-db01 \
SQL_USER=folpix-2020 \
SQL_PASS=PiData20! \
DATABASE_NAME=piconsulting \
MONGO_USER=folpix-user \
MONGO_PWD=pidata2020 \
STORAGE_FRAMES=folpixeusstorage \
API_CLIENT_SECRET="supersecretshh" \
env/bin/python3 scripts/seed_events.py