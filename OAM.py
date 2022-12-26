#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 17:09:09 2022

@author: colinbehr
"""



import re

######################################################################
# The OAM class defines the OAM model. 
class OAM():
    def __init__(self, debug=False):
        self.debug = debug	# Run time output
        self.pc = 1		# Program counter
        self.ar = '?'		# Address register
        self.ir = '?'		# Instruction register
        self.acc = '?'		# Accumulator
        self.b = '?'		# B register
        self.mem = []		# Memory
        self.labels = {'stdin':0, 'stdout':0}	# Labels, including I/O 

    # The verbose() method toggles the debug variable
    def verbose(self):
        self.debug = not self.debug

    # The run() method initalizes the machine 
    def run(self):
        self.pc = 1
        self.ar = '?'
        self.ir = '?'
        self.acc = '?'
        self.b = '?'
        while self.pc > 0:
            self.fetch()
            self.increment()
            self.execute()
        if self.debug:
            print("Processing halted.")

    # The fetch() method implements the fetch cycle.
    def fetch(self):
        self.ar = self.pc
        self.ir = self.read()
        if self.debug:
            print("Fetch: AR = {} IR = {}".format(self.ar, ' '.join(self.ir)))

    # The increment() method implements the increment cycle.
    def increment(self):
        self.pc = self.pc + 1
        if self.debug:
            print("  Increment: PC = {}".format(self.pc))

    # The execute() method implements the execute cycle, dispatching
    # to the appropriate method as per the first part of the
    # IR. Returns a Boolean indicating whether execution should
    # continue.
    def execute(self):
        # Check for a match, report an issue
        if self.debug:
            print("  Execute: IR = '{}'".format(self.ir))
        try:
            exec('self.' + self.ir[0] + '()')
        except:
            if self.debug:
                print("Abort: ill-formed instruction IR = '{}'".format(self.ir))
            self.pc = 0

    # The resolve() method resolves a reference to a memory location,
    # which may be an integer or a reference label, such as may be
    # found in an instruction, and returns an int.
    def resolve(self, address):
        if address in self.labels:
            return self.labels[address]
        return int(address)
        

    # The read() method returns a value from the memory location
    # specified by the AR. If the AR value is 0, it returns a value
    # from keyboard input. If the AR value is a label, it returns the
    # value from memory at the label's reference. Otherwise, if the AR
    # value is a number, it returns the value of memory at that
    # location. If the memory location does not exist, it returns '?'.
    def read(self):
        if self.ar == 0:
            return input('Input: ')
        elif self.ar in self.labels:
            return self.mem[self.labels[self.ar]]
        elif self.ar <= len(self.mem):
            return self.mem[self.ar]
        else:
            return('?')

    # The write() copies the value a value from the ACC into the
    # location specified by the AR. If the AR value is 0, it prints
    # the value to the screen. If the AR value is a label, it copies
    # the value from the ACC into the label's reference. Otherwise, if
    # the AR value is a number, it copies the value from the ACC to
    # memory at that location.
    def write(self):
        if self.ar not in range(len(self.mem)):      
            self.mem.append('?')
            self.write()
        elif self.ar == 0:
            print('Output: {}'.format(self.acc))
        elif self.ar in self.labels:
            self.labels[self.ar] = self.acc
        else:
            self.mem[self.ar] = self.acc

    # The add() method adds the B register to ACC and stores the
    # result in ACC.
    def add(self):
        self.ar = self.resolve(self.ir[1])
        self.b = self.read()
        self.acc = int(self.acc) + int(self.b)

    # The sub() method subtracts the B register from ACC and stores
    # the result in ACC.
    def sub(self):
        self.ar = self.resolve(self.ir[1])
        self.b = self.read()
        self.acc = int(self.acc) -  int(self.b)
        

    # The mlt() method multiplies the B register with ACC and stores
    # the result in ACC.
    def mlt(self):
        self.ar = self.resolve(self.ir[1])
        self.b = self.read()
        self.acc = int(self.acc) * int(self.b)

    # The div() method divides the ACC with the B register and stores
    # the result in ACC.
    def div(self):
       self.ar = self.resolve(self.ir[1])
       self.b = self.read()
       self.acc = int(self.acc) // int(self.b)

    # The set() method sets the ACC to the specified value from the
    # IR.
    def set(self):
        self.acc = int(self.ir[1])

    # The neg() method inverts the sign of the ACC.
    def neg(self):
        self.acc = int(self.acc) * -1

    # The inc() method adds 1 to the ACC.
    def inc(self):
        self.acc = int(self.acc) + 1

    # The dec() method subtracts 1 from the ACC.
    def dec(self):
        self.acc = int(self.acc) - 1

    # The lda() method sets the AR to the address from the IR and
    # reads the corresponding value from memory into ACC. 
    def lda(self):
        self.ar = self.resolve(self.ir[1])
        self.acc = self.read()

    # The sta() method sets the AR to the address from the IR and
    # stores the value of ACC into the corresponding value in
    # memory.
    def sta(self):
        self.ar = self.resolve(self.ir[1])
        self.write()

    # The br() method sets the PC to the specified value (-1 to
    # account for intervening increment phase).
    def br(self):
        self.pc = self.resolve(self.ir[1])

    # The brp() method sets the PC to the specified value (-1 to
    # account for intervening increment phase) if and only if ACC > 0.
    def brp(self):
        if int(self.acc) > 0:
            self.pc = self.resolve(self.ir[1])

    # The brp() method sets the PC to the specified value (-1 to
    # account for intervening increment phase) if and only if ACC ==
    # 0.
    def brz(self):
        if int(self.acc) == 0:
            self.pc = self.resolve(self.ir[1])
        
    # The bri() method sets the PC to the value of memory at the
    # location referenced. 
    def bri(self):
        self.ar = self.resolve(self.ir[1])
        self.pc = self.resolve(self.read())

    # The brs() method stores the PC value in the memory location
    # referenced and then branches to one beyond that location
    def brs(self):
        self.acc = str(self.pc)
        self.ar = self.resolve(self.ir[1])
        self.write()
        self.pc = self.ar + 1

    # The hlt() method stops the machine by setting the PC to 0.
    def hlt(self):
        self.pc = 0

    # The load(filename) method takes a file of OAM machine/assembly
    # code, initializes the OAM memory and label reference table, and
    # loads the contents of the file into memory starting at location
    # 1.
    def load(self, filename):
        input_file = open(filename)
        count = 1
        self.mem.append('?')
        for line in input_file:
            if line == '\n' or line.startswith('#'):
                continue
            else:
               line = line.strip()
               com = re.match("(?:[\d]+[.]\s+)?([a-zA-Z]+[,]\s+)?([a-zA-Z]{2,5}[,]?)\s*(\w+)?", line)
               if com.group(1):
                   match = re.match('([a-zA-Z]+)', com.group(1))
                   self.labels[match.group(0)] = count
               if com == None:
                   continue
               if com.group(3):
                   self.acc = ((com.group(2).lower(), com.group(3)))
                   self.ar = count
                   self.write()
               else:
                   self.acc = ((com.group(2).lower(),))
                   self.ar = count
                   self.write()
               count = count + 1
        if self.debug:
            print(str(count-1) + ' instructions loaded successfully')

    # The dump() method prints out a representation of the state of
    # the machine, followed by whatever is in memory and the label
    # references.
    def dump(self):
        state = 'State:' + 'PC='+str(self.pc)+': ' + 'ACC='+str(self.acc) + ':' +'B='+ str(self.b)+';' +'AR='+str(self.ar)+';'+'IR='+ str(self.ir) +'\n'
        memory = 'Memory: ' +'\n'
        for i in range(len(self.mem)):
            memory = memory + '  ' + str(i) + ': ' + str(self.mem[i]) + '\n'
        
        ref = 'Reference Table: ' + '\n'
        for key, value in self.labels.items():
            ref = ref+ '  ' + str(key) + ': ' + str(value) + '\n'
    
        print(state + memory + ref)