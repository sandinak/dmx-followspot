""" Xbox 360 controller support for Python
11/9/13 - Steven Jacobs

This class module supports reading a connected xbox controller.
It requires that xboxdrv be installed first:

    sudo apt-get install xboxdrv

See http://pingus.seul.org/~grumbel/xboxdrv/ for details on xboxdrv

Example usage:

    import xbox
    joy = xbox.Joystick()         #Initialize joystick
    
    if joy.A():                   #Test state of the A button (1=pressed, 0=not pressed)
        print 'A button pressed'
    x_axis   = joy.leftX()        #X-axis of the left stick (values -1.0 to 1.0)
    (x,y)    = joy.leftStick()    #Returns tuple containing left X and Y axes (values -1.0 to 1.0)
    trigger  = joy.rightTrigger() #Right trigger position (values 0 to 1.0)
    
    joy.close()                   #Cleanup before exit
"""

import subprocess
import os
import signal
import select
import time
import logging as log
import sys

xboxdrv_options = [
#    '--no-uinput',
#    '--detach-kernel-driver'
]

XBOXDRV = '/usr/bin/xboxdrv'
SUDO = '/usr/bin/sudo'


class Joystick:

    """Initializes the joystick/wireless receiver, launching 'xboxdrv' as a subprocess
    and checking that the wired joystick or wireless receiver is attached.
    The refreshRate determines the maximnum rate at which events are polled from xboxdrv.
    Calling any of the Joystick methods will cause a refresh to occur, if refreshTime has elapsed.
    Routinely call a Joystick method, at least once per second, to avoid overfilling the event buffer.

    Usage:
        joy = xbox.Joystick()
    """

    def __init__(self, config={}, refreshRate=30, debug=False):
        self.refreshRate = refreshRate
        self.debug = debug
        self.cid = config.get('controller_id')
        self.wid = config.get('wireless_id')
        self.controller_check() 
        self.connect()

    def controller_check(self):
        ''' Make sure the controller is connected and ready '''
        if not os.path.isfile(XBOXDRV) and os.access(XBOXDRV, os.X_OK):
            print('%s not found, need to install' % XBOXDRV)
            sys.exit(1)

        c_list_result = subprocess.run([ SUDO, XBOXDRV, '-L' ], capture_output=True) 
        c_list_out = c_list_result.stdout.decode('utf-8')
        if 'no controller detected' in c_list_out:
            print('ERROR: no controller detected:\n%s' % c_list_out)
            if not self.debug: 
                sys.exit(1)


    def connect(self, options=[]):
        run_options = [XBOXDRV]

        # become root if needed
        if os.geteuid():
            run_options.insert(0, SUDO)

        # type of controller, and target
        print('controller: %d' % self.cid)
        if self.cid and self.cid > 0:
            run_options.append('--id')
            run_options.append('%d' % self.cid)
        if self.wid and self.wid > 0:
            run_options.append('--wid')
            run_options.append('%d' % self.wid)

        run_options = run_options + xboxdrv_options + options
        log.debug('running %s' % (" ".join(run_options)))
        self.proc = subprocess.Popen(
            run_options,
            stdout=subprocess.PIPE)
        self.pipe = self.proc.stdout
        # reset connect status
        # will be set to True once controller is detected and stays on
        self.connectStatus = False
        self.reading = '0' * 140  # initialize stick readings to all zeros
        #
        # absolute time when next refresh (read results from xboxdrv stdout
        # pipe) is to occur
        self.refreshTime = 0
        # joystick refresh is to be performed 30 times per sec by default
        self.refreshDelay = 1.0 / self.refreshRate
        #
        # Read responses from 'xboxdrv' for upto 2 seconds, looking for
        # controller/receiver to respond
        found = True
        waitTime = time.time() + 2
        while waitTime > time.time() and not found:
            readable, writeable, exception = select.select(
                [self.pipe], [], [], 0)
            if readable:
                response = self.pipe.readline()
                # Hard fail if we see this, so force an error
                if response[0:7] == 'No Xbox':
                    raise IOError('No Xbox controller/receiver found')
                # Success if we see the following
                    found = True
                # If we see 140 char line, we are seeing valid input
                if 'now be available' in response or len(response) == 140:
                    found = True
                    self.connectStatus = True
                    self.reading = response

        # if the controller wasn't found, then halt
        if not found:
            self.close()
            raise IOError(
                'Unable to detect Xbox controller/receiver - Run python as sudo')

    def disconnect(self):
        log.info('disconnecting from xboxdrv')
        self.proc.terminate()
        self.proc.wait()
        del self.proc
        del self.pipe

    """Used by all Joystick methods to read the most recent events from xboxdrv.
    The refreshRate determines the maximum frequency with which events are checked.
    If a valid event response is found, then the controller is flagged as 'connected'.
    """

    def refresh(self):
        # Refresh the joystick readings based on regular defined freq
        if self.refreshTime < time.time():
            self.refreshTime = time.time() + self.refreshDelay  # set next refresh time
            # If there is text available to read from xboxdrv, then read it.
            readable, writeable, exception = select.select(
                [self.pipe], [], [], 0)
            if readable:
                # Read every line that is available.  We only need to decode the
                # last one.
                while readable:
                    response = self.pipe.readline()
                    # print(f'response: %s' % response)
                    # A zero length response means controller has been
                    # unplugged.
                    if len(response) == 0:
                        raise IOError('Xbox controller disconnected from USB')
                    readable, writeable, exception = select.select(
                        [self.pipe], [], [], 0)
                # Valid controller response will be 140 chars.
                if len(response) == 140:
                    self.connectStatus = True
                    self.reading = response
                    return True
                else:  # Any other response means we have lost wireless or controller battery
                    self.connectStatus = False
        return False

    """Return a status of True, when the controller is actively connected.
    Either loss of wireless signal or controller powering off will break connection.  The
    controller inputs will stop updating, so the last readings will remain in effect.  It is
    good practice to only act upon inputs if the controller is connected.  For instance, for
    a robot, stop all motors if "not connected()".
    
    An inital controller input, stick movement or button press, may be required before the connection
    status goes True.  If a connection is lost, the connection will resume automatically when the
    fault is corrected.
    """

    def connected(self):
        self.refresh()
        return self.connectStatus

    # LED operations
    def led(self, code):
        self.disconnect()
        self.connect(['--led', '%d' % code])

    # Left stick X axis value scaled between -1.0 (left) and 1.0 (right) with
    # deadzone tolerance correction
    def leftX(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[3:9])
        return self.axisScale(raw, deadzone)

    # Left stick Y axis value scaled between -1.0 (down) and 1.0 (up)
    def leftY(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[13:19])
        return self.axisScale(raw, deadzone)

    # Right stick X axis value scaled between -1.0 (left) and 1.0 (right)
    def rightX(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[24:30])
        return self.axisScale(raw, deadzone)

    # Right stick Y axis value scaled between -1.0 (down) and 1.0 (up)
    def rightY(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[34:40])
        return self.axisScale(raw, deadzone)

    # Scale raw (-32768 to +32767) axis with deadzone correcion
    # Deadzone is +/- range of values to consider to be center stick (ie. 0.0)
    def axisScale(self, raw, deadzone):
        if abs(raw) < deadzone:
            return 0.0
        else:
            if raw < 0:
                return (raw + deadzone) / (32768.0 - deadzone)
            else:
                return (raw - deadzone) / (32767.0 - deadzone)

    # Dpad Up status - returns 1 (pressed) or 0 (not pressed)
    def dpadUp(self):
        self.refresh()
        return int(self.reading[45:46])

    # Dpad Down status - returns 1 (pressed) or 0 (not pressed)
    def dpadDown(self):
        self.refresh()
        return int(self.reading[50:51])

    # Dpad Left status - returns 1 (pressed) or 0 (not pressed)
    def dpadLeft(self):
        self.refresh()
        return int(self.reading[55:56])

    # Dpad Right status - returns 1 (pressed) or 0 (not pressed)
    def dpadRight(self):
        self.refresh()
        return int(self.reading[60:61])

    # Back button status - returns 1 (pressed) or 0 (not pressed)
    def Back(self):
        self.refresh()
        return int(self.reading[68:69])

    # Guide button status - returns 1 (pressed) or 0 (not pressed)
    def Guide(self):
        self.refresh()
        return int(self.reading[76:77])

    # Start button status - returns 1 (pressed) or 0 (not pressed)
    def Start(self):
        self.refresh()
        return int(self.reading[84:85])

    # Left Thumbstick button status - returns 1 (pressed) or 0 (not pressed)
    def leftThumbstick(self):
        self.refresh()
        return int(self.reading[90:91])

    # Right Thumbstick button status - returns 1 (pressed) or 0 (not pressed)
    def rightThumbstick(self):
        self.refresh()
        return int(self.reading[95:96])

    # A button status - returns 1 (pressed) or 0 (not pressed)
    def A(self):
        self.refresh()
        return int(self.reading[100:101])

    # B button status - returns 1 (pressed) or 0 (not pressed)
    def B(self):
        self.refresh()
        return int(self.reading[104:105])

    # X button status - returns 1 (pressed) or 0 (not pressed)
    def X(self):
        self.refresh()
        return int(self.reading[108:109])

    # Y button status - returns 1 (pressed) or 0 (not pressed)
    def Y(self):
        self.refresh()
        return int(self.reading[112:113])

    # Left Bumper button status - returns 1 (pressed) or 0 (not pressed)
    def leftBumper(self):
        self.refresh()
        return int(self.reading[118:119])

    # Right Bumper button status - returns 1 (pressed) or 0 (not pressed)
    def rightBumper(self):
        self.refresh()
        return int(self.reading[123:124])

    # Left Trigger value scaled between 0.0 to 1.0
    def leftTrigger(self):
        self.refresh()
        return int(self.reading[129:132]) / 255.0

    # Right trigger value scaled between 0.0 to 1.0
    def rightTrigger(self):
        self.refresh()
        return int(self.reading[136:139]) / 255.0

    # Returns tuple containing X and Y axis values for Left stick scaled between -1.0 to 1.0
    # Usage:
    #     x,y = joy.leftStick()
    def leftStick(self, deadzone=4000):
        self.refresh()
        return (self.leftX(deadzone), self.leftY(deadzone))

    # Returns tuple containing X and Y axis values for Right stick scaled between -1.0 to 1.0
    # Usage:
    #     x,y = joy.rightStick()
    def rightStick(self, deadzone=4000):
        self.refresh()
        return (self.rightX(deadzone), self.rightY(deadzone))

    # Cleanup by ending the xboxdrv subprocess
    def close(self):
        try:
            # Try to terminate our specific subprocess first
            if hasattr(self, 'proc') and self.proc:
                self.proc.terminate()
                self.proc.wait(timeout=2)
                log.debug('Xbox controller subprocess terminated')
        except Exception as e:
            log.debug(f'Error terminating xbox subprocess: {e}')

        # Fallback to pkill (may fail with permission error, but that's ok)
        try:
            os.system('pkill xboxdrv')
        except Exception as e:
            log.debug(f'pkill xboxdrv failed (non-critical): {e}')
