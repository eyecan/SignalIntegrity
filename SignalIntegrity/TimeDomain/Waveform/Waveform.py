from TimeDescriptor import TimeDescriptor
from AdaptedWaveforms import AdaptedWaveforms

class Waveform(object):
    def __init__(self,x=None,y=None):
        if isinstance(x,Waveform):
            self.m_t=x.m_t
            self.m_y=x.m_y
        elif isinstance(x,TimeDescriptor):
            self.m_t=x
            if isinstance(y,list):
                self.m_y=y
            else:
                self.m_y=[0 for k in range(x.N)]
        else:
            self.m_t=None
            self.m_y=None
    def __len__(self):
        return len(self.m_y)
    def __getitem__(self,item):
        return self.m_y[item]
    def Times(self,unit=None):
        return self.m_t.Times(unit)
    def TimeDescriptor(self):
        return self.m_t
    def Values(self):
        return self.m_y
    def OffsetBy(self,v):
        self.m_y = [y+v for y in self.m_y]
        return self
    def DelayBy(self,d):
        return Waveform(self.TimeDescriptor().DelayBy(d),self.Values())
    def __add__(self,other):
        if self.TimeDescriptor() == other.TimeDescriptor():
            return Waveform(self.TimeDescriptor(),[self[k]+other[k] for k in range(len(self))])
        else:
            awf=AdaptedWaveforms([self,other])
            return awf[0]+awf[1]
    def __sub__(self,other):
        if self.TimeDescriptor() == other.TimeDescriptor():
            return Waveform(self.TimeDescriptor(),[self[k]-other[k] for k in range(len(self))])
        else:
            awf=AdaptedWaveforms([self,other])
            return awf[0]-awf[1]
    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)
    def __mul__(self,other):
        from SignalIntegrity.TimeDomain.Filters.FirFilter import FirFilter
        from SignalIntegrity.TimeDomain.Filters.WaveformTrimmer import WaveformTrimmer
        if isinstance(other,FirFilter):
            return other.FilterWaveform(self)
        elif isinstance(other,WaveformTrimmer):
            return other.TrimWaveform(self)
    def ReadFromFile(self,fileName):
        with open(fileName,"rU") as f:
            data=f.readlines()
            HorOffset=float(data[0])
            NumPts=int(data[1])
            SampleRate=float(data[2])
            Values=[float(v) for v in data[3:]]
        self.m_t=TimeDescriptor(HorOffset,NumPts,SampleRate)
        self.m_y=Values
        return self
    def WriteToFile(self,fileName):
        with open(fileName,"w") as f:
            td=self.TimeDescriptor()
            f.write(str(td.H)+'\n')
            f.write(str(td.N)+'\n')
            f.write(str(td.Fs)+'\n')
            for v in self.Values():
                f.write(str(v)+'\n')
        return self
    def __eq__(self,other):
        if self.TimeDescriptor() != other.TimeDescriptor():
            return False
        if len(self.Values()) != len(other.Values()):
            return False
        for k in range(len(self.Values())):
            if abs(self.Values()[k]-other.Values()[k])>1e-6:
                return False
        return True
    def __ne__(self,other):
        return not self == other

class WaveformFileAmplitudeOnly(Waveform):
    def __init__(self,fileName,td=None):
        if not td is None:
            HorOffset=td.H
            NumPts=td.N
            SampleRate=td.Fs
        else:
            HorOffset=0.0
            NumPts=0
            SampleRate=1.
        with open(fileName,'rb') as f:
            wf = [float(line) for line in f]
        if NumPts==0:
            NumPts=len(wf)
        else:
            if len(wf) > NumPts:
                wf = [wf[k] for k in range(NumPts)]
            else:
                NumPts=len(wf)
        Waveform.__init__(self,TimeDescriptor(HorOffset,NumPts,SampleRate),wf)