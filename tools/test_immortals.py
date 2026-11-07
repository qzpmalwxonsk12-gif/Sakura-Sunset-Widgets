"""Position, resource fidelity and loop continuity checks for the second artwork."""
import json
import unittest
from PIL import Image, ImageChops
import generate_immortals as art


class ImmortalsTests(unittest.TestCase):
    def test_reference_position_and_classification_margin(self):
        rows,samples=art.board_position()
        self.assertEqual(len(rows),19)
        self.assertTrue(all(len(row)==19 for row in rows))
        self.assertEqual(sum(r.count('B') for r in rows),101)
        self.assertEqual(sum(r.count('W') for r in rows),100)
        # Every sampled intersection is far from a classification threshold.
        self.assertTrue(all(min(abs(s['shade']-85),abs(s['shade']-180))>15 for s in samples))
        self.assertEqual(json.loads((art.ROOT/'art/go-position.json').read_text())['rows'],rows)

    def test_bundled_frames_are_exact_and_unique(self):
        base=Image.open(art.ROOT/'art/immortals-base.png').convert('RGB')
        hashes=set()
        for i in range(art.N):
            frame=Image.open(art.RES/f'drawable-nodpi/immortals_frame_{i:03d}_pixels.png').convert('RGBA')
            self.assertEqual(frame.size,(480,270))
            expected=art.render(base,i)
            self.assertEqual(frame.getchannel('A').tobytes(),expected.getchannel('A').tobytes())
            # RGB under fully transparent rounded corners has no visible meaning.
            self.assertEqual(Image.alpha_composite(Image.new('RGBA',frame.size),frame).tobytes(),
                             Image.alpha_composite(Image.new('RGBA',frame.size),expected).tobytes())
            hashes.add(frame.tobytes())
        self.assertEqual(len(hashes),96)

    def test_loop_and_ground_exit(self):
        base=Image.open(art.ROOT/'art/immortals-base.png').convert('RGB')
        self.assertEqual(art.render(base,0).tobytes(),art.render(base,96).tobytes())
        changes=[]
        for i in range(96):
            a=art.render(base,i).convert('RGB'); b=art.render(base,(i+1)%96).convert('RGB')
            changes.append(sum(pixel!=(0,0,0) for pixel in ImageChops.difference(a,b).get_flattened_data()))
        self.assertLess(max(changes),200)
        self.assertLess(changes[-1],sum(changes)/96*1.5)
        for p in art.petal_specs():
            x,y,t=art.position(p,95.99-p['phase'])
            self.assertGreater(x,art.W+3)
            before=art.position(p,.72*96-p['phase']-.001)
            after=art.position(p,.72*96-p['phase']+.001)
            self.assertLess(abs(before[0]-after[0])+abs(before[1]-after[1]),.1)


if __name__=='__main__': unittest.main()
