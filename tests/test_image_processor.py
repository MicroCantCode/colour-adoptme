import os
from unittest import TestCase
from unittest.mock import (
    patch,
    call
)

import extract_colour_image

class TestImageProcessor(TestCase):

    def test_read_args_string_not_file_input(self):

        args = ['pgm', 'imagefile']

        with patch('sys.argv', args):
            actual_args = extract_colour_image.read_args()
            print(actual_args.imagefile)
            self.assertEqual(args[1], actual_args.imagefile)

    def test_read_args_no_args_supplied(self):

        args = ['pgm']

        with (patch('sys.argv', args), 
              patch('sys.exit') as mock_sys_exit):

            extract_colour_image.read_args()

            exit_ok_call = call(os.EX_OK)

            mock_sys_exit.assert_called_once()

            # Negative check against exit success as non-successful
            # error value might be platform dependent
            self.assertNotIn(exit_ok_call, mock_sys_exit.call_args_list)
    
    def test_init_invalid_filenames(self):

      test_data = [ ('', False, 'value error'),
                    (None, False, 'type error'),
                    ('nonexistent_filename', False, '^Could not find'), ]


      for image_filename, is_file, wanted_exception_regex in test_data:

        with self.subTest(image_filename=image_filename,
                          is_file=is_file,
                          wanted_exception_regex=wanted_exception_regex):
       
          with patch('os.path.isfile') as mock_isfile:
            mock_isfile.return_value = is_file

            with self.assertRaisesRegex(RuntimeError, wanted_exception_regex):
                extract_colour_image.ImageProcessor(image_filename=image_filename)

    def test_init_valid_file_present(self):

        test_data = [('valid_filename_no_ext', [True, False], '.jpeg'),
                     ('valid_filename_no_ext', [True, True], '.jpeg'),
                     ('valid_filename_no_ext', [False, True], '.png'),
                     ('valid_filename.jpeg', [True, False], ''),
                     ('valid_filename.png', [False, True], ''),
                     ('valid_filename.JPeg', [True, False], ''),
                     ('valid_filename.txt.jpeg', [True, False], ''),]

        for image_filename, is_file_effects, suffix_added in test_data:

          with self.subTest(image_filename=image_filename,
                            is_file_effects=is_file_effects,
                            suffix_added=suffix_added):
        
            with patch('os.path.isfile') as mock_isfile:

              mock_isfile.side_effect = is_file_effects
              image_proc = extract_colour_image.ImageProcessor(image_filename=image_filename)

              self.assertEqual(image_proc.image_filename, (image_filename + suffix_added).lower())
          
    def test_constructor_extractor_none_arg(self):
      
       with (patch('os.path.isfile') as mock_isfile,
             patch('extract_colour_image.ColourExtractorBasic.get_colour') as mock_colour_extractor):

          mock_isfile.return_value = True
      
          some_filename = 'some_filename.jpeg'
          image_proc = extract_colour_image.ImageProcessor(image_filename=some_filename,colour_extractor=None)
          image_proc.get_colour()
 
          mock_colour_extractor.assert_called_once_with(some_filename)
