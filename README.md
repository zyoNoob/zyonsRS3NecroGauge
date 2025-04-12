![appicon](https://github.com/zyoNoob/zyonsRS3NecroGauge/assets/32070378/780658cd-8c41-4d83-a1f5-4d770a3497b1)
# What is RS3 Necro Gauge?

RS3 Necro Gauge is a UI plugin that allows RuneScape 3 players to track their Necromancy stackable buffs with improved visuals and sound alerts.

# Why? Don't we already have enough of these?

I will break down the reasoning behind creating a new Necro Gauge when there are already multiple available via the Alt-1 Toolkit.

1. **FPS Impact:** Alt-1 inherently causes a net FPS (frames per second) loss for most users, which becomes more pronounced at higher resolutions.
2. **Compatibility Limitations:** Alt-1 is only compatible with the following:
    - Interface Scaling - `100%`
    - Buff Bar - `small`

Due to these limitations, I created a new Necro Gauge to improve the quality of life for players. My plugin works with the following settings with minimal FPS impact :
- Any resolution
- Any Windows display scaling
- Any buff bar size
- Any interface scaling

# Will it run on my PC?

This depends on your operating system:
- **Windows PC:** Yes
- **MacOS/Linux:** No (Implementation for these systems is possible but I won't be doing it for now.)

# Do I need a GPU to run this?

No! All processing is done using the CPU of your computer.

# Features and Demo

This app supports the following customizations with presets provided by me:
1. Resolution
2. Windows Display Scaling
3. Buff Bar Size
4. Update Rate (How frequently the app updates its state, default is 50ms)
5. Selective Buff Tracking (Choose which buffs you want to track and display)

Interface scaling is not a preset parameter since it can vary greatly. To work with other than `100%` scaling, a custom preset will need to be made.

## Tracked Buffs

The app tracks the following Necromancy buffs:
1. **Soul Stacks** - Tracks up to 5 soul stacks with visual and audio alerts when maxed
2. **Necrosis Stacks** - Tracks up to 12 necrosis stacks with visual and audio alerts when maxed
3. **Death Spark Stacks** - Tracks up to 5 death spark stacks

If you are not satisfied with the provided customizations or presets, you will need to manually set up a custom preset. Details on how to do this are below.

If you dislike the audio alerts, you can disable them using the Windows audio mixer or change the sound of the alert by following the first approach listed below.

Here is a short clip showing how the app looks and sounds.


https://github.com/zyoNoob/zyonsRS3NecroGauge/assets/32070378/41950af6-2021-4b14-afbe-b87d29a06fdc



# How do I run it?

There are two ways to use this app:
1. Clone this repository or download the source code and run the Python script in a custom environment.
2. Download the executable provided in the releases for an easy, ready-to-use experience.

## If you decide to go with the first approach

Feel free to explore the code if you have privacy concerns. The project uses the following libraries which are available through PyPI:

- mss
- opencv-python
- pillow
- pygame
- pyinstaller
- pyqt5

### Environment Setup with uv

This project uses `uv` for Python environment management. Follow these steps to set up your environment:

1. Install uv following the instructions at [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
2. Clone this repository and navigate to the project directory
3. Create a virtual environment and install dependencies:
   ```
   uv sync
   ```

### Building the Executable

To build the executable, run the following command:

```
uv run pyinstaller --onefile --noconsole --add-data "assets:assets" necro_gauge.py --icon="assets\appicon.png"
```

This will create a standalone executable in the `dist` directory.

## For the more laid-back and average user, welcome to your own necromancy paradise :P

### Preset Based Setup

1. Download the app, store it in a separate folder, and launch it.
2. The app will open on your primary monitor and prompt you to select a resolution preset. Choose one from the dropdown and click confirm.
<div style="text-align: center;">
  <img src="media/resolution_select.png" alt="Resolution Selection" width="600">
  <p><em>Resolution Selection</em></p>
</div>

3. Select the Windows display scaling, which can be found in your system's display settings, and click confirm.
<div style="text-align: center;">
  <img src="media/display_scaling_select.png" alt="Display Scaling Selection" width="600">
  <p><em>Display Scaling Selection</em></p>
</div>

4. Select a buff bar size from the dropdown presets, matching your RuneScape 3 settings, and click confirm.
<div style="text-align: center;">
  <img src="media/buffbar_size_select.png" alt="Buffbar Size Selection" width="600">
  <p><em>Buffbar Size Selection</em></p>
</div>

5. Select update rate of the application in using the slider, or type a numerical value. This is the delay between each cycle of stack tracking measured in miliseconds (ms), and click confirm.
<div style="text-align: center;">
  <img src="media/update_rate_select.png" alt="Update Rate Selection" width="400">
  <p><em>Update Rate Selection</em></p>
</div>

6. Choose which buffs you want to track by checking or unchecking the corresponding checkboxes, and click confirm.
<div style="text-align: center;">
  <img src="media/buff_select.png" alt="Buff Tracking Selection" width="400">
  <p><em>Buff Tracking Selection</em></p>
</div>

7. **Scanning Region of Interest (Very Important):**
    - Use the sliders (left, top, width, height) to ensure the cyan rectangle on the screen covers your RuneScape buff bar completely.
    - Once done, click confirm.
<div style="text-align: center;">
  <img src="media/roi_selection.png" alt="Scanning Area Selection" width="600">
  <p><em>Scanning Area Selection</em></p>
</div>

8. Adjust the scale and position of your necro gauge using the sliders. Once satisfied, click confirm to save the settings in a config.json file in the application folder, and the application will restart to function properly.
<div style="text-align: center;">
  <img src="media/scale_and_position.png" alt="Customise the UI" width="600">
  <p><em>Customise Scale and Position</em></p>
</div>

*To quit the application, `Alt+Tab` into it and press `Ctrl+Shift+Q` or use the Task Manager to close it.*

### Custom Setup

1. Download the app, store it in a separate folder, and launch it.
2. The app will open on your primary monitor and prompt you to select a resolution preset. Choose 'custom' in the dropdown and click confirm.
<div style="text-align: center;">
  <img src="media/resolution_select.png" alt="Resolution Selection" width="600">
  <p><em>Resolution Selection</em></p>
</div>

3. Select update rate of the application in using the slider, or type a numerical value. This is the delay between each cycle of stack tracking measured in miliseconds (ms), and click confirm.
<div style="text-align: center;">
  <img src="media/update_rate_select.png" alt="Update Rate Selection" width="400">
  <p><em>Update Rate Selection</em></p>
</div>

4. Choose which buffs you want to track by checking or unchecking the corresponding checkboxes, and click confirm.
<div style="text-align: center;">
  <img src="media/buff_select.png" alt="Buff Tracking Selection" width="400">
  <p><em>Buff Tracking Selection</em></p>
</div>

5. **Scanning Region of Interest (Very Important):**
    - Use the sliders (left, top, width, height) to ensure the cyan rectangle on the screen covers your RuneScape buff bar completely.
    - Once done, click confirm.
<div style="text-align: center;">
  <img src="media/roi_selection.png" alt="Scanning Area Selection" width="600">
  <p><em>Scanning Area Selection</em></p>
</div>

6. Adjust the scale and position of your necro gauge using the sliders. Once satisfied, click confirm to save the settings in a config.json file in the application folder, and the application will exit.
<div style="text-align: center;">
  <img src="media/scale_and_position.png" alt="Customise the UI" width="600">
  <p><em>Customise Scale and Position</em></p>
</div>

*You have now completed 50% of the work for custom settings. The app exited because we still need to provide it with buff images for your custom settings.*

7. To create your own buff images, start by getting different numbers of souls and capturing screenshots of the soul buff in the buff bar. Crop the images into square PNGs using MS Paint (Photoshop is too expensive for this task). A good tip for doing this, all buffs have a green border, use that as a reference to get clean cropped images.
<div style="text-align: center;">
  <img src="media/custom_soul_demo.png" alt="Screenshot of buff bar" width="600">
  <p><em>Screenshot of buff bar</em></p>
</div>
<div style="text-align: center;">
  <img src="media/custom_soul_demo_cropped.png" alt="Screenshot of cropped 44x44pixel buff." width="50">
  <p><em>Screenshot of square cropped buff to be saves as `soul_1.png`, `soul_1_alt.png` in the `custom_assets` folder generated by the program.</em></p>
</div>

8. Rename the images using this scheme:
    - Soul stack image -> `soul_{soulcount}.png, soul_{soulcount}_alt.png` (e.g., `soul_2.png`, `soul_2_alt.png` for 2 soul stacks).
    - Necrosis stack image -> `necrosis_{necrosiscount}.png` (e.g., `necrosis_4.png` for 4 necrosis stacks).
    - Death spark stack image -> `deathspark_{sparkcount}.png` (e.g., `deathspark_3.png` for 3 death spark stacks).
9. Copy or move these renamed images to the `custom_assets` folder created by the app.
10. Ensure all images for soul count values `[1,2,3,4,5]`, necrosis count values `[2,4,6,8,10,12]`, and death spark count values `[1,2,3,4,5]` exist.
11. Once all steps are complete, run the program again with your custom image settings. It should work flawlessly.
12. You can look in the custom_assets folder of the repository for reference as to how the images are named.
