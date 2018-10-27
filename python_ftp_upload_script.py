#!python3
# Author: Kuba Streit - streit <at> robotikabrno.cz
# Licence: MIT

from sys import version
#print(version)

from ftplib import FTP, error_perm
from os import listdir as ls
from os.path import getsize, isdir
from os import get_terminal_size
from time import perf_counter, gmtime, strftime

host = 'YOUR-FTP-URL'
user = 'YOUR-USER-NAME'
password = 'YOUR-PASSWORD'

class Progress:
    time = perf_counter
    units = [(1024**e, u) for e, u in ((0, '  '), (1, 'ki'), (2, 'Mi'), (3, 'Gi'), (4, 'Ti'))]
    def __init__(self, file, block_size = 8192, terminal_width = 0):
        self.file = file
        self.block_size = block_size
        self.size = getsize(file)
        
        for i in range(1, len(Progress.units)):
            if self.size < (100 * Progress.units[i][0]):
                self.divide, self.unitr = Progress.units[i-1]
                break
        self.next_print = 0
        self.print_step = self.size / 1000
        self.start_time = Progress.time()
        self.last_time = self.start_time
        self.sended = 0
        self.last_sended = 0
        if terminal_width <= 0:
            try:
                self.terminal_width = get_terminal_size()[0] if terminal_width == 0 else terminal_width
            except ValueError:
                self.terminal_width = 80
        
                
    def __call__(self, v = None, final = False):
        if final:
            self.sended = self.size
        else:
            self.sended += self.block_size
        if self.sended < self.next_print:
            return
        self.next_print += self.print_step
        percentage = self.sended / self.size
        if percentage > 1:
            percentage = 1
        bar_width = get_terminal_size()[0] if self.terminal_width == -1 else self.terminal_width
        time = Progress.time()
        speed = (self.sended - self.last_sended) / (time - self.last_time)
        self.last_sended = self.sended
        self.last_time = time
        avg_speed = self.sended / (time - self.start_time)
        remaining = (self.size - self.sended) / avg_speed
        if final:
            speed = avg_speed
        for i in range(1, len(Progress.units)):
            if speed < (8 * Progress.units[i][0]):
                speed /= Progress.units[i-1][0]
                unit = Progress.units[i-1][1] + 'B/s'
                break
        bar_width -= 40
        if bar_width > 6:
            bar = '|' + (int(percentage * bar_width) * '=').ljust(bar_width) + '| '
        else:
            bar = ''
        print('{}{:5.1f} % ({:8.3f} {}) {}'.format(
            bar,
            100.0*percentage,
            speed, unit,
            strftime('%H:%M:%S', gmtime(remaining))
            ), end = '\r')

    def finalize(self):
        self(final = True)
        print('\n')

with FTP(host, user, password) as ftp:
    #print(ftp.getwelcome())
    files = ls()
    fcnt = 0
    for file in files:
        fcnt += 1
        if isdir(file):
            print('Skipping directory', file)
            continue
        print('Sending file {}/{}: {}'.format(fcnt, len(files), file))
        progress = Progress(file)
        with open(file, 'rb') as f:
##            try:
##                ftp.delete(file)
##            except error_perm as e:
##                print('deletion failed:', e)
            try:
                ftp.storbinary('STOR ' + file, f, progress.block_size, progress)
            except error_perm as e:
                print('\n', e)
            finally:
                progress.finalize()
