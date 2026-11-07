"""Verify actual image continuity, dimensions, stability and resource integration."""
import unittest
import xml.etree.ElementTree as ET
from PIL import Image, ImageChops
from generate_assets import ROOT, RES, FRAME_COUNT, WIDTH, HEIGHT, render_frame, petal_specs, position


class AssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Image.open(ROOT/"art/scene-base.png").convert("RGB")
        cls.frames = [Image.open(RES/f"drawable-nodpi/petal_frame_{i:03d}_pixels.png").convert("RGBA")
                      for i in range(FRAME_COUNT)]

    def test_exact_period_without_duplicate_end_frame(self):
        self.assertEqual(render_frame(self.base, 0).tobytes(), render_frame(self.base, 96).tobytes())
        self.assertNotEqual(self.frames[-1].tobytes(), self.frames[0].tobytes())

    def test_wrap_delta_is_typical_motion(self):
        counts = []
        for index in range(FRAME_COUNT):
            a, b = self.frames[index].convert("RGB"), self.frames[(index+1) % FRAME_COUNT].convert("RGB")
            delta = ImageChops.difference(a,b)
            counts.append(sum(1 for r,g,b in delta.get_flattened_data() if r or g or b))
        self.assertLessEqual(counts[-1], max(counts[:-1]))
        self.assertGreater(min(counts), 15)
        self.assertLess(max(counts), WIDTH*HEIGHT*.01)

    def test_background_is_stable_and_petal_coverage_bounded(self):
        for frame in self.frames:
            self.assertEqual(frame.size, (WIDTH, HEIGHT))
            delta = ImageChops.difference(frame.convert("RGB"), self.base)
            changes = sum(1 for p in delta.get_flattened_data() if any(p))
            self.assertGreater(changes, 10)
            self.assertLess(changes, 150)

    def test_petals_leave_boundary_before_rebirth(self):
        for p in petal_specs():
            frame = FRAME_COUNT - p["phase"] - 0.001
            x, _, _ = position(p, frame)
            self.assertGreater(x, WIDTH+3)

    def test_unique_frames_and_crisp_drawables(self):
        self.assertEqual(len(set(im.tobytes() for im in self.frames)), FRAME_COUNT)
        ns = "{http://schemas.android.com/apk/res/android}"
        for index in range(FRAME_COUNT):
            xml = ET.parse(RES/f"drawable/petal_frame_{index:03d}.xml").getroot()
            self.assertEqual(xml.get(ns+"filter"), "false")
            self.assertTrue((RES/"drawable-nodpi"/(xml.get(ns+"src").split("/")[1]+".png")).exists())

    def test_widget_has_no_host_slideshow_or_periodic_updates(self):
        ns = "{http://schemas.android.com/apk/res/android}"
        info = ET.parse(RES/"xml/sakura_widget_info.xml").getroot()
        self.assertIsNone(info.get(ns+"autoAdvanceViewId"))
        self.assertEqual(info.get(ns+"updatePeriodMillis"), "0")
        manifest = ET.parse(ROOT/"app/src/main/AndroidManifest.xml").getroot()
        self.assertEqual(manifest.findall("uses-permission"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
