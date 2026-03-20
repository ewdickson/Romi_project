Wiring Diagram
==============

Pin Assignments
---------------

Motors
~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 20 30 10

   * - Pin
     - Signal
     - Function
     - Notes
   * - PC6
     - TIM8_CH1 (PWM)
     - Right motor PWM
     - 10 kHz
   * - PA5
     - GPIO
     - Right motor direction
     -
   * - PB6
     - GPIO
     - Right motor enable (nSLP)
     - Active low
   * - PC7
     - TIM8_CH2 (PWM)
     - Left motor PWM
     - 10 kHz
   * - PB4
     - GPIO
     - Left motor direction
     -
   * - PB10
     - GPIO
     - Left motor enable (nSLP)
     - Active low

Encoders
~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 20 30

   * - Pin
     - Timer Channel
     - Function
   * - PA6
     - TIM3_CH1
     - Right encoder A
   * - PA7
     - TIM3_CH2
     - Right encoder B
   * - PA0
     - TIM2_CH1
     - Left encoder A
   * - PA1
     - TIM2_CH2
     - Left encoder B

Line Sensors
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 10 30

   * - Pin
     - Type
     - Function
   * - PA4
     - ADC
     - Sensor 1
   * - PB0
     - ADC
     - Sensor 2
   * - PB1
     - ADC
     - Sensor 3
   * - PC0
     - ADC
     - Sensor 4
   * - PC1
     - ADC
     - Sensor 5
   * - PC2
     - ADC
     - Sensor 6
   * - PC3
     - ADC
     - Sensor 7

IMU
~~~

.. list-table::
   :header-rows: 1
   :widths: 10 20 30

   * - Pin
     - Signal
     - Function
   * - PB8
     - I2C1_SCL
     - Clock
   * - PB9
     - I2C1_SDA
     - Data
   * - PA15
     - GPIO
     - IMU reset (active low)

Bump Sensor
~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 25 30

   * - Pin
     - Type
     - Function
   * - PC12
     - EXTI (falling edge)
     - Bump sensor

User Button
~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 25 30

   * - Pin
     - Type
     - Function
   * - PC13
     - EXTI (falling edge)
     - Blue user button

Diagram
-------

.. image:: _static/ME405_wiring.jpg
   :width: 80%
   :align: center
   :alt: Robot on the track