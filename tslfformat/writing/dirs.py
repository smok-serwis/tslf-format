# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import os.path
import os
import io
import warnings
from tslfformat.writing.single_file import SingleFileWriter

logger = logging.getLogger(__name__)


class TSLFDirectory(object):
    """
    Manage a bunch of TSLF files

    Should be a singleton per path
    """

    def __init__(self, path):
        """
        Initialize a database (directory of TSLF files)

        If directory does not exist, it will be created.

        This does not return until everything is prepared, and
        possibly

        :param path: path to direct
        """
        self.path = path
        self.done_files = []        #: list of files that won't be written to anymore, and can be synced
        self.leader_name = u''      #: name of current file that is being written to
        self.leader = None          #: current SingleFileWriter. Kept here for rotate()

        if not os.path.exists(path):        # if directory does not exist
            os.mkdir(path)

        file_name_list = os.listdir(path)
        if len(file_name_list) == 0:            # if directory empty
            self.leader_name = u'0'
        else:                                   # not really
            as_ints = []

            for fname in file_name_list:
                try:
                    as_ints.append(int(fname))
                except ValueError:
                    warnings.warn(u'Non-TSLF file %s found' % (fname, ))
                    continue

            as_ints.sort()

            self.leader_name = six.text_type(as_ints.pop()) # the leader
            self.done_files = [six.text_type(n) for n in as_ints]

        self.leader = SingleFileWriter(os.path.join(path, self.leader_name))

    def rotate(self):
        """
        Rotate TSLF files. Return new leader.

        Finish writing current leader. Sync it. Move it to done_files. Create a new leader.

        This may result in substantial amount of disk I/O. This blocks until everything is done.
        Do not conduct writing any I/O on this directory or files inside in the meantime.
        :return: new leader (SingleFileWriter)
        """

        # Close and move old leader
        old_leader_name = self.leader_name
        self.leader.close()
        self.as_done.append(old_leader_name)

        # Generate new leader
        self.leader_name = six.text_type(int(old_leader_name)+1)
        self.leader = SingleFileWriter(self.leader_name)

        return self.leader


