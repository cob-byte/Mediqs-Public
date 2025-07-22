from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django_apscheduler.models import DjangoJobExecution
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from doctor.models import Appointment
from notifications.signals import notify
from doctor.views import reschedule
from django_apscheduler import util
from django.utils import timezone
from datetime import time

import sys
import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
  DjangoJobExecution.objects.delete_old_job_executions(max_age)

def send_first_notification():
    try:
        # Get the appointments scheduled for 24 hours from now
        tomorrow = timezone.now() + timedelta(days=1)
        appointments = Appointment.objects.filter(date=tomorrow.date(), confirmed=False)

        # For each appointment, send a notification to the patient
        for appointment in appointments:
            notify.send(appointment.healthcenter, recipient=appointment.patient.user, verb='Your appointment is tomorrow', 
                        description=f'You have an appointment tomorrow at {appointment.time}. Please confirm or cancel as necessary.', 
                        redirect=f'/confirm-appointment/{appointment.id}', icon='calendar', appointment=appointment.id)
    except Exception as e:
        # Handle the exception and log the error
        print(f"An error occurred during job execution: {str(e)}", file=sys.stdout)

def send_second_notification():
    try:
        # Get the appointments scheduled for 3 hours from now
        soon = timezone.now() + timedelta(hours=3)
        appointments = Appointment.objects.filter(date=soon.date(), confirmed=False)

        # Filter appointments by time slot
        for appointment in appointments:
            # Convert the start of the time slot to a datetime object
            appointment_time = datetime.strptime(appointment.time.split(" - ")[0], "%I:%M %p")
            # If the appointment is within 3 hours, send a notification
            if soon.time() <= appointment_time.time() <= (soon + timedelta(hours=1)).time():
                notify.send(appointment.healthcenter, recipient=appointment.patient.user, verb='Your appointment is in 3 hours', 
                            description=f'You have an appointment in 3 hours at {appointment.time}. Please confirm or cancel as necessary.', 
                            redirect=f'/confirm-appointment/{appointment.id}', icon='calendar', appointment=appointment.id)
    except Exception as e:
        # Handle the exception and log the error
        print(f"An error occurred during job execution: {str(e)}", file=sys.stdout)

def check_and_reschedule():
    try:
        # Get the current time and the time for one hour later
        now = timezone.now()
        one_hour_later = now + timedelta(hours=1)

        # Get the appointments scheduled for today and which are not confirmed yet
        appointments = Appointment.objects.filter(date=now.date(), confirmed=False)

        # Filter appointments by time slot and reschedule unconfirmed appointments
        for appointment in appointments:
            # Convert the start of the time slot to a datetime object
            appointment_start_time = datetime.strptime(appointment.time.split(" - ")[0], "%I:%M %p").time()

            # Create datetime objects for the start and end of the appointment
            appointment_start = datetime.combine(now.date(), appointment_start_time)
            appointment_end = appointment_start + timedelta(hours=1)

            # Convert naive datetime objects to timezone-aware objects
            appointment_start = timezone.make_aware(appointment_start)
            appointment_end = timezone.make_aware(appointment_end)

            # If the current time is within 1 hour of the start of the appointment
            if now <= appointment_start <= one_hour_later:
                appointment.appointment_status = "unconfirmed"
                appointment.save()

                # Send notification about the status change
                notify.send(appointment.healthcenter, recipient=appointment.patient.user, verb='Your appointment status is unconfirmed',
                            description='Your appointment status has been marked as unconfirmed due to no response to our confirmation request. We are sorry for any inconvenience it may cause.',
                            redirect=f'/patient-dashboard/', icon='calendar', appointment=appointment.id)

                reschedule(appointment)
    except Exception as e:
        # Handle the exception and log the error
        print(f"An error occurred during job execution: {str(e)}", file=sys.stdout)
    
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Create a trigger for the first notification that runs every day at 12:00 PM
    first_notification_trigger = CronTrigger(hour=12, minute=0)
    scheduler.add_job(send_first_notification, first_notification_trigger, id='send_first_notification', name='send_first_notification', replace_existing=True, misfire_grace_time=160, coalesce=False, max_instances=1)

    # Create a trigger for the second notification that runs every 3 hours, starting at 12:00 AM
    second_notification_trigger = CronTrigger(hour='0-23/3', minute=0)
    scheduler.add_job(send_second_notification, second_notification_trigger, id='send_second_notification', name='send_second_notification', replace_existing=True, misfire_grace_time=160, coalesce=False, max_instances=1)

    # Create a trigger for rescheduling check that runs every 30 minutes, starting at 12:00 AM
    check_reschedule_trigger = CronTrigger(hour='0-23', minute='0/30')
    scheduler.add_job(check_and_reschedule, check_reschedule_trigger, id='check_and_reschedule', name='check_and_reschedule', replace_existing=True, misfire_grace_time=160, coalesce=False, max_instances=1)

    register_events(scheduler)
    try:
        scheduler.start()
        print("Scheduler started...", file=sys.stdout)
    except (KeyboardInterrupt, SystemExit):
        print("Something went wrong...", file=sys.stdout)
        scheduler.shutdown()
        pass