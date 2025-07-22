def normalize_score(score, max_score):
    if max_score == 0:
        return 0
    else:
        return score / max_score

def get_urgency_score(urgency_level):
    weights = {"low": 1, "medium": 2, "high": 3}
    return weights.get(urgency_level, 1)

@login_required(login_url="login")
def booking(request, pk):
    # Check if there are already 4 appointments for this date and time
    try:
        existing_appointments = Appointment.objects.filter(healthcenter=healthcenter, date=transformed_date, time=time).count()
        if existing_appointments >= 4:
            # Calculate raw scores
            age_score_raw = patient.age
            urgency_score_raw = get_urgency_score(patient.urgency)
            no_show_score_raw = patient.no_shows
            cancellations_score_raw = patient.cancellations
            waitlist_time_raw = (datetime.datetime.now() - Waitlist.objects.filter(patient=patient).first().timestamp).days

            # Calculate maximum possible scores
            max_age_score = Patient.objects.annotate(
                percent_rank=CumeDist('age') 
            ).filter(
                percent_rank__gte=0.95
            ).order_by(
                'age'
            ).first().age
            max_urgency_score = Urgency.objects.all().order_by('-value').first().value 
            max_no_show_score = Patient.objects.all().order_by('-no_show').first().value 
            max_cancellations_score = Patient.objects.all().order_by('-cancellations').first().value 
            max_waitlist_time = (datetime.datetime.now() - Waitlist.objects.all().order_by('timestamp').first().timestamp).days

            # Normalize scores
            if patient.age <= 18:
                age_score = normalize_score(age_score_raw, max_age_score) * 1.5
            elif patient.age <= 60:
                age_score = normalize_score(age_score_raw, max_age_score)
            else:
                age_score = normalize_score(age_score_raw, max_age_score) * 2

            urgency_score = normalize_score(urgency_score_raw, max_urgency_score) * 2  # Multiply by 2 to give urgency a higher weight
            no_show_score = normalize_score(no_show_score_raw, max_no_show_score) * -1  # Negate to penalize frequent no-shows
            cancellations_score = normalize_score(cancellations_score_raw, max_cancellations_score) * -1  # Negate to penalize frequent cancellations
            waitlist_score = normalize_score(waitlist_time_raw, max_waitlist_time) #reward patient with long waiting time

            heuristic_score = urgency_score + no_show_score + cancellations_score + waitlist_score + age_score


            # Add patient to the waitlist
            waitlist_entry = Waitlist(patient=patient, healthcenter=healthcenter, desired_date=transformed_date, desired_time=time, score=heuristic_score)
            waitlist_entry.save()

            messages.info(request, 'This time slot is already full. You have been added to the waitlist.')
            return redirect('booking', pk=pk)
        
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment does not exist.')
        return redirect('booking', pk=pk)

    except Patient.DoesNotExist:
        messages.error(request, 'Patient does not exist.')
        return redirect('booking', pk=pk)

#Run reschedule appointments if there is a cancellation/no show from a patient
def reschedule_appointments():
    try:
        # Find all open slots
        open_slots = Appointment.objects.filter(patient=None)

        # For each open slot, find the highest-scoring patient on the waitlist
        for slot in open_slots:
            # Also filter by required service and desired time
            best_candidate = Waitlist.objects.filter(healthcenter=slot.healthcenter, desired_time=slot.time).order_by('-score', 'timestamp').first()
        
            slot.patient = best_candidate.patient
            slot.save()
            best_candidate.delete()

    except Appointment.DoesNotExist:
        # Handle Appointment.DoesNotExist exception
        pass

    except Waitlist.DoesNotExist:
        # Handle Waitlist.DoesNotExist exception
        pass