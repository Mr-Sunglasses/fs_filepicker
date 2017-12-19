# -*- coding: utf-8 -*-
"""

    fslib._tests.test_fs_filepicker
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    tests fslib.fs_filepicker

    This file is part of fs_filepicker.

    :copyright: Copyright 2017 Reimar Bauer
    :license: APACHE-2.0, see LICENSE for details.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import mock
import fs
import pytest

from PyQt5 import QtCore, QtWidgets, QtTest
from conftest import ROOT_FS, TESTDATA_DIR, ROOT_DIR, SUB_DIRS
from fslib import fs_filepicker


class Test_Open_FilePicker(object):
    def setup(self):
        self.application = QtWidgets.QApplication([])
        self.fs_url = ROOT_FS.geturl(TESTDATA_DIR)
        self.window = fs_filepicker.FilePicker(fs_url=self.fs_url)
        self.window.show()
        QtWidgets.QApplication.processEvents()
        QtTest.QTest.qWaitForWindowExposed(self.window)
        QtWidgets.QApplication.processEvents()

    def teardown(self):
        self.application.quit()

    def test_fs_filepicker_cancel(self):
        self.window.cancel()
        filename = self.window.filename
        self.window.close()
        assert filename is None

    def test_fs_filepicker_nothing_selected_ok(self):
        self.window.action()
        filename = self.window.filename
        self.window.close()
        assert filename is None

    def test_fs_filepicker_files_selected_ok(self):
        data_fs = fs.open_fs(fs.path.join(ROOT_DIR, TESTDATA_DIR))
        for item in sorted(data_fs.listdir(u'.')):
            if data_fs.isfile(item):
                self.window.ui_SelectedName.setText(item)
                QtWidgets.QApplication.processEvents()
                self.window.selection_name()
                QtWidgets.QApplication.processEvents()
                assert self.window.filename == item
        self.window.close()

    def test_selection_directory(self):
        index = sorted(SUB_DIRS).index(u'testdata/foo')
        self.window.ui_FileList.selectRow(index)
        QtWidgets.QApplication.processEvents()
        self.window.onCellDoubleClicked(index, 0)
        QtWidgets.QApplication.processEvents()
        self.window.selection_directory()

        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        self.window.action()
        assert u"./foo/foo.txt" in self.window.file_list_items
        assert len(self.window.file_list_items) == 1

    def test_showname_close(self):
        self.window.show_name()
        self.window.close()
        assert self.window.filename is None

    def test_showname_on_filename(self):
        self.window.show_name()
        filename = u"./example.csv"
        all_items = self.window.dir_list_items + self.window.file_list_items
        index = all_items.index(filename)
        self.window.ui_FileList.selectRow(index)
        QtWidgets.QApplication.processEvents()
        self.window.onCellClicked(index, 0)
        QtWidgets.QApplication.processEvents()
        self.window.show_name()
        self.window.close()
        assert self.window.filename == fs.path.basename(filename)

    def test_selection_file_type(self):
        self.window.file_pattern = u"*.never"
        self.window.ui_FileType.setText(u"*.never")
        QtWidgets.QApplication.processEvents()
        self.window.selection_file_type()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        self.window.browse_folder()
        self.window.selection_directory()
        QtWidgets.QApplication.processEvents()
        assert self.window.filename is None
        self.window.ui_FileType.setText(u"*.txt")
        QtWidgets.QApplication.processEvents()
        self.window.selection_file_type()
        QtWidgets.QApplication.processEvents()
        self.window.ui_FileList.setFocus()
        QtWidgets.QApplication.processEvents()
        self.window.ui_SelectedName.setText(u"example.txt")
        QtWidgets.QApplication.processEvents()
        self.window.action()
        QtWidgets.QApplication.processEvents()
        assert self.window.filename == u"example.txt"

    def test_subdirectory(self):
        self.window.browse_folder(subdir=u"bar")
        self.window.selection_directory()
        QtWidgets.QApplication.processEvents()
        self.window.onCellClicked(0, 0)
        QtWidgets.QApplication.processEvents()
        self.window.action()
        QtWidgets.QApplication.processEvents()
        self.window.close()
        assert self.window.filename == "foo.txt"

    def test_onCellClicked(self):
        self.window.onCellDoubleClicked(0, 0)
        QtWidgets.QApplication.processEvents()
        self.window.close()
        assert u"bar" in self.window.ui_DirList.currentText()
        assert u"./bar/foo.txt" in self.window.file_list_items


class Test_Save_FilePicker(object):
    def setup(self):
        self.application = QtWidgets.QApplication([])
        self.fs_url = ROOT_FS.geturl(TESTDATA_DIR)
        self.window = fs_filepicker.FilePicker(fs_url=self.fs_url, show_save_action=True)
        self.window.show()
        QtWidgets.QApplication.processEvents()
        QtTest.QTest.qWaitForWindowExposed(self.window)
        QtWidgets.QApplication.processEvents()

    def teardown(self):
        self.application.quit()

    def test_fs_filepicker_cancel(self):
        self.window.cancel()
        filename = self.window.filename
        self.window.close()
        assert filename is None

    def test_filename_cancel(self):
        self.window.ui_SelectedName.setText(u"example.txt")
        QtWidgets.QApplication.processEvents()
        self.window.action()
        QtWidgets.QApplication.processEvents()
        self.window.cancel()
        QtWidgets.QApplication.processEvents()
        filename = self.window.filename
        assert filename is None

    def test_filename_save_newname(self):
        self.window.ui_SelectedName.setText(u"newexample.txt")
        QtWidgets.QApplication.processEvents()
        self.window.action()
        QtWidgets.QApplication.processEvents()
        self.window.close()
        filename = self.window.filename
        assert filename == u"newexample.txt"

    def test_filename_high_light_by_selectedname(self):
        pytest.skip("this needs further investigation")
        index = sorted(SUB_DIRS).index(u'testdata/foo')
        self.window.ui_FileList.selectRow(index)
        QtWidgets.QApplication.processEvents()
        self.window.onCellClicked(index, 0)
        QtWidgets.QApplication.processEvents()
        self.window.ui_SelectedName.setText(u'foo.txt')
        QtWidgets.QApplication.processEvents()
        self.window.selection_name()
        QtWidgets.QApplication.processEvents()
        # get the highlighted row
        index = self.window.ui_FileList.selectedIndexes()[0].row()
        assert index == 0

    def test_default_filename(self):
        self.window.default_filename = u"abc.txt"
        self.window.show_action()
        QtWidgets.QApplication.processEvents()
        self.window.action()
        QtWidgets.QApplication.processEvents()
        self.window.close()
        filename = self.window.filename
        assert filename == u"abc.txt"

    def test_save_in_empty_dir(self):
        index = sorted(SUB_DIRS).index(u'testdata/empty')
        self.window.ui_FileList.selectRow(index)
        QtWidgets.QApplication.processEvents()
        self.window.onCellClicked(index, 0)
        QtWidgets.QApplication.processEvents()
        self.window.selection_directory()
        self.window.ui_SelectedName.setText(u"example.txt")
        QtWidgets.QApplication.processEvents()
        self.window.action()
        QtWidgets.QApplication.processEvents()
        self.window.close()
        assert self.window.wparm.value == u'./empty'
        assert u"example.txt" in self.window.filename

    @mock.patch("fslib.fs_filepicker.QtWidgets.QInputDialog.getText",
                return_value=(u"exampledir", True))
    def test_makedir(self, mocktext):
        index = sorted(SUB_DIRS).index(u'testdata/empty')
        self.window.ui_FileList.selectRow(index)
        QtWidgets.QApplication.processEvents()
        self.window.onCellDoubleClicked(index, 0)
        QtWidgets.QApplication.processEvents()
        self.window.make_dir()
        QtWidgets.QApplication.processEvents()
        self.window.close()
        assert u'./empty/exampledir' in self.window.dir_list_items
