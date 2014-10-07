# Installation notes

* create a virtualenv for MXCuBE
    
    virtualenv --no-site-packages venv

* activate the environment

    . ./venv/bin/activate

* install packages

    - pip install bottle
    - pip install gevent
    - pip install PIL (or: pip install PIL --allow-external PIL --allow-unverified PIL)
    - pip install numpy
    - pip install louie
    - pip install scipy 
      
    *PROBLEM: we still depend on Qub, which depends on Qt for Bayer to RGB conversion*

* for production use, install uwsgi

    pip install uwsgi 