##################################
#                                           
#  Byron C. Wallace                   
#  Tufts Medical Center               
#  OpenMeta[analyst]                  
#                                     
#  This form is for 'batch' editing a dataset. Note that any 
#  edits apply to *all* MetaAnalyticUnit objects known. So
#  e.g., if a group name is changed, it will be changed 
# *everywhere*.
#
#  Note also that this form doesn't itself provide any 
#  undo/redo functionality. Rather, the strategy is to
#  treat *all* editing done via this form as one
#  undoable action.
#                                     
##################################


from PyQt4.Qt import *
import ui_edit_dialog
import edit_list_models
import meta_py_r
import add_new_dialogs
import pdb

import ma_dataset
from ma_dataset import *

class EditDialog(QDialog, ui_edit_dialog.Ui_edit_dialog):

    def __init__(self, dataset, parent=None):
        super(EditDialog, self).__init__(parent)
        self.setupUi(self)
        
        ### groups
        self.groups_model = edit_list_models.TXGroupsModel(dataset = dataset)
        self.group_list.setModel(self.groups_model)
        self.selected_group = None
        
        ### outcomes
        self.outcomes_model = edit_list_models.OutcomesModel(dataset = dataset)
        self.outcome_list.setModel(self.outcomes_model)
        self.selected_outcome = None
        
        self._setup_connections()
        self.dataset = dataset
        

    def _setup_connections(self):
        ###
        # groups
        QObject.connect(self.add_group_btn, SIGNAL("pressed()"),
                                    self.add_group)
        QObject.connect(self.remove_group_btn, SIGNAL("pressed()"),
                                    self.remove_group)
        QObject.connect(self.group_list, SIGNAL("clicked(QModelIndex)"),
                                    self.group_selected)
                 
        ###
        # outcomes   
        QObject.connect(self.add_outcome_btn, SIGNAL("pressed()"),
                                    self.add_outcome)
        
        #self.model.add_new_outcome(outcome_name, outcome_type)
                                    
    def add_group(self):
        form = add_new_dialogs.AddNewGroupForm(self)
        form.group_name_le.setFocus()        
        if form.exec_():
            new_group_name = unicode(form.group_name_le.text().toUtf8(), "utf-8")
            self.group_list.model().dataset.add_group(new_group_name)
            self.group_list.model().refresh_group_list()
      
    def add_outcome(self)      :
        form =  add_new_dialogs.AddNewOutcomeForm(self)
        form.outcome_name_le.setFocus()
        if form.exec_():
            # then the user clicked ok and has added a new outcome.
            # here we want to add the outcome to the dataset, and then
            # display it
            new_outcome_name = unicode(form.outcome_name_le.text().toUtf8(), "utf-8")
            # the outcome type is one of the enumerated types; we don't worry about
            # unicode encoding
            data_type = str(form.datatype_cbo_box.currentText())
            data_type = STR_TO_TYPE_DICT[data_type.lower()]
            self.outcome_list.model().dataset.add_outcome(Outcome(new_outcome_name, data_type))
            self.outcome_list.model().refresh_outcome_list()
            #self.dataset.add_outcome(Outcome(new_outcome_name, data_type))
            #print self.dataset.get_outcome_names()
            
            #self.outcome_list.model().reset()
            
            
    def remove_group(self):
        self.group_list.model().dataset.delete_group(self.selected_group)
        self.group_list.model().reset()
        
    def group_selected(self, index):
        self.selected_group = self.group_list.model().group_list[index.row()]
        self.remove_group_btn.setEnabled(True)