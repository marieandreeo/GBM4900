1. exeGuiLeapMotionAngle
 
   This folder contains programme exe which can run on any computer (PC or MAC)
   For run, click "..\LMPY\exeGuiLeapMotionAngle\guiLeapMotionAngle.exe"


2. demoLeapMotionAngle.py
   
   This program, execute angle computing with console. We need to configure console 
   with parameters in "..\LMPY\utility\configurationConsolePoliceDemoTest.PNG" and
   "..\LMPY\utility\configurationConsoleWindowDemoTest.PNG"

3. testLeapMotionAngle.py

   This program, save angles calculated for tests validation. We need to configure console 
   with parameters in "..\LMPY\utility\configurationConsolePoliceDemoTest.PNG" and
   "..\LMPY\utility\configurationConsoleWindowDemoTest.PNG"

4. guiLeapMotionAngle.py 

   Program for angle computing and display with GUI using Qt Designer and PySide library.
   "..\LMPY\filesUi" contains all files for Qt Designer (http://doc.qt.io/qt-4.8/designer-manual.html)
   "..\LMPY\mainPageUi.py" and "..\LMPY\pageUi.py" are generate with "..\LMPY\mainPage.ui" and "..\LMPY\page.ui"
   For convert ui to py, see line command console in "..LMPY\utility\conversionUiToPyGui.txt"

5. Leap Motion library 

   4 files :

   "..\LMPY\Leap.dll"
   "..\LMPY\Leap.lib"
   "..\LMPY\Leap.py"
   "..\LMPY\LeapPython.pyd"

   Don't delete this files because it is the library for Leap Motion acquisition.
   You can download latest version in SDK : https://developer.leapmotion.com/