IMPEx-SMDB PHP webservice
=========================

[IMPEx](http://impex-fp7.oeaw.ac.at/) is an FP7 project which enables a better interaction between planetary models and data meassured by spacecraft.

This repository is aimed to the Data Model providers and not to the end user.

Installation
------------

[Zend framwork](http://framework.zend.com/) needs to be installed. That depends on your OS, for example in a debian-like box you could do:

```bash
$ apt-get install zendframework
```

Next, clone this repository in an accessible place from the outside world.
Change globals.php as required and write the wrappers to your model.

Contributing
------------

If you are a SMDB provider and you would like to add your wrapper to the repository to help others, then fork this repository and ask for a Pull Request when your code is ready.

Are you new to git? nothing to worry about! Git is easy. Try [this short tutorial](http://try.github.io/) and you will know how to proceed.  Don't hesitate to ask if you have any doubts.

FMI
---

FMI has the following requirements:

```scipy >= 0.12, numpy, astropy```

Also, astropy requires that ```$XDG_CONFIG_HOME``` set for the ```www-data``` and the ```$XDG_CONFIG_HOME/astropy``` directory created and accessible by the ```www-data``` user.  This variable is set in: ```/etc/apache2/envvars```.

