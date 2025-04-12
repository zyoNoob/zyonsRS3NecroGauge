from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QVBoxLayout,
    QSlider,
    QPushButton,
    QShortcut,
    QGroupBox,
    QLineEdit,
    QComboBox
    )
from PyQt5.QtGui import (
    QPixmap,
    QImage,
    QKeySequence
    )
import cv2
import numpy as np
import mss
import json
import sys
import os
import pygame
import re
import time

# Initialize pygame mixer for sound
pygame.mixer.init()

if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

config_path = 'config.json'

def loadConfig():
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        return {}

def saveConfig(config):
    with open(config_path, 'w') as f:
        json.dump(config, f)

def getAvailableResolutions():
    resolutions = []
    for folder in os.listdir(os.path.join(base_path, 'assets')):
        if re.match(r'reso_*', folder):
            resolutions.append(folder)
    return resolutions

def getWindowsScalingOptions(resolution):
    scaling_options = []
    path = os.path.join(base_path, 'assets', resolution)
    if os.path.exists(path):
        for folder in os.listdir(path):
            scaling_options.append(folder)
    return scaling_options

def getBuffbarSizeOptions(resolution, windows_scaling):
    buffbar_sizes = []
    path = os.path.join(base_path, 'assets', resolution, windows_scaling)
    if os.path.exists(path):
        for folder in os.listdir(path):
            buffbar_sizes.append(folder)
    return buffbar_sizes

config = loadConfig()

preconfigured = bool(config)

main_roi = config.get('main_roi', {'left': 0, 'top': 0, 'width': 795, 'height': 160})
scale = config.get('scale', 1/6.5)
image_position = config.get('image_position', {'x': 0, 'y': 0})
resolution = config.get('resolution', 'reso_3840x2160')
windows_scaling = config.get('windows_scaling', 150)
buffbar_size = config.get('buffbar_size', 'medium')
update_rate = config.get('update_rate', 50)

# Default to tracking all buffs
track_souls = config.get('track_souls', True)
track_necrosis = config.get('track_necrosis', True)
track_deathsparks = config.get('track_deathsparks', True)

asset_path_prefix = os.path.join(base_path, 'assets', resolution, str(windows_scaling), buffbar_size)

soul_alert_sound_path = os.path.join(base_path, 'assets', 'soul_alert.wav')
necrosis_alert_sound_path = os.path.join(base_path, 'assets', 'necrosis_alert.wav')

class ImageDisplay(QWidget):
    def __init__(self):
        super().__init__()

        self.soul_count = 0
        self.necrosis_count = 0
        self.deathspark_count = 0

        self.soul_alert_played = False
        self.necrosis_alert_played = False

        self.template_list_souls = []
        self.template_list_necrosis = []
        self.template_list_deathsparks = []

        self.modular_render_assets = {'souls':{},'necrosis':{},'deathsparks':{}}
        self.loadModularRenderAssets()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('RS3 Necro Gauge')
        self.setGeometry(0, 0, self.screen().size().width(), self.screen().size().height())
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        if preconfigured:
            self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
            self.setAttribute(QtCore.Qt.WA_NoChildEventsForParent, True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.image_label = QLabel(self)
        self.image_label.setGeometry(0, 0, self.screen().size().width(), self.screen().size().height())

        if preconfigured:
            # Apply saved settings directly
            self.applyConfig(config)
            self.roi_confirmed = True
        else:
            self.roi_confirmed = True
            self.initResolutionStep()

        self.shortcut = QShortcut(QKeySequence("Ctrl+Shift+Q"), self)
        self.shortcut.activated.connect(self.closeApplication)

        self.showFrame()

        self.soul_count = 0
        self.necrosis_count = 0

    def initResolutionStep(self):
        self.slider_box = QGroupBox("Resolution Settings", self)
        self.slider_box.setGeometry(800, 200, 500, 200)
        self.slider_layout = QVBoxLayout()
        self.slider_box.setLayout(self.slider_layout)
        self.slider_box.setStyleSheet("background-color: rgba(255, 255, 255, 150);")  # Semi-transparent background

        # Resolution Dropdown
        self.resolution_dropdown = QComboBox(self)
        self.resolution_dropdown.addItems(getAvailableResolutions()+['custom'])
        self.resolution_label = QLabel('Resolution')
        self.slider_layout.addWidget(self.resolution_label)
        self.slider_layout.addWidget(self.resolution_dropdown)

        self.confirmResolution_button = QPushButton('Confirm')
        self.confirmResolution_button.clicked.connect(self.confirmResolution)
        self.slider_layout.addWidget(self.confirmResolution_button)

    def confirmResolution(self):
        global config
        config['resolution'] = self.resolution_dropdown.currentText()

        self.resolution_label.setParent(None)
        self.resolution_dropdown.setParent(None)
        self.confirmResolution_button.setParent(None)
        self.slider_box.setTitle("Window Scaling Settings")


        if self.resolution_dropdown.currentText() == 'custom':
            self.slider_box.setGeometry(800, 200, 500, 200)
            self.initUpdateRateStep()
        else:
            self.slider_box.setGeometry(800, 200, 500, 200)
            self.initWindowsScalingStep()

    def initWindowsScalingStep(self):
        # Window Scaling Dropdown
        self.windows_scaling_dropdown = QComboBox(self)
        self.updateWindowsScalingOptions()
        self.windows_scaling_label = QLabel('Window Scaling')
        self.slider_layout.addWidget(self.windows_scaling_label)
        self.slider_layout.addWidget(self.windows_scaling_dropdown)

        self.confirmWindowsScaling_button = QPushButton('Confirm')
        self.confirmWindowsScaling_button.clicked.connect(self.confirmWindowsScaling)
        self.slider_layout.addWidget(self.confirmWindowsScaling_button)

    def confirmWindowsScaling(self):
        global config
        config['windows_scaling'] = self.windows_scaling_dropdown.currentText()

        self.windows_scaling_label.setParent(None)
        self.windows_scaling_dropdown.setParent(None)
        self.confirmWindowsScaling_button.setParent(None)
        self.slider_box.setTitle("Buffbar Size Settings")
        self.slider_box.setGeometry(800, 200, 500, 200)

        self.initBuffbarSizeStep()

    def initBuffbarSizeStep(self):
        # Buffbar Size Dropdown
        self.buffbar_size_dropdown = QComboBox(self)
        self.updateBuffbarSizeOptions()
        self.buffbar_size_label = QLabel('Buffbar Size')
        self.slider_layout.addWidget(self.buffbar_size_label)
        self.slider_layout.addWidget(self.buffbar_size_dropdown)

        self.confirmBuffbarSize_button = QPushButton('Confirm')
        self.confirmBuffbarSize_button.clicked.connect(self.confirmBuffbarSize)
        self.slider_layout.addWidget(self.confirmBuffbarSize_button)

    def confirmBuffbarSize(self):
        global config
        config['buffbar_size'] = self.buffbar_size_dropdown.currentText()

        self.buffbar_size_label.setParent(None)
        self.buffbar_size_dropdown.setParent(None)
        self.confirmBuffbarSize_button.setParent(None)
        self.slider_box.setTitle("Update Rate Settings")
        self.slider_box.setGeometry(800, 200, 500, 200)

        self.initUpdateRateStep()

    def initUpdateRateStep(self):
        # Update Rate Slider + Text Box
        self.update_rate_slider = QSlider(Qt.Horizontal)
        self.update_rate_slider.setRange(10, 1000)  # Range in milliseconds
        self.update_rate_slider.setValue(50)  # Default update rate
        self.update_rate_label = QLabel(f'Update Rate: {self.update_rate_slider.value()} ms')
        self.update_rate_textbox = QLineEdit(self)
        self.update_rate_textbox.setText(str(self.update_rate_slider.value()))
        self.update_rate_slider.valueChanged.connect(self.updateRateChanged)
        self.update_rate_textbox.textChanged.connect(self.updateRateTextChanged)

        self.slider_layout.addWidget(self.update_rate_label)
        self.slider_layout.addWidget(self.update_rate_slider)
        self.slider_layout.addWidget(self.update_rate_textbox)

        self.confirmUpdateRate_button = QPushButton('Confirm')
        self.confirmUpdateRate_button.clicked.connect(self.confirmUpdateRate)
        self.slider_layout.addWidget(self.confirmUpdateRate_button)

        # self.main_layout.addWidget(self.slider_box)

    def confirmUpdateRate(self):
        global config
        config['update_rate'] = self.update_rate_slider.value()

        self.update_rate_label.setParent(None)
        self.update_rate_slider.setParent(None)
        self.update_rate_textbox.setParent(None)
        self.confirmUpdateRate_button.setParent(None)
        self.slider_box.setTitle("Buff Tracking Settings")
        self.slider_box.setGeometry(800, 200, 500, 250)

        self.initBuffTrackingStep()

    def initBuffTrackingStep(self):
        # Create checkboxes for each buff type
        from PyQt5.QtWidgets import QCheckBox

        self.track_souls_checkbox = QCheckBox("Track Soul Stacks")
        self.track_souls_checkbox.setChecked(True)
        self.slider_layout.addWidget(self.track_souls_checkbox)

        self.track_necrosis_checkbox = QCheckBox("Track Necrosis Stacks")
        self.track_necrosis_checkbox.setChecked(True)
        self.slider_layout.addWidget(self.track_necrosis_checkbox)

        self.track_deathsparks_checkbox = QCheckBox("Track Death Spark Stacks")
        self.track_deathsparks_checkbox.setChecked(True)
        self.slider_layout.addWidget(self.track_deathsparks_checkbox)

        self.confirmBuffTracking_button = QPushButton('Confirm')
        self.confirmBuffTracking_button.clicked.connect(self.confirmBuffTracking)
        self.slider_layout.addWidget(self.confirmBuffTracking_button)

    def confirmBuffTracking(self):
        global config
        config['track_souls'] = self.track_souls_checkbox.isChecked()
        config['track_necrosis'] = self.track_necrosis_checkbox.isChecked()
        config['track_deathsparks'] = self.track_deathsparks_checkbox.isChecked()

        self.track_souls_checkbox.setParent(None)
        self.track_necrosis_checkbox.setParent(None)
        self.track_deathsparks_checkbox.setParent(None)
        self.confirmBuffTracking_button.setParent(None)
        self.slider_box.setTitle("Main ROI Settings")
        self.slider_box.setGeometry(800, 200, 500, 400)

        self.initMainROIStep()

    def initMainROIStep(self):
        self.roi_confirmed = False
        self.update()
        # ROI Sliders
        self.main_roi_sliders = {
            'left': QSlider(Qt.Horizontal),
            'top': QSlider(Qt.Horizontal),
            'width': QSlider(Qt.Horizontal),
            'height': QSlider(Qt.Horizontal)
        }
        self.main_roi_labels = {
            'left': QLabel('Left'),
            'top': QLabel('Top'),
            'width': QLabel('Width'),
            'height': QLabel('Height')
        }
        self.main_roi_sliders['left'].setRange(0, self.screen().size().width())
        self.main_roi_sliders['top'].setRange(0, self.screen().size().height())
        self.main_roi_sliders['width'].setRange(0, self.screen().size().width())
        self.main_roi_sliders['height'].setRange(0, self.screen().size().height())

        for key, slider in self.main_roi_sliders.items():
            slider.setValue(main_roi[key])
            slider.valueChanged.connect(self.updateROI)

        self.confirmROI_button = QPushButton('Confirm')
        self.confirmROI_button.clicked.connect(self.confirmROI)

        for key in self.main_roi_sliders.keys():
            self.slider_layout.addWidget(self.main_roi_labels[key])
            self.slider_layout.addWidget(self.main_roi_sliders[key])
        self.slider_layout.addWidget(self.confirmROI_button)

    def confirmROI(self):
        global config, main_roi
        config['main_roi'] = main_roi

        for key, slider in self.main_roi_sliders.items():
            slider.setParent(None)
            self.main_roi_labels[key].setParent(None)
        self.confirmROI_button.setParent(None)
        self.slider_box.setTitle("Image Settings")
        self.slider_box.setGeometry(800, 200, 500, 350)

        self.initScaleAndLocationStep()

    def initScaleAndLocationStep(self):
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(1, 100)
        self.scale_slider.setValue(int(scale * 100))
        self.scale_slider.valueChanged.connect(self.updateImageProperties)

        self.x_slider = QSlider(Qt.Horizontal)
        self.x_slider.setRange(0, self.width())
        self.x_slider.setValue(image_position['x'])
        self.x_slider.valueChanged.connect(self.updateImageProperties)

        self.y_slider = QSlider(Qt.Horizontal)
        self.y_slider.setRange(0, self.height())
        self.y_slider.setValue(image_position['y'])
        self.y_slider.valueChanged.connect(self.updateImageProperties)

        self.confirm_image_button = QPushButton('Confirm Image Settings')
        self.confirm_image_button.clicked.connect(self.confirmImageSettings)

        self.slider_layout.addWidget(QLabel('Scale'))
        self.slider_layout.addWidget(self.scale_slider)
        self.slider_layout.addWidget(QLabel('X Position'))
        self.slider_layout.addWidget(self.x_slider)
        self.slider_layout.addWidget(QLabel('Y Position'))
        self.slider_layout.addWidget(self.y_slider)
        self.slider_layout.addWidget(self.confirm_image_button)

    def updateImageProperties(self):
        global scale, image_position, track_souls, track_necrosis, track_deathsparks

        # Update scale
        scale = self.scale_slider.value() / 100.0

        # Update position
        image_position['x'] = self.x_slider.value()
        image_position['y'] = self.y_slider.value()

        # Start with a blank image (all zeros)
        frame = None

        # Only add the buffs that are being tracked
        if track_souls:
            if frame is None:
                frame = self.modular_render_assets['souls'][self.soul_count].copy()
            else:
                frame = frame + self.modular_render_assets['souls'][self.soul_count]

        if track_necrosis:
            if frame is None:
                frame = self.modular_render_assets['necrosis'][self.necrosis_count].copy()
            else:
                frame = frame + self.modular_render_assets['necrosis'][self.necrosis_count]

        if track_deathsparks:
            if frame is None:
                frame = self.modular_render_assets['deathsparks'][self.deathspark_count].copy()
            else:
                frame = frame + self.modular_render_assets['deathsparks'][self.deathspark_count]

        # If no buffs are being tracked, use a blank image
        if frame is None:
            # Create a blank transparent image with the same dimensions as the buff images
            sample_image = next(iter(self.modular_render_assets['souls'].values()))
            frame = np.zeros_like(sample_image)

        cv2image = cv2.cvtColor(cv2.resize(frame, (int(frame.shape[1] * scale), int(frame.shape[0] * scale))), cv2.COLOR_BGRA2RGBA)
        image = Image.fromarray(cv2image, mode="RGBA")

        # Convert the PIL image to a format suitable for QPixmap
        data = image.tobytes("raw", "RGBA")
        q_image = QImage(data, image.width, image.height, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(q_image)

        # Update the QPixmap of the label
        self.image_label.setPixmap(pixmap)
        self.image_label.setFixedSize(pixmap.size())
        self.image_label.setGeometry(self.x_slider.value(), self.y_slider.value(), cv2image.shape[0], cv2image.shape[1])

    def updateROI(self):
        global main_roi
        for key, slider in self.main_roi_sliders.items():
            main_roi[key] = slider.value()
        self.update()

    def loadModularRenderAssets(self):
        if preconfigured:
            for i in range(0, 6):
                img_buffer = cv2.imread(os.path.join(base_path, 'assets', f'modular_render_assets\\s{i}.png'), cv2.IMREAD_UNCHANGED)
                self.modular_render_assets['souls'][i] = cv2.resize(img_buffer, (int(img_buffer.shape[1] * scale), int(img_buffer.shape[0] * scale)))
            for i in [0, 2, 4, 6, 8, 10, 12]:
                img_buffer = cv2.imread(os.path.join(base_path, 'assets', f'modular_render_assets\\n{i}.png'), cv2.IMREAD_UNCHANGED)
                self.modular_render_assets['necrosis'][i] = cv2.resize(img_buffer, (int(img_buffer.shape[1] * scale), int(img_buffer.shape[0] * scale)))
            for i in range(0, 6):
                img_buffer = cv2.imread(os.path.join(base_path, 'assets', f'modular_render_assets\\ds{i}.png'), cv2.IMREAD_UNCHANGED)
                self.modular_render_assets['deathsparks'][i] = cv2.resize(img_buffer, (int(img_buffer.shape[1] * scale), int(img_buffer.shape[0] * scale)))
        else:
            for i in range(0, 6):
                self.modular_render_assets['souls'][i] = cv2.imread(os.path.join(base_path, 'assets', f'modular_render_assets\\s{i}.png'), cv2.IMREAD_UNCHANGED)
            for i in [0, 2, 4, 6, 8, 10, 12]:
                self.modular_render_assets['necrosis'][i] = cv2.imread(os.path.join(base_path, 'assets', f'modular_render_assets\\n{i}.png'), cv2.IMREAD_UNCHANGED)
            for i in range(0, 6):
                self.modular_render_assets['deathsparks'][i] = cv2.imread(os.path.join(base_path, 'assets', f'modular_render_assets\\ds{i}.png'), cv2.IMREAD_UNCHANGED)

    def updateRateChanged(self):
        value = self.update_rate_slider.value()
        self.update_rate_label.setText(f'Update Rate: {value} ms')
        self.update_rate_textbox.setText(str(value))

    def updateRateTextChanged(self):
        try:
            value = int(self.update_rate_textbox.text())
        except:
            value = 0
        self.update_rate_slider.setValue(value)
        self.update_rate_label.setText(f'Update Rate: {value} ms')

    def updateWindowsScalingOptions(self):
        self.windows_scaling_dropdown.clear()
        resolution = self.resolution_dropdown.currentText()
        scaling_options = getWindowsScalingOptions(resolution)
        self.windows_scaling_dropdown.addItems(scaling_options)

    def updateBuffbarSizeOptions(self):
        self.buffbar_size_dropdown.clear()
        resolution = self.resolution_dropdown.currentText()
        windows_scaling = self.windows_scaling_dropdown.currentText()
        buffbar_sizes = getBuffbarSizeOptions(resolution, windows_scaling)
        self.buffbar_size_dropdown.addItems(buffbar_sizes)

    def confirmImageSettings(self):
        global config, scale, image_position
        config['scale'] = scale
        config['image_position'] = image_position

        if config['resolution'] == 'custom':
            os.makedirs('custom_assets', exist_ok=True)
            config['windows_scaling'] = ''
            config['buffbar_size'] = ''

            saveConfig(config)

            self.scale_slider.setParent(None)
            self.x_slider.setParent(None)
            self.y_slider.setParent(None)
            self.confirm_image_button.setParent(None)
            self.slider_box.setParent(None)

            exit()
        else:
            saveConfig(config)

            self.scale_slider.setParent(None)
            self.x_slider.setParent(None)
            self.y_slider.setParent(None)
            self.confirm_image_button.setParent(None)
            self.slider_box.setParent(None)

            # Make the entire application click-through
            self.restartApplication()

    def applyConfig(self, config):
        global scale, image_position, main_roi, resolution, windows_scaling, buffbar_size, update_rate, asset_path_prefix
        global track_souls, track_necrosis, track_deathsparks
        main_roi = config.get('main_roi', {'left': 1520, 'top': 1660, 'width': 795, 'height': 160})
        scale = config.get('scale', 1/6.5)
        image_position = config.get('image_position', {'x': 0, 'y': 0})
        resolution = config.get('resolution', 'reso_3840x2160')
        windows_scaling = config.get('windows_scaling', 150)
        buffbar_size = config.get('buffbar_size', 'medium')
        update_rate = config.get('update_rate', 50)
        track_souls = config.get('track_souls', True)
        track_necrosis = config.get('track_necrosis', True)
        track_deathsparks = config.get('track_deathsparks', True)
        if resolution == 'custom':
            asset_path_prefix = os.path.join('custom_assets', str(windows_scaling), buffbar_size)
        else:
            asset_path_prefix = os.path.join(base_path, 'assets', resolution, str(windows_scaling), buffbar_size)

        for i in range(1, 6):
            self.template_list_souls.append(cv2.imread(os.path.join(asset_path_prefix, f'soul_{i}.png'), cv2.IMREAD_COLOR))
            self.template_list_souls.append(cv2.imread(os.path.join(asset_path_prefix, f'soul_{i}_alt.png'), cv2.IMREAD_COLOR))
        for i in [2, 4, 6, 8, 10, 12]:
            self.template_list_necrosis.append(cv2.imread(os.path.join(asset_path_prefix, f'necrosis_{i}.png'), cv2.IMREAD_COLOR))
        for i in range(1, 6):
            self.template_list_deathsparks.append(cv2.imread(os.path.join(asset_path_prefix, f'deathspark_{i}.png'), cv2.IMREAD_COLOR))

        self.show()

        self.updateStacks()

    def showFrame(self):
        # start_time = time.time()
        global scale, image_position, track_souls, track_necrosis, track_deathsparks

        # Start with a blank image (all zeros)
        stacked_image = None

        # Only add the buffs that are being tracked
        if track_souls:
            if stacked_image is None:
                stacked_image = self.modular_render_assets['souls'][self.soul_count].copy()
            else:
                stacked_image = stacked_image + self.modular_render_assets['souls'][self.soul_count]

        if track_necrosis:
            if stacked_image is None:
                stacked_image = self.modular_render_assets['necrosis'][self.necrosis_count].copy()
            else:
                stacked_image = stacked_image + self.modular_render_assets['necrosis'][self.necrosis_count]

        if track_deathsparks:
            if stacked_image is None:
                stacked_image = self.modular_render_assets['deathsparks'][self.deathspark_count].copy()
            else:
                stacked_image = stacked_image + self.modular_render_assets['deathsparks'][self.deathspark_count]

        # If no buffs are being tracked, use a blank image
        if stacked_image is None:
            # Create a blank transparent image with the same dimensions as the buff images
            sample_image = next(iter(self.modular_render_assets['souls'].values()))
            stacked_image = np.zeros_like(sample_image)

        if preconfigured:
            cv2image = cv2.cvtColor(stacked_image, cv2.COLOR_BGRA2RGBA)
        else:
            cv2image = cv2.cvtColor(cv2.resize(stacked_image, (int(stacked_image.shape[1] * scale), int(stacked_image.shape[0] * scale))), cv2.COLOR_BGRA2RGBA)
        image = Image.fromarray(cv2image, mode="RGBA")

        data = image.tobytes("raw", "RGBA")
        q_image = QImage(data, image.width, image.height, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(q_image)

        self.image_label.setPixmap(pixmap)
        self.image_label.setFixedSize(pixmap.size())
        self.image_label.move(image_position['x'], image_position['y'])
        # print((time.time()-start_time)*1000)

    def captureScreen(self):
        with mss.mss() as sct:
            screenshot = sct.grab(main_roi)
            return np.array(screenshot)

    def findImage(self, template, screenshot):
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        h, w = template_gray.shape
        top_left = max_loc
        return top_left[0], top_left[1], w, h, max_val

    def matchTemplates(self, template_list, game_screen):
        score_list = []
        match_list = []
        for template in template_list:
            M = self.findImage(template, game_screen)
            match_list.append(M)
            score_list.append(M[-1])
        max_index, max_value = max(enumerate(score_list), key=lambda x: x[1])
        return max_index, max_value, match_list

    def updateStacks(self):
        global track_souls, track_necrosis, track_deathsparks
        game_screen = self.captureScreen()
        try:
            with ThreadPoolExecutor() as executor:
                # Only process the buffs that are being tracked
                futures = {}

                if track_souls:
                    futures['souls'] = executor.submit(self.matchTemplates, self.template_list_souls, game_screen)

                if track_necrosis:
                    futures['necrosis'] = executor.submit(self.matchTemplates, self.template_list_necrosis, game_screen)

                if track_deathsparks:
                    futures['deathsparks'] = executor.submit(self.matchTemplates, self.template_list_deathsparks, game_screen)

                # Process results for tracked buffs
                if 'souls' in futures:
                    max_index_souls, max_value_souls, _ = futures['souls'].result()
                    if max_value_souls > 0.9:
                        self.soul_count = (max_index_souls // 2) + 1
                    else:
                        self.soul_count = 0

                if 'necrosis' in futures:
                    max_index_necrosis, max_value_necrosis, _ = futures['necrosis'].result()
                    if max_value_necrosis > 0.9:
                        self.necrosis_count = (max_index_necrosis + 1) * 2
                    else:
                        self.necrosis_count = 0

                if 'deathsparks' in futures:
                    max_index_deathsparks, max_value_deathsparks, _ = futures['deathsparks'].result()
                    if max_value_deathsparks > 0.9:
                        self.deathspark_count = (max_index_deathsparks + 1)
                    else:
                        self.deathspark_count = 0

            self.showFrame()

            # Only play alerts for tracked buffs
            if track_souls and self.soul_count == 5 and not self.soul_alert_played:
                self.playAlert('soul')
                self.soul_alert_played = True
            elif not track_souls or self.soul_count < 5:
                self.soul_alert_played = False

            if track_necrosis and self.necrosis_count == 12 and not self.necrosis_alert_played:
                self.playAlert('necrosis')
                self.necrosis_alert_played = True
            elif not track_necrosis or self.necrosis_count < 12:
                self.necrosis_alert_played = False

        except Exception as e:
            print(f"An error occurred: {e}")

        QTimer.singleShot(update_rate, self.updateStacks)

    def playAlert(self, type):
        if type == 'soul':
            pygame.mixer.music.load(soul_alert_sound_path)
            pygame.mixer.music.play()
        elif type == 'necrosis':
            pygame.mixer.music.load(necrosis_alert_sound_path)
            pygame.mixer.music.play()

    def closeApplication(self):
        pygame.mixer.music.stop()
        self.close()

    def paintEvent(self, event):
        if not self.roi_confirmed:
            painter = QtGui.QPainter(self)
            pen = QtGui.QPen(QtGui.QColor(0, 255, 255))
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawRect(main_roi['left'], main_roi['top'], main_roi['width'], main_roi['height'])
        super().paintEvent(event)

    def restartApplication(self):
        """Restart the current script, with file objects and descriptors cleanup"""
        try:
            print("Restarting script...")
            # Close all file descriptors to avoid issues with open files
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            print(f"Error restarting script: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageDisplay()
    ex.show()
    sys.exit(app.exec_())