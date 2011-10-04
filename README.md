#Online Petition

Simple system for registering and validating people signing an online petition.
Derp derp.

# Install

* Install virtualenv (on debian/ubuntu: apt-get install python-virtualenv ) 
* virtualenv --no-site-packages /path/to/store/your/virtualenv/onlinepetition
* source /path/to/virtualenv/onlinepetition/bin/activate
* pip install Django
* pip install South
* pip install django-uni-form
* pip install ipython

## Initialize database first time

* comment the onlinepetition module in settings.py and run  python manage.py syncdb
* python manage.py createsuperuser
* uncomment the onlinepetition module in settings.py
* python manage.py migrate

You should now be done :-)

# Note

System currently under heavy dev, please consider current code rather unstable ;-)

