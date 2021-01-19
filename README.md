academic-integrator
===================

academic integration code

### Running tests

Running a specific test

> python3 -m unittest tests.unit.test_TimetableIntegrator

Running all tests

> python3 -m unittest discover <test_folder>

Installing packages for lambda deployment
=============================================

pip3 install --target ./packages requests --system

Note :

--system may not be required on all systems


Supported Operations
======================

### 1. Timetable to calendar integration

When timetable is created, it is used to generate class calendars and employee calendars

#### Trigger source

SQS queue

#### Request Format

```
{

}

```
