from copy import deepcopy
from datetime import datetime
from imp import reload
import maya.cmds as cmds


import sys

from schema import File
sys.path.append("D:\program\MayaScript")

import database
from database import Database

import util
reload(util)
from util import downloadImage, uploadImage


class FileInfo :
    def __init__(self,file : File,db : Database):

        self.db = db
        self.file = file
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

        dir = "D:/program/MayaScript/imgShow/"
        
        downloadImage(self.file.image,dir)
        self._image = cmds.image( parent=self._info,image=dir+self.file.image,height=100)

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
        print(uploadImage(result)) # prints out the names of all the rendered files
        pass
