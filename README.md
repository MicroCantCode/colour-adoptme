# colour-adoptme

## Introduction
The original motivation behind this little project was for my own purpose: to automate the extraction of a Hex Colour code from an image to help me build in Adopt Me, Roblox, on my iPhone and iPad. That's all!

Although this is a personal project, I am putting it on here for reference in case anyone wants to use/fork it or do similar.

## Description
The script in the root of the project simply takes in an image file namem, which might be a screenshot or a photo, and outputs the most frequently occurring colour towards the centre of image.

Then it is up to you what you do with the output. For my Use Case, I integrated it into iOS shortcuts, placing the output on the Clipboard.

## Basic Usage
This example applies to Linuxy OS's and can be run from the built image in `containerfiles`.

From the directory where the script is located, run:

`./extract_colour_image.py <image_filename>`

which will output something like `e0d5ff`.

### `image_filename` input
 * The basename of the input file plus the extension. The extension may be omitted from the argument but MUST exist on the physical file.
 * Valid extensions are `.jpeg` and `.png`.
 * Supported image colour modes are RGB and RGBA.
 * The file is assumed to be in the working directory of the script.
 * The file is processed in read-mod.

### Hex Colour output
 * Is written to `stdout`.
 * Is fixed width, 6 bytes with each Hexadecimal code padded with a leading zero, where applicable.
 * Is lowercase.
 * Is unprefixed.
 * If extracting colour from screenshots, textures and lighting on destination objects may present the colour differently from the source.

## Using with iOS Shortcut Workflows
On iPhone and iPad, Pyto IDE was installed, which also integrates with Shortcuts to be able to run the script. Additional dependencies can be installed via `pip`, as listed in `containerfiles\requirements.txt`.

Unfortunately, Shortcut workflows are unable to be exported in something like XML, so cannot be version controlled. They can be frustrating to set up and seem limited, especially if you're more used to the flexibility of CICD tools in building sophisticated pipelines and workflows.

Points of note:

 * iOS versions and updates can affect shortcut behaviour so check when updating versions.
 * Image files may needs to be renamed after saving to remove hidden extensions.
 * `stderr` output from the script can't be separated from `stdout`.
 * Running the script from a Shortcut on iPad/iPhone is a non-blocking operation so explicit waits for output may be required to mitigate against race conditions.
 * Security on iPad/iPhones means you have very little control over process management and scheduling of tasks so stopping other processes on the device may help prevent time outs.
 * If invoking the script from different devices, but from the same storage (iCloud), files must be available on the local device. Mount points and paths may vary between devices so no assumptions should be made about absolute paths when running the script.
 * There is little control over exception handling or exit traps. Bear this in mind when ensuring workflow idempotency on steps such as file clean up (and don't forget to auto-cull unused image files!).

## Development
By preference, development is done in a Container, using the relevant VSCode extensions, to get a reproducible environment. Development container files are in `containerfiles` and should be automatically built via VSCode when it detects the `devcontainer.json`. All dependencies are installed into the local image. 

## Testing
Logic is tested using the `unittest` framework in python and can be run within the IDE or from `scripts/coverage.sh`, where you get the bonus of a coverage report!

## Future Work
Probably once I have invested in a proper computer, I will want to make improvements but I also have a lot of legendaries to age, which I really need to get cracking on with.