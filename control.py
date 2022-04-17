
#from database import Database
from copy import deepcopy
from datetime import datetime
from imp import reload
import maya.cmds as cmds
import os
from functools import partial

import sys
sys.path.append("D:\program\MayaScript")

import database
from database import Database

import util
from util import encodeImage

import schema
from schema import Shot
from schema import File


reload(schema)
reload(database)
reload(util)
class FileInfo :
    def __init__(self,db : Database):

        self.db = db
        self.file = self.db.getDataOneFile("Test")
        self.tmpFile = deepcopy(self.file)
        self._main = cmds.scrollLayout( 'page2' , width=300)
        #cmds.file(q=True,shn=True,sn=True)
        cmds.frameLayout( label='File detail')
        cmds.setParent( '..' )
        self._info = cmds.columnLayout()

        self._name = cmds.textField()
        cmds.textField(self._name,edit=True,parent=self._info,text=self.file.name,editable=False)

        _dateStuff = cmds.paneLayout(parent=self._info,configuration="vertical2")
        self._createdAt = cmds.textFieldGrp(cw2=[50,100],cl2=["left","left"],parent=_dateStuff, 
            label='CreatedAt', text=self.file.createdAt, editable=False )
        print("lastUpdated",self.file.lastUpdated)
        self._lastUpdated = cmds.textFieldGrp(cw2=[90,100],cl2=["left","left"],parent=_dateStuff, 
            label='LastedUpdated', text=str(self.file.lastUpdated).split()[0], editable=False )
        self._image = cmds.image( parent=self._info,image=self.file.image )

        self._description = cmds.scrollField(parent=self._info, editable=False, wordWrap=True,text=self.file.description)
        cmds.scrollField(self._description,edit=True,parent=self._info, editable=False, wordWrap=True)
        cmds.setParent( '..' )

        btnStuff = cmds.paneLayout(configuration="vertical2")
        self._edit = cmds.button(parent=btnStuff,label="Edit",command=self.handleEdit)
        self._cancel = cmds.button(parent=btnStuff,label="Cancel",command=self.handleCancel,enable=False)
        cmds.setParent( '..' )
        self._render = cmds.button(label="ReRender",command=self.handleRender)


        cmds.setParent( '..' )
        cmds.setParent( '..' )

        self.readMode = True

    def handleCancel(self,*args): 
        self.tmpFile = deepcopy(self.file)
        cmds.textField(self._name,edit=True,parent=self._info,text=self.file.name,editable=False)
        cmds.scrollField(self._description,edit=True,parent=self._info,text=self.file.description,editable=False)
        self.readMode = True
        pass

    def handleEdit(self,*args):
        if self.readMode == False:
            #update data
            result = cmds.confirmDialog( title='Confirm', message='Save new data',
                button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
            if result=="No" : 
                return
            self.tmpFile.name = cmds.textField(self._name,query=True,text=True)
            self.tmpFile.description = cmds.scrollField(self._description,query=True,text=True)
            self.tmpFile.lastUpdated = datetime.now()
            self.db.updateOneFile(self.tmpFile)


            cmds.textField(self._name,editable=False,edit=True)
            cmds.scrollField(self._description,editable=False,edit=True)
        else :
            print(self.readMode)
            cmds.textField(self._name,edit=True,editable=True)
            cmds.scrollField(self._description,edit=True,editable=True)
            cmds.button(self._edit,edit=True,label="Save")
            cmds.button(self._cancel,edit=True,enable=True)
        self.readMode = not self.readMode


    def handleRender(self,*args):
        filename = cmds.file(q=True,shn=True,sn=True)
        cmds.file(filename, open =True, force=True)
        cmds.setAttr("defaultRenderGlobals.imageFormat", 32)
        # other render settings would go here
        result = cmds.render('persp', x=512, y=512)
        print(result)
        print(encodeImage(result)) # prints out the names of all the rendered files
        pass

def make_dir(path):
    """
    input a path to check if it exists, if not, it creates all the path
    :return: path string
    """
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def MakeFolder(*args):
    # always put *args to function inside ui command flag because maya pass by default one argument True
    userInput = cmds.textField('textBox', q=1, tx=1)
    # you should here verify that this path is valid
    path = make_dir(userInput)
    print('{0} has been created'.format(path))

print("hello")



class FileManager :

    resPath = "D:/program/Maya/project/res/"
    path = "D:/program/Maya/project/"
    def __init__(self):
        self.file = File
        self.assets = dict()
        self.selectedObjs = []
        self.deleteObjs = []
        self.nameNewFile = None
        self.db = Database()
        self.projects = self.db.projects
        self.sequences = self.db.sequences
        self.shots = self.db.shots


        self.seqMap = {"One": ["A","B"] , "Two" : ["C","A"]}
        self.shotMap = {"A":["a"],"B" : ["c","b"] , "C" : ["a","c"]}
        #self.allShots = {"a" : Shot("a","aaaaa") , "b": Shot("b","bbbb") , "c" : Shot("c","cccc")}
        self.allObjs = []
        
        files = cmds.getFileList(folder=FileManager.resPath)

        if len(files) == 0:
            cmds.warning("No files found")

        #set one obj to be a standard size
        window = cmds.window( widthHeight=(400, 500) )
        form = cmds.formLayout()
        tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        cmds.formLayout( form, edit=True, attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)) )
        

        
        
        #cmds.button( label='Save', command=self.saveFile)
        child1 = cmds.rowColumnLayout( numberOfColumns=3, columnAttach=(1, 'right', 0), columnWidth=[(1, 100), (2, 200),(3, 50)] )
        l = 'Select obj to import'
        cmds.text( label=l )

        #self.selectObj = cmds.textField("focusdistance", enterCommand=self.handleSelectObj)
        self._selectedObjs = cmds.textScrollList( append=files,ams=True)
       
        # now set the selection command and pass in the textScrollList 
        cmds.textScrollList( self._selectedObjs,e=True, sc=partial(self.handleSelectObj, self._selectedObjs) ) 
        cmds.button( label='Import', command=self.importFile)


        l = 'Select obj to delete'
        cmds.text( label=l )
        self._deleteObjs = cmds.textScrollList(append=list(self.assets.keys()),ams=True)
        cmds.textScrollList( self._deleteObjs,e=True, sc=partial(self.handleDeleteObj, self._deleteObjs) ) 
        cmds.button( label='Delete', command=self.deleteFile)
        

        cmds.text( label= "Type new Name" )
        self._newFile = cmds.textField()
        cmds.textField( self._newFile, edit=True, cc=partial(self.handleNewFile, self._newFile))

        #cmds.rowColumnLayout( numberOfColumns=4, columnAttach=(1, 'right', 0) )
        cmds.button( label='New', command=self.createFile)
        
        cmds.setParent( '..' )

       
        page2 = FileInfo(self.db)
        child2 = page2._main       
        

        child3 = cmds.scrollLayout( 'page3' )
        cmds.paneLayout( configuration='vertical2' )
        #cmds.setParent( '..' )
        cmds.columnLayout(width=200)
        cmds.text("Shot information")
        
        cmds.paneLayout(configuration="vertical2")
        cmds.textField(ann="Name",editable=False)
        cmds.textField(ann="Status",editable=False)
        cmds.setParent( '..' )
        cmds.image( image='D:\\program\\MayaScript\\res\\wow.png' )
        cmds.text("description...........")
        cmds.setParent( '..' )

        #related seq project
        self._rela = cmds.scrollLayout(sp="down",w=200,h=100)
        cmds.text(parent=self._rela,label="Related Project&Sequence")

        cmds.rowColumnLayout(parent=child3, numberOfColumns=3, columnAttach=(1, 'right', 0), columnWidth=[(1, 100), (2, 100),(3, 100)] )
        cmds.text( label="Project" )
        cmds.text( label="Sequence" )
        cmds.text( label="Shot" )
        self._project = cmds.textScrollList( append=self.projects.keys(),ams=True,width=100)
        cmds.textScrollList( self._project,e=True, sc=partial(self.handleSelectProject, self._project) )
        self._sequence = cmds.textScrollList( ams=True,width=100)
        cmds.textScrollList( self._sequence,e=True, sc=partial(self.handleSelectSequence, self._sequence) )
        self._shot = cmds.textScrollList( ams=True,width=100)
        cmds.textScrollList( self._shot,e=True, sc=partial(self.handleSelectShot, self._shot) )
        cmds.setParent( '..' )
        
        cmds.button("Link this file",command=self.linkFile)
        cmds.setParent( '..' )
       


        cmds.tabLayout( tabs, edit=True, tabLabel=((child1, 'One'), (child2, 'Two') ,(child3,"Three")) )
        cmds.showWindow()   


        self.file.name = cmds.file(q=True,shn=True,sn=True)
        #query data from database if exists

        

        cmds.showWindow( window )
    def handleSelectObj(self,this_textScrollList):
        self.selectedObjs = cmds.textScrollList( this_textScrollList, query=True, si=True)

    def handleDeleteObj(self,this_textScrollList):
        self.deleteObjs = cmds.textScrollList( this_textScrollList, query=True, si=True)

    def handleNewFile(self,this_textField,tmp):
        self.newFile= tmp
    
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

        #query data from db 

    def linkFile(self,*args):
        result = cmds.confirmDialog( title='Confirm', message='Are you sure?',
         button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        
        if self.file.name == "":
            cmds.confirmDialog(message="Save this file before link!")
            return
        if result == "No": return
        #add this file to selected shot\

        self.db.linkFile(self.selectedShot[0],self.file.name)


    def importFile(self,*args):
        for file in self.selectedObjs :
            self.assets[file] = []
            print(FileManager.resPath + file)
            before = cmds.ls()
            print("before",before)
            cmds.file(FileManager.resPath + file,i=True)
            after = cmds.ls()
            print("after",after)
            self.assets[file] = list(set(after) - set(before))
        print(self.assets)
        cmds.textScrollList(self._deleteObjs, e=True,append=list(self.assets.keys()), removeAll=True)
        self.selectedObjs = []

    def deleteFile(self,*args):
        for file in self.deleteObjs:
            for obj in self.assets[file]:
                try :
                    cmds.delete(obj)
                except :
                    print(obj+" is not existed")
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

    def createFile(self,*args):
        #ToDO : create file with specific path
        cmds.file( f=True, type='mayaBinary', save=True )
        cmds.file(  f=True, new=True )
        cmds.file( rename=self.newFile )
        cmds.file( f=True, type='mayaBinary', save=True )

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

     
        

f = FileManager()






        
