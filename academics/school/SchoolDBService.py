import boto3
from boto3.dynamodb.conditions import Key, Attr
import academics.school.School as scl
SCHOOL = 'School'

def add_or_update_school(school):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table(SCHOOL)
	response = table.put_item(
		Item = school
	)
	return response

def get_school(school_key):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table(SCHOOL)
	response = table.get_item(
		Key={
		'school_id':school_key
	  }
	)
	if response['Item'] is not None:
		return scl.School(response['Item'])

