#!/usr/bin/python
# python -m pip install watchdog==0.8.2
import os
import errno
import re
import sys
import traceback
import collections
import shutil
import glob
import time
import string
import six
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SOURCE = "/Users/a2big/temp/source_dir"
DESTINATION = "/Users/a2big/temp/dest_dir"


class FileManager:
    def __init__(self, src_filename, dst_filename):
        self.src_filename = src_filename
        self.dst_filename = dst_filename
        print("FileManager src_path - %s." % self.src_filename)
        print("FileManager dst_path - %s." % self.dst_filename)

    def copyFile(self, src, dest):
        try:
            shutil.copy(src, dest)
        # eg. src and dest are the same file
        except shutil.Error as e:
            print('Error: %s' % e)
        # eg. source or destination doesn't exist
        except IOError as e:
            print('Error: %s' % e.strerror)

    def make_sure_path_exists(self, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def get_filenames(self, path):
        directory = path + "/*"
        names = glob.glob(directory)
        return names

    def recursive_overwrite(self, src, dest, ignore=None):
        if os.path.isdir(src):
            if not os.path.isdir(dest):
                os.makedirs(dest)
            files = os.listdir(src)
            if ignore is not None:
                ignored = ignore(src, files)
            else:
                ignored = set()
            for f in files:
                if f not in ignored:
                    self.recursive_overwrite(os.path.join(src, f),
                                             os.path.join(dest, f),
                                             ignore)
        else:
            print("Copy " + dest)
            shutil.copyfile(src, dest)

    def mkdirnotex(self, filename):
        folder = os.path.dirname(filename)
        if not os.path.exists(folder):
            os.makedirs(folder)

    def _mkdir_recursive(self, path):
        sub_path = os.path.dirname(path)
        if not os.path.exists(sub_path):
            self._mkdir_recursive(sub_path)
        if not os.path.exists(path):
            os.mkdir(path)

    # def doCopy(src_filename, dst_filename):
    def doCopy(self):
        # print "Copy " + dst_filename
        head, tail = os.path.split(self.dst_filename)
        self._mkdir_recursive(head)

        if os.path.isdir(self.src_filename):
            self.recursive_overwrite(self.src_filename, self.dst_filename)
        else:
            # print "Copy " + src_filename + " " + dst_filename
            print("Copy " + self.dst_filename)
            self.copyFile(self.src_filename, self.dst_filename)
            time.sleep(0.1)  # sleep during 100ms


class Watcher:
    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, SOURCE, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print ("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            if six.PY2:
                new_str = string.replace(event.src_path, SOURCE, DESTINATION)
            else:
                new_str = event.src_path.replace( SOURCE, DESTINATION)
            print("Received created src_path - %s." % event.src_path)
            print("Received created dst_path - %s." % new_str)
            f = FileManager(event.src_path, new_str)
            f.doCopy()

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            if six.PY2:
                new_str = string.replace(event.src_path, SOURCE, DESTINATION)
            else:
                new_str = event.src_path.replace( SOURCE, DESTINATION)
            print("Received created src_path - %s." % event.src_path)
            print("Received created dst_path - %s." % new_str)
            f = FileManager(event.src_path, new_str)
            f.doCopy()


if __name__ == '__main__':
    w = Watcher()
    w.run()

