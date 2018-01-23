import unittest
import SignalIntegrity as si
from numpy import matrix
import math
import cmath
from numpy import linalg
from numpy import array
import os
from TestHelpers import *

class TestImpedanceProfile(unittest.TestCase,SParameterCompareHelper):
    def testImpedanceProfileCable(self):
        sp = si.sp.SParameterFile('cable.s2p',50.)
        ip = si.ip.ImpedanceProfile(sp,100,2)
        Z0 = 50.
        Zc = [-Z0*(rho+1.)/(rho-1) for rho in ip]
        """
        import matplotlib.pyplot as plt
        plt.plot(Zc)
        plt.show()
        """
        pass
    def testImpedanceProfileContrived(self):
        N=1000
        f=[20.e9*n/N for n in range(N+1)]
        Td=1./(2.*f[N])
        gamma=[1j*2.*math.pi*fe*Td for fe in f]
        Zc = [50.,55.,50.,45.,60.,52.,50.,50.,50.]
        Z0=50.
        rho = [(Z-Z0)/(Z+Z0) for Z in Zc]
        Gsp=[]
        for n in range(N+1):
            T = [si.cvt.S2T(si.dev.IdealTransmissionLine(rho[m],gamma[n])) for m in range(len(rho))]
            tacc=matrix([[1.,0.],[0.,1.]])
            for m in range(len(rho)):
                tacc=tacc*matrix(T[m])
            G=si.cvt.T2S(tacc.tolist())
            Gsp.append(G)
        sp = si.sp.SParameters(f,Gsp,Z0)
        ip = si.ip.ImpedanceProfile(sp,len(Zc),1)
        Zc2 = [-Z0*(rho+1.)/(rho-1) for rho in ip]
        """
        import matplotlib.pyplot as plt
        plt.plot(Zc)
        plt.show()
        """
#       print Zc2 # should be equal to Zc
        difference = linalg.norm(array(Zc2)-array(Zc))
        self.assertTrue(difference<1e-4,'contrived impedance profile incorrect')
    def testCableDeembed(self):
        sp = si.sp.SParameterFile('cable.s2p',50.)
        ip = si.ip.ImpedanceProfile(sp,6,1)
        Z0 = 50.
        Zc = [-Z0*(rho+1.)/(rho-1) for rho in ip]
        """
        import matplotlib.pyplot as plt
        plt.plot(Zc)
        plt.show()
        """
        spls=ip.SParameters(sp.f())
        spls.WriteToFile('cableLeftSide.s2p')
        ip = si.ip.ImpedanceProfile(sp,6,2)
        Zc = [-Z0*(rho+1.)/(rho-1) for rho in ip]
        """
        import matplotlib.pyplot as plt
        plt.plot(Zc)
        plt.show()
        """
        sprs=ip.SParameters(sp.f())
        sprs.WriteToFile('cableRightSide.s2p')
        dp = si.p.DeembedderNumericParser(sp.f())
        dp.AddLines(['unknown ?1 2',
                     'device L 2 file cableLeftSide.s2p',
                     'device R 2 file cableRightSide.s2p',
                     'port 1 L 1 2 R 1',
                     'connect L 2 ?1 1',
                     'connect R 2 ?1 2',
                     'system file cable.s2p'])
        cd = dp.Deembed()
        fileName='cableDeembedded.s2p'
        if not os.path.exists(fileName):
            cd.WriteToFile(fileName)
            self.assertTrue(False,fileName + 'does not exist')
        regression = si.sp.SParameterFile(fileName,50.)
        self.assertTrue(self.SParametersAreEqual(cd,regression,0.001),self.id()+'result not same')
    def AssembleLine(self,Zc):
        netListLine=[]
        td=si.td.wf.TimeDescriptor(0,100,20e9)
        for (z,e) in zip(Zc,range(len(Zc))):
            netListLine.append('device T'+str(e)+' 2 tline zc '+str(z)+' td '+str(1/td.Fs/2*4))
        for e in range(1,len(Zc)):
            netListLine.append('connect T'+str(e-1)+' 2 T'+str(e)+' 1')
        netListLine.append('device R1 1 R 50')
        netListLine.append('connect T'+str(len(Zc)-1)+' 2 R1 1')
        netListLine.append('port 1 T0 1')
        sp=si.p.SystemSParametersNumericParser(f=td.FrequencyList()).AddLines(netListLine).SParameters()
        return sp
    def testAssembled(self):
        spDict=dict()
        Zc = [50.,55.,52.,45.,60.]
        for e in range(len(Zc)):
            ZSingle=[50 for _ in Zc]
            ZSingle=[Zc[e] for _ in range(len(Zc))]
            ZSingle=[ZSingle[e] if i>=e else 50 for i in range(len(Zc))]
            spDict[str(e)]=self.AssembleLine(ZSingle)
        spDict['all']=self.AssembleLine(Zc)

        plotthem=True
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        td=spDict[str(e)].FrequencyResponse(1,1).ImpulseResponse().td
        impulsewf=si.td.wf.Waveform(td,[1 if abs(t)<= 25e-12 else 0 for t in td.Times()])
        for e in range(len(Zc)):
            wf=spDict[str(e)].FrequencyResponse(1,1).ImpulseResponse()+impulsewf
            plt.plot(wf.Times('ns'),wf.Values(),label=str(e))
        wf=spDict['all'].FrequencyResponse(1,1).ImpulseResponse()
        plt.plot(wf.Times('ns'),wf.Values(),label='all')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(True)
        #self.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        for e in range(len(Zc)):
            wf=(spDict[str(e)].FrequencyResponse(1,1).ImpulseResponse()+impulsewf).Integral(addPoint=True,scale=False)
            plt.plot(wf.Times('ns'),wf.Values(),label=str(e))
        wf=(spDict['all'].FrequencyResponse(1,1).ImpulseResponse()+impulsewf).Integral(addPoint=True,scale=False)
        plt.plot(wf.Times('ns'),wf.Values(),label='all')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(True)
        #self.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
#         for e in range(len(Zc)):
#             wf=spDict[str(e)].FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
#             plt.plot(wf.Times('ns'),wf.Values(),label=str(e))
        wf=spDict['all'].FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
        plt.plot(wf.Times('ns'),wf.Values(),label='all')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(True)
        #self.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
#         for e in range(len(Zc)):
#             wf=spDict[str(e)].FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
#             plt.plot(wf.Times('ns'),wf.Values(),label=str(e))
        wf=spDict['all'].FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
        wfApprox=spDict['all'].FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
        for k in range(len(wf)):
            wf[k]=50*(1+wf[k])/(1-wf[k])
            wfApprox[k]=50+2*50*wfApprox[k]
        plt.plot(wf.Times('ns'),wf.Values(),label='Z estimated')
        plt.plot(wf.Times('ns'),wf.Values(),label='Z approx')
        plt.xlabel('time (ns)')
        plt.ylabel('Z (Ohms)')
        plt.legend(loc='upper right')
        plt.grid(True)
        #self.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()


if __name__ == "__main__":
    unittest.main()