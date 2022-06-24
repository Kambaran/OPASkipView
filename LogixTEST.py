from types import NoneType
from pylogix import PLC

"""    prop = comm.GetDeviceProperties()
    print("Device ",prop)

    for i in [0,3]:
        print ("Module ", i,comm.GetModuleProperties(i))
    print(comm.GetPLCTime().Value)

    programs = comm.GetProgramsList()
    print(programs.Value)

    tags = comm.GetTagList()
    for t in tags.Value:
        print("Tag:", t.TagName, t.DataType)
"""


class PLCRead(PLC):
    def __init__(self, parent=None):
        super(PLC, self).__init__()

        self.IPAddress = '192.168.100.200'
        self._tags = []


    def ReadTags(self):        
        if self.GetTagList().Value is not NoneType:
            for t in self.GetTagList().Value:
                self._tags.append(f"Nazwa tagu:  {t.TagName} |  Typ zmiennej:  {t.DataType}")
                return self._tags
            else:
                self.tags = ['Failed to load tags']
                return self._tags

    def __call__(self):
        return self._tags

"""
    def ReadTags(self):
        with PLC(self.PLCAddress) as driver:
            if driver.GetTagList().Value is not NoneType:
                for t in driver.GetTagList().Value:
                    self._tags.append(f"Nazwa tagu:  {t.TagName} |  Typ zmiennej:  {t.DataType}")
            else:
                pass
            return self._tags
            #if driver.GetTagList().Value is not NoneType:
            #    self._tags = [tags for tags in driver.GetTagList().Value]
            #    print('works')
            #    return self._tags
            #else:
            #    pass
    
    def ReadTagValue(self):
        with PLC(self.PLCAddress) as driver:
            if driver.GetTagList().Value is not NoneType:
                self._tag_value = driver.Read(self._tag_name)
                return self._tag_value
            else:
                pass

    def __call__(self):
        return self._tags, self._tag_value

"""
if __name__ == '__main__':
    x = PLCRead()
    pass
