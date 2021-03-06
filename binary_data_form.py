######################################
#                                    #
#  Byron C. Wallace                  #
#  George Dietz                      #     
#  CEBM @ Brown                      #     
#  OpenMeta[analyst]                 ########################## 
#  ---                                                        #
#  Binary data form module; for flexible entry of dichotomous #
#  outcome data                                               #
###############################################################

#import pdb

# from PyQt4.Qt import *
from PyQt4.Qt import (pyqtSignature, QDialog, QDialogButtonBox, QMessageBox,
                      QObject, QPalette, QString, Qt, QTableWidgetItem, SIGNAL,
                      pyqtRemoveInputHook, QColor, QBrush)
# from PyQt4.QtGui import *

import meta_py_r
import meta_globals
from meta_globals import (BINARY_ONE_ARM_METRICS, BINARY_TWO_ARM_METRICS,
                          _is_a_float, _is_empty, EMPTY_VALS)

import ui_binary_data_form
import ui_choose_back_calc_result_form
# from ui_binary_data_form import Ui_BinaryDataForm

# @TODO this should be an *application global*. It is now a
# global here and in the data_table_view class. (However
# here we show four digits; there it is 3. We want different
# levels of granularity).
NUM_DIGITS = 4 

# this is the maximum size of a residual that we're willing to accept
# when computing 2x2 data
THRESHOLD = 1e-5

class BinaryDataForm2(QDialog, ui_binary_data_form.Ui_BinaryDataForm):
    def __init__(self, ma_unit, cur_txs, cur_group_str, cur_effect, parent=None):
        super(BinaryDataForm2, self).__init__(parent)
        self.setupUi(self)
        self._setup_signals_and_slots()
        self.ma_unit = ma_unit
        self.raw_data_d = {}
        for group in cur_txs:
            raw_data = self.ma_unit.get_raw_data_for_group(group)
            self.raw_data_d[group] = raw_data
        self.cur_groups = cur_txs
        print("CUR TXS: ",cur_txs)
        self.group_str = cur_group_str
        self.cur_effect = cur_effect
        self.entry_widgets = [self.raw_data_table, self.low_txt_box,
                              self.high_txt_box, self.effect_txt_box]
        self.already_showed_change_CI_alert = False
        
        meta_globals.init_ci_spinbox_and_label(self.CI_spinbox, self.ci_label)
        
        self.initialize_table_items() # initialize all cell to empty items
        self.setup_inconsistency_checking()
        self.initialize_backup_structures()
        
        # Color for clear_button_pallette
        self.setup_clear_button_palettes()
        
        self._update_raw_data()  # ma_unit --> table
        self._populate_effect_data()  # make combo boxes for effects
        self.set_current_effect()  # fill in current effect data in line edits
        self._update_data_table()  # fill in 2x2
        self.enable_back_calculation_btn()
        self.save_form_state()
        
    def initialize_table_items(self):
        ''' Initialize all cells to empty items '''
        print("Entering initialize_table_items")
        for row in range(3):
            for col in range(3):
                self._set_val(row, col, None)

    def setup_clear_button_palettes(self):
        # Color for clear_button_pallette
        self.orig_palette = self.clear_Btn.palette()
        self.pushme_palette = QPalette()
        self.pushme_palette.setColor(QPalette.ButtonText, Qt.red)
        self.set_clear_btn_color()
    
    def set_clear_btn_color(self):
        if self.input_fields_disabled():
            self.clear_Btn.setPalette(self.pushme_palette)
        else:
            self.clear_Btn.setPalette(self.orig_palette)
    
    def input_fields_disabled(self):
        table_disabled = True
        for row in range(3):
            for col in range(3):
                item = self.raw_data_table.item(row, col)
                if item is None:
                    continue
                if (item.flags() & Qt.ItemIsEditable) == Qt.ItemIsEditable:
                    table_disabled = False
                    
        txt_boxes_disabled = self._txt_boxes_disabled()

        if table_disabled and txt_boxes_disabled:
            self.CI_spinbox.setEnabled(False)  # weird place for ?this? but whatever
            return True
        return False

    def _txt_boxes_disabled(self):
        return not (self.effect_txt_box.isEnabled() or
                    self.low_txt_box.isEnabled() or
                    self.high_txt_box.isEnabled())
        
    def print_effects_dict_from_ma_unit(self):
        print self.ma_unit.get_effects_dict()
    
    def enable_back_calculation_btn(self, engage=False):
        print("Enabling back-calculation button...")

        def build_back_calc_args_dict():
            
            effect = self.cur_effect
            d = {}
            
            d["metric"] = str(effect)
            
            for key, R_key in zip(["est", "lower", "upper"], ["estimate", "lower", "upper"]):
                try:
                    d["%s" % R_key] = float(self.form_effects_dict[effect][key])
                except:
                    d["%s" % R_key] = None
            
            x = self.CI_spinbox.value()
            d["conf.level"] = x if _is_a_float(x) else None
            
            d["Ev_A"] = float(self._get_int(0, 0)) if not self._is_empty(0, 0) else None
            d["N_A"] = float(self._get_int(0, 2)) if not self._is_empty(0, 2) else None
            d["Ev_B"] = float(self._get_int(1, 0)) if not self._is_empty(1, 0) else None
            d["N_B"] = float(self._get_int(1, 2)) if not self._is_empty(1, 2) else None
            
            return d
        def new_data(bin_data, imputed):
            changed = False
            old_data = (bin_data["Ev_A"],
                        bin_data["N_A"],
                        bin_data["Ev_B"],
                        bin_data["N_B"])
            new_data = []
            new_data.append((int(round(imputed["op1"]["a"])),
                             int(round(imputed["op1"]["b"])),
                             int(round(imputed["op1"]["c"])),
                             int(round(imputed["op1"]["d"])),
                             ))
            if "op2" in imputed:
                new_data.append((int(round(imputed["op2"]["a"])),
                                 int(round(imputed["op2"]["b"])),
                                 int(round(imputed["op2"]["c"])),
                                 int(round(imputed["op2"]["d"])),
                                 ))
            def new_item_available(old,new):
                isBlank = lambda x: x in meta_globals.EMPTY_VALS
                no_longer_blank = isBlank(old) and not isBlank(new)
                return no_longer_blank
                #if (old is not None) and (new is not None):
                #    return old != new
            comparison0 = [new_item_available(old_data[i], new_data[0][i]) for i in range(len(old_data))]
            new_data_in_op1 = any(comparison0)
            print("Comparison0:", comparison0)

            if new_data_in_op1:
                changed = True
                if "op2" in imputed:
                    comparison1 = [new_item_available(old_data[i], new_data[1][i]) for i in range(len(old_data))]
                    print("Comparison1:", comparison1)
                    new_data_in_op2 = any(comparison1)
                    if not new_data_in_op2:
                        changed = False
            else:
                changed = False
                
            return changed
        ### end of new_data() definition ####
            
        # Makes no sense to show the button on a form where the back calculation is not implemented
        if not self.cur_effect in ["OR", "RR", "RD"]:
            self.back_calc_btn.setVisible(False)
            return None
        else:
            self.back_calc_btn.setVisible(True)
            
        bin_data = build_back_calc_args_dict()
        print("Binary data for back-calculation:", bin_data)
        
        imputed = meta_py_r.impute_bin_data(bin_data.copy())
        print("Imputed data: %s", imputed)
        
        # Leave if nothing was imputed
        if "FAIL" in imputed:
            print("Fail to impute")
            self.back_calc_btn.setEnabled(False)
            return None
        
        if new_data(bin_data, imputed):
            self.back_calc_btn.setEnabled(True)
        else:
            self.back_calc_btn.setEnabled(False)
        
        self.set_clear_btn_color()
        
        if not engage:
            return None
        ########################################################################
        # Actually do stuff with imputed data here if we are 'engaged'
        ########################################################################
        for x in range(3):
            self.clear_column(x)  # clear out the table

        if len(imputed.keys()) > 1:
            dialog = ChooseBackCalcResultForm(imputed, parent=self)
            if dialog.exec_():
                choice = dialog.getChoice()
            else:  # don't do anything if cancelled
                return None
        else:  # only one option
            choice = "op1"
            
            
        # set values in table & save in ma_unit
        self.raw_data_table.blockSignals(True)
        self._set_val(0, 0, int(round(imputed[choice]["a"])))
        self._set_val(0, 2, int(round(imputed[choice]["b"])))  
        self._set_val(1, 0, int(round(imputed[choice]["c"]))) 
        self._set_val(1, 2, int(round(imputed[choice]["d"]))) 
        self.raw_data_table.blockSignals(False)
        
        self._update_data_table()
        self._update_ma_unit()  # save in ma_unit
        self.save_form_state()
        
        self.set_clear_btn_color()

    def setup_inconsistency_checking(self):
        # set-up inconsistency label
        inconsistency_palette = QPalette()
        inconsistency_palette.setColor(QPalette.WindowText, Qt.red)
        self.inconsistencyLabel.setPalette(inconsistency_palette)
        self.inconsistencyLabel.setVisible(False)
        
        def action_consistent_table():    
            self.inconsistencyLabel.setVisible(False)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        def action_inconsistent_table():
            # show label, disable OK buttonbox button
            self.inconsistencyLabel.setVisible(True)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        
        self.check_table_consistency = meta_globals.ConsistencyChecker(
                            fn_consistent=action_consistent_table,
                            fn_inconsistent=action_inconsistent_table,
                            table_2x2=self.raw_data_table)

    def initialize_backup_structures(self):
        # Stores form effect info as text
        self.form_effects_dict = {}
        # self.form_effects_dict["alpha"] = ""
        for effect in self.get_effect_names():
            self.form_effects_dict[effect] = {"est":"", "lower":"", "upper":""}
        
        # Stores table items as text
        self.table_backup = [[None, None, None], [None, None, None], [None, None, None]]
    
    @pyqtSignature("int, int, int, int")
    def on_raw_data_table_currentCellChanged(self, currentRow, currentColumn, previousRow, previousColumn):
        self.current_item_data = self._get_int(currentRow, currentColumn)
        print "Current Item Data:", self.current_item_data
        
    def _setup_signals_and_slots(self):
        QObject.connect(self.raw_data_table, SIGNAL("cellChanged (int, int)"), self.cell_changed)
        QObject.connect(self.effect_cbo_box, SIGNAL("currentIndexChanged(QString)"), self.effect_changed)
        QObject.connect(self.clear_Btn, SIGNAL("clicked()"), self.clear_form)
        
        QObject.connect(self.effect_txt_box, SIGNAL("textEdited(QString)"), lambda new_text : self.val_edit("est", new_text))
        QObject.connect(self.low_txt_box, SIGNAL("textEdited(QString)"), lambda new_text : self.val_edit("lower", new_text))
        QObject.connect(self.high_txt_box, SIGNAL("textEdited(QString)"), lambda new_text : self.val_edit("upper", new_text))
        
        QObject.connect(self.effect_txt_box, SIGNAL("editingFinished()"), lambda: self.val_changed("est"))
        QObject.connect(self.low_txt_box, SIGNAL("editingFinished()"), lambda: self.val_changed("lower"))
        QObject.connect(self.high_txt_box, SIGNAL("editingFinished()"), lambda: self.val_changed("upper"))
        
        QObject.connect(self.back_calc_btn, SIGNAL("clicked()"), lambda: self.enable_back_calculation_btn(engage=True))
        QObject.connect(self.CI_spinbox, SIGNAL("valueChanged(double)"), self._change_ci)
        
        QObject.connect(self, SIGNAL("accepted()"), self.reset_conf_level)
    
    def _change_ci(self, val):
        self.ci_label.setText("{0:.1F} % Confidence Interval".format(val))
        print("New CI val:", val)
        
        self.change_CI_alert(val)
        self.enable_back_calculation_btn()
                                                                                              
    def _populate_effect_data(self):
        q_effects = sorted([QString(effect_str) for effect_str in self.ma_unit.effects_dict.keys()])
        self.effect_cbo_box.blockSignals(True)
        self.effect_cbo_box.addItems(q_effects)
        self.effect_cbo_box.blockSignals(False)
        self.effect_cbo_box.setCurrentIndex(q_effects.index(QString(self.cur_effect)))
        
    def get_effect_names(self):
        return self.ma_unit.get_effect_names()
    
    def set_current_effect(self):
        '''Fills in text boxes with data from ma unit'''
        
        print("Entering set_current_effect")
        
        # Fill in text boxes with data from ma unit
        self.block_all_signals(True)
        effect_dict = self.ma_unit.get_effect_dict(self.cur_effect, self.group_str)
        for s, txt_box in zip(['display_est', 'display_lower', 'display_upper'], \
                              [self.effect_txt_box, self.low_txt_box, self.high_txt_box]):
            if effect_dict[s] is not None:
                txt_box.setText(QString("%s" % round(effect_dict[s], NUM_DIGITS)))
            else:
                txt_box.setText(QString(""))
        self.block_all_signals(False)
        
        self.change_row_color_according_to_metric()
        
    def change_row_color_according_to_metric(self):
        # Change color of bottom rows of table according one or two-arm metric
        curr_effect_is_one_arm = self.cur_effect in BINARY_ONE_ARM_METRICS
        #ungreyed_brush = self.raw_data_table.item(0,0).background()
        for row in (1,2):
            for col in range(3):
                item = self.raw_data_table.item(row, col)
                if curr_effect_is_one_arm:
                    item.setBackground(QBrush(QColor(Qt.gray)))
                else:
                    # just reset the item
                    text = item.text()
                    self.raw_data_table.blockSignals(True)
                    popped_item = self.raw_data_table.takeItem(row, col)
                    self.raw_data_table.blockSignals(False)
                    del popped_item
                    self._set_val(row, col, text)
 
    def effect_changed(self):
        '''Called when a new effect is selected in the combo box'''
        
        # Re-scale previous effect first
        self.reset_conf_level()
        
        self.cur_effect = unicode(self.effect_cbo_box.currentText().toUtf8(), "utf-8")
        self.group_str = self.get_cur_group_str()
        
        self.try_to_update_cur_outcome()
        self.set_current_effect()
        
        self.enable_txt_box_input()
        self.enable_back_calculation_btn()
        
    def save_form_state(self):
        ''' Saves the state of all objects on the form '''
        
        print("Saving form state...")
        
        def save_table_data():
            for row in range(3):
                for col in range(3):
                    item = self.raw_data_table.item(row, col)
                    contents = "" if item is None else item.text()
                    self.table_backup[row][col] = contents
                    
        def save_displayed_effects_data(effect=None):
            print "Saving Displayed Effects data...."
            
            if effect is None:
                effect = self.cur_effect
            
            self.form_effects_dict[effect]["est"] = self.effect_txt_box.text() 
            self.form_effects_dict[effect]["lower"] = self.low_txt_box.text()    
            self.form_effects_dict[effect]["upper"] = self.high_txt_box.text()    
        
            self.candidate_est = self.effect_txt_box.text()
            self.candidate_lower = self.low_txt_box.text()
            self.candidate_upper = self.high_txt_box.text()

        save_table_data()
        save_displayed_effects_data()
        self.enable_back_calculation_btn()
    
    def block_all_signals(self, state):
        for widget in self.entry_widgets:
            widget.blockSignals(state)
        
    def restore_form_state(self):
        ''' Restores the state of all objects on the form '''
        
        # Block all signals on the form 
        self.block_all_signals(True)
        ########################################################################
        
        def restore_displayed_effects_data():
            print "Restoring displayed effects data..."
            
            self.effect_txt_box.setText(self.form_effects_dict[self.cur_effect]["est"])    
            self.low_txt_box.setText(self.form_effects_dict[self.cur_effect]["lower"])       
            self.high_txt_box.setText(self.form_effects_dict[self.cur_effect]["upper"])                     
            
            self.candidate_est = self.effect_txt_box.text()
            self.candidate_lower = self.low_txt_box.text()
            self.candidate_upper = self.high_txt_box.text()
        
        def restore_table():
            # print "Table to restore:"
            # self.print_backup_table()
        
            for row in range(3):
                for col in range(3):
                    self.raw_data_table.blockSignals(True)
                    self._set_val(row, col, self.table_backup[row][col])
                    self.raw_data_table.blockSignals(False)
            self.check_table_consistency.run()
            
            # print("Backed-up table:")
            # self.print_backup_table()
        
        self.CI_spinbox.setValue(meta_py_r.get_global_conf_level())
        restore_displayed_effects_data()
        restore_table()
        self.enable_back_calculation_btn()
        ########################################################################
        # Unblock the signals
        self.block_all_signals(False)
        
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
                (good_result, msg) = is_between_bounds(est=self.candidate_est)
                if not good_result:
                    QMessageBox.warning(self, "whoops", msg)
                    raise Exception("error")
                display_scale_val = float(self.candidate_est)
            elif val_str == "lower" and not _is_empty(self.candidate_lower):
                if not _is_a_float(self.candidate_lower) :
                    QMessageBox.warning(self, "whoops", float_msg)
                    raise Exception("error")
                (good_result, msg) = is_between_bounds(low=self.candidate_lower)
                if not good_result:
                    QMessageBox.warning(self, "whoops", msg)
                    raise Exception("error")
                display_scale_val = float(self.candidate_lower)
            elif val_str == "upper" and not _is_empty(self.candidate_upper): 
                if not _is_a_float(self.candidate_upper) :
                    QMessageBox.warning(self, "whoops", float_msg)
                    raise Exception("error")
                (good_result, msg) = is_between_bounds(high=self.candidate_upper)
                if not good_result:
                    QMessageBox.warning(self, "whoops", msg)
                    raise Exception("error")
                display_scale_val = float(self.candidate_upper)
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
            self.block_all_signals(False)
            return
        
        self.block_all_signals(False)
        # If we got to this point it means everything is ok so far
        
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
        else:
            self.ma_unit.set_upper(self.cur_effect, self.group_str, calc_scale_val)
            self.ma_unit.set_display_upper(self.cur_effect, self.group_str, display_scale_val)
        
        self.enable_txt_box_input()
        self.save_form_state()
        self.enable_back_calculation_btn()
    
    def val_edit(self, val_str, display_scale_val):
        # print "Editing %s with value: %s" % (val_str,display_scale_val)
        if val_str == "est":
            self.candidate_est = display_scale_val
        if val_str == "lower":
            self.candidate_lower = display_scale_val
        if val_str == "upper":
            self.candidate_upper = display_scale_val
        
    def _update_raw_data(self):
        ''' Generates the 2x2 table with whatever parametric data was provided '''
        ''' Sets #events and #subjects in binary table'''

        for row, group in enumerate(self.cur_groups):
            for col in (0, 2):
                adjusted_index = 0 if col == 0 else 1
                val = self.raw_data_d[group][adjusted_index]
                self._set_val(row, col, val)
      
    def _update_ma_unit(self):
        ''' Copy data from binary data table to the MA_unit'''
        ''' 
        Walk over the entries in the matrix (which may have been updated
        via imputation in the cell_changed method) corresponding to the 
        raw data in the underlying meta-analytic unit and update the values.
        '''
        for row in range(2):
            for col in (0, 2):
                adjusted_col = 1 if col == 2 else 0
                self.raw_data_d[self.cur_groups[row]][adjusted_col] = self._get_int(row, col)  # TODO: ENC
                print "%s, %s: %s" % (row, col, self._get_int(row, col))
        print "ok -- raw data is now: %s" % self.raw_data_d
        
    def _cell_data_not_valid(self, celldata_string):
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
        
    def cell_changed(self, row, col):
        # tries to make sense of user input before passing
        # on to the R routine
        
        print("Entering cell changed...")
        print("New cell data(%d,%d): %s" % (row, col, self.raw_data_table.item(row, col).text()))
        
        try:
            # Test if entered data is valid (a number)
            warning_msg = self._cell_data_not_valid(self.raw_data_table.item(row, col).text())
            if warning_msg:
                raise Exception("Invalid Cell Data")
    
            self._update_data_table()  # calculate rest of table (provisionally) based on new entry
            warning_msg = self.check_table_consistency.run()
            if warning_msg:
                raise Exception("Table no longer consistent.")
        except Exception as e:
            msg = e.args[0]
            QMessageBox.warning(self.parent(), "whoops", msg)  # popup warning
            self.restore_form_state()  # brings things back to the way they were
            return  # and leave
        
        self.save_form_state()    
        self._update_ma_unit()  # table widget --> ma_unit
        self.try_to_update_cur_outcome()  # update metric
        self.enable_back_calculation_btn()
        self.save_form_state()
        
        # disable just-edited cell
        self.block_all_signals(True)
        item = self.raw_data_table.item(row, col)
        newflags = item.flags() & ~Qt.ItemIsEditable
        item.setFlags(newflags)
        self.block_all_signals(False)
        
        self.enable_txt_box_input()  # if the effect was imputed
        self.set_clear_btn_color()
        
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
    
    def clear_column(self, col):
        '''Clears out column in table and ma_unit'''

        for row in range(3):
            self.raw_data_table.blockSignals(True)
            self._set_val(row, col, None)  
            self.raw_data_table.blockSignals(False)
        
        self._update_ma_unit()
        self.save_form_state()
         
    def _set_vals(self, computed_d):
        '''Sets values in table widget'''
        self.raw_data_table.blockSignals(True)
        self._set_val(0, 0, computed_d["c11"])
        self._set_val(0, 1, computed_d["c12"])
        self._set_val(1, 0, computed_d["c21"])
        self._set_val(1, 1, computed_d["c22"])  
        self._set_val(0, 2, computed_d["r1sum"])
        self._set_val(1, 2, computed_d["r2sum"])
        self._set_val(2, 0, computed_d["c1sum"])
        self._set_val(2, 1, computed_d["c2sum"])  
        self._set_val(2, 2, computed_d["total"])  
        self.raw_data_table.blockSignals(False)  
        
    def _set_val(self, row, col, val):
        if meta_globals.is_NaN(val):  # get out quick
            print "%s is not a number" % val
            return
        
        try:
            self.raw_data_table.blockSignals(True)
            str_val = "" if val in EMPTY_VALS else str(int(val))
            if self.raw_data_table.item(row, col) == None:
                self.raw_data_table.setItem(row, col, QTableWidgetItem(str_val))
            else:
                self.raw_data_table.item(row, col).setText(str_val)
            print("    setting (%d,%d) to '%s'" % (row,col,str_val))
            
            # disable item
            if str_val != "": 
                item = self.raw_data_table.item(row, col)
                newflags = item.flags() & ~Qt.ItemIsEditable
                item.setFlags(newflags)
                
            self.raw_data_table.blockSignals(False)
        except:
            print("    Got to except in _set_val when trying to set (%d,%d)" % (row, col))
            raise
 
    def _build_dict(self):
        d = dict(zip(["control.n.outcome", "control.N", "tx.n.outcome", "tx.N"], self.raw_data))
        d["estimate"] = self.ma_unit.get_estimate(self.cur_effect, self.group_str)
        return d
        
    def _update_data_table(self):        
        '''Fill in 2x2 table from other entries in the table '''
        
        self.raw_data_table.blockSignals(True)
        
        params = self._get_table_vals()
        computed_params = meta_globals.compute_2x2_table(params)
        print "Computed Params", computed_params
        if computed_params:
            self._set_vals(computed_params)  # computed --> table widget
            
        self.raw_data_table.blockSignals(False)
        
    def _is_empty(self, i, j):
        val = self.raw_data_table.item(i, j)
        return val is None or val.text() == ""
        
    def _get_int(self, i, j):
        '''Get value from cell specified by row=i, col=j as an integer'''
        if not self._is_empty(i, j):
            val = int(float(self.raw_data_table.item(i, j).text()))
            print("Val from _get_int: %d" % val)
            return val
        else:
            return None  # its good to be explicit
            
    def _isBlank(self, x):
        return x is None or x == ""
        
    def try_to_update_cur_outcome(self):
        print("Entering try_to_update_cur_outcome...")
        print("    current effect: %s" % self.cur_effect)
        
        e1, n1, e2, n2 = self.ma_unit.get_raw_data_for_groups(self.cur_groups)
        print("    e1: %s, n1: %s, e2: %s, n2: %s" % (str(e1),str(n1),str(e2),str(n2)))
        
        two_arm_raw_data_ok = not any([self._isBlank(x) for x in [e1, n1, e2, n2]])
        one_arm_raw_data_ok = not any([self._isBlank(x) for x in [e1, n1]])
        curr_effect_is_one_arm = self.cur_effect in BINARY_ONE_ARM_METRICS
        curr_effect_is_two_arm = self.cur_effect in BINARY_TWO_ARM_METRICS
        
        # if None is in the raw data, should we clear out current outcome?
        if two_arm_raw_data_ok or (curr_effect_is_one_arm and one_arm_raw_data_ok):
            if curr_effect_is_two_arm:
                est_and_ci_d = meta_py_r.effect_for_study(e1, n1, e2, n2, metric=self.cur_effect, conf_level=self.CI_spinbox.value())
            else:
                # binary, one-arm
                est_and_ci_d = meta_py_r.effect_for_study(e1, n1, two_arm=False, metric=self.cur_effect, conf_level=self.CI_spinbox.value())
        
            display_est, display_low, display_high = est_and_ci_d["display_scale"]
            self.ma_unit.set_display_effect_and_ci(self.cur_effect, self.group_str, display_est, display_low, display_high)                            
            est, low, high = est_and_ci_d["calc_scale"]  # calculation (e.g., log) scale
            self.ma_unit.set_effect_and_ci(self.cur_effect, self.group_str, est, low, high)
            self.set_current_effect()
           
    def clear_form(self):
        keys = ["c11", "c12", "r1sum", "c21", "c22", "r2sum", "c1sum", "c2sum", "total"]
        blank_vals = dict(zip(keys, [""] * len(keys)))

        self._set_vals(blank_vals)
        self._update_ma_unit()
        
        # clear out effects stuff
        for metric in BINARY_ONE_ARM_METRICS + BINARY_TWO_ARM_METRICS:
            if ((self.cur_effect in BINARY_TWO_ARM_METRICS and metric in BINARY_TWO_ARM_METRICS) or
                (self.cur_effect in BINARY_ONE_ARM_METRICS and metric in BINARY_ONE_ARM_METRICS)):
                self.ma_unit.set_effect_and_ci(metric, self.group_str, None, None, None)
                self.ma_unit.set_display_effect_and_ci(metric, self.group_str, None, None, None)
            else:
                # TODO: Do nothing for now..... treat the case where we have to switch group strings down the line
                pass
            
        # clear line edits
        self.set_current_effect()
        self.save_form_state()
        
        self.reset_table_item_flags()
        self.initialize_backup_structures()
        self.enable_txt_box_input()
        self.CI_spinbox.setValue(meta_py_r.get_global_conf_level())
        self.CI_spinbox.setEnabled(True)
        
    def enable_txt_box_input(self):
        # meta_globals.enable_txt_box_input(self.effect_txt_box, self.low_txt_box,
        #                                  self.high_txt_box)
        # print("Enabled text box input")
        pass
        
    def reset_table_item_flags(self):
        self.block_all_signals(True)
        for row in range(3):
            for col in range(3):
                item = self.raw_data_table.item(row, col)
                if not item is None:
                    newflags = item.flags() | Qt.ItemIsEditable
                    item.setFlags(newflags)
        self.block_all_signals(False)
        
    def change_CI_alert(self, value=None):
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
        
        res["display_est"] = meta_py_r.binary_convert_scale(res["est"], self.cur_effect, convert_to="display.scale")
        res["display_low"] = meta_py_r.binary_convert_scale(res["low"], self.cur_effect, convert_to="display.scale")
        res["display_high"] = meta_py_r.binary_convert_scale(res["high"], self.cur_effect, convert_to="display.scale")
        
        # Save results in ma_unit
        self.ma_unit.set_effect_and_ci(self.cur_effect, self.group_str, res["est"], res["low"], res["high"])
        self.ma_unit.set_display_effect_and_ci(self.cur_effect, self.group_str, res["display_est"], res["display_low"], res["display_high"])
        
    def get_cur_group_str(self):
        # Inspired from get_cur_group_str of ma_data_table_model
        
        if self.cur_effect in BINARY_ONE_ARM_METRICS:
            group_str = self.cur_groups[0] 
        else:
            group_str = "-".join(self.cur_groups)
        return group_str
        
        
################################################################################
class ChooseBackCalcResultForm(QDialog, ui_choose_back_calc_result_form.Ui_ChooseBackCalcResultForm):
    def __init__(self, imputed_data, parent=None):
        super(ChooseBackCalcResultForm, self).__init__(parent)
        self.setupUi(self)
        
        op1 = imputed_data["op1"]  # option 1 data
        a, b, c, d = op1["a"], op1["b"], op1["c"], op1["d"]
        a, b, c, d = int(round(a)), int(round(b)), int(round(c)), int(round(d))
        option1_txt = "Group 1:\n  #events: %d\n  Total: %d\nGroup 2:\n  #events: %d\n  Total: %d" % (a, b, c, d)
        
        op2 = imputed_data["op2"]
        a, b, c, d = op2["a"], op2["b"], op2["c"], op2["d"]
        a, b, c, d = int(round(a)), int(round(b)), int(round(c)), int(round(d))
        option2_txt = "Group 1:\n  #events: %d\n  Total: %d\nGroup 2:\n  #events: %d\n  Total: %d" % (a, b, c, d)
        
        self.choice1_lbl.setText(option1_txt)
        self.choice2_lbl.setText(option2_txt)
        self.info_label.setText("The back-calculation has resulted in two "
                                "possible sets of choices for the counts. Please"
                                " choose one from below. These choices do not "
                                "reflect possible corrections for zero counts.")

    def getChoice(self):
        choices = ["op1", "op2"]
        
        if self.choice1_btn.isChecked():
            return choices[0]  # op1
        else:
            return choices[1]  # op2

