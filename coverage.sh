#!/bin/sh -xe

coverage run --branch --source=evrobot `which nosetests` --with-xunit
coverage html
coverage xml
