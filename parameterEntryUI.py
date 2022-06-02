import tkinter as tk
import os
import ast
from datetime import datetime
import shutil
import subprocess

#Window Configuration
root = tk.Tk()
root.minsize(500, 300)
root.title('OpenTrons Configuration')
root.grid_columnconfigure(0, weight=0) 
root.grid_columnconfigure(1, weight=1) 

# Global Variables
# Define path for source files
path = 'C:\\Users\\USERNAME\\Desktop\\PermDir\\'
# Keeps track of how many parameters were in the previously selected file when
# you select a new file
prevNumParam = 0
# Lists of entry box and label elements
entryBoxes = []
entryLabels = []
rangeLabels = []
# List of all provided range parameters
rangeList = []
# List of line numbers where parameters are located in the selected file
parameterLocation = []
# File name to print to log
fileNameForLog = "None"
# Currently selected file in the file selector
selectedFile = ""

# Title
protocolListTitle = tk.Label(root, text = "Protocol List", font='Helvetica 18 bold')
protocolListTitle.grid(row = 0, columnspan = 4)

# Listbox Configuration (Listbox is the file selector)
fileList = os.listdir(path)
listbox = tk.Listbox(root, selectmode='single', exportselection=0)
listbox.grid(row = 1, columnspan = 4, sticky = "nsew")
# For each file in the fileList, display it in the listbox
for i in range(len(fileList)):
    listbox.insert(tk.END, fileList[i])

# Select Button Action
def select(event):
    # Get access to read/write the following global vars
    global prevNumParam, entryBoxes, entryLabels, rangeLabels, parameterLocation, path, rangeList, fileNameForLog, selectedFile
    # Event is when you click on a file in the listbox, so get its current selection
    selection = event.widget.curselection() 
    # If something is selected, display the selected file in the
    # displaySelectedFile label and change the file name that gets printed
    # to the log file to whatever is selected
    if selection:
        index = selection[0]
        selectedFile = event.widget.get(index)
        displaySelectedFile.config(text=selectedFile)
        fileNameForLog = selectedFile
    # Create the full file path with the general path + file name
    filePath = path+str(selectedFile)
    # Count how many lines have been read
    lineCount = 0
    # List of user-inputtable parameters
    parametersList = []
    # Clear global lists from earlier
    parameterLocation = []
    rangeList = []
    # Open the file in read mode
    editFile = open(filePath, 'r')
    # readState checks if you want to be moving whatever is being read into 
    # the list of parameters 
    readState = False
    for line in editFile:
        # if the line reads #inputend then stop reading the file
        if line == "#inputend\n":
            break
        # if the readState is true, split the line at the = sign, store
        # whatever was on the left side of the var name into the parametersList
        # and store the line number in the parameterLocation list
        if readState == True:
            nameSection = line.split("=",1)
            varName = nameSection[0]
            parametersList.append(varName)
            parameterLocation.append(lineCount)
        # if the line reads #inputstart then start moving whatever is being read
        # into the parameterList (above)
        if line == "#inputstart\n":
            readState = True
        lineCount+=1
        # if the line count reaches 50 without finding anything stop reading
        # the file. This makes things a lot snappier but it also means that parameters
        # and ranges cannot be below line 50 in the selected file. They should
        # be as close to the top as possible.
        if lineCount == 50:
            break
    # Same as the earlier block, but to read the ranges
    readState = False
    lineCount = 0
    for line in editFile:
        if line == "#rangeend\n":
            break
        if readState == True:
            # The following lines take a range (e.g." [2,5]\n") and turn it
            # into [2,5] and then append that to the list of given ranges
            acceptableRange = line.split("=",1)
            acceptableRange = acceptableRange[1].replace("\n", "")
            acceptableRange = acceptableRange.replace(" ", "")
            rangeList.append(ast.literal_eval(acceptableRange))
        if line == "#rangestart\n":
            readState = True
        lineCount+=1
        if lineCount == 50:
            break
    # Destroy every entry label, box, and range label that was displayed 
    # for the previously selected file
    for i in range(prevNumParam):
        entryLabels[i].destroy()
        entryBoxes[i].destroy()
        rangeLabels[i].destroy()
    # Clear the contents of every entry label, box, and range label that was
    # assigned values from the previously selected file
    entryBoxes.clear()
    entryLabels.clear()
    rangeLabels.clear()
    """Both destroy and clear are required because clear only clears the contents of 
    the widget lists. You must destroy each existing widget so that it does not
    create duplicates upon the next selection and try to place them on top 
    of the already existing widgets.Then you must clear the lists containing
    the widgets in order to refresh the number of widgets and their values"""
    # Create a label and entry box for each parameter in parametersList as well
    # as a label for each range in rangeList
    for i in range(len(parametersList)):
        entryBoxes.append(tk.Entry(root))
        entryLabels.append(tk.Label(root, text=(str(parametersList[i]).replace("_", " "))))
        rangeLabels.append(tk.Label(root, text= ("Range: "+str(rangeList[i]))))
    # Variable to correctly space out the labels in the window
    stagger = 0;
    # Display entry labels, boxes and range labels in the window
    for i in range(len(parametersList)):
        if i != 0:
            stagger += 1
        entryLabels[i].grid(row =i+3+stagger, column = 0,  sticky = "w")
        entryBoxes[i].grid(row =i+3+stagger, column = 1, columnspan = 3, sticky = "ew")
        rangeLabels[i].grid(row =i+4+stagger, column = 1,  columnspan = 3,  sticky = "w")
    # Store how many parameters there are in parametersList so that you know
    # how many widgets need to be deleted when a new file is selected
    prevNumParam = len(parametersList)
    # Close the file that we were reading
    editFile.close()

# Check if There is a Range
def noRange(list):
    if not list:
        return True

# Edit File Variables Function (writes out the user-given values)
def editVarFunc():
    # Bool to check if the write out was successful which depends on wether
    # or not the input was acceptable
    success = True
    # For each value in given by the user in the entry boxes
    for i in range(len(entryBoxes)):
        curr = entryBoxes[i].get()
        currRange = rangeList[i]
        # Try to convert the given value from a string which is the automatic
        # type for an entryBox to an int or a float (e.g. "5.5" to 5.5)
        try:
            curr = int(curr)
        except:
            try:
                curr = float(curr)
            except:
                pass
        # if the value is now a float or int and it's value is positive and it
        # is within the provided range then write out it's value at the 
        # appropriate line and in the appropriate spot
        if (((isinstance(curr, int) or isinstance(curr, float))) and 
        (noRange(currRange) or (currRange[0] <= curr <= currRange[1])) ) :
            filePath = path+str(listbox.get('anchor'))
            writeFile = open(filePath, 'r')
            lines = writeFile.readlines()
            getLine = lines[parameterLocation[i]]
            value = getLine.split("=",1)
            newLine = value[0]+"="+str(curr)+"\n"
            lines[parameterLocation[i]] = newLine
            writeFile = open(filePath, "w")
            writeFile.writelines(lines)
            writeFile.close()
        # if the value fails this check then replace whatever the user entered
        # with INVALID INPUT, display "Failed!" and change the success 
        # Bool to false
        else:
            entryBoxes[i].delete(0,'end')
            entryBoxes[i].insert(0,"INVALID INPUT")
            unsavedLabel()
            success = False
    # return wether or not the write was successful
    return success

# Display "Saved!" Label fpr 5 seconds
def savedLabel():
    successLabel = tk.Label(root, text = 'Saved!', fg = '#ffffff', bg = '#03970b')
    successLabel.grid(row = 20, columnspan = 3, sticky = 'e')
    successLabel.after(5000, lambda: successLabel.destroy())

# Display "Failed!" Label for 5 seconds
def unsavedLabel():
    failedLabel = tk.Label(root, text = 'Failed!', fg = '#ffffff', bg = '#d31818')
    failedLabel.grid(row = 20, columnspan = 3, sticky = 'e')
    failedLabel.after(5000, lambda: failedLabel.destroy())

# Write out the operator's name, the program run, and the date & time
# to a log.txt file
def logFile(operatorName):
    global fileNameForLog
    writePath = "C:\\Users\\USERNAME\\Desktop\\Log.txt"
    writeFile = open(writePath, 'a')
    writeFile.write("\n")
    writeFile.write("===============================================")
    writeFile.write("\n")
    operatorName = str("Accessed by: " + operatorName)
    writeFile.write(fileNameForLog)
    writeFile.write("\n")
    writeFile.write(operatorName)
    writeFile.write("\n")
    now = datetime.now()
    dateAndTime = str("Date & Time: " + now.strftime("%d/%m/%Y, %H:%M:%S"))
    writeFile.write(dateAndTime)
    
# Copy the file from the permanent directory to the working directory
def copyFile():
    workingDir = "C:\\Users\\USERNAME\\Desktop\\WorkingDir\\"
    # Erase anything already in the working directory
    for f in os.listdir(workingDir):
        os.remove(os.path.join(workingDir, f))
    # Copy the file from PermDir to WorkDir
    shutil.copy(str(path+selectedFile), workingDir)
    # Open the file path in an explorer window for easy user access
    filePath = str(workingDir+selectedFile)
    subprocess.Popen(r'explorer /select,"{}"'.format(filePath))
     
# Attempt to save all inputted values
def save():
    # Get the current name from the entry box, convert them to str
    currName = str(nameEntry.get())
    # If the entered values for name are only alphabetic/spaces and
    # the value is not "INVALID INPUT" or nothing at all, then display "Saved!",
    # write to the log file, run the copy file method, tell the user to drag
    # the file to opentrons, and then quit the window once they say ok
    if (editVarFunc() and ((currName != '' and currName != "INVALID INPUT") and (all(char.isalpha() or char.isspace() for char in currName) 
    ))):
        savedLabel()
        logFile(currName)
        copyFile()
        root.after(3000, lambda: root.destroy())
    # If the name was an invalid input then replace the user input
    # with INVALID INPUT 
    if (currName == '' or currName == "INVALID INPUT" or not (all(char.isalpha() or char.isspace() for char in currName))):
        nameEntry.delete(0,'end')
        nameEntry.insert(0,"INVALID INPUT")
        unsavedLabel()

# Name Entry Box/Label
nameEntry = tk.Entry(root)
nameEntry.grid(row = 18, column = 2, columnspan = 2)
nameEntryLabel = tk.Label(root, text = 'Full Name')
nameEntryLabel.grid(row = 18, column = 0, sticky = "w")
credentialsTitle = tk.Label(root, text = "Credentials: ", font='Helvetica 16 bold')
credentialsTitle.grid(row = 17, column = 0, sticky = 'w')

# Widgets
saveButton = tk.Button(root, text='Save', command=save)
selectedFileTextLabel = tk.Label(root, text = "Selected File: ", font='Helvetica 16 bold')
displaySelectedFile = tk.Label(root, text = 'None')
listbox.bind("<<ListboxSelect>>", select)
selectedFileTextLabel.grid(row = 2, column = 0, columnspan = 1, sticky="w")
displaySelectedFile.grid(row = 2, column = 1, columnspan = 2, sticky="w")
saveButton.grid(row = 20, column = 3, sticky = "e")

root.mainloop()