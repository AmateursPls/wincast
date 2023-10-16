from argparse import ArgumentParser
import win32gui, win32process
from pathlib import Path
from time import sleep
import subprocess
import pathlib
import psutil
import os

# Returns a parsed Path object based on if absolute or relative
def getParsedPathName(pathName):
    if Path(pathName).is_absolute():
        return Path(pathName).absolute()
    else:
        return Path(currentWorkingDirectory / pathName).absolute()

# Returns a list of Window Titles from a given Process ID
# Code adapted from the following Stack question:
# https://stackoverflow.com/questions/51418928/find-all-window-handles-from-a-subprocess-popen-pid
def getWindowTitlesFromProcessID(pid):
    def callback (hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    windowTitles = []
    for hwnd in hwnds:
        windowTitles.append(win32gui.GetWindowText(hwnd))
    return windowTitles

# Returns the game title from the ROM Path for use in creating our partial txt file
def getGameTitleFromRomPath(romPath, isRPCS3=False):
    if isRPCS3:
        if "EBOOT.BIN" in commandLineArguments.rom:
            return str(romPath.absolute()).rsplit("\\", 4)[1].split("\\", 1)[0]
    return str(romPath.absolute()).rsplit(".", 1)[0].rsplit("\\", 1)[1]

# Parser for accepting the command-line arguments
commandLineParser = ArgumentParser(
    prog = "RetroArch WindowCast Wrapper"
)

# Define the command-line arguments we will utilise
commandLineParser.add_argument("--emulator", required=True, \
help="The path to the standalone emulator (or game exe) you're running")

commandLineParser.add_argument("--retroarch", required=True, \
help="The path to your retroarch.exe")

commandLineParser.add_argument("--partialdir", default=None, \
help="(OPTIONAL) The path to the directory you want to store the partial txt files")

commandLineParser.add_argument("--emulator_args", default=None, \
help="(OPTIONAL) You can use this to pass arguments to the standalone emulator (or game) on launch if you need to for some reason. \
This is a fairly crude implementation, I wouldn't expect much from it/would expect bugs if I were you. \
You're much better off just configuring your emulator as necessary in the UI.")

commandLineParser.add_argument("--waitduration", type=int, default=10, \
help="(OPTIONAL) Specifies the time in seconds to wait for standalone emulator to load. \
Setting to a higher value should assist slow computers and slow HDDs. \
Default = 5")

commandLineParser.add_argument("--rom", default=None, \
help="(OPTIONAL) The path to the rom you're running. \
If you're launching a game instead of an emulator, don't pass any argument to this.")

# Parse the command-line arguments into a usable object
commandLineArguments  = commandLineParser.parse_args()

# Get the directory this utility is being ran from as a Path()
# Ignoring the filthily-chained 1-liner, this can't be the best way to do this can it? Was the best I could find, though.
currentWorkingDirectory = Path(os.path.abspath("."))

# Standalone emulator executable as Path instance
emulatorExePath = getParsedPathName(commandLineArguments.emulator)

# RetroArch executable as Path instance
retroarchExePath = getParsedPathName(commandLineArguments.retroarch)

# Rom file as Path instance, if undefined at runtime we'll assume we're launching a game instead of an emulator
if commandLineArguments.rom:
    romFilePath = getParsedPathName(commandLineArguments.rom)

# Partial files directory as Path instance
if not commandLineArguments.partialdir:
    partialDirPath = currentWorkingDirectory
else:
    # Use this path instead if an argument is specified at runtime
    partialDirPath = getParsedPathName(commandLineArguments.partialdir)
    # If the passed directory for storing the txt files doesn't exist, create it
    if not partialDirPath.exists():
        partialDirPath.mkdir(parents=True, exist_ok=True)

# Null output so we can prevent games/emulators with a console output holding us up
# This might be completely unnecessary, idk tbh
nullOutput = open(os.devnull, "w")

# Construct our arguments to pass to the emulator
if not commandLineArguments.emulator_args:
    if commandLineArguments.rom:
        emulatorArgumentsToPass = romFilePath
    else:
        emulatorArgumentsToPass = ''
else:
    # This is a very crude implementation of the arguments and doesn't support the only useful use-case I can think of
    # (Assigning per-game configs to support per-game user input settings)
    # TODO then actually, I guess
    standaloneSwitches = commandLineArguments.emulator_args.split()
    emulatorArgumentsToPass = ""
    for switch in standaloneSwitches:
        emulatorArgumentsToPass += "--{} ".format(switch)
    emulatorArgumentsToPass += '"{}"'.format(str(romFilePath))

# Run the standalone emulator
emulatorProcess = subprocess.Popen([emulatorExePath, emulatorArgumentsToPass], stderr=nullOutput, stdout=nullOutput)

# Dump the stdout and stderr of the ran emulator (or game)
nullOutput.close

# List to hold all window title(s) found from the standalone emulator (or game)
windowTitles = []

# Halt here while we wait for a window to appear
firstLoop = True
# A list containing our original process, and if necessary, all child processes
processesToSniff = [emulatorProcess]
while len(windowTitles) == 0:
    # This is our second attempt, so start scanning any potential child processes
    # This could probably be expanded upon to handle launchers and the such where we know the parent process isn't what we're after
    # TODO ^
    if not firstLoop:
        parentProcess = psutil.Process(emulatorProcess.pid)
        childrenProcesses = parentProcess.children(recursive=True)
        for childProcess in childrenProcesses:
            processesToSniff.append(childProcess)
    # Time (in seconds) to wait for window(s) to load after executing the emulator
    sleep(commandLineArguments.waitduration)
    for eachProcess in processesToSniff:
        windowTitles = getWindowTitlesFromProcessID(eachProcess.pid)
    if firstLoop:
        firstLoop = False

# Set the window title we actually want to work with
desiredWindowTitle = windowTitles[0]

# Track if the running content is RPCS3 to avoid creating a partial file named "EBOOT"
contentIsRPCS3 = False

# For now we're just going to crudely assume that if there's more than one window we're dealing with RPCS3
# Is anybody even using this for RPCS3 though? I feel like PS3 is after the cutoff for CRT/scanline shenanigans
if len(windowTitles) == 2:
    contentIsRPCS3 = True
    for window in windowTitles:
        if "RPCS3" in window:
            pass
        else:
            # RPCS3 reports the FPS in the window title so we need to trim it down
            # For now, going to leave the Game ID (for example [BLUS12345]) in
            try:
                desiredWindowTitle = window.rsplit(" | ", 1)[1]
            except:
                # this code is getting very gross, really need to rewrite it already
                # Even though this is as flagged as RPCS3 = True, it's actually not, this is to handle Dolphin
                desiredWindowTitle = window

# Grab the folder name of the emulator for cleaner storage of the partial.txt files
# Also enables mimicking "Per Core" shader settings by using Content Directory
if commandLineArguments.rom:
    standaloneFolderName = str(emulatorExePath).rsplit("\\", 1)[0].rsplit("\\", 1)[1]
# No rom defined so let's use the generic name 'win32' here to specify we're loading a game not an emulator
else:
    standaloneFolderName = "win32"

# If a ROM is passed at runtime then let's get the title of that ROM
if commandLineArguments.rom:
    gameTitleForPartialFile = getGameTitleFromRomPath(romFilePath, contentIsRPCS3)
# No ROM passed so let's just use the exe file name, which is not perfect but it will do.
else:
    gameTitleForPartialFile = str(emulatorExePath).rsplit("\\", 1)[1].split(".")[0]

# The path we'll create to hold our partial txt files
pathToCreate = partialDirPath / standaloneFolderName

# Check if it already exists
if not pathToCreate.exists():
    pathToCreate.mkdir(parents=True, exist_ok=False)

# Save the Path reference to the txt file we create to load in Retroarch
partialTextFile = str(Path(pathToCreate / gameTitleForPartialFile)) + ".txt"

# Write the actual txt file to the directory we created using the Game Title we extracted earlier
with open(partialTextFile, "w", encoding="utf-8") as textFile:
    textFile.write(desiredWindowTitle)

# Get an absolute path to the WindowsCast DLL to be referenced when calling RetroArch 
winCastCorePath = Path(str(retroarchExePath).rsplit("\\", 1)[0] + "\\cores\\wgc_libretro.dll")

retroarchLaunchString = '{} -L "{}" "{}"'.format(retroarchExePath, winCastCorePath, partialTextFile)

# Launch retroarch with our desired paramaters. Using os.walk cos subprocess.call doesn't wanna play ball.
os.system(retroarchLaunchString)

for process in processesToSniff:
    process.terminate()