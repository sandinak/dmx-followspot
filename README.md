# DMX Followspot

Having an available follow-spot at a venue is sometimes a challenge...
and having stage based follow-spots is even harder.  This tool allows an 
operator to select a collection of moving 
[DMX](https://en.wikipedia.org/wiki/DMX512) heads in a "universe" and 
override the H,V settings (while passing through everything else!) 
on a scene by scene basis; and direct the focus position on the stage 
via an XBox 360 controller. 
This means you can define colors, timing, etc from your existing DMX 
system ( I use [QLC+](http://qlcplus.com) ;) and only use this tool to 
handle scenes that need the followspot. 

It works by taking 'input' on your normal DMX 'universe' via olad 
( part of the [Open Lighting Project](https://www.openlighting.org/) ) 
and sending the 'output' on a second DMX 'universe' where you put the 
moving heads.  So the tool acts as a pass-through device during normal 
operation .. and then handles H,V values specifically during "run" mode.

I wrote this as I run lighting for a portable show, and so it allows the 
dynamic configuration of a 'stage' for a location using the basic setup 
as hints and then prompting the operator to align the lights so the 
system can discover the stage.  However if you have a single stage .. 
this can be setup 


# Requirements
- A reasonable host to run as the passthrough, I am using a 
  [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) 
  with good success; however any host you can run OLA and install python 
  should work.
- Any [OLA supported DMX interface](https://www.openlighting.org/ola/get-help/ola-faq/#What_are_the_recommended_USB_Device_to_use_with_OLA) should work.
  I am using a 
  [DMX Hat](http://bitwizard.nl/shop/DMX-interface-for-Raspberry-pi)
  on the Raspi 3 and have used a [DMXKing USB](https://www.amazon.com/DMXking-ultraDMX-Micro-adapter-dongle/dp/B00T8OKM98/ref=sr_1_cc_1?s=aps&ie=UTF8&qid=1523466866&sr=1-1-catcorr&keywords=DMXKing)
- A [USB to Xbox 360 Wireless controller](https://www.amazon.com/Microsoft-Authentic-Wireless-Receiver-Windows/dp/B00FAS1WDG/ref=sr_1_6?ie=UTF8&qid=1523465136&sr=8-6&keywords=USB+Xbox+wireless)
- An Xbox 360 Controller

# Usage 
In general operation the system will read the data on the input 
Universe, and write the same data to the output Universe. The system 
is controlled via 3 DMX channels on the primary DMX universe. It will 
read all the values passed to it from the console and then perform the 
actions as necessary.  The channels are:
- n - Mode
- n+1 - Command
- n+2 - Scene

## Definitions
- Show - a predefined set of fixtures and fixture groups.
- Stage - a location for a show.. generally considered to be mapped by 
distance in the x,y plane
- Fixtures - a list of existing fixtures with DMXid, type and location 
if known
- FixtureGroups - a predefined set of fixtures to use in a Scene 
- Target - the location on the stage in the X,Y plane
- Scene - a Fixture Group and Target

## Operational Modes
The system currently has two modes: Production and Tech.

 - *Production mode* - the joystick operator can only react to scenes as 
 they are cue'd to the system from the DMX controller upstream. They
cannot edit any scenes or stage layouts.  The intent for this is to 
prevent inadvertant operation during a show.

 - *Tech mode* - the joystick operator can select Edit mode for a Scene 
 that's cue'd from the master DMX controller by pressing the Guide 
 button.   They can also edit the stage at any time using the Home 
 button.  

## Control Commands
The system is activated simply using a DMX value on the Command DMX 
channel.

 - 0 - Pass-through - all values sent to Universe 1 will be reflected
 to Universe 2 just as sent.  
 - 1 - Play - This will activate a Scene as defined by the id on the 
   Scene DMX channel.  The heads H,V will be overridden to point to the
   configured X,Y at the defined height.  The right joystick on the 
   controller will move the X,Y position around the stage using the 
   stored speed. 
   2 -  Scene Edit = this will load the Scene .. and also allow editing 
   of the scenes configuration:
      - X,Y starting position on the stage 
      - Z height of the spotlight Target
      - Fixture Group - one of the selection defined for the show
      - Speed - the speed the joystick will move the position on the 
      stage.
      
   3 - Stage Edit - 
