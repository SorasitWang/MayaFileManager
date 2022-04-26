from copy import deepcopy
from datetime import datetime
from functools import partial
from imp import reload
from os import remove
import maya.cmds as cmds


import sys

from schema import File
sys.path.append("D:\program\MayaScript")

import database
from database import Database


class AssetManage :

    resPath = "D:/program/Maya/project/res/"
    path = "D:/program/Maya/project/"

    def __init__(self,file : File,db : Database):

        self.assets = dict()
        self.db = db
        self.selectedObjs = []
        self.deleteObjs = []
        self.nameNewFile = None
        self.file = file
        self.allObjs = []
        self.unlinkObjs = []
        self.selectedObjs = []
        self.deleteObjs = []

        self._main = cmds.rowColumnLayout( numberOfColumns=3, columnAttach=(1, 'right', 0), columnWidth=[(1, 100), (2, 200),(3, 50)] )
        
        self.files : list = cmds.getFileList(folder=AssetManage.resPath)

        if len(self.files) == 0:
            cmds.warning("No files found")

        cmds.text( label='Select obj to import' )

        #self.selectObj = cmds.textField("focusdistance", enterCommand=self.handleSelectObj)
        self._selectedObjs = cmds.textScrollList( append=self.files,ams=True,height=150)
       
        # now set the selection command and pass in the textScrollList 
        cmds.textScrollList( self._selectedObjs,e=True, sc=partial(self.handleSelectObj, self._selectedObjs) ) 
        cmds.button( label='Import', command=self.importFile)


        l = 'Select obj to delete'
        cmds.text( label=l )
        self._deleteObjs = cmds.textScrollList(append=list(self.assets.keys()),ams=True,height=150)
        cmds.textScrollList( self._deleteObjs,e=True, sc=partial(self.handleDeleteObj, self._deleteObjs) ) 
        cmds.button( label='Delete', command=self.deleteFile)

        l = 'Select obj to unlink'
        cmds.text( label=l )
        self._unlinkObjs = cmds.textScrollList(append=self.file.relation,ams=True,height=150)
        cmds.textScrollList( self._unlinkObjs,e=True, sc=partial(self.handleUnlinkObj, self._unlinkObjs) ) 
        cmds.button( label='Delete', command=self.unlinkFile)
        

        cmds.text( label= "Type new Name" )
        self._newFile = cmds.textField()
        cmds.textField( self._newFile, edit=True, cc=partial(self.handleNewFile, self._newFile))

        #cmds.rowColumnLayout( numberOfColumns=4, columnAttach=(1, 'right', 0) )
        cmds.button( label='New', command=self.createFile)
        
        cmds.setParent( '..' )
        pass


    def handleSelectObj(self,this_textScrollList):
        self.selectedObjs = cmds.textScrollList( this_textScrollList, query=True, si=True)

    def handleDeleteObj(self,this_textScrollList):
        self.deleteObjs = cmds.textScrollList( this_textScrollList, query=True, si=True)

    def handleUnlinkObj(self,this_textScrollList):
        self.unlinkObjs = cmds.textScrollList( this_textScrollList, query=True, si=True)

    def handleNewFile(self,this_textField,tmp):
        self.newFile= tmp

    def importFile(self,*args):
        for file in self.selectedObjs :
            self.assets[file] = []
            print(AssetManage.resPath + file)
            before = cmds.ls()
            print("before",before)
            cmds.file(AssetManage.resPath + file,i=True)
            after = cmds.ls()
            print("after",after)
            self.assets[file] = list(set(after) - set(before))
            self.files.remove(file)
        print(self.assets)
        cmds.textScrollList(self._deleteObjs, e=True,append=list(self.assets.keys()), removeAll=True)
        cmds.textScrollList(self._selectedObjs,e=True,append=self.files,removeAll=True)
        self.selectedObjs = []

    def deleteFile(self,*args):
        for file in self.deleteObjs:
            for obj in self.assets[file]:
                try :
                    cmds.delete(obj)
                except :
                    print(obj+" is not existed")
            self.files.append(file)
            self.assets.pop(file,None)
        cmds.textScrollList(self._deleteObjs, e=True,append=list(self.assets.keys()), removeAll=True)
        cmds.textScrollList(self._selectedObjs,e=True,append=self.files,removeAll=True)
        self.deleteObjs = []
    
    def saveFile(self,*args):
        # send self.asstes to update relation
        cmds.file(f=True, type='mayaBinary',save=True)

        #check if some object are incorrect deleted
        nowObjs = set(cmds.ls())
        diff = nowObjs - set(self.allObjs)
        for obj in diff :
            #delete from self.asset, so that it can be link correctly
            pass

        return

    def unlinkFile(self,*args):
        for e in self.unlinkObjs:
            self.file.relation.remove(e)
            if e not in self.files: 
                self.files.append(e)
        cmds.textScrollList(self._unlinkObjs, e=True,append=self.file.relation, removeAll=True)
        cmds.textScrollList(self._selectedObjs,e=True,append=self.files,removeAll=True)

    def createFile(self,*args):
        #ToDO : create file with specific path
        cmds.file( f=True, type='mayaBinary', save=True )
        cmds.file(  f=True, new=True )
        cmds.file( rename=self.newFile )
        cmds.file( f=True, type='mayaBinary', save=True )

    def close(self):
        if len(self.assets.keys()) == 1 :
            self.file.relation += self.assets.keys()
        else :
            for asset in self.assets.keys():
                self.file.relation += asset
            
        self.db.updateOneFile(1,file=self.file)
        return
        