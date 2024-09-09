from PySide2 import QtCore, QtUiTools, QtWidgets, QtGui
from PySide2.QtMultimedia import QMediaPlayer, QMediaContent
from PySide2.QtMultimediaWidgets import QVideoWidget
from maya import OpenMayaUI as omu
from shiboken2 import wrapInstance
import maya.cmds as cmds
import os, sys, shutil
import maya.mel as mel
import subprocess
import re
from PySide2.QtCore import QThread, Signal, Slot
# from typing import Optional

space_re = re.compile(r"\s+")
py_ver = sys.version_info.major
# This maps the BVH naming convention to Maya
translationDict = {
    "Xposition": "translateX",
    "Yposition": "translateY",
    "Zposition": "translateZ",
    "Xrotation": "rotateX",
    "Yrotation": "rotateY",
    "Zrotation": "rotateZ"
}


# local addresses

# SCRIPT_FILE_PATH = 'D:/reza_niroumand/Script/animation_generator/maya/'
# DRIVE_LETTER ='D:'
# ACTIVATE_MGPT_ENV_COMMAND = 'D:/reza_niroumand/Script/animation_generator/MotionGPT/mGPT/Scripts/activate.bat'
# CHANGE_DIR_COMMAND = 'cd D:/reza_niroumand/Script/animation_generator/MotionGPT'
# RUN_DEMO_PY_COMMAND = 'python.exe D:/reza_niroumand/Script/animation_generator/MotionGPT/demo.py'
# AGPT_CONFIG_FILE_PATH = 'D:/reza_niroumand/Script/animation_generator/MotionGPT/config_AGPT.yaml'
# MOTIONGPT_CONFIG_FILE_PATH = 'D:/reza_niroumand/Script/animation_generator/MotionGPT/configs/config_h3d_stage3.yaml'

# ACTIVATE_CONVERTOR_ENV_COMMAND = 'D:/reza_niroumand/Script/animation_generator/convertor/Scripts/activate'
# MP4_CONVERTOR_FILE_PATH = 'D:/reza_niroumand/Script/animation_generator/MotionGPT/tools/animation.py'

# BVH_CONVERTOR_FILE_PATH = 'D:/reza_niroumand/Script/AnimationGPT/MotionGPT/tools/npy2bvh'
# RUN_BVH_CONVERTOR_COMMAND = 'python D:/reza_niroumand/Script/animation_generator/MotionGPT/tools/npy2bvh/joints2bvh.py'

# RETARGET_TEMPLATE_FILE = 'D:/reza_niroumand/Script/animation_generator/maya/retarget_template/retarget_HIK.ma'



# server addresses
'''
SCRIPT_FILE_PATH = 'L:/LEMONSKY/LSA_Pipeline/02_RnD/Tools_Library/Animation/Animation/animation_generator/'
DRIVE_LETTER ='L:'
ACTIVATE_MGPT_ENV_COMMAND = 'L:/LEMONSKY/LSA_PIPELINE/02_RnD/Tools_Library/Animation/Animation/animation_generator/python/py310_venv/mGPT/Scripts/activate.bat'
CHANGE_DIR_COMMAND = 'cd L:/LEMONSKY/LSA_PIPELINE/02_RnD/Tools_Library/Animation/Animation/animation_generator/MotionGPT'
RUN_DEMO_PY_COMMAND = 'python.exe L:/LEMONSKY/LSA_Pipeline/02_RnD/Tools_Library/Animation/Animation/animation_generator/MotionGPT/demo.py'
AGPT_CONFIG_FILE_PATH = 'L:/LEMONSKY/LSA_Pipeline/02_RnD/Tools_Library/Animation/Animation/animation_generator/MotionGPT/config_AGPT.yaml'
MOTIONGPT_CONFIG_FILE_PATH = 'L:/LEMONSKY/LSA_Pipeline/02_RnD/Tools_Library/Animation/Animation/animation_generator/MotionGPT/configs/config_h3d_stage3.yaml'

ACTIVATE_CONVERTOR_ENV_COMMAND = 'L:/LEMONSKY/LSA_PIPELINE/02_RnD/Tools_Library/Animation/Animation/animation_generator/python/py39_venv/convertor/Scripts/activate'
MP4_CONVERTOR_FILE_PATH = 'L:/LEMONSKY/LSA_Pipeline/02_RnD/Tools_Library/Animation/Animation/animation_generator/MotionGPT/tools/animation.py'

BVH_CONVERTOR_FILE_PATH = 'L:/LEMONSKY/LSA_Pipeline/02_RnD/Tools_Library/Animation/Animation/animation_generator/MotionGPT/tools/npy2bvh'
RUN_BVH_CONVERTOR_COMMAND = 'python L:/LEMONSKY/LSA_Pipeline/02_RnD/Tools_Library/Animation/Animation/animation_generator/MotionGPT/tools/npy2bvh/joints2bvh.py'

RETARGET_TEMPLATE_FILE = 'L:/LEMONSKY/LSA_Pipeline/02_RnD/Tools_Library/Animation/Animation/animation_generator/retarget_template'

'''


# server addresses N drive

SCRIPT_FILE_PATH = 'N:/pipeline/Tools/Maya/scripts/anim/animation_generator/'
DRIVE_LETTER ='N:'
ACTIVATE_MGPT_ENV_COMMAND = 'N:/pipeline/external/python/venvs/mGPT/Scripts/activate.bat'
CHANGE_DIR_COMMAND = 'cd N:/pipeline/Tools/Maya/scripts/anim/animation_generator/MotionGPT'
RUN_DEMO_PY_COMMAND = 'python.exe N:/pipeline/Tools/Maya/scripts/anim/animation_generator/MotionGPT/demo.py'
AGPT_CONFIG_FILE_PATH = 'N:/pipeline/Tools/Maya/scripts/anim/animation_generator/MotionGPT/config_AGPT.yaml'
MOTIONGPT_CONFIG_FILE_PATH = 'N:/pipeline/Tools/Maya/scripts/anim/animation_generator/MotionGPT/configs/config_h3d_stage3.yaml'

ACTIVATE_CONVERTOR_ENV_COMMAND = 'N:/pipeline/external/python/venvs/convertor/Scripts/activate'
MP4_CONVERTOR_FILE_PATH = 'N:/pipeline/Tools/Maya/scripts/anim/animation_generator/MotionGPT/tools/animation.py'

BVH_CONVERTOR_FILE_PATH = 'N:/pipeline/Tools/Maya/scripts/anim/animation_generator/MotionGPT/tools/npy2bvh'
RUN_BVH_CONVERTOR_COMMAND = 'python N:/pipeline/Tools/Maya/scripts/anim/animation_generator/MotionGPT/tools/npy2bvh/joints2bvh.py'

RETARGET_TEMPLATE_FILE = 'N:/pipeline/Tools/Maya/scripts/anim/animation_generator/retarget_template'



mainObject = omu.MQtUtil.mainWindow()
mayaMainWind = wrapInstance(int(mainObject), QtWidgets.QWidget)

class TinyDAG(object):
    """
    Tiny DAG class for storing the hierarchy of the BVH file.
    """

    def __init__(self, obj, parent = None):
        """Constructor"""
        self.obj = obj
        self.__parent = parent

    @property
    def parent(self):
        """Returns the parent of the object"""
        return self.__parent

    def __str__(self):
        """String representation of the object"""
        return str(self.obj)

    def full_path(self):
        """Returns the full path of the object"""
        if self.parent is not None:
            return "%s|%s" % (self.parent.full_path(), str(self))
        return str(self.obj)
    

class VideoWidget(QVideoWidget):
    def __init__(self, video_path, parent=None):
        super(VideoWidget, self).__init__(parent)
        self.setMouseTracking(True)
        # Create a media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        
        self.media_player.setVideoOutput(self)
        
        # Set the media content
        video_url = QtCore.QUrl.fromLocalFile(video_path)
        self.media_player.setMedia(video_url)
        self.media_player.pause()
        self.media_player.mediaStatusChanged.connect(self.handle_media_status_change)
    
    def handle_media_status_change(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()
    def release(self):
        self.media_player.stop()
        self.media_player.setMedia(QMediaContent())
        self.media_player.deleteLater()
        self.deleteLater()


class ImportFbxWorker(QThread):
    fbx_imported = Signal()  

    def __init__(self):
        super(ImportFbxWorker,self).__init__()
    
    def run(self):
        if py_ver == 3:
            result = subprocess.run(ACTIVATE_MGPT_ENV_COMMAND +' & ' + DRIVE_LETTER + ' & cd ' + BVH_CONVERTOR_FILE_PATH + ' & ' + RUN_BVH_CONVERTOR_COMMAND , shell=True, capture_output=True, text=True)
            print(result)
        else:
            result_temp = subprocess.Popen(ACTIVATE_MGPT_ENV_COMMAND +' & ' + DRIVE_LETTER + ' & cd ' + BVH_CONVERTOR_FILE_PATH + ' & ' + RUN_BVH_CONVERTOR_COMMAND , stdout=subprocess.PIPE, stderr=subprocess.PIPE , shell=True)
            result, err = result_temp.communicate()
            print(err)       
        self.fbx_imported.emit()


class VideoGenerationWorker(QThread):
    video_generated = Signal()  

    def __init__(self, comboBox, plainTextEdit, preview_pushButton, fbx_pushButton ):
        super(VideoGenerationWorker,self).__init__()
        
        self.comboBox = comboBox
        self.plainTextEdit = plainTextEdit
        self.preview_pushButton = preview_pushButton
        self.fbx_pushButton = fbx_pushButton
    
    
    def run(self):
        self.comboBox.setEnabled(False)
        self.plainTextEdit.setEnabled(False)
        self.preview_pushButton.setEnabled(False)
        
        current_model = self.comboBox.currentText()
        print('current_model')
        print(current_model)
        self.temp_folder = os.getenv('TEMP')
        
        folder_path = os.path.join(self.temp_folder, 'animation_generator')
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        os.makedirs(folder_path)
        input_file_path = os.path.join(folder_path, 'input.txt')
        #print(input_file_path)

        prompt = self.plainTextEdit.toPlainText()
        with open(input_file_path, 'w') as file:
            file.write(prompt)

        
        if current_model == "combat model":
            if py_ver == 3:
                result = subprocess.run(ACTIVATE_MGPT_ENV_COMMAND +' & ' + DRIVE_LETTER + ' & ' + CHANGE_DIR_COMMAND + ' & ' + RUN_DEMO_PY_COMMAND + ' --cfg ' + AGPT_CONFIG_FILE_PATH + ' --example ' + input_file_path, shell=True, capture_output=True, text=True)
                print(result)
            else:
                result_temp = subprocess.Popen(ACTIVATE_MGPT_ENV_COMMAND +' & ' + DRIVE_LETTER + ' & ' + CHANGE_DIR_COMMAND + ' & ' + RUN_DEMO_PY_COMMAND + ' --cfg ' + AGPT_CONFIG_FILE_PATH + ' --example ' + input_file_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE , shell=True)
                result, err = result_temp.communicate()
                print(result)           
        else:
            if py_ver == 3:
                result = subprocess.run(ACTIVATE_MGPT_ENV_COMMAND +' & ' + DRIVE_LETTER + ' & ' + CHANGE_DIR_COMMAND + ' & ' + RUN_DEMO_PY_COMMAND + ' --cfg ' + MOTIONGPT_CONFIG_FILE_PATH + ' --example ' + input_file_path, shell=True, capture_output=True, text=True)
                print(result)
            else:
                result_temp = subprocess.Popen(ACTIVATE_MGPT_ENV_COMMAND +' & ' + DRIVE_LETTER + ' & ' + CHANGE_DIR_COMMAND + ' & ' + RUN_DEMO_PY_COMMAND + ' --cfg ' + MOTIONGPT_CONFIG_FILE_PATH + ' --example ' + input_file_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                result, err = result_temp.communicate()
                print(result) 
        if py_ver==3:
            result = subprocess.run(DRIVE_LETTER + ' & ' + ACTIVATE_CONVERTOR_ENV_COMMAND + ' & python '+ MP4_CONVERTOR_FILE_PATH, shell=True, capture_output=True, text=True)
            print(result)
        else:
            result_temp = subprocess.Popen(DRIVE_LETTER + ' & ' + ACTIVATE_CONVERTOR_ENV_COMMAND + ' & python '+ MP4_CONVERTOR_FILE_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            result, err = result_temp.communicate()
            print(err)   
        self.comboBox.setEnabled(True)
        self.plainTextEdit.setEnabled(True)
        self.preview_pushButton.setEnabled(True)
        self.fbx_pushButton.setEnabled(True)
        
        self.video_generated.emit()



class AnimationGPT(QtWidgets.QWidget):    
    def __init__(self,parent=mayaMainWind):
        
        super(AnimationGPT, self).__init__(parent=parent)
                   
        if(__name__ == '__main__'):
            self.ui = SCRIPT_FILE_PATH+"ui/animation_gpt.ui"
        else:
            self.ui = os.path.abspath(os.path.dirname(__file__)+'/ui/animation_gpt.ui')        
        
        self.temp_folder = os.getenv('TEMP')
        
        self.setAcceptDrops(True)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('AnimationGenerator')
        self.resize(900,490)                
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(self.ui)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.theMainWidget = loader.load(ui_file)
        ui_file.close()
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.theMainWidget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        self.switch = True
        self.widget_switch = True
        
        self.theMainWidget.generate_preview_pushButton.clicked.connect(self.generate_preview)

        self.theMainWidget.simplify_anim_curve_pushButton.clicked.connect(self.simplify_anim_curve)
        self.theMainWidget.simplify_anim_curve_pushButton.setEnabled(False)
        
        self.theMainWidget.import_fbx_pushButton.setEnabled(False)
        self.theMainWidget.import_fbx_pushButton.clicked.connect(self.import_fbx)
        
        self.theMainWidget.play_pushButton.clicked.connect(self.play_media)

        self.theMainWidget.model_comboBox.addItem("general model")
        self.theMainWidget.model_comboBox.addItem("combat model")

        self.theMainWidget.video_examples_pushButton.clicked.connect(self.open_video_folder)
        self.theMainWidget.help_pushButton.clicked.connect(self.open_help)
        
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_progress)    
    
    def open_help(self):
        os.startfile(SCRIPT_FILE_PATH + 'doc/animation_generator_help.pdf')

    
    def open_video_folder(self):
        os.startfile(SCRIPT_FILE_PATH + 'doc/examples')
    
    
    def update_progress(self):

        temp_folder = os.getenv('TEMP')
        self.progress_file = os.path.join(temp_folder, 'animation_generator', 'progress.txt')
        try:
            with open(self.progress_file, 'r') as file:
                lines = file.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    progress = int(last_line.replace('%', ''))
                    self.theMainWidget.progressBar.setValue(progress)
                    if progress == 100:
                        self.timer.stop()
                        # self.start_button.setEnabled(True)
        except IOError as e:
            pass
    
    
    
    
    def simplify_anim_curve(self):

        attributes = []

        descendants = cmds.listRelatives('animation_generator_ref', allDescendents=True, fullPath=True)
        descendants.remove('|animation_generator_ref|animation_generator_refShape')
        print(len(descendants))
        for item in descendants:
            attributes.append(item+".translateX")
            attributes.append(item+".translateY")
            attributes.append(item+".translateZ")
            attributes.append(item+".rotateX")
            attributes.append(item+".rotateY")
            attributes.append(item+".rotateZ")
        print(len(attributes))
        cmds.filterCurve(attributes, f='simplify', timeTolerance=0.05)
    
    
    
    
    def closeEvent(self, event):
        # Call the release method of VideoWidget before closing
        try:
            self.video_widget.release()
            event.accept()  # Proceed with the window closing
        except:
            pass    
    
    
    def generate_preview(self):
        self.theMainWidget.import_fbx_pushButton.setEnabled(False)
        self.theMainWidget.simplify_anim_curve_pushButton.setEnabled(False)
        self.theMainWidget.model_comboBox.setEnabled(False)
        self.timer.start(500)

        if not self.theMainWidget.prompt_plainTextEdit.toPlainText():
            cmds.confirmDialog(title='Warning',message='Please type something for the prompt.',button=['OK'],defaultButton='OK',cancelButton='OK',dismissString='OK')
            return

        try:
            if  self.video_widget is not None:
                self.theMainWidget.play_pushButton.setText('Play')
                self.video_widget.release()
                self.switch = True

        except:
            pass   
        
        
        self.worker = VideoGenerationWorker(self.theMainWidget.model_comboBox, self.theMainWidget.prompt_plainTextEdit, self.theMainWidget.generate_preview_pushButton, self.theMainWidget.import_fbx_pushButton )
        self.worker.video_generated.connect(self.on_video_generated)
        self.worker.start()        

 
    
    def on_video_generated(self):    
        self.verticalLayout = self.findChild(QtWidgets.QLayout, "verticalLayout")

        mp4_video_file = os.path.join(self.temp_folder, 'animation_generator','animation','out.mp4')
        self.video_widget = VideoWidget(mp4_video_file)
        self.verticalLayout.addWidget(self.video_widget)

                
               
    def play_media(self):
        if self.switch:
            self.video_widget.media_player.play()
            self.theMainWidget.play_pushButton.setText('Pause')
            self.switch = False
        else:
            self.video_widget.media_player.pause()
            self.theMainWidget.play_pushButton.setText('Play')
            self.switch = True

    def import_fbx(self):
        self.theMainWidget.generate_preview_pushButton.setEnabled(False)
        self.theMainWidget.prompt_plainTextEdit.setEnabled(False)
        self.theMainWidget.model_comboBox.setEnabled(False)
        self.theMainWidget.import_fbx_pushButton.setEnabled(False)
        temp_folder = os.getenv('TEMP')
        progress_file = os.path.join(temp_folder, 'animation_generator', 'progress.txt')
        if os.path.exists(progress_file):
            os.remove(progress_file)

        self.timer.start(500)
        self.worker = ImportFbxWorker()
        self.worker.fbx_imported.connect(self.on_fbx_imported)
        self.worker.start() 

    def on_fbx_imported(self):
        self.theMainWidget.generate_preview_pushButton.setEnabled(True)
        self.theMainWidget.prompt_plainTextEdit.setEnabled(True)
        self.theMainWidget.model_comboBox.setEnabled(True)
        self.theMainWidget.import_fbx_pushButton.setEnabled(True)
        options = "v=0;"
        import_frame_rate = True
        import_time_range = "override"
        root_objects = cmds.ls(assemblies=True)
        if py_ver==3:
            TEMPLATE_FILE = RETARGET_TEMPLATE_FILE+'/retarget_HIK.ma'
        else:
            TEMPLATE_FILE = RETARGET_TEMPLATE_FILE+'/retarget_HIK_2020.ma'
        # print(RETARGET_TEMPLATE_FILE)
        if 'animation_generator_ref' not in root_objects:
            cmds.file(TEMPLATE_FILE, i=True, options=options, pr=True, importFrameRate=import_frame_rate, importTimeRange=import_time_range)
        self.read_bvh()

    def read_bvh(self, *_args):
        # Safe close is needed for End Site part to keep from setting new
        # parent.
        safe_close = False
        # Once motion is active, animate.
        motion = False
        # Clear channels before appending
        self._channels = []

        # Scale the entire rig and animation

        frame = 0 
        rot_order = 0 
        
        self.root_node = '|animation_generator_ref|Hips'
        
        temp_folder = os.getenv('TEMP')
        self.bvh_filename =  os.path.join(temp_folder, 'animation_generator','bvh_folder','out.bvh')
             
        with open(self.bvh_filename) as f:
            # Check to see if the file is valid (sort of)
            if not f.readline().startswith("HIERARCHY"):
                cmds.error("No valid .bvh file selected.")
                return False

            my_parent = TinyDAG(self.root_node, None)
            self.clear_animation()
            print('Tiny')
            for line in f:
                line = line.replace("	", " ")  # force spaces
                if not motion:
                    # root joint
                    if line.startswith("ROOT"):
                        my_parent = TinyDAG(str(self.root_node), None)
                    if "JOINT" in line:
                        jnt = space_re.split(line.strip())
                        # Create the joint
                        my_parent = TinyDAG(jnt[1], my_parent)

                    if "End Site" in line:
                        # Finish up a hierarchy and ignore a closing bracket
                        safe_close = True

                    if "}" in line:
                        # Ignore when safeClose is on
                        if safe_close:
                            safe_close = False
                            continue

                        # Go up one level
                        if my_parent is not None:
                            my_parent = my_parent.parent
                            if my_parent is not None:
                                cmds.select(my_parent.full_path())

                    if "CHANNELS" in line:
                        chan = line.strip()
                        chan = space_re.split(chan)

                        # Append the channels that are animated
                        for i in range(int(chan[1])):
                            self._channels.append("%s.%s" % (
                                my_parent.full_path(),
                                translationDict[chan[2 + i]]
                            ))

                    if "OFFSET" in line and safe_close == False:
                        offset = line.strip()
                        offset = space_re.split(offset)
                        jnt_name = str(my_parent)

                        # When End Site is reached, name it "_tip"
                        if safe_close:
                            jnt_name += "_tip"

                        # skip if exists
                        if cmds.objExists(my_parent.full_path()):
                            jnt = my_parent.full_path()
                        else:
                            # Build a new joint
                            jnt = cmds.joint(name=jnt_name, p=(0, 0, 0))

                        cmds.setAttr(jnt + ".rotateOrder", rot_order)
                        cmds.setAttr(
                            jnt + ".translate",
                            float(offset[1]),
                            float(offset[2]),
                            float(offset[3])
                        )

                    if "MOTION" in line:
                        # Animate!
                        motion = True

                else:
                    # We don't really need to use Frame count and time
                    # (since Python handles file reads nicely)
                    if "Frame" not in line:
                        data = space_re.split(line.strip())
                        # Set the values to channels
                        for index, value in enumerate(data):
                            cmds.setKeyframe(self._channels[index],
                                           time=frame,
                                           value=float(value))

                        frame = frame + 1
        self.theMainWidget.simplify_anim_curve_pushButton.setEnabled(True)

    def clear_animation(self):
        # Select hierarchy
        cmds.select(str(self.root_node), hi=True)
        nodes = cmds.ls(sl=True)

        trans_attrs = ["translateX", "translateY", "translateZ"]
        rot_attrs = ["rotateX", "rotateY", "rotateZ"]
        for node in nodes:
            for attr in trans_attrs + rot_attrs:
                # Delete input connections
                connections = cmds.listConnections("%s.%s" % (node, attr),
                                                 s=True,
                                                 d=False)
                if connections is not None:
                    cmds.delete(connections)

            for attr in rot_attrs:
                # Reset rotation
                cmds.setAttr("%s.%s" % (node, attr), 0)


try:
    ui.deleteLater()
except:
    pass
ui = AnimationGPT()

def main():
    ui.show()



    