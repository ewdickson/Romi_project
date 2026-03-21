Results
=======

Final Times
-----------

.. list-table::
   :header-rows: 1
   :widths: 10 25

   * - Run
     - Time
   * - 1
     - 1:02
   * - 2
     - DNF
   * - 3
     - 1:05


Demonstration Videos
--------------------

Run 1
~~~~~

.. raw:: html

   <video width="560" controls>
     <source src="_static/run1.mp4" type="video/mp4">
   </video>


Run 2
~~~~~

.. raw:: html

   <video width="560" controls>
     <source src="_static/run2.mp4" type="video/mp4">
   </video>


Run 3
~~~~~

.. raw:: html

   <video width="560" controls>
     <source src="_static/run3.mp4" type="video/mp4">
   </video>

Challenges and Lessons Learned
------------------------------

Consistency
~~~~~~~~~~~
The main challenge we faced was consistency, for two different reasons. The first is 
that we practiced a lot on the track that had poor reflectance. For about 6 hours
the day before the final runs, we tuned our rotations and distances over and over, but 
it would never be consistent for long. We didn't know it was the track, since our line 
following works fine on both and we defaulted to practicing on the "bad" one so as to 
not have to wait in testing lines. Finally, we tried it on the actual track and it
worked far more consistently. We think that maybe the line following was decent on both
to the eye, but created enough variable heading coming off the first curve that would 
mess up parking garage navigation.

The second reason is that all of our states are dependent on encoder counts. This means
that if wheel slip and starting positions change the encoder readings even a little bit, 
down the line that could compound into the difference of hitting a garage pole or not.
Perhaps a heading controller would have corrected this, but would introduce higher
complexity to the project without fully eliminating drift.

Unusually Fast Runs
~~~~~~~~~~~~~~~~~~~
Another challenge was that our Romi would sometimes run the entire track at much higher
setpoints than prescribed. This would ususally happen after waiting a while to do a 
subsequent run with Romi still on. We adjusted our code to eliminate integral windup, but 
to no avail. The increased speed would last for the entire run, causing more slip and 
reducing consistency. Since it would never "wind down", we think it is a different issue.
For some reason, we were able to solve this by immediately running Romi again after a run,
or power cycling.

Memory
~~~~~~
The last significant challenge that we faced was running out of memory. At times, this 
prevented us from adding states or variables and being able to run our code. To fix this,
we got rid of a lot of Queues that we inherited from previous labs, and either commented 
them out or turned them into Shares, as we really only needed immediate data for control.
Additionally, we removed a lot of attributes that didn't need to be attributes in the 
FSM task.




