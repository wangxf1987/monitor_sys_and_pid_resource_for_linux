#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psutil
import csv
import datetime
import time

class monitor_linux_for_influxd():
   """
      monitor_linux_for_influxd
      2016-03-21
   """
   def __init__(self, pid, sleep_time=3):
      csv_path = 'MonitorData_%s.csv' % \
                 (str(datetime.datetime.now().\
                  strftime('%Y%m%d%H%M%S')))
      self.pid = pid
      self.pid_name = psutil.Process(pid).name()
      self.sleep_time = sleep_time

   def data_for_sys(self, interval=1):
      phymem = psutil.virtual_memory()
      phymem_list = [phymem.percent,\
                     str(int(phymem.used/1024/1024)),\
                     str(int(phymem.total/1024/1024))]

      return psutil.cpu_percent(interval),\
             phymem_list

   def iodata_for_sys(self):
      """get iops for read"""
      iodata_for_sys_old = str(psutil.disk_io_counters())
      read_count_old = iodata_for_sys_old[\
                       iodata_for_sys_old.find("=")+1\
                       :iodata_for_sys_old.find(",")]
      write_count_old = iodata_for_sys_old[\
                        iodata_for_sys_old.find("write_count=")+12\
                        :iodata_for_sys_old.find(", read")]

      read_bytes_old = iodata_for_sys_old[\
                       iodata_for_sys_old.find("read_bytes=")+11\
                       :iodata_for_sys_old.find(", write_bytes")]
      write_bytes_old = iodata_for_sys_old[\
                        iodata_for_sys_old.find("write_bytes=")+12\
                        :iodata_for_sys_old.find(", read_time=")]

      time.sleep(self.sleep_time)

      iodata_for_sys_new = str(psutil.disk_io_counters())
      read_count_new = iodata_for_sys_new[\
                       iodata_for_sys_new.find("=")+1\
                       :iodata_for_sys_new.find(",")]
      write_count_new = iodata_for_sys_new[\
                        iodata_for_sys_new.find("write_count=")+12\
                        :iodata_for_sys_new.find(", read")]

      read_bytes_new = iodata_for_sys_new[\
                       iodata_for_sys_new.find("read_bytes=")+11\
                       :iodata_for_sys_new.find(", write_bytes")]
      write_bytes_new = iodata_for_sys_new[\
                        iodata_for_sys_new.find("write_bytes=")+12\
                        :iodata_for_sys_new.find(", read_time=")]

      return (int(read_count_new)-int(read_count_old))/self.sleep_time,\
             (int(write_count_new)-int(write_count_old))/self.sleep_time,\
             ((int(read_bytes_new)-int(read_bytes_old))/1024/1024)/self.sleep_time,\
             ((int(write_bytes_new)-int(write_bytes_new))/1024/1024)/self.sleep_time
             
 
   def data_for_influxd(self, interval=1):
      pid_info = psutil.Process(self.pid)

      """get iops for read of the pid"""
      iodata_for_pid_old = str(pid_info.io_counters())
      read_count_old = iodata_for_pid_old[\
                       iodata_for_pid_old.find("=")+1\
                       :iodata_for_pid_old.find(",")]
      write_count_old = iodata_for_pid_old[\
                        iodata_for_pid_old.find("write_count=")+12\
                        :iodata_for_pid_old.find(", read")]

      read_bytes_old = iodata_for_pid_old[\
                       iodata_for_pid_old.find("read_bytes=")+11\
                       :iodata_for_pid_old.find(", write_bytes")]
      write_bytes_old = iodata_for_pid_old[\
                        iodata_for_pid_old.find("write_bytes=")+12\
                        :iodata_for_pid_old.find(")")]

      time.sleep(self.sleep_time)

      iodata_for_pid_new = str(pid_info.io_counters())
      read_count_new = iodata_for_pid_new[\
                       iodata_for_pid_new.find("=")+1\
                       :iodata_for_pid_new.find(",")]
      write_count_new = iodata_for_pid_new[\
                        iodata_for_pid_new.find("write_count=")+12\
                        :iodata_for_pid_new.find(", read")]

      read_bytes_new = iodata_for_pid_new[\
                       iodata_for_pid_new.find("read_bytes=")+11\
                       :iodata_for_pid_new.find(", write_bytes")]
      write_bytes_new = iodata_for_pid_new[\
                        iodata_for_pid_new.find("write_bytes=")+12\
                        :iodata_for_pid_new.find(")")]
      
      iodata_pid_list = [(int(read_count_new)-int(read_count_old))/self.sleep_time,\
                         (int(write_count_new)-int(write_count_old))/self.sleep_time,\
                         ((int(read_bytes_new)-int(read_bytes_old))/1024/1024)/self.sleep_time,\
                         ((int(write_bytes_new)-int(write_bytes_new))/1024/1024)/self.sleep_time]

      pid_vms_mem = str(pid_info.memory_info())
      pid_vms_mem = pid_vms_mem[\
                    pid_vms_mem.find("vms=")+4:\
                    pid_vms_mem.find(", shared")]

      return pid_info.cpu_percent(interval),\
             int(pid_vms_mem)/1024/1024,\
             iodata_pid_list

   def show_and_record_data(self):
      cpu_percent_sys,\
      phymem_list_sys = self.data_for_sys()

      iops_read,\
      iops_write,\
      BW_read,\
      BW_write = self.iodata_for_sys()

      cpu_percent_pid,\
      memory_used_pid,\
      iodata_pid_list = self.data_for_influxd()
      
      """show data in """
      print "*-"*32+"\n"+" "*23+"DATA INFO\n"
      print "System monitoring data\n"+"-"*24
      print "CPU percent(total): %s%%\n" %\
             str(cpu_percent_sys) + \
            "Used Memory Percent(total): %s%%\n" %\
             str(phymem_list_sys[0]) + \
            "Used Memory Size(total): %sMB\n" %\
             str(phymem_list_sys[1]) + \
            "Total Memory Size(total): %sMB\n" %\
             str(phymem_list_sys[2]) +\
            "IOPS_read: %s\n" %\
             str(iops_read) +\
            "IOPS_write: %s\n" %\
             str(iops_write) +\
            "BW_read: %sMbps\n" %\
             str(BW_read) +\
            "BW_write: %sMbps" %\
             str(BW_write)
            
      print "\npid(%s) monitoring data\n" % \
             self.pid_name + "-"*24
      print "pid_CPU_percent: %s%%\n" %\
             str(cpu_percent_pid) +\
            "pid_mem_used: %sMB\n" %\
             str(memory_used_pid/1024/1204) +\
            "pid_IOPS_read: %s\n" %\
             str(iodata_pid_list[0])+\
            "pid_IOPS_write: %s\n" %\
             str(iodata_pid_list[1])+\
            "pid_BW_read: %sMbps\n" %\
             str(iodata_pid_list[2])+\
            "pid_BW_write: %sMbps\n" %\
             str(iodata_pid_list[3])
      print " "*27+"END"+"\n"+"*-"*32
             
      """"""      
      
if __name__ == '__main__':
    m = monitor_linux_for_influxd(20365)
    m.show_and_record_data()
