import hashlib
import json
import unittest
from PIL import Image, ImageChops
import generate_winter as art


class WinterTests(unittest.TestCase):
    def test_snow_contacts_ground_and_merges_before_rebirth(self):
        for p in art.snow_specs():
            start=art.state(p,-p['phase'])
            landed=art.state(p,art.LAND_AT*art.N-p['phase'])
            merged=art.state(p,.99*art.N-p['phase'])
            self.assertLess(start[1],0)
            self.assertAlmostEqual(landed[0],p['land_x'])
            self.assertAlmostEqual(landed[1],p['land_y'])
            self.assertGreaterEqual(landed[1],150)
            self.assertAlmostEqual(merged[1],p['land_y'])
            self.assertEqual(merged[2],0)
            alphas=[art.state(p,t*art.N-p['phase'])[2] for t in [.84,.88,.92,.96,.99]]
            self.assertEqual(alphas,sorted(alphas,reverse=True))

    def test_lossless_frames_and_loop_seam(self):
        base=Image.open(art.ROOT/'art/winter-base.png').convert('RGB')
        previous=None; changes=[]; hashes=set(); frames=[]
        for i in range(art.N):
            expected=art.render(base,i)
            bundled=Image.open(art.RES/f'drawable-nodpi/winter_frame_{i:03d}_pixels.png').convert('RGBA')
            blank=Image.new('RGBA',bundled.size)
            self.assertEqual(Image.alpha_composite(blank,expected).tobytes(),Image.alpha_composite(blank,bundled).tobytes())
            self.assertEqual(bundled.size,(320,180))
            hashes.add(bundled.tobytes()); frames.append(expected.convert('RGB'))
        self.assertEqual(len(hashes),96)
        self.assertEqual(art.render(base,0).tobytes(),art.render(base,96).tobytes())
        for i in range(96):
            delta=ImageChops.difference(frames[i],frames[(i+1)%96])
            changes.append(sum(p!=(0,0,0) for p in delta.get_flattened_data()))
        self.assertLess(max(changes),400)
        self.assertLess(changes[-1],sum(changes)/96*1.5)
        # Scene coverage stays bounded; snow never accumulates into a changing background.
        self.assertTrue(all(sum(p!=(0,0,0) for p in ImageChops.difference(frame,base).get_flattened_data())<160 for frame in frames))

    def test_previous_artworks_unchanged(self):
        for prefix,manifest in [('petal','asset-manifest.json'),('immortals','immortals-manifest.json')]:
            expected=json.loads((art.ROOT/'art'/manifest).read_text())['frame_sha256']
            actual=[hashlib.sha256((art.RES/f'drawable-nodpi/{prefix}_frame_{i:03d}_pixels.png').read_bytes()).hexdigest() for i in range(96)]
            self.assertEqual(actual,expected)

    def test_warm_window_colors_survive_pixel_palette(self):
        base=Image.open(art.ROOT/'art/winter-base.png').convert('RGB')
        window=base.crop((85,101,101,116))
        self.assertGreater(sum(r>190 and r>1.3*b and g>90 for r,g,b in window.get_flattened_data()),20)


if __name__=='__main__': unittest.main()
