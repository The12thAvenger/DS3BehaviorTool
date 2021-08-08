# DS3BehaviorXMLTool
Tool for editing Dark Souls 3 Behavior XML files, currently supports:  
-hkbClipGenerators  
-hkStateMachineStateInfos  
-hkManualSelectorGenerators  
-CustomManualSelectorGenerators  
-hkVariableBindingSets  

Registers animations for tae sections, skipping any that are already present, meaning you don't need to worry about accidental duplicates.   
Customizable config and presets for mass editing, please read config.ini before use.  
Supports registering to any CustomManualSelectorGenerator  
Supports creation of CMSGs for regular attacks and hkManualSelectorGenerators for weapon arts.  
Can currently only load behavior file from the same folder as the .exe and .ini files.  
