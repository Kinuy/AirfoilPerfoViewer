import os
import sys
from pathlib import Path
import pyqtgraph as pg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *  

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import coefficients as co
import utility as wnu


class UI_MainWindow(object):
    def loadData(self):
        Data = []
        self.DataObjects = []
        self.DataREFNUM = []
        for i in range(len(self.polarList)):
            Data.append(self.polarList[i])
        for i in range(len(self.polarList)):
            self.DataObjects.append(co.AirfoilCoefficients(Data[i]))
            self.DataREFNUM.append(self.DataObjects[i].REFNUM)
            self.DataObjects[i].writeDataToJSONFormat(f"Airfoil{self.DataObjects[i].REFNUM}.json",i)

    def SetPlotData(self):
        for i in range(len(self.polarList)):
            self.curve0[i].setData(
                self.DataObjects[i].Alpha[self.DataREFNUM[i]],
                self.DataObjects[i].Cl[self.DataREFNUM[i]],
                name=self.DataREFNUM[i],
            )
            self.curve1[i].setData(
                self.DataObjects[i].Alpha[self.DataREFNUM[i]],
                self.DataObjects[i].Cd[self.DataREFNUM[i]],
            )
            self.curve2[i].setData(
                self.DataObjects[i].Alpha[self.DataREFNUM[i]],
                self.DataObjects[i].Cm[self.DataREFNUM[i]],
            )
            self.curve3[i].setData(
                self.DataObjects[i].Cl[self.DataREFNUM[i]]
                / self.DataObjects[i].Cd[self.DataREFNUM[i]],
                self.DataObjects[i].Cl[self.DataREFNUM[i]],
            )

    def setupUi(self, MainWindow, inputData):
        self.polarList = inputData["Polars"]
        self.loadData()
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setWindowTitle("Polar Data")
        self.layout = QVBoxLayout()
        self.centralWidget.setLayout(self.layout)
        MainWindow.setCentralWidget(self.centralWidget)
        MainWindow.setWindowTitle("Polar Data")
        self.win = pg.GraphicsLayoutWidget()# GraphicsWindow()
        self.layout.addWidget(self.win)
        pg.setConfigOptions(antialias=True)

        self.win.setBackground("w")
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")
        pg.setConfigOptions(antialias=True)

        ## |Cl||Cl/Cd|
        ## |Cd||Cm|


        self.p0 = self.win.addPlot(row=0, col=0)
        self.p1 = self.win.addPlot(row=1, col=0)
        self.p2 = self.win.addPlot(row=1, col=1)
        self.p3 = self.win.addPlot(row=0, col=1)

        self.p0.showGrid(x=True, y=True, alpha=100)
        self.p1.showGrid(x=True, y=True, alpha=100)
        self.p2.showGrid(x=True, y=True, alpha=100)
        self.p3.showGrid(x=True, y=True, alpha=100)

        self.p0.setLabels(left="cl [-]")
        self.p0.setLabels(bottom="alpha [deg]")
        self.p1.setLabels(left="cd [-]")
        self.p1.setLabels(bottom="alpha [deg]")
        self.p2.setLabels(left="cm [-]")
        self.p2.setLabels(bottom="alpha [deg]")
        self.p3.setLabels(left="cl [-]")
        self.p3.setLabels(bottom="cl/cd [-]")

        self.p0.showAxis("right")
        self.p1.showAxis("right")
        self.p2.showAxis("right")
        self.p3.showAxis("right")

        # dynamic curve generation

        self.curve0 = []
        self.curve1 = []
        self.curve2 = []
        self.curve3 = []

        colorList = [
            "#3399ff",
            "#ff3300",
            "#00ff00",
            "#ff00ff",
            "#009999",
            "#ffff00",
            "#993333",
            "#ff6600",
            "#66ccff",
            "#006600",
            "#993366",
            "#999966",
        ]

        for i in range(len(self.polarList)):
            pen = pg.mkPen(colorList[i], width=3)
            self.curve0.append(self.p0.plot(pen=pen))  # pen="r"))  # cl
            self.curve1.append(self.p1.plot(pen=pen))  # pen="r"))  # cd
            self.curve2.append(self.p2.plot(pen=pen))  # pen="r"))  # cm
            self.curve3.append(self.p3.plot(pen=pen))  # pen="r"))  # clcd
        self.SetPlotData()

        self.legend = pg.LegendItem()
        self.legend.setParentItem(self.p0)
        for i in range(len(self.polarList)):
            self.legend.addItem(self.curve0[i], name=self.curve0[i].opts["name"])
        self.legend.anchor((0, 0), (0, 0))



def main(input_file):

    input_data = wnu.readYAML(input_file)
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = UI_MainWindow()
    ui.setupUi(MainWindow, input_data)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        import os
        print("Current Working Directory:", os.getcwd())
        os.chdir("..") 

        main(sys.argv[1])
    except:
        print(
            "######################################################\n##################### DEBUG MODE #####################\n######################################################\n\n"
        )
        file_path = Path("userInput") / "AirfoilPerfoData.yaml"
        newPath = os.getcwd()+os.sep+"AirfoilPerfoViewer"+os.sep+"userInput"+os.sep+"AirfoilPerfoData.yaml"
        main(newPath)
