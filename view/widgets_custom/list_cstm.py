from PySide2.QtWidgets import QListWidget, QListWidgetItem

class listWidget(QListWidget):
    def __init__(self, dict, fixeWidth=None, minWidth=None, maxWidth=None, fixeHeight = None, minHeight=None, maxHeight=None, on_change_callback=None, parent=None):
        super(listWidget, self).__init__(parent)
        self.dict = dict
        self.fixeWidth = fixeWidth
        self.minWidth = minWidth
        self.maxWidth = maxWidth
        self.fixeHeight = fixeHeight
        self.minHeight = minHeight
        self.maxHeight = maxHeight
        self.on_change_callback = on_change_callback
        self.init_ui()

    def init_ui(self):
        if self.fixeWidth is None:
            if self.minWidth:
                self.setMinimumWidth(self.minWidth)
            if self.maxWidth:
                self.setMaximumWidth(self.maxWidth)
        else:
            self.setFixedWidth(self.fixeWidth)
        if self.fixeHeight:
            self.setFixedHeight(self.fixeHeight)
        elif self.minHeight and self.maxHeight:
            self.setMinimumHeight(self.minHeight)
            self.setMaximumHeight(self.maxHeight)   
        else:
            if self.dict != None:
                self.setFixedHeight(len(self.dict) * 20)
            else:
                self.setFixedHeight(100)
        self.update_list()

    def update_list(self):
        print('update')
        if self.dict != None:
            print(666)
            self.setSelectionMode(QListWidget.SingleSelection)  # Permet de ne sélectionner qu'une seule option à la fois
            for spe in self.dict.keys():
                item = QListWidgetItem(spe)
                self.addItem(item)
                print(item)

            if self.on_change_callback:
                self.itemSelectionChanged.connect(self.on_change_callback)