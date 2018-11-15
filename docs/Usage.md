# Usage 

* [Definitions](#definitions) - monikers and their definitions
* [Modes of Operation](#modes) - the operational modes
* [Control Commands](#control-commands) - commands sent from originating 
DMX Universe
* [Scenes](#scenes) - A starting location for a "Target" 
* [Show](#show) - how we define fixtures
* [Fixuture Groups](#fixture-groups)
* [Aspect](#aspect)

In normal operation the system will read the data on the input 
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
- FixtureGroups - a predefined set of fixtures to use in a Scene 
- Target - the location on the stage in the X,Y plane with a specific 
height
- Scene - a Fixture Group and Target

## Modes
The system currently has two modes: Production and Tech.

 - *Production mode* - (Mode:0) the joystick operator can only react to scenes as 
 they are cue'd to the system from the DMX controller upstream. They
cannot edit any scenes or stage layouts.  The intent for this is to 
prevent inadvertant operation during a show.

 - *Tech mode* - (Mode: 1) the joystick operator can select Edit 
 mode for a Scene that's cue'd from the master DMX controller by 
 pressing the Guide button.  

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
 - 3 - Stage Edit - TBD...

## Scenes 
These are stored starting location for the selected FixtureGroup.  This 
will include an x,y and z in the stage plane.  The Z will be consistent
for any movement of the joystick.  Right now you can use the d-pad to 
move the Z position up as needed, however one of the TODO I have is to 
allow the stage to be more detailed with risers, platforms, etc.

## Show
All the fixtures in a show are 
Each head is assigned a few pieces of data so that the system can do 
the math.  The x,y and z data must be consistent with type of 
measurement system used, but can be english, metric or anything else. 

- Name  - whatever naming scheme you use..
- DMX Id - the orignating universe ID 
- Profile - a reference to fixture capabilities description.
- x - the position of the fixture from SR to SL
- y - the position of the fixture from Down Stage to Upstage
- z - the vertical height of the fixture as it would be measured at 
the origin (eg .. if you have a sloped stage you have to account for that) 

## Fixture Groups
An organizational structure allowing fixtures to be grouped in any way 
you'd like.  A group can have any number of individual fixtures, and a 
fixture can be in more than one group.  

## Aspect 
Fixtures have aspects which help the system determine 
the installed orientation of the fixture so it can determine which 
directions to move the head as requested.  The default aspect:

 - Fixture is on it's feet on the floor
 - Fixture control connections are pointing UP STAGE (Away from audience) 

I typically name the fixture aspects *Where* they're hanging or what 
they are sitting on.


