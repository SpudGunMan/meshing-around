# Modules and Adding stuff

To help with code testing see `etc/simulator.py` to simulate a bot. I also enjoy meshtasticd(linux-native) in noradio with MQTT server and client to just emulate a mesh.

## By following these steps, you can add a new bbs option to the bot.

1. **Define the Command Handler**:
   Add a new function in mesh_bot.py to handle the new command. For example, if you want to add a command `newcommand`:
   ```python
   def handle_newcommand(message, message_from_id, deviceID):
       return "This is a response from the new command."
   ```
2. **Add the Command to the Auto Response**:
   Update the auto_response function in mesh_bot.py to include the new command:
   ```python
   def auto_response(message, snr, rssi, hop, pkiStatus, message_from_id, channel_number, deviceID, isDM):
       #...
       "newcommand": lambda: handle_newcommand(message, message_from_id, deviceID),
       #...
   ```
3. **Update the Trap List and Help**:
    A quick way to do this is to edit the line 16/17 in `modules/system.py` to include the new command:
    ```python
    #...
    trap_list = ("cmd", "cmd?", "newcommand")  # default trap list, with the new command added
    help_message = "Bot CMD?:newcommand, "
    #...
    ```

    **If looking to merge** the prefered way would be to update `modules/system.py` Adding this block below `ping` which ends around line 28:
    ```python
    # newcommand Configuration
    newcommand_enabled = True  # settings.py handles the config.ini values; this is a placeholder
    if newcommand_enabled:
         trap_list_newcommand = ("newcommand",)
         trap_list = trap_list + trap_list_newcommand
         help_message = help_message + ", newcommand"
    ```

5. **Test the New Command**:
   Run MeshBot and test the new command by sending a message with the command `newcommand` to ensure it responds correctly.