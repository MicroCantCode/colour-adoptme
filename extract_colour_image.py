"""Get most frequently occuring hex colour from centre of supplied image."""
import argparse
import pathlib
from functools import reduce
from os import path
import traceback

import numpy as np
from PIL import Image


class ColourExtractorBasic:
    """Extracts colour from a given image."""

    """How much to crop image by on both axes."""
    INITIAL_CROP_SIZE=50
    
    """List of supported image modes."""
    SUPPORTED_MODES=['RGB', 'RGBA']

    def get_colour(self, image_filename: str) -> str:
      """Gets colour as a hex string.
      Gets the most frequently occuring colour from the centre of the supplied 
      image.
      
      Does some basic processing to reduce, resample and retry in the unlikely event there is
      no dominant colour.

      Nearest neighbour algorithm is preferred on resampling for performance and fidelity reasons.
      
      Params:
        image_filename: Image file name as a string.

      Returns:
        A lowercase string containing the colour as a 6 digit hex number.
        No '0x' prefix. Where necessary, each channel will be padded with 
        a leading zero so the returned string will have a fixed width of 6 bytes.

      Raises:
        RuntimeError: Raised if no colour was extracted and no other exception was raised.
      """

      with Image.open(image_filename, mode='r') as img:

        if img.mode not in self.SUPPORTED_MODES:
          raise RuntimeError(f"Only {self.SUPPORTED_MODES} modes supported but got {img.mode}")

        crop_pxl_edge = self.INITIAL_CROP_SIZE
        cropped_img = img
        colour=None

        while crop_pxl_edge > 0: 
          width, height = cropped_img.size

          if all( i > crop_pxl_edge for i in [width, height] ):

            new_width = new_height = crop_pxl_edge

            # Cartesian coordinates
            crop_box = ( (width//2) - new_width//2,   # Left x coordinate
                    (height//2) - new_height//2, # Upper y coordinate
                    (width//2) + new_width//2,   # Right x coordinate
                    (height//2) + new_height//2) # Lower y coordinate

            # Don't use Image.Resampling.NEAREST attribute for 
            # library version compatibility reasons
            cropped_img = cropped_img.resize(size=(new_width, new_height),
                                             box=crop_box,
                                             resample=Image.NEAREST 
                                             )

          cropped_colours = cropped_img.getcolors(maxcolors=reduce((lambda w,h: w*h),cropped_img.size))
          colour_counts = [ (count, colour)
                           for count, colour in cropped_colours
                            if count == max(cropped_colours)[0] ]
                   
          if len(colour_counts) > 0:
            colour = colour_counts[0][1] 

          crop_pxl_edge = crop_pxl_edge//2 if len(colour_counts) > 1 else 0

        if colour:
          # if it exists here, alpha channel is ignored
          return  f"{colour[0]:02x}{colour[1]:02x}{colour[2]:02x}"
      
        raise RuntimeError('Unable to extract colour from image')

  
class ImageProcessor:
    """Manages colour extraction from an image file."""

    """List of supported image extensions."""
    VALID_SUFFICES = ['.jpeg', '.png']

    def __init__(self, image_filename: str, colour_extractor=ColourExtractorBasic()) -> None:
        """ImageProcessor constructor.
      
          Args:
            image_filename: Image file name as a string. 
            This is the basename of the file and is expected to reside in the working
            directory.
            The extension in the string is optional but the actual file MUST have one
            of the VALID_SUFFICES as an extension.

            colour_extractor: Currently only supports ColourExtractorBasic instance.
            Any future colour extractors will require the get_colour() method implementing.
        """
        self.__image_filename = self.__check_filename(
            image_filename=image_filename)
        self.__colour_extractor = colour_extractor

        if not colour_extractor:
            self.__colour_extractor = ColourExtractorBasic()

    @property
    def image_filename(self) -> str:
        """image_filename is basename plus extension."""
        return self.__image_filename

    def get_colour(self):
        """Gets the extracted colour hex string.
        
        Delegates extraction to its colour extractor instance.
        """
        return self.__colour_extractor.get_colour(self.image_filename)

    def __check_filename(self, image_filename: str) -> str:

        # Depending on how the script is invoked, the supplied image filename
        # may be missing the extension

        try:

            imagefilepath = pathlib.Path(image_filename)

            valid_file = [imagefilepath.with_suffix(ext)
                          for ext in self.VALID_SUFFICES
                          if path.isfile(imagefilepath.with_suffix(ext))]

        except ValueError as e:
            raise RuntimeError('Image filename value error.') from e
        
        except TypeError as e:
            raise RuntimeError('Image filename type error.') from e

        if not valid_file:
            raise RuntimeError(
                f"Could not find/access: {image_filename}")

        return valid_file[0].name


def read_args():

    desc = 'Extract colour as hexcode and send unprefixed to stdout.'
    parser = argparse.ArgumentParser(description=desc)

    # File validation is deferred as argument may be missing file extension
    parser.add_argument('imagefile',
                        type=str,
                        help='Image file name of screenshot to process expected to be in working dir.'
                        + 'Basename only and specifying the extension is optional.'
                        + f"{ImageProcessor.VALID_SUFFICES} and {ColourExtractorBasic.SUPPORTED_MODES} supported only")

    return parser.parse_args()

if __name__ == '__main__':

    try:
        args = read_args()
        image_proc = ImageProcessor(args.imagefile)
        print(image_proc.get_colour())
    except Exception as e:
        print(f"Something when wrong {e}")
        print(traceback.print_exc())
