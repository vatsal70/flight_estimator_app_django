# Problem Statement: #

Travelling through flights has become an integral part of today’s lifestyle as more and more people are opting for faster travelling options. The flight ticket prices increase or decrease every now and then depending on various factors like timing of the flights, destination, and duration of flights various occasions such as vacations or festive season. Therefore, having some basic idea of the flight fares before planning the trip will surely help many people save money and time.


# Approach #
The classical machine learning tasks like Data Exploration, Data Cleaning,
Feature Engineering, Model Building and Model Testing. Try out different machine
learning algorithms that’s best fit for the above case.
<pre>
<li> Data Exploration        : I explored the  dataset using pandas, numpy, matplotlib and seaborn.</li>
<li> Data Visualization      : Plotted the graphs using the matlplotib and seaborn library to get the insights.</li>
<li> Feature Engineering     :  Removed all the NA values from the dataset and converted the categorial data to the desired type.</li>
<li> Model Selection         :  Tested different models and algrithms to check the accuracy of models. Plotted graph for the difference of (y_test - y_pred).</li>
<li> Hyperparameter Tuning   :  Performed Hyperparameter tuning using RandomizedSearchCV.</li>
<li> Pickle File             :  Selected model as per best accuracy and created pickle file using joblib .</li>
<li> Web-Application         :  Created a Django Web Application which takes neccessary inputs and predicts the price. It also stores the data into the database which can only be accessed by superuser.</li>
<li>Deployment               :  I have deployed project on heroku.</li></pre>


# Deployed Project #
<a href="https://flight-estimator-django.herokuapp.com/">https://flight-estimator-django.herokuapp.com</a>
