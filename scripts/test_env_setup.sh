cd test
export MONGO_SERVER=mongodb://localhost:27017/ \
SQL_DRIVER='{ODBC Driver 17 for SQL Server}' \
SQL_SERVER=127.0.0.1 \
SQL_DATABASE=folpix_test \
SQL_USER=SA \
SQL_PASS=PiData20! \
API_CLIENT_SECRET="supersecretshh"
docker-compose up -d
echo 'Setting up test database servers ...'
sleep 10
echo 'Creating test databases ...'
docker exec test_sqlserver /opt/mssql-tools/bin/sqlcmd -U SA -P $SQL_PASS -q "CREATE DATABASE ${SQL_DATABASE};"
docker exec test_mongodb mongo --eval 'db.createUser({ user: "folpix-user" , pwd: "pidata2020", roles: []})' piconsulting
echo 'ENVIRONMENT READY.'