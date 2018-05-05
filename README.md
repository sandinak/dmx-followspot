# DMX Followspot


Having an available follow-spot at a venue is sometimes a challenge...
and having stage based follow-spots is even harder.  This tool allows an 
operator to select a collection of moving 
[DMX](https://en.wikipedia.org/wiki/DMX512) heads in a "universe" and 
override the H,V settings (while passing through everything else!) 
on a scene by scene basis; and direct the focus position on the stage 
via an XBox 360 controller. 
This means you can define colors, timing, etc from your existing DMX 
system ( I use [QLC+](http://qlcplus.com) ;) and use this tool to 
handle scenes that need the followspot. 

It works by taking 'input' on your normal DMX 'universe' via ```olad``` 
( part of the [Open Lighting Project](https://www.openlighting.org/) ) 
and sending the 'output' on a second DMX 'universe' where you put the 
moving heads.  So the tool acts as a pass-through device during normal 
operation .. and then handles H,V values specifically during "run" mode.
The rest of the fixtures in that universe can remain on the originating 
or be placed on the new one as connectivity warrants.

I wrote this as I run lighting for a portable show, and I hope to allows 
the dynamic configuration of a 'stage' for a location using the basic 
setup as hints and then prompting the operator to align the lights so the 
system can discover the stage.  Phase 2. 

## TOC
* [Theory](docs/Theory.md) - deeper discussion on how it works
* [Requirements](docs/Requirements.md) - what you need to run this 
* [Config](config/README.md) - how to configure the tool
* [Usage](docs/Usage.md) - how to use the tool

I am looking for more contributors to this project, so if you have
some python-fu .. and like to make things work in cool ways, drop 
me a note. 
