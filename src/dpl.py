#
# dropbox-links.py
# Copyright (C) 2013  Ilan Pegoraro
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from gi.repository import Gtk
from gi.repository import Gdk
import os
import subprocess


class  ListViewTestApp:
    def __init__(self, dirpath):
        builder = Gtk.Builder()
        builder.add_from_file('src/main-ui.glade')
        builder.connect_signals(self)
        self.shown = True

        self.statusIcon = Gtk.StatusIcon()
        self.statusIcon.set_from_stock(Gtk.STOCK_ABOUT)
        self.statusIcon.set_tooltip_text("Dropbox link detector")
        self.statusIcon.set_has_tooltip(True)
        
        self.dirpath = dirpath
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        
        self.btnCopy = builder.get_object('btnCopy')
        self.model = builder.get_object('list_items')
        self.list = builder.get_object('items_view')

        column = Gtk.TreeViewColumn('Name', Gtk.CellRendererText(), text=0)
        column.set_clickable(True)   
        column.set_resizable(True)
        self.list.append_column(column)

        column = Gtk.TreeViewColumn('URL', Gtk.CellRendererText(), text=1)
        column.set_clickable(True)   
        column.set_resizable(True)
        column.set_visible(False)
        self.list.append_column(column)

        self.load_list_items()
        window = builder.get_object('main_window')
        window.set_title("Dropbox Link detector")
        window.show_all()

    def on_copy_clicked(self, button) :
        selection = self.list.get_selection()
        rows = selection.get_selected_rows()
        links = ""

        for row in rows[1] :
            iter2 = self.model.get_iter(row)
            links += self.model[iter2][1] + "\n"
        self.clipboard.set_text(links, -1)

    def on_statusIcon_activate(self, status) :
        if self.shown: 
            self.shown

    def on_refresh(self, button) :
        self.load_list_items()

    def on_destroy(self, window):
        #Gtk.main_quit()
        t = 1

    def on_close(self, button): 
        Gtk.main_quit()

    def get_filepaths(self, directory):
        file_paths = []  # List which will store all of the full filepaths.
        
        # Walk the tree.
        for root, directories, files in os.walk(directory):
            for filename in files:
                # Join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)  # Add it to the list.
        
        return file_paths  # Self-explanatory.
    
    #def on_tree_selection_changed(self,selection) :
    #    model, treeiter = selection.get_selected()
    #    if treeiter != None:
    #        print "You selected", model[treeiter][1]
    #        self.clipboard.set_text(model[treeiter][1], -1)

    def on_row_activated(self, tree, path, iter) :
        selection = self.list.get_selection()
        rows = selection.get_selected_rows()

        for row in rows[1] :
            iter2 = self.model.get_iter(row)
            print self.model[iter2][1]


    def load_list_items(self) :
        self.model.clear()        
        full_file_paths = self.get_filepaths(dirpath)

        listOfFiles = []
        for i in full_file_paths :
            process = subprocess.Popen(["/usr/bin/dropbox", "puburl", i], stdout=subprocess.PIPE)
            out, err = process.communicate()
            path = out[0:-1]
            filename = os.path.basename(out[0:-1])
            listOfFiles += [[i, filename, path]]
        for row in listOfFiles:
            self.model.append([row[1], row[2]])

if __name__ == "__main__":
    dirpath = None
    try :
        print os.environ['DROPLINKS_PATH']
    except :
        try :
            dirpath = os.environ['HOME'] + "/Dropbox/Public"
        except : 
            print "Unable to get fallback path"
    

    if dirpath is None :
        print "Error directory not defined"
    else :
        ListViewTestApp(dirpath)
        Gtk.main()
