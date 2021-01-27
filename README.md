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

1. Creates events in class calendar for the subjects assigned in timetable
2. Add events in teacher calendar for those who are involved in handling the sessions. Class calendar events are linked to the teacher calendar event

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

```
{
	"request_type":"TIMETABLE_TO_CALENDAR_GEN",
	"time_table_key":"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"academic_year":"2020-2021"
}


```


### 2.Calendar to lessonplan integration

When calendars is created, it is used to generate lessonplans of each subjects

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

```
{
	"request_type":"CALENDAR_TO_LESSON_PLAN_GEN",
	"class_info_key":"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"division":"A"
}


```

### 3.Timetable to lessonplan integration

When timetable is created, it is used to generate class calendars and employee calendars and lessonplans

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

```
{
	"request_type":"TIMETABLE_CALENDAR_LESSON_PLAN_GEN",
	"timetable_key":"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"academic_year" : "2020-2021"
}


```

### 4.Add class session event integration

We can add more class session events to class calendar ,it is used to update teacher calendars and lessonplans 

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

```
{
	"request_type":"CLASS_SESSION_EVENT_SYNC",
	"calendar_key":"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"events":[
			{
	      		"event_code": "event-8" 
		    },
		    {
		    	"event_code": "event-9" 
		    }
		]
}


```

### 5.Add holiday event integration

We can make an event as holiday( no class ),it is used to update teacher calendars and lessonplans 

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

```
{
	"request_type":"HOLIDAY_LESSONPLAN_SYNC",
	"calendar_key":"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"event_code": "cbvchv"
}


```

### 6.Remove holiday event integration

We can remove a holiday event from calendar(may be school calendar or class calendar ),it is used to update teacher calendars and lessonplans 

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

```
{
	"request_type":"REMOVE_EVENT_LESSONPLAN_SYNC",
	"calendar_key":"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"events":[
				  {
				      "event_code": "cf78e5",
				      "event_type": "CLASS_SESSION",
				      "from_time": "2020-05-22T10:00:00",
				      "to_time": "2020-05-22T10:40:00",
				      "params": [
			               {
			                  "key" :"cancel_class_flag",
			                  "value" : "true"
			               }
			            ],
        				"to_time":"2020-08-04T10:40:00"
				    }
				]
}


```
### 7.Update period integration

We can update a period (subject changing with teacher ) ,it is used to update class calendars,teacher calendars and lessonplans 

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

```
{
	"request_type":"PERIOD_UPDATE_SYNC",
	"time_table_key":"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"period_code" :" hcghywu99"
}


```

### 8.Update subject teacher integration

We can update subject teacher ( teacher is changing with out subject )  ,it is used to update class calendars,teacher calendars, and timetables 

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

```
{
	"request_type":"UPDATE_SUBJECT_TEACHER_SYNC",
	"division" :"A",
	"class_info_key":"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"subject_code" :" bio-1",
	"existing_teacher_emp_key":"0016112155079559146EEE03DF-752",
	"new_teacher_emp_key" :"0016112155079559146EEE03DF-752"
}


```

### 9.Add exam integration

We can add an exam in the calendar,it is used to update class calendars,teacher calendars, and lessonplans

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

```

{
	"request_type":"EXAM_CALENDAR_SYNC",
	"division" :"A",
	"class_info_key":"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"series_code" :" bio-1"
}


```

### 10.Cancel exam integration

We can cancel series of exam ,it is used to update class calendars,teacher calendars, and lessonplans

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

```

{
	"exam_series":[{"code":"Apretncj7","classes":[{"division":"B","class_key":"001610357616442257365E3740-01D7-4920-BDA7-0BC669CDCFCA-168810859"}],"name":"April-exam-test"}],
	"request_type":"EXAM-DELETE-SYNC",
	"academic_year":"2020-2021",
	"school_key":"1e4d12bc2b58050ff084f8da"
}


```
### 11.Update exam integration

We can update an exam in the calendar,it is used to update class calendars,teacher calendars, and lessonplans

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

```

{
	"request_type":"EXAM_UPDATE_CALENDAR_SYNC",
	"division" :"A",
	"class_info_key":"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"series_code" :" bio-1"
}


```

### 12.Add leave integration

We can add leave for a teacher,it is reflecting on class calendars,teacher calendars, and lessonplans

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

```

{
	"request_type":"TEACHER_LEAVE_SYNC",
	"leave_key" :"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534"
	
}


```
### 13.Cancel leave integration

We can cancel a leave of a teacher,it is reflecting on class calendars,teacher calendars, and lessonplans

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

```

{
	"request_type":"TEACHER_LEAVE_CANCEL",
	"leave_key" :"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534"
	
}


```
### 14.Teacher substitution integration

We can substitute another teacher when a teacher taking leave , it is reflecting on class calendars,teacher calendars, and lessonplans

#### Trigger source

SQS queue

https://sqs.us-west-2.amazonaws.com/272936841180/academic-integrator-q.fifo

#### Request Format

Here is request format of two types :-

1) First time substitution

```

{
	"request_type":"TEACHER_SUBSTITUTE_SYNC",
	"calendar_key" : "0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"leave_key" :"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"event_code" : "ryfuy24",
	"substitution_emp_key" :"5079559146EEE03DF-752B-4AA5-9690-0EE"
}


```
1) Resubstitution

```

{
	"request_type":"TEACHER_SUBSTITUTE_SYNC",
	"calendar_key" : "0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"leave_key" :"0016112155079559146EEE03DF-752B-4AA5-9690-0EED878BEBC1-672163534",
	"event_code" : "ryfuy24",
	"substitution_emp_key" :"5079559146EEE03DF-752B-4AA5-9690-0EE",
	"previous_substitution_emp_key" : "146EEE03DF-752B-4AA5-9690-0EED8",
	"previous_substitution_subject_code" : "bio3"
}


```

