import shutil
import sys
from lxml import etree
from pathlib import Path, PosixPath
import configparser
import collections
import os
from io import StringIO
import copy
import subprocess
import stat
from shutil import copyfile
import copy

def CallRegisterAnibnd(taeID, taeSubID):
    return subprocess.run([os.path.join(exeFolder, "Dependencies\AniBNDRegister\AniBNDRegister.exe"), sys.argv[1], taeID, taeSubID])

def CallYabber(filePath):
    return subprocess.run([os.path.join(exeFolder, "Dependencies\Yabber\Yabber.exe"), filePath])

def CallHkxPackSoulsDs3(filePath):
    return subprocess.run([os.path.join(exeFolder, "Dependencies\hkxpack-souls\hkxpack-souls.exe"), filePath])

# get next free NameID
def GetNameID():
    NameID = 90
    for name in __data__.findall("hkobject[@name]"):
        NameID += 1
    return NameID

def GetEventID():
    EventID = 0
    for event in __data__.findall("hkobject[@class='hkbBehaviorGraphStringData']/hkparam[@name='eventNames']/hkcstring"):
        EventID += 1
    return EventID

#check SM for next available stateId
def GetStateID(StateMachine):
    for SM in __data__.findall("hkobject[@class='hkbStateMachine']"):
        if SM.find("hkparam[@name='name']").text == StateMachine:
            transitions = SM.find("hkparam[@name='wildcardTransitions']").text
            break

    for TransitionInfoArray in __data__.findall('hkobject[@class="hkbStateMachineTransitionInfoArray"]'):
        if TransitionInfoArray.get("name") == transitions:
            StateID = 200
            while True:
                for toStateId in TransitionInfoArray.findall('hkparam[@name="transitions"]/hkobject/hkparam[@name="toStateId"]'):
                    if int(toStateId.text) == StateID:
                        StateID += 1
                        break
                else:
                    return StateID

def GetUserData(StateMachineName):
    for SM in __data__.findall("hkobject[@class='hkbStateMachine']"):
        if SM.find("hkparam[@name='name']").text == StateMachineName:
            hkbStateMachine = SM
            break

    UserData = None
    CMSGList = []
    for SMSIName in hkbStateMachine.find('hkparam[@name="states"]').text.split():
        for SMSI in __data__.findall('hkobject[@class="hkbStateMachineStateInfo"]'):
            if SMSI.get("name") == SMSIName:
                hkbStateMachineStateInfo = SMSI 
                break

        GeneratorName = hkbStateMachineStateInfo.find('hkparam[@name="generator"]').text

        CMSGFound = False
        while CMSGFound == False:
            for hkobject in __data__.findall('hkobject'):
                if hkobject.get("name") == GeneratorName:
                    if hkobject.get("class") == "CustomManualSelectorGenerator":
                        CMSGFound = True
                        CMSGList.append(GeneratorName)
                        if UserData == None:
                            UserData = int(hkobject.find('hkparam[@name="userData"]').text)
                        break
                    elif hkobject.get("class") == "hkbScriptGenerator":
                        GeneratorName = hkobject.find('hkparam[@name="child"]').text
                        break
                    elif hkobject.get("class") == "hkbManualSelectorGenerator":
                        CMSGFound = True
                        for generator in hkobject.find('hkparam[@name="generators"]').text.split():
                            CMSGList.append(generator)
                        break
                    else:
                        print("CMSG " + GeneratorName + " not found")

    shouldBreak = False
    while True:
        for CMSGName in CMSGList:
            if shouldBreak == True:
                shouldBreak = False
                break
            for CMSG in __data__.findall('hkobject[@class="CustomManualSelectorGenerator"]'):
                if CMSG.get("name") == CMSGName:            
                    if int(CMSG.find('hkparam[@name="userData"]').text) == UserData:
                        UserData += 1
                        shouldBreak = True
                    break
            else:
                print(CMSGName + " is not a CustomManualSelectorGenerator")
        else:
            return UserData

<<<<<<< HEAD
def GetLayerGenParams():
    isValid = False
    while isValid != True:
        LayerGenName = RemoveSuffix(str(input('Enter LayerGenerator name: ')), "_LayerGenerator")
        if LayerGenName == "":
            print("Invalid input")
            continue
        else:
            isValid = True

    isValid = False
    while isValid != True:
        LayerGenParentName = str(input('Enter parent ScriptGenerator (e.g. AttackRight_Script): '))
        if LayerGenParentName == "":
            print("Invalid input")
            continue
        for ScriptGen in __data__.findall('hkobject[@class="hkbScriptGenerator"]'):
            if LayerGenParentName.lower() in [ScriptGen.find('hkparam[@name="name"]').text.lower(), RemoveSuffix(ScriptGen.find('hkparam[@name="name"]').text.lower(), "_Script"), RemoveSuffix(ScriptGen.find('hkparam[@name="name"]').text.lower(), " Script")]:
                ScriptGenerator = ScriptGen
                isValid = True
                break
        else:
            print("No hkbScriptGenerator with name " + LayerGenParentName + " found")

    isValid = False
    while isValid != True:
        LayerGenStartAnimIDStr = str(input('Enter starting AnimID for blend anims: '))
        try:
            LayerGenStartAnimID = int(LayerGenStartAnimIDStr)
        except:
            print("Invalid input")
            continue

        if LayerGenStartAnimID == "":
            print("Invalid input")
            continue

        newAnimIDList = [LayerGenStartAnimID, LayerGenStartAnimID + 10, LayerGenStartAnimID + 20, LayerGenStartAnimID + 50, LayerGenStartAnimID + 60, LayerGenStartAnimID + 70]
        for AnimID in __data__.findall('hkobject[@class="CustomManualSelectorGenerator"]/hkparam[@name=animId]'):
            if int(AnimID.text) in newAnimIDList:
                print("Anim ID " + LayerGenStartAnimID + " already exists")
                break
        else:
            isValid = True

    isValid = False
    while isValid != True:
        LayerGenVarPrefix = str(input('Enter variable prefix (variables will be named [prefix]_a00/[prefix]_a02/[prefix]_a03): '))
        if LayerGenVarPrefix == "":
            print("Invalid input")
            continue
        else:
            isValid = True

    CreateLayerGen(LayerGenName, ScriptGenerator, LayerGenStartAnimID, LayerGenVarPrefix)


def CreateLayerGen(Name, ScriptGenerator, StartAnimID, VarPrefix):
    ScriptGenName = RemoveSuffix(ScriptGenerator.find('hkparam[@name="name"]').text, "_Script")
    ScriptGenName = RemoveSuffix(ScriptGenName, " Script")
    ScriptGenerator.find('hkparam[@name="onPreUpdateScript"]').text = ScriptGenName + "_Update()"
    ScriptGenChildID = ScriptGenerator.find('hkparam[@name="child"]').text

    LayerGen = copy.deepcopy(__data__.find('hkobject[@class="hkbLayerGenerator"]'))
    NameID = GetNameID()
    LayerGen.set("name", "#" + str(NameID))
    __data__.append(LayerGen)

    LayerGen.find('hkparam[@name="name"]').text = Name + "_LayerGenerator"

    for i in range(4):
        BlendTemplate = etree.parse("HavokClasses/BlendTemplate.xml", parser=parser)
        NameID = GetNameID()
        if i == 0:
            SMLayer = BlendTemplate.find('hkobject[@class="hkbLayer"]')
            SMLayer.find('hkparam[@name="variableBindingSet"]').text = "null"
            SMLayer.find('hkparam[@name="boneWeights"]').text = "null"
            SMLayer.find('hkparam[@name="generator"]').text = ScriptGenChildID
            __data__.append(BlendTemplate.find('hkobject[@class="hkbLayer"]'))
        else:
            for hkobject in BlendTemplate.findall("hkobject"):
                for ref in BlendTemplate.findall('hkobject/hkparam'):
                    if ref.text == hkobject.get("name"):
                        ref.text = "#" + str(NameID)

                hkobject.set("name", "#" + str(NameID))
                NameID += 1

            if i == 1:
                HoldStyle = "_a00"
            elif i == 2:
                HoldStyle = "_a02"
                StartAnimID += 10
            elif i == 3:
                HoldStyle = "_a03"
                StartAnimID += 20

            BlendTemplate.find('hkobject[@class="hkbBlenderGenerator"]/hkparam[@name="name"]').text = Name + HoldStyle + "_Blend"

            for CMSG in BlendTemplate.findall('hkobject[@class="CustomManualSelectorGenerator"]'):
                if "Idle" in CMSG.find('hkparam[@name="name"]').text:
                    CMSG.find('hkparam[@name="name"]').text = Name + "Idle" + HoldStyle + "_CMSG"
                    CMSG.find('hkparam[@name="animId"]').text = str(StartAnimID)
                elif "Active" in CMSG.find('hkparam[@name="name"]').text:
                    CMSG.find('hkparam[@name="name"]').text = Name + "Active" + HoldStyle + "_CMSG"
                    CMSG.find('hkparam[@name="animId"]').text = str(StartAnimID+50)

                for hkbClipGenerator in BlendTemplate.findall('hkobject[@class="hkbClipGenerator"]'):
                    if hkbClipGenerator.get("name") in CMSG.find('hkparam[name="generators"]').text:
                        AnimID = CMSG.find('hkparam[@name="animId"]').text
                        hkbClipGenerator.find('hkparam[name="name"]').text = "a000_" + AnimID + "_hkx_AutoSet_00"
                        hkbClipGenerator.find('hkparam[name="animationName"]').text = "a000_" + AnimID

            VarName = VarPrefix + HoldStyle
            CreateVariable(VarName, "0", "1065353216", "VARIABLE_TYPE_REAL", "0")
            variableIndex = int(__data__.find('hkobject[@class="hkbBehaviorGraphStringData"]/hkparam[@name=variableNames]').get("numelements")) - 1
            BlendTemplate.find('hkobject[class="hkbVariableBindingSet"]/hkparam[@name="bindings"]/hkobject/hkparam[@name="variableIndex"]').text = variableIndex

            __data__.append(BlendTemplate.getchildren())


=======
>>>>>>> parent of dec9338 (Initial LayerGenerator support)
def GetCMSGParams(AnimID):
    isValid = False
    while isValid != True:
        CMSGName = str(input('Enter CMSG name (this will be used in hks with the prefix "W_" to trigger the animation): '))
        if CMSGName == "":
            print("Invalid input")
            continue
        for SMSIName in __data__.findall('hkobject[@class="hkbStateMachineStateInfo"]/hkparam[@name="name"]'):
            if SMSIName.text.lower() == CMSGName.lower():
                print("A CMSG with this name already exists.")
                break
        else:
            isValid = True

    isValid = False
    while isValid != True:
        HandInput = str(input("Which hand does this animation belong to? [Right/Left/Both]: "))
        if HandInput.lower() in ["right", "r"]:
            HandSM = "AttackRight_SM"
            offsetType = "WeaponCategoryRight"
            isValid = True
        elif HandInput.lower() in ["left", "l"]:
            HandSM = "AttackLeft_SM"
            offsetType = "WeaponCategoryLeft"
            isValid = True
        elif HandInput.lower() in ["both", "b"]:
            HandSM = "AttackBoth_SM"
            offsetType = "WeaponCategoryHandStyle"
            isValid = True
        else:
            print("Invalid input")

    isValid = False
    while isValid != True:
        TransitionInput = str(input("Enter transition name or ID. [default: #292]: "))
        if TransitionInput.lower() in ["292", "#292", "defaulttransition" "default", "d", ""]:
            transition = "#292"
            isValid = True
        else:
            for hkobject in __data__.findall("hkobject"):
                if hkobject.get("class") in ["CustomTransitionEffect", "hkbBlendingTransitionEffect"]:
                    if hkobject.get("name") == TransitionInput:
                        transition = TransitionInput
                        isValid = True
                        break
                    elif hkobject.find("hkparam[@name='name']").text.lower() == TransitionInput.lower():
                        transition = hkobject.get("name")
                        isValid = True
                        break
            else:
                print("No hkbBlendingTransitionEffect or CustomTransitionEffect found")


    isValid = False
    while isValid != True:
        GCTEInput = str(input("Enter generatorChangedTransitionEffect. [default: null]: "))
        if GCTEInput in ["null", "n", "default", "d", ""]:
            GCTE = "null"
            isValid = True
        else:
            for hkobject in __data__.findall("hkobject"):
                if hkobject.get("class") in ["CustomTransitionEffect", "hkbBlendingTransitionEffect"]:
                    if hkobject.get("name") == GCTEInput:
                        GCTE = GCTEInput
                        isValid = True
                        break
            else:
                print("No hkbBlendingTransitionEffect or CustomTransitionEffect found")


    isValid = False
    while isValid != True:
        IsWAInput = str(input('Is this animation part of a Weapon Art? [Y/N]: ')).lower()
        if IsWAInput in ["yes", "y", "ye"]:
            IsWA = True
            isValid = True
        elif IsWAInput in ["no", "n"]:
            IsWA = False
            isValid = True
        else:
            print("Invalid input")

    if IsWA == False:
        CreateCMSG(AnimID, CMSGName, HandSM, offsetType, transition, GCTE)
    else:
        isValid = False
        requireInput = True
        while isValid != True:
            if requireInput:
                VariableInput = str(input('Which variable should determine whether the PC has enough Points? [default: "IsEnoughArtPointsL2"]: '))
            if VariableInput.lower() in ["default", "d", "isenoughartpointsl2", "", "128"]:
                variableIndex = 128
                isValid = True
            else:
                for i, var in enumerate(__data__.findall('hkobject[@class="hkbBehaviorGraphStringData"]/hkparam[@name="variableNames"]/hkcstring')):
                    if var.text.lower() == VariableInput.lower() or str(i) == VariableInput:
                        variableIndex = i
                        isValid = True
                        break
                else:
                    print("Variable not found.")
                    requireInput = True
                    # shouldCreateVar = str(input("Variable not found. Create variable " + VariableInput + "? [Y/N]: "))
                    # if shouldCreateVar.lower() in ["yes", "ye", "y"]:
                        # GetVariableParams(VariableInput)
                        # requireInput = False
                    # else:
                        # requireInput = True

        CreateWACMSG(AnimID, CMSGName, HandSM, offsetType, transition, GCTE, variableIndex)

def CreateCMSG(AnimID, CMSGName, HandSM, offsetType, transition, generatorChangedTransitionEffect):
    NameID = GetNameID()
    StateID = GetStateID(HandSM)
    UserData = GetUserData(HandSM)

    #parse, edit and append SMSI
    hkbStateMachineStateInfo = etree.parse(os.path.join(exeFolder, "HavokClasses/hkbStateMachineStateInfo.xml"), parser=parser).getroot()
    hkbStateMachineStateInfo.set("name", "#" + str(NameID))
    hkbStateMachineStateInfo.find('hkparam[@name="generator"]').text = "#" + str(NameID + 1)
    hkbStateMachineStateInfo.find('hkparam[@name="name"]').text = CMSGName
    hkbStateMachineStateInfo.find('hkparam[@name="stateId"]').text = str(StateID)
    __data__.append(hkbStateMachineStateInfo)

    #parse, edit and append CMSG
    CustomManualSelectorGenerator = etree.parse(os.path.join(exeFolder, "HavokClasses/CustomManualSelectorGenerator.xml"), parser=parser).getroot()
    CustomManualSelectorGenerator.set("name", "#" + str(NameID + 1))
    CustomManualSelectorGenerator.find('hkparam[@name="userData"]').text = str(UserData)
    CustomManualSelectorGenerator.find('hkparam[@name="name"]').text = CMSGName + "_CMSG"
    CustomManualSelectorGenerator.find('hkparam[@name="offsetType"]').text = offsetType
    CustomManualSelectorGenerator.find('hkparam[@name="animId"]').text = str(AnimID)
    CustomManualSelectorGenerator.find('hkparam[@name="generatorChangedTransitionEffect"]').text = generatorChangedTransitionEffect
    __data__.append(CustomManualSelectorGenerator)

    #add event and transition entry
    EventID = GetEventID()

    eventNames = __data__.find("hkobject[@class='hkbBehaviorGraphStringData']/hkparam[@name='eventNames']")
    etree.SubElement(eventNames, 'hkcstring').text = "W_" + CMSGName
    eventNames.set("numelements", str(int(eventNames.get("numelements")) + 1))

    eventInfos = __data__.find("hkobject[@class='hkbBehaviorGraphData']/hkparam[@name='eventInfos']")
    eventInfoObject = etree.SubElement(eventInfos, "hkobject")
    etree.SubElement(eventInfoObject, "hkparam", name="flags").text = "0"
    eventInfos.set("numelements", str(int(eventInfos.get("numelements")) + 1))

    for SM in __data__.findall("hkobject[@class='hkbStateMachine']"):
        if SM.find("hkparam[@name='name']").text == HandSM:
            SMstates = SM.find("hkparam[@name='states']")
            SMstates.text += "#" + str(NameID) + "\n"
            SMstates.set("numelements", str(int(SMstates.get("numelements"))+1))
            transitions = SM.find("hkparam[@name='wildcardTransitions']").text
            break

    for TransitionInfoArray in __data__.findall('hkobject[@class="hkbStateMachineTransitionInfoArray"]'):
        if TransitionInfoArray.get("name") == transitions:
            transitionParam = TransitionInfoArray.find("hkparam[@name='transitions']")
            transitionParam.set("numelements", str(int(transitionParam.get("numelements"))+1))
            newTransition = copy.deepcopy(transitionParam.find("hkobject"))
            newTransition.find('hkparam[@name="eventId"]').text = str(EventID)
            newTransition.find('hkparam[@name="toStateId"]').text = str(StateID)
            newTransition.find('hkparam[@name="transition"]').text = transition
            TransitionInfoArray.find("hkparam[@name='transitions']").append(newTransition)
            break

def CreateWACMSG(AnimID, CMSGName, HandSM, offsetType, transition, generatorChangedTransitionEffect, variableIndex):
    NameID = GetNameID()
    StateID = GetStateID(HandSM)
    UserData = GetUserData(HandSM)

    #parse, edit and append SMSI
    hkbStateMachineStateInfo = etree.parse(os.path.join(exeFolder, "HavokClasses/hkbStateMachineStateInfo.xml"), parser=parser).getroot()
    hkbStateMachineStateInfo.set("name", "#" + str(NameID))
    hkbStateMachineStateInfo.find('hkparam[@name="generator"]').text = "#" + str(NameID + 1)
    hkbStateMachineStateInfo.find('hkparam[@name="name"]').text = CMSGName
    hkbStateMachineStateInfo.find('hkparam[@name="stateId"]').text = str(StateID)
    __data__.append(hkbStateMachineStateInfo)

    #parse, edit and append hkbManualSelectorGenerator
    hkbManualSelectorGenerator = etree.parse(os.path.join(exeFolder, "HavokClasses/hkbManualSelectorGenerator.xml"), parser=parser).getroot()
    hkbManualSelectorGenerator.set("name", "#" + str(NameID + 1))
    hkbManualSelectorGenerator.find('hkparam[@name="variableBindingSet"]').text = "#" + str(NameID + 2)
    hkbManualSelectorGenerator.find('hkparam[@name="generators"]').text = "\n#" + str(NameID + 3) + "\n#" + str(NameID + 4)
    hkbManualSelectorGenerator.find('hkparam[@name="generators"]').set("numelements", "2")
    hkbManualSelectorGenerator.find('hkparam[@name="userData"]').text = "0"
    hkbManualSelectorGenerator.find('hkparam[@name="name"]').text = CMSGName + "_Selector"
    hkbManualSelectorGenerator.find('hkparam[@name="generatorChangedTransitionEffect"]').text = generatorChangedTransitionEffect
    __data__.append(hkbManualSelectorGenerator)

    #parse, edit and append hkbVariableBindingSet
    hkbVariableBindingSet = etree.parse(os.path.join(exeFolder, "HavokClasses/hkbVariableBindingSet.xml"), parser=parser).getroot()
    hkbVariableBindingSet.set("name", "#" + str(NameID + 2))
    hkbVariableBindingSet.find('hkparam[@name="bindings"]/hkobject/hkparam[@name="variableIndex"]').text = str(variableIndex)
    __data__.append(hkbVariableBindingSet)

    #parse, edit and append CMSG
    CustomManualSelectorGenerator = etree.parse(os.path.join(exeFolder, "HavokClasses/CustomManualSelectorGenerator.xml"), parser=parser).getroot()
    CustomManualSelectorGenerator.set("name", "#" + str(NameID + 3))
    CustomManualSelectorGenerator.find('hkparam[@name="userData"]').text = str(UserData)
    CustomManualSelectorGenerator.find('hkparam[@name="name"]').text = CMSGName + "_CMSG"
    CustomManualSelectorGenerator.find('hkparam[@name="offsetType"]').text = offsetType
    CustomManualSelectorGenerator.find('hkparam[@name="animId"]').text = str(AnimID)
    CustomManualSelectorGenerator.find('hkparam[@name="generatorChangedTransitionEffect"]').text = "null"
    __data__.append(CustomManualSelectorGenerator)

    #parse, edit and append NoPoints_CMSG
    CustomManualSelectorGeneratorNoPoints = etree.parse(os.path.join(exeFolder, "HavokClasses/CustomManualSelectorGenerator.xml"), parser=parser).getroot()
    CustomManualSelectorGeneratorNoPoints.set("name", "#" + str(NameID + 4))
    CustomManualSelectorGeneratorNoPoints.find('hkparam[@name="userData"]').text = str(UserData)
    CustomManualSelectorGeneratorNoPoints.find('hkparam[@name="name"]').text = CMSGName + "_NoPoints_CMSG"
    CustomManualSelectorGeneratorNoPoints.find('hkparam[@name="offsetType"]').text = offsetType
    CustomManualSelectorGeneratorNoPoints.find('hkparam[@name="animId"]').text = str(AnimID + 1)
    CustomManualSelectorGeneratorNoPoints.find('hkparam[@name="generatorChangedTransitionEffect"]').text = "null"
    __data__.append(CustomManualSelectorGeneratorNoPoints)

    #add event and transition entry
    EventID = GetEventID()

    eventNames = __data__.find("hkobject[@class='hkbBehaviorGraphStringData']/hkparam[@name='eventNames']")
    etree.SubElement(eventNames, 'hkcstring').text = "W_" + CMSGName
    eventNames.set("numelements", str(int(eventNames.get("numelements")) + 1))

    eventInfos = __data__.find("hkobject[@class='hkbBehaviorGraphData']/hkparam[@name='eventInfos']")
    eventInfoObject = etree.SubElement(eventInfos, "hkobject")
    etree.SubElement(eventInfoObject, "hkparam", name="flags").text = "0"
    eventInfos.set("numelements", str(int(eventInfos.get("numelements")) + 1))

    for SM in __data__.findall("hkobject[@class='hkbStateMachine']"):
        if SM.find("hkparam[@name='name']").text == HandSM:
            SMstates = SM.find("hkparam[@name='states']")
            SMstates.text += "#" + str(NameID) + "\n"
            SMstates.set("numelements", str(int(SMstates.get("numelements"))+1))
            transitions = SM.find("hkparam[@name='wildcardTransitions']").text
            break

    for TransitionInfoArray in __data__.findall('hkobject[@class="hkbStateMachineTransitionInfoArray"]'):
        if TransitionInfoArray.get("name") == transitions:
            transitionParam = TransitionInfoArray.find("hkparam[@name='transitions']")
            transitionParam.set("numelements", str(int(transitionParam.get("numelements"))+1))
            newTransition = copy.deepcopy(transitionParam.find("hkobject"))
            newTransition.find('hkparam[@name="transition"]').text = transition
            newTransition.find('hkparam[@name="eventId"]').text = str(EventID)
            newTransition.find('hkparam[@name="toStateId"]').text = str(StateID)
            TransitionInfoArray.find("hkparam[@name='transitions']").append(newTransition)
            break

#check whether animation has already been registered, otherwise register
def CheckAndAppendAnim(TaeID, AnimID):
    TaeName = "a" + str(TaeID).zfill(3)
    AnimName = str(AnimID).zfill(6)
    CustomManualSelectorGeneratorFound = False

    for NameParam in __data__.findall('hkobject[@class="hkbClipGenerator"]/hkparam[@name="animationName"]'):
            if NameParam.text == TaeName + "_" + AnimName:
                print("Animation " + TaeName + "_" + AnimName + " is already registered.")
                return

    while CustomManualSelectorGeneratorFound == False:
        for CustomManualSelectorGenerator in __data__.findall('hkobject[@class="CustomManualSelectorGenerator"]'):
            if CustomManualSelectorGenerator.find('hkparam[@name="animId"]').text == str(AnimID):
                try:
                    clipGenID = CustomManualSelectorGenerator.find('hkparam[@name="generators"]').text.split()[0]
                    for clipGen in __data__.findall('hkobject[@class="hkbClipGenerator"]'):
                        if clipGen.get("name") == clipGenID:
                            hkbClipGenerator = copy.deepcopy(clipGen)
                            break
                    else:
                        hkbClipGenerator = etree.parse(os.path.join(exeFolder, "HavokClasses/hkbClipGenerator.xml"), parser=parser).getroot()
                except:
                    hkbClipGenerator = etree.parse(os.path.join(exeFolder, "HavokClasses/hkbClipGenerator.xml"), parser=parser).getroot()
                    
                hkbClipGenerator.find("hkparam[@name='name']").text = TaeName + "_" + AnimName + ".hkx"
                hkbClipGenerator.find("hkparam[@name='animationName']").text = TaeName + "_" + AnimName
                
                Name = "#" + str(GetNameID())
                hkbClipGenerator.set("name", Name)
                generators = CustomManualSelectorGenerator.find('hkparam[@name="generators"]')
                if type(generators.text) is str:
                    generators.text += Name + "\n"
                else:
                    generators.text = "\n" + Name + "\n"
                generators.set("numelements", str(int(generators.get("numelements"))+1))
                CustomManualSelectorGeneratorFound = True
        if CustomManualSelectorGeneratorFound == False:
            continueInput = str(input("No CustomManualSelectorGenerator found for animation ID " + str(AnimID) + ".\nCreate CustomManualSelectorGenerator? [Y/N]: "))
            if continueInput.lower() != "y" and continueInput.lower() != "yes" and continueInput.lower() != "ye":
                return
            else:
                GetCMSGParams(AnimID)

    __data__.append(hkbClipGenerator)
    print("Animation " + TaeName + "_" + AnimName + " successfully registered.")

def GetVariableParams(Name):
    isValid = False
    while isValid != True:
        MinInput = input("Enter minimum value of variable: ")
        try:
            Min = float(MinInput)
        except:
            print("Invalid input")
            continue

        MaxInput = input("Enter maximum value of variable: ")
        try:
            Max = float(MaxInput)
        except:
            print("Invalid input")
            continue

        if Min >= Max:
            print("Invalid input")
        else:
            isValid = True

    isValid = False
    while isValid != True:
        InitialInput = input("Enter initial value of variable: ")
        try:
            initialValue = float(InitialInput)
        except:
            print("Invalid input")
            continue 

        if Min <= initialValue <= Max:
            isValid = True
        else:
            print("Invalid input")

def CreateVariable(Name):
    return

def divide_chunks(list1, n): 
  for i in range(0, len(list1), n): 
    yield list1[i:i + n] 

exeFolder = os.path.dirname(sys.argv[0])

if len(sys.argv) > 1:
    fileNameArgv1 = os.path.basename(sys.argv[1])
    print("The 'Drag and Dropped' File Path is:" ,sys.argv[1], "\n")
else:
    print("A c0000.behbnd.dcx or c0000.anibnd.dcx path was not provided to the executable as an argument.\nTry drag and dropping the file on the executable next time.")
    os.system('pause')
    sys.exit()

# read config
config = configparser.ConfigParser(allow_no_value=True)
config.read_file(open(os.path.join(exeFolder, "config.ini")))

#get AnimIDs
AnimIDType = config["General"]["animidmode"].lower()
if AnimIDType != "custom":
    AnimDef = configparser.ConfigParser(allow_no_value=True)
    AnimDef.read_file(open(os.path.join(exeFolder, "PresetDefinitions.ini")))
    AnimIDList = list(map(int, AnimDef.options(AnimIDType)))
else:
    AnimIDList = list(map(int, config.options("CustomAnimID")))

#get TaeIDs
TaeMode = config["General"]["taemode"].lower()
if TaeMode != "custom":
    TaeDef = configparser.ConfigParser(allow_no_value=True)
    TaeDef.read_file(open(os.path.join(exeFolder, "TaeIDList.ini")))
    TaeIDList = []
    for TaeID in TaeDef.options(TaeMode):
        if " - " in TaeID:
            TaeRangeList = TaeID.split(" - ", 2)
            try:
                TaeMin = int(TaeRangeList[0])
                TaeMax = int(TaeRangeList[1])
                for i in range(TaeMin, TaeMax+1):
                    TaeIDList.append(i)
            except:
                print("Invalid Tae input: " + TaeID)

        elif "-" in TaeID:
            TaeRangeList = TaeID.split("-", 2)
            try:
                TaeMin = int(TaeRangeList[0])
                TaeMax = int(TaeRangeList[1])
                for i in range(TaeMin, TaeMax+1):
                    TaeIDList.append(i)
            except:
                print("Invalid Tae input: " + TaeID)
        else:
            try:
                TaeIDList.append(int(TaeID))
            except:
                print("Invalid Tae input: " + TaeID)
else:
    TaeIDList = []
    for TaeID in config.options("TaeID"):
        if " - " in TaeID:
            TaeRangeList = TaeID.split(" - ", 2)
            try:
                TaeMin = int(TaeRangeList[0])
                TaeMax = int(TaeRangeList[1])
                for i in range(TaeMin, TaeMax+1):
                    TaeIDList.append(i)
            except:
                print("Invalid Tae input: " + TaeID)

        elif "-" in TaeID:
            TaeRangeList = TaeID.split("-", 2)
            try:
                TaeMin = int(TaeRangeList[0])
                TaeMax = int(TaeRangeList[1])
                for i in range(TaeMin, TaeMax+1):
                    TaeIDList.append(i)
            except:
                print("Invalid Tae input: " + TaeID)
        else:
            try:
                TaeIDList.append(int(TaeID))
            except:
                print("Invalid Tae input: " + TaeID)

#Register AniBND Moveset if AniBND is drag and dropped onto .exe then pause and close program.
if fileNameArgv1 == "c0000.anibnd.dcx":
    commaSeparatedAnimList = ""
    for taeSubID in AnimIDList:
        commaSeparatedAnimList += str(taeSubID) + ","
    else:
        commaSeparatedAnimList = commaSeparatedAnimList[:-1]

    commaSeparatedTaeIDList = ""
    for taeIDLoop in TaeIDList:
        commaSeparatedTaeIDList += str(taeIDLoop) + ","
    else:
        commaSeparatedTaeIDList = commaSeparatedTaeIDList[:-1]
        CallRegisterAnibnd(taeID=commaSeparatedTaeIDList, taeSubID=commaSeparatedAnimList)
elif fileNameArgv1 == "c0000.behbnd.dcx":
    # Create Temporary Directory to unpack the behbnd into, Deletes the directory if it already exists.
    workFolderPath = os.path.join(exeFolder, "WorkFolder")
    if os.path.isdir(workFolderPath):
        shutil.rmtree(workFolderPath)
    os.mkdir(workFolderPath)

    # Copy drag and dropped behbnd to work folder
    shutil.copy(sys.argv[1], workFolderPath)
    workFolderBehBndPath = os.path.join(workFolderPath, "c0000.behbnd.dcx")

    # Calling yabber onto c0000.behbnd.dcx inside work folder
    CallYabber(workFolderBehBndPath)
    workFolderBehBndUnpackedPath = os.path.join(workFolderPath, "c0000-behbnd-dcx")

    # Calling HkxPackSouls onto c0000.hkx
    workFolderc0000hkxPath = os.path.join(workFolderBehBndUnpackedPath ,"Action\c0000\Export\Behaviors\c0000.hkx")
    CallHkxPackSoulsDs3(workFolderc0000hkxPath)
    workFolderc0000xmlPath = os.path.join(workFolderBehBndUnpackedPath ,"Action\c0000\Export\Behaviors\c0000.xml")

    # Print Separator
    print("----------------------------------------------------------")

    # parse behavior xml
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(workFolderc0000xmlPath, parser=parser)
    root = tree.getroot()
<<<<<<< HEAD
    __data__ = root.find("hksection[@name='__data__']")  

    SpecialMode = config["General"]["specialmode"].lower()  

    if SpecialMode == "none":
        #append hkbClipGenerators and add them to CustomManualSelectorGenerators
        for TaeID in TaeIDList:
            if int(TaeID) > 999:
                print("Tae ID " + str(TaeID) + "is too large.")
            elif int(TaeID) < 0:
                print("Tae ID " + str(TaeID) + "is too small.")
            else:
                for AnimID in AnimIDList:
                    CheckAndAppendAnim(TaeID, AnimID)
    elif SpecialMode == "blend":
        GetLayerGenParams()
    else:
        print('Invalid SpecialMode "' + SpecialMode + '"')
=======
    __data__ = root.find("hksection[@name='__data__']")    

    #append hkbClipGenerators and add them to CustomManualSelectorGenerators
    for TaeID in TaeIDList:
        if int(TaeID) > 999:
            print("Tae ID " + str(TaeID) + "is too large.")
        elif int(TaeID) < 0:
            print("Tae ID " + str(TaeID) + "is too small.")
        else:
            for AnimID in AnimIDList:
                CheckAndAppendAnim(TaeID, AnimID)
>>>>>>> parent of dec9338 (Initial LayerGenerator support)

    # write to c0000.xml in work folder
    tree.write(workFolderc0000xmlPath, encoding="ASCII", xml_declaration=True, method="xml", standalone=False, pretty_print=True)

        # Print Separator
    print("----------------------------------------------------------\n")
    # Calling HkxPackSouls onto c0000.xml to get updated c0000.hkx
    CallHkxPackSoulsDs3(workFolderc0000xmlPath)

    # Calling Yabber onto unpacked folder to get updated c0000.behbnd.dcx
    CallYabber(workFolderBehBndUnpackedPath)

    # Rename Drag and Dropped file to c0000.behbnd.dcx.bak
    if os.path.isfile(sys.argv[1] + ".bak"):
        os.remove(sys.argv[1] + ".bak")
    os.rename(sys.argv[1], sys.argv[1] + ".bak")

    # Copy updated file back into the source folder
    shutil.copy(workFolderBehBndPath, os.path.dirname(sys.argv[1]))

    # Remove Work Directory and all files inside of it.
    shutil.rmtree(workFolderPath)

    os.system('pause')
