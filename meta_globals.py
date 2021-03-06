######################################
#                                    #       
#  Byron C. Wallace                  #
#  George Dietz                      #
#  CEBM @ Brown                      # 
#  OpenMeta[analyst]                 # 
#                                    # 
#  Contains globals used             #
#   throughout.                      # 
#                                    # 
######################################

import os

import meta_py_r
from PyQt4.Qt import QColor   #, QDialogButtonBox
from PyQt4.Qt import QMessageBox

# number of digits to display
NUM_DIGITS = 3

# Confidence level 
DEFAULT_CONF_LEVEL = 95.0    # (normal 95% CI)

# completely made up. need an actual versioning system.
VERSION = .005 

## For now we're going to hardcode which metrics are available.
# In the future, we may want to pull these out dynamically from 
# the R side. But then meta-analytic methods would have either to
# only operate over the effects and variances or else themselves 
# know how to compute arbitrary metrics.

# Binary metrics
BINARY_TWO_ARM_METRICS = ["OR", "RD", "RR", "AS", "YUQ", "YUY"]
BINARY_ONE_ARM_METRICS = ["PR", "PLN", "PLO", "PAS", "PFT"]
BINARY_METRIC_NAMES = {"OR":"Odds Ratio",
                       "RD":"Risk Difference",
                       "RR":"Risk Ratio",
                       "AS":"Difference of arcsines transformed proportions",
                       "YUQ":"Yule's Q is equal to (oi-1)/(oi+1), where oi is the odds ratio.",
                       "YUY":"Yule's Y is equal to (sqrt(oi)-1)/(sqrt(oi)+1), where oi is the odds ratio.",
                       "PR":"Untransformed Proportion",
                       "PLN":"Natural Logarithm transformed Proportion",
                       "PLO":"Logit transformed Proportion",
                       "PAS":"Arcsine transformed Proportion",
                       "PFT":"Freeman-Tukey Transformed Proportion",
                       }

# Continuous metrics
CONTINUOUS_TWO_ARM_METRICS = ["MD", "SMD"]
CONTINUOUS_ONE_ARM_METRICS = ["TX Mean"]
CONTINUOUS_METRIC_NAMES = {"MD":"Mean Difference",
                           "SMD":"Standardized Mean Difference",
                           "TX Mean":"TX Mean",
                           }


# Default metrics (for when making a new dataset)
DEFAULT_BINARY_ONE_ARM = "PR"
DEFAULT_BINARY_TWO_ARM = "OR"
DEFAULT_CONTINUOUS_ONE_ARM = "TX Mean"
DEFAULT_CONTINUOUS_TWO_ARM = "SMD"

# Sometimes it's useful to know if we're dealing with a one-arm outcome,
# in general
ONE_ARM_METRICS = BINARY_ONE_ARM_METRICS + CONTINUOUS_ONE_ARM_METRICS 
TWO_ARM_METRICS = BINARY_TWO_ARM_METRICS + CONTINUOUS_TWO_ARM_METRICS

# Diagnostic metrics
DIAGNOSTIC_METRICS = ["Sens", "Spec", "PLR", "NLR", "DOR"]
DIAGNOSTIC_LOG_METRICS = ["PLR", "NLR", "DOR"]
DIAGNOSTIC_METRIC_NAMES = {"Sens":"Sensitivity",
                           "Spec":"Specificity",
                           "PLR":"Positive Likelihood Ratio",
                           "NLR":"Negative Likelihood Ratio",
                           "DOR":"Diagnostic Odds Ratio",
                           }

# Construct dictionary of all the metric names
ALL_METRIC_NAMES = {}
ALL_METRIC_NAMES.update(BINARY_METRIC_NAMES)
ALL_METRIC_NAMES.update(CONTINUOUS_METRIC_NAMES)
ALL_METRIC_NAMES.update(DIAGNOSTIC_METRIC_NAMES)

# enumeration of data types and dictionaries mapping both ways
BINARY, CONTINUOUS, DIAGNOSTIC, OTHER = range(4)

# we need two types for covariates; factor and continuous. we'll use the 
# above definition (enumerated as part of a general data type) for continuous
# and just define factor here.
FACTOR = 4

# making life easier
COV_INTS_TO_STRS = {4:"Factor", 1:"Continuous"}

STR_TO_TYPE_DICT = {u"binary":BINARY,
                    u"continuous":CONTINUOUS, 
                    u"diagnostic":DIAGNOSTIC,
                    u"OTHER":OTHER
                    }

TYPE_TO_STR_DICT = {BINARY:u"binary",
                    CONTINUOUS:u"continuous",
                    DIAGNOSTIC:u"diagnostic",
					OTHER:u"OTHER",
                    FACTOR:u"factor",
                    }
                                    
# enumeration of meta-analytic types
VANILLA, NETWORK = range(2)

EMPTY_VALS = ("", None) # these indicate an empty row/cell 

BASE_PATH = str(os.path.abspath(os.getcwd())) # where temporary R output should go

# this is the (local) path to a (pickled) dictionary containing
# user preferences
PREFS_PATH = "user_prefs.dict"

# this is a useful function sometimes.
none_to_str = lambda x: "" if x is None else x

HELP_URL = "http://www.cebm.brown.edu/open_meta"

# for diagnostic data -- this dictionary maps
# the mteric names as they appear in the UI/ure
# used here to the names used in the model.
# see get_diag_metrics_to_run.
DIAG_METRIC_NAMES_D = {"sens":["Sens"], 
                       "spec":["Spec"],
                       "dor":["DOR"],
                       "lr":["PLR", "NLR"]
                      }

DIAG_FIELDS_TO_RAW_INDICES = {"TP":0, "FN":1, "FP":2, "TN":3}

PATH_TO_HELP = "http://tuftscaes.org/open_meta/help/openMA_help.html"#os.path.join("doc", "openMA_help.html")

# list of methods with no forest plot parameters
METHODS_WITH_NO_FOREST_PLOT = ["diagnostic.hsroc", "diagnostic.bivariate.ml"]

# this is the maximum size of a residual that we're willing to accept
# when computing 2x2 data
THRESHOLD = 1e-5

ERROR_COLOR = QColor("red")
OK_COLOR = QColor("black")

DEFAULT_GROUP_NAMES = ["Grp A", "Grp B"]  # old: DEFAULT_GROUP_NAMES = ["tx A", "tx B"]


'''
some useful static methods
'''

def seems_sane(xticks):
    num_list = xticks.split(",")
    if len(num_list) == 1:
        return False
    try:
        num_list = [eval(x) for x in num_list]
    except:
        return False
    return True
    
def check_plot_bound(bound):
    try:
        # errrm... this might cause a problem if 
        # bound is 0... 
        return float(bound) 
    except:
        return False

def _is_a_float(s):
    try:
        float(s)
        return True
    except:
        return False

def _is_empty(s):
    return s is None or s == ""
    
def _is_an_int(s):
    try:
        int(s)
        return True
    except:
        return False
    
def is_NaN(x):
    # there's no built-in for checking if a number is a NaN in
    # Python < 2.6. checking if a number is equal to itself
    # does the trick, though purportedly does not always work.
    return x != x



# These two functions started life in the diagnostic data form used for checking
#  that low < effect < high
def my_lt(a,b):
    if _is_a_float(a) and _is_a_float(b):
        return float(a) < float(b)
    else:
        return None
def between_bounds(est=None, 
                   low=None, 
                   high=None):
    good_result = my_lt(low,est)
    okay = True if not (good_result is None) else False
    if okay and not good_result:
        msg = "The lower CI must be less than the point estimate!"
        return False,msg
    
    good_result = my_lt(est,high)
    okay = True if not (good_result is None) else False
    if okay and not good_result:
        msg = "The higher CI must be greater than the point estimate!"
        return False,msg
    
    good_result = my_lt(low,high)
    okay = True if not (good_result is None) else False
    if okay and not good_result:
        msg = "The lower CI must be less than the higher CI!"
        return False,msg
    
    return True,None

def cast_to_int(value, name=None):
    '''Converts value to int if possible'''
    try:
        rounded = round(float(value))
        return int(rounded)
    except:
        if not name is None:
            print("Could not convert %s='%s' to int" % (name,str(value)))
        else:
            print("Could not convert '%s' to int" % (str(value)))
        return None

def compute_2x2_table(params):
    ''' Computes values for the whole 2x2 table if possible based on partial values from the rest of the table'''
    
    # Realized R code is screwy.... now for some more screwy code that hopefully works better
    table = [[ params['c11'],   params['c12'],   params['r1sum']],
             [ params['c21'],   params['c22'],   params['r2sum']],
             [ params['c1sum'], params['c2sum'], params['total'] ]]
    
    while True:
        changed = False 
        for row in range(3):
            for col in range(3):
                # go through row-wise
                if table[row][col] in EMPTY_VALS:
                    if col == 0:
                        try:
                            table[row][col] = table[row][2] - table[row][1]
                            changed = True
                        except:
                            pass
                    if col == 1:
                        try:
                            table[row][col] = table[row][2] - table[row][0]
                            changed = True
                        except:
                            pass
                    if col == 2:
                        try:
                            table[row][col] = table[row][0] + table[row][1]
                            changed = True
                        except:
                            pass
                # and now column-wise
                if table[row][col] in EMPTY_VALS:
                    if row == 0:
                        try:
                            table[row][col] = table[2][col] - table[1][col]
                            changed = True
                        except:
                            pass
                    if row == 1:
                        try:
                            table[row][col] = table[2][col] - table[0][col]
                            changed = True
                        except:
                            pass
                    if row == 2:
                        try:
                            table[row][col] = table[0][col] + table[1][col]
                            changed = True
                        except:
                            pass
        if not changed:
            break
    ## end of big while loop
        
    coef = {}
    coef['c11']   = table[0][0]
    coef['c12']   = table[0][1]
    coef['r1sum'] = table[0][2]
    coef['c21']   = table[1][0]
    coef['c22']   = table[1][1]
    coef['r2sum'] = table[1][2]
    coef['c1sum'] = table[2][0]
    coef['c2sum'] = table[2][1]
    coef['total'] = table[2][2]
    
    return coef

# Consistency checking code for 2x2 tables (binary and diagnostic)
########################### CONSISTENCY CHECKING CODE ##########################
class ConsistencyChecker():
    def __init__(self,fn_consistent=None,fn_inconsistent=None,table_2x2=None):
        functions_passed = (not fn_consistent is None) and (not fn_inconsistent is None)
        assert functions_passed, "Not enough functions passed to check_for_consistencies"
        assert not table_2x2 is None, "No table argument passed."
        
        self.inconsistent = False
        self.inconsistent_action = fn_inconsistent
        self.consistent_action = fn_consistent
        self.table = table_2x2
        
    def run(self):
        msg = self.check_for_consistencies()
        
        if not self.inconsistent:
            self._color_all(color=OK_COLOR)
        return msg
     
    def check_for_consistencies(self):
        self.inconsistent = False
        rows_sum  = self.check_that_rows_sum() # also colors non-summing rows
        cols_sum = self.check_that_cols_sum()
        all_pos  = self.check_that_values_positive()
        
        if self.inconsistent:
            self.inconsistent_action()
        else:
            self.consistent_action()
        
        if not rows_sum:
            return "Rows must sum!"
        elif not cols_sum:
            return "Columns must sum!"
        elif not all_pos:
            return "Counts must be positive!"
        else:
            return None
        
    def check_that_rows_sum(self):
        rows_sum = True
        for row in range(3):
            if self._row_is_populated(row):
                row_sum = 0
                for col in range(2):
                    row_sum += self._get_int(row, col)
                if not row_sum == self._get_int(row, 2):
                    self._color_row(row)
                    self.inconsistent = True
                    rows_sum = False
        return rows_sum
    
    def _get_int(self, i, j):
        '''Get value from cell specified by row=i, col=j as an integer'''
        if not self._is_empty_cell(i,j):
            return int(float(self.table.item(i, j).text()))
        else:
            return None # its good to be explicit
                    
    def check_that_cols_sum(self):
        cols_sum = True
        for col in range(3):
            if self._col_is_populated(col):
                col_sum = 0
                for row in range(2):
                    col_sum += self._get_int(row,col)
                if not col_sum == self._get_int(2,col):
                    self._color_col(col)
                    self.inconsistent = True
                    cols_sum = False
        return cols_sum
                    
    def check_that_values_positive(self):
        all_positive = True
        
        for row in range(3):
            for col in range(3):
                value = self._get_int(row,col)
                if not value in EMPTY_VALS:
                    if value < 0:
                        # Color item
                        self.table.blockSignals(True)
                        self.table.item(row,col).setTextColor(ERROR_COLOR)
                        self.table.blockSignals(False)
                        # Set flag
                        self.inconsistent = True
                        all_positive = False
        return all_positive
                        
    def _color_all(self, color=ERROR_COLOR):
        self.table.blockSignals(True)
        for row in range(3):
            for col in range(3):
                #print "setting row: %s, col: %s" % (row, col)
                item = self.table.item(row, col)
                if item is not None:
                    item.setTextColor(color)
        self.table.blockSignals(False)
        
    def _color_row(self, row):
        self.table.blockSignals(True)
        for col in range(3):
            print "setting row: %s, col: %s" % (row, col)
            self.table.item(row, col).setTextColor(ERROR_COLOR)
        self.table.blockSignals(False)
        
    def _color_col(self, col):
        self.table.blockSignals(True)
        for row in range(3):
            print "setting row: %s, col: %s" % (row, col)
            self.table.item(row, col).setTextColor(ERROR_COLOR)
        self.table.blockSignals(False)
        
    def _row_is_populated(self, row):
        
        result = not True in [self._is_empty_cell(row, col) for col in range(3)]
        if result:
            print "Row %d is populated" % row
        return result
    def _col_is_populated(self, col):
        return not True in [self._is_empty_cell(row, col) for row in range(3)]
    
    def _is_empty_cell(self, i, j):
        val = self.table.item(i,j)
        return val is None or val.text() == ""
########################### END CONSISTENCY CHECKER ############################

####### SHARED BINARY, CONTINUOUS, DIAGNOSTIC DATA FORM UTILITY FUNCTIONS#####
def enable_txt_box_input(*args):
    ''' Enables text boxes if they are empty, disables them otherwise
        Input is textbox(es) '''
    
    for text_box in args:
        text_box.blockSignals(True)
        
        text_box.setEnabled(False)
        if text_box.text() in EMPTY_VALS:
            text_box.setEnabled(True)
            
        text_box.blockSignals(False)
        
def init_ci_spinbox_and_label(ci_spinbox, ci_label, value=None):
    if value is None:
        value = meta_py_r.get_global_conf_level()
    
    ci_spinbox.blockSignals(True)
    ci_spinbox.setValue(value)
    ci_label.setText("{0:.1f}% Confidence Interval".format(ci_spinbox.value()))
    ci_spinbox.blockSignals(False)
####### end enable_txt_box_input #######
 
CHANGE_CI_ALERT_BASE_MSG = (
    "The size of the confidence level used for a particular study in this "
    "calculator need not correspond with the global confidence level "
    "(currently set at {0:.1%}) chosen for data display on spreadsheets and "
    "forest plots.")
def get_CHANGE_CI_ALERT_MSG():
    return CHANGE_CI_ALERT_BASE_MSG.format(meta_py_r.get_global_conf_level()/100.0)

# WORK ON STANDARDIZING THIS LATER?
#def validate_txt_box_input(box_data=None,
#                           block_all_signals=None,
#                           val_str=None,
#                           parent=None,
#                           *args):
#    '''validates txt box input based on info for each field given by the dicts'''
#    
#    
#    est_default = box_data['est']['default']
#    low_default = box_data['low']['default']
#    high_default = box_data['high']['default']
#    
#    def is_between_bounds(est=est_default, low=low_default, high=high_default):
#        return between_bounds(est=est, low=low, high=high)
#    
#    # Make sure entered value is numeric and between the appropriate bounds
#    block_all_signals(True)
#    float_msg = "Must be numeric!"
#    try:
#        for box_key, box_info in box_data.iteritems():
#            if val_str==box_key and not _is_empty(box_info['candidate']):
#                # Check type
#                if not _is_a_float(box_info['candidate']) :
#                    QMessageBox.warning(self.parent(), "whoops", float_msg)
#                    raise Exception("error")
#                (good_result,msg) = is_between_bounds(est=self.candidate_est)
#                if not good_result:
#                    QMessageBox.warning(parent, "whoops", msg)
#                    raise Exception("error")
#                if (not 0 <= float(self.candidate_est) <= 1):
#                    QMessageBox.warning(parent, "whoops", "Estimate must be between 0 and 1.")
#                    raise Exception("error")
#                display_scale_val = float(box_info['candidate'])
#    
#
#    ###### ERROR CHECKING CODE#####
#
#    try:
#        if val_str == "est" and not _is_empty(self.candidate_est):
#            # Check type
#            if not _is_a_float(self.candidate_est) :
#                QMessageBox.warning(self.parent(), "whoops", float_msg)
#                raise Exception("error")
#            (good_result,msg) = is_between_bounds(est=self.candidate_est)
#            if not good_result:
#                QMessageBox.warning(self.parent(), "whoops", msg)
#                raise Exception("error")
#            if (not 0 <= float(self.candidate_est) <= 1):
#                QMessageBox.warning(self.parent(), "whoops", "Estimate must be between 0 and 1.")
#                raise Exception("error")
#            display_scale_val = float(self.candidate_est)
#        elif val_str == "lower" and not _is_empty(self.candidate_lower):
#            if not _is_a_float(self.candidate_lower) :
#                QMessageBox.warning(self.parent(), "whoops", float_msg)
#                raise Exception("error")
#            (good_result,msg) = is_between_bounds(low=self.candidate_lower)
#            if not good_result:
#                QMessageBox.warning(self.parent(), "whoops", msg)
#                raise Exception("error")
#            display_scale_val = float(self.candidate_lower)
#        elif val_str == "upper" and not _is_empty(self.candidate_upper): 
#            if not _is_a_float(self.candidate_upper) :
#                QMessageBox.warning(self.parent(), "whoops", float_msg)
#                raise Exception("error")
#            (good_result,msg) = is_between_bounds(high=self.candidate_upper)
#            if not good_result:
#                QMessageBox.warning(self.parent(), "whoops", msg)
#                raise Exception("error")
#            display_scale_val = float(self.candidate_upper)
#        elif val_str == "prevalence" and not _is_empty(self.candidate_prevalence):
#            if not _is_a_float(self.candidate_prevalence):
#                QMessageBox.warning(self.parent(), "whoops", float_msg)
#                raise Exception("error")
#            if _is_a_float(self.candidate_prevalence) and not 0 < float(self.candidate_prevalence) < 1:
#                QMessageBox.warning(self.parent(), "whoops", "Prevalence must be between 0 and 1.")
#                raise Exception("error")
#    except:
#        print "Error flag is true"
#        self.restore_form_state()
#        block_all_signals(True)
#        if val_str == "est":
#            self.effect_txt_box.setFocus()
#        elif val_str == "lower":
#            self.low_txt_box.setFocus()
#        elif val_str == "upper":
#            self.high_txt_box.setFocus()
#        elif val_str == "prevalence":
#            self.prevalence_txt_box.setFocus()
#        block_all_signals(False)
#        return
#            
#    block_all_signals(False)

################FOR FROM BEGINNING OF val_changed of diagnostic_data_form######
#        est_d = {'default':self.form_effects_dict[self.cur_effect]["est"],
#                 'candidate':self.candidate_est,}
#        low_d = {'default':self.form_effects_dict[self.cur_effect]["lower"],
#                 'candidate':self.candidate_lower,}
#        high_d = {'default':self.form_effects_dict[self.cur_effect]["upper"],
#                  'candidate':self.candidate_upper,}
#        
#        box_data = {'est':est_d, 'low':low_d, 'high':high_d}
#        
#        meta_globals.validate_txt_box_input(box_data=box_data,
#                                            block_all_signals=self.block_all_signals,
#                                            val_str = val_str,
#                                            parent=self.parent()
#                                            )
################################################################################