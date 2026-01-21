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

### Why not improve the Extended edition?

Alcater has not updated his version on Curseforge for more than 1.5 years, his version as many performance bottlenecks and weird approaches
to implementation of some features.


## **For development Java 25 is used!**
[JvmDowngrader](https://github.com/unimined/JvmDowngrader) to target Java 8 bytecode seamlessly while still using modern syntax and apis.


### General quickstart
1. Clone this repository.
2. Prepare JDK 25
3. Run task `setupDecompWorkspace` (this will setup workspace, including MC sources deobfuscation)
4. Ensure everything is OK. Run task `runClient` (should open minecraft client with mod loaded)


- Always use `gradlew` (Linux/MACOS) or `gradlew.bat` (Win) and not `gradle` for tasks. So each dev will have consistent environment.
### Development quirks for Apple M-chip machines.

Since there are no natives for ARM arch, therefore you will have to use x86_64 JDK (the easiest way to get the right one is IntelliJ SDK manager)

You can use one of the following methods:
- GRADLE_OPTS env variable `export GRADLE_OPTS="-Dorg.gradle.java.home=/path/to/your/desired/jdk"`
- additional property in gradle.properties (~/.gradle or pwd) `org.gradle.java.home=/path/to/your/desired/jdk`
- direct usage with -D param in terminal `./gradlew -Dorg.gradle.java.home=/path/to/your/desired/jdk wantedTask`

#### Troubleshooting:

1. If you see that even when using x86_64 JDK in logs gradle treats you as ARM machine. Do following:
    1. Clear workspace `git fetch; git clean -fdx; git reset --hard HEAD` (IMPORTANT: will sync local to git, and remove all progress)
    2. Clear gradle cache `rm -rf ~/.gradle` (IMPORTANT: will erase WHOLE gradle cache)
    3. Clear downloaded JVMs `rm -rf /path/to/used/jvm`
       (path to used jvm can be found in /run/logs/latest.log like this `Java is OpenJDK 64-Bit Server VM, version 1.8.0_442, running on Mac OS X:x86_64:15.3.2, installed at /this/is/the/path`)
    4. Repeat quickstart.
