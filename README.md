### Listin
=======================

This project is configured with Vagrant. Some of the main tools included:

* A Vagrantfile for building an Ubuntu Trusty based VM
* A virtualenv (configured to be active on login), with project dependencies managed through a requirements.txt file
* A PostgreSQL database (with the same name as the project, pre-configured in the project settings file)
* Separation of configuration settings into base.py, dev.py and production.py (and optionally local.py, kept outside
  of version control) as per http://www.sparklewise.com/django-settings-for-production-and-development-best-practices/
* django-compressor and django-debug-toolbar

Setup
-----
Install Django 1.9 on your host machine. (Be sure to explicitly uninstall earlier versions first, or use a virtualenv -
having earlier versions around seems to cause pre-1.4-style settings.py and urls.py files to be generated alongside the
new ones.)

First, install Vagrant and VirtualBox.
To start project on you local machine, run the following commands:
```
    vagrant up
    vagrant ssh
      (then, within the SSH session:)
    ./manage.py runserver 0.0.0.0:8000
```
This will make the app accessible on the host machine as http://localhost:8000/ .
The codebase is located on the host machine, exported to the VM as a shared folder;
code editing and Git operations will generally be done on the host.

Building frontend
-----------------
You need to install React dev tools and sass compiler to build static files.
```
    cd core/static/
    jsx -w jsx/:js/
    sass -w scss/:css/
```
    

