from multiprocessing import context
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from doctor.views import appointments
from healthcenter.models import Healthcenter_Information
from .models import chatMessages, ChatSession
from django.contrib.auth import get_user_model
from healthcenter.models import User as UserModel
from healthcenter.models import Patient
from doctor.models import Doctor_Information, Appointment, Walkin  
from django.db.models import Q
import json,datetime
from django.core import serializers
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from notifications.signals import notify
from notifications.models import Notification
from django.utils import timezone
from datetime import timedelta

# Create your views here.

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request,pk):
    if request.user.is_patient:
            User = get_user_model()
            users = User.objects.all()
            patients = Patient.objects.get(user_id=pk)
            appointments = Appointment.objects.filter(patient=patients).filter(appointment_status='confirmed')
            health_centers = Healthcenter_Information.objects.filter(appointment__in=appointments)
            doctor = Doctor_Information.objects.filter(health_center__in=health_centers)

            chats = {}
            if request.method == 'GET' and 'u' in request.GET:
                # chats = chatMessages.objects.filter(Q(user_from=request.user.id & user_to=request.GET['u']) | Q(user_from=request.GET['u'] & user_to=request.user.id))
                chats = chatMessages.objects.filter(Q(user_from=request.user.id, user_to=request.GET['u']) | Q(user_from=request.GET['u'], user_to=request.user.id))
                chats = chats.order_by('date_created')
                doc = Doctor_Information.objects.get(user_id=request.GET['u'])
                
                context = {
                "page":"home",
                "users":users,
                "chats":chats,
                "patient":patients,
                "doctor":doctor,
                "doc":doc,
                "app":appointments,
                
                "chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
            }
            elif request.method == 'GET' and 'search' in request.GET:
                query = request.GET.get('search')
                doctor= Doctor_Information.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))
                #chats = chatMessages.objects.filter(Q(user_from=request.user.id, user_to=request.GET['u']) | Q(user_from=request.GET['u'], user_to=request.user.id))
                #chats = chats.order_by('date_created')
                #doc = Doctor_Information.objects.get(username=request.GET['search'])
                context = {
                "page":"home",
                "users":users,
                
                "patient":patients,
                
                "doctor":doctor,
                
            }
            else:
            
            
                context = {
                    "page":"home",
                    "users":users,
                    "chats":chats,
                    "patient":patients,
                    "doctor":doctor,
                    "app":appointments,
                    "chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
                }
            return render(request,"chat.html",context)
    elif request.user.is_doctor:
            User = get_user_model()
            users = User.objects.all()
            #patients = Patient.objects.all()
            doctor = Doctor_Information.objects.get(user_id=pk)
            healthcenter = Healthcenter_Information.objects.get(healthcenter_id=doctor.health_center.healthcenter_id)
            appointment_patients = set(Appointment.objects.filter(healthcenter=healthcenter, appointment_status='confirmed').values_list('patient', flat=True))
            walkin_patients = set(Walkin.objects.filter(healthcenter=healthcenter).values_list('patient', flat=True))
            unique_patients = appointment_patients.union(walkin_patients)
            patients = Patient.objects.filter(patient_id__in=unique_patients)

            chats = {}
            if request.method == 'GET' and 'u' in request.GET:
                # chats = chatMessages.objects.filter(Q(user_from=request.user.id & user_to=request.GET['u']) | Q(user_from=request.GET['u'] & user_to=request.user.id))
                chats = chatMessages.objects.filter(Q(user_from=request.user.id, user_to=request.GET['u']) | Q(user_from=request.GET['u'], user_to=request.user.id))
                chats = chats.order_by('date_created')
                pat = Patient.objects.get(user_id=request.GET['u'])
                
                context = {
                "page":"home",
                "users":users,
                "chats":chats,
                "patient":patients,
                "doctor":doctor,
                "pat":pat,
                "app":unique_patients,
                
                "chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
            }
            elif request.method == 'GET' and 'search' in request.GET:
                query = request.GET.get('search')
                patients= Patient.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))
                #chats = chatMessages.objects.filter(Q(user_from=request.user.id, user_to=request.GET['u']) | Q(user_from=request.GET['u'], user_to=request.user.id))
                #chats = chats.order_by('date_created')
                #doc = Doctor_Information.objects.get(username=request.GET['search'])
                context = {
                "page":"home",
                "users":users,
                
                "patient":patients,
                "app":unique_patients,
                "doctor":doctor,
                
            }
            
                
            
            else:
            
                context = {
                    "page":"home",
                    "users":users,
                    "chats":chats,
                    "patient":patients,
                    "doctor":doctor,
                    "chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
                }
            return render(request,"chat-doctor.html",context)

@csrf_exempt
@login_required
def profile(request):
    context = {
        "page":"profile",
    }
    return render(request,"chat/profile.html",context)

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_messages(request):
    chats = chatMessages.objects.filter(Q(id__gt=request.POST['last_id']),Q(user_from=request.user.id, user_to=request.POST['chat_id']) | Q(user_from=request.POST['chat_id'], user_to=request.user.id))
    new_msgs = []
    for chat in list(chats):
        data = {}
        data['id'] = chat.id
        data['user_from'] = chat.user_from.id
        data['user_to'] = chat.user_to.id
        data['message'] = chat.message
        data['date_created'] = chat.date_created.strftime("%b-%d-%Y %H:%M")
        new_msgs.append(data)
    return HttpResponse(json.dumps(new_msgs), content_type="application/json")

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def send_chat(request):
    resp = {}
    User = get_user_model()
    if request.method == 'POST':
        post = request.POST
        u_from = User.objects.get(id=post['user_from'])
        u_to = User.objects.get(id=post['user_to'])

        # Get or create a chat session for these two users
        chat_session, created = ChatSession.objects.get_or_create(
            defaults={'user_one': u_from, 'user_two': u_to},
            **({f'user_one': u_from, 'user_two': u_to} if ChatSession.objects.filter(Q(user_one=u_from, user_two=u_to) | Q(user_one=u_to, user_two=u_from)).exists() else {'user_one': u_from, 'user_two': u_to})
        )

        # Get the chat message from the POST data
        message = post['message'].strip()  # Remove leading/trailing whitespaces

        # Check if the message is not blank
        if not message:
            resp['status'] = 'failed'
            resp['mesg'] = 'Message cannot be blank.'
            return HttpResponse(json.dumps(resp), content_type="application/json")

        insert = chatMessages(user_from=u_from, user_to=u_to, message=post['message'], chat_session=chat_session)

        try:
            # If the chat session is newly created or the last message was more than 30 minutes ago, send a notification
            if created or timezone.now() - chat_session.last_message_time > timedelta(minutes=30):
                verb = f'You have a new message'
                description = f'You have a new message from {u_from.first_name}.'
                redirect_url = f'/chat/home/{u_to.id}/?u={u_from.id}'
                icon = 'chatbox-ellipses-outline'
                notify.send(u_from, recipient=u_to, verb=verb, description=description, redirect=redirect_url, icon=icon)

                insert.notified = True # set notified to true for this message

            chat_session.last_message_time = timezone.now()  # Update the last message time
            chat_session.save()

            insert.save()
            resp['status'] = 'success'
        except Exception as ex:
            resp['status'] = 'failed'
            resp['mesg'] = str(ex)
    else:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")