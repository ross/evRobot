#!/bin/sh -xe

# ignoring empty except b/c we're rethrowing
lint8 evrobot/
lint8 --ignore=L007 tests/
