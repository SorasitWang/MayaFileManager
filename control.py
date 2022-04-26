
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
reload(util)
from util import downloadImage, uploadImage

import schema
from schema import Shot
from schema import File

import fileInfo
import linkAnim
import assetManage
reload(schema)
reload(database)
reload(fileInfo)
reload(linkAnim)
reload(assetManage)
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


    def __init__(self):

        cmds.workspace(fileRule=['images',"D:\program\MayaScript"])
        self.db = Database()
        self.file : File = self.db.getDataOneFile("Test")
        self.page1 = None
        self.page2 = None
        self.page3 = None

        window = cmds.window( widthHeight=(400, 500),cc=self.close )
        form = cmds.formLayout()
        tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        cmds.formLayout( form, edit=True, attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)) )
    
        self.page1 = assetManage.AssetManage(self.file,self.db)
        child1 = self.page1._main     
           
        self.page2 = fileInfo.FileInfo(self.file,self.db)
        child2 = self.page2._main       
        
        self.page3 = linkAnim.LinkAnim(self.file,self.db)
        child3 = self.page3._main
        cmds.tabLayout( tabs, edit=True, tabLabel=((child1, 'One'), (child2, 'Two') ,(child3,"Three")) )
    

        cmds.showWindow( window )

    def close(self,*args):
        result = cmds.confirmDialog( title='Confirm', message='Do you want to save the change?',
         button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        dir = "D:/program/MayaScript/imgShow/"
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
        if result == "No": return
        self.page1.close()
        self.page2.close()
        self.page3.close()
        #clear imgShow 
        

    
f = FileManager()






        
