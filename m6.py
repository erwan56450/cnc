# Disclaimer: The provided code is open-source and free to use, modify, and distribute. 
# The author shall not be held responsible for any injury, damage, or loss resulting from the use of this code.
# By using this code, you agree to assume all responsibility and risk associated with the use of the code.



# infos
ToolCount = 11                      # Nombre max. d'outils sur la table premier outil =1 (Maximum number of tools on the table, first tool=1)





# input/output csmio number (instead a number, with " Bone " and it will be ignore)
check_tool_in_spindel = 24          # Digital input number managing the tool detection sensor.
check_clamp_status = 25             # Digital input number managing the cone clamp open sensor.
valve_collet = 13                   # Digital output number managing the valve for tool change.
valve_clean_cone = 14               # Digital output number managing the valve for tool holder cone cleaning.
valve_dustColect_out = 9            # Remove dust shoe
valve_dustColect_under = 11         # put the dust shoe ready to suck
valve_blower = 12                   # Digital output number managing the valve for the blower

# time
blowing_time = 0.5                  # Time in seconds of the blower at the tool drop or measurement.
time_spindle_stop = 15              # WARNING If to short you will destroy your spindel. Time in seconds for the stop of your spindel with the heaviest tool.




#-----------------------------------------------------------
# Assigns a name to each axis when using getposition.
# "d.getPosition(CoordMode.Machine)" returns a machine position which, if the machine is at zero, will be: 0.0.0.0.0.0
# These lines of code are used to name each digit returned in the format X.Y.Z.A.B.C, where the first zero at position 0 is named X, the second zero at position 1 is named Y, etc.
# If your tool changer/holder is on the Y-axis instead of X-axis like mine, you can either replace all the X's in the code m6.py with Y's, or here, name X=1 and Y=0 (a trick I haven't tested).
#-----------------------------------------------------------

X = 0
Y = 1
Z = 2
A = 3
C = 5



from ConfigMachine import *  # Import the ConfigMachine.py file, which must be in the same directory as m6.py
import time   # Import time for the function time.sleep
import sys    # For using the function sys.exit()

#-----------------------------------------------------------
# Function checks if a tool is in place; otherwise stops the program
# Copy/Paste the two sentences below to the desired location in the code starting from #Start of the macro

# Read_if_tool_in(check_tool_in_spindle)
# Read_if_tool_in(check_clamp_status)
#-----------------------------------------------------------

def Read_if_tool_in(input_number):
    if input_number is None:  # Ignore the code if the input is configured as None
        return
    elif input_number == check_tool_in_spindle:  # Indicates the number of the input to control configured at the beginning of the code
        mod_IP = d.getModule(ModuleType.IP, 0)  # Call the CSMIO IP-S module
        if mod_IP.getDigitalIO(IOPortDir.InputPort, input_number) == DIOPinVal.PinSet:  # PinSet = On
            print("Sensor: Tool detected")  # Message in the console
        if mod_IP.getDigitalIO(IOPortDir.InputPort, input_number) == DIOPinVal.PinReset:  # PinReset = Off
            print("There is no tool in the spindle.")  # Message in the console
            msg.info("There is no tool in the spindle.")
            sys.exit(1)  # Stop the program
    elif input_number == check_clamp_status:  # Second input check
        mod_IP = d.getModule(ModuleType.IP, 0)
        if mod_IP.getDigitalIO(IOPortDir.InputPort, input_number) == DIOPinVal.PinReset:
            print("Sensor: Clamp closed")
        if mod_IP.getDigitalIO(IOPortDir.InputPort, input_number) == DIOPinVal.PinSet:
            print("Clamp open")
            msg.info("Clamp open")
            sys.exit(1)   # Stop the program

#-----------------------------------------------------------
# Function checks if the tool has been properly released; otherwise stops the program
# Copy/Paste the two sentences below to the desired location in the code

# Read_if_tool_out(check_tool_in_spindle)
# Read_if_tool_out(check_clamp_status)
#-----------------------------------------------------------

def Read_if_tool_out(input_number):
    if input_number is None:  # Ignore the code if the input is configured as None
        return
    elif input_number == check_tool_in_spindle:
        mod_IP = d.getModule(ModuleType.IP, 0)
        if mod_IP.getDigitalIO(IOPortDir.InputPort, input_number) == DIOPinVal.PinSet:
            print("The tool remains in the spindle")
            msg.info("The tool remains in the spindle")
            sys.exit(1)  # Stop the program
        if mod_IP.getDigitalIO(IOPortDir.InputPort, input_number) == DIOPinVal.PinReset:
            print("Sensor: The tool has been successfully released")
    elif input_number == check_clamp_status:
        mod_IP = d.getModule(ModuleType.IP, 0)
        if mod_IP.getDigitalIO(IOPortDir.InputPort, input_number) == DIOPinVal.PinReset:
            print("The clamp sensor indicates that the clamp has remained closed.")
            msg.info("The clamp sensor indicates that the clamp has remained closed.")
            sys.exit(1)  # Stop the program
        if mod_IP.getDigitalIO(IOPortDir.InputPort, input_number) == DIOPinVal.PinSet:
            print("Sensor: Clamp Open")

#-----------------------------------------------------------
# Function to activate any specified digital outputs example:
# on = set_digital_output(valve_collet, DIOPinVal.PinSet)
# off = set_digital_output(valve_collet, DIOPinVal.PinReset)
# Replace 'valve_collet' to handle other outputs; see ConfigMachine.py
#-----------------------------------------------------------

def set_digital_output(output_number, value):
    if output_number is None:  # If ConfigMachine.py returns None, the function is ignored
        return
    try:
        mod_IP = d.getModule(ModuleType.IP, 0)  # For CSMIO IP-S
        mod_IP.setDigitalIO(output_number, value)
    except NameError:
        print("------------------\nThe digital output has not been well defined.")

############################################################
# Start of the macro
############################################################

#-----------------------------------------------------------
# Check if there is a tool in the spindle. If "no tool," indicates tool zero in SimCNC.
#-----------------------------------------------------------

mod_IP = d.getModule(ModuleType.IP, 0)
if mod_IP.getDigitalIO(IOPortDir.InputPort, check_tool_in_spindle) == DIOPinVal.PinReset:
    d.setSpindleToolNumber("0")
    print("------------------\n NO TOOL IN SPINDLE.\n------------------")

#-----------------------------------------------------------
# Ask the CSMIO and name the returned values.
#-----------------------------------------------------------

# Get the tool number on the spindle and name it "hold_tool."
hold_tool = d.getSpindleToolNumber()

# Get the tool number from the G-code and name it "new_tool."
new_tool = d.getSelectedToolNumber()

# Get the known size in SimCNC of the new tool.
new_tool_length = d.getToolLength(new_tool)

# Get the machine's position and name it "position."
position = d.getPosition(CoordMode.Machine)

# Get the Y coordinate and name it y_coord.
y_coord = position[Y]

# Remove soft limits.
d.ignoreAllSoftLimits(True)

#-----------------------------------------------------------
# Prevent G-code from calling Probe 3D
#-----------------------------------------------------------

if threeD_prob is not None and new_tool == threeD_prob:
    print("The tool called in the G-code cannot be the 3D probe")
    msg.info("The tool called in the G-code cannot be the 3D probe")
    sys.exit(1)  # Stop the program

#-----------------------------------------------------------
# Get the tool number in the spindle and then return it to its place.
#-----------------------------------------------------------

# Evacuate the dust collector
set_digital_output(valve_dustCollect_out, DIOPinVal.PinSet)
time.sleep(2)
set_digital_output(valve_dustCollect_out, DIOPinVal.PinReset)

# If new_tool equals hold_tool or zero, skip procedure of storing hold_tool
if hold_tool != new_tool and hold_tool != 0:

    if hold_tool <= ToolCount:  # Checks if the tool number is between 1 and ToolCount
        print(f"------------------\n Storing tool number {hold_tool}\n------------------")
    else:
        msg.info("------------------\nThe tool called in the G-code does not exist")
        sys.exit(1)  # Stop the program

    # Calculate the X position based on the tool number
    X_position_hold_tool = X_position_first_tool + ((hold_tool - 1) * X_distance_between_tools)
    print(f"------------------\n Old tool will be stored at the location: {hold_tool}\n------------------")

    #-----------------------------------------------------------
    # Stop spindle
    #-----------------------------------------------------------

    d.setSpindleState(SpindleState.OFF)  # Turn off the spindle
    start_time_stop_spin = time.time()  # Start a timer

    #-----------------------------------------------------------
    # Begin movements to store hold_tool
    #-----------------------------------------------------------

    # Move Z axis up
    position[Z] = 0
    d.moveToPosition(CoordMode.Machine, position, Z_up_speed)

    # Check where the machine is and then shift Y if necessary
    if y_coord > Y_position_safe_zone:
        # Move towards the safe zone on the Y-axis
        position[Y] = Y_position_safe_zone
        d.moveToPosition(CoordMode.Machine, position, YX_speed)

    # Move in X and Y to a safe zone to avoid touching the tools
    position[X] = X_position_hold_tool
    position[Y] = Y_position_safe_zone
    d.moveToPosition(CoordMode.Machine, position, YX_speed)

    # Move the Y axis to the final location
    position[Y] = Y_position_first_tool
    d.moveToPosition(CoordMode.Machine, position, YX_speed)

    # Calculate the elapsed time since the timer was started and pause if the configured time_spindle_stop is not elapsed
    time_spent = time.time() - start_time_stop_spin
    remaining_time = time_spindle_stop - time_spent
    if remaining_time > 0:
        print(f"------------------\n {remaining_time} before next move, spindle still turning!!!\n------------------")
        time.sleep(remaining_time)

    # Move Z axis fast approach
    position[Z] = Z_position_approach
    d.moveToPosition(CoordMode.Machine, position, Z_down_fast_speed)

    # A quick blow of compressed air
    set_digital_output(valve_blower, DIOPinVal.PinSet)
    time.sleep(blowing_time)  # See timing in ConfigMachine.py
    set_digital_output(valve_blower, DIOPinVal.PinReset)

    # Move Z axis slow final approach
    position[Z] = Z_position_tools
    d.moveToPosition(CoordMode.Machine, position, Z_down_final_speed)

#-----------------------------------------------------------
# Retrieve the tool number from the M6 G-code, calculate its position, and perform the corresponding movements
#-----------------------------------------------------------

if hold_tool != new_tool:  # Ignore the code if hold_tool == new_tool

    if new_tool <= ToolCount:
        # Check that the new tool does not exceed ToolCount
        new_tool = (new_tool - 1) % ToolCount + 1
        print(f"------------------\n Loading the new tool: {new_tool}\n------------------")
    else:
        msg.info("Tool number called is too large.")
        sys.exit(1)  # Stop the program

    # Release the tool or open the clamp if there was no tool
    set_digital_output(valve_collet, DIOPinVal.PinSet)

    # Name the tool zero in SimCNC; in case of emergency stop, it is important that SimCNC knows there is no tool
    d.setToolOffsetNumber(0)

    # Pause for clamp opening
    time.sleep(0.5)

    # If the start of the script was skipped because of a zero tool, then replace Y
    # Otherwise, do not move because you are already at this location
    position[Y] = Y_position_first_tool
    d.moveToPosition(CoordMode.Machine, position, YX_speed)

    # Calculate the X position based on the tool number
    X_position_new_tool = X_position_first_tool + ((new_tool - 1) * X_distance_between_tools)

    # Raise Z to zero
    position[Z] = 0
    d.moveToPosition(CoordMode.Machine, position, Z_up_speed)

    # Verify that a tool has been properly released
    Read_if_tool_out(check_tool_in_spindle)
    Read_if_tool_out(check_clamp_status)

    # Move X above new tool
    position[X] = X_position_new_tool
    d.moveToPosition(CoordMode.Machine, position, YX_speed)

    # Move Z-axis in fast approach
    position[Z] = Z_position_approach
    d.moveToPosition(CoordMode.Machine, position, Z_down_fast_speed)

    # Clean the cone
    set_digital_output(valve_clean_cone, DIOPinVal.PinSet)

    # Move Z axis to final slow approach
    position[Z] = Z_position_tools
    d.moveToPosition(CoordMode.Machine, position, Z_down_final_speed)

    # Finish cleaning the cone
    set_digital_output(valve_clean_cone, DIOPinVal.PinReset)

    # Lock the tool
    set_digital_output(valve_collet, DIOPinVal.PinReset)

    # Pause
    time.sleep(0.5)

    # Indicate to SimCNC that the new tool is in place
    d.setToolLength(new_tool, new_tool_length)
    d.setToolOffsetNumber(new_tool)
    d.setSpindleToolNumber(new_tool)

    # Raise Z to zero after picking up the tool
    position[Z] = 0
    d.moveToPosition(CoordMode.Machine, position, Z_up_speed)

    # Check if a tool is in place
    Read_if_tool_in(check_tool_in_spindle)
    Read_if_tool_in(check_clamp_status)

    # Move the Y axis to a safe zone to avoid hitting other tools
    position[Y] = Y_position_safe_zone
    d.moveToPosition(CoordMode.Machine, position, YX_speed)

    print("-------------------\n End of tool change \n--------------------")

    #-----------------------------------------------------------
    # End of tool change movements
    #-----------------------------------------------------------
else:
    print(f"-------------------\n The tool {new_tool} is already in place \n--------------------")


else:
    print("-------------------\n Tool measurement cancelled, no probe installed \n--------------------")

# Return to the soft limit zone
position[Y] = Y_position_safe_zone
d.moveToPosition(CoordMode.Machine, position, YX_speed)

# Dust shoe back in place
set_digital_output(valve_dustCollect_under, DIOPinVal.PinSet)
time.sleep(2)
set_digital_output(valve_dustCollect_under, DIOPinVal.PinReset)

# Activate soft limits
d.ignoreAllSoftLimits(False)

# Export the new tool information to SimCNC
d.setToolLength(new_tool, new_tool_length)
d.setToolOffsetNumber(new_tool)
d.setSpindleToolNumber(new_tool)
