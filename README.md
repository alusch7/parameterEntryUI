# parameterEntryUI
A UI for Windows that enables easy value entry for programs with numeric variables that need to change from run to run. Also supports value ranges. Designed with Opentrons protocols in mind.

# Setup
### Folder Setup
On your desktop, create two new folders. Name one *PermDir* and the other *WorkingDir*.
***PermDir***: store all of your source code files, the ones you want to set parameters for. You can have multiple protocols in this folder.
***WorkingDir***: leave this empty. WorkingDir will pop up after you press save in the program, with a copy of the modified file for easy access.

### Code Setup
In the parapeterEntryUI.py file find lines 17, 217, and 233 and change their paths appropriately:
- Line 17: point to the *PermDir* folder
- Line 217: point to any destination that you wish the log file to be written to (e.g. C:\\Users\\USERNAME\\Desktop\\Log.txt)
- Line 233: point to the *Working Dir* folder

# Writing Code for parameterEntryUI
Your code must contain two sections (in the given order) specifically written for parameterEntryUI.

### Section 1:
This is the section of the code that contains the variables you wish to change through ParameterEntryUI. You must wrap any variables that you want to be changed in two comments:
#\inputstart
#\inputend

For example, if you want var1, var2, and var3 to be editable, you must write:
```
#inputstart
var1 = 0
var2 = 0
var3 = 0
#inputend
```
### Section 2:
This is the section of code that contains the ranges for the previous variables. You must write them in the same order as their corresponding variables. If a value has no range, provide it with an empty range (e.g. []). Again, you must wrap the ranges in two comments:
#\rangestart
#\rangeend

For example, if the ranges are var1 [0,10], var2 [-5, 10], and var3 = any value:
```
#rangestart
var1range = [0, 10]
var2range = [-5, 10]
var3range = []
#rangeend
```
***NOTE: Ranges are inclusive!***

### Important Notes:
You **MUST** put both the variable and range declarations ***before line 50*** in the source code files. There is a hard-coded cutoff at line 50 for runtime speed purposes so that the program does not scan an entire multi-thousand line file for the keyword comments and freeze up while it is doing so.

While the program automatically pops up the *WorkingDir* with a *copy* of the modified file, it is important to note that this does not mean the original files in the *PermDir* are not also modified -- they are.
