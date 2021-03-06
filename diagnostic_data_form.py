##################################################
#
#  Byron C. Wallace                  
#  George Dietz                      
#  CEBM @ Brown                       
#  OpenMeta[analyst] 
#
#  ---
#  Diagnostic data form module; for flexible entry of diagnostic
#  outcome data.
#
##################################################


import pdb

#from PyQt4.Qt import *
from PyQt4.Qt import (QDialog, QDialogButtonBox, QMessageBox, QObject, QPalette,
                      QString, Qt, QTableWidgetItem, SIGNAL)
#from PyQt4 import QtGui

import meta_py_r
import meta_globals
from meta_globals import (_is_a_float, _is_empty, NUM_DIGITS,
                          DIAGNOSTIC_METRICS, DIAG_FIELDS_TO_RAW_INDICES,EMPTY_VALS)
#import ui_continuous_data_form
from ui_diagnostic_data_form import Ui_DiagnosticDataForm

BACK_CALCULATABLE_DIAGNOSTIC_EFFECTS = ["Sens", "Spec"]

class DiagnosticDataForm(QDialog, Ui_DiagnosticDataForm):
    def __init__(self, ma_unit, cur_txs, cur_group_str, parent=None):
        super(DiagnosticDataForm, self).__init__(parent)
        self.setupUi(self)
        self.setup_signals_and_slots()
        self.ma_unit = ma_unit
        self.raw_data_dict = {}
        for group in cur_txs:
            raw_data = self.ma_unit.get_raw_data_for_group(group)
            self.raw_data_dict[group] = raw_data
        self.cur_groups = cur_txs
        self.group_str = cur_group_str
        self.cur_effect = "Sens" # arbitrary
        
        self.entry_widgets = [self.two_by_two_table, self.prevalence_txt_box,
                              self.low_txt_box, self.high_txt_box,
                              self.effect_txt_box,]
        self.already_showed_change_CI_alert = False
        
        # block all the widgets for a moment
        self.block_all_signals(True)
        
        meta_globals.init_ci_spinbox_and_label(self.CI_spinbox, self.ci_label)
        
        self.setup_inconsistency_checking()
        self.initialize_backup_structures()
        self.setup_clear_button_palettes()
        
        self.setup_table_effect_dict()         # gather effect info from ma_unit
        self._read_in_table_data_from_MAunit() # populate table items from raw data in ma_unit
        self._populate_effect_cmbo_box()     # make cmbo box entries for effects
        self._update_data_table()         # fill in the rest of the data table
        self.set_current_effect()         # fill in current effect data in line edits
        self.enable_back_calculation_btn()
        self.enable_txt_box_input()
        self.save_form_state()

        # unblock
        self.block_all_signals(False)
        
        # Color for clear_button_pallette
        self.orig_palette = self.clear_Btn.palette()
        self.pushme_palette = QPalette()
        self.pushme_palette.setColor(QPalette.ButtonText,Qt.red)
        self.set_clear_btn_color()
        
    def setup_clear_button_palettes(self):
        # Color for clear_button_pallette
        self.orig_palette = self.clear_Btn.palette()
        self.pushme_palette = QPalette()
        self.pushme_palette.setColor(QPalette.ButtonText,Qt.red)
        self.set_clear_btn_color()
        
    def initialize_backup_structures(self):
        # Stores form effect info as text
        self.form_effects_dict = {"Sens":{"est":"","lower":"","upper":""},
                                  "Spec":{"est":"","lower":"","upper":""},
                                  "prevalence":""}
        # Stores table items as text
        self.table_backup = [[None,None,None],[None,None,None],[None,None,None]]
    
    def setup_signals_and_slots(self):
        QObject.connect(self.two_by_two_table, SIGNAL("cellChanged (int, int)"), self.cell_changed)                          
        QObject.connect(self.effect_cbo_box, SIGNAL("currentIndexChanged(QString)"), self.effect_changed) 
        QObject.connect(self.clear_Btn, SIGNAL("clicked()"), self.clear_form)
        
        QObject.connect(self.effect_txt_box, SIGNAL("textEdited(QString)"), lambda new_text : self.val_edit("est", new_text))
        QObject.connect(self.low_txt_box,    SIGNAL("textEdited(QString)"), lambda new_text : self.val_edit("lower", new_text))
        QObject.connect(self.high_txt_box,   SIGNAL("textEdited(QString)"), lambda new_text : self.val_edit("upper", new_text))
        QObject.connect(self.prevalence_txt_box, SIGNAL("textEdited(QString)"), lambda new_text : self.val_edit("prevalence", new_text))
        
        QObject.connect(self.effect_txt_box, SIGNAL("editingFinished()"), lambda: self.val_changed("est")   )
        QObject.connect(self.low_txt_box,    SIGNAL("editingFinished()"), lambda: self.val_changed("lower") )
        QObject.connect(self.high_txt_box,   SIGNAL("editingFinished()"), lambda: self.val_changed("upper") )
        QObject.connect(self.prevalence_txt_box, SIGNAL("editingFinished()"), lambda: self.val_changed("prevalence") )

        QObject.connect(self.back_calc_Btn, SIGNAL("clicked()"), lambda: self.enable_back_calculation_btn(engage=True) )
        QObject.connect(self.CI_spinbox, SIGNAL("valueChanged(double)"), self._change_ci)
        QObject.connect(self, SIGNAL("accepted()"), self.reset_conf_level)
        
    def _change_ci(self,val):
        self.ci_label.setText("{0:.1F} % Confidence Interval".format(val))
        print("New CI val:",val)
        
        self.change_CI_alert(val)
        self.enable_back_calculation_btn()

    def setup_inconsistency_checking(self):
        # set-up inconsistency label
        inconsistency_palette = QPalette()
        inconsistency_palette.setColor(QPalette.WindowText,Qt.red)
        self.inconsistencyLabel.setPalette(inconsistency_palette)
        self.inconsistencyLabel.setVisible(False)
        
        def action_consistent_table():    
            self.inconsistencyLabel.setVisible(False)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        def action_inconsistent_table():
            #show label, disable OK buttonbox button
            self.inconsistencyLabel.setVisible(True)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        
        self.check_table_consistency = meta_globals.ConsistencyChecker(
                            fn_consistent=action_consistent_table,
                            fn_inconsistent=action_inconsistent_table,
                            table_2x2 = self.two_by_two_table)

    def _get_int(self, i, j):
        try:
            if not self._is_empty(i,j):
                int_val = int(float(self.two_by_two_table.item(i, j).text()))
                return int_val
        except:
            # Should never appear....
            msg = "Could not convert %s to integer" % self.two_by_two_table.item(i, j)
            QMessageBox.warning(self.parent(), "whoops", msg)
            raise Exception("Could not convert %s to int" % self.two_by_two_table.item(i, j))
            
    def cell_data_invalid(self, celldata_string):
        # ignore blank entries
        if celldata_string.trimmed() == "" or celldata_string is None:
            return None

        if not meta_globals._is_a_float(celldata_string):
            return "Raw data needs to be numeric."

        if not meta_globals._is_an_int(celldata_string):
            return "Expecting count data -- you provided a float (?)"

        if int(celldata_string) < 0:
            return "Counts cannot be negative."
        return None

    def _is_empty(self, i, j):
        val = self.two_by_two_table.item(i,j)
        return val is None or val.text() == "" or val.text() == None
    def _is_invalid(self, i, j):
        val = self.two_by_two_table.item(i,j)
        try:
            int(val.text())
        except:
            return True
        return False
    
    def _is_txt_box_invalid(self, txt_box):
        val = txt_box.text()
        empty = val in EMPTY_VALS
        return meta_globals.is_NaN(val) or empty or (not _is_a_float(val))
    
    def _set_val(self, row, col, val):
        if meta_globals.is_NaN(val): # get out quick
            print "%s is not a number" % val
            return
        
        try:
            str_val = "" if val in EMPTY_VALS else str(int(val))
            self.two_by_two_table.blockSignals(True)
            if self.two_by_two_table.item(row, col) == None:
                self.two_by_two_table.setItem(row, col, QTableWidgetItem(str_val))
            else:
                self.two_by_two_table.item(row, col).setText(str_val)
            self.two_by_two_table.blockSignals(False)
            
            if str_val != "": #disable item
                self.two_by_two_table.blockSignals(True)
                item = self.two_by_two_table.item(row, col)
                newflags = item.flags() & ~Qt.ItemIsEditable
                item.setFlags(newflags)
                self.two_by_two_table.blockSignals(False)
        except:
            print("Got to except in _set_val when trying to set (%d,%d)" % (row,col)) 
    
    def _set_vals(self, computed_d):
        '''Sets values in table widget'''
        
        self.two_by_two_table.blockSignals(True)
        self._set_val(0, 0, computed_d["c11"])
        self._set_val(0, 1, computed_d["c12"])
        self._set_val(1, 0, computed_d["c21"])
        self._set_val(1, 1, computed_d["c22"])  
        self._set_val(0, 2, computed_d["r1sum"])
        self._set_val(1, 2, computed_d["r2sum"])
        self._set_val(2, 0, computed_d["c1sum"])
        self._set_val(2, 1, computed_d["c2sum"])  
        self._set_val(2, 2, computed_d["total"])  
        self.two_by_two_table.blockSignals(False)

    def cell_changed(self, row, col):
        print "Beginning of cell_changed"
        
        try:
            # Test if entered data is valid (a number)
            warning_msg = self.cell_data_invalid(self.two_by_two_table.item(row, col).text())
            if warning_msg:
                raise Exception("Invalid Cell Data")
    
            self._update_data_table() # calculate rest of table (provisionally) based on new entry
            warning_msg = self.check_table_consistency.run()
            if warning_msg:
                raise Exception("Table no longer consistent.")
        except Exception as e:
            msg = e.args[0]
            QMessageBox.warning(self.parent(), "whoops", msg) #popup warning
            self.restore_form_state() # brings things back to the way they were
            return                    # and leave
        
        # if we got here, everything seems ok
        self.save_form_state()
        self._update_ma_unit()           # 2x2 table --> ma_unit
        self.impute_effects_in_ma_unit() # effects   --> ma_unit
        self.set_current_effect()        # ma_unit   --> effects
        self.enable_back_calculation_btn()
        self.save_form_state()
        
        # disable just-edited cell
        self.block_all_signals(True)
        item = self.two_by_two_table.item(row, col)
        newflags = item.flags() & ~Qt.ItemIsEditable
        item.setFlags(newflags)
        self.block_all_signals(False)
    
        self.enable_txt_box_input() # if the effect was imputed
        self.set_clear_btn_color()
        
    def save_form_state(self):
        ''' Saves the state of all objects on the form '''
        def save_table_data():
            for row in range(3):
                for col in range(3):
                    item = self.two_by_two_table.item(row, col)
                    contents = "" if item is None else item.text()
                    self.table_backup[row][col]=contents
                    
        def save_displayed_effects_data(effect=None):
            print "Saving Displayed Effects data...."
            
            if effect is None:
                effect = self.cur_effect
            
            self.form_effects_dict[effect]["est"]   = self.effect_txt_box.text() 
            self.form_effects_dict[effect]["lower"] = self.low_txt_box.text()    
            self.form_effects_dict[effect]["upper"] = self.high_txt_box.text()    
            self.form_effects_dict["prevalence"] = self.prevalence_txt_box.text() 
        
            self.candidate_est        = self.effect_txt_box.text()
            self.candidate_lower      = self.low_txt_box.text()
            self.candidate_upper      = self.high_txt_box.text()
            self.candidate_prevalence = self.prevalence_txt_box.text()

        save_table_data()
        save_displayed_effects_data()
        self.enable_back_calculation_btn()
    
    def restore_form_state(self):
        ''' Restores the state of all objects on the form '''
        
        # Block all signals on the form 
        self.block_all_signals(True)
        ########################################################################
        
        def restore_displayed_effects_data():
            print "Restoring displayed effects data..."
            
            self.effect_txt_box.setText(    self.form_effects_dict[self.cur_effect]["est"]  )    
            self.low_txt_box.setText(       self.form_effects_dict[self.cur_effect]["lower"])       
            self.high_txt_box.setText(      self.form_effects_dict[self.cur_effect]["upper"])                    
            self.prevalence_txt_box.setText(self.form_effects_dict["prevalence"]            )
            
            self.candidate_est        = self.effect_txt_box.text()
            self.candidate_lower      = self.low_txt_box.text()
            self.candidate_upper      = self.high_txt_box.text()
            self.candidate_prevalence = self.prevalence_txt_box.text()
        
        def restore_table():
            #print "Table to restore:"
            #self.print_backup_table()
        
            for row in range(3):
                for col in range(3):
                    self.two_by_two_table.blockSignals(True)
                    self._set_val(row, col, self.table_backup[row][col])
                    self.two_by_two_table.blockSignals(False)
            self.check_table_consistency.run()
            
            #print("Backed-up table:")
            #self.print_backup_table()
        
        self.CI_spinbox.setValue(meta_py_r.get_global_conf_level())
        restore_displayed_effects_data()
        restore_table()
        self.enable_back_calculation_btn()
        
        
        ########################################################################
        # Unblock the signals
        self.block_all_signals(False)
                    
    
    def getTotalSubjects(self):
        try:
            return int(self.table_backup[2][2])
        except:
            return None

    def print_backup_table(self):
        for row in range(3):
            line = ""
            for col in range(3):
                line += self.table_backup[row][col] + ", "
            print line
    
    def _get_table_vals(self):
        ''' Package table from 2x2 table in to a dictionary'''
        
        vals_d = {}
        vals_d["c11"] = self._get_int(0, 0)
        vals_d["c12"] = self._get_int(0, 1)
        vals_d["c21"] = self._get_int(1, 0)
        vals_d["c22"] = self._get_int(1, 1)
        vals_d["r1sum"] = self._get_int(0, 2)
        vals_d["r2sum"] = self._get_int(1, 2)
        vals_d["c1sum"] = self._get_int(2, 0)
        vals_d["c2sum"] = self._get_int(2, 1)
        vals_d["total"] = self._get_int(2, 2)
        return vals_d
            
    def impute_effects_in_ma_unit(self):
        '''Calculate and store values for effects in ma_unit based on values in 2x2 table'''
        
        # diagnostic data
        counts = self.get_raw_diag_data()
        tp, fn, fp, tn = counts['TP'], counts['FN'], counts['FP'], counts['TN']
        
        # Do what we can if we don't have all the counts
        can_calculate_sens, can_calculate_spec = True, True
        if None in [tp,fn]:
            can_calculate_sens = False
            tp,fn = 0,0 # dummy data
        if None in [tn,fp]:
            can_calculate_spec = False
            tn, fp = 0,0 # dummy data
        
        # sensitivity and specificity
        ests_and_cis = meta_py_r.diagnostic_effects_for_study(
                                tp, fn, fp, tn, metrics=DIAGNOSTIC_METRICS,
                                conf_level=self.CI_spinbox.value())
        
        # now we're going to set the effect estimate/CI on the MA object.
        for metric in DIAGNOSTIC_METRICS:
            # don't set stuff if it made-up
            if metric.lower()=="sens" and not can_calculate_sens:
                continue
            elif metric.lower()=="spec" and not can_calculate_spec:
                continue
            
            est, lower, upper = ests_and_cis[metric]["calc_scale"]
            self.ma_unit.set_effect_and_ci(metric, self.group_str, est, lower, upper)
            disp_est, disp_lower, disp_upper = ests_and_cis[metric]["display_scale"]
            self.ma_unit.set_display_effect_and_ci(metric, self.group_str, disp_est, disp_lower, disp_upper)

    def _get_row_col(self, field):
        row = 0 if field in ("FP", "TP") else 1
        col = 1 if field in ("FP", "TN") else 0
        return (row, col)

    def update_2x2_table(self, imputed_dict):
        ''' Fill in entries in 2x2 table and add data to ma_unit'''
        
        print "Updating 2x2......"
        
        # reset relevant column and sums column if we have new data
        if imputed_dict["TP"] and imputed_dict["FN"]:
            print("TP, FN:", imputed_dict["TP"],imputed_dict["FN"])
            print "clearing col 0 and 2"
            self.clear_column(0)
            self.clear_column(2)
        if imputed_dict["TN"] and imputed_dict["FP"]:
            print "clearing col 1 and 2"
            self.clear_column(1)
            self.clear_column(2)
        
        for field in ["FP", "TP", "TN", "FN"]:
            if (field in imputed_dict) and (not imputed_dict[field] is None):
                row, col = self._get_row_col(field)
                self._set_val(row, col, imputed_dict[field])
                # here we update the MA unit
                raw_data_index = DIAG_FIELDS_TO_RAW_INDICES[field]
                
                # TODO: ENC
                self.ma_unit.tx_groups[self.group_str].raw_data[raw_data_index] =\
                    None if not _is_a_float(imputed_dict[field]) else float(imputed_dict[field])
    
    def _update_ma_unit(self):
        '''Copy data from data table to the MA_unit'''
        
        print "updating ma unit...."
        raw_dict = self.get_raw_diag_data() # values are floats or None
        for field in raw_dict.iterkeys():
            i = DIAG_FIELDS_TO_RAW_INDICES[field]
            self.ma_unit.tx_groups[self.group_str].raw_data[i] = raw_dict[field]  # TODO: ENC
    
    def get_raw_diag_data(self,convert_None_to_NA_string=False):
        '''Returns a dictionary of the raw data in the table (TP,FN,FP,TN), 
           None for empty cell'''
        
        NoneValue = "NA" if convert_None_to_NA_string else None
        
        d={}
        d["TP"] = float(self._get_int(0,0)) if not self._is_empty(0,0) else NoneValue
        d["FN"] = float(self._get_int(1,0)) if not self._is_empty(1,0) else NoneValue
        d["FP"] = float(self._get_int(0,1)) if not self._is_empty(0,1) else NoneValue
        d["TN"] = float(self._get_int(1,1)) if not self._is_empty(1,1) else NoneValue
        return d

    def block_all_signals(self,state):
        for widget in self.entry_widgets:
            widget.blockSignals(state)

    def val_changed(self, val_str):
        print "--------------\nEntering val_changed...."
        
        def is_between_bounds(est=self.form_effects_dict[self.cur_effect]["est"], 
                              low=self.form_effects_dict[self.cur_effect]["lower"], 
                              high=self.form_effects_dict[self.cur_effect]["upper"]):
            return meta_globals.between_bounds(est=est, low=low, high=high)

        ###### ERROR CHECKING CODE#####
        # Make sure entered value is numeric and between the appropriate bounds
        self.block_all_signals(True)
        float_msg = "Must be numeric!"
        try:
            if val_str == "est" and not _is_empty(self.candidate_est):
                # Check type
                if not _is_a_float(self.candidate_est) :
                    QMessageBox.warning(self, "whoops", float_msg)
                    raise Exception("error")
                (good_result,msg) = is_between_bounds(est=self.candidate_est)
                if not good_result:
                    QMessageBox.warning(self, "whoops", msg)
                    raise Exception("error")
                if (not 0 <= float(self.candidate_est) <= 1):
                    QMessageBox.warning(self, "whoops", "Estimate must be between 0 and 1.")
                    raise Exception("error")
                display_scale_val = float(self.candidate_est)
            elif val_str == "lower" and not _is_empty(self.candidate_lower):
                if not _is_a_float(self.candidate_lower) :
                    QMessageBox.warning(self, "whoops", float_msg)
                    raise Exception("error")
                (good_result,msg) = is_between_bounds(low=self.candidate_lower)
                if not good_result:
                    QMessageBox.warning(self, "whoops", msg)
                    raise Exception("error")
                display_scale_val = float(self.candidate_lower)
            elif val_str == "upper" and not _is_empty(self.candidate_upper): 
                if not _is_a_float(self.candidate_upper) :
                    QMessageBox.warning(self, "whoops", float_msg)
                    raise Exception("error")
                (good_result,msg) = is_between_bounds(high=self.candidate_upper)
                if not good_result:
                    QMessageBox.warning(self, "whoops", msg)
                    raise Exception("error")
                display_scale_val = float(self.candidate_upper)
            elif val_str == "prevalence" and not _is_empty(self.candidate_prevalence):
                if not _is_a_float(self.candidate_prevalence):
                    QMessageBox.warning(self, "whoops", float_msg)
                    raise Exception("error")
                if _is_a_float(self.candidate_prevalence) and not 0 < float(self.candidate_prevalence) < 1:
                    QMessageBox.warning(self, "whoops", "Prevalence must be between 0 and 1.")
                    raise Exception("error")
        except:
            print "Error flag is true"
            self.restore_form_state()
            self.block_all_signals(True)
            if val_str == "est":
                self.effect_txt_box.setFocus()
            elif val_str == "lower":
                self.low_txt_box.setFocus()
            elif val_str == "upper":
                self.high_txt_box.setFocus()
            elif val_str == "prevalence":
                self.prevalence_txt_box.setFocus()
            self.block_all_signals(False)
            return
                
        self.block_all_signals(False)
        
        # If we got to this point it means everything is ok so far
        #######self._save_displayed_effects_data()
        
        try:
            display_scale_val = float(display_scale_val)
        except:
            # a number wasn't entered; ignore
            # should probably clear out the box here, too.
            print "fail."
            return None
            
        calc_scale_val = meta_py_r.binary_convert_scale(display_scale_val, \
                                        self.cur_effect, convert_to="calc.scale")
        
        if val_str == "est":
            self.ma_unit.set_effect(self.cur_effect, self.group_str, calc_scale_val)
            self.ma_unit.set_display_effect(self.cur_effect, self.group_str, display_scale_val)
        elif val_str == "lower":
            self.ma_unit.set_lower(self.cur_effect, self.group_str, calc_scale_val)
            self.ma_unit.set_display_lower(self.cur_effect, self.group_str, display_scale_val)
        elif val_str == "upper":
            self.ma_unit.set_upper(self.cur_effect, self.group_str, calc_scale_val)
            self.ma_unit.set_display_upper(self.cur_effect, self.group_str, display_scale_val)
        elif val_str == "prevalence":
            pass

        self.enable_txt_box_input()
        self.save_form_state()
        self.enable_back_calculation_btn()
        
    def val_edit(self, val_str, display_scale_val):
        print "Editing %s with value: %s" % (val_str,display_scale_val)
        if val_str == "est":
            self.candidate_est = display_scale_val
        if val_str == "lower":
            self.candidate_lower = display_scale_val
        if val_str == "upper":
            self.candidate_upper = display_scale_val
        if val_str == "prevalence":
            self.candidate_prevalence = display_scale_val

    def effect_changed(self):
        # Re-scale previous effect first
        self.reset_conf_level()
        
        self.cur_effect = str(self.effect_cbo_box.currentText()) 
        self.set_current_effect()
        
        self.enable_txt_box_input()
        self.enable_back_calculation_btn()
            
    def _read_in_table_data_from_MAunit(self):
        ''' populates the 2x2 table with whatever parametric data was provided '''
        self.two_by_two_table.blockSignals(True) 
        field_index = 0
        for col in (0,1):
            for row in (0,1):
                val = self.raw_data_dict[self.group_str][field_index]
                if val is not None:
                    try:
                        val = str(int(val))
                    except:
                        val = str(val)
                    item = QTableWidgetItem(val)
                    self.two_by_two_table.setItem(row, col, item)
                field_index+=1
        self.two_by_two_table.blockSignals(False)

    def _populate_effect_cmbo_box(self):
        # for now we only back-calculate from sens/spec
        effects = BACK_CALCULATABLE_DIAGNOSTIC_EFFECTS # TODO add more metrics
        self.effect_cbo_box.blockSignals(True)
        self.effect_cbo_box.addItems(effects)
        self.effect_cbo_box.blockSignals(False)
        self.effect_cbo_box.setCurrentIndex(0)
    
    def set_current_effect(self):
        '''Fill in effect text boxes with data from ma_unit'''
        effect_dict = self.ma_unit.effects_dict[self.cur_effect][self.group_str]
        for s, txt_box in zip(['display_est', 'display_lower', 'display_upper'],
                              [self.effect_txt_box, self.low_txt_box, self.high_txt_box]):
            txt_box.blockSignals(True)
            if effect_dict[s] is not None:
                txt_box.setText(QString("%s" % round(effect_dict[s], NUM_DIGITS)))
                print("From set_current effect: %s=%s" %(s, round(effect_dict[s], NUM_DIGITS)))
            else:
                txt_box.setText(QString(""))
            txt_box.blockSignals(False)
    
    def print_effects_dict_from_ma_unit(self):
        print self.ma_unit.get_effects_dict()
            
    def setup_table_effect_dict(self):
        '''Fill in local copy of table-effects dict w/ data from ma_unit'''
        
        print "effects dict from ma unit:"
        self.print_effects_dict_from_ma_unit() 
        
        for effect in BACK_CALCULATABLE_DIAGNOSTIC_EFFECTS:
            effects_dict = self.ma_unit.effects_dict[effect][self.group_str]
            for keyA,keyB in zip(['display_est', 'display_lower', 'display_upper'],["est","lower","upper"]):
                self.form_effects_dict[effect][keyB] = str(effects_dict[keyA])
                
        print "Form effects dict:",self.form_effects_dict

    def _update_data_table(self):
        '''Try to calculate rest of 2x2 table from existing cells'''
        
        self.block_all_signals(True)
        
        params = self._get_table_vals()
        computed_params = meta_globals.compute_2x2_table(params)
        print "Computed Params", computed_params
        if computed_params:
            self._set_vals(computed_params) # computed --> table widget
        
        # Compute prevalence if possible
        if (not computed_params['c1sum'] in EMPTY_VALS) and (not computed_params['total'] in EMPTY_VALS):
            prevalence = float(computed_params['c1sum'])/float(computed_params['total'])
            prev_str = str(prevalence)[:7]
            self.prevalence_txt_box.setText("%s" % prev_str)
            self.enable_txt_box_input()
        
        self.block_all_signals(False)
        
    def clear_column(self,col):
        '''Clears out column in table and ma_unit'''
        
        print("Clearing column %d" % col)
        for row in range(3):
            self._set_val(row, col, None)  
        
        self._update_ma_unit()
        self.save_form_state()
        
    def clear_form(self):
        keys = ["c11", "c12", "r1sum", "c21", "c22", "r2sum", "c1sum", "c2sum", "total"]
        blank_vals = dict( zip(keys, [""]*len(keys)) )

        self._set_vals(blank_vals)
        self._update_ma_unit()
        
        # clear out effects stuff
        for metric in DIAGNOSTIC_METRICS:
            self.ma_unit.set_effect_and_ci(metric, self.group_str, None, None, None)
            self.ma_unit.set_display_effect_and_ci(metric, self.group_str, None, None, None)
            
        # clear line edits
        self.set_current_effect()
        self.prevalence_txt_box.blockSignals(True)
        self.prevalence_txt_box.setText("")
        self.prevalence_txt_box.blockSignals(False)
        
        self.save_form_state()
       
        # reset form_effects_dict (backup)
        self.form_effects_dict = {"Sens":{"est":"","lower":"","upper":"",},
                                  "Spec":{"est":"","lower":"","upper":"",},
                                  "prevalence":""}

        self.reset_table_item_flags()
        self.enable_txt_box_input()
        self.CI_spinbox.setValue(meta_py_r.get_global_conf_level())
        self.CI_spinbox.setEnabled(True)
        
    def enable_txt_box_input(self):
        ''' Enables text boxes if they are empty, disables them otherwise '''
        
        #meta_globals.enable_txt_box_input(self.effect_txt_box, self.low_txt_box,
        #                                  self.high_txt_box, self.prevalence_txt_box)
        pass
           
    def reset_table_item_flags(self):
        self.block_all_signals(True)
        for row in range(3):
            for col in range(3):
                item = self.two_by_two_table.item(row, col)
                if not item is None:
                    newflags = item.flags() | Qt.ItemIsEditable
                    item.setFlags(newflags)
        self.block_all_signals(False)
    
    def input_fields_disabled(self):
        table_disabled = True
        for row in range(3):
            for col in range(3):
                item = self.two_by_two_table.item(row, col)
                if item is None:
                    continue
                if (item.flags() & Qt.ItemIsEditable) == Qt.ItemIsEditable:
                    table_disabled = False
                    
        txt_boxes_disabled = self._txt_boxes_disabled()

        if table_disabled and txt_boxes_disabled:
            self.CI_spinbox.setEnabled(False) # weird place for ?this? but whatever
            return True
        return False
    
    
    def _txt_boxes_disabled(self):
        return not (self.effect_txt_box.isEnabled() or
                    self.low_txt_box.isEnabled() or
                    self.high_txt_box.isEnabled() or
                    self.prevalence_txt_box.isEnabled())
    
    def set_clear_btn_color(self):
        if self.input_fields_disabled():
            self.clear_Btn.setPalette(self.pushme_palette)
        else:
            self.clear_Btn.setPalette(self.orig_palette)
            
    def enable_back_calculation_btn(self, engage = False):
        print("Enabling back-calculation button...")
        
        def build_dict():
            d = {}

            for effect in BACK_CALCULATABLE_DIAGNOSTIC_EFFECTS:
                for key,Rsubkey in zip(["est","lower","upper"],["",".lb",".ub"]):
                    try:
                        d["%s%s" % (effect.lower(), Rsubkey)] = float(self.form_effects_dict[effect][key])
                    except:
                        pass
            
            x = self.getTotalSubjects()
            d["total"] = float(x) if _is_a_float(x) else None

            x = self.prevalence_txt_box.text()
            d["prev"] = float(x) if _is_a_float(x) else None

            x = self.CI_spinbox.value()
            d["conf.level"] = x if _is_a_float(x) else None
    
            # now grab the raw data, if available
            d.update(self.get_raw_diag_data())
            
            return d
        
        def new_data(diag_data, imputed):
            new_data = (imputed["TP"],
                        imputed["FP"],
                        imputed["FN"],
                        imputed["TN"])
            old_data = (self._get_int(0,0),
                        self._get_int(0,1),
                        self._get_int(1,0),
                        self._get_int(1,1),
                        )
            isBlank = lambda x: x in meta_globals.EMPTY_VALS
            new_item_available = lambda old, new: isBlank(old) and not isBlank(new)
            comparison = [new_item_available(old_data[i], new_data[i]) for i in range(len(new_data))]
            print("Comparison:", comparison)
            if any(comparison):
                changed = True
            else:
                changed = False
            return changed
            
        diag_data = build_dict()
        print("Diagnostic Data for back-calculation: ", diag_data)

        #if diag_data is not None:
            
        imputed = meta_py_r.impute_diag_data(diag_data)
        print "imputed data: %s" % imputed
        
        # Leave if nothing was imputed
        if not (imputed["TP"] or imputed["TN"] or imputed["FP"] or imputed["FN"]):
            print("Nothing could be imputed")
            self.back_calc_Btn.setEnabled(False)
            return None
    
        if new_data(diag_data, imputed):
            self.back_calc_Btn.setEnabled(True)
        else:
            self.back_calc_Btn.setEnabled(False)
        self.set_clear_btn_color()
            
        if not engage:
            return None
        ########################################################################
        # Actually do stuff with imputed data here if we are 'engaged'
        ########################################################################
        self.update_2x2_table(imputed)
        self._update_data_table()
        self.save_form_state()
        
        self.set_clear_btn_color()

        # Go backward in case we have a missing effect
        #self.impute_effects_in_ma_unit() 
        #self.set_current_effect()
        #self.save_form_state()

    def change_CI_alert(self,value=None):
        if not self.already_showed_change_CI_alert:
            QMessageBox.information(self, "Changing Confidence Level", meta_globals.get_CHANGE_CI_ALERT_MSG())
            self.already_showed_change_CI_alert = True
    
    # TODO: should be refactored to shared function in meta_globals
    def reset_conf_level(self):
        print("Re-scaling est, low, high to standard confidence level")
        
        old_effect_and_ci = self.ma_unit.get_effect_and_ci(self.cur_effect, self.group_str)
        
        argument_d = {"est"  : old_effect_and_ci[0],
                      "low"  : old_effect_and_ci[1],
                      "high" : old_effect_and_ci[2],
                      "orig.conf.level": self.CI_spinbox.value(),
                      "target.conf.level": meta_py_r.get_global_conf_level()}
        
        res = meta_py_r.rescale_effect_and_ci_conf_level(argument_d)
        if "FAIL" in res:
            print("Could not reset confidence level")
            return
        
        res["display_est"]  = meta_py_r.diagnostic_convert_scale(res["est"], self.cur_effect, convert_to="display.scale")
        res["display_low"]  = meta_py_r.diagnostic_convert_scale(res["low"], self.cur_effect, convert_to="display.scale")
        res["display_high"] = meta_py_r.diagnostic_convert_scale(res["high"], self.cur_effect, convert_to="display.scale")
        
        # Save results in ma_unit
        self.ma_unit.set_effect_and_ci(self.cur_effect, self.group_str, res["est"],res["low"],res["high"])
        self.ma_unit.set_display_effect_and_ci(self.cur_effect, self.group_str, res["display_est"],res["display_low"],res["display_high"])