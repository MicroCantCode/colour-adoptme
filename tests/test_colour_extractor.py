from dataclasses import dataclass
from unittest import TestCase
from unittest.mock import patch

import numpy as np
from PIL import Image

import extract_colour_image

@dataclass
class ImageMetadata:

  height: int
  width: int
  channels: int

  def size(self) -> int:
    return self.height * self.width * self.channels

class TestColourExtractorBasic(TestCase):


  def _colour_extraction_testing(self, image_data, crop_size, expected_colour_hex):

      with (patch('PIL.Image.open') as mock_image, 
            patch('os.path.isfile') as mock_isfile):
          
          img = Image.fromarray(image_data)

          mock_isfile.return_value = True
          mock_image.return_value = img

          extractor = extract_colour_image.ColourExtractorBasic()
          extractor.INITIAL_CROP_SIZE = crop_size
          actual_colour_hex = extractor.get_colour('image_file_is_mocked')

          self.assertEqual(actual_colour_hex, expected_colour_hex)

  def test_colours_extraction_different_height_width_crop_conditions(self):
      
    CHANNEL_SIZE=3

    test_data = [
                 ('colours equal frequency occurence',
                  ImageMetadata(height=10,width=8,channels=CHANNEL_SIZE),4,'848586'),
                 ('crop size same as height and width',
                  ImageMetadata(height=8,width=8,channels=CHANNEL_SIZE),8,'6c6d6e'),
                 ('crop size smaller than height and width',
                  ImageMetadata(height=7,width=7,channels=CHANNEL_SIZE),8,'48494a'),
                 ('crop size exceeds height and width',
                  ImageMetadata(height=4,width=4,channels=CHANNEL_SIZE),8,'1e1f20'),
                 ('crop size exceeds height',
                  ImageMetadata(height=4,width=16,channels=CHANNEL_SIZE),8,'78797a'),
                 ('crop size exceeds width',
                  ImageMetadata(height=16,width=4,channels=CHANNEL_SIZE),8,'666768'),
                 ('height and width set to 1',
                  ImageMetadata(height=1,width=1,channels=CHANNEL_SIZE),1,'000102'),
                ]

    for test_desc, imd, crop_size, colour in test_data:
      image_data = np.arange(imd.size(),dtype=np.uint8).reshape(imd.height,imd.width,imd.channels)

      with self.subTest(msg=test_desc):
        self._colour_extraction_testing(image_data=image_data,crop_size=crop_size,expected_colour_hex=colour)
  
  def test_colours_non_unique_for_different_image_modes(self):
  
    for no_of_channels in [3,4]:

      imd = ImageMetadata(height=6,width=6,channels=no_of_channels)

      image_data = np.arange(imd.size(),dtype=np.uint8).reshape(imd.height,imd.width,imd.channels)

      # Let's make a tiny little chessboard in the middle of the image 
      # even though the pieces wouldn't fit.
      image_data[1:5, 1:5:2, ...] = 255
      image_data[1:5, 2:5:2, ...] = 1
  
      img = Image.fromarray(image_data)

      with (patch('PIL.Image.open') as mock_image, 
            patch('os.path.isfile') as mock_isfile):
      
        mock_isfile.return_value = True
        mock_image.return_value = img

        extractor = extract_colour_image.ColourExtractorBasic()
        extractor.INITIAL_CROP_SIZE = 4
        actual_colour = extractor.get_colour('image_file_is_mocked')

        self.assertEqual(actual_colour, 'ffffff')

  def test_unsupported_image_mode(self):

      with (patch('PIL.Image.open') as mock_image, 
            patch('os.path.isfile') as mock_isfile):

          mock_isfile.return_value = True
          mock_image.mode.return_value= 'INVALID_MODE'

          extractor = extract_colour_image.ColourExtractorBasic()

          with self.assertRaisesRegex(RuntimeError,'modes supported but got'):
            extractor.get_colour('image_file_is_mocked')
  
  def test_unable_to_extract_colour(self):

      imd = ImageMetadata(height=6,width=6,channels=3)
      image_data = np.arange(imd.size(),dtype=np.uint8).reshape(imd.height,imd.width,imd.channels)
      img = Image.fromarray(image_data)

      with (patch('PIL.Image.open') as mock_image, 
            patch('os.path.isfile') as mock_isfile):

          mock_isfile.return_value = True
          mock_image.return_value = img

          extractor = extract_colour_image.ColourExtractorBasic()
          extractor.INITIAL_CROP_SIZE = 0

          with self.assertRaisesRegex(RuntimeError,'Unable to extract'):
            extractor.get_colour('image_file_is_mocked')
  
  