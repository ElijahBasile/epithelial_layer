
from PySteppables import *
import CompuCell
import sys

from PySteppablesExamples import MitosisSteppableBase
            

class ConstraintInitializerSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
    def start(self):
        xpos = 0
        ypos = 0
        for num in range(10):
            self.cellField[xpos:xpos+19,ypos:ypos+19,0] = self.newCell(self.ECM)
            xpos += 20
            
        xpos = 0
        ypos = 20
        for num in range(20):
            self.cellField[xpos:xpos+9,ypos:ypos+9,0] = self.newCell(self.LATERAL)
            xpos += 10
            
#         for cell in self.cellList:
#             cell.targetVolume=25
#             cell.lambdaVolume=2.0
    def step(self,mcs):
        if(mcs==500):
            for cell in self.cellListByType(self.APICAL):
                if(70<cell.xCOM<130):
                    for fppd in self.getFocalPointPlasticityDataList(cell):
    #                     print "fppd.neighborId", fppd.neighborAddress.id, " lambda=", fppd.lambdaDistance, " targetDistance=", fppd.targetDistance
                        lambdav = fppd.lambdaDistance*2
                        targetd = fppd.targetDistance/2.0
                        self.focalPointPlasticityPlugin.setFocalPointPlasticityParameters(cell, fppd.neighborAddress, lambdav, targetd, 200.0)
        

class GrowthSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
    def step(self,mcs):
        for cell in self.cellList:
            cell.targetVolume+=1        
    # alternatively if you want to make growth a function of chemical concentration uncomment lines below and comment lines above        
        # field=CompuCell.getConcentrationField(self.simulator,"PUT_NAME_OF_CHEMICAL_FIELD_HERE")
        # pt=CompuCell.Point3D()
        # for cell in self.cellList:
            # pt.x=int(cell.xCOM)
            # pt.y=int(cell.yCOM)
            # pt.z=int(cell.zCOM)
            # concentrationAtCOM=field.get(pt)
            # cell.targetVolume+=0.01*concentrationAtCOM  # you can use here any fcn of concentrationAtCOM     
        
        

class MitosisSteppable(MitosisSteppableBase):
    def __init__(self,_simulator,_frequency=1):
        MitosisSteppableBase.__init__(self,_simulator, _frequency)
    
    def start(self):
        self.division = 1
        cells_to_divide=[]
        
        for cell in self.cellListByType(self.LATERAL):
            cells_to_divide.append(cell)
             
             
        for cell in cells_to_divide:
            # to change mitosis mode leave one of the below lines uncommented
#             self.divideCellRandomOrientation(cell)
            self.divideCellOrientationVectorBased(cell,0,1,0)                 # this is a valid option
            # self.divideCellAlongMajorAxis(cell)                               # this is a valid option
            # self.divideCellAlongMinorAxis(cell)                               # this is a valid option
        self.division = 2
        cells_to_divide=[]
        
        for cell in self.cellListByType(self.LATERAL):
            cells_to_divide.append(cell)
             
             
        for cell in cells_to_divide:
            # to change mitosis mode leave one of the below lines uncommented
#             self.divideCellRandomOrientation(cell)
            self.divideCellOrientationVectorBased(cell,0,1,0)                 # this is a valid option
            
        for cell in self.cellListByType(self.LATERAL):  
            cell.targetVolume = 80.0
            cell.lambdaVolume = 10.0
        
        for cell in self.cellListByType(self.BASAL,self.APICAL):
            cell.targetVolume = 30.0
            cell.lambdaVolume = 10.0
        
        
    def updateAttributes(self):
#         self.parentCell.targetVolume /= 2.0 # reducing parent target volume                 
        self.cloneParent2Child()    
        # READ ONLY ACCESS - can be modified using reassignClusterId function
        clusterId = self.parentCell.clusterId        
        reassignIdFlag = self.inventory.reassignClusterId(self.childCell, clusterId)  
        
        
        # for more control of what gets copied from parent to child use cloneAttributes function
        # self.cloneAttributes(sourceCell=self.parentCell, targetCell=self.childCell, no_clone_key_dict_list = [attrib1, attrib2] )
        
        if self.division == 1:
            if (self.parentCell.yCOM < self.childCell.yCOM):
                self.parentCell.type = self.BASAL
                self.childCell.type = self.LATERAL
            else:
                self.parentCell.type = self.LATERAL
                self.childCell.type = self.BASAL
        else:
            if(self.parentCell.yCOM < self.childCell.yCOM):
                self.parentCell.type = self.LATERAL
                self.childCell.type = self.APICAL
            else:
                self.parentCell.type = self.APICAL
                self.childCell.type = self.LATERAL
        
        