import os.path
import tempfile

import matplotlib.animation
import pytest
import tools.play_whole_field as pwf

@pytest.mark.slow
def test_animation_file():
    # We use GIF and PIL here to not require CI/CD servers to install ffmpeg for mp4.
    f = tempfile.NamedTemporaryFile(suffix='.gif')
    writer = matplotlib.animation.PillowWriter()
    pwf.main(filename=f.name, writer=writer)
    assert os.path.exists(f.name)
    assert os.path.getsize(f.name) > 1024
