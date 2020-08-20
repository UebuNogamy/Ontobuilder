from relation_extractor import RelationExtractor
from corpusreader import CorpusReader
from ontobuilder import Ontobuilder
from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import pickle
import shutil
import sys
import os

def finalize(model, window):
    model.reset()
    window.close()

class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.ProjectDict = {"Project_Dir": os.environ["HOME"], "Project_Name": "Ontology"}
        self.areaName = ""
        self.availableProperties = {"Subclasses":{},"EquivClasses":{},"ObjectProperties":{},"Subproperties":{}}
        self.initUI()

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowContextHelpButtonHint)
        self.resize(500, 500)
        self.setWindowTitle("OntoBuilder")
        self.OntoCreateBtn = QtWidgets.QPushButton("Create Ontology")
        self.OntoCreateBtn.clicked.connect(self.createProject)
        self.OntoEditBtn = QtWidgets.QPushButton("Edit Ontology")
        self.OntoEditBtn.clicked.connect(self.editProject)
        self.OntoExitBtn = QtWidgets.QPushButton("Close")
        self.OntoExitBtn.clicked.connect(application.quit)
        self.DictWindow = QtWidgets.QWidget()
        self.DictView = QtWidgets.QTableView()
        self.DictView.setGridStyle(QtCore.Qt.SolidLine)
        self.DictView.setShowGrid(True)
        self.DictView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.DictView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.DictView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.DictView.setTabKeyNavigation(True)
        self.DictModel = QtGui.QStandardItemModel()
        self.DictModel.setHorizontalHeaderLabels(["Word", "Tag", "Count"])
        self.DictView.setModel(self.DictModel)
        self.DictSortBtn = QtWidgets.QPushButton("Sort")
        self.DictFilterBtn = QtWidgets.QPushButton("Filter")
        self.ExtendDictBtn = QtWidgets.QPushButton("Extend Dictionary")
        self.ExtendDictBtn.clicked.connect(self.appendTerms)
        self.RemoveTermsBtn = QtWidgets.QPushButton("Remove Terms")
        self.RemoveTermsBtn.clicked.connect(self.removeTerms)
        self.ToClsBtn = QtWidgets.QPushButton("To Classes")
        self.EditBtn = QtWidgets.QPushButton("Edit")
        hbox = QtWidgets.QHBoxLayout()
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.DictView)
        hbox.addWidget(self.DictSortBtn)
        hbox.addWidget(self.DictFilterBtn)
        hbox.addWidget(self.ExtendDictBtn)
        vbox.addLayout(hbox)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.RemoveTermsBtn)
        hbox.addWidget(self.ToClsBtn)
        hbox.addWidget(self.EditBtn)
        vbox.addLayout(hbox)
        self.DictWindow.setLayout(vbox)
        self.ClassesWindow = QtWidgets.QWidget()
        self.ClassesModel = QtGui.QStandardItemModel()
        self.ClassView = QtWidgets.QListView()
        self.ClassView.setModel(self.ClassesModel)
        self.ClassView.setViewMode(0)
        self.ClassView.setMovement(0)
        self.ClassView.setResizeMode(1)
        self.ClassView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ClassView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ClassView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ToClsBtn.clicked.connect(self.pushToClasses)
        self.RemoveClsBtn = QtWidgets.QPushButton("Remove Classes")
        self.RemoveClsBtn.clicked.connect(self.removeClasses)
        self.ChoosePatBtn = QtWidgets.QPushButton("Choose Pattern File")
        self.ChoosePatBtn.clicked.connect(self.chooseFile)
        self.FinalizeBuildBtn = QtWidgets.QPushButton("Launch Properties Master")
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.RemoveClsBtn)
        hbox.addWidget(self.ChoosePatBtn)
        hbox.addWidget(self.FinalizeBuildBtn)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.ClassView)
        vbox.addLayout(hbox)
        self.ClassesWindow.setLayout(vbox)
        self.PropWindow = QtWidgets.QWidget()
        self.PropView = QtWidgets.QTreeView()
        self.FinalizeBuildBtn.clicked.connect(self.finalizeOntology)
        self.PropModel = QtGui.QStandardItemModel()
        self.PropModel.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.PropModel.appendRow([QtGui.QStandardItem("Supperclass - Subclass")])
        self.PropModel.appendRow([QtGui.QStandardItem("Equivalent classes")])
        self.PropModel.appendRow([QtGui.QStandardItem("Object Property")])
        self.PropModel.appendRow([QtGui.QStandardItem("Supperpoperty - Subproperty")])
        self.PropView.setModel(self.PropModel)
        self.EditRngBtn = QtWidgets.QPushButton("Edit Range")
        self.EditDmnBtn = QtWidgets.QPushButton("Edit Domain")
        self.EditSppBtn = QtWidgets.QPushButton("Edit Subproperty")
        self.AppPropBtn = QtWidgets.QPushButton("Append Property")
        self.RemPropBtn = QtWidgets.QPushButton("Remove Property")
        self.EditInvBtn = QtWidgets.QPushButton("Edit Inversity")
        vbox = QtWidgets.QVBoxLayout()
        hbox = QtWidgets.QHBoxLayout()
        vbox.addWidget(self.PropView)
        hbox.addWidget(self.EditRngBtn)
        hbox.addWidget(self.EditDmnBtn)
        vbox.addLayout(hbox)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.EditSppBtn)
        hbox.addWidget(self.AppPropBtn)
        vbox.addLayout(hbox)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.RemPropBtn)
        hbox.addWidget(self.EditInvBtn)
        vbox.addLayout(hbox)
        self.PropWindow.setLayout(vbox)
        self.MainMenu = QtWidgets.QTabWidget()
        self.MainMenu.addTab(self.DictWindow, "Dictionary")
        self.MainMenu.addTab(self.ClassesWindow, "Classes")
        self.MainMenu.addTab(self.PropWindow, "Properties")
        hbox = QtWidgets.QHBoxLayout()
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.MainMenu)
        hbox.addWidget(self.OntoCreateBtn)
        hbox.addWidget(self.OntoEditBtn)
        hbox.addWidget(self.OntoExitBtn)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        self.show()

    def createProject(self):
        projectEditWindow = QtWidgets.QWidget(parent=self, flags=QtCore.Qt.Dialog)
        projectEditWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        projectEditWindow.setFixedSize(500, 150)
        projectEditWindow.setWindowModality(QtCore.Qt.WindowModal)
        projectEditWindow.setWindowTitle("New Project")
        getProjDirBtn = QtWidgets.QPushButton("Browse")
        getAplDocDir = QtWidgets.QPushButton("Browse")
        getContrDocDir = QtWidgets.QPushButton("Browse")
        CreateProjBtn = QtWidgets.QPushButton("Create")
        CancelBtn = QtWidgets.QPushButton("Cancel")
        projectDirectoryLabel = QtWidgets.QLabel("Path to project directory:")
        appliedDocDirLabel = QtWidgets.QLabel("Path to applied docs:")
        contrastDocDirLabel = QtWidgets.QLabel("Path to contrast docs:")
        projectNameLabel = QtWidgets.QLabel("Project name")
        projDirPath = QtWidgets.QLineEdit()
        projDirPath.setText(self.ProjectDict["Project_Dir"])
        aplDocDirPath = QtWidgets.QLineEdit()
        aplDocDirPath.setText(os.environ["HOME"])
        contrDocDirPath = QtWidgets.QLineEdit()
        contrDocDirPath.setText(os.environ["HOME"])
        projName = QtWidgets.QLineEdit()
        projName.setText(self.ProjectDict["Project_Name"])
        gbox = QtWidgets.QGridLayout()
        gbox.addWidget(projectDirectoryLabel, 0, 0)
        gbox.addWidget(projDirPath, 0, 1)
        gbox.addWidget(getProjDirBtn, 0, 2)
        gbox.addWidget(appliedDocDirLabel, 1, 0)
        gbox.addWidget(aplDocDirPath, 1, 1)
        gbox.addWidget(getAplDocDir, 1, 2)
        gbox.addWidget(contrastDocDirLabel, 2, 0)
        gbox.addWidget(contrDocDirPath, 2, 1)
        gbox.addWidget(getContrDocDir, 2, 2)
        gbox.addWidget(projectNameLabel, 3, 0)
        gbox.addWidget(projName, 3, 1)
        gbox.addWidget(CreateProjBtn, 4, 1)
        gbox.addWidget(CancelBtn, 4, 2)
        projectEditWindow.setLayout(gbox)
        getProjDirBtn.clicked.connect(partial(self.browse_dir, projectEditWindow, projDirPath))
        getAplDocDir.clicked.connect(partial(self.browse_dir, projectEditWindow, aplDocDirPath))
        getContrDocDir.clicked.connect(partial(self.browse_dir, projectEditWindow, contrDocDirPath))
        CreateProjBtn.clicked.connect(partial(self.createDir, projectEditWindow, projDirPath, projName, aplDocDirPath, contrDocDirPath))
        CancelBtn.clicked.connect(projectEditWindow.close)
        projectEditWindow.show()

    def editProject(self):
        choseDirWindow = QtWidgets.QFileDialog(parent=self, directory=os.environ["HOME"])
        choseDirWindow.setFixedSize(300, 300)
        choseDirWindow.setWindowModality(QtCore.Qt.WindowModal)
        choseDirWindow.setAcceptMode(0)
        choseDirWindow.setViewMode(0)
        choseDirWindow.setFileMode(2)
        fullDirName = choseDirWindow.getExistingDirectory(parent=choseDirWindow, caption="Choose directory",
                                                      directory=os.environ["HOME"],
                                                      options=QtWidgets.QFileDialog.ShowDirsOnly)
        self.ProjectDict["Project_Name"] = fullDirName.split("/")[-1:][0]
        self.ProjectDict["Project_Dir"] = fullDirName[:-len(fullDirName.split("/")[-1:][0])-1]
        with open(fullDirName + "/data/Applied_Tagged_Text.pickle", "rb") as file:
            words = pickle.load(file)
            for word in words:
                item1 = QtGui.QStandardItem(word)
                item2 = QtGui.QStandardItem(words[word][0])
                item3 = QtGui.QStandardItem(str(words[word][1]))
                self.DictModel.appendRow([item1, item2, item3])
            self.DictView.reset()
        builder = Ontobuilder("{}/{}.owl".format(fullDirName, self.ProjectDict["Project_Name"]))
        classes = list(builder.showClasses())
        if len(classes) != 0:
            for ontoclass in builder.showClasses():
                self.ClassesModel.appendRow(QtGui.QStandardItem(str(ontoclass).split(".")[1]))
            self.ClassView.reset()
            fullfilename = QtWidgets.QFileDialog.getOpenFileName(parent=choseDirWindow, directory=os.environ["HOME"])[0]
            filename = fullfilename.split("/")[-1][:-7]
            self.areaName = filename
            with open("{}/data/{}.pickle".format(fullDirName, filename), "rb") as file:
                self.availableProperties = pickle.load(file)
            if "{}.pickle".format(filename) not in os.listdir("../Properties"):
                src = "{}/data/{}.pickle".format(fullDirName, filename)
                dst = "../Properties/{}.pickle".format(filename)
                shutil.copyfile(src, dst)
            count = 0
            for proptype in self.availableProperties:
                if proptype == "Subclasses":
                    properties = self.availableProperties[proptype].keys()
                    if len(properties) != 0:
                        for prop in self.availableProperties[proptype]:
                            parentRow = self.PropModel.findItems("Supperclass - Subclass")[0]
                            rowTreshold = self.PropModel.rowCount(parent=self.PropModel.indexFromItem(parentRow))
                            parentRow.setChild(rowTreshold, 0, QtGui.QStandardItem("Name:"))
                            parentRow.setChild(rowTreshold, 1, QtGui.QStandardItem(prop))
                            childRow = parentRow.child(rowTreshold)
                            childRow.setChild(0, 0, QtGui.QStandardItem("Domain:"))
                            childRow.setChild(0, 1, QtGui.QStandardItem(self.availableProperties[proptype][prop]["Domain"]))
                            childRow.setChild(1, 0, QtGui.QStandardItem("Range:"))
                            childRow.setChild(1, 1, QtGui.QStandardItem(self.availableProperties[proptype][prop]["Range"]))
                            childRow.setChild(2, 0, QtGui.QStandardItem("Pattern:"))
                            childRow.setChild(2, 1, QtGui.QStandardItem(self.availableProperties[proptype][prop]["Pattern"]))
                            count += 1
                elif proptype == "EquivClasses":
                    properties = self.availableProperties[proptype].keys()
                    if len(properties) != 0:
                        for prop in self.availableProperties[proptype]:
                            parentRow = self.PropModel.findItems("Equivalent classes")[0]
                            rowTreshold = self.PropModel.rowCount(parent=self.PropModel.indexFromItem(parentRow))
                            parentRow.setChild(rowTreshold, 0, QtGui.QStandardItem("Name:"))
                            parentRow.setChild(rowTreshold, 1, QtGui.QStandardItem(prop))
                            childRow = parentRow.child(rowTreshold)
                            childRow.setChild(0, 0, QtGui.QStandardItem("Domain:"))
                            childRow.setChild(0, 1, QtGui.QStandardItem(self.availableProperties[proptype][prop]["Domain"]))
                            childRow.setChild(1, 0, QtGui.QStandardItem("Range:"))
                            childRow.setChild(1, 1,  QtGui.QStandardItem(self.availableProperties[proptype][prop]["Range"]))
                            childRow.setChild(2, 0, QtGui.QStandardItem("Pattern:"))
                            childRow.setChild(2, 1, QtGui.QStandardItem(self.availableProperties[proptype][prop]["Pattern"]))
                            count += 1
                elif proptype == "ObjectProperties":
                    properties = self.availableProperties[proptype].keys()
                    if len(properties) != 0:
                        for prop in self.availableProperties[proptype]:
                            parentRow = self.PropModel.findItems("Object Property")[0]
                            rowTreshold = self.PropModel.rowCount(parent=self.PropModel.indexFromItem(parentRow))
                            parentRow.setChild(rowTreshold, 0, QtGui.QStandardItem("Name:"))
                            parentRow.setChild(rowTreshold, 1, QtGui.QStandardItem(prop))
                            childRow = parentRow.child(rowTreshold)
                            childRow.setChild(0, 0, QtGui.QStandardItem("Domain:"))
                            childRow.setChild(0, 1, QtGui.QStandardItem(self.availableProperties[proptype][prop]["Domain"]))
                            childRow.setChild(1, 0, QtGui.QStandardItem("Range:"))
                            childRow.setChild(1, 1, QtGui.QStandardItem(self.availableProperties[proptype][prop]["Range"]))
                            childRow.setChild(2, 0, QtGui.QStandardItem("Inversed Property:"))
                            childRow.setChild(2, 1, QtGui.QStandardItem(self.availableProperties[proptype][prop]["Inversed Property"]))
                            childRow.setChild(3, 0, QtGui.QStandardItem("Pattern:"))
                            childRow.setChild(3, 1, QtGui.QStandardItem(self.availableProperties[proptype][prop]["Pattern"]))
                            count += 1
                elif proptype == "Subproperties":
                    properties = self.availableProperties[proptype].keys()
                    if len(properties) != 0:
                        for prop in self.availableProperties[proptype]:
                            parentRow = self.PropModel.findItems("Supperpoperty - Subproperty")[0]
                            rowTreshold = self.PropModel.rowCount(parent=self.PropModel.indexFromItem(parentRow))
                            parentRow.setChild(rowTreshold, 0, QtGui.QStandardItem("Name:"))
                            parentRow.setChild(rowTreshold, 1, QtGui.QStandardItem(prop))
                            childRow = parentRow.child(rowTreshold)
                            childRow.setChild(0, 0, QtGui.QStandardItem("Domain:"))
                            childRow.setChild(0, 1,  QtGui.QStandardItem(self.availableProperties[proptype][prop]["Domain"]))
                            childRow.setChild(1, 0, QtGui.QStandardItem("Range:"))
                            childRow.setChild(1, 1, QtGui.QStandardItem(self.availableProperties[proptype][prop]["Range"]))
                            childRow.setChild(2, 0, QtGui.QStandardItem("Inversed Property:"))
                            childRow.setChild(2, 1, QtGui.QStandardItem(self.availableProperties[proptype][prop]["Inversed Property"]))
                            childRow.setChild(3, 0, QtGui.QStandardItem("Pattern:"))
                            childRow.setChild(3, 1, QtGui.QStandardItem(self.availableProperties[proptype][prop]["Pattern"]))
                            count += 1
            self.PropView.reset()

    def appendTerms(self):
        appendTermsWindow = QtWidgets.QWidget(parent=self, flags=QtCore.Qt.Dialog)
        appendTermsWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        appendTermsWindow.setFixedSize(500, 150)
        appendTermsWindow.setWindowModality(QtCore.Qt.WindowModal)
        appendTermsWindow.setWindowTitle("Append Terms")
        newTermsFileDirBtn = QtWidgets.QPushButton("Browse")
        AppendTermsBtn = QtWidgets.QPushButton("Confirm")
        CancelBtn = QtWidgets.QPushButton("Cancel")
        newTermsDirLabel = QtWidgets.QLabel("Path to new terms directory:")
        newTermsDirPath = QtWidgets.QLineEdit()
        gbox = QtWidgets.QGridLayout()
        gbox.addWidget(newTermsDirLabel, 0, 0)
        gbox.addWidget(newTermsDirPath, 0, 1)
        gbox.addWidget(newTermsFileDirBtn, 0, 2)
        gbox.addWidget(AppendTermsBtn, 1, 1)
        gbox.addWidget(CancelBtn, 1, 2)
        appendTermsWindow.setLayout(gbox)
        newTermsFileDirBtn.clicked.connect(partial(self.browse_dir, appendTermsWindow, newTermsDirPath))
        AppendTermsBtn.clicked.connect(partial(self.insertNewTerms, appendTermsWindow, newTermsDirPath))
        CancelBtn.clicked.connect(appendTermsWindow.close)
        appendTermsWindow.show()

    def removeTerms(self):
        ChoosenRows = self.DictView.selectedIndexes()
        if len(ChoosenRows) == 0: pass
        fname = "{}/{}/data/Applied_Cleaned_Text.pickle".format(self.ProjectDict["Project_Dir"],
                                                                       self.ProjectDict["Project_Name"])
        file = open(fname, "rb")
        currDict = pickle.load(file)
        file.close()
        with open(fname, "wb") as file:
            count = 0
            while count < len(ChoosenRows) / 3:
                term = QtGui.QStandardItem(ChoosenRows[count * 3].data()).text()
                count += 1
                currDict.pop(term)
            pickle.dump(currDict, file)
        self.DictModel.clear()
        for word in currDict:
            item1 = QtGui.QStandardItem(word)
            item2 = QtGui.QStandardItem(currDict[word][0])
            item3 = QtGui.QStandardItem(str(currDict[word][1]))
            self.DictModel.appendRow([item1, item2, item3])
        self.DictView.setModel(self.DictModel)
        self.DictView.reset()

    def pushToClasses(self):
        fname = "{}/{}/{}.owl".format(self.ProjectDict["Project_Dir"], self.ProjectDict["Project_Name"], self.ProjectDict["Project_Name"])
        ChoosenRows = self.DictView.selectedIndexes()
        builder = Ontobuilder(fname)
        if len(ChoosenRows) != 0:
            count = 0
            terms = []
            while count < len(ChoosenRows) / 3:
                term = QtGui.QStandardItem(ChoosenRows[count * 3].data())
                self.ClassesModel.appendRow(term)
                terms.append(term.text())
                count += 1
            builder.defineClasses(words=terms)
            builder.save()
            self.ClassView.reset()

    def removeClasses(self):
        fname = "{}/{}/{}.owl".format(self.ProjectDict["Project_Dir"], self.ProjectDict["Project_Name"], self.ProjectDict["Project_Name"])
        ChoosenRows = [idx.row() for idx in self.ClassView.selectedIndexes()]
        builder = Ontobuilder(fname)
        if len(ChoosenRows) != 0:
            count = 0
            for index in sorted(ChoosenRows):
                term = self.ClassesModel.takeRow(index - count)[0]
                builder.deleteEntity(term.text())
                count += 1
            builder.save()
            self.ClassView.reset()
	
    def chooseFile(self):
        chooseFileWindow = QtWidgets.QWidget(parent=self, flags=QtCore.Qt.Dialog)
        chooseFileWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        chooseFileWindow.setFixedSize(500, 500)
        chooseFileWindow.setWindowModality(QtCore.Qt.WindowModal)
        chooseFileWindow.setWindowTitle("Choose Property File")
        model = QtGui.QStandardItemModel()
        files = os.listdir("../Properties/")
        if len(files) != 0:
            for file in files:
                model.appendRow(QtGui.QStandardItem(file[:-7]))
        view = QtWidgets.QListView()
        view.setViewMode(0)
        view.setMovement(0)
        view.setResizeMode(1)
        view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        view.setModel(model)
        ChooseFileBtn = QtWidgets.QPushButton("Choose File")
        NewFileBtn = QtWidgets.QPushButton("New File")
        DeleteFileBtn = QtWidgets.QPushButton("Delete File")
        CancelBtn = QtWidgets.QPushButton("Cancel")
        Label = QtWidgets.QLabel("New File's Name:")
        Fname = QtWidgets.QLineEdit()
        hbox0 = QtWidgets.QHBoxLayout()
        hbox0.addWidget(Label)
        hbox0.addWidget(Fname)
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(ChooseFileBtn)
        hbox1.addWidget(NewFileBtn)
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(DeleteFileBtn)
        hbox2.addWidget(CancelBtn)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(view)
        vbox.addLayout(hbox0)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        chooseFileWindow.setLayout(vbox)
        ChooseFileBtn.clicked.connect(partial(self.getPattern, view, chooseFileWindow))
        NewFileBtn.clicked.connect(partial(self.newFile, Fname, view, chooseFileWindow))
        DeleteFileBtn.clicked.connect(partial(self.deletePattern, view))
        CancelBtn.clicked.connect(chooseFileWindow.close)
        chooseFileWindow.show()
		
    def getPattern(self, target, window):
        fname = QtGui.QStandardItem(target.selectedIndexes()[0].data()).text()
        self.areaName = fname
        fullname = "../Properties/" + fname + ".pickle"
        with open(fullname, "rb") as file:
            self.availableProperties = pickle.load(file)
        window.close()
	
    def newFile(self, FLine, target, window):
        fname = FLine.text()
        self.areaName = fname
        target.model().appendRow(QtGui.QStandardItem(fname))
        target.reset()
        fullname = "../Properties/" + fname + ".pickle"
        file = open(fullname, "wb")
        file.close()
        window.close()
	
    def deletePattern(self, target):
        index = target.selectedIndexes()[0]
        fname = target.model().takeRow(index.row())
        fullname = "../Properties/{}.pickle".format(fname)
        os.remove(fullname)
        fullname = "{}/{}/data/{}.pickle".format(self.ProjectDict["Project_Dir"], self.ProjectDict["Project_Name"], fname)
        os.remove(fullname)
        target.reset()
	
    def finalizeOntology(self):
        if self.areaName == "": raise FileNotFoundError("Specify Pattern File Name!")
        propertyMasterWindow = QtWidgets.QWidget(parent=self, flags=QtCore.Qt.Dialog)
        propertyMasterWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        propertyMasterWindow.setFixedSize(500, 500)
        propertyMasterWindow.setWindowModality(QtCore.Qt.WindowModal)
        propertyMasterWindow.setWindowTitle("Master of properties")
        stub = QtGui.QStandardItem(" ")
        PropModel = QtGui.QStandardItemModel()
        PropModel.setHorizontalHeaderLabels(["Type", "Domain", "Range", "Name", "Inversed Property", "Search", "Pattern"])
        for _ in range(15): PropModel.appendRow([stub,stub,stub,stub,stub,stub])
        PropView = QtWidgets.QTableView()
        PropView.setGridStyle(QtCore.Qt.SolidLine)
        PropView.setShowGrid(True)
        PropView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        PropView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        PropView.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        PropView.setTabKeyNavigation(True)
        PropView.setModel(PropModel)
        GenPropBtn = QtWidgets.QPushButton("Generate Properties")
        AcceptPropBtn = QtWidgets.QPushButton("Accept Selected")
        FinishBtn = QtWidgets.QPushButton("Finish")
        DeletePropBtn = QtWidgets.QPushButton("Delete Selected")
        gbox = QtWidgets.QGridLayout()
        gbox.addWidget(GenPropBtn, 0, 0)
        gbox.addWidget(AcceptPropBtn, 0, 1)
        gbox.addWidget(FinishBtn, 2, 1)
        gbox.addWidget(DeletePropBtn, 2, 2)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(PropView)
        vbox.addLayout(gbox)
        propertyMasterWindow.setLayout(vbox)
        FinishBtn.clicked.connect(propertyMasterWindow.close)
        GenPropBtn.clicked.connect(partial(self.generateProperties, PropView))
        AcceptPropBtn.clicked.connect(partial(self.acceptProperties, PropView))
        DeletePropBtn.clicked.connect(partial(self.removeProperties, PropView))
        PropView.doubleClicked.connect(partial(self._fillData, propertyMasterWindow, PropView))
        propertyMasterWindow.show()

    def _fillData(self, parent, target):
        if len(target.selectedIndexes()) > 1:
            return
        col = target.selectedIndexes()[0].column()
        row = target.selectedIndexes()[0].row()
        model = target.model()
        getTerms = lambda view: [QtGui.QStandardItem(idx.data()).text() for idx in view.selectedIndexes()]
        concatTerms = lambda view: ";".join(map(str, getTerms(view)))
        pasteTerms = lambda target, view, row, col: target.model().setItem(row, col, QtGui.QStandardItem(concatTerms(view)))
        setTypeFunc = lambda model, param, row, col: model.setItem(row, col, QtGui.QStandardItem(param))
        if col == 0:
            propertyWindow = QtWidgets.QWidget(parent=parent, flags=QtCore.Qt.Dialog)
            propertyWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
            propertyWindow.setFixedSize(300, 300)
            propertyWindow.setWindowModality(QtCore.Qt.WindowModal)
            propertyWindow.setWindowTitle("Chose property type")
            mainbox = QtWidgets.QVBoxLayout()
            box = QtWidgets.QGroupBox()
            vbox = QtWidgets.QVBoxLayout()
            SubclassType = QtWidgets.QRadioButton("Type Supperclass - Subclass")
            SubclassType.setChecked(False)
            EquivClassType = QtWidgets.QRadioButton("Type Equivalent Classes")
            EquivClassType.setChecked(False)
            ObjPropType = QtWidgets.QRadioButton("Type Object Property")
            ObjPropType.setChecked(False)
            ConfirmBtn = QtWidgets.QPushButton("Confirm")
            vbox.addWidget(SubclassType)
            vbox.addWidget(EquivClassType)
            vbox.addWidget(ObjPropType)
            box.setLayout(vbox)
            mainbox.addWidget(box)
            mainbox.addWidget(ConfirmBtn)
            propertyWindow.setLayout(mainbox)
            SubclassType.toggled.connect(partial(setTypeFunc, model, "SubclassOf", row, col))
            EquivClassType.toggled.connect(partial(setTypeFunc, model, "EquivClasses", row, col))
            ObjPropType.toggled.connect(partial(setTypeFunc, model, "ObjProp", row, col))
            ConfirmBtn.clicked.connect(propertyWindow.close)
            propertyWindow.show()
        elif (col == 1):
            domainWindow = QtWidgets.QWidget(parent=parent, flags=QtCore.Qt.Dialog)
            domainWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
            domainWindow.setFixedSize(300, 300)
            domainWindow.setWindowModality(QtCore.Qt.WindowModal)
            domainWindow.setWindowTitle("Chose property domain")
            domain_model = QtGui.QStandardItemModel()
            self.ClassView.selectAll()
            for term in [QtGui.QStandardItem(idx.data()).text() for idx in self.ClassView.selectedIndexes()]:
                domain_model.appendRow(QtGui.QStandardItem(term))
            DomainView = QtWidgets.QListView()
            DomainView.setModel(domain_model)
            DomainView.setViewMode(0)
            DomainView.setMovement(0)
            DomainView.setResizeMode(1)
            DomainView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            DomainView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            DomainView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            CloseBtn = QtWidgets.QPushButton("Close")
            ConfirmBtn = QtWidgets.QPushButton("Confirm")
            vbox = QtWidgets.QVBoxLayout()
            gbox = QtWidgets.QGridLayout()
            gbox.addWidget(ConfirmBtn, 0, 1)
            gbox.addWidget(CloseBtn, 0, 2)
            vbox.addWidget(DomainView)
            vbox.addLayout(gbox)
            domainWindow.setLayout(vbox)
            ConfirmBtn.clicked.connect(partial(pasteTerms, target, DomainView, row, col))
            CloseBtn.clicked.connect(partial(finalize, target, domainWindow))
            domainWindow.show()
        elif col == 2:
            rangeWindow = QtWidgets.QWidget(parent=parent, flags=QtCore.Qt.Dialog)
            rangeWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
            rangeWindow.setFixedSize(300, 300)
            rangeWindow.setWindowModality(QtCore.Qt.WindowModal)
            rangeWindow.setWindowTitle("Chose property range")
            range_model = QtGui.QStandardItemModel()
            self.ClassView.selectAll()
            for term in [QtGui.QStandardItem(idx.data()).text() for idx in self.ClassView.selectedIndexes()]:
                range_model.appendRow(QtGui.QStandardItem(term))
            RangeView = QtWidgets.QListView()
            RangeView.setModel(range_model)
            RangeView.setViewMode(0)
            RangeView.setMovement(0)
            RangeView.setResizeMode(1)
            RangeView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            RangeView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            RangeView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            CloseBtn = QtWidgets.QPushButton("Close")
            ConfirmBtn = QtWidgets.QPushButton("Confirm")
            vbox = QtWidgets.QVBoxLayout()
            gbox = QtWidgets.QGridLayout()
            gbox.addWidget(ConfirmBtn, 0, 1)
            gbox.addWidget(CloseBtn, 0, 2)
            vbox.addWidget(RangeView)
            vbox.addLayout(gbox)
            rangeWindow.setLayout(vbox)
            ConfirmBtn.clicked.connect(partial(pasteTerms, target, RangeView, row, col))
            CloseBtn.clicked.connect(partial(finalize, target, rangeWindow))
            rangeWindow.show()

    def removeProperties(self, target):
        file = open("../Properties/{}.pickle".format(self.areaName), "wb")
        ChoosenRows = target.selectionModel().selectedRows()
        if len(ChoosenRows) != 0:
            count = 0
            for index in sorted(ChoosenRows):
                delprop = target.model().takeRow(index.row() - count)
                proptype = QtGui.QStandardItem(delprop[0].data()).text()
                if proptype == "SubclassOf":
                    self.availableProperties["Subclasses"].pop(delprop)
                elif proptype == "EquivClasses":
                    self.availableProperties["EquivClasses"].pop(delprop)
                elif proptype == "ObjProp":
                    self.availableProperties["ObjectProperties"].pop(delprop)
                elif proptype == "SubProp":
                    self.availableProperties["Subproperties"].pop(delprop)
                count += 1
            target.reset()
        pickle.dump(self.availableProperties, file)
        file.close()
		
    def generateProperties(self, target):
        ChoosenRows = target.selectedIndexes()
        ChoosenRowsIdxs = target.selectionModel().selectedRows()
        if len(ChoosenRows) != 0:
            RowsDict = {}
            ProjDir = self.ProjectDict["Project_Dir"]
            ProjName = self.ProjectDict["Project_Name"]
            extractor = RelationExtractor({})
            extractor.readCleanDict(fname = ProjDir + "/" + ProjName + "/data/Applied_Cleaned_Text.pickle")
            linked_text = {}
            with open(ProjDir + "/" + ProjName + "/data/Applied_Linked_Text.pickle", "rb") as file:
                linked_text = pickle.load(file)
            for i in range(len(ChoosenRowsIdxs)):
                RowsDict[ChoosenRowsIdxs[i]] = ChoosenRows[i * 7: (i * 7) + 7]
            count = 0
            for idx in sorted(list(RowsDict.keys())):
                term1 = QtGui.QStandardItem(RowsDict[idx][1].data()).text()
                term2 = QtGui.QStandardItem(RowsDict[idx][2].data()).text()
                pair = [(term1, extractor.cleanDict[term1][0]), (term2, extractor.cleanDict[term2][0])]
                search = QtGui.QStandardItem(RowsDict[idx][5].data()).text()
                pattern = extractor.supposePatterns(wordpair = pair, linked_text=linked_text, conttres=0, search=eval(search))
                if pattern != None:
                    target.model().setItem(idx.row() + count, 6, QtGui.QStandardItem(pattern))
                    pairs = extractor.parsePattern(pattern=pattern, tokenizedText=linked_text)
                    clean_pairs = []
                    for elem in pairs:
                        if elem not in clean_pairs:
                            clean_pairs.append(elem)
                    for result in clean_pairs:
                        if result[0] == pair[0][0] and result[1] == pair[1][0]: continue
                        count += 1
                        target.model().setItem(idx.row() + count, 1, QtGui.QStandardItem(result[0]))
                        target.model().setItem(idx.row() + count, 2, QtGui.QStandardItem(result[1]))
                        target.model().setItem(idx.row() + count, 5, QtGui.QStandardItem(search))
                else:
                    print("Pattern not found")
            target.reset()
		
    def acceptProperties(self, target):

        ChoosenRows = target.selectedIndexes()
        ChoosenRowsIdxs = target.selectionModel().selectedRows()
        if len(ChoosenRows) != 0:
            file = open("../Properties/{}.pickle".format(self.areaName), "wb")
            RowsDict = {}
            ProjDir = self.ProjectDict["Project_Dir"]
            ProjName = self.ProjectDict["Project_Name"]
            builder = Ontobuilder(ProjDir + "/" + ProjName + "/" + ProjName + ".owl")
            for i in range(len(ChoosenRowsIdxs)):
                RowsDict[ChoosenRowsIdxs[i]] = ChoosenRows[i * 7: (i * 7) + 7]
            count = 0
            for idx in sorted(list(RowsDict.keys())):
                type = QtGui.QStandardItem(RowsDict[idx][0].data()).text()
                if type == "SubclassOf":
                    term1 = QtGui.QStandardItem(RowsDict[idx][1].data()).text()
                    term2 = QtGui.QStandardItem(RowsDict[idx][2].data()).text()
                    if term1 != "" and term2 != "":
                        pair = [term1, term2]
                        builder.defineProperty(pairs=pair, proptype="Subclass_Of")
                        parentRow = self.PropModel.findItems("Supperclass - Subclass")[0]
                        rowTreshold = self.PropModel.rowCount(parent=self.PropModel.indexFromItem(parentRow))
                        parentRow.setChild(rowTreshold, 0, QtGui.QStandardItem("Name:"))
                        parentRow.setChild(rowTreshold, 1, QtGui.QStandardItem("Property_{}".format(rowTreshold + 1)))
                        domain = QtGui.QStandardItem(RowsDict[idx][1].data()).text()
                        rng = QtGui.QStandardItem(RowsDict[idx][2].data()).text()
                        pattern = QtGui.QStandardItem(RowsDict[idx][6].data()).text()
                        childRow = parentRow.child(rowTreshold)
                        childRow.setChild(0, 0, QtGui.QStandardItem("Domain:"))
                        childRow.setChild(0, 1, QtGui.QStandardItem(RowsDict[idx][1].data()))
                        childRow.setChild(1, 0, QtGui.QStandardItem("Range:"))
                        childRow.setChild(1, 1, QtGui.QStandardItem(RowsDict[idx][2].data()))
                        childRow.setChild(2, 0, QtGui.QStandardItem("Pattern:"))
                        childRow.setChild(2, 1, QtGui.QStandardItem(RowsDict[idx][6].data()))
                        target.model().takeRow(idx.row() - count)
                        self.availableProperties["Subclasses"]["Property_{}".format(rowTreshold + 1)] = {}
                        self.availableProperties["Subclasses"]["Property_{}".format(rowTreshold + 1)]["Domain"] = domain
                        self.availableProperties["Subclasses"]["Property_{}".format(rowTreshold + 1)]["Range"] = rng
                        self.availableProperties["Subclasses"]["Property_{}".format(rowTreshold + 1)]["Pattern"] = pattern
                        builder.defineProperty(pairs=[pair], proptype="Subclass_Of")
                        count += 1
                elif type == "EquivClasses":
                    term1 = QtGui.QStandardItem(RowsDict[idx][1].data()).text()
                    term2 = QtGui.QStandardItem(RowsDict[idx][2].data()).text()
                    if term1 != "" and term2 != "":
                        pair = [term1, term2]
                        builder.defineProperty(pairs=pair, proptype="Equal_Class_Of")
                        parentRow = self.PropModel.findItems("Equivalent classes")[0]
                        rowTreshold = self.PropModel.rowCount(parent=self.PropModel.indexFromItem(parentRow))
                        parentRow.setChild(rowTreshold, 0, QtGui.QStandardItem("Name:"))
                        parentRow.setChild(rowTreshold, 1, QtGui.QStandardItem("Property_{}".format(rowTreshold + 1)))
                        domain = QtGui.QStandardItem(RowsDict[idx][1].data()).text()
                        rng = QtGui.QStandardItem(RowsDict[idx][2].data()).text()
                        pattern = QtGui.QStandardItem(RowsDict[idx][6].data()).text()
                        childRow = parentRow.child(rowTreshold)
                        childRow.setChild(0, 0, QtGui.QStandardItem("Domain:"))
                        childRow.setChild(0, 1, QtGui.QStandardItem(RowsDict[idx][1].data()))
                        childRow.setChild(1, 0, QtGui.QStandardItem("Range:"))
                        childRow.setChild(1, 1, QtGui.QStandardItem(RowsDict[idx][2].data()))
                        childRow.setChild(2, 0, QtGui.QStandardItem("Pattern:"))
                        childRow.setChild(2, 1, QtGui.QStandardItem(RowsDict[idx][6].data()))
                        target.model().takeRow(idx.row() - count)
                        self.availableProperties["EquivClasses"]["Property_{}".format(rowTreshold + 1)] = {}
                        self.availableProperties["EquivClasses"]["Property_{}".format(rowTreshold + 1)]["Domain"] = domain
                        self.availableProperties["EquivClasses"]["Property_{}".format(rowTreshold + 1)]["Range"] = rng
                        self.availableProperties["EquivClasses"]["Property_{}".format(rowTreshold + 1)]["Pattern"] = pattern
                        builder.defineProperty(pairs=[pair], proptype="Equal_Class_Of")
                        count += 1
                elif type == "ObjProp":
                    term1 = QtGui.QStandardItem(RowsDict[idx][1].data()).text()
                    term2 = QtGui.QStandardItem(RowsDict[idx][2].data()).text()
                    name = QtGui.QStandardItem(RowsDict[idx][3].data()).text()
                    if term1 != "" and term2 != "" and name != "":
                        pair = [term1, term2]
                        builder.defineProperty(pairs=pair, proptype="Object_Property", name=name, inverse_property=QtGui.QStandardItem(RowsDict[idx][4].data()).text())
                        parentRow = self.PropModel.findItems("Object Property")[0]
                        rowTreshold = self.PropModel.rowCount(parent=self.PropModel.indexFromItem(parentRow))
                        propname = QtGui.QStandardItem(RowsDict[idx][3].data()).text()
                        parentRow.setChild(rowTreshold, 0, QtGui.QStandardItem("Name:"))
                        parentRow.setChild(rowTreshold, 1, QtGui.QStandardItem(propname))
                        domain = QtGui.QStandardItem(RowsDict[idx][1].data()).text()
                        rng = QtGui.QStandardItem(RowsDict[idx][2].data()).text()
                        inv = QtGui.QStandardItem(RowsDict[idx][4].data()).text()
                        pattern = QtGui.QStandardItem(RowsDict[idx][6].data()).text()
                        childRow = parentRow.child(rowTreshold)
                        childRow.setChild(0, 0, QtGui.QStandardItem("Domain:"))
                        childRow.setChild(0, 1, QtGui.QStandardItem(RowsDict[idx][1].data()))
                        childRow.setChild(1, 0, QtGui.QStandardItem("Range:"))
                        childRow.setChild(1, 1, QtGui.QStandardItem(RowsDict[idx][2].data()))
                        childRow.setChild(2, 0, QtGui.QStandardItem("Inversed Property:"))
                        childRow.setChild(2, 1, QtGui.QStandardItem(RowsDict[idx][4].data()))
                        childRow.setChild(3, 0, QtGui.QStandardItem("Pattern:"))
                        childRow.setChild(3, 1, QtGui.QStandardItem(RowsDict[idx][6].data()))
                        target.model().takeRow(idx.row() - count)
                        self.availableProperties["ObjectProperties"][propname] = {}
                        self.availableProperties["ObjectProperties"][propname]["Domain"] = domain
                        self.availableProperties["ObjectProperties"][propname]["Range"] = rng
                        self.availableProperties["ObjectProperties"][propname]["Inversed Property"] = inv
                        self.availableProperties["ObjectProperties"][propname][ "Pattern"] = pattern
                        builder.defineProperty(pairs=[pair], proptype="Object_Property", name=propname, inverse_property=inv)
                        count += 1
                elif type == "SubProp":
                    term1 = QtGui.QStandardItem(RowsDict[idx][1].data()).text()
                    term2 = QtGui.QStandardItem(RowsDict[idx][2].data()).text()
                    if term1 != "" and term2 != "":
                        pair = [term1, term2]
                        builder.defineProperty(pairs=pair, proptype="Subproperty", inverse_property=QtGui.QStandardItem(RowsDict[idx][4].data()).text())
                        parentRow = self.PropModel.findItems("Supperpoperty - Subproperty")[0]
                        rowTreshold = self.PropModel.rowCount(parent=self.PropModel.indexFromItem(parentRow))
                        propname = QtGui.QStandardItem(RowsDict[idx][3].data()).text()
                        parentRow.setChild(rowTreshold, 0, QtGui.QStandardItem("Name:"))
                        parentRow.setChild(rowTreshold, 1, QtGui.QStandardItem(propname))
                        domain = QtGui.QStandardItem(RowsDict[idx][1].data()).text()
                        rng = QtGui.QStandardItem(RowsDict[idx][2].data()).text()
                        inv = QtGui.QStandardItem(RowsDict[idx][4].data()).text()
                        pattern = QtGui.QStandardItem(RowsDict[idx][6].data()).text()
                        childRow = parentRow.child(rowTreshold)
                        childRow.setChild(0, 0, QtGui.QStandardItem("Domain:"))
                        childRow.setChild(0, 1, QtGui.QStandardItem(RowsDict[idx][1].data()))
                        childRow.setChild(1, 0, QtGui.QStandardItem("Range:"))
                        childRow.setChild(1, 1, QtGui.QStandardItem(RowsDict[idx][2].data()))
                        childRow.setChild(2, 0, QtGui.QStandardItem("Inversed Property:"))
                        childRow.setChild(2, 1, QtGui.QStandardItem(RowsDict[idx][4].data()))
                        childRow.setChild(3, 0, QtGui.QStandardItem("Pattern:"))
                        childRow.setChild(3, 1, QtGui.QStandardItem(RowsDict[idx][6].data()))
                        target.model().takeRow(idx.row() - count)
                        self.availableProperties["Subproperties"][propname] = {}
                        self.availableProperties["Subproperties"][propname]["Domain"] = domain
                        self.availableProperties["Subproperties"][propname]["Range"] = rng
                        self.availableProperties["Subproperties"][propname]["Inversed Property"] = inv
                        self.availableProperties["Subproperties"][propname]["Pattern"] = pattern
                        builder.defineProperty(pairs=[pair], proptype="Object_Property", name=propname, inverse_property=inv)
                        count += 1
                else:
                    continue
            builder.save()
            target.reset()
            self.PropView.reset()
            pickle.dump(self.availableProperties, file)
            file.close()
            src = "../Properties/{}.pickle".format(self.areaName)
            dst = "{}/{}/data/{}.pickle".format(self.ProjectDict["Project_Dir"], self.ProjectDict["Project_Name"], self.areaName)
            shutil.copyfile(src, dst)

    def browse_dir(self, parent, target):
        choseDirWindow = QtWidgets.QFileDialog(parent=self, directory=os.environ["HOME"])
        choseDirWindow.setFixedSize(300, 300)
        choseDirWindow.setWindowModality(QtCore.Qt.WindowModal)
        choseDirWindow.setAcceptMode(0)
        choseDirWindow.setViewMode(0)
        choseDirWindow.setFileMode(2)
        dirName = choseDirWindow.getExistingDirectory(parent=parent, caption="Choose directory",
                                                      directory=os.environ["HOME"],
                                                      options=QtWidgets.QFileDialog.ShowDirsOnly)
        target.setText(dirName)

    def insertNewTerms(self, parent, target):
        dirName = target.text()
        datapath = "{}/{}/data/".format(self.ProjectDict["Project_Dir"], self.ProjectDict["Project_Name"])
        corpuspath = "{}/{}/Applied_corpus/".format(self.ProjectDict["Project_Dir"], self.ProjectDict["Project_Name"])
        for file in os.listdir(dirName):
            if not file.endswith(".docx"): continue
            src = dirName + "/" + file
            dst = corpuspath + file
            shutil.copyfile(src, dst)
        newReader = CorpusReader(corpuspath)
        newReader.createRawCorpus(lower=True)
        newReader.tokenizeText()
        newReader.lematizeText()
        newReader.tagText()
        newReader.cleanNolex()
        newReader.errazeStopWords()
        newReader.lematizeDict()
        newReader.dropToFileRawText(fname = datapath + "Applied_Raw_Text")
        newReader.dropToFileTokenizedText(fname = datapath + "Applied_Tokenized_Text")
        newReader.dropToFileTaggedText(fname = datapath + "Applied_Tagged_Text")
        newReader.linkText()
        newReader.dropToFileTokenizedText(fname = datapath + "Applied_Linked_Text")
        file = open(datapath + "Contrast_Tagged_Text.pickle", "rb")
        contrData = pickle.load(file)
        file.close()
        relationExtractor = RelationExtractor(newReader.taggedText)
        relationExtractor.contrastErrase(contrastDict=contrData, policy="soft")
        relationExtractor.dropToFile(fname = datapath + "Applied_Cleaned_Text")
        self.DictModel.clear()
        for term in newReader.taggedText:
            item1 = QtGui.QStandardItem(term)
            item2 = QtGui.QStandardItem(newReader.taggedText[term][0])
            item3 = QtGui.QStandardItem(str(newReader.taggedText[term][1]))
            self.DictModel.appendRow([item1, item2, item3])
        self.DictView.reset()
        parent.close()

    def createDir(self, parent, projDirPath, projName, aplDocDirPath, contrDocDirPath):
        ProjDir = projDirPath.text()
        ProjName = projName.text()
        AplDocDir = aplDocDirPath.text()
        ContrDocDir = contrDocDirPath.text()
        self.ProjectDict["Project_Dir"] = ProjDir
        self.ProjectDict["Project_Name"] = ProjName
        os.mkdir(ProjDir + "/" + ProjName)
        os.mkdir(ProjDir + "/" + ProjName + "/Applied_corpus")
        os.mkdir(ProjDir + "/" + ProjName + "/Contrast_corpus")
        os.mkdir(ProjDir + "/" + ProjName + "/data")
        for file in os.listdir(AplDocDir):
            if not file.endswith(".docx"): continue
            src = AplDocDir + "/" + file
            dst = ProjDir + "/" + ProjName + "/Applied_corpus/" + file
            shutil.copyfile(src, dst)
        for file in os.listdir(ContrDocDir):
            if not file.endswith(".docx"): continue
            src = ContrDocDir + "/" + file
            dst = ProjDir + "/" + ProjName + "/Contrast_corpus/" + file
            shutil.copyfile(src, dst)
        appliedReader = CorpusReader(path = AplDocDir)
        appliedReader.createRawCorpus(lower = True)
        appliedReader.tokenizeText()
        appliedReader.lematizeText()
        appliedReader.tagText()
        appliedReader.cleanNolex()
        appliedReader.errazeStopWords()
        appliedReader.lematizeDict()
        appliedReader.dropToFileRawText(fname = ProjDir + "/" + ProjName + "/data/Applied_Raw_Text")
        appliedReader.dropToFileTokenizedText(fname = ProjDir + "/" + ProjName + "/data/Applied_Tokenized_Text")
        appliedReader.dropToFileTaggedText(fname = ProjDir + "/" + ProjName + "/data/Applied_Tagged_Text")
        appliedReader.linkText()
        appliedReader.dropToFileTokenizedText(fname = ProjDir + "/" + ProjName + "/data/Applied_Linked_Text")
        contrastReader = CorpusReader(path = ContrDocDir)
        contrastReader.createRawCorpus(lower = True)
        contrastReader.tokenizeText()
        contrastReader.lematizeText()
        contrastReader.tagText()
        contrastReader.cleanNolex()
        contrastReader.errazeStopWords()
        contrastReader.lematizeDict()
        contrastReader.dropToFileTaggedText(fname = ProjDir + "/" + ProjName + "/data/Contrast_Tagged_Text")
        relationExtractor = RelationExtractor(appliedReader.taggedText)
        relationExtractor.contrastErrase(contrastDict = contrastReader.taggedText, policy = "soft")
        relationExtractor.dropToFile(fname = ProjDir + "/" + ProjName + "/data/Applied_Cleaned_Text")
        for word in relationExtractor.cleanDict:
            item1 = QtGui.QStandardItem(word)
            item2 = QtGui.QStandardItem(relationExtractor.cleanDict[word][0])
            item3 = QtGui.QStandardItem(str(relationExtractor.cleanDict[word][1]))
            self.DictModel.appendRow([item1, item2, item3])
        self.DictView.setModel(self.DictModel)
        parent.close()

if __name__ == "__main__":
    application = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(application.exec_())