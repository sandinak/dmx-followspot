# Theory

This software works by designating the stage as a space in 
x,y,z coordinated planes with the origin at the farthest spot 
Down Stage Right.  All Fixtures and Targets are referenced from 
that point.  It then uses configuration, basic Euclidean geometry 
and vectors to determine how to align designated moving head fixtures
to the specified point on the stage.  

```
                             UP STAGE
SR |---------------------------------------------------------| SL
   |                                                         |
   |                                                         |
   |                                                         |
   |             * (x=5,y=10,z=5.5)                          |
   |                                                         |
   |                                                         |
   |                                                         |
   |                                                         |
   |                                                         |
   | ======================= CURTAIN ======================= |
   |                                                         |
   |                                                         |
   |                                                         |
   |                                                         |
 X>|_________________________________________________________|
   ^                         DOWN STAGE                       
   Y 
```
