#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import os

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

import Qt4_queue_item
import queue_model_enumerables_v1 as queue_model_enumerables


class TreeOptionsDialog(QtGui.QDialog):
    """
    Descript. : 
    """
 
    def __init__(self, parent = None, name = None, flags = 0):
        QtGui.QDialog.__init__(self, parent,
              QtCore.Qt.WindowFlags(flags | QtCore.Qt.WindowStaysOnTopHint))

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.sample_listview = None

        # Properties ---------------------------------------------------------- 

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.tree_options_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
                       'ui_files/Qt4_tree_options_dialog_widget_layout.ui'))

        # Layout --------------------------------------------------------------
        __main_vlayout = QtGui.QVBoxLayout(self)
        __main_vlayout.addWidget(self.tree_options_widget)
        __main_vlayout.setSpacing(0)
        __main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.tree_options_widget.reset_button.clicked.connect(\
             self.reset_button_clicked)
        self.tree_options_widget.close_button.clicked.connect(\
             self.close_button_clicked)
        self.tree_options_widget.basket_treewidget.itemClicked.connect(\
             self.basket_filter_listview_clicked)
        self.tree_options_widget.protein_treewidget.itemClicked.connect(\
             self.protein_filter_listview_clicked)
        self.tree_options_widget.space_group_combo.activated.connect(\
             self.space_group_changed)
        self.tree_options_widget.holder_length_combo.activated.connect(\
             self.holder_length_changed)

    def space_group_changed(self, index):
        space_group = self.space_group_combo.currentText()
        it = qt.QListViewItemIterator(self.sample_listview)
        item = it.current()

        while item:
            if isinstance(item, queue_item.SampleQueueItem):
                item_space_group = item.get_model().crystals[0].space_group
                if space_group == "All":
                    item.setVisible(True)
                else:
                    item.setVisible(str(item_space_group) == space_group)
            it += 1
            item = it.current()

    def holder_length_changed(self, index):
        holder_length = self.holder_length_combo.currentText()
        it = qt.QListViewItemIterator(self.sample_listview)
        item = it.current()

        while item:
            if isinstance(item, queue_item.SampleQueueItem):
                item_holder_length = item.get_model().crystals[0].holder_length
                if space_group == "All":
                    item.setVisible(True)
                else:
                    item.setVisible(str(item_holder_length) == holder_length)
            it += 1
            item = it.current() 

    def basket_filter_listview_clicked(self, listview_item):
        it = qt.QListViewItemIterator(self.sample_listview)
        item = it.current()

        while item:
            if isinstance(item, queue_item.BasketQueueItem):
                if listview_item.text() == item.get_model().get_display_name():
                    item.setVisible(listview_item.isOn())
            it += 1
            item = it.current()

    def protein_filter_listview_clicked(self, listview_item):
        it = qt.QListViewItemIterator(self.sample_listview)
        item = it.current()

        while item:
            if isinstance(item, queue_item.SampleQueueItem):
                protein_name = item.get_model().crystals[0].protein_acronym
                if listview_item.text() == protein_name:
                    item.setVisible(listview_item.isOn())
            it += 1
            item = it.current()

    def set_filter_lists(self, sample_listview):
        self.sample_listview = sample_listview
        item_iterator = QtGui.QTreeWidgetItemIterator(self.sample_listview)
        self.basket_list = []
        self.sample_list = []
        self.protein_list = []      
        self.space_group_list = [] 
        self.holder_length_list = []

        item = item_iterator.value()
       
        while item:
            if isinstance(item, Qt4_queue_item.BasketQueueItem):
                self.basket_list.append(item)
            if isinstance(item, Qt4_queue_item.SampleQueueItem):
                self.sample_list.append(item)

                protein_name = item.get_model().crystals[0].protein_acronym
                if protein_name not in self.protein_list:
                    self.protein_list.append(protein_name)
                space_group = item.get_model().crystals[0].space_group
                if space_group not in self.space_group_list:
                    self.space_group_list.append(space_group)
                holder_length = item.get_model().holder_length
                if holder_length not in self.holder_length_list:
                    self.holder_length_list.append(holder_length)

            item_iterator += 1
            item = item_iterator.value()

        self.tree_options_widget.basket_treewidget.clear()
        for basket in self.basket_list:
            #last_item = self.basket_filter_tree.lastItem()
            item = QtGui.QTreeWidgetItem(self.tree_options_widget.basket_treewidget, 
                                         str(basket.get_model().get_display_name()))
            item.setCheckState(0, QtCore.Qt.Checked)

        """
        self.protein_filter_listview.clear()
        for protein in self.protein_list:
            last_item = self.protein_filter_listview.lastItem()
            item = qt.QCheckListItem(self.protein_filter_listview, last_item, 
                protein, qt.QCheckListItem.CheckBoxController)
            item.setState(qt.QCheckListItem.On)

        self.space_group_combo.clear()
        self.space_group_combo.insertItem("All")
        for space_group in self.space_group_list:
            self.space_group_combo.insertItem(str(space_group))
        self.space_group_combo.setCurrentItem(0)

        self.holder_length_combo.clear()
        self.holder_length_combo.insertItem("All")
        for holder_length in self.holder_length_list:
            self.holder_length_combo.insertItem(str(holder_length))
        self.holder_length_combo.setCurrentItem(0)
        """

    def reset_button_clicked(self):
        it = qt.QListViewItemIterator(self.sample_listview)
        item = it.current()
        while item:
            item.setVisible(True)
            it += 1
            item = it.current()

        it = qt.QListViewItemIterator(self.basket_filter_listview)
        item = it.current()
        while item:
            item.setState(qt.QCheckListItem.On)
            it += 1
            item = it.current()

        it = qt.QListViewItemIterator(self.protein_filter_listview)
        item = it.current()
        while item:
            item.setState(qt.QCheckListItem.On)
            it += 1
            item = it.current()

        self.space_group_combo.setCurrentItem(0)  
        self.holder_length.setCurrentItem(0)

    def close_button_clicked(self):
        self.reject()