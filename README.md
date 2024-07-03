# maadb-2024

## Project Description

This repository contains the project implementation for the "Advanced Models and Architectures for Databases" course from the University of Turin.

The Project consists in the implementation of a Event creation and ticket selling backend with the following requirements:

- The application has to allow business users to store and publish events. business users may define events through a different schema having some common parts. All events should have a capability of customers by day and start end date and a name.

- Customers User can buy tickets for events, multiple Customers may try to buy tickets at same time and can register on the system to take eventual discounts on the base of accumulated rewards based on the events attended.

- A business user may be interested to analyze events performances for defining the location planning. Other customer users may be interested to check their profile for seeing accumulated rewards and list of attended events.

The project showcases the polyglot usage of nosql database such as Cassandra, MongoDB and redis.

# Run the project

### Initialize databases:
```bash
docker compose up 
```
Initialization may take a wile due to the health checks in the cassandra nodes.

### Run the backend application:
Create a venv then:
```bash
pip install -f requirements.txt
uvicorn src.main:app --reload # dev mode
# may require restart if cassandra containers are not up
# http://localhost:8000/docs has endpoint documentation
```

### Run Load tests
```bash
locust --autostart -u 1000 -t 1m -r 100 -f test/locustfile.py
# run with 1000 users for 1 minute spawning 100 users per second
locust test/locustfile.py
# both commands starts a ui on port 8089, this command doesn't start the test automatically
# to run the tests one by one (or any combination) comment the unwanted imported tests in test/locustfile.py
```


