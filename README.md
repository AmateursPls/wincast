
# A simple python wrapper for the RetroArch WindowCast core

The [WindowCast core](https://forums.libretro.com/t/official-release-thread-for-windowcast-core/40464) for Retroarch is, imo, one of the coolest things to happen in emulation in quite a while - With this core you can now **FINALLY** run the full suite of Shaders and Bezels/Overlays available to Retroarch in any standalone emulator, including the systems that have traditionally suffered in Retroarch like [PCSX2](https://pcsx2.net/), [Dolphin](https://dolphin-emu.org/) and the never-before-supported [xemu](https://xemu.app/). (Yes I know WindowCast has been around for a while now, but I only just discovered it XD)

The only problem? It's not entirely intuitive on how to leverage it, it seemingly doesn't intergrate nicely or easily with frontends like [Pegasus](https://pegasus-frontend.org/) or [Launchbox](https://www.launchbox-app.com/) and it requires too much manual intervention in terms of loading up games or even exiting when done.

That's where this simple wrapper comes into the picture \o/ Download here: [here](https://github.com/AmateursPls/wincast/releases/download/release/wincast_v01.zip)

With this little tool you can simply point a few command-line arguments to the tool and get near-native-core support for your standalone emulators in RetroArch.

### Usage in Pegasus-Frontend

Set the wincast.exe as your launch "emulator" in the metadata file, pass a few command-line arguments (supporting relative or absolute paths for that sweet, sweeeet portability), and voila

launch: .\\..\\..\\Emulators\\RetroArch\\wincast.exe --emulator ".\\..\\..\\Emulators\\PCSX2\\pcsx2-qtx64-avx2.exe" --retroarch ".\\..\\..\\Emulators\\RetroArch\\retroarch.exe" --rom "{file.path}"

It's that simple. Unfortunately I don't have Launchbox anymore so can't provide a word-for-word example on that, but iirc it should be as easy as adding wincast.exe as an emulator for your desired platform, passing the arguments to your emulator.exe, retroarch.exe and then passing through `{rom.file}` or whatever it is as the final argument for `--rom`

It also supports running your more modern standalone Windows games with pixel art like Triangle Strategy:

wincast.exe --emulator "E:\Games\Windows\Octopath Traveler\Octopath_Traveler.exe"  --retroarch "..\retroarch.exe"

Some effort has been made to handle things intelligently, for example if a game loads a slave process (as Triangle Strategy in that example does), it will still capture the correct window to pass to RetroArch, and when you exit RetroArch, terminate the correct process.

### Features

- Automatically creates the partial.txt files necessary for capturing the correct window to pass through to RetroArch
- When you quit RetroArch, it will also quit the launched Emulator/Game
- Supports "per-core" shader/config settings in RetroArch (by way of leveraging the 'Content Directory" save type)
- Supports per-game shader/config settings in RetroArch
- Can define the directory to use to store the partial-match.txt files by using the `--partialdir` command-line argument - If no argument is passed it will use the location of where wincast.exe is placed, so put it somewhere logical. Personally I created a wincast folder in RetroArch, and keep wincast.exe inside of it.
- Supports relative or absolute paths for all arguments you pass
- Has support for passing command-line arguments to the standalone emulators/games themselves (although this is currently a very crude implementation requiring some extra work)

### TODO
- Fix/improve passing command-line arguments to standalone emulators/games
- More intelligent handling of windows and child processes to support opening a game that needs to be opened with a launcher, then loads the *real* window.
- Capturing an xinput controller combination (I'm thinking Up+Select) to pass Ctrl-Alt-T to RetroArch - The only reason I didn't implement this is because it seems I no longer need it after changing the setting advised to change in the Nvidia Control Panel by the WindowCast Readme
- Further testing
- A schite-load of inevitable bugfixing

### Output of --help
**usage**: RetroArch WindowCast Wrapper [-h] --emulator EMULATOR --retroarch RETROARCH [--partialdir PARTIALDIR] [--emulator_args EMULATOR_ARGS] [--waitduration WAITDURATION] [--rom ROM]

optional arguments:
-  `-h, --help`            show this help message and exit
-  `--emulator EMULATOR`   The path to the standalone emulator (or game exe) you're running
-  `--retroarch RETROARCH`
                        The path to your retroarch.exe
-  `--partialdir PARTIALDIR`
                        (OPTIONAL) The path to the directory you want to store the - partial txt files
 - `--emulator_args` EMULATOR_ARGS
                        (OPTIONAL) You can use this to pass arguments to the standalone emulator (or game) on launch if you need to for some reason. This is a fairly crude implementation, I wouldn't expect much from it/would expect bugs if I were you. You're much better off just configuring your emulator as necessary in the UI.
-  `--waitduration WAITDURATION`
                        (OPTIONAL) Specifies the time in seconds to wait for standalone emulator to load. Setting to a higher value should assist slow computers and slow HDDs. Default = 5
-  `--rom ROM`             (OPTIONAL) The path to the rom you're running. If you're launching a game instead of an emulator, don't pass any argument to this.

### Warning
I didn't test this nearly as much as I should've. I am **not** a programmer. There **will be** bugs. Your mileage will vary. So far in my limited testing, it has exceeded all expectations, but that doesn't mean much.

Personally I've had best results using fullscreen 16:9 stretched (despite the advice of the WindowCast readme), and then letting the [HSM MegaBezel](https://forums.libretro.com/t/mega-bezel-reflection-shader-feedback-and-updates/25512) pack downscale it back to 4:3 like is (was?) suggested for the native cores.

I strongly advise you to read the WindowCast readme thorougly - Particulary the part about the setting to toggle in the NVidia Control Panel if you have an NVidia card. Experiment with the Vulkan, Software and D3D versions of the core. Trial and error is key here right now, to be honest. This tool helps, but it far from solves every edge case.

### Thanks
All thanks and credit goes to IHQMD over at the Libretro forums for the WindowCast core. Amazing work by him.

o7
