PASSW = test
HOS = localhost
USE = postgres


runcont:
	sudo docker run --rm --name pg-docker -e POSTGRES_PASSWORD=$(PASSW) -d -p 5432:5432 postgres
	sleep 10
	PGPASSWORD=$(PASSW) psql -h $(HOS) -U $(USE) -c "CREATE DATABASE dbtoy;"
	PGPASSWORD=$(PASSW) psql -h $(HOS) -U $(USE) -d dbtoy -c "CREATE TABLE sample (sample_num integer PRIMARY KEY,dim_1 real,dim_2 real,dim_3 real,dim_4 real,dim_5 real);"
	PGPASSWORD=$(PASSW) psql -h $(HOS) -U $(USE) -d dbtoy -c "CREATE TABLE label (sample_num integer REFERENCES sample (sample_num),sample_type integer,sample_type_binary integer,PRIMARY KEY (sample_num));"
	
	python3 dataConn.py 



# PGPASSWORD=test psql -h localhost -U postgres -c "\l"
# PGPASSWORD=test psql -h localhost -U postgres -d dbtoy -c "SELECT * FROM sample;"

	



	


