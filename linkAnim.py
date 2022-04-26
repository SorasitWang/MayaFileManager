from copy import deepcopy
from datetime import datetime
from functools import partial
from imp import reload
import maya.cmds as cmds


import sys

from schema import File
sys.path.append("D:\program\MayaScript")

import database
from database import Database




class LinkAnim :
    def __init__(self,file:File,db : Database):

        self.db = db
        self._main = cmds.scrollLayout( )
        self.file = file
        self.projects = self.db.projects
        self.sequences = self.db.sequences
        self.shots = self.db.shots
        self.selectedShot = None

        self.genMap()
        cmds.paneLayout( configuration='vertical2' )
        #cmds.setParent( '..' )
        cmds.columnLayout(width=200)
        cmds.text("Shot information")
        
        cmds.paneLayout(configuration="vertical2")
        self._shotName = cmds.textField(editable=False)
        #cmds.textField(self._shotName,edit=True,text=self.shots[self.selectedShot[0]].name if self.selectedShot != None else "")
        cmds.textField(ann="Status",editable=False)
        cmds.setParent( '..' )
        self._shotImg = cmds.image()
        cmds.image(self._shotImg, image='D:\\program\\MayaScript\\res\\wow.png' )
        self._shotDescription = cmds.textField(editable=False)
        #cmds.textField(self._shotDescription,,edit=True,text=self.shots[self.selectedShot[0]].description if self.selectedShot != None else "")
        cmds.setParent( '..' )

        #related seq project
        self._rela = cmds.scrollLayout(sp="down",w=200,h=100)
        cmds.text(parent=self._rela,label="Related Project&Sequence")

        relate = cmds.paneLayout(parent=self._main ,configuration="vertical2")
        cmds.rowColumnLayout(parent=relate, numberOfColumns=3, columnAttach=(1, 'right', 0), columnWidth=[(1, 75), (2, 75),(3, 75)] )
        cmds.text( label="Project" )
        cmds.text( label="Sequence" )
        cmds.text( label="Shot" )
        self._project = cmds.textScrollList( append=list(self.projects.keys()),ams=True,width=75)
        cmds.textScrollList( self._project,e=True, sc=partial(self.handleSelectProject, self._project) )
        self._sequence = cmds.textScrollList( ams=True,width=75)
        cmds.textScrollList( self._sequence,e=True, sc=partial(self.handleSelectSequence, self._sequence) )
        self._shot = cmds.textScrollList( ams=True,width=75)
        cmds.textScrollList( self._shot,e=True, sc=partial(self.handleSelectShot, self._shot) )
        cmds.setParent( '..' )
        
        now = cmds.columnLayout()
        cmds.text("Current relate shot")
        self._currentRela = cmds.textScrollList( append=self.file.shots,ams=True,width=75)
        cmds.textScrollList(self._currentRela,parent=now,e=True, 
            sc=partial(self.handleSelectUnlinkShot, self._currentRela) )
        cmds.setParent( '..' )

        cmds.setParent( '..' )

        cmds.button("Link to this shot",command=self.linkShot)
        cmds.button("Unlink to this shot",command=self.unlinkShot)
        cmds.setParent( '..' )

    def handleSelectProject(self,this_textScrollList):
        self.selectedProject = cmds.textScrollList( this_textScrollList, query=True, si=True)
        cmds.textScrollList(self._sequence, e=True,append=list(self.seqMap[self.selectedProject[0]]), removeAll=True)
        cmds.textScrollList(self._shot, e=True, removeAll=True)

    def handleSelectSequence(self,this_textScrollList):
        self.selectedSequence = cmds.textScrollList( this_textScrollList, query=True, si=True)
        cmds.textScrollList(self._shot, e=True,append=list(self.shotMap[self.selectedSequence[0]]), removeAll=True)
    
    def handleSelectShot(self,this_textScrollList):
        self.selectedShot = cmds.textScrollList( this_textScrollList, query=True, si=True)
        self.findShotRela()
        #update shot infor
        print("selectedShot",self.shots[self.selectedShot[0]].name)
        cmds.textField(self._shotName,edit=True,text=self.shots[self.selectedShot[0]].name)
        cmds.textField(self._shotDescription,edit=True,text=self.shots[self.selectedShot[0]].description)

    def handleSelectUnlinkShot(self,this_textScrollList):
        self.selectedUnlinkShot = cmds.textScrollList( this_textScrollList, query=True, si=True)
        #query data from db 

    def linkShot(self,*args):
        result = cmds.confirmDialog( title='Confirm', message='Are you sure?',
         button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        
        if self.file.name == "":
            cmds.confirmDialog(message="Save this file before link!")
            return
        if result == "No": return
        #add this file to selected shot\
        print(self.file.name)
        self.db.linkShot(self.selectedShot[0],self.file.name)
    
    def unlinkShot(self,*args):
        result = cmds.confirmDialog( title='Confirm', message='Are you sure?',
         button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        
        if self.file.name == "":
            cmds.confirmDialog(message="Save this file before link!")
            return
        if result == "No": return
        #add this file to selected shot\

        self.db.unlinkShot(self.selectedUnlinkShot[0],self.file.name)

    def findShotRela(self):
        seq = []
        for key,item in self.shotMap.items():
            if self.selectedShot[0] in item :
                seq.append(key)
        pro = dict()
        for key,item in self.seqMap.items():
            for s in seq :
                
                if s in item:
                    if pro.get(key) == None:
                        pro[key] = [s]
                    else :
                        pro[key].append(s)
        #update ui
        print(pro)
        prev = cmds.scrollLayout(self._rela,q=True,ca=True)
        for obj in prev:
            if "text" in obj : continue
            cmds.deleteUI(obj,control=True)


        for key,items in pro.items():
            itemHight = len(items)*20
            relatList = cmds.paneLayout(parent=self._rela,configuration="vertical2",width=150,h=itemHight)
            cmds.text(parent=relatList,label=key,width=50)
            cmds.textScrollList(parent=relatList,append=items,width=50,h=itemHight,enable=False)

    def genMap(self):
        #gen SeqMap project : [seq]
        self.seqMap = dict()
        for pro in self.projects.keys():
            self.seqMap[pro] = []
            for seq,data in self.sequences.items():
                if pro in data.projects :
                    self.seqMap[pro].append(seq)

        #gen ShotMap sequence : [shot]
        self.shotMap = dict()
        for seq in self.sequences.keys():
            self.shotMap[seq] = []
            for shot,data in self.shots.items():
                print(shot,data.sequences)
                if seq in data.sequences :
                    self.shotMap[seq].append(shot)
        print(self.seqMap)
        print(self.shotMap)

    def close(self):
        return
        