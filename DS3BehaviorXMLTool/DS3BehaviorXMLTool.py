import sys
from lxml import etree
from pathlib import Path
import configparser
import collections
import os
from io import StringIO
import copy

import stat
import os

exeFolder = os.path.dirname(sys.argv[0]) + "\\"

if len(sys.argv) > 1:
    print("The 'Drag and Dropped' File Path is:" ,sys.argv[1])
    st = os.stat(sys.argv[1])
    os.chmod(sys.argv[1], st.st_mode | stat.S_IWOTH)
else:
    print("A c0000.xml path was not provided to the executable as an argument.\nTry drag and dropping c0000.xml on the executable")
    os.system('pause')
    sys.exit()

# parse behavior xml
parser = etree.XMLParser(remove_blank_text=True)
tree = etree.parse(sys.argv[1], parser=parser)
root = tree.getroot()
__data__ = root.find("hksection[@name='__data__']")

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
    hkbStateMachineStateInfo = etree.parse("HavokClasses/hkbStateMachineStateInfo.xml", parser=parser).getroot()
    hkbStateMachineStateInfo.set("name", "#" + str(NameID))
    hkbStateMachineStateInfo.find('hkparam[@name="generator"]').text = "#" + str(NameID + 1)
    hkbStateMachineStateInfo.find('hkparam[@name="name"]').text = CMSGName
    hkbStateMachineStateInfo.find('hkparam[@name="stateId"]').text = str(StateID)
    __data__.append(hkbStateMachineStateInfo)

    #parse, edit and append CMSG
    CustomManualSelectorGenerator = etree.parse("HavokClasses/CustomManualSelectorGenerator.xml", parser=parser).getroot()
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
    hkbStateMachineStateInfo = etree.parse("HavokClasses/hkbStateMachineStateInfo.xml", parser=parser).getroot()
    hkbStateMachineStateInfo.set("name", "#" + str(NameID))
    hkbStateMachineStateInfo.find('hkparam[@name="generator"]').text = "#" + str(NameID + 1)
    hkbStateMachineStateInfo.find('hkparam[@name="name"]').text = CMSGName
    hkbStateMachineStateInfo.find('hkparam[@name="stateId"]').text = str(StateID)
    __data__.append(hkbStateMachineStateInfo)

    #parse, edit and append hkbManualSelectorGenerator
    hkbManualSelectorGenerator = etree.parse("HavokClasses/hkbManualSelectorGenerator.xml", parser=parser).getroot()
    hkbManualSelectorGenerator.set("name", "#" + str(NameID + 1))
    hkbManualSelectorGenerator.find('hkparam[@name="variableBindingSet"]').text = "#" + str(NameID + 2)
    hkbManualSelectorGenerator.find('hkparam[@name="generators"]').text = "\n#" + str(NameID + 3) + "\n#" + str(NameID + 4)
    hkbManualSelectorGenerator.find('hkparam[@name="generators"]').set("numelements", "2")
    hkbManualSelectorGenerator.find('hkparam[@name="userData"]').text = "0"
    hkbManualSelectorGenerator.find('hkparam[@name="name"]').text = CMSGName + "_Selector"
    hkbManualSelectorGenerator.find('hkparam[@name="generatorChangedTransitionEffect"]').text = generatorChangedTransitionEffect
    __data__.append(hkbManualSelectorGenerator)

    #parse, edit and append hkbVariableBindingSet
    hkbVariableBindingSet = etree.parse("HavokClasses/hkbVariableBindingSet.xml", parser=parser).getroot()
    hkbVariableBindingSet.set("name", "#" + str(NameID + 2))
    hkbVariableBindingSet.find('hkparam[@name="bindings"]/hkobject/hkparam[@name="variableIndex"]').text = str(variableIndex)
    __data__.append(hkbVariableBindingSet)

    #parse, edit and append CMSG
    CustomManualSelectorGenerator = etree.parse("HavokClasses/CustomManualSelectorGenerator.xml", parser=parser).getroot()
    CustomManualSelectorGenerator.set("name", "#" + str(NameID + 3))
    CustomManualSelectorGenerator.find('hkparam[@name="userData"]').text = str(UserData)
    CustomManualSelectorGenerator.find('hkparam[@name="name"]').text = CMSGName + "_CMSG"
    CustomManualSelectorGenerator.find('hkparam[@name="offsetType"]').text = offsetType
    CustomManualSelectorGenerator.find('hkparam[@name="animId"]').text = str(AnimID)
    CustomManualSelectorGenerator.find('hkparam[@name="generatorChangedTransitionEffect"]').text = "null"
    __data__.append(CustomManualSelectorGenerator)

    #parse, edit and append NoPoints_CMSG
    CustomManualSelectorGeneratorNoPoints = etree.parse("HavokClasses/CustomManualSelectorGenerator.xml", parser=parser).getroot()
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

    hkbClipGenerator = etree.parse("HavokClasses/hkbClipGenerator.xml", parser=parser).getroot()
    hkbClipGenerator.find("hkparam[@name='name']").text = TaeName + "_" + AnimName + ".hkx"
    hkbClipGenerator.find("hkparam[@name='animationName']").text = TaeName + "_" + AnimName

    while CustomManualSelectorGeneratorFound == False:
        for CustomManualSelectorGenerator in __data__.findall('hkobject[@class="CustomManualSelectorGenerator"]'):
            if CustomManualSelectorGenerator.find('hkparam[@name="animId"]').text == str(AnimID):
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

# read config
config = configparser.ConfigParser(allow_no_value=True)
config.read_file(open(exeFolder + "config.ini"))

#get AnimIDs
AnimIDType = config["General"]["animidmode"].lower()
if AnimIDType != "custom":
    AnimDef = configparser.ConfigParser(allow_no_value=True)
    AnimDef.read_file(open(exeFolder + "PresetDefinitions.ini"))
    AnimIDList = list(map(int, AnimDef.options(AnimIDType)))
else:
    AnimIDList = list(map(int, config.options("CustomAnimID")))

#get TaeIDs
TaeMode = config["General"]["taemode"].lower()
if TaeMode != "custom":
    TaeDef = configparser.ConfigParser(allow_no_value=True)
    TaeDef.read_file(open(exeFolder + "TaeIDList.ini"))
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


#append hkbClipGenerators and add them to CustomManualSelectorGenerators
for TaeID in TaeIDList:
    if int(TaeID) > 999:
        print("Tae ID " + str(TaeID) + "is too large.")
    elif int(TaeID) < 0:
        print("Tae ID " + str(TaeID) + "is too small.")
    else:
        for AnimID in AnimIDList:
            CheckAndAppendAnim(TaeID, AnimID)

# write to file
tree.write(sys.argv[1] + "-out.xml", encoding="ASCII", xml_declaration=True, method="xml", standalone=False, pretty_print=True)
os.system('pause')