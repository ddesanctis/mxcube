import qt
import logging
import copy
import queue_item
import queue_model_objects_v1 as queue_model_objects
import sys
import os

#from PyMca import QPeriodicTable
from PeriodicTableBrick import PeriodicTableBrick
from create_task_base import CreateTaskBase
from widgets.data_path_widget import DataPathWidget
from widgets.data_path_widget_vertical_layout import\
    DataPathWidgetVerticalLayout
from BlissFramework.Utils import widget_colors

class CreateEnergyScanWidget(CreateTaskBase):
    def __init__(self, parent = None, name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, fl, 'Energy-scan')

        # Data attributes
        self.init_models()

        #Layout
        v_layout = qt.QVBoxLayout(self, 2, 5, "main_v_layout")
        h_box = qt.QHGroupBox('Available elements', self)
        self.periodic_table = PeriodicTableBrick(h_box) #QPeriodicTable.QPeriodicTable(h_box)
        font = self.periodic_table.font()
        font.setPointSize(8)
        self.periodic_table.setFont(font)
        
        h_box.setMaximumWidth(454)
        h_box.setMaximumHeight(300)

        self._data_path_gbox = qt.QVGroupBox('Data location', self, 'data_path_gbox')
        self._data_path_widget = DataPathWidget(self._data_path_gbox, 
                                               data_model = self._path_template,
                                               layout = DataPathWidgetVerticalLayout)

        self._data_path_widget.data_path_widget_layout.file_name_label.setText('')
        self._data_path_widget.data_path_widget_layout.file_name_value_label.hide()


        v_layout.addWidget(h_box)
        v_layout.addWidget(self._data_path_gbox)
        v_layout.addStretch()


        self.connect(self._data_path_widget.data_path_widget_layout.prefix_ledit, 
                     qt.SIGNAL("textChanged(const QString &)"), 
                     self._prefix_ledit_change)


        self.connect(self._data_path_widget.data_path_widget_layout.run_number_ledit,
                     qt.SIGNAL("textChanged(const QString &)"), 
                     self._run_number_ledit_change)
        
        self.connect(self._data_path_widget,
                     qt.PYSIGNAL("path_template_changed"),
                     self.handle_path_conflict)

    def _prefix_ledit_change(self, new_value):
        item = self._current_selected_item
        
        if isinstance(item, queue_item.EnergyScanQueueItem):
            prefix = self._path_template.get_prefix()
            item.get_model().set_name(prefix)
            item.setText(0, item.get_model().get_name())
        

    def _run_number_ledit_change(self, new_value):
        item = self._current_selected_item
        
        if isinstance(item, queue_item.EnergyScanQueueItem):
            if str(new_value).isdigit():
                item.get_model().set_number(int(new_value))
                item.setText(0, item.get_model().get_name())


    def init_models(self):
        self.enery_scan = queue_model_objects.EnergyScan()
        self._path_template = queue_model_objects.PathTemplate()


    def set_energy_scan_hw_obj(self, energy_hwobj):
        self.periodic_table.periodicTable.\
            setElements(energy_hwobj.getElements())


    def _selection_changed(self, tree_item):
        if isinstance(tree_item, queue_item.SampleQueueItem) or \
               isinstance(tree_item, queue_item.DataCollectionGroupQueueItem):

            self.init_models()
            sample_data_model = self.get_sample_item().get_model()

            (data_directory, proc_directory) = self.get_default_directory()
                
            self._path_template.directory = data_directory
            self._path_template.process_directory = proc_directory
            self._path_template.base_prefix = self.get_default_prefix(sample_data_model)
            self._path_template.run_number = self._tree_brick.queue_model_hwobj.\
                                             get_run_number(self._path_template)
            
        elif isinstance(tree_item, queue_item.EnergyScanQueueItem):
            escan_model = tree_item.get_model()
            self._path_template = escan_model.path_template

        self._data_path_widget.update_data_model(self._path_template)


    def handle_path_conflict(self, widget, new_value):
        path_conflict = self._tree_brick.queue_model_hwobj.\
                        check_for_path_collisions(self._path_template)

        if new_value != '':
            if path_conflict:
                logging.getLogger("user_level_log").\
                    error('The current path settings will overwrite data' +\
                          ' from another task. Correct the problem before adding to queue')

                widget.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
            else:
                widget.setPaletteBackgroundColor(widget_colors.WHITE)


    def approve_creation(self):
        selected_edge = False
        
        if self.periodic_table.current_edge:
            selected_edge = True
        else:
            logging.getLogger("user_level_log").\
                info("No element selected, please select an element.") 

        path_conflict = self._tree_brick.queue_model_hwobj.\
                        check_for_path_collisions(self._path_template)

        if path_conflict:
            logging.getLogger("user_level_log").\
                error('The current path settings will overwrite data' +\
                      ' from another task. Correct the problem before adding to queue')

        return (not path_conflict) and selected_edge


    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, dcg, sample):
        data_collections = []

        if self.periodic_table.current_edge:
            path_template = copy.deepcopy(self._path_template)
            
            energy_scan = queue_model_objects.EnergyScan(sample,
                                                         path_template)
            energy_scan.set_name(path_template.get_prefix())
            energy_scan.set_number(path_template.run_number)
            energy_scan.symbol = self.periodic_table.current_element
            energy_scan.edge = self.periodic_table.current_edge

            data_collections.append(energy_scan)
        else:
            logging.getLogger("user_level_log").\
                info("No element selected, please select an element.") 

        return data_collections


if __name__ == "__main__":
    app = qt.QApplication(sys.argv)
    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"), app, qt.SLOT("quit()"))
    widget = CreateEnergyScanWidget()
    app.setMainWidget(widget)
    widget.show()
    app.exec_loop()