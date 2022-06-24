import sys
sys.path.append('..')

from pylogix import PLC

def getDevices():
    '''
    Get all of the devices on the network
    '''
    with PLC() as comm:
        comm.ProcessorSlot = 2
        return comm.Discover()

def audit_plcs(devices):
    '''
    Parse out any devices that are a PLC, then audit
    the rack for all of the modules
    '''
    for d in devices.Value:
        if d.DeviceID == 14:
            audit_rack(d)
        else:          
            f.write('%s %s\n' %(d.ProductName,  d.Revision))
            
def audit_rack(plc):
    '''
    Query each slot for a module
    '''
    with PLC() as c:
        c.IPAddress = plc.IPAddress
        f.write('%s - %s\n' %(plc.IPAddress, plc.ProductName))
        for i in range(17):
            x = c.GetModuleProperties(i)
            f.write('\tSlot %d:%s  rev:%s\n' %(i, x.ProductName, x.Revision))
        f.write('')

devices = getDevices()
with open('network_audit.txt' , 'w') as f:
    audit_plcs(devices)