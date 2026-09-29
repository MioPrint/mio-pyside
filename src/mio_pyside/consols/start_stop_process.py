
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from typing import Literal

class QStartStopConsole(QWidget):

    divider = "------------------------------------------------------------------------ \n"

    def __init__(self,
            start_script:str,
            stop_script:str="",
            process_type:Literal["bash_command", "sh_file"]="bash_command",
            parent:QWidget= None
            ):

        super().__init__(
            parent= parent,
            )
        
        self.start_script = start_script
        self.stop_script = stop_script

        self.process_type = process_type
        
        self.process_start = QProcess(parent=self)
        self.process_start.readyReadStandardOutput.connect(self.on_start_stdout)
        self.process_start.readyReadStandardError.connect(self.on_start_stderr)
        self.process_start.finished.connect(self.on_start_finished)

        self.process_stop = QProcess(parent=self)
        self.process_stop.readyReadStandardOutput.connect(self.on_stop_stdout)
        self.process_stop.readyReadStandardError.connect(self.on_stop_stderr)
        self.process_stop.finished.connect(self.on_stop_finished)

        self.process_debug = QProcess(parent=self)
        self.process_debug.readyReadStandardOutput.connect(self.on_start_stdout)
        self.process_debug.readyReadStandardError.connect(self.on_start_stderr)
        self.process_debug.finished.connect(self.on_start_finished)

        self.init_widgets()
        self.init_layout()

    def init_widgets(self):

        # --- Widgets --- #

        self.button_start = QPushButton(" Start ", parent=self)
        self.button_start.setEnabled(True)
        self.button_start.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.button_start.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)))
        self.button_start.clicked.connect(self.on_start)

        self.button_stop = QPushButton(" Stop ", parent=self)
        self.button_stop.setEnabled(False)
        self.button_stop.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)))
        self.button_stop.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.button_stop.clicked.connect(self.on_stop)

        self.output = QTextEdit(parent=self)
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                font-family: "Consolas", "Courier New", "Liberation Mono", monospace;
                font-size: 10pt;
            }
        """)
        
        #doc = self.output.document()
        #blockFmt = doc.begin().blockFormat()
        #blockFmt.setNonBreakableLines(True)  # allow wrapping
        #blockFmt.setLineHeight(100, blockFmt.LineHeightTypes.ProportionalHeight)
        #cursor = QTextCursor(doc)
        #cursor.select(QTextCursor.SelectionType.Document)
        #cursor.setBlockFormat(blockFmt)

        #cursor = self.output.textCursor()
        #cursor.movePosition(QTextCursor.MoveOperation.End)
        #self.output.setTextCursor(cursor)



        self.output.document().setDefaultStyleSheet("""
            div, p, span, pre {
                white-space: pre-wrap !important;
                word-wrap:normal !important;
                overflow-wrap: normal !important;
                word-break: break-word !important;
                font-family: Consolas, monospace;
                font-size: 10pt;
                background-color: #1e1e1e;
            }
        """)
        self.output.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        #self.output.setMinimumWidth(800)

    def init_layout(self):

        # --- Layout --- #

        layout_buttons = QVBoxLayout()
        layout_buttons.addWidget(self.button_start)
        layout_buttons.addWidget(self.button_stop)

        layout_buttons_with_output = QHBoxLayout()
        layout_buttons_with_output.addWidget(self.output, 1)
        layout_buttons_with_output.addLayout(layout_buttons)

        #layout_stop = QHBoxLayout()
        #layout_stop.addWidget(button_stop)
        #layout_stop.addWidget(self.stop_output)

        layout_main_v = QVBoxLayout()
        layout_main_v.addLayout(layout_buttons_with_output)

        self.setLayout(layout_main_v)

    def setStartScript(self, script:str):

        self.start_script = script

    def setStopScript(self, script:str):

        self.stop_script = script

    @Slot()
    def on_start(self):

        text = f"\n --- Start Dev ---" + self.divider
        self.update_output(text, color="white")

        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(True)

        if self.process_type == "bash_command":
            self.process_start.start("/bin/bash", ["-c", self.start_script])
            return

        if self.process_type == "sh_file":
            self.process_start.start(self.start_script)
            return


        #################################


        #pid = self.process_start.processId()
        #self.update_output(f"{pid}", color="blue")

        #self.process_debug.start("/bin/bash", ["-c", f"PORT_PID=$(lsof -ti tcp:5173) && echo 'Port 5173 is used by PID: ' $PORT_PID || echo 'Port 5173 is free'"])

        #port_pid_format = "PORT_PID=$(lsof -ti tcp:{port}) && echo $PORT_PID" 

        #self.process_debug.start("/bin/bash", ["-c", port_pid_format.format(port=5174)])

        #get_port_pids_process.waitForFinished()



        #subprocess.call(dev_script_path, shell=True)

        #subprocess.run(["gnome-terminal", "--", "bash", "-c", "echo test; exec bash"]) #, "--", "bash", "-c", "ls; exec bash"])

        #self.process = QProcess(self)
        #self.process.start("gnome-terminal", ["--", "bash", "-c", "echo test; exec bash"])

    @Slot()
    def on_stop(self):

        text = f"\n --- Stop Dev ---" + self.divider
        self.update_output(text, color="white")

        self.process_start.kill()

        self.button_start.setEnabled(True)
        self.button_stop.setEnabled(False)

        if self.stop_script:

            if self.process_type == "bash_command":

                self.process_stop.start("/bin/bash", ["-c", self.stop_script])
                return

            if self.process_type == "sh_file":

                self.process_stop.start(self.stop_script)
                return
            
        #################################

        #subprocess.call(dev_script_path, shell=True)

    @Slot()
    def on_start_stdout(self):

        text = self.process_start.readAllStandardOutput().data().decode()
        self.update_output(text, color="green")

    @Slot()
    def on_start_stderr(self):

        text = self.process_start.readAllStandardError().data().decode()
        self.update_output(text, color="red")
  
    @Slot()
    def on_start_finished(self):

        #text = self.process_debug.readAllStandardOutput().data().decode()
        #self.update_output(text, color="blue")

        return
        text = "finished start"
        self.update_output(text, color="lightblue")

    @Slot()
    def on_stop_stdout(self):

        text = self.process_stop.readAllStandardOutput().data().decode()
        self.update_output(text, color="green")

    @Slot()
    def on_stop_stderr(self):

        text = self.process_stop.readAllStandardError().data().decode()
        self.update_output(text, color="red")
  
    @Slot()
    def on_stop_finished(self):

        return
        text = "finished stop"
        self.update_output(text, color="lightblue")

    def update_output(self, text:str, color:str = "white"):

        self.output.moveCursor(QTextCursor.MoveOperation.End)

        html = text.replace("\n", "<br>")
        wrapped = f'<div style="color:{color};">{html}</div>'
        self.output.insertHtml(wrapped)
        self.output.moveCursor(QTextCursor.MoveOperation.End)

        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def closeEvent(self, event:QCloseEvent):

        if self.process_start.state() == QProcess.ProcessState.Running:
            self.process_start.kill()
            self.process_start.waitForFinished()

            self.process_stop.start(self.stop_script)
            self.process_stop.waitForFinished()

        super().closeEvent(event)
