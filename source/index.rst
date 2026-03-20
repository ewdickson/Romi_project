.. ME405 Term Project documentation master file, created by
   sphinx-quickstart on Mon Mar 16 15:17:29 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ME405 Term Project
==================

to update html = py -m sphinx -b html source build OR FOR MAC python3 -m sphinx -E -b html source build

Project Summary
---------------

This project is an autonomous line-following robot designed for the ME405 term project.
Depending on track position, the robot detects and follows printed lines, naviagates 
predetermined paths, or recovers from bumping a wall.

General Strategy
----------------

Our team designed and built a robot capable (maybe) of completing repeated time trials on the
printed lab track primarily using line sensing and encoder feedback in combination with
PI motor controllers.

Repository
----------

View the project on `GitHub <https://github.com/ewdickson/Romi_project>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   hardware_design
   program_structure
   results


