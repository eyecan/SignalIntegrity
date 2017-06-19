'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2017 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from CalculationPropertiesProject import PropertiesDialog,CalculationProperty,CalculationPropertyTrueFalseButton

class PreferencesDialog(PropertiesDialog):
    def __init__(self, parent,preferences):
        PropertiesDialog.__init__(self,parent,preferences,parent,'Preferences')
        self.fontSizeFrame=CalculationProperty(self.propertyListFrame,'font size',None,self.onUpdatePreferences,preferences,'Appearance.FontSize')
        self.backgroundColorFrame=CalculationProperty(self.propertyListFrame,'background color',None,self.onUpdateColors,preferences,'Appearance.Color.Background')
        self.foregroundColorFrame=CalculationProperty(self.propertyListFrame,'foreground color',None,self.onUpdateColors,preferences,'Appearance.Color.Foreground')
        self.matPlotLibColorFrame=CalculationProperty(self.propertyListFrame,'plot color',None,self.onUpdateColors,preferences,'Appearance.Color.Plot')
        self.retainRecentFilesFrame=CalculationPropertyTrueFalseButton(self.propertyListFrame,'retain recent project files',None,self.onUpdatePreferences,preferences,'ProjectFiles.RetainLastFilesOpened')
        self.openLastFileFrame=CalculationPropertyTrueFalseButton(self.propertyListFrame,'open last file on start',None,self.onUpdatePreferences,preferences,'ProjectFiles.OpenLastFile')
        self.Finish()
    def onUpdatePreferences(self):
        self.project.SaveToFile()
    def onUpdateColors(self):
        self.parent.UpdateColorsAndFonts()
        self.onUpdatePreferences()