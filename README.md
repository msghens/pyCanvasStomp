# pyCanvasStomp

## Lum5 Glassfish Canvas client

*Note:* My institution will be moving away from Luminis V soon. This is non-suported software


Python replacement for JMSHTTPAdapter_1.0.zip

Problem: 

pyCanvasStomp was developed as a quick hack to solve the issue that student enrollments not being processed by  Canvas.

The basic logic is to check for IMS member records (student enrollment), convert them to Canvas CSV, else pass on the XML.

This script is in production. However, there is still work to be done. 

Future plans

* None This is legacy software

Use at your discretion.

## Bugs?

* Seems that when a grade change happens, a 0 or inactive status is sent

### Documentation on IMS XML for Ellucian Elearning:

https://manualzz.com/doc/o/m9599/banner-integration-for-elearning---administration-guide--...-course-section-data-object