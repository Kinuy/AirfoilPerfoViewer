
import numpy as np
import os
from pathlib import Path



class AirfoilCoefficients:
    def __init__(self, InFile=None):
        self.InFileAFCOEF = InFile
        self.initVariablesAFCoeff()
        self.checkFormatAndRead()

    def initVariablesAFCoeff(self):
        self.FlagAFCOEF = ""
        self.Flags = ["F", "RFOIL", "WT", "OF", "ATG"]
        self.RelTh = None
        self.REYN = None
        self.maxAoA = -1
        self.Ma = None
        self.hasVG = False
        self.Revision = "RXX"
        self.varDict = {}
        self.Cl = dict()
        self.Cd = dict()
        self.Cm = dict()
        self.Alpha = dict()
        self.ClCd = dict()
        self.cdp = {}
        self.Top_Xtr = {}
        self.Bot_Xtr = {}
        self.alphaMinAndMax = {}
        self.REFNUM = None
        self.XA = 25
        self.THICK = 0.0
        self.DEPANG = 0
        self.NALPHA = 0
        self.NVALS = 3
        self.InterfaceData = True
        self.PATH = ""
        self.ATG_ZeroLiftAngle = 0
        self.ATG_LiftGradient = 0
        self.ATG_MaxLiftDragRatio = 0
        self.ATG_MaxLift = 0
        self.ATG_MaxLiftAngle = 0
        self.ATG_CharLift = None
        self.ATG_CharDrag = None
        self.ATG_CharMom = None

    def readAirfoilCoefficients(self):
        self.WNHeaderValues = []
        if self.FlagAFCOEF == "F":
            # print("F Polar")
            PolarFile = open(self.InFileAFCOEF, "r")
            polar_file_lines = PolarFile.readlines()
            PolarFile.close()
            data_lines = [line.rstrip() for line in polar_file_lines]
            count = 0
            for line in data_lines:
                if line.startswith("REFNUM"):
                    self.REFNUM = str(line.split("\t", 1)[1]).strip("\t")
                    # print('2',self.REFNUM)
                    self.WNHeaderValues.append(self.REFNUM)
                    self.Cl[self.REFNUM] = []
                    self.Cd[self.REFNUM] = []
                    self.Cm[self.REFNUM] = []
                    self.Alpha[self.REFNUM] = []
                    continue
                if line.startswith("XA"):
                    self.XA = float(line.split("\t", 1)[1])
                    self.WNHeaderValues.append(self.XA)
                    continue
                if line.startswith("THICK"):
                    self.THICK = float(line.split("\t", 1)[1])
                    self.WNHeaderValues.append(float(self.THICK))
                    continue
                if line.startswith("REYN"):
                    self.REYN = float(line.split("\t", 1)[1])
                    self.WNHeaderValues.append(self.REYN)

                    continue
                if line.startswith("DEPANG"):
                    self.DEPANG = float(line.split("\t", 1)[1])
                    self.WNHeaderValues.append(self.DEPANG)
                    continue
                if line.startswith("NALPHA"):
                    self.NALPHA = int(line.split("\t", 1)[1])
                    self.WNHeaderValues.append(self.NALPHA)
                    continue
                if line.startswith("NVALS"):
                    self.NVALS = int(line.split("\t", 1)[1])
                    self.WNHeaderValues.append(self.NVALS)
                    continue
                if line.startswith("ENDSECTION"):
                    continue
                if line.startswith("VORTEXGENS"):
                    temp = line.split()
                    if temp[1] == "true":
                        self.hasVG = True
                    else:
                        self.hasVG = False
                    # print("Airfoil has VGs:", self.hasVG)
                    continue
                if line.startswith("#"):
                    continue
                if line.startswith("*"):
                    continue
                else:
                    columns = line.split()
                    # print('3',columns)
                    self.Alpha[self.REFNUM].append(columns[0])
                    self.Cl[self.REFNUM].append(columns[1])
                    self.Cd[self.REFNUM].append(columns[-2])
                    self.Cm[self.REFNUM].append(columns[-1])
        if self.FlagAFCOEF == "WT":
            print("WT Polar")
            PolarFile = open(self.InFileAFCOEF, "r")
            polar_file_lines = PolarFile.readlines()
            PolarFile.close()
            data_lines = [line.rstrip() for line in polar_file_lines]
            count = 0
            self.Cl[self.REFNUM] = []
            self.Cd[self.REFNUM] = []
            self.Cm[self.REFNUM] = []
            self.Alpha[self.REFNUM] = []
            for line in data_lines:
                if count >= self.readlineAFCOEF:
                    columns = line.split()
                    self.Alpha[self.REFNUM].append(columns[0])
                    self.Cl[self.REFNUM].append(columns[1])
                    self.Cd[self.REFNUM].append(columns[-2])
                    self.Cm[self.REFNUM].append(columns[-1])
                count += 1
        if self.FlagAFCOEF == "OF":
            print("Open Foam Polar")
            PolarFile = open(self.InFileAFCOEF, "r")
            polar_file_lines = PolarFile.readlines()
            PolarFile.close()
            data_lines = [line.rstrip() for line in polar_file_lines]
            count = 0
            for line in data_lines:
                if line.startswith("# Case name:"):
                    self.REFNUM = str(line.split()[3])
                    self.Cl[self.REFNUM] = []
                    self.Cd[self.REFNUM] = []
                    self.Cm[self.REFNUM] = []
                    self.Alpha[self.REFNUM] = []
                if count >= 8:
                    columns = line.split()
                    self.Alpha[self.REFNUM].append(float(columns[0]))
                    self.Cl[self.REFNUM].append(float(columns[1]))
                    self.Cd[self.REFNUM].append(float(columns[2]))
                    self.Cm[self.REFNUM].append(float(columns[3]))
                count += 1
        if self.FlagAFCOEF == "ATG":
            print("ATG Polar")
            PolarFile = open(self.InFileAFCOEF, "r")
            polar_file_lines = PolarFile.readlines()
            PolarFile.close()
            data_lines = [line.rstrip() for line in polar_file_lines]
            count = 0
            REFNUMLine = 50

            CharLiftArray = np.array([])
            CharDragArray = np.array([])
            CharMomArray = np.array([])
            CharLift = []
            CharLiftAlpha = []
            CharDrag = []
            CharDragAlpha = []
            CharMom = []
            CharMomAlpha = []

            for line in data_lines:
                if line.startswith("#       Airfoil :"):
                    REFNUMLine = count + 2
                if count == REFNUMLine:
                    # print(str(line.split()))
                    self.REFNUM = str(line.split()[0]) + str(line.split()[1])
                    self.Cl[self.REFNUM] = []
                    self.Cd[self.REFNUM] = []
                    self.Cm[self.REFNUM] = []
                    self.Alpha[self.REFNUM] = []
                if count > self.readlineAFCOEF and count < self.EndreadlineAFCOEF:
                    columns = line.split()
                    self.Alpha[self.REFNUM].append(float(columns[0]))
                    self.Cl[self.REFNUM].append(float(columns[1]))
                    self.Cd[self.REFNUM].append(float(columns[2]))
                    self.Cm[self.REFNUM].append(float(columns[3]))
                if count > self.readlineAFCharLift and count < self.EndreadlineAFCharLift:
                    columns = line.split()
                    CharLift.append(float(columns[0]))
                    CharLiftAlpha.append(float(columns[1]))
                if count > self.readlineAFCharDrag and count < self.EndreadlineAFCharDrag:
                    columns = line.split()
                    CharDrag.append(float(columns[0]))
                    CharDragAlpha.append(float(columns[1]))
                if count > self.readlineAFCharMom and count < self.EndreadlineAFCharMom:
                    columns = line.split()
                    CharMom.append(float(columns[0]))
                    CharMomAlpha.append(float(columns[1]))
                count += 1

            self.CharLiftArray = np.column_stack([CharLift, CharLiftAlpha])
            self.CharDragArray = np.column_stack([CharDrag, CharDragAlpha])
            self.CharMomArray = np.column_stack([CharMom, CharMomAlpha])
            # print(CharLiftArray[:, 1])
        if self.FlagAFCOEF == "RFOIL":
            print("RFOIL")
            Data = open(self.InFileAFCOEF, "r")
            DataLines = Data.readlines()
            Data.close()
            for line in DataLines:
                if line.startswith(" xtrf"):
                    lineList = line.replace("   ", " ").strip("\n").split(" ")
                    self.xtrf_suc_pres = [float(lineList[3]), float(lineList[6])]
                if line.startswith(" Rot."):
                    lineList = line.replace("   ", " ").replace("  ", " ").strip("\n").split(" ")
                    self.f0 = float(lineList[5])
                    self.c_r = float(lineList[8])
                if line.startswith("  REFNUM"):
                    self.REFNUM = line.strip("\n").split("\t")[-1]
                if line.startswith(" Mach"):
                    lineList = (
                        line.replace("      ", " ")
                        .replace("     ", " ")
                        .replace("   ", " ")
                        .strip("\n")
                        .split(" ")
                    )
                    lineList = [x for x in lineList if x]
                    # [x for x in strings if x.strip()]
                    self.mach = float(lineList[2])
                    self.re = float(lineList[(lineList.index("Re", 0, -1) + 2)]) * pow(
                        10, int(lineList[lineList.index("e", 0, -1) + 1])
                    )

                    # self.re = float(lineList[6] + lineList[7] + lineList[8])
                    self.ncrit = float(
                        lineList[(lineList.index("Ncrit", 0, -1) + 2)]
                    )  # float(lineList[11])
                    break
            DataLinesList = [line.replace("   ", " ") for line in DataLines]
            DataLinesList = [line.replace("  ", " ") for line in DataLinesList]
            DataLinesList = [line.strip("\n").split(" ") for line in DataLinesList]
            DataLinesList = [line[1:] for line in DataLinesList]

            self.df = pd.DataFrame(
                DataLinesList[13:],
                columns=["alpha", "CL", "CD", "Re(CL)", "CM", "S_xtr", "P_xtr", "CDp"],
            )
            if self.REFNUM == None:
                self.REFNUM = str(self.re)
            self.Alpha[self.REFNUM] = self.df["alpha"]  # .append(float(columns[0]))
            self.Cl[self.REFNUM] = self.df["CL"]  # .append(float(columns[1]))
            self.Cd[self.REFNUM] = self.df["CD"]  # .append(float(columns[2]))
            self.Cm[self.REFNUM] = self.df["CM"]  # .append(float(columns[3]))

        for key in self.Alpha.keys():
            self.alphaMinAndMax[key] = [min(self.Alpha[key]), max(self.Alpha[key])]
            self.Cl[key] = np.array(self.Cl[key], float)
            self.Cd[key] = np.array(self.Cd[key], float)
            self.Cm[key] = np.array(self.Cm[key], float)
            self.Alpha[key] = np.array(self.Alpha[key], float)

        #self.writeDataToJSONFormat("Airfoil.json",1)
        return

    def checkFormatAndRead(self):
        if self.InFileAFCOEF != None:
            # print(self.InFileAFCOEF)
            # os.path.split()
            filename = os.path.basename(self.InFileAFCOEF)
            ending = filename[-3]
            # print(ending)
            File = open(self.InFileAFCOEF, "r")
            Lines = File.readlines()
            File.close()
            count = 0
            self.readlineAFCOEF = 0
            for line in Lines:
                if count == 0:
                    if line.startswith("REFNUM"):
                        self.FlagAFCOEF = "F"
                        self.readlineAFCOEF = 8
                        break
                    if line.startswith("# Polar Data"):
                        self.FlagAFCOEF = "OF"
                        self.readlineAFCOEF = 9
                        break
                    if line.startswith("#"):
                        self.FlagAFCOEF = "WT"
                        self.readlineAFCOEF = 4
                        if count == 0 and self.FlagAFCOEF == "WT":
                            temp = line.strip("\n").strip("# ").strip("\t").strip(" ")
                            self.REFNUM = temp
                        break
                if line.startswith("       RFOIL"):
                    self.FlagAFCOEF = "RFOIL"
                    break
                count += 1

            if ending == "P":
                self.FlagAFCOEF = "ATG"
                # self.readlineAFCOEF = 39
                count = 0
                for line in Lines:
                    if line.startswith("<COEFFICIENTS>"):
                        self.readlineAFCOEF = count
                    if line.startswith("</COEFFICIENTS>"):
                        self.EndreadlineAFCOEF = count
                    if line.startswith("<CHARLIFT>"):
                        self.readlineAFCharLift = count
                    if line.startswith("</CHARLIFT>"):
                        self.EndreadlineAFCharLift = count
                    if line.startswith("<CHARDRAG>"):
                        self.readlineAFCharDrag = count
                    if line.startswith("</CHARDRAG>"):
                        self.EndreadlineAFCharDrag = count
                    if line.startswith("<CHARMOM>"):
                        self.readlineAFCharMom = count
                    if line.startswith("</CHARMOM>"):
                        self.EndreadlineAFCharMom = count
                    count += 1

            self.readAirfoilCoefficients()

    def plotAirfoilCoefficients(self, title, outPNGFile, show):
        # print(type(self.Cl[self.REYN]))
        fig = plt.figure(num=None, figsize=(10, 5), dpi=150, facecolor="w", edgecolor="k")
        ax = fig.add_subplot(111)
        ax.set_title(title)
        ax.grid(True)
        # ax.grid.xdata(np.arange(-200,200,50))
        # ax.xaxis.grid
        ax.grid(color="k", alpha=0.2, linestyle="-", linewidth=1.0)
        ax.set_xlim(-200, 200)
        ax.set_ylim(-2.0, 2.0)
        ax.set_xticks(np.arange(-200, 200 + 0.1, 50))
        ax.set_yticks(np.arange(-2.0, 2.0 + 0.1, 0.5))
        ax.xaxis.set_tick_params(labelsize=12)
        ax.yaxis.set_tick_params(labelsize=12)
        ax.set_ylabel("cl [-] , cd [-] , cm [-]", fontsize=12, color="k")
        # ax.set_ylabel('cd [-]',fontsize=6, color='r')
        # ax.set_ylabel('cl [-]''cd [-]' 'cm [-]',fontsize=6, color='b')
        ax.set_xlabel("Alpha [deg]", fontsize=12)
        ax.plot(
            np.array(self.Alpha[self.REFNUM], float),
            np.array(self.Cl[self.REFNUM], float),
            linewidth=2,
            color="b",
            linestyle="-",
            label="cl",
        )  # ,marker='s',markersize=4,label = 'cl')
        ax.plot(
            np.array(self.Alpha[self.REFNUM], float),
            np.array(self.Cd[self.REFNUM], float),
            linewidth=2,
            color="r",
            linestyle="-",
            label="cd",
        )  # ,marker='^',markersize=4,label = 'cd')
        ax.plot(
            np.array(self.Alpha[self.REFNUM], float),
            np.array(self.Cm[self.REFNUM], float),
            linewidth=2,
            color="g",
            linestyle="-",
            label="cm",
        )  # ,marker='o',markersize=4,label = 'cm')

        # Move left y-axis and bottim x-axis to centre, passing through (0,0)
        ax.spines["left"].set_position("zero")
        ax.spines["bottom"].set_position("zero")

        # Eliminate upper and right axes
        ax.spines["right"].set_color("none")
        ax.spines["top"].set_color("none")

        # Show ticks in the left and lower axes only
        ax.xaxis.set_ticks_position("bottom")
        ax.yaxis.set_ticks_position("left")

        # Place axis labels
        ax.xaxis.set_label_coords(0.5, -0.025)
        ax.yaxis.set_label_coords(-0.02, 0.5)

        ax.legend()
        fig.tight_layout()
        plt.savefig(outPNGFile)
        if show == True:
            plt.show()
        print("Done plotting  Airfoil Coefficients")

    # def opener(self,path, flags):
    #     return os.open(path, flags, 0o777)

    def WriteCoefficients(self, Flag):
        if Flag == "F":
            self.WNHeader = [
                "REFNUM",
                "XA",
                "THICK",
                "REYN",
                "DEPANG",
                "NALPHA",
                "NVALS",
                "ENDSECTION",
            ]
            # print(self.OutFile)
            file = open(self.OutFile, "w")
            ###write header
            for i in range(len(self.WNHeader) - 1):

                file.write(self.WNHeader[i] + "\t" + "\t" + "\t")
                # if i == 0:
                file.write(str(self.WNHeaderValues[i]) + "\n")

            ###write data
            # print(len(self.Cd[self.REFNUM]))
            for i in range(len(self.Alpha[self.REFNUM])):
                file.write(format(float(self.Alpha[self.REFNUM][i]), ".2f"))
                file.write("\t")
                file.write(format(float(self.Cl[self.REFNUM][i]), ".4f"))  # self.Cl[i])
                file.write("\t")
                file.write(format(float(self.Cd[self.REFNUM][i]), ".4f"))  # self.Cd[i])
                file.write("\t")
                file.write(format(float(self.Cm[self.REFNUM][i]), ".4f"))  # self.Cm[i])
                file.write("\n")
            file.write(self.WNHeader[-1])
            if self.hasVG == True:
                file.write("\nVORTEXGENS			true	# {true,false}; default if Param missing= false;")
            file.close()

    def setHeaderValues(self, Flag, outpath):
        self.WNHeaderValues = []
        self.OutFile = outpath
        if Flag == "F":
            # if self.hasVG == True:
            #    self.REFNUM = "Cut-" + str(int(self.THICK * 10)) +'-'+ self.Revision +'-'+ 'VG'
            # else:
            #    self.REFNUM = "Cut-" + str(int(self.THICK * 10)) +'-'+ self.Revision +'-'+ 'Clean'
            # print(self.OutFile)
            # self.OutFile = outpath + "\\" + self.REFNUM + ".dat"
            self.XA = 25
            self.NALPHA = len(self.Alpha[self.REFNUM])
            self.NVALS = 3
            self.WNHeaderValues.append(self.REFNUM)
            self.WNHeaderValues.append(self.XA)
            self.WNHeaderValues.append(round(float(self.THICK), 2))
            self.WNHeaderValues.append(self.REYN)
            self.WNHeaderValues.append(self.DEPANG)
            self.WNHeaderValues.append(self.NALPHA)
            self.WNHeaderValues.append(self.NVALS)

    def ChangeKey(self, Key_neu):
        Key_alt = self.REFNUM
        print("Key old: ", Key_alt, "\nKey new: ", Key_neu)
        self.Alpha[Key_neu] = self.Alpha[Key_alt]
        self.Cl[Key_neu] = self.Cl[Key_alt]
        self.Cd[Key_neu] = self.Cd[Key_alt]
        self.Cm[Key_neu] = self.Cm[Key_alt]
        del self.Alpha[Key_alt]
        del self.Cl[Key_alt]
        del self.Cd[Key_alt]
        del self.Cm[Key_alt]
        self.REFNUM = Key_neu
        self.WNHeaderValues[0] = self.REFNUM

    def getClOpt(self):

        self.ClCd[self.REFNUM] = self.Cl[self.REFNUM] / self.Cd[self.REFNUM]
        ClCdMax = max(self.ClCd[self.REFNUM])
        ClCl_Max_index = np.where(self.ClCd[self.REFNUM] == ClCdMax)
        # print('ClCd_max: ',ClCdMax , ' with Cl_opt: ',self.Cl[self.REFNUM][ClCl_Max_index],' at Alpha_opt: ',self.Alpha[self.REFNUM][ClCl_Max_index])
        self.Cl_opt = float(self.Cl[self.REFNUM][ClCl_Max_index])
        self.Alpha_opt = float(self.Alpha[self.REFNUM][ClCl_Max_index])

    def writeDataToJSONFormat(self,outfile,id):#,REFNUM,THICK,REYN,NALPHA_NUM,alfa_List,cl_list,cd_list,cm_list):

        filePath = Path(self.InFileAFCOEF)
        outfile = filePath.parent.joinpath(outfile)

        file = open(outfile, "w")
        file.write("{")
        file.write(f"\"_id\": {id},\n""")
        file.write("\"data\":{")
        file.write("\n\"alfa_deg\": [")

        for i in range(len(self.Alpha[self.REFNUM])):
            file.write(format(float(self.Alpha[self.REFNUM][i]), ".2f"))
            if(i!=len(self.Alpha[self.REFNUM])-1):
                file.write(" , ")
            else:
                file.write("],")
        #file.write("],\"")
        file.write("\n\"cl\": [")
        for i in range(len(self.Alpha[self.REFNUM])):
            file.write(format(float(self.Cl[self.REFNUM][i]), ".4f"))
            if(i!=len(self.Alpha[self.REFNUM])-1):
                file.write(" , ")
            else:
                file.write("],")
        file.write("\n\"cd\": [")
        for i in range(len(self.Alpha[self.REFNUM])):
            file.write(format(float(self.Cd[self.REFNUM][i]), ".4f"))
            if(i!=len(self.Alpha[self.REFNUM])-1):
                file.write(" , ")
            else:
                file.write("],")
        file.write("\n\"cm\": [")
        for i in range(len(self.Alpha[self.REFNUM])):
            file.write(format(float(self.Cm[self.REFNUM][i]), ".4f"))
            if(i!=len(self.Alpha[self.REFNUM])-1):
                file.write(" , ")
            else:
                file.write("]")

        file.write("\n}")
        file.write("\n}")
        file.close()
