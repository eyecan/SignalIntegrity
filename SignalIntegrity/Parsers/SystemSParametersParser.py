from SignalIntegrity.SystemDescriptions import SystemSParametersNumeric
from SignalIntegrity.Parsers import SystemDescriptionParser
from SignalIntegrity.SParameterFiles import SParameters

class SystemSParametersNumericParser(SystemDescriptionParser):
    def __init__(self, f=None, args=None):
        SystemDescriptionParser.__init__(self, f, args)
    def SParameters(self):
        sd=self.SystemDescription()
        if not sd.CheckConnections():
            return
        spc=self.m_spc
        result = []
        for n in range(len(self.m_f)):
            for d in range(len(spc)):
                sd[sd.IndexOfDevice(spc[d][0])].pSParameters=spc[d][1][n]
            result.append(SystemSParametersNumeric(sd).SParameters())
        sf = SParameters(self.m_f, result)
        return sf