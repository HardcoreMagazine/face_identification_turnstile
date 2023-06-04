## Turnstile face detection and identification system
Part of my diploma project, uses tools from
'OpenCV' and 'face_recognition' ('dlib') libraries to detect and identify faces.

Project purpose is further automation of existing 
turnstile security system while also increasing it's reaction time
and security.

Methods used: 
- Haar Cascade + LBPH ('alg1', 'OpenCV'); 
- unknown, possibly CNN ('alg2', 'face_recognition')

System structure (simplified):  
![](system_graph.png)

Project structure:  
. - *root (this folder)*  
.\ComputerVision - *face detection and identification subsystem*  
.\GateSimulator - *turnstile subsystem simulator*   
.\MySQL - *SQL script for table creation*  

**Note:** this is a prototype - project uses HTTP protocol for cross-platform 
communication instead of proper TCP/UDP connection.  
**Note:** this release contains no pre-trained LBPH model nor 
face images

