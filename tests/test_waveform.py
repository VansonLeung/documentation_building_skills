import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as E

spec = importlib.util.spec_from_file_location('waveform', Path(__file__).resolve().parents[1] / 'documentation-building/scripts/waveform.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WaveformTest(unittest.TestCase):
    def test_duration_scale_and_silence(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'tone.wav'
            module.example(file)
            data = module.envelope(file, bins=4)
            self.assertEqual(data['frames'], 64000)
            self.assertEqual(data['duration_s'], 4)
            self.assertEqual(data['bins'][0]['max'], 0)
            self.assertEqual(data['bins'][3]['min'], 0)
            self.assertGreater(data['bins'][1]['max'], .4)
            self.assertLess(data['bins'][1]['max'], .5)
            self.assertEqual(E.fromstring(module.render(data, '<Synthetic>')).tag, '{http://www.w3.org/2000/svg}svg')
            with self.assertRaises(ValueError):
                module.envelope(file, channel=2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
