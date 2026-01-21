<div dir=rtl align=center>

### **English 🇺🇸** 
</div>


<h1 align="center"> HBM's Nuclear Tech Mod Community Edition  <br>
	<a href="https://www.curseforge.com/minecraft/mc-mods/hbm-nuclear-tech-mod-community-edition"><img src="http://cf.way2muchnoise.eu/1312314.svg" alt="CF"></a>
    <a href="https://modrinth.com/mod/ntm-ce"><img src="https://img.shields.io/modrinth/dt/ntm-ce?logo=modrinth&label=&suffix=%20&style=flat&color=242629&labelColor=5ca424&logoColor=1c1c1c" alt="Modrinth"></a>
	<a href="https://discord.gg/eKFrH7P5ZR"><img src="https://img.shields.io/discord/1241479482964054057?color=5865f2&label=Discord&style=flat" alt="Discord"></a>
    <br>
</h1>


>  If you have Universal Tweaks installed, set `B:"Disable Fancy Missing Model"` to `false` to fix**  
>  can be found at `config/Universal Tweaks - Tweaks.cfg`

<br>
<br>

### Is the mod compatible with NTM: Extended edition addons/shaders?

Sadly, no. Installing EE addons will most likely result in crashes, making the modpack unplayable; due to having the new gun system ported, shaders
are also incompatible and will cause heavy visual artifacts when holding a gun. <br>
Also shaders are incompatible with NTM skybox; this can be fixed in 'config/hbm -> hbm.cfg' by changing the line 'B:1.00_enableSkybox=true' to 'false'. <br>

### How different is it from Extended edition?

**Extended worlds are fully incompatible!** <br>

- Always use `gradlew` (Linux/MACOS) or `gradlew.bat` (Win) and not `gradle` for tasks. So each dev will have consistent environment.
### Development quirks for Apple M-chip machines.

#### Troubleshooting:

1. If you see that even when using x86_64 JDK in logs gradle treats you as ARM machine. Do following:
    1. Clear workspace `git fetch; git clean -fdx; git reset --hard HEAD` (IMPORTANT: will sync local to git, and remove all progress)
    2. Clear gradle cache `rm -rf ~/.gradle` (IMPORTANT: will erase WHOLE gradle cache)
    3. Clear downloaded JVMs `rm -rf /path/to/used/jvm`
       (path to used jvm can be found in /run/logs/latest.log like this `Java is OpenJDK 64-Bit Server VM, version 1.8.0_442, running on Mac OS X:x86_64:15.3.2, installed at /this/is/the/path`)
    4. Repeat quickstart.

