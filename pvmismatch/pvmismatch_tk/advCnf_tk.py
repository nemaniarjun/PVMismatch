# -*- coding: utf-8 -*-
"""
Created on Aug 18, 2012

@author: mmikofski
"""

from six.moves.tkinter_constants import W, E, RIGHT
from six.moves.tkinter import Frame, Label, Button, DoubleVar, Entry, IntVar
import six.moves.tkinter_font as tkFont

PVAPP_TXT = 'PVmismatch'
INTEGERS = '0123456789'
FLOATS = '.' + INTEGERS


class AdvCnf_tk(Frame):
    """
    classdocs
    """

    def __init__(self, pvapp, top):
        """
        Constructor
        """
        self.pvapp = pvapp
        Frame.__init__(self, top, name='advCnf')
        self.pack()
        self.focus_set()  # get the focus
        self.grab_set()  # make this window modal
        top.resizable(False, False)  # not resizable in x or y
        top.title(PVAPP_TXT)  # set title bar
        top.protocol("WM_DELETE_WINDOW", self.quit)  # close window to quit
        CAPTION_FONT = tkFont.nametofont('TkCaptionFont')  # font for titles

        self.class_tk_location = ".advCnfTop.advCnf."

        cellnum = self.cellnum = IntVar(self, name='cellnum')
        current_cell = cellnum.get()
        total_cells = pvapp.numCells.get()
        total_mods = pvapp.numMods.get()
        current_pos = current_cell // total_cells
        temp1 = self.temp1 = pvapp.pvSys.pvmods[current_pos // total_mods][current_pos % total_mods]
        temp = self.temp = temp1.pvcells[current_cell % total_cells]        
        
        self.lst = lst = [
            ["Rs", "{:10.4e}", temp.Rs, 'Rs [Ohms]', 'rsEntry', 'min 0', 'Invalid series resistance!'],
            ["Rsh", "{:10.4f}", temp.Rsh, 'Rsh [Ohms]', 'rshEntry', 'min 0', 'Invalid shunt resistance!'],
            ["Isat1_T0", "{:10.4e}", temp.Isat1_T0, 'Isat1_T0 [A]', 'isat1_T0Entry', 'min 0', 'Invalid diode-1 saturation current!'],
            ["Isat2", "{:10.4e}", temp.Isat2, 'Isat2 [A]', 'isat2Entry', 'min 0', 'Invalid diode-2 saturation current!'],
            ["Aph", "{:10.4f}", temp.Aph, 'Aph', 'aphEntry', 'min 0', 'Invalid photo-generated current coefficient!'],
            ["Isc0_T0", "{:10.4f}", temp.Isc0_T0, 'Isc0_T0 [A]', 'isc01_T0Entry', 'min 1', 'Invalid short circuit current!'],
            ["Tcell", "{:10.4f}", temp.Tcell, 'Tcell [K]', 'tcellEntry', 'min 0', 'Invalid cell temperature!'],
            ["aRBD", "{:10.4e}", temp.aRBD, 'aRBD', 'aRBDEntry', 'min 0', 'Invalid reverse bias breakdown coefficient (aRBD)!'],
            ["VRBD", "{:10.4f}", temp.VRBD, 'VRBD [V]', 'vRBDEntry', 'min 0', 'Invalid reverse bias breakdown voltage!'],
            ["nRBD", "{:10.4f}", temp.nRBD, 'nRBD', 'nRBDEntry', 'min 0', 'Invalid reverse bias breakdown exponent (nRBD)!'],
            ["Vbypass", "{:10.4f}", temp1.Vbypass, 'Vbypass [V]', 'vbypassEntry', 'min 0', 'Invalid bypass diode trigger voltage!'],
            ["cellArea", "{:10.4f}", temp1.cellArea, 'cell area [cm^2]', 'cellAreaEntry', 'min 0', 'Invalid cell area!'],
            ]


        # must register vcmd and invcmd as Tcl functions
        vcmd = (self.register(self.validateWidget),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        invcmd = (self.register(self.invalidWidget),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        # layout
        Label(self,
              text='Advanced Configuration',
              font=CAPTION_FONT).grid(row=0, columnspan=3, sticky=W)

        # cellnum, Rs, Rsh, Isat1_T0
        Label(self, text='cell #').grid(row=1, sticky=W)

        # Variables set and show on Tk
        for pos, i in enumerate(lst):
            # Create Variable
            temp_var = DoubleVar(self, name=i[0])
            # Set using format string
            temp_var.set(i[1].format(i[2]))
            # Now self.i[0] => self.Rs .. etcs
            setattr(self, i[0], temp_var)
            # Create Label
            Label(self, text=i[3]).grid(row=pos+2, sticky=W)
            # Create entry Box
            Entry(self, textvariable=temp_var, width=12, justify=RIGHT,
                  name=i[4], validatecommand=vcmd,
                  invalidcommand=invcmd, validate='all').grid(row=pos+2, column=1)

        Button(self, text='OK',
               command=self.okay).grid(row=len(lst)+2, sticky=(E + W))
        Button(self, text='Cancel',
               command=self.quit).grid(row=len(lst)+2, column=1, sticky=(E + W))


    def okay(self):
        # get the new values

        valid_conts = self.pvapp.validationConstants["advCnf"]
        messagetext = self.pvapp.messagetext

        kwargs = {}
        for i in self.lst:
            temp = self.getattr(i[0]).get()
            kwargs[i[0]] = temp
            
            if i[5].startswith("min"):
                if not int(i[5][-1]) < temp <= valid_conts[i[0]]:
                    self.pvapp.msgtext.set(i[6])
                    self.bell()
                    return
            
            if i[5].startswith("max"):
                if not int(i[5][-1]) > temp >= valid_conts[i[0]]:
                    self.pvapp.msgtext.set(i[6])
                    self.bell()
                    return 

        # update PVconstants
        self.pvapp.msgtext.set(messagetext["pvapplication"]["Ready"])
        pvapp = self.pvapp

        self.temp.update(
            **kwargs
        )  # cellArea, Vbypass updated by module
        # update PVapplication_tk
        self.pvapp.updatePVsys(pvapp.pvSys)
        self.pvapp.updateIVstats()
        self.quit()

#    Validation substitutions
#    %d  Type of action: 1 for insert, 0 for delete, or -1 for focus, forced or
#        textvariable validation.
#    %i  Index of char string to be inserted/deleted, if any, otherwise -1.
#    %P  The value of the spinbox should edition occur. If you are configuring
#        the spinbox widget to have a new textvariable, this will be the value
#        of that textvariable.
#    %s  The current value of spinbox before edition.
#    %S  The text string being inserted/deleted, if any. Otherwise it is an
#        empty string.
#    %v  The type of validation currently set.
#    %V  The type of validation that triggered the callback (key, focusin,
#        focusout, forced).
#    %W  The name of the spinbox widget.

# TODO: Fix these functions so that delete and overwrite work

    def validateWidget(self, *args):
        # W = Tkinter.W = 'w' is already used, so use W_ instead
        (d, i, P, s, S, v, V, W_) = args  # @UnusedVariable # IGNORE:W0612
        print("OnValidate:",)
        print("d={}, i={}, P={}, s={}, S={}, v={}, V={}, W={}".format(*args))

        if W_.startswith(self.class_tk_location):
            W_ = W_[len(self.class_tk_location):]
            if W_ == "cellnumEntry":
                valType = INTEGERS
                valTest = lambda val: int(val)  # IGNORE:W0108
            else:
                valType = FLOATS
                valTest = lambda val: float(val)  # IGNORE:W0108
        else:
            return False
        
        w = self.nametowidget(W_)
        w.config(validate=v)
        if S in valType:
            try:
                valTest(P)
            except ValueError:
                return False
            return True
        else:
            return False

    def invalidWidget(self, *args):
        (d, i, P, s, S, v, V, W_) = args  # @UnusedVariable # IGNORE:W0612
        print("OnInvalid: ",)
        print("d={}, i={}, P={}, s={}, S={}, v={}, V={}, W={}".format(*args))
        errText = None
        for i in self.lst:
            if W_ == i[4]:
                errText = i[6] 
                break
        if not errText:
            errText = 'Unknown widget!'
        w = self.nametowidget(W_)
        w.config(validate=v)
        self.pvapp.msgtext.set(errText)
        self.bell()
