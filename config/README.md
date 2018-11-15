# Configuration
DMX Followspot uses several config files to organize the information
into easily managable bites. 

- [DMXFS Config](#dmxfs-config) - base config of the toolset
- [Shows](#shows)
  - [Fixtures](#fixtures) - individual devices
  - [Fixture Groups](#fixture-groups) - device groupings
  - [Fixture Aspects](#fixture-aspects) - how devices are mounted
- [Fixture Profiles](#fixture-profiles) - definition of each device

## DMXFS Config

Base configuration of the tool, saved in [config/dmxfs.yml](./dmxfs.yml).

- *dmx*
  - *input* - how we take DMX in
    - *universe* - the Universe ID we're taking input from as configured in OLA
    - *id* - the base DMX id for control messages to dmxfs. We use 3 channels.
  - *output* - where we send DMX 
    - *universe* - the output Universe ID (Cannot be same as input)
- *joystick*
  - *type*
  - *id*
  - *deadzone*

#### Example
```yaml
dmx:
  # where the input comes from
  # this is the DMX Spot Controller ID
  input: 
    universe: 1
    id: 20

  # where the spots are at least, anything else will be passed from 
  # the input universe
  output:
    universe: 2

# how we manage the joystick
joystick:
  type: wireless
  id: 1
  deadzone: 4000 
```



## Shows
Shows are the "top-level" of the system configuration for fixtures, and 
are specified on the commandline using *-s*.  If no show is specified,
and there is only 1 show, then it will be loaded, else the show named 
'default' will be loaded. Each show defines a set of fixtures that 
can be manipulated, their default positions on the stage, and groupings 
used to point at targets.

The [config/shows.yml](./shows.yml) is structured like this:

- *shows*
  - custom show name
    - *fixtures* - a dict of fixtures used in the show
    - *fixture_groups* - a dict of lists of fixtures 
    - *fixture_aspects* - a dict of mount names and aspect information
  - ...

#### Example

```yaml
shows:
  evolution:
    fixtures:
       # Stage Right Floor 
       F-SR-S:
        id: 465
        profile: Generic_Spot
        x: 2
        y: 0
        z: 0
      F-SR-1-P: 
        id: 127
        profile: LED_Wash
        x: 2.3
        y: 0
        z: 0     

      # Truss 1
      T1-SR-1-S:
        id: 127
        profile: Generic_Spot
        aspect: truss
        x: 2.3
        y: 0
        z: 0     

    fixture_groups:
      all_spots:
        - F-SR-S
        - T1-SR-1-S

    fixture_aspects:
      truss: hanging
```


### Fixtures
A fixture is a single device in your show that can be manipulated by 
dmxfs. Location data can be in any base10 form (eg meters, feet) as 
long as you're consistent through all location data. This means, if you
use feet, you must use decimal format for inches (e.g. 12'3" = 12.25).
Each fixture has a name, and data that identify it:

- *name* - a unique identifier; typically the same name used in your
DMX software to identify a particular fixture
- *profile* - the [fixture profile](#fixture-profiles) id
- *aspect* - use a [fixture aspect](#fixture-aspects)
- *id* - the DMX id on the default universe. 
- *x* - the relative location of the fixture to the origin SR->SL
- *y* - the relative location of the fixture to the origin DS->US
- *z* - the relative location of the fixture to the lowest point on the stage (x=0, y=0) 


#### Example

```yaml
fixtures:
  F-SR-PS:
    id: 257
    profile: 36LED_PS
    x: 0
    y: 0
    z: 0
```

### Fixture Groups
This is a logical grouping of fixtures to use in a scene. E.g., there are 
times when you might only want to use front spots, or back spots, or 
all washes, etc. There is a default group *all* created which is 
all fixtures defined for a show. 

### Example

```yaml
fixture_groups:
  front_spots:
    - F-SL-S
    - F-SC-S
    - F-SL-S
```


### Fixture Aspects
This denotes are how the fixture is deployed:
- the name of the aspect can be something useful like the mount name
- options: ( can be one or both of these... ) 
    - reversed  - connections facing audience 
    - hanging   - hanging inverted
the default is sitting on it's feet with connections facing up stage
and is used if no aspect is defined.

#### Example

```yaml
fixture_aspects:
  truss: hanging
  tree: hanging,reversed
```

## Fixture Profiles

Each fixture has a profile which defines its attributes. Profile files are saved in the [config/fixture_profiles/](./fixture_profiles/) directory.

A profile file is structured like this:

- custom fixture name (used in shows->fixtures)
  - *h-range* - maximum number of rotational degrees horizontally
  - *v-range* - maximum number of rotational degrees vertically
  - *h-rotation* - default if not specified is counter-clockwise (as 
  looking down on the fixture) however you can specify 'cw' for clockwise
  - *hx* - the H value for when the fixture is pointing down the x-axis sitting on the floor with the connections facing to the stage.
  - *vz* - the V value for when the fixture is pointing down the z-axis sitting on the floor with the connections facing the stage.
  - *color_values* - this is for color-wheel based spots; The DMX values at which the 'color' channel actives each of these colors:
    - *white*
    - *red*
    - *green*
    - *blue*
  - *channels* - an ordered list of the channels matching the DMX channels for the fixture. 
- ...

### Channels
Each Fixture has a set of channels which can be managed by dmxfs as part 
of a scene.  These managed channels must be specifically named for the 
tool to know, otherwise you can use whatever nomenclature you'd like
for the channel names.  Movement is either 8-bit or 16-bit, so you can't
define both 'horizontal' and 'h-coarse' for instance.

- Horizontal, Pan or X - the horizontal component of movement
  - *horizontal* - 8-bit measurement (0-255)
  - *h-coarse* - most significant 8-bits of a 16 bit value of horizontal 
movement (0-255)
  - *h-fine* - least significant 8-bits of the 16 bit value of horizontal 
movement (0-255)
- Vertical, Tilt or Y - the vertical componnent of movement
  - *vertical* - 8-bit measurement (0-255)
  - *v-coarse* - most significant 8-bits of a 16 bit value of horizontal 
movement (0-255)
  - *v-fine* - least significant 8-bits of the 16 bit value of horizontal 
movement (0-255)
- *color* - for color wheel based fixtures .. will need color_values set 
for the fixture
- *white, red, green, blue* - individual color channels

### Example 

```yaml
LED_Spot:
  h-range: 540
  v-range: 190
  h-rotation: cw
  hx: 45
  vz: 15
  color_values:
    white: 0
    red: 15
    green: 25
    blue: 35
  channels:
   - h-coarse
   - h-fine
   - v-coarse
   - v-fine
   - movement_speed
   - intensity
   - strobe
   - color
   - gobo
   - function
```


  