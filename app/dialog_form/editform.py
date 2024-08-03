import addform
from internation import HAN_EN

class EditForm(addform.AddForm):

    def __init__(self, info):
        super(EditForm, self).__init__()
        self.setWindowTitle(f"{HAN_EN.get('Edit Node')}: {info.nodeID} {info.nodeName}")
        self.initUIData(info)

    def initUIData(self, info):
        parentID = info.parentID
        nodeName = info.nodeName
        content = info.content
        attribute = info.attribute
        nodeType = info.nodeType
        reason = info.reason
        DSTheory = info.DSTheory
        Addition = info.Addition
        nodeWidth = str(info.nodeWidth)

        self.parentIDEdit.setText(str(parentID))
        self.nodeNameEdit.setText(nodeName)
        self.DSTheoryEdit.setText(DSTheory)
        self.AdditionEdit.setText(Addition)
        self.attrComBox.setCurrentText(attribute)
        self.typeComBox.setCurrentText(nodeType)
        self.reasonComBox.setCurrentText(reason)
        self.nodeWidthEdit.setText(nodeWidth)

        pos = content.find('THEN')
        if pos == -1:
            self.thenEdit.setText(content)
        else:
            self.ifEdit.setText(content[2:pos].strip())
            self.thenEdit.setText(content[pos+4:].strip())
