from academics.calendar.CalendarLessonPlanIntegrator import remove_calendar_lessonplan_integration
import boto3

school_key = "1e4d12bc2b58050ff084f8da"
academic_year = "2022-2023"
remove_calendar_lessonplan_integration(school_key, academic_year)