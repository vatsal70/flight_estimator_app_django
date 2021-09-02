from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import datetime
from django.contrib import messages
from datetime import date
from database_app.models import *
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test, login_required, user_passes_test

# Custom decorators
def dec_func(user):
    if user.is_superuser == True:
        return user
    return None

user_login_required = user_passes_test(dec_func, login_url='/authentication_required/')

def active_user_required(view_func):
    decorated_view_func = login_required(user_login_required(view_func))
    return decorated_view_func


with open('static/random_forest_model.pkl', 'rb') as f:
    __model = joblib.load(f)
    
test_data =  pd.read_excel('static/testing data.xlsx')




# Function to convert the various columns and creating new ones.
def conversion_function(dataframe):
  
  # extracting information from 'date_of_journey' column and storing in new columns 'Journey_month' and 'journey_day'
  dataframe['Journey_month'] = pd.to_datetime(dataframe["Date_of_Journey"], format="%d/%m/%Y").dt.month
  dataframe['Journey_day'] = pd.to_datetime(dataframe["Date_of_Journey"], format="%d/%m/%Y").dt.day

  # Extracting Hours from 'Dep_Time' column by creating a new column 'Dep_hour'
  dataframe["Dep_hour"] = pd.to_datetime(dataframe['Dep_Time']).dt.hour

  # Extracting Minutes from 'Dep_Time' column by creating a new column 'Dep_min'
  dataframe["Dep_min"] = pd.to_datetime(dataframe['Dep_Time']).dt.minute

  # Extracting Hours from 'Arrival_Time' column by creating a new column 'Arr_hour'
  dataframe["Arr_hour"] = pd.to_datetime(dataframe['Arrival_Time']).dt.hour

  # Extracting Minutes from 'Arrival_Time' column by creating a new column 'Arr_min'
  dataframe["Arr_min"] = pd.to_datetime(dataframe['Arrival_Time']).dt.minute


  dataframe.drop(["Date_of_Journey", "Dep_Time", "Arrival_Time"], axis=1, inplace=True)
  
  

# Function to convert the duration column to duration in hours and minutes.
def duration_conversion(dataframe):
  duration = list(dataframe["Duration"])
  for i in range(len(duration)):
    if len(duration[i].split()) != 2:    # Check if duration contains only hour or mins
      if "h" in duration[i]:
          duration[i] = duration[i].strip() + " 0m"   # Adds 0 minute
      else:
          duration[i] = "0h " + duration[i]           # Adds 0 hour
  duration_hours = []
  duration_mins = []
  for i in range(len(duration)):
    duration_hours.append(int(duration[i].split(sep = "h")[0]))    # Extract hours from duration
    duration_mins.append(int(duration[i].split(sep = "m")[0].split()[-1]))   # Extracts only minutes from duration
  dataframe.drop(['Duration'], axis=1, inplace=True)
  return duration_hours, duration_mins

# Function to convert the categorial data.

def convert_categorial(dataframe):

  # As Airline column has nominal Categorical data , we will perform One Hot encoding
  Airline = dataframe[["Airline"]]
  #By using the drop_first paramater, it will drop the first column it created to avoid the dummy variable trap.
  Airline = pd.get_dummies(Airline, drop_first=True)


  # as Source column has  nominal categorical data, we will perform OneHotEncoding
  Source = dataframe[["Source"]]
  #By using the drop_first paramater, it will drop the first column it created to avoid the dummy variable trap.
  Source = pd.get_dummies(Source, drop_first=True)


  # as Destination column has  nominal categorical data, we will perform OneHotEncoding
  Destination = dataframe[["Destination"]]
  #By using the drop_first paramater, it will drop the first column it created to avoid the dummy variable trap.
  Destination = pd.get_dummies(Destination, drop_first=True)

  dataframe.drop(["Airline", "Source", "Destination"], axis=1, inplace=True)

  return Airline, Source, Destination










conversion_function(test_data)
test_data['Duration_hours'], test_data['Duration_mins'] = duration_conversion(test_data)
Airline, Source, Destination = convert_categorial(test_data)
data_test = pd.concat([test_data, Airline, Source, Destination],axis=1)
data_test.drop(["Route", "Additional_Info"],axis=1,inplace=True)
# Converting the categorial data for the 'Total_Stops' column.
data_test.replace({"non-stop":0,"1 stop":1,"2 stops":2,"3 stops":3,"4 stops":4},inplace=True)
pd.set_option('display.max_columns',None)



final_airline = [item.split('_')[1] for item in list(Airline.columns)]
final_destination = [item.split('_')[1] for item in list(Destination.columns)]
final_source = [item.split('_')[1] for item in list(Source.columns)]


all_column_names = ['Total_Stops', 'Journey_month', 'Journey_day', 'Dep_hour', 'Dep_min', 'Arr_hour', 'Arr_min', 'Duration_hours', 
                    'Duration_mins', 'Airline_Air India', 'Airline_GoAir', 'Airline_IndiGo', 'Airline_Jet Airways', 
                    'Airline_Jet Airways Business', 'Airline_Multiple carriers', 'Airline_Multiple carriers Premium economy', 
                    'Airline_SpiceJet', 'Airline_Trujet', 'Airline_Vistara', 'Airline_Vistara Premium economy', 'Source_Chennai', 
                    'Source_Delhi', 'Source_Kolkata', 'Source_Mumbai', 'Destination_Cochin', 'Destination_Delhi', 
                    'Destination_Hyderabad', 'Destination_Kolkata', 'Destination_New Delhi']


def home(request):
    params={}
    try:
        data_test_dictionary = dict.fromkeys(all_column_names, 0)
        yet_to_predict = True
        if request.method == "POST":
            Journey_month = request.POST.get('Journey_month')
            Journey_day = request.POST.get('Journey_day')
            Dep_hour = request.POST.get('Dep_hour')
            Dep_min = request.POST.get('Dep_min')
            Arr_hour = request.POST.get('Arr_hour')
            Arr_min = request.POST.get('Arr_min')
            Total_Stops = request.POST.get('Total_Stops')
            source = request.POST.get('source')
            destination = request.POST.get('destination')
            airline = request.POST.get('airline')
            
            time_1 = datetime.datetime.strptime(Dep_hour + ":" + Dep_min, "%H:%M")
            time_2 = datetime.datetime.strptime(Arr_hour + ":" + Arr_min, "%H:%M")
            
            time_difference = time_2 - time_1
                
            if 'day' in str(time_difference):
                time_difference = str(time_difference).split(",")[1].split(" ")[1]
                Duration_hours = time_difference.split(":")[0]
                Duration_mins = time_difference.split(":")[1]
            else:
                Duration_hours = str(time_difference).split(":")[0]
                Duration_mins = str(time_difference).split(":")[1]
                
            if source.split('_')[1] == destination.split('_')[1]:
                print("sorry source and destination cannot be the same.")
                messages.success(request, "source and destination cannot be the same.")
            else:
                print("Journey_month", Journey_month)
                print("Journey_day", Journey_day)
                print("Dep_hour", Dep_hour)
                print("Dep_min", Dep_min)
                print("Arr_hour", Arr_hour)
                print("Arr_min", Arr_min)
                print("Total_Stops", Total_Stops)
                print("Duration_hours", Duration_hours)
                print("Duration_mins", Duration_mins)
                print("source", source)
                print("destination", destination)
                print("airline", airline)
                
                
                data_test_dictionary['Journey_month'] = int(Journey_month)
                data_test_dictionary['Journey_day'] = int(Journey_day)
                data_test_dictionary['Dep_hour'] = int(Dep_hour)
                data_test_dictionary['Dep_min'] = int(Dep_min)
                data_test_dictionary['Arr_hour'] = int(Arr_hour)
                data_test_dictionary['Arr_min'] = int(Arr_min)
                data_test_dictionary['Total_Stops'] = int(Total_Stops)
                data_test_dictionary['Duration_hours'] = int(Duration_hours)
                data_test_dictionary['Duration_mins'] = int(Duration_mins)
                
                for key in data_test_dictionary:
                    if key == source:
                        data_test_dictionary[key] = 1
                        
                    if key == destination:
                        data_test_dictionary[key] = 1
                            
                    if key == airline:
                        data_test_dictionary[key] = 1
                    else:
                        print("something wrong")
                    list_to_predict = []
                    for key in data_test_dictionary:
                        list_to_predict.append(data_test_dictionary[key])
                
                price = __model.predict([list_to_predict])
                yet_to_predict = False
                
                # creating the date object of today's date
                todays_date = date.today()
                
                FlightDetails.objects.create(Journey_month=Journey_month, Journey_day=Journey_day, Journey_year=str(todays_date.year), 
                                            Dep_hour=Dep_hour, Dep_min=Dep_min, Arr_hour=Arr_hour, Arr_min=Arr_min,
                                            Total_Stops=Total_Stops, Duration_hours=Duration_hours, Duration_mins=Duration_mins,
                                            source=str(source).split("_")[1], destination=str(destination).split("_")[1], airline=str(airline).split("_")[1], price=round(price[0], 2))
                
                params['airline_name'] = str(airline).split("_")[1]
                params['source_name'] = str(source).split("_")[1]
                params['destination_name'] = str(destination).split("_")[1]
                params['departure_time'] = str(Dep_hour) + ":" + str(Dep_min)
                params['arrival_time'] = str(Arr_hour) + ":" + str(Arr_min)
                params['journey_date'] = str(Journey_day) + "/" + str(Journey_month) + "/" + str(todays_date.year)
                params['total_stops'] = str(Total_Stops)
                params['price'] = str(round(price[0], 2))
        params['destination']=final_destination
        params['source']=final_source
        params['airline']=final_airline
        params['yet_to_predict']=yet_to_predict
    except Exception as e:
        print(e)
        params['exception_error'] = e
        params['except_error'] = 'Something went wrong please fill all the necessary fields.'
        params['yet_to_predict'] = True
    return render(request, 'flight_estimator/index.html', params)






def logout_request(request):
    logout(request)
    print("Logged out successfully!")
    return redirect("/")



def login_request(request):
    context = {}
    print("inside")
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            return redirect('database')
    else:
        if request.method == 'POST':
            form = AuthenticationForm(request=request, data=request.POST)
            username = request.POST.get('username')
            password = request.POST.get('password')
            user_exists = User.objects.filter(username=username).exists()
            if user_exists:
                try:
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    messages.info(request, f"You are now logged in as {username}")
                    print("You are now logged in as", username)
                    if user.is_superuser == True:
                        return redirect('database')
                    else:
                        return redirect('/authentication_required')
                except:
                    errors = "Incorrect Password"
                    print("Incorrect Password")
                    context['errors'] = errors
            else:
                print("username does not exists.")
                errors = "Username/Email does not exists."
                context['errors'] = errors
        form = AuthenticationForm()
        context['form'] = form
    return render(request, "flight_estimator/login.html", context)




def authentication_required(request):
    messages.success(request, 'you need to login first.')
    return redirect('login_page')





@login_required(login_url='/authentication_required/')
@active_user_required
def view_database(request):
    flight_details = FlightDetails.objects.all()
    params = {
        'flight_details': flight_details,
    }
    return render(request, 'flight_estimator/database.html', params)